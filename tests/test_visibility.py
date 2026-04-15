from core.schemas import ContactInfo, JobDescriptionData, ResumeStructuredData
from core.visibility import build_visibility_profile, normalize_hebrew_text


def test_hebrew_normalization_removes_niqqud():
    assert normalize_hebrew_text("מְנַהֵל הנדסה") == "מנהל הנדסה"


def test_visibility_profile_contains_product_fields():
    resume = ResumeStructuredData(
        contact=ContactInfo(email="candidate@example.com"),
        summary="Engineering manager with automation and supplier management experience.",
        hard_skills=["automation", "supplier management"],
        leadership_signals=["managed cross-functional teams"],
        quantified_achievements=["reduced downtime by 20%"],
    )
    jd = JobDescriptionData(
        role_title="Engineering Manager",
        must_have_skills=["automation", "supplier management"],
        leadership_indicators=["manage"],
        raw_text="Engineering Manager automation supplier management",
    )

    profile = build_visibility_profile(resume, jd, resume.summary, [], 95, 90, 85, 80)

    assert profile["visibility_score"] > 70
    assert profile["compatibility_scores"]["workday_like"] > 70
    assert profile["what_ats_sees"]
    assert profile["what_recruiter_sees"]
