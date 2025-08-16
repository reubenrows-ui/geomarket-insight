# GeoMarket Insight

**Ask questions in plain English, get GIS answers from BigQuery.**  
🏆 Submission for the [BigQuery AI Hackathon 2025](https://www.kaggle.com/competitions/bigquery-ai-hackathon).

## 🌟 What it does
- Users type: *"Find areas with income > $70k and no coffee shops within 1 km"*
- Slot extractor parses query into structured JSON
- Ontology mapper links categories → OSM / ACS
- SQL template generates BigQuery GIS query
- Results → GeoJSON → interactive map

## 📂 Repo structure
- `/backend` – FastAPI service, SQL templates, YAML adapters
- `/frontend` – React + MapLibre interface
- `/notebooks/infra_setup.ipynb` – Creates BigQuery tables
- `/infra/bq/` – Equivalent SQL scripts for reference
- `/tests` – Unit tests

## 🚀 Quickstart
```bash
git clone https://github.com/reubenrows-ui/geomarket-insight.git
cd geomarket-insight
pip install -r requirements.txt
