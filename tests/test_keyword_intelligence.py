from __future__ import annotations

from core.keyword_intelligence import canonical_skill, expand_skill_terms, infer_title_family


def test_skill_aliases_normalize_common_tool_variants() -> None:
    expanded = expand_skill_terms({"SQL Server", "TIM", "liquid-cooled"})

    assert "mssql" in expanded
    assert "thermal interface material" in expanded
    assert "liquid cooling" in expanded


def test_pm_is_not_over_normalized_without_context() -> None:
    assert canonical_skill("PM") == "pm"


def test_title_family_recognizes_management_aliases() -> None:
    assert infer_title_family("Technical Manager") == "engineering manager"
