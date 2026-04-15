---
title: ATS Resume Analyzer
emoji: 🧭
colorFrom: teal
colorTo: green
sdk: docker
app_port: 7860
---

# SignalCV ATS Visibility + Job Fit Decision Engine

Private, candidate-side ATS visibility and job-fit decision engine for checking whether a resume can be parsed, found by recruiter search, aligned to a target role, and improved truthfully without inventing experience.

## What it does

- Accepts a PDF resume, a DOCX resume, or both, plus a job description as text or image
- Extracts structured resume and JD entities
- Compares the PDF and DOCX versions for consistency when both are available
- Scores ATS parseability, keyword match, semantic match, leadership alignment, quantified impact, and final ATS fit
- Adds optional market intelligence about the role and company using server-side web research
- Supports private server-side API enhancement through OpenAI or Gemini in this phase
- Keeps Hugging Face provider support architecture-ready for a later free/managed phase, but it is not the active default now
- Produces English and Hebrew summaries plus downloadable JSON and Markdown reports
- Runs locally on Windows without Docker

## Architecture

- `api/`: FastAPI backend, public UI host, password-protected public analysis endpoints, and internal local endpoints
- `public_site/`: production public web UI served by FastAPI from `/`
- `frontend/`: Streamlit command-center UI for local/internal use only
- `core/`: Parsing, extraction, scoring, matching, and report generation
- `providers/`: Swappable OpenAI, Gemini, Hugging Face, and local provider interfaces
- `config/`: Settings, logging, redaction, and request guardrails
- `tests/`: Unit tests for scoring, security, and report behavior
- `samples/`: Example JD input and report shape
- `Dockerfile`: Hugging Face Docker Space runtime
- `.github/workflows/pages.yml`: optional GitHub Pages static mirror workflow
- `.github/workflows/ci.yml`: tests and Docker build validation

Reference inspirations used for architecture ideas only:

