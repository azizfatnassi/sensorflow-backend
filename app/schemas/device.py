

from typing import Optional
from enum import Enum
from pydantic import BaseModel,Field
from datetime import datetime

class DeviceType(str,Enum):
    temperature="temperature"
    humidity="humidity"
    pressure="pressure"
    co2="co2"

class DeviceCreate(BaseModel):
    name:str= Field(...,min_length=1,max_length=100)
    device_type: DeviceType
    location: Optional[str]=None
    unit: str=Field(...,min_length=1,max_length=20)
    threshold_min: Optional[float]=None
    threshold_max: Optional[float]=None

class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = None
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    is_active: Optional[bool] = None

class DeviceResponse(BaseModel):
    id: int
    name: str
    device_type: DeviceType
    location: Optional[str]
    unit: str
    threshold_min: Optional[float]
    threshold_max: Optional[float]
    is_active: bool
    owner_id: int
    created_at: datetime

    model_config={"from_attributes":True}

class DeviceCreateResponse(DeviceResponse):
        api_key:str