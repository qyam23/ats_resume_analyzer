# Keyword Intelligence Research Notes

This note records the research inputs used for the dataset-informed keyword and structure layer. The production scorer remains deterministic; these sources are used for mining, calibration ideas, and regression thinking only.

## Hugging Face Datasets

### `cnamuangtoun/resume-job-description-fit`
- Source: https://huggingface.co/datasets/cnamuangtoun/resume-job-description-fit
- Observed shape: resume and JD text pairs in the viewer, useful for resume/JD fit examples.
- Quality notes: noisy and long text rows; safe for benchmarking and mining phrasing patterns, not direct training without deduplication and label audit.
- Product use: mine requirement phrasing, resume/JD overlap patterns, and hard-skill wording.
- Status: mining / benchmarking only.

### `opensporks/resumes`
- Source: https://huggingface.co/datasets/opensporks/resumes
- Observed shape: 2400+ resume examples with `Resume_str`, `Resume_html`, `Category`, and PDF references.
- Quality notes: scraped example resumes; useful for section-title and structure patterns, but not reliable as ground truth fit data.
- Product use: section alias discovery, resume category vocabulary, formatting/structure heuristics.
- Status: mining only.

### `lang-uk/recruitment-dataset-job-descriptions-english`
- Source: https://huggingface.co/datasets/lang-uk/recruitment-dataset-job-descriptions-english
- Observed shape: Djinni job postings with role titles, descriptions, company names, experience, keywords, language, dates, and IDs.
- Quality notes: large recruitment-language corpus, especially useful for English IT/software roles and job-title patterns.
- Product use: JD structure, title/seniority language, keyword phrase patterns, posting-noise filtering.
- Status: calibration / mining, with citation required for published research.

### `SaitejaKumboji/resume-score-details`
- Source requested by product brief, but search results surfaced the closely related `ThanuraRukshan/resume-score-details`: https://huggingface.co/datasets/ThanuraRukshan/resume-score-details
- Observed shape: GPT-4o-generated resume/JD scoring JSONs, including macro/micro scores and minimum requirement booleans.
- Quality notes: synthetic labels are useful for test inspiration, but should not override ATSA scoring business logic.
- Product use: regression-case inspiration for hard-requirement booleans and explanation structure.
- Status: benchmarking only.

## GitHub References

### `OmkarPathak/pyresparser`
- Source: https://github.com/OmkarPathak/pyresparser
- Useful ideas: contact parsing, skill vocabulary matching, education/company/designation extraction, JSON output shape.
- Caution: older dependency stack and GPL-3.0 licensing mean code should not be copied into this project.
- Adapted idea: keep field extraction deterministic and vocabulary-backed.

### `AnasAito/SkillNER`
- Source: https://github.com/AnasAito/SkillNER
- Useful ideas: skill phrase extraction with a taxonomy/ontology mindset and explainable matching.
- Caution: verify license and maintenance before any dependency adoption.
- Adapted idea: maintain local alias dictionaries and keep ambiguous terms, such as `pm`, context-sensitive.

### `Panagiotis-T/job-ad-skill-extraction`
- Source: https://github.com/Panagiotis-T/job-ad-skill-extraction
- Useful ideas: job-ad-specific extraction, phrase windows around requirements, and skill clustering.
- Caution: adapt heuristics only after tests; do not introduce an unreviewed ML dependency path.
- Adapted idea: separate must-have requirements, nice-to-have skills, tools, title family, seniority, and domain-specific terms.

## Semantic Model Choice

- Primary: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Why: multilingual practical default for Hebrew/English compatibility, small enough for local/HF Docker use, already configured.
- Fallback: TF-IDF cosine similarity already exists when local model loading fails.
- Deferred alternatives:
  - `sentence-transformers/all-mpnet-base-v2`: stronger English quality, less suitable as universal Hebrew/English default.
  - `sentence-transformers/all-MiniLM-L6-v2`: very fast English fallback, weaker multilingual coverage.

## Product Decision

The new layer adds normalization assets and safer deterministic matching. It does not train a model, does not use synthetic scores as truth, and does not let any LLM calculate the final ATS score.
