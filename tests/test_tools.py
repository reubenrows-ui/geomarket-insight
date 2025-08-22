# tests/test_tools.py
import importlib
import os

def test_env_has_required_keys(monkeypatch):
    # Set env for this test
    for k in ["PROJECT_ID", "DATASET_NAME", "LOCATION", "GCS_BUCKET"]:
        monkeypatch.setenv(k, "x")

    # Re-import module and clear cache to be explicit
    m = importlib.import_module("backend.config")
    m.get_config.cache_clear()  # type: ignore[attr-defined]
    cfg = m.get_config()

    assert cfg.PROJECT_ID == "x"
    assert cfg.DATASET_NAME == "x"
    assert cfg.LOCATION == "x"
    assert cfg.GCS_BUCKET == "x"
