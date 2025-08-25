# cli/setup_search.py
from __future__ import annotations
from backend.config import get_config
from tools.create_bucket import ensure_bucket
from tools.export_to_gcs import export_table_to_jsonl
from google.cloud import discoveryengine_v1 as de
from tools.create_datastore import create_or_replace_datastore
import os

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
        ("poi_entities_search",      "search_exports/poi_entities_search.jsonl"),
        ("org_locations_search",     "search_exports/org_locations_search.jsonl")
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

    # 3)  Create two datastores (categories + gazetteer)


    PROJECT_ID = os.getenv("PROJECT_ID")
    SEARCH_LOCATION = os.getenv("SEARCH_LOCATION", "global")
    COLLECTION_ID = os.getenv("COLLECTION_ID", "default_collection")
    SEARCH_DATASTORE_CATEGORIES = os.getenv("SEARCH_DATASTORE_CATEGORIES")
    SEARCH_DATASTORE_GAZETTEER = os.getenv("SEARCH_DATASTORE_GAZETTEER")


    assert PROJECT_ID and SEARCH_DATASTORE_CATEGORIES and SEARCH_DATASTORE_GAZETTEER, "Set PROJECT_ID and SEARCH_DATASTORE_CATEGORIES and SEARCH_DATASTORE_GAZETTEER in your .env"

    cat_ds = create_or_replace_datastore(
        project_id=PROJECT_ID,
        location=SEARCH_LOCATION,
        collection_id=COLLECTION_ID,
        data_store_id=SEARCH_DATASTORE_CATEGORIES,
        display_name=SEARCH_DATASTORE_CATEGORIES,
        industry_vertical=de.IndustryVertical.GENERIC,
        solution_types=(de.SolutionType.SOLUTION_TYPE_SEARCH,),
        content_config=de.DataStore.ContentConfig.NO_CONTENT,
        overwrite=False, # Set to True to overwrite existing datastore (if any)
    )

    print(cat_ds)

    gaz_ds = create_or_replace_datastore(
        project_id=PROJECT_ID,
        location=SEARCH_LOCATION,
        collection_id=COLLECTION_ID,
        data_store_id=SEARCH_DATASTORE_GAZETTEER,
        display_name=SEARCH_DATASTORE_GAZETTEER,
        industry_vertical=de.IndustryVertical.GENERIC,
        solution_types=(de.SolutionType.SOLUTION_TYPE_SEARCH,),
        content_config=de.DataStore.ContentConfig.NO_CONTENT,
        overwrite=False, # Set to True to overwrite existing datastore (if any)
    )

    print(gaz_ds)
    print("✅ setup_search completed.")

if __name__ == "__main__":
    main()
