import pytest

from app.core.config import Settings


@pytest.mark.unit
class TestGoogleCalendarTokenKeyValidation:
    def test_calendar_without_token_key_is_rejected(self):
        with pytest.raises(ValueError, match="GOOGLE_CALENDAR_TOKEN_KEY"):
            Settings(
                DATABASE_URL="sqlite://",
                SECRET_KEY="test-secret",
                GOOGLE_CALENDAR_CLIENT_ID="client-id",
                GOOGLE_CALENDAR_CLIENT_SECRET="client-secret",
                GOOGLE_CALENDAR_TOKEN_KEY="",
                _env_file=None,
            )

    def test_calendar_with_token_key_is_accepted(self):
        settings = Settings(
            DATABASE_URL="sqlite://",
            SECRET_KEY="test-secret",
            GOOGLE_CALENDAR_CLIENT_ID="client-id",
            GOOGLE_CALENDAR_CLIENT_SECRET="client-secret",
            GOOGLE_CALENDAR_TOKEN_KEY="separate-token-key",
            _env_file=None,
        )

        assert settings.google_calendar_enabled is True

    def test_calendar_disabled_needs_no_token_key(self):
        settings = Settings(
            DATABASE_URL="sqlite://",
            SECRET_KEY="test-secret",
            _env_file=None,
        )

        assert settings.google_calendar_enabled is False
