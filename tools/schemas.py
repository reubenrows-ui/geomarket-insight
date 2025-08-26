# src/search/schemas.py
from __future__ import annotations

import json
from typing import Optional, Union
from google.api_core import exceptions
from google.cloud import discoveryengine_v1 as de

def create_or_update_schema(
    *,
    project_id: str,
    location: str,
    collection_id: str,
    data_store_id: str,
    schema_id: str,
    schema_def: Union[dict, str],
    use_json_schema: bool = True,
    preserve_existing_on_update: bool = True,   # <--- add this
    client: Optional[de.SchemaServiceClient] = None,
    timeout: float = 600.0,
) -> de.Schema:
    client = client or de.SchemaServiceClient()
    parent = f"projects/{project_id}/locations/{location}/collections/{collection_id}/dataStores/{data_store_id}"
    name = f"{parent}/schemas/{schema_id}"

    if use_json_schema:
        if isinstance(schema_def, dict):
            schema_msg = de.Schema(json_schema=json.dumps(schema_def))
        elif isinstance(schema_def, str):
            schema_msg = de.Schema(json_schema=schema_def)
        else:
            raise TypeError("When use_json_schema=True, schema_def must be dict or JSON string.")
    else:
        if not isinstance(schema_def, dict):
            raise TypeError("When use_json_schema=False, schema_def must be a dict.")
        schema_msg = de.Schema(struct_schema=schema_def)

    try:
        op = client.create_schema(parent=parent, schema=schema_msg, schema_id=schema_id)
        return op.result(timeout=timeout)
    except exceptions.AlreadyExists:
        update_body = (
            de.Schema(name=name, json_schema=schema_msg.json_schema)
            if use_json_schema
            else de.Schema(name=name, struct_schema=schema_msg.struct_schema)
        )
        req = de.UpdateSchemaRequest(schema=update_body)
        op = client.update_schema(request=req)
        return op.result(timeout=timeout)
