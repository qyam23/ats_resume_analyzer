from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import altair as alt
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

BASE_URL = "http://127.0.0.1:8000"
ANALYZE_URL = f"{BASE_URL}/analyze"
SETTINGS_URL = f"{BASE_URL}/settings"
PREFLIGHT_URL = f"{BASE_URL}/preflight"

OPENAI_MODEL_PRESETS = {
    "GPT-4.5 Thinking": "gpt-4.5-preview",
    "GPT-5.1 Thinking": "gpt-5.1",
    "GPT-5.3": "gpt-5.3-chat-latest",
    "GPT-5.4": "gpt-5.4",
    "GPT-5.4 Thinking External": "gpt-5.4",
    "Custom": "__custom__",
}

TEXT = {
    "English": {
        "dir": "ltr",
        "title": "ATS Positioning Studio",
        "subtitle": "ATS fit, provider validation, live pipeline visibility, and failure diagnostics.",
        "resume": "Resume Input",
        "resume_hint": "Upload a PDF, a Word file, or both.",
        "pdf": "PDF Resume",
        "docx": "Word Resume",
        "jd": "Target Role Input",
        "jd_text": "Job description text",
        "jd_image": "Job description image",
        "settings": "Runtime Settings",
        "analyze": "Run Analysis",
        "readiness": "Run Readiness",
        "readiness_hint": "Pre-analysis checks appear here after validation.",
        "failure": "Failure Report",
        "download_failure": "Download Failure Report",
        "summary": "Executive Summary",
        "scores": "Score Breakdown",
        "timeline": "Pipeline Timeline",
        "recommendations": "Recommendations",
        "market": "Market Intel",
        "fit": "Fit & Gaps",
        "source": "Source Data",
    },
    "Hebrew": {
        "dir": "rtl",
        "title": "ATS Positioning Studio",
        "subtitle": "ניתוח ATS עם בדיקת Provider, שקיפות בזמן אמת, ודוח כשל מסודר.",
        "resume": "העלאת קורות חיים",
        "resume_hint": "אפשר להעלות קובץ PDF, קובץ Word, או את שניהם.",
        "pdf": "קורות חיים PDF",
        "docx": "קורות חיים Word",
        "jd": "תיאור המשרה",
        "jd_text": "טקסט תיאור משרה",
        "jd_image": "תמונה של תיאור המשרה",
        "settings": "הגדרות ריצה",
        "analyze": "הפעל ניתוח",
        "readiness": "בדיקת מוכנות",
        "readiness_hint": "בדיקות לפני הניתוח יוצגו כאן לאחר האימות.",
        "failure": "דוח כשל",
        "download_failure": "הורדת דוח כשל",
        "summary": "סיכום מנהלים",
        "scores": "פירוק ציונים",
        "timeline": "ציר שלבי הניתוח",
        "recommendations": "המלצות",
        "market": "מודיעין שוק",
        "fit": "התאמה ופערים",
        "source": "נתוני מקור",
    },
}

