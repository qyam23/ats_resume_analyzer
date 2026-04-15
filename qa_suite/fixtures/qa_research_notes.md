# ATS QA Research Pack

This package is intended to seed a QA engine inside the ATS project.

## Included files
- `resume_variants.json` — five role-positioned resume variants derived from Yuval's Hebrew and English CVs.
- `live_job_descriptions.json` — eight live JD targets with fit-band labels.
- `qa_matrix.json` — case matrix for automated or semi-automated QA.

## Fit bands
Strong:
- jd_01 Eitan Medical
- jd_02 Medtronic
- jd_03 Stratasys
- jd_04 Boston Scientific

Medium:
- jd_05 Plastics App
- jd_06 Manpower Israel

Weak / weak-to-medium:
- jd_07 COBRA IO
- jd_08 Google Data Center Operational Audits

## QA objective
The QA runner should test:
- strong fit behavior
- medium fit behavior
- weak fit behavior
- Hebrew CV behavior
- English CV behavior
- Hebrew-English mixed market behavior

## Minimum output fields to evaluate
For every run, store:
- decision
- final_ats_score
- visibility_score
- recruiter_match_score
- ats_parse_score
- missing_keywords
- why_not_found
- top_fixes
- transformed_blocks
- rewrite_preview
- premium
- job_search_plan

## Human review questions
1. Is the decision direction sensible?
2. Is the visibility explanation credible?
3. Are the missing keywords real and relevant?
4. Are the fixes practical and truthful?
5. Does the premium content feel worth unlocking?
6. Does the role expansion section make sense?
7. Does the job-search plan look useful or generic?

## Recommended next implementation
Build a QA runner that:
1. loads these JSON files,
2. maps each resume variant onto each JD,
3. calls the analyzer,
4. stores outputs,
5. compares expected vs actual behavior,
6. emits a QA report for manual review.
