from typing import List, Optional
from pydantic import BaseModel, Field

class Metric(BaseModel):
    name: str = Field(..., description="Logical metric")

class Dimension(BaseModel):
    name: str = Field(..., description="Logical dimension")

class Filter(BaseModel):
    field: str
    op: str = Field(..., description="eq, neq, gt, gte, lt, lte, in, within_km")
    value: str

class SlotExtraction(BaseModel):
    intent: str = Field(..., description="nearby | within | gap | rank | aggregate")
    target_category: Optional[str] = None
    metrics: List[Metric] = []
    dimensions: List[Dimension] = []
    filters: List[Filter] = []
