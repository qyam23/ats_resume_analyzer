# Bilingual ATS Resume Analyzer

Local-first candidate-side ATS analyzer for checking ATS hygiene, matching a resume against a target role, running optional company and job-market web research, and producing bilingual Hebrew/English recommendations.

## What it does

- Accepts a PDF resume, a DOCX resume, or both, plus a job description as text or image
- Extracts structured resume and JD entities
- Compares the PDF and DOCX versions for consistency when both are available
- Scores ATS parseability, keyword match, semantic match, leadership alignment, quantified impact, and final ATS fit
- Adds optional market intelligence about the role and company using server-side web research
- Supports runtime provider settings for local mode, Gemini, or OpenAI
- Produces English and Hebrew summaries plus downloadable JSON and Markdown reports
- Runs locally on Windows without Docker

## Architecture

- `api/`: FastAPI backend, public UI host, secured public analysis endpoints, and internal local endpoints
- `public_site/`: production public web UI served by FastAPI from `/`
- `frontend/`: Streamlit command-center UI for local/internal use only
- `core/`: Parsing, extraction, scoring, matching, and report generation
- `providers/`: Swappable OpenAI, Gemini, and local provider interfaces
- `config/`: Settings, logging, redaction, and request guardrails
- `tests/`: Unit tests for scoring, security, and report behavior
- `samples/`: Example JD input and report shape
- `render.yaml`: Render Web Service blueprint
- `.github/workflows/pages.yml`: optional GitHub Pages static mirror workflow

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

## Public production architecture

- Render runs one Python Web Service using FastAPI only
- `public_site` is served from the same Render domain at `/`
- Public API calls are same-origin under `/public/precheck` and `/public/analyze`
- OpenAI and Gemini keys stay server-side in Render environment variables
- Internal endpoints (`/settings`, `/preflight`, `/analyze`) are disabled in production when `ENABLE_INTERNAL_ENDPOINTS=false`
- Streamlit remains available for local diagnostics and private workflows only

## Render deployment

The repository includes `render.yaml` for a Render Blueprint.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
python launch.py
```

The launcher binds to `0.0.0.0` when `APP_ENV=production` and reads the port from Render's `PORT` environment variable, falling back to `8000` locally.

Required or recommended Render environment variables:

- `APP_ENV=production`
- `PYTHON_VERSION=3.10.13`
- `PORT` is provided by Render
- `LLM_PROVIDER=openai` or `gemini`
- `OPENAI_API_KEY` set as a secret if OpenAI enhancements are enabled
- `GEMINI_API_KEY` set as a secret if Gemini enhancements are enabled
- `ENABLE_LLM_ENHANCEMENTS=false` for deterministic public mode, or `true` for provider-enhanced analysis
- `ENABLE_WEB_RESEARCH=true`
- `ENABLE_INTERNAL_ENDPOINTS=false`
- `API_ONLY_MODE=true`
- `ALLOWED_ORIGINS=https://ats-resume-analyzer.onrender.com`

Health check path:

```text
/health
```

## GitHub Pages mirror

GitHub Pages is optional and only publishes a static mirror. It does not run resume analysis. The workflow builds `public_site` into a Pages artifact, sets `STATIC_MIRROR=true`, disables upload/analyze actions, and shows an `Open live analyzer` CTA.

Workflow file:

```text
.github/workflows/pages.yml
```

Set this repository variable if the final Render URL differs from the default:

```text
RENDER_LIVE_URL=https://your-render-service.onrender.com
```

## Providers and local mode

- Core analysis works offline: parsing, PDF vs DOCX comparison, ATS formatting checks, keyword extraction, and scoring
- The app now includes a local settings panel in the UI for provider selection, model choice, and server-side API key storage in `.local_settings.json`
- If `OPENAI_API_KEY` or `GEMINI_API_KEY` is configured and provider analysis is enabled, the backend adds explanation and rewrite suggestions server-side
- For zero cloud-token use, select `local_llm` in the internal Streamlit settings and run a local OpenAI-compatible model server such as Ollama, LM Studio, or another local server exposed at `/v1/chat/completions`
- Default local model settings are `LOCAL_LLM_BASE_URL=http://127.0.0.1:11434/v1` and `LOCAL_LLM_MODEL=gemma3:4b`; adjust these to the exact model name served by your local runtime
- The public web page at `http://localhost:8000` intentionally uses local deterministic analysis only and does not call OpenAI or Gemini
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
