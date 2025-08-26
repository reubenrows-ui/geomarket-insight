# cli/setup_search_infra.py
from __future__ import annotations

import json
import os
from typing import List

from backend.config import get_config
from tools.datastores import create_or_replace_datastore
from tools.schemas import create_or_update_schema  # <-- uses your existing helper
from google.cloud import discoveryengine_v1 as de


# --------------------------
# Validation / helpers
# --------------------------

def _validate_cfg(cfg):
    missing = []
    for k in ("PROJECT_ID", "LOCATION"):
        if not getattr(cfg, k):
            missing.append(k)
    if missing:
        raise ValueError(f"[setup_search_infra] Missing required config: {', '.join(missing)}")


def _split_csv(s: str) -> List[str]:
    return [p.strip() for p in (s or "").split(",") if p.strip()]


def _build_json_schema(schema_json: dict) -> dict:
    """Wrap PROPERTIES/REQUIRED/etc into a Discovery Engine JSON Schema document."""
    schema_id = schema_json["SCHEMA_ID"]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": schema_id,
        "title": f"{schema_id} Schema",
        "type": "object",
        "properties": schema_json["PROPERTIES"],
        "required": schema_json.get("REQUIRED", []),
        "additionalProperties": schema_json.get("ADDITIONAL_PROPERTIES", False),
    }


# --------------------------
# Main
# --------------------------

def main():
    cfg = get_config()
    _validate_cfg(cfg)

    raw = os.getenv("SCHEMA_FILES")
    if not raw:
        raise ValueError("[setup_search_infra] Missing SCHEMA_FILES env var.")
    files = _split_csv(raw)
    if not files:
        raise ValueError(f"[setup_search_infra] SCHEMA_FILES='{raw}' contains no files")

    project_id = os.getenv("PROJECT_ID") or cfg.PROJECT_ID
    search_location = (os.getenv("SEARCH_LOCATION", "global") or "global").lower()
    collection_id = os.getenv("SEARCH_COLLECTION_ID", "default_collection")

    for path in files:
        if not os.path.isfile(path):
            raise ValueError(f"[setup_search_infra] Schema file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            s = json.load(f)

        ds_id = s.get("SEARCH_DATASTORE")
        schema_id = s.get("SCHEMA_ID")
        if not ds_id or not schema_id:
            print(f"⚠️ Skipping {path}: need SEARCH_DATASTORE and SCHEMA_ID")
            continue

        print(f"\n=== Infra for {path} ===")

        # a) Ensure DataStore exists
        print(f"→ Ensuring datastore {ds_id}")
        ds = create_or_replace_datastore(
            project_id=project_id,
            location=search_location,
            collection_id=collection_id,
            data_store_id=ds_id,
            display_name=ds_id,
            industry_vertical=de.IndustryVertical.GENERIC,
            solution_types=(de.SolutionType.SOLUTION_TYPE_SEARCH,),
            content_config=de.DataStore.ContentConfig.NO_CONTENT,
            overwrite=False,
        )
        print(f"   {ds.name}")

        # b) Create/Update Schema for that DataStore
        json_schema = _build_json_schema(s)
        print(f"→ Upserting schema {schema_id} on datastore {ds_id}")
        _ = create_or_update_schema(
            project_id=project_id,
            location=search_location,
            collection_id=collection_id,
            data_store_id=ds_id,
            schema_id=schema_id,
            schema_def=json_schema,
            use_json_schema=True,
            # optional: preserve existing to avoid “removing fields” errors
            preserve_existing_on_update=True,
        )
        print(f"   schema upserted: {schema_id}")

    print("\n✅ setup_search_infra completed.")


if __name__ == "__main__":
    main()
