from __future__ import annotations
import os
from functools import lru_cache
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

load_dotenv(override=False)

class AppConfig(BaseModel):
    # GCP / BigQuery
    PROJECT_ID: str = Field(..., description="GCP project")
    DATASET_NAME: str = Field(..., description="BigQuery dataset")
    LOCATION: str = Field(..., description="GCP region, e.g. US")
    GCS_BUCKET: str = Field(..., description="GCS bucket for exports")

    # Vertex AI Search (Discovery Engine)
    SEARCH_LOCATION: str = Field(default="global")
    SEARCH_COLLECTION_ID: str | None = None
    SEARCH_DATASTORE_CATEGORIES: str | None = None
    SEARCH_DATASTORE_GAZETTEER: str | None = None

    # Misc
    USER_AGENT: str | None = None

    @property
    def DATASET_ID(self) -> str:
        return f"{self.PROJECT_ID}.{self.DATASET_NAME}"

@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    try:
        return AppConfig(
            PROJECT_ID=os.getenv("PROJECT_ID", ""),
            DATASET_NAME=os.getenv("DATASET_NAME", ""),
            LOCATION=os.getenv("LOCATION", ""),
            GCS_BUCKET=os.getenv("GCS_BUCKET", ""),
            SEARCH_LOCATION=os.getenv("SEARCH_LOCATION", "global"),
            SEARCH_COLLECTION_ID=os.getenv("SEARCH_COLLECTION_ID"),
            SEARCH_DATASTORE_CATEGORIES=os.getenv("SEARCH_DATASTORE_CATEGORIES"),
            SEARCH_DATASTORE_GAZETTEER=os.getenv("SEARCH_DATASTORE_GAZETTEER"),
            USER_AGENT=os.getenv("USER_AGENT"),
        )
    except ValidationError as e:
        raise SystemExit(f"[config] Missing/invalid settings:\n{e}") from e
