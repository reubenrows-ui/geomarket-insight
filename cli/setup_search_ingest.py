# cli/setup_search_ingest.py
from __future__ import annotations

import json
import os
from typing import List

from backend.config import get_config
from tools.create_bucket import ensure_bucket
from tools.export_to_gcs import export_table_to_jsonl  # or export_bq_table_as_de_documents if you added it
from tools.datastore_engines import ensure_engine_with_datastores, import_from_config


# --------------------------
# Validation / helpers
# --------------------------

def _validate_cfg(cfg):
    missing = []
    for k in ("PROJECT_ID", "DATASET_NAME", "LOCATION", "GCS_BUCKET"):
        if not getattr(cfg, k):
            missing.append(k)
    if missing:
        raise ValueError(f"[setup_search_ingest] Missing required config: {', '.join(missing)}")


def _split_csv(s: str) -> List[str]:
    return [p.strip() for p in (s or "").split(",") if p.strip()]


def _build_gcs_uri(cfg, schema: dict, filename_pattern: str = "export-*.jsonl.gz") -> str:
    """
    Build a full gs:// URI from cfg.GCS_BUCKET + schema['GCS_PATH'].
    If GCS_PATH is a file (.jsonl[.gz]) return that; else append pattern.
    """
    bucket = cfg.GCS_BUCKET
    rel_path = schema.get("GCS_PATH")
    if not rel_path:
        raise ValueError("Schema missing GCS_PATH")
    rel_path = rel_path.lstrip("/")

    if rel_path.endswith(".jsonl") or rel_path.endswith(".jsonl.gz"):
        return f"gs://{bucket}/{rel_path}"
    return f"gs://{bucket}/{rel_path.rstrip('/')}/{filename_pattern}"


# --------------------------
# Main
# --------------------------

def main():
    cfg = get_config()
    _validate_cfg(cfg)

    # 1) Ensure bucket exists (for export target)
    ensure_bucket(cfg.GCS_BUCKET, cfg.LOCATION)
    print(f"✅ Bucket ready: gs://{cfg.GCS_BUCKET}")

    # 2) Load schema file list
    raw = os.getenv("SCHEMA_FILES")
    if not raw:
        raise ValueError("[setup_search_ingest] Missing SCHEMA_FILES env var.")
    files = _split_csv(raw)
    if not files:
        raise ValueError(f"[setup_search_ingest] SCHEMA_FILES='{raw}' contains no files")

    # 3) Discovery Engine context
    project_id = os.getenv("PROJECT_ID") or cfg.PROJECT_ID
    search_location = (os.getenv("SEARCH_LOCATION", "global") or "global").lower()
    collection_id = os.getenv("SEARCH_COLLECTION_ID", "default_collection")

    # 4) Per-schema: export → ensure engine link → import
    for path in files:
        if not os.path.isfile(path):
            raise ValueError(f"[setup_search_ingest] Schema file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            s = json.load(f)

        ds_id = s.get("SEARCH_DATASTORE")
        engine_id = s.get("ENGINE_ID") or s.get("engine_id")
        bq_table = s.get("BQ_TABLE_FQN")
        gcs_path_cfg = s.get("GCS_PATH")

        if not ds_id:
            print(f"⚠️ Skipping {path}: missing SEARCH_DATASTORE")
            continue
        if not engine_id:
            print(f"⚠️ Skipping {path}: missing ENGINE_ID")
            continue
        if not bq_table:
            print(f"⚠️ Skipping {path}: missing BQ_TABLE_FQN")
            continue
        if not gcs_path_cfg:
            print(f"⚠️ Skipping {path}: missing GCS_PATH")
            continue

        print(f"\n=== Ingest for {path} ===")

        # a) Export table → JSONL (your existing exporter that writes JSONL rows)
        export_table_to_jsonl(
            project_id=cfg.PROJECT_ID,
            dataset=cfg.DATASET_NAME,
            table=bq_table,
            gcs_bucket=cfg.GCS_BUCKET,
            gcs_path=gcs_path_cfg,  # relative path from schema
            user_agent=cfg.USER_AGENT or "geomarket-insight",
            location=cfg.LOCATION,
        )
        print(f"✅ Exported {bq_table} to gs://{cfg.GCS_BUCKET}/{gcs_path_cfg}")

        # b) Ensure engine exists and is linked to the datastore (safe no-op if already linked)
        print(f"→ Ensuring engine {engine_id} linked to datastore {ds_id}")
        ensure_engine_with_datastores(
            project_id=project_id,
            location=search_location,
            collection_id=collection_id,
            engine_id=engine_id,
            display_name=engine_id,
            data_store_ids=[ds_id],
        )

        # c) Import documents into Engine (supports file or folder)
        import_uri = _build_gcs_uri(cfg, s)
        print(f"→ Importing into engine {engine_id} from {import_uri}")
        try:
            engine_id, results = import_from_config(
                {"ENGINE_ID": engine_id, "GCS_PATH": import_uri},
                project_id=project_id,
                location=search_location,
                collection_id=collection_id,
            )
            for r in results:
                print(
                    f"   {engine_id} @ {r['data_store_id']}: "
                    f"success={r['success_count']}, failure={r['failure_count']}"
                )
        except Exception as e:
            print(f"   ⚠️ Engine import failed for {engine_id}: {e}")

    print("\n✅ setup_search_ingest completed.")


if __name__ == "__main__":
    main()