- [OmkarPathak/pyresparser](https://github.com/OmkarPathak/pyresparser)
- [raghavendranhp/AI_driven_Applicant_Tracking_System](https://github.com/raghavendranhp/AI_driven_Applicant_Tracking_System)

## Setup

### PowerShell

```powershell
cd C:\Users\user\Documents\Playground\ats_resume_analyzer
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### CMD

```bat
cd C:\Users\user\Documents\Playground\ats_resume_analyzer
py -3.10 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
```

## Run

### Local visual product mode

For the current UX and visualization phase, use the local-only launcher:

```powershell
cd C:\Users\user\Documents\Playground\ats_resume_analyzer
.\run_visual_local.bat
```

The script starts FastAPI locally, opens the browser, enables the password gate, and defaults the AI enhancement layer to the local OpenAI-compatible provider:

- URL: `http://127.0.0.1:8000`
- Local password: `local`
- Provider: `local_llm`
- Default local endpoint: `http://127.0.0.1:11434/v1`
- Default model name: `gemma3:4b`

If Ollama is installed and available in `PATH`, the launcher attempts to start `ollama serve` when the local server is not already responding. If Ollama or the model is unavailable, the deterministic ATS analysis still runs and the UI shows that local AI rewrite suggestions were skipped.

### Public app only

```powershell
cd C:\Users\user\Documents\Playground\ats_resume_analyzer
.\.venv\Scripts\Activate.ps1
python launch.py
```

Open `http://localhost:8000`. FastAPI serves `public_site/index.html` from `/`, and the browser calls the same-origin `/public/precheck` and `/public/analyze` endpoints.

### Internal Streamlit

```powershell
cd C:\Users\user\Documents\Playground\ats_resume_analyzer
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py --server.port 8501
```

### Helper scripts

```powershell
.\setup_local.bat
.\run_local.bat
```

`run_local.bat` starts FastAPI on `127.0.0.1:8000` and Streamlit on `127.0.0.1:8501`. Streamlit is not the production UI.

## Private production architecture

- A FastAPI container serves one protected public product surface
- `public_site` is served from the same app domain at `/`
- Public API calls are same-origin under `/public/precheck` and `/public/analyze`
- The site can be protected by `SITE_AUTH_ENABLED=true` and `SITE_PASSWORD`
- Private provider keys stay server-side only
- OpenAI or Gemini are the active private API providers for this phase
- Hugging Face remains available in the provider abstraction for a later phase
- Internal endpoints (`/settings`, `/preflight`, `/analyze`) are disabled in production when `ENABLE_INTERNAL_ENDPOINTS=false`
- Streamlit remains available for local diagnostics and private workflows only

## Password protection

Enable the private access gate with:

```env
SITE_AUTH_ENABLED=true
SITE_PASSWORD=<your private site password>
SITE_AUTH_SECRET=<long random cookie signing secret>
```

The password is checked only on the server. A signed HTTP-only cookie is issued after login. The browser never receives the password, provider keys, or raw provider settings. When `SITE_AUTH_ENABLED=true`, `/public/precheck` and `/public/analyze` require an authenticated session.

## Hugging Face Docker readiness

The repo is still ready to run as a Hugging Face Docker Space later. Do not choose Gradio; this project already serves a custom FastAPI app and static `public_site`.

Docker runtime:

```bash
python launch.py
```

The Dockerfile exposes port `7860`. The launcher binds to `0.0.0.0` when `APP_ENV=production` and reads the port from `PORT`, falling back to `7860` in Docker and `8000` locally.

For the current private API phase, recommended production variables are:

- `APP_ENV=production`
- `PORT=7860`
- `LLM_PROVIDER=openai`
- `OPENAI_API_KEY=<your OpenAI key>`
- `OPENAI_MODEL=gpt-5.1`
- `OPENAI_REASONING_EFFORT=high`
- `ENABLE_LLM_ENHANCEMENTS=true`
- `ENABLE_WEB_RESEARCH=true`
- `ENABLE_INTERNAL_ENDPOINTS=false`
- `API_ONLY_MODE=true`
- `SITE_AUTH_ENABLED=true`
- `SITE_PASSWORD=<your private site password>`
- `SITE_AUTH_SECRET=<long random cookie signing secret>`
- `ALLOWED_ORIGINS=https://qyam23-ats-resume-analyzer.hf.space`

For Gemini instead of OpenAI:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=<your Gemini key>
GEMINI_MODEL=gemini-2.5-flash
```

Health check:

```text
/health
```

## AI modes

- Deterministic mode runs parsing, ATS checks, consistency, matching, scoring, and recommendations without an LLM
- Local visual mode defaults to `local_llm` for commentary, rewrite guidance, and explanation
- AI-enhanced mode keeps deterministic scoring as the source of truth and uses the selected provider only for commentary, rewrite guidance, and explanation
- If the provider fails, times out, or returns an incomplete response, the deterministic ATS result still completes
- Hugging Face can be enabled later with `LLM_PROVIDER=huggingface`, `HF_API_TOKEN`, and `HF_MODEL`
- GitHub Models are not used as the production inference backend
- Streamlit remains local/internal only and is not the production UI

## ATS visibility model

The analyzer models ATS realistically as:

- ingestion and parsing
- searchable indexing
- recruiter query visibility
- keyword and title discoverability
- practical fit scoring

The public result now includes product-level concepts such as `decision`, `visibility_score`, `recruiter_match_score`, `ats_parse_score`, `missing_signals`, `top_fixes`, `compatibility_scores`, `what_ats_sees`, `what_recruiter_sees`, and `career_suggestions`.

Approximate compatibility scores are heuristic only and cover Workday-like, Greenhouse-like, legacy parser-like, and Israeli ATS-like behavior. They do not reverse-engineer vendor systems.

## GitHub Pages mirror

GitHub Pages is optional and only publishes a static mirror. It does not run resume analysis. The workflow builds `public_site` into a Pages artifact, sets `STATIC_MIRROR=true`, disables upload/analyze actions, and shows an `Open live analyzer` CTA.

Workflow file:

```text
.github/workflows/pages.yml
```

Set this repository variable if the final Hugging Face Space URL differs from the default:

```text
HF_SPACE_URL=https://your-space-name.hf.space
```

## Providers and local mode

- Core analysis works offline: parsing, PDF vs DOCX comparison, ATS formatting checks, keyword extraction, and scoring
- The app now includes a local settings panel in the UI for provider selection, model choice, and server-side API key storage in `.local_settings.json`
- If a private provider key is configured and provider analysis is enabled, the backend adds explanation and rewrite suggestions server-side
- For zero cloud-token use, select `local_llm` in the internal Streamlit settings and run a local OpenAI-compatible model server such as Ollama, LM Studio, or another local server exposed at `/v1/chat/completions`
- Default local model settings are `LOCAL_LLM_BASE_URL=http://127.0.0.1:11434/v1` and `LOCAL_LLM_MODEL=gemma3:4b`; adjust these to the exact model name served by your local runtime
- The public web page at `http://localhost:8000` uses deterministic analysis first and optionally adds private API commentary when configured
- Local semantic scoring uses Sentence Transformers by default
- Optional reranker support can be enabled via `RERANKER_MODEL`
- OpenAI defaults to `gpt-5.1` with configurable reasoning effort; if your account later exposes a newer official model id, you can enter it directly in settings

## Calibration test cases

Two local job-description files are included for regression checks against the fixed reference resume:

- `samples/test_cases/positive_cv_fit_jd.txt`: a strong-fit engineering/manufacturing/automation leadership role
- `samples/test_cases/negative_cv_fit_jd.txt`: an intentionally unrelated clinical/regulatory biostatistics role

The public no-API endpoint should clearly separate them: the positive case should score high and the negative case should score low. This helps verify that the analyzer is not simply rewarding every readable resume.

## Web research

- The backend can query the public web to estimate how long a role has been visible, whether it appears reposted or syndicated, and whether the company shows positive, mixed, or watchlist signals
- This layer is heuristic and internet-dependent; it should be treated as directional candidate intelligence, not as formal due diligence
- Web research can be disabled from the settings panel

## Secret handling and rotation

- Keep keys only in environment variables, a local `.env`, or the local server-side `.local_settings.json`
- Never expose provider keys to the Streamlit frontend
- Logs use redaction and should never print full secret values
- Rotate a key by replacing its environment variable and restarting the backend
- If a key is compromised: revoke in the provider console, update `.env`, restart the app, and remove any leaked artifacts from local reports/logs

## Security guardrails

- Upload size limits are enforced server-side
- File types are validated before parsing
- FastAPI endpoints are rate limited
- Outbound provider calls use short timeouts and bounded retries
- Reports and error responses are sanitized to avoid leaking secrets

## Sample inputs and outputs

- `samples/sample_job_description.txt`
- `samples/sample_report.md`
- `samples/sample_report.json`

## Notes

- OCR fallback uses `rapidocr-onnxruntime` when the PDF or JD image lacks selectable text
- On first semantic analysis run, local embedding models may download from Hugging Face
- V1 is candidate-side only and intentionally avoids recruiter workflow features
- The local development target is Python 3.10 using `py -3.10`
- The OpenAI API model catalog changes over time; use an exact model id that is available on your account
