import strawberry
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from api.database import get_db
from api.models.machine import Machine, Measurement, MachineStatus
from api.graphql.types import (
    MachineType,
    MeasurementType,
    MachineStatusType,
    MachineInput,
    MeasurementInput
)


def get_machines(info) -> List[MachineType]:
    """Get all machines"""
    db: Session = next(get_db())
    try:
        machines = db.query(Machine).all()
        return [
            MachineType(
                id=m.id,
                machine_id=m.machine_id,
                name=m.name,
                location=m.location,
                status=m.status,
                created_at=m.created_at
            )
            for m in machines
        ]
    finally:
        db.close()


def get_machine_by_id(info, machine_id: str) -> Optional[MachineType]:
    """Get a specific machine by ID"""
    db: Session = next(get_db())
    try:
        machine = db.query(Machine).filter(
            Machine.machine_id == machine_id
        ).first()
        
        if not machine:
            return None
        
        return MachineType(
            id=machine.id,
            machine_id=machine.machine_id,
            name=machine.name,
            location=machine.location,
            status=machine.status,
            created_at=machine.created_at
        )
    finally:
        db.close()


def get_measurements(
    info,
    machine_id: Optional[str] = None,
    limit: int = 100
) -> List[MeasurementType]:
    """Get measurements, optionally filtered by machine"""
    db: Session = next(get_db())
    try:
        query = db.query(Measurement)
        
        if machine_id:
            query = query.filter(Measurement.machine_id == machine_id)
        
        measurements = query.order_by(
            desc(Measurement.timestamp)
        ).limit(limit).all()
        
        return [
            MeasurementType(
                id=m.id,
                machine_id=m.machine_id,
                temperature=float(m.temperature) if m.temperature else None,
                vibration=m.vibration,
                production_count=m.production_count,
                fault=m.fault,
                timestamp=m.timestamp
            )
            for m in measurements
        ]
    finally:
        db.close()


def get_machine_status(info, machine_id: str) -> Optional[MachineStatusType]:
    """Get current status of a machine"""
    db: Session = next(get_db())
    try:
        status = db.query(MachineStatus).filter(
            MachineStatus.machine_id == machine_id
        ).first()
        
        if not status:
            return None
        
        return MachineStatusType(
            machine_id=status.machine_id,
            temperature=float(status.temperature) if status.temperature else None,
            vibration=status.vibration,
            production_count=status.production_count,
            fault=status.fault,
            last_updated=status.last_updated
        )
    finally:
        db.close()


def get_all_machine_statuses(info) -> List[MachineStatusType]:
    """Get current status of all machines"""
    db: Session = next(get_db())
    try:
        statuses = db.query(MachineStatus).all()
        
        return [
            MachineStatusType(
                machine_id=s.machine_id,
                temperature=float(s.temperature) if s.temperature else None,
                vibration=s.vibration,
                production_count=s.production_count,
                fault=s.fault,
                last_updated=s.last_updated
            )
            for s in statuses
        ]
    finally:
        db.close()


def create_machine(info, machine_input: MachineInput) -> MachineType:
    """Create a new machine"""
    db: Session = next(get_db())
    try:
        new_machine = Machine(
            machine_id=machine_input.machine_id,
            name=machine_input.name,
            location=machine_input.location,
            status=machine_input.status or "active"
        )
        db.add(new_machine)
        db.commit()
        db.refresh(new_machine)
        
        return MachineType(
            id=new_machine.id,
            machine_id=new_machine.machine_id,
            name=new_machine.name,
            location=new_machine.location,
            status=new_machine.status,
            created_at=new_machine.created_at
        )
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def add_measurement(info, measurement_input: MeasurementInput) -> MeasurementType:
    """Add a new measurement"""
    db: Session = next(get_db())
    try:
        new_measurement = Measurement(
            machine_id=measurement_input.machine_id,
            temperature=measurement_input.temperature,
            vibration=measurement_input.vibration,
            production_count=measurement_input.production_count,
            fault=measurement_input.fault,
            timestamp=measurement_input.timestamp or datetime.utcnow()
        )
        db.add(new_measurement)
        
        # Update machine status
        status = db.query(MachineStatus).filter(
            MachineStatus.machine_id == measurement_input.machine_id
        ).first()
        
        if status:
            status.temperature = measurement_input.temperature
            status.vibration = measurement_input.vibration
            status.production_count = measurement_input.production_count
            status.fault = measurement_input.fault
            status.last_updated = measurement_input.timestamp or datetime.utcnow()
        else:
            status = MachineStatus(
                machine_id=measurement_input.machine_id,
                temperature=measurement_input.temperature,
                vibration=measurement_input.vibration,
                production_count=measurement_input.production_count,
                fault=measurement_input.fault,
                last_updated=measurement_input.timestamp or datetime.utcnow()
            )
            db.add(status)
        
        db.commit()
        db.refresh(new_measurement)
        
        return MeasurementType(
            id=new_measurement.id,
            machine_id=new_measurement.machine_id,
            temperature=float(new_measurement.temperature) if new_measurement.temperature else None,
            vibration=new_measurement.vibration,
            production_count=new_measurement.production_count,
            fault=new_measurement.fault,
            timestamp=new_measurement.timestamp
        )
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()