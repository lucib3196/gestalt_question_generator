from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings
from typing import Literal
from dotenv import load_dotenv
from functools import lru_cache

# Load .env variables before settings are instantiated.
load_dotenv()


ENV = Literal["dev", "production", "test"]
PROMPT_SOURCE = Literal["local", "production"]


class Settings(BaseSettings):

    # AI Settings
    model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-001"
    google_api_key: str | None = None

    # Vectordatabase
    ASTRA_DB_API_ENDPOINT: str | None = None
    ASTRA_DB_APPLICATION_TOKEN: str | None = None

    env: ENV = "dev"
    prompt_source: PROMPT_SOURCE = "production"

    @model_validator(mode="after")
    def _validate_mode(self):
        if not self.google_api_key:
            raise RuntimeError(f"Missing GOOGLE API Key")
        if not self.model:
            raise RuntimeError("Failed to load AI model. Must be set in ENV")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached validated application settings."""
    return Settings()  # type: ignore


@lru_cache
def get_settings_pretty_print() -> str:
    """Return a readable summary of key runtime settings."""
    settings = get_settings()

    lines = [
        "=== Runtime Settings ===",
        f"ENV: {settings.env}",
        f"Base Model: {settings.model}",
        f"Embedding Model: {settings.embedding_model}",
        f"API Key set {(bool(settings.google_api_key))}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_settings_pretty_print())
