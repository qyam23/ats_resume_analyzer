from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TermMatch:
    canonical: str
    aliases: tuple[str, ...]
    weight: float = 1.0


SECTION_TITLE_ALIASES: dict[str, tuple[str, ...]] = {
    "summary": ("professional summary", "profile", "career profile", "about", "תקציר", "פרופיל"),
    "experience": ("work experience", "professional experience", "employment history", "ניסיון", "נסיון תעסוקתי"),
    "skills": ("core skills", "technical skills", "core competencies", "areas of expertise", "כישורים", "מיומנויות"),
    "education": ("academic background", "education and training", "השכלה", "לימודים"),
    "languages": ("language skills", "שפות"),
    "certifications": ("certificates", "licenses", "הסמכות", "תעודות"),
    "projects": ("selected projects", "key projects", "פרויקטים", "פרוייקטים"),
}

SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "mssql": ("sql server", "microsoft sql server", "ms sql"),
    "sql": ("structured query language",),
    "power bi": ("powerbi", "microsoft power bi"),
    "kubernetes": ("k8s",),
    "continuous improvement": ("process improvement", "kaizen", "lean improvement"),
    "technical leadership": ("engineering leadership", "technical lead", "led technical teams"),
    "stakeholder management": ("cross-functional stakeholder management", "management interfaces"),
    "vendor management": ("supplier management", "supplier coordination", "third-party management"),
    "commissioning": ("start-up", "startup", "site acceptance", "sat", "fat"),
    "thermal interface material": ("tim", "thermal interface materials"),
    "computational fluid dynamics": ("cfd",),
    "finite element analysis": ("fea",),
    "electronics cooling": ("high-power electronics cooling", "cooling of electronics"),
    "liquid cooling": ("liquid-cooled", "liquid cooled", "cold plate"),
}

TITLE_ALIASES: dict[str, tuple[str, ...]] = {
    "engineering manager": ("engineering lead", "technical manager", "manager, engineering"),
    "project engineering manager": ("engineering project manager", "technical project manager"),
    "manufacturing engineering manager": ("manufacturing engineering lead", "production engineering manager"),
    "technical operations manager": ("engineering operations manager", "technical ops manager"),
    "thermal mechanical engineering lead": ("thermal engineering manager", "mechanical thermal lead"),
    "automation engineering lead": ("automation lead", "control systems lead"),
}

SENIORITY_TERMS: dict[str, tuple[str, ...]] = {
    "entry": ("intern", "junior", "associate"),
    "mid": ("mid", "professional", "experienced"),
    "senior": ("senior", "sr", "lead", "principal"),
    "management": ("manager", "head", "director", "vp", "owner", "ownership"),
}

DOMAIN_TERMS: dict[str, tuple[str, ...]] = {
    "thermal_mechanical": (
        "thermal engineering",
        "thermal design",
        "liquid cooling",
        "electronics cooling",
        "thermo-mechanical",
        "high-power electronics",
        "chip-to-rack",
        "cold plate",
        "heat sink",
        "thermal interface material",
        "soldering",
        "joining",
        "brazing",
        "cfd",
        "fea",
    ),
    "manufacturing_operations": (
        "manufacturing engineering",
        "production readiness",
        "process engineering",
        "plant engineering",
        "factory execution",
        "lean",
        "six sigma",
        "commissioning",
    ),
    "data_analytics": (
        "python",
        "sql",
        "etl",
        "analytics",
        "power bi",
        "tableau",
        "machine learning",
    ),
}


def normalize_phrase(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9\u0590-\u05FF+#./-]+", value.lower()))


def canonical_skill(value: str) -> str:
    normalized = normalize_phrase(value)
    for canonical, aliases in SKILL_ALIASES.items():
        if normalized == canonical or normalized in {normalize_phrase(alias) for alias in aliases}:
            return canonical
    return normalized


def expand_skill_terms(terms: list[str] | set[str]) -> set[str]:
    expanded: set[str] = set()
    for term in terms:
        canonical = canonical_skill(term)
        if canonical:
            expanded.add(canonical)
            expanded.update(normalize_phrase(alias) for alias in SKILL_ALIASES.get(canonical, ()))
    return {term for term in expanded if term}


def expand_title_terms(title: str) -> set[str]:
    normalized = normalize_phrase(title)
    expanded = {normalized} if normalized else set()
    for canonical, aliases in TITLE_ALIASES.items():
        if normalized == canonical or normalized in {normalize_phrase(alias) for alias in aliases}:
            expanded.add(canonical)
            expanded.update(normalize_phrase(alias) for alias in aliases)
    return {term for term in expanded if term}


def infer_title_family(title: str) -> str:
    normalized = normalize_phrase(title)
    for canonical, aliases in TITLE_ALIASES.items():
        values = {canonical, *(normalize_phrase(alias) for alias in aliases)}
        if normalized in values or any(value and value in normalized for value in values):
            return canonical
    return normalized


def section_aliases() -> dict[str, tuple[str, ...]]:
    return SECTION_TITLE_ALIASES


def known_skill_vocabulary() -> set[str]:
    terms = set(SKILL_ALIASES)
    for aliases in SKILL_ALIASES.values():
        terms.update(normalize_phrase(alias) for alias in aliases)
    for values in DOMAIN_TERMS.values():
        terms.update(normalize_phrase(value) for value in values)
    return {term for term in terms if term}
