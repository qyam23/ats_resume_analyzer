from contextlib import asynccontextmanager
from pathlib import Path
import re
from typing import Optional
from urllib.parse import urlparse

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config.local_settings import LocalSettingsPayload
from config.logging_utils import get_logger
from config.security import enforce_upload_size, sanitized_error, validate_upload
from config.settings import BASE_DIR, get_settings
from core.exceptions import AnalysisPipelineError
from core.jd_cleaner import clean_job_description_text
from core.parsers.docx_parser import extract_docx
from core.parsers.pdf_parser import extract_pdf
from core.reporting import build_failure_report
from core.schemas import PreflightCheck, PreflightReport, PreflightRequest
from core.services.analyzer import ATSAnalyzerService
from core.services.settings_service import SettingsService
from providers.factory import get_llm_provider


settings = get_settings()
logger = get_logger("ats.api")
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])


@asynccontextmanager
async def lifespan(_: FastAPI):
    current = get_settings()
    logger.info("ATS Resume Analyzer API starting on %s:%s", current.api_host, current.runtime_port)
    yield


app = FastAPI(title="ATS Resume Analyzer API", default_response_class=ORJSONResponse, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
PUBLIC_SITE_DIR = BASE_DIR / "public_site"
if PUBLIC_SITE_DIR.exists():
    app.mount("/assets", StaticFiles(directory=PUBLIC_SITE_DIR), name="public_assets")
service = ATSAnalyzerService()
settings_service = SettingsService()


def _active_model_name() -> str:
    current = get_settings()
    if current.llm_provider == "openai":
        return current.openai_model
    if current.llm_provider == "gemini":
        return current.gemini_model
    if current.llm_provider == "huggingface":
        return current.hf_model
    if current.llm_provider == "local_llm":
        return current.local_llm_model
    return "local-rules"


def _require_internal_endpoints() -> None:
    if not get_settings().enable_internal_endpoints:
        raise HTTPException(status_code=404, detail="Not found")


@app.get("/", response_class=FileResponse)
def public_home():
    index_path = PUBLIC_SITE_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Public site is not built yet.")
    return FileResponse(index_path)


@app.get("/health")
def health() -> dict[str, object]:
    current = get_settings()
    return {
        "status": "ok",
        "python_target": "3.10",
        "llm_provider": current.llm_provider,
        "llm_enhancements_enabled": current.enable_llm_enhancements,
        "web_research_enabled": current.enable_web_research,
        "api_only_mode": current.api_only_mode,
        "ocr_enabled": current.enable_ocr,
    }


@app.get("/settings")
def get_runtime_settings():
    _require_internal_endpoints()
    return settings_service.get_runtime_settings_summary().model_dump()


@app.post("/settings")
def save_runtime_settings(payload: LocalSettingsPayload):
    _require_internal_endpoints()
    return settings_service.save_runtime_settings(payload).model_dump()


def _load_fixed_resume(slot: str) -> tuple[bytes | None, str]:
    current = get_settings()
    if slot == "he":
        path_value = current.default_resume_he_path
    elif slot == "en":
        path_value = current.default_resume_en_path
    else:
        return None, ""
    if not path_value:
        raise HTTPException(status_code=400, detail=f"No fixed resume is configured for slot '{slot}'.")
    path = Path(path_value)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=400, detail=f"Configured fixed resume was not found: {path_value}")
    return path.read_bytes(), path.name


def _extract_text_from_url(url: str) -> tuple[str, str]:
    if not url.strip():
        return "", ""
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Job URL must start with http:// or https://")
    try:
        response = httpx.get(
            url.strip(),
            timeout=15,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 ATS Resume Analyzer"},
        )
        response.raise_for_status()
    except Exception as exc:
        return "", f"Could not extract job text from URL: {sanitized_error(str(exc))}"
    html = response.text
    html = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 200:
        return "", "URL was reachable, but not enough readable job text was found."
    return clean_job_description_text(text[:15000]), ""


