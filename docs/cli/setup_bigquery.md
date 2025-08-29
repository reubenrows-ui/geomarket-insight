
---

## `docs/cli/setup_bigquery.md`

```markdown
# setup_bigquery.py

Creates and configures BigQuery datasets and tables for competition data.

## Behavior
- Creates dataset if it doesn’t exist (`DATASET_NAME` in `.env`)
- Executes SQL files from `sql/` or `config/` folders
- Ensures schema matches YAML definitions

## Arguments
- `--overwrite` (optional, default=false): Replace existing tables if present
- `--tables` (optional): Comma-separated list of table IDs to create

## Response Codes
- **0** → Success (tables created/updated)
- **1** → Missing required config (e.g., DATASET_NAME not set)
- **2** → SQL execution failed
- **3** → Schema mismatch

## How to Run
```bash
# Run full setup
python cli/setup_bigquery.py

# Overwrite tables
python cli/setup_bigquery.py --overwrite

# Run for specific tables only
python cli/setup_bigquery.py --tables org_locations,poi_entities
