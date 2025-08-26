# tools/engines.py
from __future__ import annotations

from typing import Iterable, List, Tuple, Union, Dict

from google.api_core import exceptions
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as de


# --------------------------
# Helpers
# --------------------------

def _endpoint_for(location: str) -> str:
    loc = (location or "global").lower()
    return "discoveryengine.googleapis.com" if loc == "global" else f"{loc}-discoveryengine.googleapis.com"


def _engine_name(project_id: str, location: str, collection_id: str, engine_id: str) -> str:
    return (
        f"projects/{project_id}/locations/{location}"
        f"/collections/{collection_id}/engines/{engine_id}"
    )


# --------------------------
# Engine ensure / update
# --------------------------

def ensure_engine_with_datastores(
    *,
    project_id: str,
    location: str,
    collection_id: str,
    engine_id: str,
    display_name: str | None = None,
    data_store_ids: list[str] | None = None,
    solution_type: de.SolutionType = de.SolutionType.SOLUTION_TYPE_SEARCH,
    industry_vertical: de.IndustryVertical = de.IndustryVertical.GENERIC,
) -> de.Engine:
    """
    Idempotently create an Engine (if missing) and ensure it is linked to the given datastores.
    """
    loc = (location or "global").lower()
    endpoint = _endpoint_for(loc)
    client = de.EngineServiceClient(client_options=ClientOptions(api_endpoint=endpoint))
    parent = f"projects/{project_id}/locations/{loc}/collections/{collection_id}"
    name = f"{parent}/engines/{engine_id}"

    try:
        engine = client.get_engine(name=name)
    except exceptions.NotFound:
        engine = de.Engine(
            display_name=display_name or engine_id,
            industry_vertical=industry_vertical,
            solution_type=solution_type,
            data_store_ids=list(data_store_ids or []),
        )
        op = client.create_engine(parent=parent, engine=engine, engine_id=engine_id)
        return op.result()

    # Update linked datastores if different
    want = set(data_store_ids or [])
    have = set(engine.data_store_ids)
    if want and want != have:
        engine.data_store_ids[:] = list(want)
        op = client.update_engine(engine=engine)
        engine = op.result()

    return engine


# --------------------------
# Import JSONL into engine
# --------------------------

def _normalize_uris(gcs_uris: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(gcs_uris, str):
        uris = [gcs_uris]
    else:
        uris = list(gcs_uris or [])
    if not uris:
        raise ValueError("gcs_uris must contain at least one GCS URI (string or iterable).")
    return uris


def import_to_engine_from_gcs(
    *,
    engine_id: str,
    gcs_uris: Union[str, Iterable[str]],
    project_id: str,
    location: str,
    collection_id: str,
    branch_id: str = "default_branch",
    reconciliation_mode: de.ImportDocumentsRequest.ReconciliationMode = de.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    timeout: int = 1800,
) -> List[Dict[str, object]]:
    """
    Import JSONL documents (URI or wildcard pattern) into ALL datastores attached to an Engine.
    Returns a list of dicts:
      {"data_store_id": <id>, "success_count": <int>, "failure_count": <int>}
    """
    uris = _normalize_uris(gcs_uris)
    loc = (location or "global").lower()
    endpoint = _endpoint_for(loc)

    # 1) Resolve engine and attached datastores
    eng_client = de.EngineServiceClient(client_options=ClientOptions(api_endpoint=endpoint))
    engine_path = _engine_name(project_id, loc, collection_id, engine_id)
    try:
        engine = eng_client.get_engine(name=engine_path)
    except exceptions.NotFound as e:
        raise exceptions.NotFound(f"Engine not found: {engine_path}") from e

    if not engine.data_store_ids:
        raise ValueError(f"Engine '{engine_id}' has no linked data_store_ids; nothing to import into.")

    # 2) GCS source
    doc_client = de.DocumentServiceClient(client_options=ClientOptions(api_endpoint=endpoint))
    gcs_source = de.GcsSource(input_uris=uris)

    # 3) Import into each attached datastore's branch
    results: List[Dict[str, object]] = []
    for ds_id in engine.data_store_ids:
        parent = (
            f"projects/{project_id}/locations/{loc}/collections/{collection_id}"
            f"/dataStores/{ds_id}/branches/{branch_id}"
        )

        req = de.ImportDocumentsRequest(
            parent=parent,
            gcs_source=gcs_source,
            reconciliation_mode=reconciliation_mode,
        )
        op = doc_client.import_documents(request=req)
        # Wait for completion
        _ = op.result(timeout=timeout)

        # Get counts from operation metadata (not response)
        md = op.metadata() if callable(getattr(op, "metadata", None)) else getattr(op, "metadata", None)
        success = getattr(md, "success_count", None)
        failure = getattr(md, "failure_count", None)

        results.append({
            "data_store_id": ds_id,
            "success_count": int(success) if success is not None else None,
            "failure_count": int(failure) if failure is not None else None,
        })

    return results


# --------------------------
# Convenience wrapper
# --------------------------

def import_from_config(
    cfg: dict,
    *,
    project_id: str,
    location: str,
    collection_id: str,
    branch_id: str = "default_branch",
    filename_pattern: str = "export-*.jsonl.gz",
    reconciliation_mode: de.ImportDocumentsRequest.ReconciliationMode = de.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    timeout: int = 1800,
) -> Tuple[str, List[Dict[str, object]]]:
    """
    Import using a config dict containing:
      - ENGINE_ID (str) : required
      - GCS_PATH (str)  : required (file or prefix). If prefix, pattern is appended.
    Returns (engine_id, results[list of dicts])
    """
    engine_id = cfg.get("ENGINE_ID")
    gcs_path = cfg.get("GCS_PATH")
    if not engine_id or not gcs_path:
        raise ValueError("Config must include ENGINE_ID and GCS_PATH.")

    # Append shard pattern if not a file
    if not (gcs_path.endswith(".jsonl") or gcs_path.endswith(".jsonl.gz")):
        gcs_path = gcs_path.rstrip("/") + f"/{filename_pattern}"

    results = import_to_engine_from_gcs(
        engine_id=engine_id,
        gcs_uris=gcs_path,
        project_id=project_id,
        location=location,
        collection_id=collection_id,
        branch_id=branch_id,
        reconciliation_mode=reconciliation_mode,
        timeout=timeout,
    )
    return engine_id, results
