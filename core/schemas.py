from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    full_name: str = ""
    phone: str = ""
    email: str = ""
    location: str = ""


class ExperienceEntry(BaseModel):
    job_title: str
    employer: str = ""
    date_range: str = ""
    achievements: list[str] = Field(default_factory=list)


class ResumeStructuredData(BaseModel):
    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: str = ""
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    hard_skills: list[str] = Field(default_factory=list)
    leadership_signals: list[str] = Field(default_factory=list)
    quantified_achievements: list[str] = Field(default_factory=list)
    raw_sections: dict[str, str] = Field(default_factory=dict)


class ParsedDocument(BaseModel):
    filename: str
    file_type: str
    text: str
    detected_language: str
    selectable_text: bool = True
    ocr_used: bool = False
    warnings: list[str] = Field(default_factory=list)
    structured: ResumeStructuredData | None = None
    formatting_signals: dict[str, Any] = Field(default_factory=dict)


class JobDescriptionData(BaseModel):
    role_title: str = ""
    role_title_inferred: bool = False
    company_name: str = ""
    seniority: str = ""
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    domain_keywords: list[str] = Field(default_factory=list)
    leadership_indicators: list[str] = Field(default_factory=list)
    tools_and_technologies: list[str] = Field(default_factory=list)
    operational_expectations: list[str] = Field(default_factory=list)
    raw_text: str = ""
    detected_language: str = ""


class ScoreBreakdown(BaseModel):
    parseability_score: float
    consistency_score: float
    keyword_match_score: float
    semantic_match_score: float
    leadership_alignment_score: float
    quantified_impact_score: float
    final_ats_score: float


class ConsistencyMismatch(BaseModel):
    field: str
    pdf_value: str
    docx_value: str
    severity: str


class RecommendationBlock(BaseModel):
    english: list[str] = Field(default_factory=list)
    hebrew: list[str] = Field(default_factory=list)


class PipelineEvent(BaseModel):
    step: str
    status: str
    detail: str
    elapsed_ms: int


class CompanyResearch(BaseModel):
    company_name: str = ""
    company_snapshot: str = ""
    stability_signal: str = ""
    role_market_age_days: int | None = None
    reposted_role_signal: bool = False
    posting_evidence_count: int = 0
    sources: list[str] = Field(default_factory=list)
    notes_en: list[str] = Field(default_factory=list)
    notes_he: list[str] = Field(default_factory=list)


class RuntimeSettingsSummary(BaseModel):
    llm_provider: str = "local_llm"
    enable_llm_enhancements: bool = True
    enable_web_research: bool = True
    api_only_mode: bool = True
    hf_model: str = "Qwen/Qwen2.5-7B-Instruct"
    openai_model: str = "gpt-5.1"
    openai_reasoning_effort: str = "high"
    gemini_model: str = "gemini-2.5-flash"
    local_llm_base_url: str = ""
    local_llm_model: str = "gemma3:4b"
    hf_key_masked: str = ""
    openai_key_masked: str = ""
    gemini_key_masked: str = ""
    default_resume_he_path: str = ""
    default_resume_en_path: str = ""
    default_resume_he_ready: bool = False
    default_resume_en_ready: bool = False


class TokenUsage(BaseModel):
    provider: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    usage_available: bool = False
    estimated_input_cost_usd: float = 0.0
    estimated_output_cost_usd: float = 0.0
    estimated_total_cost_usd: float = 0.0
    pricing_reference: str = ""


class SessionUsage(BaseModel):
    analyses_count: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    provider: str = ""
    model: str = ""
    estimated_input_cost_usd: float = 0.0
    estimated_output_cost_usd: float = 0.0
    estimated_total_cost_usd: float = 0.0


class PreflightRequest(BaseModel):
    pdf_name: str = ""
    docx_name: str = ""
    jd_text_present: bool = False
    jd_image_name: str = ""
    validate_provider_connection: bool = True
    fixed_resume_slot: str = ""


class PreflightCheck(BaseModel):
    key: str
    label: str
    status: str
    detail: str


class PreflightReport(BaseModel):
    ready: bool = False
    provider: str = ""
    model: str = ""
    checks: list[PreflightCheck] = Field(default_factory=list)
    recommended_action: str = ""


class FailureReport(BaseModel):
    report_id: str
    created_at: str
    stage: str
    error_summary: str
    provider: str = ""
    model: str = ""
    file_inputs: dict[str, str] = Field(default_factory=dict)
    runtime_settings: dict[str, Any] = Field(default_factory=dict)
    timeline: list[PipelineEvent] = Field(default_factory=list)
    report_path: str = ""


class AnalysisResult(BaseModel):
    scores: ScoreBreakdown
    executive_summary: dict[str, str]
    detailed_diagnostics: dict[str, Any]
    consistency_mismatches: list[ConsistencyMismatch]
    recommendations: RecommendationBlock
    company_research: CompanyResearch = Field(default_factory=CompanyResearch)
    timeline: list[PipelineEvent] = Field(default_factory=list)
    runtime_settings: RuntimeSettingsSummary = Field(default_factory=RuntimeSettingsSummary)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    session_usage: SessionUsage = Field(default_factory=SessionUsage)
    json_report_path: str
    markdown_report_path: str
