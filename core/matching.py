from __future__ import annotations

from functools import lru_cache

import numpy as np
from rapidfuzz import fuzz
from sentence_transformers import CrossEncoder, SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config.settings import get_settings
from core.extractors import extract_top_keywords
from core.schemas import JobDescriptionData, ResumeStructuredData


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    settings = get_settings()
    return SentenceTransformer(settings.embedding_model, local_files_only=True)


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoder | None:
    settings = get_settings()
    if not settings.reranker_model:
        return None
    return CrossEncoder(settings.reranker_model, trust_remote_code=True)


SYNONYM_GROUPS = {
    "engineering leadership": ["senior engineering leader", "led engineering", "leading engineering", "managed"],
    "engineering management": ["senior engineering leader", "managed", "management interfaces"],
    "manufacturing engineering": ["manufacturing process", "production lines", "manufacturing systems"],
    "manufacturing systems": ["production systems", "production lines", "manufacturing processes"],
    "industrial operations": ["industrial experience", "production floor", "operations"],
    "industrial projects": ["industrial environments", "plants and production lines", "projects in israel and abroad"],
    "process engineering": ["process engineer", "process improvement", "process stability"],
    "plant engineering": ["plants", "production lines", "plant upgrade"],
    "factory execution": ["production floor", "on-site execution", "implementation"],
    "production readiness": ["transfer of products from development to production", "production floor", "process stabilization"],
    "automation leadership": ["automation", "control systems", "led projects"],
    "technical operations": ["technological support", "technical stakeholders", "operations"],
    "vendor management": ["supplier coordination", "supplier negotiations", "suppliers"],
    "supplier management": ["supplier coordination", "supplier negotiations", "suppliers"],
    "contractor management": ["subcontractors", "contractors"],
    "budget management": ["budget", "cost reduction", "supplier negotiations"],
    "stakeholder management": ["stakeholders", "interfaces", "management interfaces"],
    "cross-functional teams": ["cross-functional teams", "production teams", "technological teams"],
    "commissioning": ["start-up", "implementation", "process stabilization", "on-site implementation"],
    "delivery": ["delivery", "implementation", "milestones", "handover"],
    "requirements analysis": ["need definition", "requirements", "planning"],
    "system design": ["system view", "infrastructure planning", "engineering solutions"],
    "implementation": ["implemented", "implementation", "on-site implementation"],
    "cost reduction": ["costs", "reduction", "reduce waste"],
    "quality improvement": ["quality", "improved product quality"],
    "downtime reduction": ["downtime", "technical failures"],
    "productivity improvement": ["output", "throughput", "performance"],
}