def _public_result_payload(result: object) -> dict[str, object]:
    data = result.model_dump()
    diagnostics = data.get("detailed_diagnostics", {})
    scores = data.get("scores", {})
    missing_keywords = diagnostics.get("missing_keywords", [])
    recommendations = data.get("recommendations", {})
    primary_resume = diagnostics.get("docx_structured") or diagnostics.get("pdf_structured") or {}
    job_description = diagnostics.get("job_description", {})
    final_score = float(scores.get("final_ats_score", 0) or 0)
    provider_warning = diagnostics.get("provider_warning", "")
    analysis_mode = (
        "local_no_api"
        if provider_warning.startswith("Public mode uses local")
        else "ai_enhancement_skipped"
        if provider_warning
        else "provider_enhanced"
    )
    if final_score >= 78:
        verdict = "Strong fit"
    elif final_score >= 62:
        verdict = "Good fit after targeted edits"
    elif final_score >= 45:
        verdict = "Needs resume tailoring before applying"
    else:
        verdict = "Low ATS pass likelihood"
    return {
        "verdict": verdict,
        "final_ats_score": final_score,
        "scores": scores,
        "summary": (
            f"{verdict}. ATS score is {final_score:.1f}/100. "
            f"Focus first on {len(missing_keywords)} missing keywords and the weakest score areas."
        ),
        "missing_keywords": missing_keywords[:12],
        "recommendations": (recommendations.get("english") or [])[:6],
        "hebrew_recommendations": (recommendations.get("hebrew") or [])[:6],
        "career_suggestions": _career_suggestions(primary_resume, job_description),
        "ai_status": "skipped" if provider_warning else "completed",
        "ai_note": provider_warning,
        "analysis_mode": analysis_mode,
        "token_usage": {
            "provider": data.get("token_usage", {}).get("provider", ""),
            "model": data.get("token_usage", {}).get("model", ""),
            "total_tokens": data.get("token_usage", {}).get("total_tokens", 0),
            "usage_available": data.get("token_usage", {}).get("usage_available", False),
        },
        "company_research": data.get("company_research", {}),
    }


def _career_suggestions(resume: dict[str, object], jd: dict[str, object]) -> list[str]:
    skills = " ".join(str(item).lower() for item in resume.get("hard_skills", []))
    leadership = " ".join(str(item).lower() for item in resume.get("leadership_signals", []))
    role_title = str(jd.get("role_title", "")).lower()
    text = " ".join([skills, leadership, role_title])
    suggestions: list[str] = []
    if any(term in text for term in ["manufacturing", "factory", "plant", "production", "process"]):
        suggestions.extend(["Manufacturing Engineering Manager", "Process Engineering Lead", "Plant Engineering Manager"])
    if any(term in text for term in ["automation", "control", "plc", "robot", "industrial"]):
        suggestions.extend(["Automation Project Manager", "Industrial Automation Lead", "Technical Operations Manager"])
    if any(term in text for term in ["project", "commissioning", "vendor", "contractor", "budget"]):
        suggestions.extend(["Project Engineering Manager", "Industrial Projects Lead", "Engineering Program Manager"])
    if any(term in text for term in ["manager", "lead", "team", "ownership", "director"]):
        suggestions.extend(["Engineering Manager", "Head of Engineering Operations", "Director of Engineering"])
    if not suggestions:
        suggestions.extend(["Operations Engineering Lead", "Technical Project Manager", "Process Improvement Manager"])
    deduped: list[str] = []
    for suggestion in suggestions:
        if suggestion not in deduped:
            deduped.append(suggestion)
    return deduped[:6]


