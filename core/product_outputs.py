from __future__ import annotations

import re

from core.schemas import JobDescriptionData, ResumeStructuredData


def build_product_outputs(
    *,
    resume: ResumeStructuredData,
    jd: JobDescriptionData,
    missing_keywords: list[str],
    visibility_profile: dict[str, object],
    final_score: float,
    premium_unlocked: bool = False,
) -> dict[str, object]:
    """Create product-facing transformation data without changing ATS scoring."""
    top_keywords = _clean_terms(missing_keywords)[:8]
    role_title = jd.role_title or _first_title(resume) or "target role"
    current_title = _first_title(resume) or "Current resume headline"
    summary_before = resume.summary or _fallback_summary(resume)
    first_bullets = _first_bullets(resume)

    transformed_blocks = [
        {
            "id": "headline",
            "label": "Headline",
            "before": current_title,
            "after": _headline_after(current_title, role_title, top_keywords),
            "change_reason": "Improved title alignment for recruiter search.",
            "inserted_terms": [role_title, *top_keywords[:2]],
            "premium_locked": False,
        },
        {
            "id": "summary",
            "label": "Summary",
            "before": summary_before,
            "after": _summary_after(summary_before, role_title, top_keywords),
            "change_reason": "Moves role fit, ownership and missing search phrases closer to the top.",
            "inserted_terms": top_keywords[:4],
            "premium_locked": False,
        },
    ]
    for index, bullet in enumerate(first_bullets[:3], start=1):
        transformed_blocks.append(
            {
                "id": f"bullet_{index}",
                "label": f"Experience bullet {index}",
                "before": bullet,
                "after": _bullet_after(bullet, role_title, top_keywords[index - 1 : index + 2]),
                "change_reason": "Strengthened measurable impact and role-specific wording without inventing facts.",
                "inserted_terms": top_keywords[index - 1 : index + 2],
                "premium_locked": index > 1,
            }
        )

    rewrite_preview = {
        "headline": transformed_blocks[0]["after"],
        "summary": transformed_blocks[1]["after"],
        "bullets": [block["after"] for block in transformed_blocks if block["id"].startswith("bullet_")],
        "search_phrases": _search_phrase_suggestions(role_title, jd, top_keywords),
    }
    fix_impact_estimates = _fix_impact_estimates(visibility_profile, top_keywords)
    job_search_plan = build_job_search_plan(resume=resume, jd=jd, visibility_profile=visibility_profile, missing_keywords=top_keywords)

    return {
        "premium": {
            "mode": "premium_unlocked" if premium_unlocked else "premium_preview",
            "is_unlocked": premium_unlocked,
            "free": [
                "decision",
                "visibility_score",
                "why_not_found",
                "top_fixes",
                "one_rewrite_preview",
                "adjacent_roles",
            ],
            "locked": [
                "full_transformed_resume",
                "full_rewrite_pack",
                "exact_recruiter_keyword_pack",
                "exact_job_search_plan",
                "linkedin_search_strings",
                "expanded_role_targeting_pack",
            ],
            "cta": "Unlock full optimized resume + job search plan",
        },
        "transformed_blocks": transformed_blocks,
        "rewrite_preview": rewrite_preview,
        "rewrite_explanations": [block["change_reason"] for block in transformed_blocks],
        "fix_impact_estimates": fix_impact_estimates,
        "job_search_plan": job_search_plan,
        "estimated_after_scores": {
            "visibility_score": min(100, round(float(visibility_profile.get("visibility_score", final_score) or 0) + sum(item["visibility_uplift"] for item in fix_impact_estimates), 1)),
            "final_ats_score": min(100, round(final_score + sum(item["ats_uplift"] for item in fix_impact_estimates), 1)),
        },
    }


def build_job_search_plan(
    *,
    resume: ResumeStructuredData,
    jd: JobDescriptionData,
    visibility_profile: dict[str, object],
    missing_keywords: list[str],
) -> dict[str, object]:
    role_title = jd.role_title or _first_title(resume) or "Engineering Manager"
    adjacent_roles = _target_roles(resume, jd)
    domains = _clean_terms(jd.domain_keywords + jd.operational_expectations + jd.tools_and_technologies)[:6]
    keyword_bundle = _clean_terms([role_title, *missing_keywords[:5], *domains[:4]])
    location_hint = resume.contact.location or "your target location / remote"
    filters = {
        "posted_this_week": True,
        "seniority": jd.seniority or "mid-senior",
        "location": location_hint,
        "remote_or_hybrid": "include remote/hybrid when relevant",
    }
    queries = []
    for role in adjacent_roles[:5]:
        query_terms = " ".join(_clean_terms([role, *domains[:2], *missing_keywords[:2]])[:5])
        queries.append(f'"{role}" {query_terms}'.strip())
    if not queries:
        queries.append(f'"{role_title}" {" ".join(keyword_bundle[:4])}'.strip())
    company_types = _company_types(jd, domains)
    return {
        "target_roles": adjacent_roles[:5],
        "linkedin_queries": queries[:5],
        "filters": filters,
        "company_types": company_types,
        "keyword_bundles": {
            "core": keyword_bundle[:6],
            "management": _clean_terms(jd.leadership_indicators + resume.leadership_signals)[:6],
            "technical": _clean_terms(jd.tools_and_technologies + jd.must_have_skills)[:8],
        },
        "free_preview": queries[:1],
    }


