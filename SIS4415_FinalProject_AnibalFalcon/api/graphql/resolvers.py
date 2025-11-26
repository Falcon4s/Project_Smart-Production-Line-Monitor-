from typing import List, Optional, AsyncGenerator
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from api.database import SessionLocal
from api.models.machine import Machine
from api.models.measurement import Measurement, MachineStatus
from api.models.alert import Alert
from api.graphql.types import (
    MachineType,
    MeasurementType,
    MachineStatusType,
    AlertType,
    SystemStatsType
)
import asyncio
from datetime import datetime


# Dependency para obtener DB session
def get_db() -> Session:
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


# Query Resolvers
def get_machines() -> List[MachineType]:
    """Obtener todas las máquinas"""
    db = SessionLocal()
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


def get_machine(machine_id: str) -> Optional[MachineType]:
    """Obtener una máquina específica"""
    db = SessionLocal()
    try:
        machine = db.query(Machine).filter(Machine.machine_id == machine_id).first()
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


def get_machines_status() -> List[MachineStatusType]:
    """Obtener estado actual de todas las máquinas"""
    db = SessionLocal()
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


def get_measurements(machine_id: Optional[str] = None, limit: int = 100) -> List[MeasurementType]:
    """Obtener mediciones (opcionalmente filtradas por máquina)"""
    db = SessionLocal()
    try:
        query = db.query(Measurement)
        if machine_id:
            query = query.filter(Measurement.machine_id == machine_id)
        
        measurements = query.order_by(Measurement.timestamp.desc()).limit(limit).all()
        
        return [
            MeasurementType(
                id=m.id,
                machine_id=m.machine_id,
                temperature=float(m.temperature) if m.temperature else None,
                vibration=m.vibration,
                production_count=m.production_count,
                fault=m.fault,
                timestamp=m.timestamp,
                created_at=m.created_at
            )
            for m in measurements
        ]
    finally:
        db.close()


def get_alerts(resolved: Optional[bool] = None) -> List[AlertType]:
    """Obtener alertas (opcionalmente filtradas por estado)"""
    db = SessionLocal()
    try:
        query = db.query(Alert)
        if resolved is not None:
            query = query.filter(Alert.resolved == resolved)
        
        alerts = query.order_by(Alert.created_at.desc()).all()
        
        return [
            AlertType(
                id=a.id,
                machine_id=a.machine_id,
                alert_type=a.alert_type,
                severity=a.severity,
                message=a.message,
                resolved=a.resolved,
                created_at=a.created_at,
                resolved_at=a.resolved_at
            )
            for a in alerts
        ]
    finally:
        db.close()


def get_system_stats() -> SystemStatsType:
    """Obtener estadísticas generales del sistema"""
    db = SessionLocal()
    try:
        total_machines = db.query(func.count(Machine.id)).scalar()
        active_machines = db.query(func.count(Machine.id)).filter(Machine.status == 'active').scalar()
        total_measurements = db.query(func.count(Measurement.id)).scalar()
        active_alerts = db.query(func.count(Alert.id)).filter(Alert.resolved == False).scalar()
        
        return SystemStatsType(
            total_machines=total_machines or 0,
            active_machines=active_machines or 0,
            total_measurements=total_measurements or 0,
            active_alerts=active_alerts or 0
        )
    finally:
        db.close()


# Subscription Resolvers
async def live_machine_data() -> AsyncGenerator[List[MachineStatusType], None]:
    """Subscription para datos en tiempo real de máquinas"""
    while True:
        db = SessionLocal()
        try:
            statuses = db.query(MachineStatus).all()
            yield [
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
        
        await asyncio.sleep(2)  # Actualizar cada 2 segundos


async def live_alerts() -> AsyncGenerator[List[AlertType], None]:
    """Subscription para alertas en tiempo real"""
    while True:
        db = SessionLocal()
        try:
            alerts = db.query(Alert).filter(Alert.resolved == False).order_by(Alert.created_at.desc()).all()
            yield [
                AlertType(
                    id=a.id,
                    machine_id=a.machine_id,
                    alert_type=a.alert_type,
                    severity=a.severity,
                    message=a.message,
                    resolved=a.resolved,
                    created_at=a.created_at,
                    resolved_at=a.resolved_at
                )
                for a in alerts
            ]
        finally:
            db.close()
        
        await asyncio.sleep(3)  # Actualizar cada 3 segundos