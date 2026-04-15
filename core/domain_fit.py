from __future__ import annotations

import re
from dataclasses import dataclass

from core.matching import _term_coverage, re_tokens
from core.schemas import JobDescriptionData, ResumeStructuredData


SPECIALIZED_DOMAIN_TERMS = [
    "thermal engineering",
    "thermal design",
    "thermal analysis",
    "thermal management",
    "liquid cooling",
    "cooling systems",
    "electronics cooling",
    "high-power electronics",
    "thermo-mechanical",
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
    "nvh",
    "optical design",
    "rf design",
    "asic",
    "semiconductor packaging",
    "firmware",
    "data center operational audits",
    "data center",
    "critical facilities",
    "operational audits",
    "automotive service",
    "automotive operations",
]

CRITICAL_REQUIREMENT_HINTS = {
    "required",
    "must",
    "mandatory",
    "minimum",
    "strong experience",
    "hands-on",
    "deep understanding",
    "expertise",
    "proven experience",
    "years",
}

GENERIC_LEADERSHIP_TERMS = {
    "lead",
    "manage",
    "ownership",
    "mentor",
    "stakeholder",
    "supplier",
    "contractor",
    "budget",
    "cross-functional teams",
    "project management",
    "engineering leadership",
    "engineering management",
}


@dataclass(frozen=True)
class DomainFitAdjustment:
    keyword_score: float
    semantic_score: float
    title_alignment_score: float
    leadership_alignment_score: float
    missing_keywords: list[str]
    diagnostics: dict[str, object]


def apply_domain_fit_adjustment(
    resume: ResumeStructuredData,
    jd: JobDescriptionData,
    resume_text: str,
    keyword_score: float,
    semantic_score: float,
    title_alignment_score: float,
    leadership_alignment_score: float,
    missing_keywords: list[str],
) -> DomainFitAdjustment:
    requirement_map = assess_hard_requirement_fit(resume, jd, resume_text)
    absent = list(requirement_map["absent"])
    partial = list(requirement_map["partial"])
    critical_absent = list(requirement_map["critical_absent"])
    specialization_score = float(requirement_map["specialization_score"])
    is_specialized = bool(requirement_map["is_specialized"])

    adjusted_keyword = keyword_score
    adjusted_semantic = semantic_score
    adjusted_title = title_alignment_score
    adjusted_leadership = leadership_alignment_score
    penalty_reasons: list[str] = []

    if is_specialized and critical_absent:
        missing_ratio = len(critical_absent) / max(len(requirement_map["critical_requirements"]), 1)
        cap = 58.0 if missing_ratio < 0.5 else 48.0
        adjusted_semantic = min(adjusted_semantic, cap)
        adjusted_keyword = min(adjusted_keyword, 62.0 - min(len(critical_absent) * 4.0, 22.0))
        adjusted_title = min(adjusted_title, 62.0)
        adjusted_leadership = min(adjusted_leadership, 80.0)
        penalty_reasons.append("Major domain-specific hard requirements are not supported by resume evidence.")

    if is_specialized and len(critical_absent) >= 3:
        adjusted_semantic = min(adjusted_semantic, 42.0)
        adjusted_keyword = min(adjusted_keyword, 44.0)
        adjusted_leadership = min(adjusted_leadership, 55.0)
        penalty_reasons.append("Generic leadership was capped because the JD requires domain-specific leadership.")

    if is_specialized and specialization_score < 35:
        adjusted_semantic = min(adjusted_semantic, 45.0)
        adjusted_keyword = min(adjusted_keyword, 48.0)
        penalty_reasons.append("Specialized domain evidence is weak relative to the JD.")

    if not is_specialized and len(critical_absent) >= 1 and specialization_score < 45:
        adjusted_semantic = min(adjusted_semantic, 55.0)
        adjusted_keyword = min(adjusted_keyword, 58.0)
        adjusted_title = min(adjusted_title, 65.0)
        penalty_reasons.append("The role family matches broadly, but the job-specific domain is not evidenced.")

    if not _is_leadership_role(jd.role_title) and _resume_is_management_heavy(resume, resume_text):
        adjusted_title = min(adjusted_title, 78.0)
        adjusted_leadership = min(adjusted_leadership, 60.0)
        penalty_reasons.append("Candidate seniority is strong, but the target role is not primarily a leadership role.")

    merged_missing = list(dict.fromkeys([*critical_absent, *absent, *missing_keywords]))
    diagnostics = {
        **requirement_map,
        "penalty_applied": bool(penalty_reasons),
        "penalty_reasons": penalty_reasons,
        "score_caps": {
            "keyword_match_score": round(adjusted_keyword, 2),
            "semantic_match_score": round(adjusted_semantic, 2),
            "title_alignment_score": round(adjusted_title, 2),
            "leadership_alignment_score": round(adjusted_leadership, 2),
        },
    }
    return DomainFitAdjustment(
        keyword_score=round(max(0.0, adjusted_keyword), 2),
        semantic_score=round(max(0.0, adjusted_semantic), 2),
        title_alignment_score=round(max(0.0, adjusted_title), 2),
        leadership_alignment_score=round(max(0.0, adjusted_leadership), 2),
        missing_keywords=merged_missing[:24],
        diagnostics=diagnostics,
    )


