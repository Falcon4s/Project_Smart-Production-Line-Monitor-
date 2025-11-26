from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from api.database import get_db
from api.models.machine import Machine
from api.models.measurement import Measurement, MachineStatus
from api.schemas.machine import MachineResponse
from api.schemas.measurement import MeasurementCreate, MeasurementResponse, MachineStatusResponse
from api.utils.dependencies import get_current_user

router = APIRouter(prefix="/machines", tags=["Machines"])


@router.post("/data", status_code=status.HTTP_201_CREATED)
def receive_machine_data(
    measurement: MeasurementCreate,
    db: Session = Depends(get_db)
):
    """Recibir datos de Node-RED (sin autenticación para facilitar integración)"""
    # Verificar que la máquina existe
    machine = db.query(Machine).filter(Machine.machine_id == measurement.machine_id).first()
    
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine {measurement.machine_id} not found"
        )
    
    # Crear nueva medición
    new_measurement = Measurement(**measurement.model_dump())
    db.add(new_measurement)
    
    # Actualizar estado actual de la máquina
    machine_status = db.query(MachineStatus).filter(
        MachineStatus.machine_id == measurement.machine_id
    ).first()
    
    if machine_status:
        machine_status.temperature = measurement.temperature
        machine_status.vibration = measurement.vibration
        machine_status.production_count = measurement.production_count
        machine_status.fault = measurement.fault
        machine_status.last_updated = measurement.timestamp
    else:
        new_status = MachineStatus(
            machine_id=measurement.machine_id,
            temperature=measurement.temperature,
            vibration=measurement.vibration,
            production_count=measurement.production_count,
            fault=measurement.fault,
            last_updated=measurement.timestamp
        )
        db.add(new_status)
    
    db.commit()
    
    return {"status": "success", "message": "Data received"}


@router.get("", response_model=List[MachineResponse])
def get_machines(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener lista de máquinas (protegido con JWT)"""
    machines = db.query(Machine).all()
    return machines


@router.get("/status", response_model=List[MachineStatusResponse])
def get_machines_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener estado actual de todas las máquinas (protegido con JWT)"""
    statuses = db.query(MachineStatus).all()
    return statuses


@router.get("/{machine_id}/measurements", response_model=List[MeasurementResponse])
def get_machine_measurements(
    machine_id: str,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener mediciones históricas de una máquina (protegido con JWT)"""
    measurements = db.query(Measurement).filter(
        Measurement.machine_id == machine_id
    ).order_by(Measurement.timestamp.desc()).limit(limit).all()
    
    if not measurements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No measurements found for machine {machine_id}"
        )
    
    return measurements