from __future__ import annotations

import base64
import hashlib
import hmac
import time

from fastapi import HTTPException, Request, Response

from config.settings import get_settings


COOKIE_NAME = "ats_site_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 12


def auth_is_enabled() -> bool:
    settings = get_settings()
    if getattr(settings, "effective_dev_full_access", False):
        return False
    return bool(settings.site_auth_enabled)


def require_site_auth(request: Request) -> None:
    if getattr(get_settings(), "effective_dev_full_access", False) or not auth_is_enabled():
        return
    settings = get_settings()
    if not settings.site_password:
        raise HTTPException(status_code=503, detail="Site password is not configured.")
    token = request.cookies.get(COOKIE_NAME, "")
    if not verify_session_token(token):
        raise HTTPException(status_code=401, detail="Authentication required.")


def verify_password(password: str) -> bool:
    expected = get_settings().site_password
    return bool(expected) and hmac.compare_digest(password or "", expected)


def issue_session(response: Response) -> None:
    token = _build_session_token(int(time.time()))
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=get_settings().app_env == "production",
        samesite="strict",
        path="/",
    )


def clear_session(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path="/")


def verify_session_token(token: str) -> bool:
    if not token or "." not in token:
        return False
    raw_timestamp, signature = token.split(".", 1)
    try:
        timestamp = int(raw_timestamp)
    except ValueError:
        return False
    if time.time() - timestamp > SESSION_MAX_AGE_SECONDS:
        return False
    expected = _signature(raw_timestamp)
    return hmac.compare_digest(signature, expected)


def _build_session_token(timestamp: int) -> str:
    raw_timestamp = str(timestamp)
    return f"{raw_timestamp}.{_signature(raw_timestamp)}"


def _signature(value: str) -> str:
    settings = get_settings()
    secret = settings.site_auth_secret or settings.site_password
    digest = hmac.new(secret.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
