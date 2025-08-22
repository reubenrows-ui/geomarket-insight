# tools/export_to_gcs.py
from __future__ import annotations
from google.cloud import bigquery
from google.api_core.client_info import ClientInfo

def _normalize_path(p: str) -> str:
    # remove accidental leading slashes; GCS URIs must be gs://bucket/dir/file
    return p.lstrip("/")

def export_table_to_jsonl(
    project_id: str,
    dataset: str,
    table: str,
    gcs_bucket: str,
    gcs_path: str,
    user_agent: str | None = None,
    location: str = "US",
):
    """
    Export a BigQuery table to GCS in JSONL format.

    Raises:
        ValueError with helpful message if inputs are invalid.
    """
    errs = []
    if not project_id: errs.append("project_id")
    if not dataset: errs.append("dataset")
    if not table: errs.append("table")
    if not gcs_bucket: errs.append("gcs_bucket")
    if not gcs_path: errs.append("gcs_path")
    if errs:
        raise ValueError(f"[export_table_to_jsonl] Missing required arg(s): {', '.join(errs)}")

    gcs_path = _normalize_path(gcs_path)

    table_id = f"{project_id}.{dataset}.{table}"
    destination_uri = f"gs://{gcs_bucket}/{gcs_path}"

    client_kwargs = {}
    if user_agent:
        client_kwargs["client_info"] = ClientInfo(user_agent=user_agent)

    client = bigquery.Client(project=project_id, **client_kwargs)

    job_config = bigquery.job.ExtractJobConfig(
        destination_format=bigquery.DestinationFormat.NEWLINE_DELIMITED_JSON
    )

    try:
        extract_job = client.extract_table(
            table_id,
            destination_uri,
            location=location,
            job_config=job_config,
        )
        extract_job.result()
    except Exception as e:
        # Add rich context so errors aren't cryptic
        raise RuntimeError(
            f"[export_table_to_jsonl] Failed export\n"
            f"  table_id      = {table_id}\n"
            f"  destination   = {destination_uri}\n"
            f"  location      = {location}\n"
            f"  user_agent    = {user_agent!r}\n"
            f"Original error: {type(e).__name__}: {e}"
        ) from e

    print(f"✅ Exported {table_id} → {destination_uri}")
