from __future__ import annotations

from time import perf_counter

from config.security import sanitized_error
from config.settings import get_settings
from core.ats_checks import evaluate_ats_hygiene
from core.consistency import compare_resume_versions
from core.exceptions import AnalysisPipelineError
from core.extractors import extract_resume_structure
from core.matching import (
    compute_keyword_match,
    compute_leadership_alignment,
    compute_quantified_impact,
    compute_semantic_match,
    compute_title_alignment,
)
from core.parsers.docx_parser import extract_docx
from core.parsers.jd_parser import parse_job_description, parse_job_description_image
from core.parsers.pdf_parser import extract_pdf
from core.pricing import apply_cost_estimate
from core.prompt_templates import build_career_alignment_prompt
from core.recommendations import build_recommendations
from core.reporting import write_reports
from core.schemas import AnalysisResult, CompanyResearch, ParsedDocument, PipelineEvent
from core.scoring import build_final_scores
from core.services.research import WebResearchService
from core.services.session_usage import SESSION_USAGE_TRACKER
from core.services.settings_service import SettingsService
from providers.factory import get_llm_provider


class ATSAnalyzerService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.provider = get_llm_provider()
        self.research_service = WebResearchService()
        self.settings_service = SettingsService()

    def analyze(
        self,
        pdf_bytes: bytes | None = None,
        pdf_name: str = "",
        docx_bytes: bytes | None = None,
        docx_name: str = "",
        jd_text: str = "",
        jd_image: bytes | None = None,
        public_mode: bool = False,
        use_provider_insights: bool = True,
    ) -> AnalysisResult:
        self.settings = get_settings()
        self.provider = get_llm_provider()
        start = perf_counter()
        timeline: list[PipelineEvent] = []
        current_stage = "ingestion"

        try:
            pdf_doc = self._parse_optional_pdf(pdf_bytes, pdf_name)
            docx_doc = self._parse_optional_docx(docx_bytes, docx_name)
            primary_doc = docx_doc or pdf_doc
            if primary_doc is None:
                raise ValueError("At least one resume file must be provided.")
            self._mark(timeline, start, "ingestion", "completed", "Resume ingestion completed for the available file set.")

            current_stage = "extraction"
            for document in [pdf_doc, docx_doc]:
                if document:
                    document.structured = extract_resume_structure(document.text)
            self._mark(timeline, start, "extraction", "completed", "Structured contact, experience, skills, and impact signals were extracted.")

            current_stage = "job-description"
            jd = parse_job_description(jd_text) if jd_text.strip() else parse_job_description_image(jd_image or b"")
            self._mark(timeline, start, "job-description", "completed", "The job description was parsed into role, skills, seniority, and operating signals.")

            current_stage = "ats-hygiene"
            pdf_signals: dict[str, object] = {"issues": []}
            docx_signals: dict[str, object] = {"issues": []}
            parseability_values: list[float] = []
            if pdf_doc:
                parseability_score_pdf, pdf_signals = evaluate_ats_hygiene(pdf_doc)
                parseability_values.append(parseability_score_pdf)
            if docx_doc:
                parseability_score_docx, docx_signals = evaluate_ats_hygiene(docx_doc)
                parseability_values.append(parseability_score_docx)
            parseability_score = round(sum(parseability_values) / max(len(parseability_values), 1), 2)
            self._mark(timeline, start, "ats-hygiene", "completed", "ATS formatting risks were checked across the uploaded resume version(s).")

            current_stage = "consistency"
            if pdf_doc and docx_doc:
                consistency_score, mismatches = compare_resume_versions(pdf_doc, docx_doc)
                consistency_detail = "PDF and DOCX were compared for candidate-side consistency."
            else:
                consistency_score, mismatches = 100.0, []
                consistency_detail = "Single-file mode was used, so consistency scoring defaulted to 100."
            self._mark(timeline, start, "consistency", "completed", consistency_detail)

            current_stage = "matching"
            keyword_match_score, missing_keywords = compute_keyword_match(primary_doc.structured, jd, primary_doc.text)
            semantic_match_score = compute_semantic_match(primary_doc.text, jd.raw_text)
            leadership_alignment_score = compute_leadership_alignment(primary_doc.structured, jd, primary_doc.text)
            quantified_impact_score = compute_quantified_impact(primary_doc.structured, jd)
            title_alignment_score = compute_title_alignment(primary_doc.structured, jd, primary_doc.text)
            self._mark(timeline, start, "matching", "completed", "Keyword, semantic, leadership, title, and impact matching finished.")

            current_stage = "web-research"
            company_research = CompanyResearch()
            if self.settings.enable_web_research:
                company_research = self.research_service.analyze_market(jd)
                self._mark(timeline, start, "web-research", "completed", "Public web signals were collected for company stability and job-market timing.")
            else:
                self._mark(timeline, start, "web-research", "skipped", "Web research is disabled in runtime settings.")

            current_stage = "scoring"
            scores = build_final_scores(
                parseability_score,
                consistency_score,
                keyword_match_score,
                semantic_match_score,
                leadership_alignment_score,
                quantified_impact_score,
                title_alignment_score,
            )
            recommendations = build_recommendations(
                resume=primary_doc.structured,
                jd=jd,
                missing_keywords=missing_keywords,
                formatting_issues=(pdf_signals["issues"] + docx_signals["issues"])[:8],
                mismatches=mismatches,
            )

            current_stage = "ai-insights"
            provider_note = ""
            token_usage = self.provider.last_usage()
            provider_warning = ""
            if not use_provider_insights:
                provider_warning = "Public mode uses local deterministic analysis only; no external AI API was called."
                self._mark(timeline, start, "ai-insights", "skipped", provider_warning)
            elif self.provider.is_available():
                try:
                    provider_note = self.provider.explain(
                        build_career_alignment_prompt(
                            candidate_name=primary_doc.structured.contact.full_name,
                            target_role=jd.role_title,
                            final_score=scores.final_ats_score,
                            match_summary=(
                                f"keyword match {scores.keyword_match_score}, semantic match {scores.semantic_match_score}, "
                                f"leadership alignment {scores.leadership_alignment_score}, title alignment {title_alignment_score}"
                            ),
                            missing_keywords=missing_keywords,
                            company_snapshot=company_research.company_snapshot,
                        ),
                        reasoning_effort="medium" if public_mode else None,
                        max_output_tokens=900 if public_mode else 2200,
                        timeout_seconds=75 if public_mode else 180,
                    )
                    token_usage = self.provider.last_usage()
                    self._mark(timeline, start, "ai-insights", "completed", f"External provider '{self.provider.provider_name()}' added higher-level commentary.")
                except Exception as exc:
                    provider_warning = self._provider_warning(exc)
                    recommendations.english.insert(0, f"Provider-based rewrite insights were skipped: {provider_warning}. Core ATS scoring still completed successfully.")
                    recommendations.hebrew.insert(0, f"תובנות הניסוח של ספק ה-AI דולגו: {provider_warning}. ניתוח ה-ATS המרכזי הושלם בהצלחה.")
                    self._mark(
                        timeline,
                        start,
                        "ai-insights",
                        "skipped",
                        f"External provider '{self.provider.provider_name()}' did not finish. Continuing with deterministic analysis only.",
                    )
            else:
                self._mark(timeline, start, "ai-insights", "skipped", "No external provider was enabled, so only local analysis was used.")
            token_usage = apply_cost_estimate(token_usage)
            session_usage = SESSION_USAGE_TRACKER.record(token_usage)

            current_stage = "reporting"
            result = AnalysisResult(
                scores=scores,
                executive_summary={
                    "en": (
                        f"Final ATS score: {scores.final_ats_score}/100. Parseability is {scores.parseability_score}, "
                        f"consistency is {scores.consistency_score}, and keyword coverage is {scores.keyword_match_score}. {provider_note}".strip()
                    ),
                    "he": (
                        f"׳¦׳™׳•׳ ATS ׳¡׳•׳₪׳™: {scores.final_ats_score}/100. ׳¦׳™׳•׳ ׳”׳§׳¨׳™׳׳•׳× ׳׳׳¢׳¨׳›׳•׳× ATS ׳”׳•׳ {scores.parseability_score}, "
                        f"׳¦׳™׳•׳ ׳”׳¢׳§׳‘׳™׳•׳× ׳‘׳™׳ ׳”׳§׳‘׳¦׳™׳ ׳”׳•׳ {scores.consistency_score}, ׳•׳›׳™׳¡׳•׳™ ׳׳™׳׳•׳× ׳”׳׳₪׳×׳— ׳”׳•׳ {scores.keyword_match_score}."
                    ),
                },
                detailed_diagnostics={
                    "pdf_warnings": pdf_doc.warnings if pdf_doc else [],
                    "docx_warnings": docx_doc.warnings if docx_doc else [],
                    "pdf_formatting": pdf_signals,
                    "docx_formatting": docx_signals,
                    "pdf_structured": pdf_doc.structured.model_dump() if pdf_doc and pdf_doc.structured else {},
                    "docx_structured": docx_doc.structured.model_dump() if docx_doc and docx_doc.structured else {},
                    "primary_resume_file": primary_doc.filename,
                    "job_description": jd.model_dump(),
                    "missing_keywords": missing_keywords,
                    "title_alignment_score": title_alignment_score,
                    "provider_warning": provider_warning,
                },
                consistency_mismatches=mismatches,
                recommendations=recommendations,
                company_research=company_research,
                timeline=timeline,
                runtime_settings=self.settings_service.get_runtime_settings_summary(),
                token_usage=token_usage,
                session_usage=session_usage,
                json_report_path="",
                markdown_report_path="",
            )
            json_path, markdown_path = write_reports(result, self.settings.reports_dir)
            result.json_report_path = json_path
            result.markdown_report_path = markdown_path
            return result
        except Exception as exc:
            self._mark(timeline, start, current_stage, "failed", f"Pipeline stopped during {current_stage}.")
            raise AnalysisPipelineError(current_stage, sanitized_error(str(exc)), timeline) from exc

    def _mark(self, timeline: list[PipelineEvent], start: float, step: str, status: str, detail: str) -> None:
        timeline.append(
            PipelineEvent(
                step=step,
                status=status,
                detail=detail,
                elapsed_ms=int((perf_counter() - start) * 1000),
            )
        )

    def _parse_optional_pdf(self, pdf_bytes: bytes | None, pdf_name: str) -> ParsedDocument | None:
        if not pdf_bytes:
            return None
        return extract_pdf(pdf_bytes, pdf_name or "resume.pdf")

    def _parse_optional_docx(self, docx_bytes: bytes | None, docx_name: str) -> ParsedDocument | None:
        if not docx_bytes:
            return None
        return extract_docx(docx_bytes, docx_name or "resume.docx")

    def _provider_warning(self, exc: Exception) -> str:
        message = sanitized_error(str(exc)) or "external provider did not return a usable response"
        lower = message.lower()
        if "incomplete" in lower:
            return "OpenAI returned an incomplete answer, usually because the output limit was reached or the reasoning task was too long"
        if "timed out" in lower or "timeout" in lower:
            return "OpenAI did not finish before the local timeout"
        return message
