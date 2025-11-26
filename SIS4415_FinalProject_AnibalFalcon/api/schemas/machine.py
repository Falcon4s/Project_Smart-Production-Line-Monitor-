from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MachineBase(BaseModel):
    machine_id: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="active", max_length=20)


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=20)


class MachineResponse(MachineBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True