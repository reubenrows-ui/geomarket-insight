# tests/conftest.py
import os
import pytest
import importlib

@pytest.fixture(autouse=True)
def reset_config_cache(monkeypatch):
    # Ensure no env leakage across tests
    for key in (
        "PROJECT_ID",
        "DATASET_NAME",
        "LOCATION",
        "GCS_BUCKET",
        "SEARCH_LOCATION",
        "SEARCH_COLLECTION_ID",
        "SEARCH_DATASTORE_CATEGORIES",
        "SEARCH_DATASTORE_GAZETTEER",
        "USER_AGENT",
    ):
        monkeypatch.delenv(key, raising=False)

    # Clear get_config() cache before each test
    import shared.config.settings as config
    config.get_config.cache_clear()  # type: ignore[attr-defined]
    yield
    config.get_config.cache_clear()  # type: ignore[attr-defined]
