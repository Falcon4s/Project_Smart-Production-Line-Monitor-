import strawberry
from typing import Optional
from datetime import datetime
from decimal import Decimal


@strawberry.type
class MachineType:
    id: int
    machine_id: str
    name: str
    location: Optional[str]
    status: str
    created_at: datetime


@strawberry.type
class MeasurementType:
    id: int
    machine_id: str
    temperature: Optional[float]
    vibration: Optional[int]
    production_count: Optional[int]
    fault: bool
    timestamp: datetime


@strawberry.type
class MachineStatusType:
    machine_id: str
    temperature: Optional[float]
    vibration: Optional[int]
    production_count: Optional[int]
    fault: bool
    last_updated: datetime


@strawberry.input
class MachineInput:
    machine_id: str
    name: str
    location: Optional[str] = None
    status: Optional[str] = "active"


@strawberry.input
class MeasurementInput:
    machine_id: str
    temperature: Optional[float] = None
    vibration: Optional[int] = None
    production_count: Optional[int] = None
    fault: bool = False
    timestamp: Optional[datetime] = None