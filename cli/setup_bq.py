from google.cloud import bigquery
from backend.config import get_config

# --- Paste your full SQL (no ellipses) into these strings ---
def poi_entities_sql(dataset_id: str) -> str:
    return f"""
    -- CREATE OR REPLACE POI table from OSM points (California)
    -- TODO: Paste the full SQL from your infra_setup.py here (without ...).
    -- Example header (keep dataset_id substitution):
    CREATE OR REPLACE TABLE `{dataset_id}.poi_entities` AS
    SELECT
      a.osm_id AS id,
      a.geometry,
      (SELECT t.value FROM UNNEST(a.all_tags) AS t WHERE t.key = 'name')    AS name,
      (SELECT t.value FROM UNNEST(a.all_tags) AS t WHERE t.key = 'amenity') AS amenity,
      (SELECT t.value FROM UNNEST(a.all_tags) AS t WHERE t.key = 'cuisine') AS cuisine,
      (SELECT t.value FROM UNNEST(a.all_tags) AS t WHERE t.key = 'brand')   AS brand
    FROM `bigquery-public-data.geo_openstreetmap.planet_features_points` AS a
    JOIN `bigquery-public-data.geo_us_boundaries.states` AS b
      ON ST_CONTAINS(b.state_geom, a.geometry)
    WHERE b.state_name = 'California'
    -- ... rest of your filters/clauses ...
    ;
    """

def area_indicators_sql(dataset_id: str) -> str:
    return f"""
    -- CREATE OR REPLACE area_indicators by joining ACS to ZIP geometries (California)
    -- TODO: Paste the full SQL from your infra_setup.py here (without ...).
    CREATE OR REPLACE TABLE `{dataset_id}.area_indicators` AS
    SELECT
      b.zip_code AS area_id,
      b.zip_code_geom AS geometry,
      b.city,
      b.county,
      a.total_pop,
      a.households,
      a.median_income
    FROM `bigquery-public-data.census_bureau_acs.zip_codes_2018_5yr` AS a
    LEFT JOIN `bigquery-public-data.geo_us_boundaries.zip_codes` AS b
      ON a.geo_id = b.zip_code
    WHERE b.state_name = 'California'
    ;
    """

def area_boundaries_sql(dataset_id: str) -> str:
    return f"""
    -- CREATE OR REPLACE area_boundaries (ZIP envelopes + subarea aggregation)
    -- TODO: Paste the full SQL from your infra_setup.py here (without ...).
    CREATE OR REPLACE TABLE `{dataset_id}.area_boundaries` AS
    SELECT
      a.zip_code AS area_id,
      a.city,
      a.county,
      a.zip_code_geom AS geometry
    FROM `bigquery-public-data.geo_us_boundaries.zip_codes` AS a
    WHERE a.state_name = 'California'
    ;
    """

def ensure_dataset(client: bigquery.Client, dataset_id: str, location: str):
    ds = bigquery.Dataset(dataset_id)
    ds.location = location
    return client.create_dataset(ds, exists_ok=True)

def ensure_org_locations_table(client: bigquery.Client, dataset_id: str):
    """
    Creates or truncates `{dataset_id}.org_locations` using the schema
    taken from your uploaded infra_setup.py (id, name, address, geometry, revenue_last_year, open_date).
    """
    table_id = f"{dataset_id}.org_locations"
    schema = [
        bigquery.SchemaField("id", "INT64"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("address", "STRING"),
        bigquery.SchemaField("geometry", "GEOGRAPHY"),
        bigquery.SchemaField("revenue_last_year", "INT64"),
        bigquery.SchemaField("open_date", "DATETIME"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    client.delete_table(table_id, not_found_ok=True)
    client.create_table(table)
    print(f"✅ Ensured table (truncated): {table_id}")

def run_query(client: bigquery.Client, sql: str, label: str):
    job = client.query(sql)
    job.result()
    print(f"✅ {label}")

def main():
    cfg = get_config()
    client = bigquery.Client(project=cfg.PROJECT_ID)
    dataset_id = cfg.DATASET_ID

    ensure_dataset(client, dataset_id, cfg.LOCATION)
    print(f"✅ Dataset ready: {dataset_id} [{cfg.LOCATION}]")

    # Create/refresh the three core tables
    run_query(client, poi_entities_sql(dataset_id), "poi_entities created")
    run_query(client, area_indicators_sql(dataset_id), "area_indicators created")
    run_query(client, area_boundaries_sql(dataset_id), "area_boundaries created")

    # Materialize org_locations as a managed table with your schema
    ensure_org_locations_table(client, dataset_id)

if __name__ == "__main__":
    main()
