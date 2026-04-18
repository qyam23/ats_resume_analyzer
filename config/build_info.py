from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from config.settings import BASE_DIR


def get_build_info() -> dict[str, str]:
    info = {
        "source_commit": os.getenv("GITHUB_SHA", ""),
        "build_timestamp": os.getenv("BUILD_TIMESTAMP", ""),
        "analyzer_version": "atsa-domain-fit-v2-keyword-intel",
    }
    file_path = BASE_DIR / "build_info.json"
    if file_path.exists():
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            info.update({key: str(value) for key, value in data.items() if value})
        except Exception:
            pass
    if not info["source_commit"]:
        try:
            info["source_commit"] = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=BASE_DIR,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=2,
            ).strip()
        except Exception:
            info["source_commit"] = "unknown"
    return info
