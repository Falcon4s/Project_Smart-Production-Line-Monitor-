from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from ..database import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    status = Column(String(20), default="active")
    created_at = Column(TIMESTAMP, server_default=func.now())


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(20), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False)
    temperature = Column(DECIMAL(5, 2))
    vibration = Column(Integer)
    production_count = Column(Integer)
    fault = Column(Boolean, default=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class MachineStatus(Base):
    __tablename__ = "machine_status"

    machine_id = Column(String(20), ForeignKey("machines.machine_id", ondelete="CASCADE"), primary_key=True)
    temperature = Column(DECIMAL(5, 2))
    vibration = Column(Integer)
    production_count = Column(Integer)
    fault = Column(Boolean, default=False)
    last_updated = Column(TIMESTAMP, nullable=False)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(20), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text)
    resolved = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    resolved_at = Column(TIMESTAMP)