from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class MeasurementBase(BaseModel):
    machine_id: str = Field(..., max_length=20)
    temperature: Optional[Decimal] = Field(None, ge=0, le=200)
    vibration: Optional[int] = Field(None, ge=0, le=100)
    production_count: Optional[int] = Field(None, ge=0)
    fault: bool = Field(default=False)
    timestamp: datetime


class MeasurementCreate(MeasurementBase):
    pass


class MeasurementResponse(MeasurementBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MachineStatusResponse(BaseModel):
    machine_id: str
    temperature: Optional[Decimal]
    vibration: Optional[int]
    production_count: Optional[int]
    fault: bool
    last_updated: datetime

    class Config:
        from_attributes = True