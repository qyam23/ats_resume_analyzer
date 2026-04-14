from core.scoring import build_final_scores


def test_final_scores_are_bounded():
    scores = build_final_scores(80, 90, 70, 60, 50, 40, 75)
    assert 0 <= scores.final_ats_score <= 100
    assert scores.parseability_score == 80

