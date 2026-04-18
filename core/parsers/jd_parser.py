from __future__ import annotations

import re

from core.language_utils import detect_language
from core.jd_cleaner import clean_job_description_text
from core.keyword_intelligence import known_skill_vocabulary
from core.parsers.ocr import extract_text_from_image_bytes
from core.schemas import JobDescriptionData


COMMON_SKILLS = {
    "python",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "fastapi",
    "streamlit",
    "machine learning",
    "data analysis",
    "project management",
    "product management",
    "salesforce",
    "sap",
    "engineering leadership",
    "engineering management",
    "technical management",
    "technical operations",
    "manufacturing engineering",
    "manufacturing systems",
    "industrial engineering",
    "industrial operations",
    "industrial projects",
    "process engineering",
    "process improvement",
    "plant engineering",
    "factory execution",
    "production readiness",
    "automation",
    "control systems",
    "commissioning",
    "implementation",
    "delivery",
    "requirements analysis",
    "system design",
    "vendor management",
    "supplier management",
    "contractor management",
    "budget management",
    "cross-functional teams",
    "stakeholder management",
    "kpi tracking",
    "cost reduction",
    "quality improvement",
    "downtime reduction",
    "yield improvement",
    "productivity improvement",
    "safety",
    "reliability",
    "clinical trials",
    "biostatistics",
    "epidemiology",
    "clinical pharmacology",
    "regulatory affairs",
    "medical writing",
    "pharmacovigilance",
    "sas programming",
    "cdisc",
    "sdtm",
    "adam",
    "ich-gcp",
    "fda submissions",
    "ema submissions",
    "thermal engineering",
    "thermal design",
    "thermal analysis",
    "thermal management",
    "liquid cooling",
    "cooling systems",
    "electronics cooling",
    "high-power electronics",
    "thermo-mechanical analysis",
    "mechanical design",
    "mechanical development",
    "chip-to-rack",
    "rack systems",
    "data center cooling",
    "cold plate",
    "heat sink",
    "heat transfer",
    "cfd",
    "fea",
    "tim",
    "thermal interface material",
    "soldering",
    "joining",
    "brazing",
    "electronics packaging",
    "data center operational audits",
    "data center",
    "critical facilities",
    "operational audits",
    "automotive service",
    "automotive operations",
} | known_skill_vocabulary()


def parse_job_description(text: str) -> JobDescriptionData:
    text = clean_job_description_text(text)
    lowered = text.lower()
    skills = [skill for skill in sorted(COMMON_SKILLS, key=len, reverse=True) if _contains_term(lowered, skill)]
    must_have = re.findall(r"(?:must have|requirements|required)[:\-\s]+(.+)", lowered)
    nice = re.findall(r"(?:nice to have|preferred)[:\-\s]+(.+)", lowered)
    leadership = [term for term in ["lead", "manage", "ownership", "mentor", "stakeholder", "supplier", "contractor", "budget"] if term in lowered]
    tools = [skill for skill in skills if skill in {"python", "sql", "excel", "power bi", "tableau", "aws", "azure", "gcp", "docker", "kubernetes", "fastapi", "streamlit", "salesforce", "sap", "sas programming"}]
    seniority = next((term for term in ["intern", "junior", "mid", "senior", "lead", "manager", "director"] if term in lowered), "")
    role_title = _extract_role_title(text)
    inferred_role_title = False
    first_lines = [line.strip() for line in text.splitlines() if line.strip()][:5]
    if not role_title:
        role_title = _infer_role_title(skills, lowered)
        inferred_role_title = bool(role_title)
    company_name = _extract_company_name(text, first_lines)
    section_requirements = _section_items(text, {"requirements", "qualifications", "required"})
    section_preferred = _section_items(text, {"preferred", "nice to have"})
    parsed_must = _split_items(must_have[0]) if must_have else []
    parsed_nice = _split_items(nice[0]) if nice else []
    must_terms = _dedupe(section_requirements + parsed_must + skills[:14])
    nice_terms = _dedupe(section_preferred + parsed_nice)

    return JobDescriptionData(
        role_title=role_title,
        company_name=company_name,
        seniority=seniority,
        must_have_skills=must_terms[:18],
        nice_to_have_skills=nice_terms[:10],
        domain_keywords=_extract_domain_keywords(lowered),
        leadership_indicators=leadership,
        tools_and_technologies=tools,
        operational_expectations=_extract_operational_expectations(lowered),
        raw_text=text,
        detected_language=detect_language(text),
        role_title_inferred=inferred_role_title,
    )


def parse_job_description_image(content: bytes) -> JobDescriptionData:
    return parse_job_description(extract_text_from_image_bytes(content))


def _split_items(value: str) -> list[str]:
    raw_items = [item.strip(" .,-") for item in re.split(r"[,;/\n]", value) if item.strip()]
    items: list[str] = []
    for item in raw_items:
        if len(item.split()) > 8:
            items.extend(_extract_requirement_phrases(item))
        else:
            items.append(item)
    return [item for item in items if len(item) > 2][:18]


