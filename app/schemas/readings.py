
from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional


class ReadingCreate(BaseModel):
    value:float
    timestamp:Optional[datetime]=None

class ReadingResponse(BaseModel):
    id: int
    device_id:int
    value: float
    timestamp:datetime
    alert_triggered: bool= False

    model_config={"from_attributes":True}

class ReadingStats(BaseModel):
    min: Optional[float]
    max: Optional[float]
    avg: Optional[float]
    count: int