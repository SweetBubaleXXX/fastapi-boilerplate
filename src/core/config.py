import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)

    API_TITLE: str = "API"
    API_DESCRIPTION: str = ""
    API_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    DB_URL: str = "sqlite+aiosqlite:///:memory:"
    TEST_DB_URL: str = "sqlite+aiosqlite:///:memory:"

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        extra="ignore",
    )


settings = Settings()
