from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.database import Base


class Measurement(Base):
    __tablename__ = "measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(20), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False)
    temperature = Column(Numeric(5, 2))
    vibration = Column(Integer)
    production_count = Column(Integer)
    fault = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    machine = relationship("Machine", back_populates="measurements")


class MachineStatus(Base):
    __tablename__ = "machine_status"
    
    machine_id = Column(String(20), ForeignKey("machines.machine_id", ondelete="CASCADE"), primary_key=True)
    temperature = Column(Numeric(5, 2))
    vibration = Column(Integer)
    production_count = Column(Integer)
    fault = Column(Boolean, default=False)
    last_updated = Column(DateTime(timezone=True), nullable=False)