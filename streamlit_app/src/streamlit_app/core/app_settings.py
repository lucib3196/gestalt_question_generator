from functools import lru_cache
from enum import Enum
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ENV(str, Enum):
    LOCAL = "local"
    PRODUCTION = "production"


class AppSettings(BaseSettings):
    # -------------------------------------------------
    # App
    # -------------------------------------------------
    name: str = "gestalt_streamlit_template"

    # -------------------------------------------------
    # Environment
    # -------------------------------------------------
    environment: ENV = ENV.LOCAL

    # -------------------------------------------------
    # LLM Server
    # -------------------------------------------------
    local_url: str = "http://127.0.0.1:2024"
    production_url: str = ""

    # -------------------------------------------------
    # Secrets
    # -------------------------------------------------
    langsmith_api_key: str | None = None

    # -------------------------------------------------
    # Derived
    # -------------------------------------------------
    @property
    def url(self) -> str:
        return self.local_url if self.environment == ENV.LOCAL else self.production_url

    # -------------------------------------------------
    # Pydantic config
    # -------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> AppSettings:
    """
    Cached settings instance.
    Safe for Streamlit, FastAPI, CLI.
    """
    return AppSettings()
