from __future__ import annotations

import pytest
from fastapi import HTTPException

from api.main import _validate_public_job_url
from urllib.parse import urlparse


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://localhost/job",
        "http://127.0.0.1:8000/job",
        "http://169.254.169.254/latest/meta-data",
    ],
)
def test_job_url_rejects_local_or_non_http_targets(url: str) -> None:
    with pytest.raises(HTTPException):
        _validate_public_job_url(urlparse(url))
