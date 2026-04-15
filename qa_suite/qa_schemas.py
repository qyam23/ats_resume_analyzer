from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


QAStatus = Literal["pass", "warning", "fail"]


class ResumeVariant(BaseModel):
    id: str
    fit_profile: str = ""
    target_role_he: str = ""
    target_role_en: str = ""
    core_positioning_he: str = ""
    core_positioning_en: str = ""
    priority_keywords: list[str] = Field(default_factory=list)
    qa_expected_strength: str = ""


class JobDescriptionCase(BaseModel):
    id: str
    company: str = ""
    role: str = ""
    location: str = ""
    fit_strength: str = ""
    language_profile: str = ""
    why: str = ""
    link: str = ""


class QAMatrixCase(BaseModel):
    case_id: str
    resume_variant_id: str
    jd_id: str
    expected_fit_band: str
    expected_decision_tendency: str = ""
    source_languages: list[str] = Field(default_factory=list)
    review_focus: list[str] = Field(default_factory=list)


class QAActualResult(BaseModel):
    decision: str = ""
    final_ats_score: float = 0.0
    visibility_score: float = 0.0
    recruiter_match_score: float = 0.0
    ats_parse_score: float = 0.0
    missing_keywords: list[str] = Field(default_factory=list)
    why_not_found: list[str] = Field(default_factory=list)
    top_fixes: list[str] = Field(default_factory=list)
    what_ats_sees: list[str] = Field(default_factory=list)
    what_recruiter_sees: list[str] = Field(default_factory=list)
    career_suggestions: list[str] = Field(default_factory=list)
    transformed_blocks_count: int = 0
    rewrite_preview_available: bool = False
    premium_mode: str = ""
    job_search_plan_available: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


class QAChecks(BaseModel):
    decision_match: bool = False
    fit_band_reasonable: bool = False
    visibility_reasonable: bool = False
    parse_reasonable: bool = False
    signals_present: bool = False
    product_outputs_present: bool = False
    career_outputs_present: bool = False


class QAEvaluationResult(BaseModel):
    case_id: str
    resume_variant_id: str
    job_id: str
    expected_fit_band: str
    expected_decision_tendency: str = ""
    source_languages: list[str] = Field(default_factory=list)
    actual: QAActualResult
    checks: QAChecks
    status: QAStatus
    notes: list[str] = Field(default_factory=list)
    failure_reasons: list[str] = Field(default_factory=list)


class QARunSummary(BaseModel):
    run_id: str
    created_at: str
    total_cases: int = 0
    passed: int = 0
    warnings: int = 0
    failed: int = 0
    by_fit_band: dict[str, dict[str, int]] = Field(default_factory=dict)
    by_language: dict[str, dict[str, int]] = Field(default_factory=dict)
    cases: list[QAEvaluationResult] = Field(default_factory=list)