st.set_page_config(page_title="ATS Positioning Studio", page_icon="AT", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
    .shell { max-width: 1360px; margin: 0 auto; }
    .hero { padding: 2rem 2.2rem; border-radius: 28px; border: 1px solid #dce8f2; background: linear-gradient(135deg, rgba(255,255,255,.98), rgba(247,250,255,.94)); box-shadow: 0 18px 52px rgba(195,205,221,.22); }
    .hero-title { font-size: 3rem; line-height: 1; margin: 0; color: #35516d; letter-spacing: -0.04em; }
    .hero-copy { color: #6b8198; font-size: 1.02rem; line-height: 1.7; max-width: 68ch; margin-top: .8rem; }
    .tag { display:inline-block; margin: .15rem .4rem .15rem 0; padding: .48rem .8rem; border-radius: 999px; background: #f8fbff; border: 1px solid #dce8f2; color: #5a728d; font-size: .9rem; }
    .section-card { padding: 1.05rem 1.1rem; border-radius: 20px; border: 1px solid #dce8f2; background: rgba(255,255,255,.88); box-shadow: 0 10px 30px rgba(204,213,225,.16); }
    .timeline-item { padding-left: 1rem; margin-left: .35rem; border-left: 2px solid #caddec; margin-bottom: .9rem; }
    .timeline-step { font-weight: 600; color: #44596f; }
    .timeline-detail { color: #7a8da3; font-size: .92rem; margin-top: .15rem; }
    .issue-box { padding: .95rem 1rem; border-radius: 16px; background: #fffdfd; border: 1px solid #e8edf3; margin-bottom: .75rem; }
    .decision-grid { display:grid; grid-template-columns: 1.1fr .9fr .9fr .9fr; gap: .8rem; margin: 1rem 0 .8rem; }
    .decision-tile { border: 1px solid #dce8f2; border-radius: 20px; padding: 1rem; background: rgba(255,255,255,.9); }
    .decision-label { color:#71869a; font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; }
    .decision-value { color:#304a63; font-size:1.55rem; font-weight:750; margin-top:.25rem; }
    .summary-line { font-size:1.05rem; line-height:1.55; color:#35516d; background:#fffdf7; border:1px solid #eadfca; border-radius:18px; padding:1rem 1.1rem; }
    .score-strip { height: 10px; border-radius: 999px; background: linear-gradient(90deg, #dc6b6b 0%, #f0c36b 50%, #5fbf87 100%); overflow:hidden; margin-top:.6rem; }
    .score-marker { height: 10px; width: 4px; background:#24384c; border-radius:999px; position:relative; }
    .quick-grid { display:grid; grid-template-columns: 1.2fr .8fr; gap: 1rem; align-items:start; }
    .copy-box textarea { font-size: .85rem !important; }
    @media (max-width: 900px) { .decision-grid, .quick-grid { grid-template-columns: 1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_runtime_settings() -> dict:
    try:
        response = requests.get(SETTINGS_URL, timeout=20)
        if response.ok:
            return response.json()
    except Exception:
        pass
    return {
        "llm_provider": "local_llm",
        "enable_web_research": True,
        "api_only_mode": True,
        "openai_model": "gpt-5.1",
        "openai_reasoning_effort": "high",
        "gemini_model": "gemini-2.5-flash",
        "hf_model": "Qwen/Qwen2.5-7B-Instruct",
        "hf_key_masked": "",
        "local_llm_base_url": "http://127.0.0.1:11434/v1",
        "local_llm_model": "gemma3:4b",
        "openai_key_masked": "",
        "gemini_key_masked": "",
        "default_resume_he_path": "",
        "default_resume_en_path": "",
        "default_resume_he_ready": False,
        "default_resume_en_ready": False,
    }


def save_runtime_settings(payload: dict) -> tuple[bool, dict | None]:
    try:
        response = requests.post(SETTINGS_URL, json=payload, timeout=30)
        if response.ok:
            return True, response.json()
    except Exception:
        return False, None
    return False, None


def run_preflight(payload: dict) -> tuple[bool, dict]:
    try:
        response = requests.post(PREFLIGHT_URL, json=payload, timeout=45)
        if response.ok:
            return True, response.json()
    except Exception as exc:
        return False, {"ready": False, "checks": [], "recommended_action": str(exc)}
    return False, {"ready": False, "checks": [], "recommended_action": "Preflight request failed."}


def preflight_payload(pdf_resume, docx_resume, jd_text: str, jd_image) -> dict:
    return {
        "pdf_name": pdf_resume.name if pdf_resume else "",
        "docx_name": docx_resume.name if docx_resume else "",
        "jd_text_present": bool(jd_text.strip()),
        "jd_image_name": jd_image.name if jd_image else "",
        "validate_provider_connection": True,
        "fixed_resume_slot": st.session_state.get("fixed_resume_slot", ""),
    }


def infer_verdict(scores: dict[str, float], has_missing_keywords: bool) -> str:
    final_score = float(scores.get("final_ats_score", 0))
    if final_score >= 78 and not has_missing_keywords:
        return "Apply now"
    if final_score >= 62:
        return "Apply after light edits"
    if final_score >= 45:
        return "Apply only after targeted edits"
    return "Low-priority target"


def verdict_tone(final_score: float) -> tuple[str, str]:
    if final_score >= 78:
        return "Positive", "#5fbf87"
    if final_score >= 62:
        return "Promising", "#8acb88"
    if final_score >= 45:
        return "Needs work", "#f0b85a"
    return "Negative", "#dc6b6b"


def build_decision_summary(scores: dict[str, float], verdict: str, missing_keywords: list[str], provider_warning: str) -> str:
    final_score = float(scores.get("final_ats_score", 0))
    parseability = float(scores.get("parseability_score", 0))
    semantic = float(scores.get("semantic_match_score", 0))
    leadership = float(scores.get("leadership_alignment_score", 0))
    weak_parts = []
    if missing_keywords:
        weak_parts.append(f"{len(missing_keywords)} missing keywords")
    if parseability < 70:
        weak_parts.append("ATS readability risk")
    if leadership < 55:
        weak_parts.append("leadership positioning is weak")
    if provider_warning:
        weak_parts.append("AI rewrite layer was skipped")
    issue_text = ", ".join(weak_parts) if weak_parts else "no critical blocker detected"
    return (
        f"{verdict}. Final ATS score is {final_score:.1f}/100. "
        f"Semantic match is {semantic:.1f}/100 and parseability is {parseability:.1f}/100; main attention point: {issue_text}."
    )


def build_export_text(result: dict, language: str, verdict: str, decision_summary: str) -> str:
    scores = result.get("scores", {})
    diagnostics = result.get("detailed_diagnostics", {})
    recommendations = result.get("recommendations", {}).get("hebrew" if language == "Hebrew" else "english", [])
    missing = diagnostics.get("missing_keywords", [])
    lines = [
        "ATS Resume Analyzer - Quick Report",
        "",
        f"Verdict: {verdict}",
        decision_summary,
        "",
        "Scores:",
    ]
    for key, value in scores.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "Missing keywords:"])
    lines.append(", ".join(missing) if missing else "None detected")
    lines.extend(["", "Recommendations:"])
    for item in recommendations[:8]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def render_copy_button(text: str) -> None:
    escaped = json.dumps(text)
    components.html(
        f"""
        <button id="copy-report" style="width:100%;padding:.75rem 1rem;border-radius:14px;border:1px solid #c9d8e6;background:#35516d;color:white;font-weight:700;cursor:pointer;">
          Copy quick report
        </button>
        <script>
        const btn = document.getElementById("copy-report");
        btn.onclick = async () => {{
          await navigator.clipboard.writeText({escaped});
          btn.innerText = "Copied";
          setTimeout(() => btn.innerText = "Copy quick report", 1400);
        }};
        </script>
        """,
        height=52,
    )


def score_chart(scores: dict[str, float]) -> alt.Chart:
    frame = pd.DataFrame([{"metric": key.replace("_", " "), "score": float(value)} for key, value in scores.items()])
    return alt.Chart(frame).mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8).encode(
        x=alt.X("score:Q", scale=alt.Scale(domain=[0, 100]), title=None),
        y=alt.Y("metric:N", sort="-x", title=None),
        color=alt.Color(
            "score:Q",
            scale=alt.Scale(domain=[0, 50, 100], range=["#dc6b6b", "#f0c36b", "#5fbf87"]),
            legend=None,
        ),
        tooltip=["metric", "score"],
    ).properties(height=260)


def compact_source_label(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "") or url


def get_text_blob(path_value: str) -> str:
    if not path_value:
        return ""
    try:
        return Path(path_value).read_text(encoding="utf-8")
    except Exception:
        return ""


if "runtime_settings" not in st.session_state:
    st.session_state.runtime_settings = get_runtime_settings()
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_failure" not in st.session_state:
    st.session_state.last_failure = None
if "last_preflight" not in st.session_state:
    st.session_state.last_preflight = None

language = st.radio("Language / שפה", ["English", "Hebrew"], horizontal=True)
t = TEXT[language]
text_dir = t["dir"]

st.markdown("<div class='shell'>", unsafe_allow_html=True)
st.markdown(
    f"""
    <section class="hero" dir="{text_dir}">
      <span class="tag">API-only</span>
      <span class="tag">Provider: {st.session_state.runtime_settings['llm_provider']}</span>
      <span class="tag">Reasoning: {st.session_state.runtime_settings.get('openai_reasoning_effort', 'high')}</span>
      <span class="tag">Web research: {'ON' if st.session_state.runtime_settings['enable_web_research'] else 'OFF'}</span>
      <h1 class="hero-title">{t['title']}</h1>
      <div class="hero-copy">{t['subtitle']}</div>
    </section>
    """,
    unsafe_allow_html=True,
)

left, middle, right = st.columns([1.2, 1.45, 1.05])
with left:
    with st.container(border=True):
        st.markdown(f"### {t['resume']}")
        st.caption(t["resume_hint"])
        resume_source = st.radio("Resume source", ["Fixed resume", "Upload now"], horizontal=True)
        fixed_resume_slot = ""
        if resume_source == "Fixed resume":
            fixed_resume_slot = st.radio(
                "Fixed profile",
                ["he", "en"],
                format_func=lambda value: "Hebrew resume" if value == "he" else "English resume",
                horizontal=True,
            )
            st.session_state.fixed_resume_slot = fixed_resume_slot
            he_status = "ready" if st.session_state.runtime_settings.get("default_resume_he_ready") else "missing"
            en_status = "ready" if st.session_state.runtime_settings.get("default_resume_en_ready") else "missing"
            st.caption(f"HE: {he_status} | EN: {en_status}")
            pdf_resume = None
            docx_resume = None
        else:
            st.session_state.fixed_resume_slot = ""
            pdf_resume = st.file_uploader(t["pdf"], type=["pdf"])
            docx_resume = st.file_uploader(t["docx"], type=["docx"])
with middle:
    with st.container(border=True):
        st.markdown(f"### {t['jd']}")
        jd_text = st.text_area(t["jd_text"], height=230)
        jd_image = st.file_uploader(t["jd_image"], type=["png", "jpg", "jpeg"])
with right:
    with st.expander(t["settings"], expanded=False):
        with st.form("runtime-settings-form"):
            provider_options = ["local_llm", "openai", "gemini", "huggingface"]
            provider = st.selectbox(
                "Provider",
                options=provider_options,
                index=provider_options.index(st.session_state.runtime_settings["llm_provider"])
                if st.session_state.runtime_settings["llm_provider"] in provider_options
                else 0,
            )
            enable_web_research = st.toggle("Enable market web research", value=st.session_state.runtime_settings["enable_web_research"])
            current_model = st.session_state.runtime_settings["openai_model"]
            preset_labels = list(OPENAI_MODEL_PRESETS.keys())
            selected_preset = next((label for label, model_id in OPENAI_MODEL_PRESETS.items() if model_id == current_model and label != "Custom"), "Custom")
            openai_model_preset = st.selectbox("OpenAI model preset", options=preset_labels, index=preset_labels.index(selected_preset))
            openai_model = OPENAI_MODEL_PRESETS[openai_model_preset]
            if openai_model == "__custom__":
                openai_model = st.text_input("Custom OpenAI model id", value=current_model)
            default_reasoning = "high" if "Thinking" in openai_model_preset or openai_model in {"gpt-5.1", "gpt-5.4"} else st.session_state.runtime_settings.get("openai_reasoning_effort", "high")
            openai_reasoning = st.selectbox("OpenAI reasoning effort", options=["low", "medium", "high"], index=["low", "medium", "high"].index(default_reasoning if default_reasoning in {"low", "medium", "high"} else "high"))
            hf_model = st.text_input("Hugging Face model", value=st.session_state.runtime_settings.get("hf_model", "Qwen/Qwen2.5-7B-Instruct"))
            gemini_model = st.text_input("Gemini model", value=st.session_state.runtime_settings["gemini_model"])
            local_llm_base_url = st.text_input("Local LLM base URL", value=st.session_state.runtime_settings.get("local_llm_base_url", "http://127.0.0.1:11434/v1"))
            local_llm_model = st.text_input("Local LLM model", value=st.session_state.runtime_settings.get("local_llm_model", "gemma3:4b"))
            hf_key = st.text_input(f"Hugging Face token ({st.session_state.runtime_settings.get('hf_key_masked') or 'not set'})", value="", type="password")
            openai_key = st.text_input(f"OpenAI API key ({st.session_state.runtime_settings['openai_key_masked'] or 'not set'})", value="", type="password")
            gemini_key = st.text_input(f"Gemini API key ({st.session_state.runtime_settings['gemini_key_masked'] or 'not set'})", value="", type="password")
            if st.form_submit_button("Save Settings", use_container_width=True):
                ok, updated = save_runtime_settings(
                    {
                        "llm_provider": provider,
                        "enable_llm_enhancements": True,
                        "enable_web_research": enable_web_research,
                        "api_only_mode": True,
                        "hf_api_token": hf_key,
                        "hf_model": hf_model,
                        "openai_api_key": openai_key,
                        "openai_model": openai_model,
                        "openai_reasoning_effort": openai_reasoning,
                        "gemini_api_key": gemini_key,
                        "gemini_model": gemini_model,
                        "local_llm_base_url": local_llm_base_url,
                        "local_llm_model": local_llm_model,
                        "local_llm_timeout_seconds": 120,
                    }
                )
                if ok and updated:
                    st.session_state.runtime_settings = updated
                    st.success("Settings saved locally.")
                else:
                    st.error("Settings could not be saved.")

with st.container(border=True):
    st.markdown(f"### {t['readiness']}")
    st.caption(t["readiness_hint"])
    cols = st.columns(3)
    if st.session_state.get("fixed_resume_slot") == "he":
        files_selected = f"Fixed HE: {Path(st.session_state.runtime_settings.get('default_resume_he_path', '')).name or '-'}"
    elif st.session_state.get("fixed_resume_slot") == "en":
        files_selected = f"Fixed EN: {Path(st.session_state.runtime_settings.get('default_resume_en_path', '')).name or '-'}"
    else:
        files_selected = ", ".join([value for value in [pdf_resume.name if pdf_resume else "", docx_resume.name if docx_resume else ""] if value]) or "-"
    cols[0].metric("Files", files_selected)
    cols[1].metric("JD", "Ready" if jd_text.strip() or jd_image else "Missing")
    if st.session_state.runtime_settings["llm_provider"] == "local_llm":
        key_masked = f"local: {st.session_state.runtime_settings.get('local_llm_model', '-')}"
    elif st.session_state.runtime_settings["llm_provider"] == "huggingface":
        key_masked = st.session_state.runtime_settings.get("hf_key_masked") or "Missing"
    else:
        key_masked = st.session_state.runtime_settings["openai_key_masked"] if st.session_state.runtime_settings["llm_provider"] == "openai" else st.session_state.runtime_settings["gemini_key_masked"]
    cols[2].metric("Key", key_masked or "Missing")
    if st.session_state.last_preflight:
        for check in st.session_state.last_preflight.get("checks", []):
            st.write(f"- {check['label']}: {check['status'].upper()} - {check['detail']}")
        if st.session_state.last_preflight.get("recommended_action"):
            st.caption(st.session_state.last_preflight["recommended_action"])

result = None
if st.button(t["analyze"], type="primary", use_container_width=True):
    st.session_state.last_result = None
    st.session_state.last_failure = None
    using_fixed_resume = bool(st.session_state.get("fixed_resume_slot"))
    if ((not pdf_resume and not docx_resume and not using_fixed_resume) or (not jd_text.strip() and not jd_image)):
        st.error("Upload at least one resume file and provide a job description as text or image.")
    else:
        files = {}
        if pdf_resume:
            files["pdf_resume"] = (pdf_resume.name, pdf_resume.getvalue(), "application/pdf")
        if docx_resume:
            files["docx_resume"] = (docx_resume.name, docx_resume.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        if jd_image:
            files["jd_image"] = (jd_image.name, jd_image.getvalue(), jd_image.type or "image/png")

        with st.status("Running analysis", expanded=True) as status:
            status.write("1. Validating provider connection and inputs.")
            ok, preflight = run_preflight(preflight_payload(pdf_resume, docx_resume, jd_text, jd_image))
            st.session_state.last_preflight = preflight
            if not ok:
                status.update(label="The backend could not be reached.", state="error")
            else:
                for check in preflight.get("checks", []):
                    status.write(f"- {check['label']}: {check['status'].upper()} - {check['detail']}")
                if not preflight.get("ready"):
                    status.update(label="Preflight did not pass. Fix the failed checks and try again.", state="error")
                else:
                    status.write("2. Uploading files to the local API.")
                    try:
                        response = requests.post(
                            ANALYZE_URL,
                            files=files,
                            data={"jd_text": jd_text, "fixed_resume_slot": st.session_state.get("fixed_resume_slot", "")},
                            timeout=300,
                        )
                    except Exception:
                        status.update(label="The backend could not be reached.", state="error")
                    else:
                        status.write("3. Waiting for the analysis response.")
                        if response.ok:
                            result = response.json()
                            st.session_state.last_result = result
                            status.update(label="Analysis completed and report assets were generated.", state="complete")
                        else:
                            try:
                                st.session_state.last_failure = response.json()
                            except Exception:
                                st.session_state.last_failure = {"detail": "Analysis failed."}
                            status.update(label="Analysis failed. Crash diagnostics were returned.", state="error")

if st.session_state.last_result:
    result = st.session_state.last_result

if st.session_state.last_failure:
    failure = st.session_state.last_failure
    crash_report = failure.get("crash_report", {})
    with st.container(border=True):
        st.markdown(f"### {t['failure']}")
        st.error(failure.get("detail", "Analysis failed."))
        st.write(f"Stage: {crash_report.get('stage', 'unknown')}")
        st.write(f"Error: {crash_report.get('error_summary', failure.get('error_summary', '-'))}")
        st.write(f"Report ID: {crash_report.get('report_id', '-')}")
        st.write(f"Saved report: {crash_report.get('report_path', '-')}")
        if crash_report.get("timeline"):
            with st.expander(t["timeline"], expanded=False):
                for item in crash_report["timeline"]:
                    st.markdown(f"<div class='timeline-item'><div class='timeline-step'>{item['step']} · {item['status']} · {item['elapsed_ms']}ms</div><div class='timeline-detail'>{item['detail']}</div></div>", unsafe_allow_html=True)
        st.download_button(
            t["download_failure"],
            data=json.dumps(crash_report, ensure_ascii=False, indent=2),
            file_name="ats_failure_report.json",
            mime="application/json",
            use_container_width=True,
            disabled=not crash_report,
            key="download_failure_report_json",
        )

if result:
    scores = result["scores"]
    diagnostics = result["detailed_diagnostics"]
    job_description = diagnostics.get("job_description", {})
    primary_resume = diagnostics.get("docx_structured") or diagnostics.get("pdf_structured") or {}
    missing_keywords = diagnostics.get("missing_keywords", [])
    usage = result.get("token_usage", {})
    session_usage = result.get("session_usage", {})
    verdict = infer_verdict(scores, bool(missing_keywords))
    final_score = float(scores.get("final_ats_score", 0))
    tone_label, tone_color = verdict_tone(final_score)
    provider_warning = diagnostics.get("provider_warning", "")
    decision_summary = build_decision_summary(scores, verdict, missing_keywords, provider_warning)
    export_text = build_export_text(result, language, verdict, decision_summary)

    st.markdown(
        f"""
        <div class="decision-grid" dir="{text_dir}">
          <div class="decision-tile">
            <div class="decision-label">Final ATS score</div>
            <div class="decision-value" style="color:{tone_color};">{final_score:.1f}/100</div>
            <div class="score-strip"><div class="score-marker" style="left:{max(0, min(final_score, 100))}%;"></div></div>
          </div>
          <div class="decision-tile">
            <div class="decision-label">Verdict</div>
            <div class="decision-value">{verdict}</div>
          </div>
          <div class="decision-tile">
            <div class="decision-label">Review tone</div>
            <div class="decision-value" style="color:{tone_color};">{tone_label}</div>
          </div>
          <div class="decision-tile">
            <div class="decision-label">Session cost</div>
            <div class="decision-value">${session_usage.get('estimated_total_cost_usd', 0):.6f}</div>
          </div>
        </div>
        <div class="summary-line" dir="{text_dir}">{decision_summary}</div>
        """,
        unsafe_allow_html=True,
    )

    quick_left, quick_right = st.columns([1.2, 0.8])
    with quick_left:
        st.markdown(f"### {t['scores']}")
        score_cols = st.columns(4)
        score_cols[0].metric("Parseability", f"{scores.get('parseability_score', 0):.1f}")
        score_cols[1].metric("Keywords", f"{scores.get('keyword_match_score', 0):.1f}")
        score_cols[2].metric("Semantic", f"{scores.get('semantic_match_score', 0):.1f}")
        score_cols[3].metric("Leadership", f"{scores.get('leadership_alignment_score', 0):.1f}")
        token_cols = st.columns(4)
        token_cols[0].metric("Run tokens", usage.get("total_tokens", 0), help=f"{usage.get('provider', '')} · {usage.get('model', '')}")
        token_cols[1].metric("Input", usage.get("input_tokens", 0))
        token_cols[2].metric("Output", usage.get("output_tokens", 0))
        token_cols[3].metric("Session tokens", session_usage.get("total_tokens", 0), help=f"Analyses: {session_usage.get('analyses_count', 0)}")
    with quick_right:
        st.markdown("### Export")
        render_copy_button(export_text)
        st.download_button("Download quick TXT", data=export_text, file_name="ats_quick_report.txt", mime="text/plain", use_container_width=True, key="download_quick_report_txt")
        st.download_button("Download JSON", data=json.dumps(result, ensure_ascii=False, indent=2), file_name="ats_analysis_report.json", mime="application/json", use_container_width=True, key="download_top_analysis_json")
        st.text_area("Copy manually if browser clipboard is blocked", value=export_text, height=138, key="quick_report_copy_text")
        if provider_warning:
            st.warning(f"AI provider warning: {provider_warning}")

    tab_overview, tab_fit, tab_market, tab_source = st.tabs(["Overview", t["fit"], t["market"], t["source"]])
    with tab_overview:
        left_col, right_col = st.columns([1.05, 0.95])
        with left_col:
            st.altair_chart(score_chart(scores), use_container_width=True)
            st.markdown(f"### {t['timeline']}")
            for item in result.get("timeline", []):
                st.markdown(f"<div class='timeline-item'><div class='timeline-step'>{item['step']} · {item['status']} · {item['elapsed_ms']}ms</div><div class='timeline-detail'>{item['detail']}</div></div>", unsafe_allow_html=True)
        with right_col:
            st.markdown(f"### {t['recommendations']}")
            for item in result["recommendations"]["hebrew" if language == "Hebrew" else "english"]:
                st.markdown(f"<div class='issue-box' dir='{text_dir}'>{item}</div>", unsafe_allow_html=True)

    with tab_fit:
        fit_left, fit_right = st.columns(2)
        with fit_left:
            st.write({"role_title": job_description.get("role_title", ""), "company_name": job_description.get("company_name", ""), "seniority": job_description.get("seniority", ""), "must_have_skills": job_description.get("must_have_skills", [])})
            st.write({"missing_keywords": missing_keywords})
            if result.get("consistency_mismatches"):
                st.dataframe(pd.DataFrame(result["consistency_mismatches"]), use_container_width=True, hide_index=True)
        with fit_right:
            st.write({"contact": primary_resume.get("contact", {}), "hard_skills": primary_resume.get("hard_skills", []), "leadership_signals": primary_resume.get("leadership_signals", [])[:5]})

    with tab_market:
        research = result.get("company_research") or {}
        if not research or (not research.get("notes_en") and not research.get("notes_he") and not research.get("sources")):
            st.info("No meaningful public market signal was collected.")
        else:
            st.write({"company": research.get("company_name") or "Unknown", "stability": research.get("stability_signal") or "unknown", "role_age_days": research.get("role_market_age_days"), "indexed_evidence": research.get("posting_evidence_count", 0)})
            for note in research.get("notes_he" if language == "Hebrew" else "notes_en", []):
                st.markdown(f"<div class='issue-box' dir='{text_dir}'>{note}</div>", unsafe_allow_html=True)
            for url in research.get("sources", [])[:6]:
                st.markdown(f"- [{compact_source_label(url)}]({url})")

    with tab_source:
        raw_left, raw_right = st.columns(2)
        with raw_left:
            st.json(diagnostics)
        with raw_right:
            st.download_button("Download JSON", data=json.dumps(result, ensure_ascii=False, indent=2), file_name="ats_analysis_report.json", mime="application/json", use_container_width=True, key="download_source_analysis_json")
            st.download_button("Download Markdown", data=get_text_blob(result.get("markdown_report_path", "")), file_name="ats_analysis_report.md", mime="text/markdown", use_container_width=True, disabled=not result.get("markdown_report_path"), key="download_source_analysis_markdown")

st.markdown("</div>", unsafe_allow_html=True)