async def _read_resume_for_precheck(pdf_resume: UploadFile | None, docx_resume: UploadFile | None) -> tuple[list[PreflightCheck], bool]:
    checks: list[PreflightCheck] = []
    if not pdf_resume and not docx_resume:
        return [
            PreflightCheck(
                key="resume_input",
                label="Resume",
                status="error",
                detail="Upload a PDF or DOCX resume to continue.",
            )
        ], False
    try:
        if pdf_resume:
            validate_upload(pdf_resume)
            pdf_bytes = await enforce_upload_size(pdf_resume)
            parsed = extract_pdf(pdf_bytes, pdf_resume.filename or "resume.pdf")
        else:
            validate_upload(docx_resume)
            docx_bytes = await enforce_upload_size(docx_resume)
            parsed = extract_docx(docx_bytes, docx_resume.filename or "resume.docx")
        enough_text = len(parsed.text.strip()) >= 500
        checks.append(
            PreflightCheck(
                key="resume_readability",
                label="Resume readability",
                status="ok" if enough_text else "error",
                detail=f"Detected language: {parsed.detected_language or 'unknown'}. Extracted {len(parsed.text.strip())} characters.",
            )
        )
        checks.append(
            PreflightCheck(
                key="language_detection",
                label="Language detection",
                status="ok" if parsed.detected_language else "warn",
                detail=f"We detected {parsed.detected_language or 'an unclear language'}. You can correct it before final analysis if needed.",
            )
        )
        return checks, enough_text
    except Exception as exc:
        return [
            PreflightCheck(
                key="resume_readability",
                label="Resume readability",
                status="error",
                detail=f"Resume could not be read: {sanitized_error(str(exc))}",
            )
        ], False


@app.post("/public/precheck")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def public_precheck(
    request: Request,
    pdf_resume: Optional[UploadFile] = File(default=None),
    docx_resume: Optional[UploadFile] = File(default=None),
    jd_text: str = Form(default=""),
    jd_url: str = Form(default=""),
    jd_image: Optional[UploadFile] = File(default=None),
):
    del request
    checks, resume_ready = await _read_resume_for_precheck(pdf_resume, docx_resume)
    url_text, url_warning = _extract_text_from_url(jd_url) if jd_url.strip() else ("", "")
    if jd_image:
        validate_upload(jd_image)
    has_jd = bool(jd_text.strip() or url_text or jd_image)
    checks.append(
        PreflightCheck(
            key="job_description",
            label="Job description",
            status="ok" if has_jd else "error",
            detail=url_warning or ("Job description input is ready." if has_jd else "Paste text, upload an image, or provide a job URL."),
        )
    )
    ready = resume_ready and has_jd and not any(check.status == "error" for check in checks)
    return PreflightReport(
        ready=ready,
        provider="server-side",
        model="hidden",
        checks=checks,
        recommended_action="Continue to full analysis." if ready else "Fix the failed checks before running a full analysis.",
    ).model_dump()


@app.post("/public/analyze")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def public_analyze(
    request: Request,
    pdf_resume: Optional[UploadFile] = File(default=None),
    docx_resume: Optional[UploadFile] = File(default=None),
    jd_text: str = Form(default=""),
    jd_url: str = Form(default=""),
    jd_image: Optional[UploadFile] = File(default=None),
):
    del request
    try:
        if not pdf_resume and not docx_resume:
            raise HTTPException(status_code=400, detail="Upload a PDF or DOCX resume.")
        if pdf_resume:
            validate_upload(pdf_resume)
        if docx_resume:
            validate_upload(docx_resume)
        if jd_image:
            validate_upload(jd_image)
        url_text, url_warning = _extract_text_from_url(jd_url) if jd_url.strip() else ("", "")
        combined_jd = clean_job_description_text("\n\n".join(part for part in [jd_text.strip(), url_text] if part))
        pdf_bytes = await enforce_upload_size(pdf_resume) if pdf_resume else None
        docx_bytes = await enforce_upload_size(docx_resume) if docx_resume else None
        jd_image_bytes = await enforce_upload_size(jd_image) if jd_image else None
        if not combined_jd.strip() and not jd_image_bytes:
            raise HTTPException(status_code=400, detail=url_warning or "Provide a job description as text, image, or URL.")
        result = service.analyze(
            pdf_bytes=pdf_bytes,
            pdf_name=pdf_resume.filename if pdf_resume else "",
            docx_bytes=docx_bytes,
            docx_name=docx_resume.filename if docx_resume else "",
            jd_text=combined_jd,
            jd_image=jd_image_bytes,
            public_mode=True,
            use_provider_insights=get_settings().enable_llm_enhancements,
        )
        payload = _public_result_payload(result)
        if url_warning:
            payload["url_warning"] = url_warning
        return payload
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Public analysis failed: %s", sanitized_error(str(exc)))
        raise HTTPException(status_code=500, detail="Analysis could not be completed. Please try another file or paste the job text directly.")