def assess_hard_requirement_fit(resume: ResumeStructuredData, jd: JobDescriptionData, resume_text: str) -> dict[str, object]:
    requirements = _critical_requirements(jd)
    searchable_resume = _searchable_resume(resume, resume_text)
    resume_terms = {_normalize(item) for item in resume.hard_skills}
    matched: list[str] = []
    partial: list[str] = []
    absent: list[str] = []
    for requirement in requirements:
        coverage = _term_coverage(_normalize(requirement), resume_terms, searchable_resume)
        if coverage >= 0.72:
            matched.append(requirement)
        elif coverage >= 0.32:
            partial.append(requirement)
        else:
            absent.append(requirement)

    domain_terms = [term for term in requirements if _is_specialized_domain_term(term)]
    critical_absent = [term for term in absent if term in domain_terms]
    specialization_score = ((len(matched) + len(partial) * 0.45) / max(len(requirements), 1)) * 100
    return {
        "requirements": requirements,
        "critical_requirements": domain_terms,
        "matched": matched,
        "partial": partial,
        "absent": absent,
        "critical_absent": critical_absent,
        "is_specialized": len(domain_terms) >= 2,
        "specialization_score": round(specialization_score, 2),
    }


def _critical_requirements(jd: JobDescriptionData) -> list[str]:
    source = list(dict.fromkeys(jd.must_have_skills + jd.tools_and_technologies + jd.domain_keywords))
    raw_text = jd.raw_text.lower()
    for term in SPECIALIZED_DOMAIN_TERMS:
        if _phrase_present(term, raw_text):
            source.append(term)
    for phrase in _extract_explicit_requirement_phrases(raw_text):
        source.append(phrase)
    filtered = []
    for item in source:
        normalized = _normalize(item)
        if len(normalized) < 3 or normalized in GENERIC_LEADERSHIP_TERMS:
            continue
        if _is_specialized_domain_term(normalized) or _looks_like_hard_requirement(normalized, raw_text):
            filtered.append(normalized)
    return list(dict.fromkeys(filtered))[:18]


def _extract_explicit_requirement_phrases(text: str) -> list[str]:
    phrases: list[str] = []
    sentence_chunks = re.split(r"[\n.;•]+", text)
    for sentence in sentence_chunks:
        if not any(hint in sentence for hint in CRITICAL_REQUIREMENT_HINTS):
            continue
        for term in SPECIALIZED_DOMAIN_TERMS:
            if _phrase_present(term, sentence):
                phrases.append(term)
        degree_match = re.search(r"(?:bachelor|master|phd|b\.s\.|m\.s\.).{0,80}?(?:engineering|mechanical|thermal|science)", sentence)
        if degree_match:
            phrases.append(_normalize(degree_match.group(0)))
        years_match = re.search(r"\b\d+\+?\s+years?.{0,70}?(?:experience|leadership|development|design)", sentence)
        if years_match:
            phrases.append(_normalize(years_match.group(0)))
    return phrases


def _looks_like_hard_requirement(term: str, jd_text: str) -> bool:
    if _is_specialized_domain_term(term):
        return True
    window_match = re.search(rf"(required|must|mandatory|experience|expertise).{{0,120}}{re.escape(term)}", jd_text)
    return bool(window_match)


def _is_specialized_domain_term(term: str) -> bool:
    normalized = _normalize(term)
    return any(_phrase_present(domain, normalized) or _phrase_present(normalized, domain) for domain in SPECIALIZED_DOMAIN_TERMS)


def _is_leadership_role(role_title: str) -> bool:
    role = _normalize(role_title)
    return any(term in role for term in ["manager", "lead", "director", "head", "principal", "staff"])


def _resume_is_management_heavy(resume: ResumeStructuredData, resume_text: str) -> bool:
    titles = " ".join(item.job_title for item in resume.experience)
    text = _normalize(f"{titles} {resume.summary} {resume_text}")
    return any(term in text for term in ["manager", "management", "leader", "led", "head", "director"])


def _searchable_resume(resume: ResumeStructuredData, resume_text: str) -> str:
    return _normalize(
        "\n".join(
            [
                resume_text,
                resume.summary,
                "\n".join(resume.hard_skills),
                "\n".join(resume.leadership_signals),
                "\n".join(resume.quantified_achievements),
                "\n".join(resume.raw_sections.values()),
            ]
        )
    )


def _normalize(value: str) -> str:
    return " ".join(re_tokens(value))


def _phrase_present(term: str, text: str) -> bool:
    normalized = _normalize(term)
    return bool(normalized and normalized in _normalize(text))
