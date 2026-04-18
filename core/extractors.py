from __future__ import annotations

import re
from collections import Counter

from core.keyword_intelligence import known_skill_vocabulary, section_aliases
from core.schemas import ContactInfo, ExperienceEntry, ResumeStructuredData


EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
DATE_PATTERN = re.compile(
    r"((?:20|19)\d{2}\s*[-/–—]\s*(?:(?:20|19)\d{2}|present)|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",
    re.I,
)
SECTION_TITLES = ["summary", "experience", "education", "skills", "languages", "certifications", "projects"]
HEBREW_SECTION_TITLES = ["תקציר", "ניסיון", "השכלה", "כישורים", "שפות", "הסמכות", "פרויקטים"]
SKILL_VOCAB = {
    "python", "sql", "excel", "power bi", "tableau", "aws", "azure", "gcp", "docker",
    "kubernetes", "fastapi", "streamlit", "pandas", "numpy", "scikit-learn", "tensorflow",
    "pytorch", "jira", "salesforce", "sap", "crm", "etl", "api", "analytics", "leadership",
    "engineering leadership", "engineering management", "project management", "technical operations",
    "manufacturing engineering", "manufacturing systems", "industrial engineering", "industrial projects",
    "industrial operations", "process engineering", "process improvement", "plant engineering",
    "factory execution", "production lines", "production readiness", "automation", "control systems",
    "monitoring", "commissioning", "implementation", "delivery", "supplier coordination",
    "supplier negotiations", "vendor management", "contractor management", "maintenance",
    "quality improvement", "cost reduction", "waste reduction", "downtime reduction",
    "throughput", "kpi", "data analysis", "cross-functional", "stakeholder management",
    "equipment selection", "technical procurement", "materials engineering", "chemical engineering",
    "plc", "robotics", "lean", "six sigma",
} | known_skill_vocabulary()
LEADERSHIP_TERMS = {
    "managed", "managing", "led", "leading", "mentored", "mentor", "owned", "ownership",
    "responsible", "guided", "guidance", "launched", "directed", "headed", "prioritize",
    "stakeholder", "interface", "supplier", "contractor", "team",
}


def extract_resume_structure(text: str) -> ResumeStructuredData:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    full_name = lines[0] if lines else ""
    email = _first_match(EMAIL_PATTERN, text)
    phone = _first_match(PHONE_PATTERN, text)
    sections = _segment_sections(lines)
    lowered_text = text.lower()
    skills = sorted(skill for skill in SKILL_VOCAB if _contains_term(lowered_text, skill))
    quantified = [line for line in lines if re.search(r"\b\d+[%+$]?\b", line)]
    leadership = [line for line in lines if any(term in line.lower() for term in LEADERSHIP_TERMS)]
    education = [line for line in lines if any(token in line.lower() for token in ["university", "college", "b.sc", "m.sc", "mba", "תואר", "אוניברסיטה"])]
    languages = [line for line in lines if any(token in line.lower() for token in ["english", "hebrew", "arabic", "spanish", "עברית", "אנגלית"])]
    experience = _extract_experience(lines)

    return ResumeStructuredData(
        contact=ContactInfo(full_name=full_name, phone=phone, email=email, location=_infer_location(lines)),
        summary=sections.get("summary") or sections.get("תקציר") or "",
        experience=experience,
        education=education,
        languages=languages,
        hard_skills=skills,
        leadership_signals=leadership,
        quantified_achievements=quantified,
        raw_sections=sections,
    )


def extract_top_keywords(text: str, limit: int = 20) -> list[str]:
    tokens = re.findall(r"[A-Za-z\u0590-\u05FF][A-Za-z\u0590-\u05FF+\-/.#]{2,}", text.lower())
    filtered = [token for token in tokens if token not in {"the", "and", "with", "for", "you", "your", "this", "that"}]
    return [token for token, _ in Counter(filtered).most_common(limit)]


def _contains_term(text: str, term: str) -> bool:
    escaped = re.escape(term.lower())
    return bool(re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text))


def _first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(1) if match and match.lastindex else match.group(0) if match else ""


def _segment_sections(lines: list[str]) -> dict[str, str]:
    aliases = {
        "professional summary": "summary",
        "profile": "summary",
        "core areas of experience": "skills",
        "core competencies": "skills",
        "professional experience": "experience",
        "work experience": "experience",
    }
    for canonical, values in section_aliases().items():
        aliases.update({value.lower(): canonical for value in values})
    titles = set(SECTION_TITLES + HEBREW_SECTION_TITLES + list(aliases))
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for line in lines:
        key = line.lower().strip(":")
        if key in titles:
            current = aliases.get(key, line.strip(":").lower())
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items() if value}


def _extract_experience(lines: list[str]) -> list[ExperienceEntry]:
    experiences: list[ExperienceEntry] = []
    for index, line in enumerate(lines):
        if " at " in line.lower() or " @ " in line:
            parts = re.split(r"\s+at\s+|\s+@\s+", line, flags=re.I)
            title = parts[0].strip()
            employer = parts[1].strip() if len(parts) > 1 else ""
            date_range = _first_match(DATE_PATTERN, line)
            achievements = lines[index + 1:index + 3]
            experiences.append(ExperienceEntry(job_title=title, employer=employer, date_range=date_range, achievements=achievements))
            continue
        if "|" in line and _first_match(DATE_PATTERN, line):
            parts = [part.strip() for part in line.split("|") if part.strip()]
            if len(parts) >= 2:
                title = parts[0]
                employer = parts[1]
                date_range = _first_match(DATE_PATTERN, line)
                achievements = lines[index + 1:index + 4]
                experiences.append(ExperienceEntry(job_title=title, employer=employer, date_range=date_range, achievements=achievements))
    return experiences[:8]


def _infer_location(lines: list[str]) -> str:
    lowered = "\n".join(lines).lower()
    for city in ["tel aviv", "jerusalem", "haifa", "new york", "london", "remote", "תל אביב", "ירושלים", "חיפה"]:
        if city in lowered:
            return city
    return ""
