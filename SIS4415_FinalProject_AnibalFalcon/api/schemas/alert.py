from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AlertBase(BaseModel):
    machine_id: str = Field(..., max_length=20)
    alert_type: str = Field(..., max_length=50)
    severity: str = Field(..., max_length=20)
    message: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    resolved: bool
    resolved_at: Optional[datetime] = None


class AlertResponse(AlertBase):
    id: int
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True