# env_check.py

Validates that all required environment variables are set and correctly formatted.

## Behavior
- Loads `.env` file from project root
- Checks for required variables (PROJECT_ID, DATASET_NAME, LOCATION, GCS_BUCKET, SEARCH_* configs)
- Verifies that referenced files (schema, ontology) exist
- Returns response code based on missing or invalid configs

## Arguments
(None)

## Response Codes
- **0** → Success (all required env vars valid)
- **1** → Missing required environment variable
- **2** → File not found (schema/ontology)
- **3** → Invalid path or JSON/YAML parsing error

## How to Run
```bash
# From repo root
python cli/env_check.py