def _fix_impact_estimates(visibility_profile: dict[str, object], top_keywords: list[str]) -> list[dict[str, object]]:
    visibility = float(visibility_profile.get("visibility_score", 0) or 0)
    low_visibility_bonus = 2 if visibility < 45 else 0
    return [
        {
            "id": "keyword",
            "label": "Add keyword",
            "visibility_uplift": 5 + low_visibility_bonus,
            "ats_uplift": 2,
            "terms": top_keywords[:3],
        },
        {
            "id": "title",
            "label": "Improve title",
            "visibility_uplift": 4 + low_visibility_bonus,
            "ats_uplift": 1.5,
            "terms": [],
        },
        {
            "id": "search_phrases",
            "label": "Improve search phrases",
            "visibility_uplift": 5,
            "ats_uplift": 2,
            "terms": top_keywords[3:6],
        },
    ]


def _target_roles(resume: ResumeStructuredData, jd: JobDescriptionData) -> list[str]:
    text = " ".join(
        [
            jd.role_title,
            " ".join(jd.domain_keywords),
            " ".join(jd.operational_expectations),
            " ".join(jd.tools_and_technologies),
            " ".join(resume.hard_skills),
            " ".join(resume.leadership_signals),
        ]
    ).lower()
    roles: list[str] = []
    if "manufactur" in text or "factory" in text or "plant" in text:
        roles.extend(["Manufacturing Engineering Manager", "Plant Engineering Manager"])
    if "automation" in text or "control" in text or "process" in text:
        roles.extend(["Automation Project Manager", "Head of Process Engineering"])
    if "project" in text or "commission" in text or "supplier" in text or "vendor" in text:
        roles.extend(["Project Engineering Manager", "Industrial Projects Lead"])
    if "operation" in text or "technical" in text:
        roles.append("Technical Operations Manager")
    roles.extend(["Engineering Manager", "Head of Engineering Operations"])
    return _dedupe(roles)[:6]


def _headline_after(current_title: str, role_title: str, terms: list[str]) -> str:
    bridge_terms = " | ".join(_clean_terms([role_title, *terms[:2]])[:3])
    if bridge_terms.lower() in current_title.lower():
        return current_title
    return f"{current_title} | {bridge_terms}"


def _summary_after(summary: str, role_title: str, terms: list[str]) -> str:
    base = summary.strip() or "Experienced engineering and operations professional."
    insert = ", ".join(_clean_terms([role_title, *terms[:4]])[:5])
    sentence = f"Positioned for {insert}, with emphasis on ownership, delivery, measurable improvement and cross-functional execution."
    if len(base) > 420:
        base = base[:420].rsplit(" ", 1)[0] + "."
    return f"{base} {sentence}".strip()


def _bullet_after(bullet: str, role_title: str, terms: list[str]) -> str:
    clean = bullet.strip() or "Led technical delivery across engineering, operations and suppliers."
    suffix_terms = ", ".join(_clean_terms([role_title, *terms])[:4])
    if suffix_terms:
        return f"{clean} Reframe for {suffix_terms} by foregrounding scope, measurable impact and ownership already supported by the resume."
    return f"{clean} Reframe by foregrounding scope, measurable impact and ownership already supported by the resume."


def _search_phrase_suggestions(role_title: str, jd: JobDescriptionData, terms: list[str]) -> list[str]:
    phrases = _clean_terms([role_title, *jd.leadership_indicators[:3], *jd.tools_and_technologies[:3], *terms[:4]])
    return phrases[:8]


def _first_title(resume: ResumeStructuredData) -> str:
    for item in resume.experience:
        if item.job_title:
            return item.job_title
    return ""


def _first_bullets(resume: ResumeStructuredData) -> list[str]:
    bullets: list[str] = []
    for item in resume.experience:
        bullets.extend(item.achievements)
        if len(bullets) >= 4:
            break
    if not bullets:
        bullets = resume.quantified_achievements[:4] or resume.leadership_signals[:4]
    return bullets[:4]


def _fallback_summary(resume: ResumeStructuredData) -> str:
    title = _first_title(resume)
    skills = ", ".join(resume.hard_skills[:4])
    parts = [part for part in [title, skills] if part]
    return " | ".join(parts) or "Summary was not clearly extracted from the resume."


def _company_types(jd: JobDescriptionData, domains: list[str]) -> list[str]:
    text = " ".join([jd.raw_text, " ".join(domains)]).lower()
    company_types = []
    if "defense" in text or "naval" in text or "aerospace" in text:
        company_types.extend(["Defense and aerospace manufacturers", "Naval systems integrators"])
    if "manufactur" in text or "factory" in text:
        company_types.extend(["Advanced manufacturing companies", "Industrial automation companies"])
    if "medical" in text or "pharma" in text:
        company_types.append("Regulated medical or pharma manufacturing")
    company_types.extend(["Engineering-led scaleups", "Operations-heavy technology companies"])
    return _dedupe(company_types)[:5]


def _clean_terms(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        text = re.sub(r"\s+", " ", str(value or "")).strip(" -|,.;:")
        if 2 <= len(text) <= 90 and text.lower() not in {item.lower() for item in cleaned}:
            cleaned.append(text)
    return cleaned


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result
