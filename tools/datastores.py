# src/search/datastores.py
from typing import Iterable, Optional
from google.api_core import exceptions
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as de


def _endpoint_for(location: str) -> str:
    # Discovery Engine uses regional endpoints except for some "global" flows.
    # If you’re using "global", default endpoint works.
    return (
        "discoveryengine.googleapis.com"
        if location == "global"
        else f"{location}-discoveryengine.googleapis.com"
    )


def create_or_replace_datastore(
    project_id: str,
    location: str,
    collection_id: str,
    data_store_id: str,
    *,
    display_name: str,
    industry_vertical: de.IndustryVertical = de.IndustryVertical.GENERIC,
    solution_types: Optional[Iterable[de.SolutionType]] = (de.SolutionType.SOLUTION_TYPE_SEARCH,),
    content_config: de.DataStore.ContentConfig = de.DataStore.ContentConfig.NO_CONTENT,
    kms_key_name: Optional[str] = None,
    client: Optional[de.DataStoreServiceClient] = None,
    overwrite: bool = True,
    timeout: float = 600.0,
) -> de.DataStore:
    """
    Idempotently create a Discovery Engine DataStore.
    If an existing DataStore is found and overwrite=True, it is deleted then recreated.
    """
    client = client or de.DataStoreServiceClient(
        client_options=ClientOptions(api_endpoint=_endpoint_for(location))
    )

    parent = f"projects/{project_id}/locations/{location}/collections/{collection_id}"
    name = f"{parent}/dataStores/{data_store_id}"

    try:
        existing = client.get_data_store(name=name)
        if not overwrite:
            return existing
        op = client.delete_data_store(name=name)
        op.result(timeout=timeout)
    except exceptions.NotFound:
        pass

    ds = de.DataStore(
        display_name=display_name,
        industry_vertical=industry_vertical,
        solution_types=list(solution_types) if solution_types else [],
        content_config=content_config,
        kms_key_name=kms_key_name or "",
    )
    op = client.create_data_store(
        parent=parent,
        data_store=ds,
        data_store_id=data_store_id,
    )
    return op.result(timeout=timeout)
