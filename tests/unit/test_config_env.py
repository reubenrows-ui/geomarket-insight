import importlib
import os

def test_config_loads(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "p")
    monkeypatch.setenv("DATASET_NAME", "d")
    monkeypatch.setenv("LOCATION", "US")
    monkeypatch.setenv("GCS_BUCKET", "b")
    monkeypatch.setenv("SEARCH_LOCATION", "global")
    monkeypatch.setenv("SEARCH_COLLECTION_ID", "default_collection")
    monkeypatch.setenv("SEARCH_DATASTORE_CATEGORIES", "cat_vocab_datastores")
    monkeypatch.setenv("SEARCH_DATASTORE_GAZETTEER", "gazetteer_datastores")
    monkeypatch.setenv("USER_AGENT", "geo_reverse_demo")

    # Ensure fresh import (clear lru_cache)
    m = importlib.import_module("shared.config.settings")
    m.get_config.cache_clear()  # type: ignore[attr-defined]
    cfg = m.get_config()

    assert cfg.DATASET_NAME == "p.d"
    assert cfg.SEARCH_COLLECTION_ID == "default_collection"
