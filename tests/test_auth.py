from fastapi import HTTPException

from config import auth


class DummyRequest:
    def __init__(self, cookies: dict[str, str] | None = None):
        self.cookies = cookies or {}


def test_site_auth_rejects_missing_cookie(monkeypatch):
    monkeypatch.setattr(auth, "auth_is_enabled", lambda: True)
    monkeypatch.setattr(auth, "get_settings", lambda: type("S", (), {"site_password": "pw", "site_auth_secret": "secret", "app_env": "test"})())

    try:
        auth.require_site_auth(DummyRequest())
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("Missing cookie should be rejected.")


def test_site_auth_accepts_signed_cookie(monkeypatch):
    monkeypatch.setattr(auth, "auth_is_enabled", lambda: True)
    monkeypatch.setattr(auth, "get_settings", lambda: type("S", (), {"site_password": "pw", "site_auth_secret": "secret", "app_env": "test"})())
    token = auth._build_session_token(1893456000)

    auth.require_site_auth(DummyRequest({auth.COOKIE_NAME: token}))
