
---

## `docs/cli/setup_search.md`

```markdown
# setup_search.py

Creates or updates a Vertex AI Search datastore.

## Behavior
- Reads schema definitions from JSON files (`SCHEMA_FILES` in `.env`)
- Creates or updates the datastore in Vertex AI Search
- Handles missing configs gracefully (returns error code)

## Arguments
- `--config` (required): Path to schema JSON file
- `--overwrite` (optional, default=false): Replace existing schema if present

## Response Codes
- **0** → Success (datastore created/updated)
- **1** → Missing required config (e.g., GCS_BUCKET not set)
- **2** → API error (invalid project, location, or credentials)
- **3** → Schema validation failed

## How to Run
```bash
# Run with default SCHEMA_FILES from .env
python cli/setup_search.py

# Run with specific schema
python cli/setup_search.py --config config/datastore_schema/org_schema.json

# Overwrite existing schema
python cli/setup_search.py --config config/datastore_schema/org_schema.json --overwrite
