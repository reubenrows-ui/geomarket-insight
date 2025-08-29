from __future__ import annotations
from typing import Any, Dict
from .workflows.query_workflow import run_slot_agent as run_query

class SlotAgent:
    def __init__(self, context: Dict[str, Any] | None = None):
        self.context = context or {}

    def __call__(self, query: str):
        return run_query(query)

def build_slot_agent(context: Dict[str, Any] | None = None):
    return SlotAgent(context)
