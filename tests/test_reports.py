from pathlib import Path

from core.reporting import write_reports
from core.schemas import AnalysisResult, CompanyResearch, RecommendationBlock, RuntimeSettingsSummary, ScoreBreakdown


def test_report_writer_creates_files(tmp_path: Path):
    result = AnalysisResult(
        scores=ScoreBreakdown(
            parseability_score=90,
            consistency_score=88,
            keyword_match_score=76,
            semantic_match_score=81,
            leadership_alignment_score=60,
            quantified_impact_score=70,
            final_ats_score=80,
        ),
        executive_summary={"en": "summary", "he": "תקציר"},
        detailed_diagnostics={"test": True},
        consistency_mismatches=[],
        recommendations=RecommendationBlock(english=["One"], hebrew=["אחד"]),
        company_research=CompanyResearch(company_name="Acme"),
        timeline=[],
        runtime_settings=RuntimeSettingsSummary(),
        json_report_path="",
        markdown_report_path="",
    )
    json_path, md_path = write_reports(result, tmp_path)
    assert Path(json_path).exists()
    assert Path(md_path).exists()
