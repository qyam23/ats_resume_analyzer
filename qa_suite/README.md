# ATS Analyzer Internal QA Suite

This module is an internal validation layer for the ATS Analyzer product. It is not part of the public UI and does not change the deterministic ATS engine.

## Fixtures

The research package is extracted into:

```text
qa_suite/fixtures/
  resume_variants.json
  live_job_descriptions.json
  qa_matrix.json
  qa_research_notes.md
```

`qa_matrix.json` is the master test-case list. Each row maps one resume variant to one job description and defines expected fit behavior.

## Run

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m qa_suite.qa_runner
```

Fast smoke run:

```powershell
.\.venv\Scripts\python.exe -m qa_suite.qa_runner --limit 3
```

Single case:

```powershell
.\.venv\Scripts\python.exe -m qa_suite.qa_runner --case-id variant_01_manufacturing_engineering_manager__jd_01
```

## Outputs

Files are written to `qa_suite/output/`:

- `qa_results_full.json`: full machine-readable run with expected inputs, actual outputs, checks, status, notes and failure reasons.
- `qa_report.md`: human-readable product QA report with summaries, repeated issue patterns, failed cases and product risk notes.
- `qa_results_table.csv`: flat spreadsheet-friendly table.

## Evaluation Philosophy

The suite uses practical product QA logic rather than rigid numeric thresholds only.

- `pass`: result is directionally correct and required product outputs are present.
- `warning`: result is plausible but borderline, sparse, or worth manual review.
- `fail`: fit band is clearly wrong, parsing breaks, or critical product outputs are missing.

## Notes

- The runner calls `ATSAnalyzerService` directly for speed and stability.
- AI/provider insights are disabled for QA runs, so results are deterministic-first.
- The generated DOCX input is synthesized from the structured resume-variant fixture.
- Future CI can run the suite in `--limit` mode for smoke checks and full mode before releases.
