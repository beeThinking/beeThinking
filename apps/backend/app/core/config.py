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

    # CORS — comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost,http://localhost:80,http://localhost:4200,http://localhost:3000"

    # Email (optional)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@beethinking.com"
    EMAIL_CONFIRMATION_ENABLED: bool = False

    # Object storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "beethinking"
    MINIO_SECRET_KEY: str = "beethinking-minio-password"
    MINIO_BUCKET: str = "beethinking-photos"
    MINIO_SECURE: bool = False

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
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
