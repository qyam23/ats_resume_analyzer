from __future__ import annotations

import re
import unicodedata

from core.schemas import JobDescriptionData, ResumeStructuredData


HEBREW_TITLE_ALIASES = {
    "מנהל הנדסה": ["engineering manager", "head of engineering", "technical manager"],
    "מנהל פרויקטים": ["project manager", "project engineering manager", "program manager"],
    "מנהל תפעול": ["operations manager", "technical operations manager"],
    "אוטומציה": ["automation", "control systems", "plc"],
    "מפעל": ["plant", "factory", "manufacturing"],
}


def normalize_hebrew_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "")
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = text.replace("־", "-").replace("–", "-").replace("—", "-")
    text = re.sub(r"[״׳`´]", "'", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def build_visibility_profile(
    resume: ResumeStructuredData,
    jd: JobDescriptionData,
    resume_text: str,
    missing_keywords: list[str],
    parseability_score: float,
    keyword_match_score: float,
    title_alignment_score: float,
    leadership_alignment_score: float,
    domain_fit: dict[str, object] | None = None,
) -> dict[str, object]:
    searchable_resume = normalize_hebrew_text(
        "\n".join(
            [
                resume_text,
                resume.summary,
                " ".join(resume.hard_skills),
                " ".join(resume.leadership_signals),
                " ".join(resume.quantified_achievements),
            ]
        )
    )
    keyword_groups = group_job_keywords(jd)
    recruiter_queries = derive_recruiter_queries(jd)
    matched_queries = [query for query in recruiter_queries if _query_visible(query, searchable_resume)]
    visibility_score = _visibility_score(
        parseability_score=parseability_score,
        keyword_match_score=keyword_match_score,
        title_alignment_score=title_alignment_score,
        leadership_alignment_score=leadership_alignment_score,
        query_coverage=(len(matched_queries) / max(len(recruiter_queries), 1)) * 100,
    )
    why_not_found = _why_not_found(
        missing_keywords=missing_keywords,
        keyword_groups=keyword_groups,
        parseability_score=parseability_score,
        title_alignment_score=title_alignment_score,
        query_coverage=(len(matched_queries) / max(len(recruiter_queries), 1)) * 100,
        domain_fit=domain_fit or {},
    )
    return {
        "visibility_score": visibility_score,
        "recruiter_match_score": round((len(matched_queries) / max(len(recruiter_queries), 1)) * 100, 2),
        "ats_parse_score": round(parseability_score, 2),
        "keyword_groups": keyword_groups,
        "recruiter_queries": recruiter_queries,
        "matched_recruiter_queries": matched_queries,
        "compatibility_scores": compatibility_scores(parseability_score, visibility_score),
        "what_ats_sees": what_ats_sees(resume, jd),
        "what_recruiter_sees": what_recruiter_sees(resume, jd, matched_queries),
        "why_not_found": why_not_found,
        "top_fixes": top_visibility_fixes(why_not_found, missing_keywords),
        "domain_fit": domain_fit or {},
    }


def group_job_keywords(jd: JobDescriptionData) -> dict[str, list[str]]:
    tools = set(jd.tools_and_technologies)
    leadership = set(jd.leadership_indicators)
    domains = set(jd.domain_keywords + jd.operational_expectations)
    all_terms = list(dict.fromkeys(jd.must_have_skills + jd.nice_to_have_skills + jd.tools_and_technologies))
    return {
        "hard_skills": [term for term in all_terms if term not in tools and term not in leadership and len(term.split()) <= 4][:12],
        "titles": _title_terms(jd.role_title),
        "domain_terms": list(dict.fromkeys(domains))[:10],
        "tools": list(dict.fromkeys(tools))[:10],
        "impact_kpi_terms": [term for term in all_terms if any(token in term for token in ["kpi", "cost", "quality", "yield", "downtime", "productivity"])][:8],
        "leadership_terms": list(dict.fromkeys(leadership))[:10],
    }


def derive_recruiter_queries(jd: JobDescriptionData) -> list[str]:
    title_terms = _title_terms(jd.role_title)
    priority_terms = list(dict.fromkeys(title_terms + jd.must_have_skills[:8] + jd.tools_and_technologies[:4] + jd.leadership_indicators[:4]))
    queries: list[str] = []
    for term in priority_terms:
        normalized = normalize_hebrew_text(term)
        if normalized and normalized not in queries:
            queries.append(normalized)
    for hebrew, aliases in HEBREW_TITLE_ALIASES.items():
        if any(alias in " ".join(queries) for alias in aliases) and hebrew not in queries:
            queries.append(hebrew)
    return queries[:14]


def compatibility_scores(parseability_score: float, visibility_score: float) -> dict[str, float]:
    return {
        "workday_like": round(parseability_score * 0.65 + visibility_score * 0.35, 2),
        "greenhouse_like": round(parseability_score * 0.45 + visibility_score * 0.55, 2),
        "legacy_parser_like": round(parseability_score * 0.8 + visibility_score * 0.2, 2),
        "israeli_ats_like": round(parseability_score * 0.55 + visibility_score * 0.45, 2),
    }


def what_ats_sees(resume: ResumeStructuredData, jd: JobDescriptionData) -> list[str]:
    titles = [item.job_title for item in resume.experience if item.job_title][:4]
    skills = resume.hard_skills[:8]
    facts = []
    if resume.contact.email:
        facts.append("Contact email was parsed.")
    if titles:
        facts.append(f"Visible titles: {', '.join(titles)}.")
    if skills:
        facts.append(f"Indexed skills include: {', '.join(skills)}.")
    if resume.quantified_achievements:
        facts.append(f"Quantified impact lines found: {len(resume.quantified_achievements)}.")
    if jd.role_title:
        inference_note = " (inferred)" if getattr(jd, "role_title_inferred", False) else ""
        facts.append(f"Target role parsed as: {jd.role_title}{inference_note}.")
    return facts[:6]


def what_recruiter_sees(resume: ResumeStructuredData, jd: JobDescriptionData, matched_queries: list[str]) -> list[str]:
    signals = []
    if matched_queries:
        signals.append(f"Likely searchable signals: {', '.join(matched_queries[:6])}.")
    if resume.leadership_signals:
        signals.append("Leadership/ownership language is present, but should be near the top if this is a management role.")
    if jd.seniority:
        signals.append(f"Role seniority signal: {jd.seniority}.")
    if not matched_queries:
        signals.append("Recruiter search visibility is weak because core title and skill queries are not clearly present.")
    return signals[:5]


def top_visibility_fixes(why_not_found: list[str], missing_keywords: list[str]) -> list[str]:
    fixes = []
    if missing_keywords:
        fixes.append(f"Add truthful wording for the top missing role signals: {', '.join(missing_keywords[:5])}.")
    fixes.extend(why_not_found[:3])
    fixes.append("Move title fit, management scope, tools, and measurable outcomes into the summary and first experience block.")
    return list(dict.fromkeys(fixes))[:6]


def _visibility_score(
    parseability_score: float,
    keyword_match_score: float,
    title_alignment_score: float,
    leadership_alignment_score: float,
    query_coverage: float,
) -> float:
    score = (
        parseability_score * 0.25
        + keyword_match_score * 0.25
        + title_alignment_score * 0.2
        + leadership_alignment_score * 0.15
        + query_coverage * 0.15
    )
    return round(max(0.0, min(score, 100.0)), 2)


def _why_not_found(
    missing_keywords: list[str],
    keyword_groups: dict[str, list[str]],
    parseability_score: float,
    title_alignment_score: float,
    query_coverage: float,
    domain_fit: dict[str, object],
) -> list[str]:
    reasons = []
    if parseability_score < 75:
        reasons.append("ATS parsing reliability is not high enough; simplify layout and section headings.")
    if title_alignment_score < 60:
        reasons.append("The target title is not visible enough for recruiter title searches.")
    if query_coverage < 45:
        reasons.append("Too few likely recruiter search queries are clearly present in the resume.")
    if missing_keywords:
        reasons.append("Important role keywords are missing or phrased differently from the job description.")
    critical_absent = list(domain_fit.get("critical_absent") or [])
    if critical_absent:
        reasons.append(f"Domain-specific hard requirements are not evidenced: {', '.join(critical_absent[:5])}.")
    if domain_fit.get("penalty_applied"):
        reasons.extend(str(reason) for reason in list(domain_fit.get("penalty_reasons") or [])[:2])
    if not keyword_groups.get("impact_kpi_terms"):
        reasons.append("The job description implies measurable ownership, but KPI/impact terms are thin.")
    return reasons[:6]


def _query_visible(query: str, searchable_resume: str) -> bool:
    if not query:
        return False
    if query in searchable_resume:
        return True
    tokens = [token for token in re.findall(r"[a-z0-9\u0590-\u05ff]+", query) if len(token) > 2]
    if not tokens:
        return False
    return len([token for token in tokens if token in searchable_resume]) / len(tokens) >= 0.65


def _title_terms(role_title: str) -> list[str]:
    cleaned = normalize_hebrew_text(role_title)
    pieces = [cleaned]
    for sep in [" - ", " | ", ",", "/"]:
        pieces.extend(part.strip() for part in cleaned.split(sep) if part.strip())
    return [piece for piece in dict.fromkeys(pieces) if 3 <= len(piece) <= 80][:5]
