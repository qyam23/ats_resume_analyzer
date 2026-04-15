from __future__ import annotations

from qa_suite.qa_schemas import QAActualResult, QAChecks, QAEvaluationResult, QAMatrixCase


FIT_THRESHOLDS = {
    "strong": {"min_score": 58, "min_visibility": 42, "bad_decisions": ["LOW VISIBILITY"]},
    "medium": {"min_score": 38, "max_score": 82, "min_visibility": 25, "bad_decisions": []},
    "weak_to_medium": {"max_score": 72, "max_visibility": 78, "bad_decisions": ["APPLY"]},
    "weak": {"max_score": 64, "max_visibility": 68, "bad_decisions": ["APPLY"]},
}


def evaluate_case(case: QAMatrixCase, actual: QAActualResult) -> QAEvaluationResult:
    band = _normalize_band(case.expected_fit_band)
    notes: list[str] = []
    failures: list[str] = []
    checks = QAChecks()

    checks.decision_match = _decision_is_reasonable(case.expected_decision_tendency, actual.decision, band)
    if not checks.decision_match:
        failures.append(f"Decision '{actual.decision}' does not align with expected tendency '{case.expected_decision_tendency}'.")

    checks.fit_band_reasonable = _score_is_reasonable(band, actual.final_ats_score)
    if not checks.fit_band_reasonable:
        failures.append(f"Final ATS score {actual.final_ats_score:.1f} is outside expected '{band}' behavior.")

    checks.visibility_reasonable = _visibility_is_reasonable(band, actual.visibility_score)
    if not checks.visibility_reasonable:
        failures.append(f"Visibility score {actual.visibility_score:.1f} is outside expected '{band}' behavior.")

    checks.parse_reasonable = actual.ats_parse_score >= 70
    if not checks.parse_reasonable:
        failures.append(f"ATS parse score is unexpectedly low for a generated clean resume: {actual.ats_parse_score:.1f}.")

    checks.signals_present = bool(actual.missing_keywords or actual.why_not_found or actual.top_fixes)
    if not checks.signals_present:
        notes.append("Missing-signal/fix explanations are thin.")

    checks.product_outputs_present = actual.transformed_blocks_count > 0 and actual.rewrite_preview_available
    if not checks.product_outputs_present:
        failures.append("Product transformation outputs are missing.")

    checks.career_outputs_present = bool(actual.career_suggestions) and actual.job_search_plan_available
    if not checks.career_outputs_present:
        notes.append("Career suggestions or job-search plan are missing.")

    if actual.final_ats_score < 30 and band == "strong":
        failures.append("Strong-fit case collapsed into a weak score band.")
    if actual.final_ats_score > 82 and band == "weak":
        failures.append("Weak-fit case was scored as very strong.")
    if len(actual.top_fixes) == 0:
        notes.append("No actionable top fixes returned.")
    if len(actual.what_ats_sees) == 0 or len(actual.what_recruiter_sees) == 0:
        notes.append("ATS/recruiter explanation fields are sparse.")

    status = _status_from_checks(failures, notes, checks)
    return QAEvaluationResult(
        case_id=case.case_id,
        resume_variant_id=case.resume_variant_id,
        job_id=case.jd_id,
        expected_fit_band=case.expected_fit_band,
        expected_decision_tendency=case.expected_decision_tendency,
        source_languages=case.source_languages,
        actual=actual,
        checks=checks,
        status=status,
        notes=notes,
        failure_reasons=failures,
    )


def _normalize_band(value: str) -> str:
    text = (value or "").strip().lower().replace("-", "_")
    if text in {"weak_medium", "weak_to_medium", "weak/medium"}:
        return "weak_to_medium"
    if text in {"strong", "medium", "weak"}:
        return text
    return "medium"


def _decision_is_reasonable(expected_tendency: str, decision: str, band: str) -> bool:
    expected = (expected_tendency or "").upper()
    actual = (decision or "").upper()
    if "APPLY_OR_APPLY_WITH_FIXES" in expected:
        return "APPLY" in actual
    if "APPLY_WITH_FIXES" in expected:
        return "FIX" in actual or "APPLY" in actual
    if "LOW_VISIBILITY_OR_APPLY_WITH_FIXES" in expected:
        return "LOW" in actual or "FIX" in actual or "APPLY" in actual
    if band == "strong":
        return "APPLY" in actual
    if band == "weak":
        return "LOW" in actual or "FIX" in actual
    return bool(actual)


def _score_is_reasonable(band: str, score: float) -> bool:
    threshold = FIT_THRESHOLDS.get(band, FIT_THRESHOLDS["medium"])
    if "min_score" in threshold and score < threshold["min_score"]:
        return False
    if "max_score" in threshold and score > threshold["max_score"]:
        return False
    return True


def _visibility_is_reasonable(band: str, score: float) -> bool:
    threshold = FIT_THRESHOLDS.get(band, FIT_THRESHOLDS["medium"])
    if "min_visibility" in threshold and score < threshold["min_visibility"]:
        return False
    if "max_visibility" in threshold and score > threshold["max_visibility"]:
        return False
    return True


def _status_from_checks(failures: list[str], notes: list[str], checks: QAChecks) -> str:
    hard_failures = [
        not checks.fit_band_reasonable,
        not checks.parse_reasonable,
        not checks.product_outputs_present,
    ]
    if any(hard_failures) or len(failures) >= 3:
        return "fail"
    if failures or notes:
        return "warning"
    return "pass"
