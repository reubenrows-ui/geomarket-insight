from shared.clients.vertex_search_client import search_validate

def validate_slots(slots: dict, intent: str):
    return search_validate(slots, intent)