def _contains_term(text: str, term: str) -> bool:
    pattern = re.escape(term.lower()).replace(r"\ ", r"\s+")
    return bool(re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", text))


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        normalized = re.sub(r"\s+", " ", item.lower()).strip(" .,-:")
        if len(normalized) < 3 or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _section_items(text: str, headings: set[str]) -> list[str]:
    lines = [line.strip(" .:-") for line in text.splitlines() if line.strip()]
    items: list[str] = []
    active = False
    stop_headings = {"responsibilities", "requirements", "qualifications", "preferred", "nice to have", "benefits", "about us"}
    for line in lines:
        lowered = line.lower().strip(" .:-")
        if lowered in headings:
            active = True
            continue
        if active and lowered in stop_headings and lowered not in headings:
            break
        if active:
            if len(line.split()) > 10:
                items.extend(_extract_requirement_phrases(line.lower()))
            else:
                items.append(line.lower())
    return items[:18]


def _extract_requirement_phrases(value: str) -> list[str]:
    phrases = [
        "bachelor degree",
        "engineering leadership",
        "manufacturing engineering",
        "industrial operations",
        "process engineering",
        "plant engineering",
        "factory execution",
        "budget management",
        "vendor management",
        "supplier management",
        "contractor management",
        "engineering lifecycle",
        "requirements analysis",
        "system design",
        "implementation",
        "delivery",
        "commissioning",
        "automation",
        "technical operations",
        "process improvement",
        "cross-functional teams",
        "production readiness",
        "cost reduction",
        "quality improvement",
        "downtime reduction",
        "yield improvement",
        "productivity improvement",
        "maritime background",
        "naval systems",
        "willingness to travel",
        "technical management",
        "project management",
        "clinical trials",
        "biostatistics",
        "epidemiology",
        "clinical pharmacology",
        "medical writing",
        "regulatory affairs",
        "pharmacovigilance",
        "sas programming",
        "cdisc",
        "sdtm",
        "adam",
        "ich-gcp",
        "fda submissions",
        "ema submissions",
        "thermal engineering",
        "thermal design",
        "thermal analysis",
        "thermal management",
        "liquid cooling",
        "cooling systems",
        "electronics cooling",
        "high-power electronics",
        "thermo-mechanical analysis",
        "mechanical design",
        "mechanical development",
        "chip-to-rack",
        "rack systems",
        "data center cooling",
        "cold plate",
        "heat sink",
        "heat transfer",
        "cfd",
        "fea",
        "tim",
        "thermal interface material",
        "soldering",
        "joining",
        "brazing",
        "electronics packaging",
        "data center operational audits",
        "data center",
        "critical facilities",
        "operational audits",
        "automotive service",
        "automotive operations",
    ]
    lowered = value.lower()
    found = [phrase for phrase in phrases if phrase in lowered]
    return found or [part.strip(" .,-") for part in re.split(r"\band\b|\bwith\b|\bfrom\b|\bto\b", value) if 2 < len(part.split()) <= 6]


def _extract_domain_keywords(text: str) -> list[str]:
    candidates = [
        "fintech",
        "healthcare",
        "saas",
        "b2b",
        "b2c",
        "operations",
        "analytics",
        "marketing",
        "cybersecurity",
        "thermal engineering",
        "liquid cooling",
        "thermo-mechanical",
        "high-power electronics",
        "electronics cooling",
        "chip-to-rack",
        "mechanical development",
        "thermal interface material",
        "soldering",
        "joining",
        "electronics packaging",
        "data center operational audits",
        "data center",
        "critical facilities",
        "operational audits",
        "automotive service",
        "automotive operations",
    ]
    return [item for item in candidates if item in text]


def _extract_operational_expectations(text: str) -> list[str]:
    return [term for term in ["cross-functional", "kpi", "stakeholder", "delivery", "roadmap", "budget", "reporting", "execution"] if term in text]


def _extract_company_name(text: str, first_lines: list[str]) -> str:
    patterns = [
        r"(?:about|join|at)\s+([A-Z][A-Za-z0-9&.\- ]{2,40})",
        r"company[:\-\s]+([A-Z][A-Za-z0-9&.\- ]{2,40})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip(" .,-")
    for line in first_lines[1:]:
        if len(line.split()) <= 6 and any(ch.isupper() for ch in line):
            return line.strip(" .,-")
    return ""


def _extract_role_title(text: str) -> str:
    lines = [line.strip(" .:-") for line in text.splitlines() if line.strip()]
    explicit_patterns = [
        r"(?im)^\s*(?:role title|job title|position|title)\s*[:\-]\s*(.+)$",
        r"(?im)^\s*(?:we are hiring|hiring|open role)\s*[:\-]\s*(.+)$",
    ]
    for pattern in explicit_patterns:
        match = re.search(pattern, text)
        if match:
            candidate = _clean_role_title(match.group(1))
            if candidate:
                return candidate
    for line in lines[:8]:
        candidate = _clean_role_title(line)
        lowered = candidate.lower()
        if not candidate or lowered in {"responsibilities", "requirements", "qualifications", "preferred", "about the job", "job description"}:
            continue
        if len(candidate.split()) <= 10 and any(token in lowered for token in ["engineer", "manager", "director", "lead", "architect", "specialist"]):
            return candidate
    return ""


def _clean_role_title(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip(" .:-|")
    junk_starts = ("team.", "in this role", "you will", "we are", "about the job", "responsibilities", "requirements")
    if cleaned.lower().startswith(junk_starts):
        return ""
    cleaned = re.split(r"\s+\|\s+|\s+-\s+| at ", cleaned, maxsplit=1)[0].strip()
    if len(cleaned) > 90 or len(cleaned.split()) > 12:
        return ""
    return cleaned


def _infer_role_title(skills: list[str], text: str) -> str:
    if any(term in text for term in ["thermal", "liquid cooling", "thermo-mechanical", "electronics cooling"]):
        if "manager" in text or "lead" in text:
            return "Thermal Mechanical Engineering Lead"
        return "Thermal Mechanical Engineer"
    if "manufacturing engineering" in skills:
        return "Manufacturing Engineering Manager" if "manager" in text else "Manufacturing Engineer"
    if "technical operations" in skills:
        return "Technical Operations Manager"
    if "automation" in skills:
        return "Automation Engineering Lead"
    return ""