@app.post("/preflight")
def run_preflight(payload: PreflightRequest) -> dict[str, object]:
    _require_internal_endpoints()
    current = get_settings()
    provider = get_llm_provider()
    model_name = (
        current.openai_model
        if current.llm_provider == "openai"
        else current.gemini_model
        if current.llm_provider == "gemini"
        else current.hf_model
        if current.llm_provider == "huggingface"
        else current.local_llm_model
    )

    checks: list[PreflightCheck] = []
    checks.append(
        PreflightCheck(
            key="provider",
            label="Provider selection",
            status="ok",
            detail=f"Provider '{current.llm_provider}' is selected in API-only mode.",
        )
    )

    key_present = (
        bool(current.openai_api_key)
        if current.llm_provider == "openai"
        else bool(current.gemini_api_key)
        if current.llm_provider == "gemini"
        else bool(current.hf_api_token)
        if current.llm_provider == "huggingface"
        else True
    )
    checks.append(
        PreflightCheck(
            key="api_key",
            label="API key" if current.llm_provider in {"openai", "gemini", "huggingface"} else "Local model",
            status="ok" if key_present else "error",
            detail=(
                f"{current.llm_provider.title()} API key {'is present' if key_present else 'is missing'}."
                if current.llm_provider in {"openai", "gemini", "huggingface"}
                else "No cloud API key is required for local LLM mode."
            ),
        )
    )

    if payload.validate_provider_connection and key_present:
        provider_ok, provider_detail = provider.validate_connection()
        checks.append(
            PreflightCheck(
                key="provider_connection",
                label="Provider connection",
                status="ok" if provider_ok else "error",
                detail=provider_detail,
            )
        )
    else:
        checks.append(
            PreflightCheck(
                key="provider_connection",
                label="Provider connection",
                status="warn",
                detail="Provider validation was skipped because the selected API key is missing.",
            )
        )

    has_resume = bool(payload.pdf_name or payload.docx_name)
    if payload.fixed_resume_slot:
        fixed_ready = (
            bool(current.default_resume_he_path and Path(current.default_resume_he_path).exists())
            if payload.fixed_resume_slot == "he"
            else bool(current.default_resume_en_path and Path(current.default_resume_en_path).exists())
        )
        checks.append(
            PreflightCheck(
                key="fixed_resume",
                label="Fixed resume",
                status="ok" if fixed_ready else "error",
                detail=f"Fixed resume slot '{payload.fixed_resume_slot}' is {'ready' if fixed_ready else 'not configured'}."
            )
        )
        has_resume = has_resume or fixed_ready
    resume_names = [name for name in [payload.pdf_name, payload.docx_name] if name]
    checks.append(
        PreflightCheck(
            key="resume_input",
            label="Resume upload",
            status="ok" if has_resume else "error",
            detail=", ".join(resume_names) if resume_names else "Upload a PDF resume, a DOCX resume, or both.",
        )
    )

    has_jd = bool(payload.jd_text_present or payload.jd_image_name)
    jd_detail = "Job description text is ready." if payload.jd_text_present else ""
    if payload.jd_image_name:
        jd_detail = f"{jd_detail} JD image: {payload.jd_image_name}".strip()
    checks.append(
        PreflightCheck(
            key="job_description",
            label="Job description",
            status="ok" if has_jd else "error",
            detail=jd_detail or "Add job description text or upload an image.",
        )
    )

    ready = all(check.status == "ok" for check in checks if check.key != "provider")
    recommended_action = "Ready to start analysis." if ready else "Resolve the failed checks before starting analysis."
    return PreflightReport(
        ready=ready,
        provider=current.llm_provider,
        model=model_name,
        checks=checks,
        recommended_action=recommended_action,
    ).model_dump()


