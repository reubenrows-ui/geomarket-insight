from google.cloud import bigquery
from backend.config import get_config

# --- Paste your full SQL (no ellipses) into these strings ---
def poi_entities_sql(dataset_id: str) -> str:
    return f"""
    SELECT
    id,
    geometry,
    names.primary AS name,
    categories.primary AS primary_category,
    IF
    (categories.alternate IS NULL, NULL, TO_JSON_STRING((
        SELECT
            ARRAY_AGG(DISTINCT ELEMENT)
        FROM
            UNNEST(categories.alternate.list)))) AS alternate_category,
    IF
    (ARRAY_LENGTH(addresses.list)>0, addresses.list[
    OFFSET
        (0)].element.freeform, NULL) AS freeform,
    IF
    (ARRAY_LENGTH(addresses.list)>0, addresses.list[
    OFFSET
        (0)].element.locality, NULL) AS locality,
    IF
    (ARRAY_LENGTH(addresses.list)>0, addresses.list[
    OFFSET
        (0)].element.postcode, NULL) AS postcode,
    IF
    (ARRAY_LENGTH(addresses.list)>0, addresses.list[
    OFFSET
        (0)].element.region, NULL) AS region,
    IF
    (ARRAY_LENGTH(addresses.list)>0, addresses.list[
    OFFSET
        (0)].element.country, NULL) AS country
    FROM
    bigquery-public-data.overture_maps.place
    WHERE
    EXISTS (
    SELECT
        1
    FROM
        UNNEST(addresses.list)
    WHERE
        element.region='CA')
    AND categories.primary IN ("cafe",
        "coffee_roastery",
        "coffee_shop",
        "hong_kong_style_cafe",
        "internet_cafe")
    AND names.primary <> 'Blue Bottle Coffee'
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

def org_locations_sql(dataset_id: str) -> str:
    return f"""
    -- CREATE OR REPLACE area_boundaries (ZIP envelopes + subarea aggregation)
    CREATE OR REPLACE TABLE `{dataset_id}.org_locations` AS
    SELECT
    id,
    geometry,
    names.primary AS name,
    cast(ROUND(40000 + RAND() * (100000 - 40000)) as INT64) as revenue_last_year,
    DATE_ADD(
            PARSE_DATE('%Y-%m-%d', '2000-01-01'),
            INTERVAL CAST(FLOOR(RAND() * (DATE_DIFF(PARSE_DATE('%Y-%m-%d', '2024-12-31'), PARSE_DATE('%Y-%m-%d', '2020-01-01'), DAY) + 1)) AS INT64) DAY
        ) AS open_date,
    IF
    (ARRAY_LENGTH(addresses.list)>0, addresses.list[
    OFFSET
        (0)].element.freeform, NULL) AS freeform,
    IF
    (ARRAY_LENGTH(addresses.list)>0, addresses.list[
    OFFSET
        (0)].element.locality, NULL) AS locality,
    IF
    (ARRAY_LENGTH(addresses.list)>0, addresses.list[
    OFFSET
        (0)].element.postcode, NULL) AS postcode,
    IF
    (ARRAY_LENGTH(addresses.list)>0, addresses.list[
    OFFSET
        (0)].element.region, NULL) AS region,
    IF
    (ARRAY_LENGTH(addresses.list)>0, addresses.list[
    OFFSET
        (0)].element.country, NULL) AS country
    FROM
    bigquery-public-data.overture_maps.place
    WHERE
    EXISTS (
    SELECT
        1
    FROM
        UNNEST(addresses.list)
    WHERE
        element.region='CA')
    AND names.primary = 'Blue Bottle Coffee'
    """

def ensure_dataset(client: bigquery.Client, dataset_id: str, location: str):
    ds = bigquery.Dataset(dataset_id)
    ds.location = location
    return client.create_dataset(ds, exists_ok=True)


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
    run_query(client, org_locations_sql(dataset_id), "org_locations created")



if __name__ == "__main__":
    main()
