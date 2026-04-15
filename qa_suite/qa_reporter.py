from __future__ import annotations

import csv
import json
from pathlib import Path

from qa_suite.qa_schemas import QARunSummary


def write_reports(summary: QARunSummary, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    full_json = output_dir / "qa_results_full.json"
    report_md = output_dir / "qa_report.md"
    table_csv = output_dir / "qa_results_table.csv"

    full_json.write_text(summary.model_dump_json(indent=2), encoding="utf-8")
    report_md.write_text(_markdown_report(summary), encoding="utf-8")
    _write_csv(summary, table_csv)
    return {
        "json": str(full_json),
        "markdown": str(report_md),
        "csv": str(table_csv),
    }


def _write_csv(summary: QARunSummary, path: Path) -> None:
    columns = [
        "run_id",
        "case_id",
        "resume_variant_id",
        "job_id",
        "expected_fit_band",
        "decision",
        "final_ats_score",
        "visibility_score",
        "recruiter_match_score",
        "ats_parse_score",
        "status",
        "notes",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for case in summary.cases:
            writer.writerow(
                {
                    "run_id": summary.run_id,
                    "case_id": case.case_id,
                    "resume_variant_id": case.resume_variant_id,
                    "job_id": case.job_id,
                    "expected_fit_band": case.expected_fit_band,
                    "decision": case.actual.decision,
                    "final_ats_score": f"{case.actual.final_ats_score:.2f}",
                    "visibility_score": f"{case.actual.visibility_score:.2f}",
                    "recruiter_match_score": f"{case.actual.recruiter_match_score:.2f}",
                    "ats_parse_score": f"{case.actual.ats_parse_score:.2f}",
                    "status": case.status,
                    "notes": " | ".join(case.failure_reasons + case.notes),
                }
            )


def _markdown_report(summary: QARunSummary) -> str:
    failed = [case for case in summary.cases if case.status == "fail"]
    warnings = [case for case in summary.cases if case.status == "warning"]
    repeated = _issue_patterns(summary)
    lines = [
        f"# ATS Product QA Report",
        "",
        f"- Run ID: `{summary.run_id}`",
        f"- Created: {summary.created_at}",
        f"- Total cases: {summary.total_cases}",
        f"- Passed: {summary.passed}",
        f"- Warnings: {summary.warnings}",
        f"- Failed: {summary.failed}",
        "",
        "## Fit-Band Summary",
        "",
        *_summary_table(summary.by_fit_band),
        "",
        "## Language Summary",
        "",
        *_summary_table(summary.by_language),
        "",
        "## Repeated Issue Patterns",
        "",
    ]
    if repeated:
        lines.extend(f"- {issue}: {count}" for issue, count in repeated[:10])
    else:
        lines.append("- No repeated issue pattern detected.")
    lines.extend(["", "## Top Failed Cases", ""])
    if failed:
        for case in failed[:10]:
            lines.append(f"- `{case.case_id}` expected `{case.expected_fit_band}` but got `{case.actual.decision}` / {case.actual.final_ats_score:.1f}. Reasons: {'; '.join(case.failure_reasons)}")
    else:
        lines.append("- No failed cases.")
    lines.extend(["", "## Warning Cases", ""])
    if warnings:
        for case in warnings[:15]:
            lines.append(f"- `{case.case_id}`: {'; '.join(case.failure_reasons + case.notes)}")
    else:
        lines.append("- No warnings.")
    lines.extend(
        [
            "",
            "## Product Risk Notes",
            "",
            "- Treat warnings as manual-review candidates, not automatic product failures.",
            "- If strong cases repeatedly score weak, inspect keyword extraction, title alignment, and semantic matching.",
            "- If weak cases repeatedly score strong, inspect overly broad synonym coverage or generated resume fixture text.",
            "- If product-output checks fail, inspect the transformation/premium/job-search output layer rather than ATS scoring first.",
            "",
            "## Suggested Improvements",
            "",
            "- Product: review failed strong/weak fit reversals first.",
            "- QA logic: tune thresholds only after reading the case text and actual outputs.",
            "- Both: keep a baseline JSON from a known-good release and compare future runs against it.",
        ]
    )
    return "\n".join(lines) + "\n"


def _summary_table(groups: dict[str, dict[str, int]]) -> list[str]:
    if not groups:
        return ["No grouped data."]
    lines = ["| Group | Pass | Warning | Fail | Total |", "|---|---:|---:|---:|---:|"]
    for group, counts in sorted(groups.items()):
        passed = counts.get("pass", 0)
        warning = counts.get("warning", 0)
        fail = counts.get("fail", 0)
        total = passed + warning + fail
        lines.append(f"| {group} | {passed} | {warning} | {fail} | {total} |")
    return lines


def _issue_patterns(summary: QARunSummary) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for case in summary.cases:
        for issue in case.failure_reasons + case.notes:
            counts[issue] = counts.get(issue, 0) + 1
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)
