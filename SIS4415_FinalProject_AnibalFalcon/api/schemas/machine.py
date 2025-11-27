from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class MachineCreate(BaseModel):
    machine_id: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="active", max_length=20)


class MachineResponse(BaseModel):
    id: int
    machine_id: str
    name: str
    location: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MeasurementCreate(BaseModel):
    machine_id: str = Field(..., max_length=20)
    temperature: Optional[Decimal] = Field(None, ge=0, le=200)
    vibration: Optional[int] = Field(None, ge=0, le=100)
    production_count: Optional[int] = Field(None, ge=0)
    fault: bool = False
    timestamp: datetime


class MeasurementResponse(BaseModel):
    id: int
    machine_id: str
    temperature: Optional[Decimal]
    vibration: Optional[int]
    production_count: Optional[int]
    fault: bool
    timestamp: datetime
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


class AlertResponse(BaseModel):
    id: int
    machine_id: str
    alert_type: str
    severity: str
    message: Optional[str]
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True