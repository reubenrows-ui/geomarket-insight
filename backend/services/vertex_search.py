# backend/services/vertex_search.py
import os
from typing import List, Dict, Optional
from google.cloud import discoveryengine_v1 as de

DATASTORE_FULL = (
    f"projects/{os.getenv('PROJECT_ID')}"
    f"/locations/{os.getenv('SEARCH_LOCATION')}"
    f"/collections/{os.getenv('SEARCH_COLLECTION_ID')}"
    f"/dataStores/{os.getenv('SEARCH_DATASTORE_NAME')}"
)
SERVING_CONFIG = f"{DATASTORE_FULL}/servingConfigs/default_config"

def search_terms(query: str, page_size: int = 5) -> List[Dict]:
    client = de.SearchServiceClient()
    request = de.SearchRequest(serving_config=SERVING_CONFIG, query=query, page_size=page_size)
    resp = client.search(request)
    out = []
    for r in resp:
        doc = r.document
        out.append({
            "id": doc.id,
            "derived_struct_data": dict(doc.derived_struct_data),
            "content": doc.content,
            "uri": doc.uri,
        })
    return out

def best_term_match(query: str, candidates: List[str]) -> Optional[str]:
    hits = search_terms(query, page_size=3)
    for c in candidates:
        if any(c.lower() in (r.get("content","") or "").lower() for r in hits):
            return c
    for c in candidates:
        if c.lower() in query.lower():
            return c
    return None
