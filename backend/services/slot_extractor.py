# backend/services/slot_extractor.py
import os, json
from pydantic import ValidationError
from google import genai
from google.genai.types import HttpOptions
from .slot_schema import SlotExtraction

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Supported JSON Schema subset (no $schema/$id/$defs)
SLOT_EXTRACTION_SCHEMA = {
    "title": "SlotExtraction",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["nearby", "within", "gap", "rank", "aggregate"],
        },
        "target_category": {"type": "string", "nullable": True},
        "metrics": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        "dimensions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        "filters": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "field": {"type": "string"},
                    "op": {
                        "type": "string",
                        "enum": ["eq","neq","gt","gte","lt","lte","in","within_km"],
                    },
                    "value": {"type": "string"},
                },
                "required": ["field", "op", "value"],
            },
        },
    },
    "required": ["intent", "metrics", "dimensions", "filters"],
}

SYSTEM_PROMPT = """You extract analytics/GIS slots from a natural-language question.
Return ONLY JSON with keys: intent, target_category, metrics[], dimensions[], filters[].
- intent ∈ {nearby, within, gap, rank, aggregate}
- operators ∈ {eq, neq, gt, gte, lt, lte, in, within_km}
Example:
{"intent":"gap","target_category":"coffee_shop","metrics":[],"dimensions":[{"name":"tract"}],
 "filters":[{"field":"income","op":"gt","value":"70000"},{"field":"distance","op":"within_km","value":"1"}]}
"""

def _client() -> genai.Client:
    # Vertex mode picked up from env (GOOGLE_GENAI_USE_VERTEXAI / PROJECT / LOCATION)
    return genai.Client(http_options=HttpOptions(api_version="v1"))

def extract_slots_genai(user_query: str) -> SlotExtraction:
    client = _client()
    resp = client.models.generate_content(
        model=MODEL,
        contents=[SYSTEM_PROMPT, user_query],
        config={
            "response_mime_type": "application/json",
            "response_schema": SLOT_EXTRACTION_SCHEMA,
        },
    )

    data = resp.parsed if hasattr(resp, "parsed") and resp.parsed is not None else json.loads(resp.text)
    try:
        return SlotExtraction.model_validate(data)
    except ValidationError as e:
        raise RuntimeError(f"Schema validation failed: {e}\nJSON: {json.dumps(data, indent=2)}")