def compute_keyword_match(resume: ResumeStructuredData, jd: JobDescriptionData, resume_text: str = "") -> tuple[float, list[str]]:
    resume_terms = {_normalize(item) for item in resume.hard_skills}
    resume_terms.update(_normalize(keyword) for keyword in extract_top_keywords(resume.summary + "\n" + "\n".join(resume.quantified_achievements)))
    searchable_resume = _normalize(
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
    target_terms = {item.lower() for item in jd.must_have_skills + jd.nice_to_have_skills + jd.tools_and_technologies}
    if not target_terms:
        return 50.0, []
    covered = []
    missing = []
    partial_credit = 0.0
    for term in sorted(_normalize(item) for item in target_terms):
        coverage = _term_coverage(term, resume_terms, searchable_resume)
        if coverage >= 0.65:
            covered.append(term)
        else:
            missing.append(term)
        partial_credit += coverage
    return round((partial_credit / len(target_terms)) * 100, 2), missing[:20]


def compute_semantic_match(resume_text: str, jd_text: str) -> float:
    try:
        model = get_embedding_model()
        embeddings = model.encode([resume_text[:4000], jd_text[:4000]], normalize_embeddings=True)
        score = float(np.dot(embeddings[0], embeddings[1]) * 100)
        reranker = get_reranker()
        if reranker:
            rerank_score = float(reranker.predict([(jd_text[:1200], resume_text[:2400])])[0]) * 20
            score = min(100.0, max(0.0, (score * 0.7) + rerank_score))
    except Exception:
        vectorizer = TfidfVectorizer(max_features=1200, ngram_range=(1, 2), stop_words="english")
        matrix = vectorizer.fit_transform([resume_text[:6000], jd_text[:6000]])
        score = float(cosine_similarity(matrix[0], matrix[1])[0][0] * 100)
    return round(max(0.0, min(score, 100.0)), 2)


def compute_title_alignment(resume: ResumeStructuredData, jd: JobDescriptionData, resume_text: str = "") -> float:
    titles = " ".join(item.job_title.lower() for item in resume.experience)
    searchable_resume = _normalize(f"{titles}\n{resume_text}\n{resume.summary}")
    role = jd.role_title.lower()
    if not role:
        return 50.0
    if role in titles:
        return 100.0
    role_tokens = {token for token in re_tokens(role) if len(token) > 3}
    resume_tokens = set(re_tokens(searchable_resume))
    if {"engineering", "manager"} <= role_tokens and "engineering" in resume_tokens and any(token in resume_tokens for token in ["leader", "managed", "leading", "management"]):
        return 85.0
    if "engineering" in role_tokens and "engineering" in resume_tokens and any(token in resume_tokens for token in ["project", "manufacturing", "process", "automation"]):
        return 75.0
    if any(token in titles for token in role.split() if len(token) > 3):
        return 70.0
    overlap = len(role_tokens & resume_tokens) / max(len(role_tokens), 1)
    if overlap >= 0.4:
        return 60.0
    if overlap >= 0.2:
        return 40.0
    return 20.0


def compute_leadership_alignment(resume: ResumeStructuredData, jd: JobDescriptionData, resume_text: str = "") -> float:
    if not jd.leadership_indicators:
        return 60.0
    searchable_resume = _normalize(f"{resume_text}\n" + "\n".join(resume.leadership_signals))
    signal_map = {
        "lead": ["lead", "led", "leading", "leader", "headed"],
        "manage": ["manage", "managed", "managing", "management"],
        "ownership": ["owned", "ownership", "responsible"],
        "mentor": ["mentor", "mentored", "guided", "guidance"],
        "stakeholder": ["stakeholder", "stakeholders", "interfaces"],
        "supplier": ["supplier", "suppliers", "vendor"],
        "contractor": ["contractor", "contractors", "subcontractors"],
        "budget": ["budget", "cost", "costs"],
    }
    overlap = 0
    for signal in jd.leadership_indicators:
        terms = signal_map.get(signal, [signal])
        if any(_phrase_present(term, searchable_resume) for term in terms):
            overlap += 1
    return round((overlap / max(len(jd.leadership_indicators), 1)) * 100, 2)


def compute_quantified_impact(resume: ResumeStructuredData, jd: JobDescriptionData) -> float:
    base = min(len(resume.quantified_achievements) * 15, 100)
    if jd.operational_expectations:
        base += min(len(jd.operational_expectations) * 2, 10)
    return round(min(base, 100), 2)


def _normalize(value: str) -> str:
    return " ".join(re_tokens(value))


def re_tokens(value: str) -> list[str]:
    import re

    return re.findall(r"[a-z0-9\u0590-\u05FF]+", value.lower())


def _phrase_present(term: str, text: str) -> bool:
    normalized = _normalize(term)
    return bool(normalized and normalized in text)


def _term_coverage(term: str, resume_terms: set[str], resume_text: str) -> float:
    if not term:
        return 0.0
    if term in resume_terms or _phrase_present(term, resume_text):
        return 1.0
    if any(_phrase_present(alias, resume_text) for alias in SYNONYM_GROUPS.get(term, [])):
        return 0.9
    token_list = [token for token in re_tokens(term) if len(token) > 2]
    if not token_list:
        return 0.0
    resume_token_set = set(re_tokens(resume_text))
    token_overlap = len(set(token_list) & resume_token_set) / len(set(token_list))
    fuzzy_score = max((fuzz.token_set_ratio(term, skill) / 100 for skill in resume_terms), default=0.0)
    if fuzzy_score >= 0.88:
        return max(0.8, token_overlap)
    if token_overlap >= 0.75 and len(token_list) >= 2:
        return 0.75
    if token_overlap >= 0.5 and len(token_list) >= 3:
        return 0.45
    return min(token_overlap * 0.4, 0.35)
