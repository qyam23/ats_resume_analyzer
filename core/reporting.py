from __future__ import annotations

import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from uuid import uuid4

from core.schemas import AnalysisResult, FailureReport


def write_reports(result: AnalysisResult, reports_dir: Path) -> tuple[str, str]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = reports_dir / f"ats_report_{timestamp}.json"
    md_path = reports_dir / f"ats_report_{timestamp}.md"
    json_path.write_text(json.dumps(result.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_to_markdown(result), encoding="utf-8")
    return str(json_path), str(md_path)


def write_failure_report(report: FailureReport, reports_dir: Path) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    failure_path = reports_dir / f"ats_failure_{timestamp}_{report.report_id}.json"
    payload = report.model_copy(update={"report_path": str(failure_path)})
    failure_path.write_text(json.dumps(payload.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return str(failure_path)


def build_failure_report(
    reports_dir: Path,
    stage: str,
    error_summary: str,
    provider: str,
    model: str,
    file_inputs: dict[str, str],
    runtime_settings: dict[str, object],
    timeline: list,
) -> FailureReport:
    report = FailureReport(
        report_id=uuid4().hex[:10],
        created_at=datetime.now(timezone.utc).isoformat(),
        stage=stage,
        error_summary=error_summary,
        provider=provider,
        model=model,
        file_inputs=file_inputs,
        runtime_settings=runtime_settings,
        timeline=timeline,
        report_path="",
    )
    report.report_path = write_failure_report(report, reports_dir)
    return report


def _to_markdown(result: AnalysisResult) -> str:
    lines = [
        "# ATS Resume Analysis Report",
        "",
        "## Executive Summary",
        f"- EN: {result.executive_summary['en']}",
        f"- HE: {result.executive_summary['he']}",
        "",
        "## Scores",
    ]
    for key, value in result.scores.model_dump().items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Recommendations"])
    for item in result.recommendations.english:
        lines.append(f"- EN: {item}")
    for item in result.recommendations.hebrew:
        lines.append(f"- HE: {item}")
    return "\n".join(lines)
