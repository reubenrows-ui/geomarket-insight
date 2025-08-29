# backend/api.py
from fastapi import FastAPI, Query
from agents.workflows.query_workflow import run_query
from agents.components.slot_extractor import extract_slots  # direct extractor endpoint

app = FastAPI(title="GeoMarket Insight API")

@app.get("/extract_slots")
def extract_slots_endpoint(q: str = Query(...)):
    return extract_slots(q).model_dump()

@app.get("/agent/slots")
async def agent_slots_endpoint(q: str = Query(...)):
    # Use our unified workflow
    return run_query(q, context={})
