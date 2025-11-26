import strawberry
from typing import Optional, List
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
    created_at: datetime


@strawberry.type
class MachineStatusType:
    machine_id: str
    temperature: Optional[float]
    vibration: Optional[int]
    production_count: Optional[int]
    fault: bool
    last_updated: datetime


@strawberry.type
class AlertType:
    id: int
    machine_id: str
    alert_type: str
    severity: str
    message: Optional[str]
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime]


@strawberry.type
class SystemStatsType:
    total_machines: int
    active_machines: int
    total_measurements: int
    active_alerts: int