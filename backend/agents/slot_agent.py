# backend/agents/slot_agent.py
import os, yaml
from typing import Dict, Any, Optional
from ..services.slot_extractor import extract_slots_genai
from ..services.vertex_search import best_term_match

ONTOLOGY_FILE = os.getenv("ONTOLOGY_FILE", "config/ontology/categories.yaml")
ONTOLOGY: Dict[str, Any] = yaml.safe_load(open(ONTOLOGY_FILE, "r"))

def resolve_category(term: str) -> Optional[str]:
    if term in ONTOLOGY:
        return term
    for logical, cfg in ONTOLOGY.items():
        syns = cfg.get("synonyms", [])
        if best_term_match(term, [logical] + syns):
            return logical
    return None

def run_slot_agent(user_text: str) -> Dict[str, Any]:
    slots = extract_slots_genai(user_text)
    if slots.target_category:
        rc = resolve_category(slots.target_category)
        if rc:
            slots.target_category = rc
    for f in slots.filters:
        if f.field in ("category", "amenity"):
            rc = resolve_category(f.value)
            if rc:
                f.value = rc
    return slots.model_dump()
