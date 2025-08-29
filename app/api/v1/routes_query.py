from fastapi import APIRouter
from agents.workflows.query_workflow import run_query

router = APIRouter()
@router.post("/query")
def query(q: str):
    return run_query(q, context={})
