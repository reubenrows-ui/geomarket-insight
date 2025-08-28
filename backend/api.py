# backend/api.py
from fastapi import FastAPI, Query
from .agents.slot_agent import build_slot_agent
from .services.slot_extractor import extract_slots  # direct extractor endpoint

app = FastAPI(title="GeoMarket Insight API")

@app.get("/extract_slots")
def extract_slots_endpoint(q: str = Query(...)):
    return extract_slots(q).model_dump()

@app.get("/agent/slots")
async def agent_slots_endpoint(q: str = Query(...)):
    agent = build_slot_agent()
    # Run the agent once with your user query and return the final response text
    from google.adk.runners import InMemoryRunner
    runner = InMemoryRunner(agent=agent, app_name="geomarket-insight")
    events = []
    async for e in runner.run_async(user_message=q):
        events.append(e)
    # Last event should contain the agent's final content; for simplicity, return the last non-empty text
    for e in reversed(events):
        if hasattr(e, "content") and e.content:
            # Your extract_slots tool returns JSON; ensure we return that JSON as dict
            try:
                import json
                return json.loads(e.content.parts[0].text)
            except Exception:
                return {"raw": getattr(e, "content", None)}
    return {"raw": [getattr(x, "content", None) for x in events]}
