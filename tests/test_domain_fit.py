from core.domain_fit import apply_domain_fit_adjustment
from core.parsers.jd_parser import parse_job_description
from core.schemas import ExperienceEntry, ResumeStructuredData


def test_jd_parser_prefers_explicit_role_title_over_sentence_fragment():
    jd = parse_job_description(
        """
        NVIDIA
        Role title: Thermal Mechanical Engineering Manager, Liquid Cooling Systems
        Our team. In this role, you will lead the development of chip-to-rack cooling systems.
        Requirements:
        10+ years of experience in thermal engineering leadership.
        """
    )

    assert jd.role_title == "Thermal Mechanical Engineering Manager, Liquid Cooling Systems"
    assert jd.role_title_inferred is False
    assert not jd.role_title.lower().startswith("team.")


def test_domain_fit_caps_generic_leadership_for_specialized_thermal_role():
    jd = parse_job_description(
        """
        Role title: Thermal Mechanical Engineering Manager, Liquid Cooling Systems
        Requirements:
        Required thermal engineering leadership, liquid cooling, thermo-mechanical analysis,
        chip-to-rack systems thinking, high-power electronics cooling, TIM, joining and soldering technologies.
        """
    )
    resume = ResumeStructuredData(
        summary="Senior industrial engineering leader with plant execution, automation, suppliers, and process improvement.",
        experience=[
            ExperienceEntry(
                job_title="Project Engineering Manager",
                achievements=["Led cross-functional industrial projects and improved production throughput."],
            )
        ],
        hard_skills=["manufacturing engineering", "automation", "supplier management", "process improvement"],
        leadership_signals=["led cross-functional teams", "managed suppliers", "owned delivery"],
        quantified_achievements=["Improved throughput by 20%."],
    )

    adjusted = apply_domain_fit_adjustment(
        resume=resume,
        jd=jd,
        resume_text=resume.summary,
        keyword_score=78,
        semantic_score=76,
        title_alignment_score=75,
        leadership_alignment_score=90,
        missing_keywords=[],
    )

    assert adjusted.semantic_score <= 42
    assert adjusted.keyword_score <= 44
    assert adjusted.leadership_alignment_score <= 55
    assert "liquid cooling" in adjusted.missing_keywords
    assert adjusted.diagnostics["penalty_applied"] is True
