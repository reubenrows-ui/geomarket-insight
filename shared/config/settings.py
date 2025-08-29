# shared/config/settings.py
import os
from typing import Optional

# Optional: use Pydantic if present; otherwise fall back to a simple class
try:
    from pydantic_settings import BaseSettings  # pydantic v2 style
except Exception:
    try:
        from pydantic import BaseSettings  # pydantic v1 style
    except Exception:
        BaseSettings = object  # type: ignore


class Settings(BaseSettings):
    # Core GCP / Vertex AI
    PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("PROJECT_ID", ""))
    DATASET_NAME: str = os.getenv("DATASET_NAME", "")
    GCS_BUCKET: str = os.getenv("GCS_BUCKET", "")
    SEARCH_LOCATION: str = os.getenv("SEARCH_LOCATION", "global")
    GOOGLE_CLOUD_LOCATION: str =os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    USER_AGENT: str = os.getenv("USER_AGENT", "geomarket-insight")
    LOCATION: str = os.getenv("LOCATION", "US")

    # Gemini
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # ADK (legacy envs still expect this)
    ADK_LOCATION: str = os.getenv("ADK_LOCATION", SEARCH_LOCATION)

    # Ontology path
    ONTOLOGY_FILE: str = os.getenv(
        "ONTOLOGY_FILE",
        "shared/schemas/ontology/categories.yaml",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"   # <- this line allows undeclared env vars without crashing



# Singleton-style settings object (preferred import path)
settings = Settings()  # loaded from env / .env if pydantic is present


# --- Backwards compatibility shims ---
def get_config() -> Settings:
    """
    Legacy accessor used in old tests/code:
        from shared.config.settings import get_config
        cfg = get_config()
    Returns the same singleton `settings`.
    """
    return settings


def reload_settings() -> Settings:
    """
    If env vars change at runtime (e.g., in a notebook),
    call this to re-create the settings instance.
    """
    global settings
    settings = Settings()
    return settings


__all__ = ["Settings", "settings", "get_config", "reload_settings"]
