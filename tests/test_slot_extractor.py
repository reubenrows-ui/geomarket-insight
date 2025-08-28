from backend.services.slot_extractor import extract_slots
from backend.agents.slot_agent import SlotAgent

def test_structured_output_basic():
    s = extract_slots("Find areas with income > 70000 and no coffee shops within 1 km")
    assert s.intent in {"nearby","within","gap","rank","aggregate"}
    assert any(f.op in {"gt","within_km"} for f in s.filters)

def test_agent_resolution():
    agent = SlotAgent()
    out = agent.respond("show me neighbourhoods with no cafes within 500 meters")
    assert out["target_category"] in {"coffee_shop", None}
