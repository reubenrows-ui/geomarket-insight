# cli/setup_search.py
from __future__ import annotations
from backend.config import get_config
from tools.create_bucket import ensure_bucket
from tools.export_to_gcs import export_table_to_jsonl

def _validate_cfg(cfg):
    missing = []
    for k in ("PROJECT_ID", "DATASET_NAME", "LOCATION", "GCS_BUCKET"):
        if not getattr(cfg, k):
            missing.append(k)
    if missing:
        raise ValueError(f"[setup_search] Missing required config: {', '.join(missing)}")

def main():
    cfg = get_config()
    _validate_cfg(cfg)

    # 1) bucket
    ensure_bucket(cfg.GCS_BUCKET, cfg.LOCATION)
    print(f"✅ Bucket ready: gs://{cfg.GCS_BUCKET}")

    # 2) exports (paths MUST NOT start with '/'; we normalize anyway)
    exports = [
        ("poi_entities",      "search_exports/poi_entities.jsonl"),
        ("org_locations",     "search_exports/org_locations.jsonl"),
        ("area_boundaries",   "search_exports/area_boundaries.jsonl"),
        ("area_indicators",   "search_exports/area_indicators.jsonl"),
    ]

    for table, path in exports:
        export_table_to_jsonl(
            project_id=cfg.PROJECT_ID,
            dataset=cfg.DATASET_NAME,
            table=table,
            gcs_bucket=cfg.GCS_BUCKET,
            gcs_path=path,                       # no leading slash
            user_agent=cfg.USER_AGENT or "geomarket-insight",
            location=cfg.LOCATION or "US",
        )

    # 3) (Optional) Discovery Engine creation/import would go here

    print("✅ setup_search completed.")

if __name__ == "__main__":
    main()
