from __future__ import annotations

from core.schemas import ScoreBreakdown


def build_final_scores(
    parseability_score: float,
    consistency_score: float,
    keyword_match_score: float,
    semantic_match_score: float,
    leadership_alignment_score: float,
    quantified_impact_score: float,
    title_alignment_score: float,
) -> ScoreBreakdown:
    final_ats = (
        parseability_score * 0.20
        + consistency_score * 0.15
        + keyword_match_score * 0.20
        + semantic_match_score * 0.20
        + leadership_alignment_score * 0.10
        + quantified_impact_score * 0.05
        + title_alignment_score * 0.10
    )
    if keyword_match_score < 20 and semantic_match_score < 35:
        final_ats = min(final_ats, 42.0)
    elif keyword_match_score < 35 and semantic_match_score < 45:
        final_ats = min(final_ats, 55.0)
    if title_alignment_score < 30 and semantic_match_score < 30:
        final_ats = min(final_ats, 38.0)
    return ScoreBreakdown(
        parseability_score=round(parseability_score, 2),
        consistency_score=round(consistency_score, 2),
        keyword_match_score=round(keyword_match_score, 2),
        semantic_match_score=round(semantic_match_score, 2),
        leadership_alignment_score=round(leadership_alignment_score, 2),
        quantified_impact_score=round(quantified_impact_score, 2),
        final_ats_score=round(final_ats, 2),
    )
