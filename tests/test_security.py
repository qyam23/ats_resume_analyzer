from config.logging_utils import redact_secrets
from config.security import sanitized_error


def test_redact_secrets_masks_known_patterns():
    text = "Token sk-1234567890ABCDEF leaked"
    redacted = redact_secrets(text)
    assert "ABCDEF" not in redacted
    assert "sk-" not in redacted


def test_sanitized_error_replaces_bearer_prefix():
    assert "[redacted]" in sanitized_error("Bearer sk-secret")

