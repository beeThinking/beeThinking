from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    APP_NAME: str = "BeeThinking Backend"
    APP_ENV: str = "development"
    DEBUG: bool = False
    ADMIN_EMAILS: str = ""

    # Frontend base URL — used for QR deep links
    FRONTEND_BASE_URL: str = "http://localhost:4200"

    # CORS — comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost,http://localhost:80,http://localhost:4200,http://localhost:3000"

    # Email (optional)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@beethinking.com"
    EMAIL_CONFIRMATION_ENABLED: bool = False

    # Google Calendar sync (optional)
    GOOGLE_CALENDAR_CLIENT_ID: str = ""
    GOOGLE_CALENDAR_CLIENT_SECRET: str = ""
    GOOGLE_CALENDAR_REDIRECT_URI: str = "http://localhost:8000/api/google-calendar/oauth/callback"
    GOOGLE_CALENDAR_FRONTEND_URL: str = "http://localhost:4200/appointments"
    GOOGLE_CALENDAR_TOKEN_KEY: str = ""

    # Object storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "beethinking"
    MINIO_SECRET_KEY: str = "beethinking-minio-password"
    MINIO_BUCKET: str = "beethinking-photos"
    MINIO_SECURE: bool = False
    PHOTO_UPLOAD_MAX_BYTES: int = 10 * 1024 * 1024
    RECEIPT_UPLOAD_MAX_BYTES: int = 20 * 1024 * 1024

    # Varroa weather planning
    VARROA_WEATHER_PROVIDER: str = "open_meteo"
    VARROA_WEATHER_CACHE_TTL_HOURS: int = 6

    @model_validator(mode="after")
    def validate_production_security(self):
        insecure_secrets = {
            "",
            "your-secret-key-here-change-in-production",
            "change-me",
            "secret",
        }
        if self.APP_ENV.lower() == "production" and self.SECRET_KEY in insecure_secrets:
            raise ValueError("SECRET_KEY must be set to a secure random value in production")
        if self.GOOGLE_CALENDAR_CLIENT_ID and not self.GOOGLE_CALENDAR_TOKEN_KEY:
            raise ValueError(
                "GOOGLE_CALENDAR_TOKEN_KEY must be set when Google Calendar is enabled. "
                "Refresh tokens are encrypted with this key; falling back to SECRET_KEY would "
                "break stored tokens whenever SECRET_KEY rotates."
            )
        return self

    @property
    def google_calendar_enabled(self) -> bool:
        return bool(self.GOOGLE_CALENDAR_CLIENT_ID and self.GOOGLE_CALENDAR_CLIENT_SECRET)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def admin_emails_set(self) -> set[str]:
        return {email.strip().lower() for email in self.ADMIN_EMAILS.split(",") if email.strip()}

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
