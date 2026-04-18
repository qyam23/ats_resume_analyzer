from __future__ import annotations

import json
from pathlib import Path

from huggingface_hub import HfApi


DATASETS = [
    "cnamuangtoun/resume-job-description-fit",
    "opensporks/resumes",
    "lang-uk/recruitment-dataset-job-descriptions-english",
    "ThanuraRukshan/resume-score-details",
]


def main() -> None:
    api = HfApi()
    output: list[dict[str, object]] = []
    for repo_id in DATASETS:
        try:
            info = api.dataset_info(repo_id)
            siblings = [s.rfilename for s in getattr(info, "siblings", [])[:20]]
            output.append(
                {
                    "repo_id": repo_id,
                    "sha": getattr(info, "sha", ""),
                    "downloads": getattr(info, "downloads", None),
                    "likes": getattr(info, "likes", None),
                    "tags": getattr(info, "tags", []),
                    "card_data": _safe_card_data(getattr(info, "card_data", None)),
                    "sample_files": siblings,
                    "recommended_use": _recommended_use(repo_id),
                }
            )
        except Exception as exc:
            output.append({"repo_id": repo_id, "error": str(exc), "recommended_use": "unavailable"})
    out_path = Path("reports") / "dataset_audit_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


def _recommended_use(repo_id: str) -> str:
    if "resumes" in repo_id:
        return "mining only: section and structure patterns"
    if "job-descriptions" in repo_id:
        return "mining/calibration: JD titles, seniority and keyword language"
    if "score-details" in repo_id:
        return "benchmarking only: synthetic labels must not control scoring"
    return "mining/benchmarking only until labels and license are manually audited"


def _safe_card_data(card_data: object) -> object:
    if card_data is None:
        return None
    if hasattr(card_data, "to_dict"):
        return card_data.to_dict()
    if isinstance(card_data, dict):
        return card_data
    return str(card_data)


if __name__ == "__main__":
    main()