@app.post("/analyze")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def analyze_resume(
    request: Request,
    pdf_resume: Optional[UploadFile] = File(default=None),
    docx_resume: Optional[UploadFile] = File(default=None),
    jd_text: str = Form(default=""),
    jd_image: Optional[UploadFile] = File(default=None),
    fixed_resume_slot: str = Form(default=""),
):
    _require_internal_endpoints()
    del request
    try:
        if not pdf_resume and not docx_resume and not fixed_resume_slot:
            raise HTTPException(status_code=400, detail="Upload a PDF resume, a DOCX resume, choose a fixed resume, or combine them.")
        if pdf_resume:
            validate_upload(pdf_resume)
        if docx_resume:
            validate_upload(docx_resume)
        if jd_image:
            validate_upload(jd_image)

        pdf_bytes = await enforce_upload_size(pdf_resume) if pdf_resume else None
        docx_bytes = await enforce_upload_size(docx_resume) if docx_resume else None
        pdf_name = pdf_resume.filename if pdf_resume else ""
        docx_name = docx_resume.filename if docx_resume else ""
        if fixed_resume_slot and not pdf_bytes and not docx_bytes:
            fixed_bytes, fixed_name = _load_fixed_resume(fixed_resume_slot)
            if fixed_name.lower().endswith(".pdf"):
                pdf_bytes = fixed_bytes
                pdf_name = fixed_name
            else:
                docx_bytes = fixed_bytes
                docx_name = fixed_name
        jd_image_bytes = await enforce_upload_size(jd_image) if jd_image else None

        if not jd_text.strip() and not jd_image_bytes:
            raise HTTPException(status_code=400, detail="Provide a job description as text or image.")

        result = service.analyze(
            pdf_bytes=pdf_bytes,
            pdf_name=pdf_name,
            docx_bytes=docx_bytes,
            docx_name=docx_name,
            jd_text=jd_text,
            jd_image=jd_image_bytes,
        )
        return result.model_dump()
    except AnalysisPipelineError as exc:
        failure_report = build_failure_report(
            reports_dir=get_settings().reports_dir,
            stage=exc.stage,
            error_summary=str(exc),
            provider=get_settings().llm_provider,
            model=_active_model_name(),
            file_inputs={
                "pdf_resume": pdf_resume.filename if pdf_resume else "",
                "docx_resume": docx_resume.filename if docx_resume else "",
                "fixed_resume_slot": fixed_resume_slot,
                "jd_image": jd_image.filename if jd_image else "",
                "jd_text_present": str(bool(jd_text.strip())),
            },
            runtime_settings=settings_service.get_runtime_settings_summary().model_dump(),
            timeline=exc.timeline,
        )
        logger.exception("Analysis pipeline failed at %s: %s", exc.stage, sanitized_error(str(exc)))
        return ORJSONResponse(
            status_code=500,
            content={
                "detail": f"Analysis failed during '{exc.stage}'.",
                "error_summary": str(exc),
                "crash_report": failure_report.model_dump(),
            },
        )
    except HTTPException:
        raise
    except Exception as exc:
        failure_report = build_failure_report(
            reports_dir=get_settings().reports_dir,
            stage="unknown",
            error_summary=sanitized_error(str(exc)),
            provider=get_settings().llm_provider,
            model=_active_model_name(),
            file_inputs={
                "pdf_resume": pdf_resume.filename if pdf_resume else "",
                "docx_resume": docx_resume.filename if docx_resume else "",
                "fixed_resume_slot": fixed_resume_slot,
                "jd_image": jd_image.filename if jd_image else "",
                "jd_text_present": str(bool(jd_text.strip())),
            },
            runtime_settings=settings_service.get_runtime_settings_summary().model_dump(),
            timeline=[],
        )
        logger.exception("Analysis failed: %s", sanitized_error(str(exc)))
        return ORJSONResponse(
            status_code=500,
            content={
                "detail": "Analysis failed. Review the crash report for the exact stage and sanitized error.",
                "error_summary": sanitized_error(str(exc)),
                "crash_report": failure_report.model_dump(),
            },
        )
