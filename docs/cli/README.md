# CLI Guide

This folder documents all command-line scripts for the project. Each command follows the same conventions:

- **Config** comes from `.env` (see required vars in each doc).
- **Non-destructive by default**; use `--force` to overwrite where supported.
- **JSON/YAML in, JSON/YAML out** for machine-friendliness.

## Index

- [setup_bigquery.md](./setup_bigquery.md) — Create BigQuery dataset/tables
- [setup_search.md](./setup_search.md) — Create/validate Vertex AI Search objects
- [ingest_org_locations.md](./ingest_org_locations.md) — Load your first-party sites
- [ingest_poi_entities.md](./ingest_poi_entities.md) — Load third-party POIs
- [rebuild_search_index.md](./rebuild_search_index.md) — Reindex Search datastore
- [validate_slots.md](./validate_slots.md) — Validate metric/dimension slots via Search
- [run_all.md](./run_all.md) — Orchestrated pipeline runner
- [serve_api.md](./serve_api.md) — Run the local API (dev)
- [deploy_app_engine.md](./deploy_app_engine.md) — Deploy to App Engine

> Tip: Run `python -m cli.<command> --help` for live options.
