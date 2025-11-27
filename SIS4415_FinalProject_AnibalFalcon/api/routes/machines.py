from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi.responses import StreamingResponse
import io

from ..database import get_db
from ..models.user import User
from ..models.machine import Machine, Measurement, MachineStatus, Alert
from ..schemas.machine import (
    MachineCreate,
    MachineResponse,
    MeasurementCreate,
    MeasurementResponse,
    MachineStatusResponse,
    AlertResponse
)
from ..utils.dependencies import get_current_user

router = APIRouter()


@router.post("/data", status_code=201)
async def receive_machine_data(
    data: MeasurementCreate,
    db: Session = Depends(get_db)
):
    """
    Receive machine data from Node-RED simulator
    This endpoint is public (no authentication required)
    """
    try:
        # Verify machine exists
        machine = db.query(Machine).filter(
            Machine.machine_id == data.machine_id
        ).first()
        
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Create measurement record
        measurement = Measurement(
            machine_id=data.machine_id,
            temperature=data.temperature,
            vibration=data.vibration,
            production_count=data.production_count,
            fault=data.fault,
            timestamp=data.timestamp
        )
        db.add(measurement)
        
        # Update or create machine status (current state)
        status = db.query(MachineStatus).filter(
            MachineStatus.machine_id == data.machine_id
        ).first()
        
        if status:
            status.temperature = data.temperature
            status.vibration = data.vibration
            status.production_count = data.production_count
            status.fault = data.fault
            status.last_updated = data.timestamp
        else:
            status = MachineStatus(
                machine_id=data.machine_id,
                temperature=data.temperature,
                vibration=data.vibration,
                production_count=data.production_count,
                fault=data.fault,
                last_updated=data.timestamp
            )
            db.add(status)
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Data received",
            "machine_id": data.machine_id,
            "timestamp": data.timestamp
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[MachineResponse])
async def get_machines(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all machines (protected endpoint)"""
    machines = db.query(Machine).all()
    return machines


@router.get("/status", response_model=List[MachineStatusResponse])
async def get_machines_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current status of all machines (protected endpoint)"""
    statuses = db.query(MachineStatus).all()
    return statuses


@router.get("/{machine_id}/measurements", response_model=List[MeasurementResponse])
async def get_machine_measurements(
    machine_id: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get measurement history for a specific machine (protected endpoint)"""
    measurements = db.query(Measurement).filter(
        Measurement.machine_id == machine_id
    ).order_by(
        desc(Measurement.timestamp)
    ).limit(limit).all()
    
    if not measurements:
        raise HTTPException(status_code=404, detail="No measurements found")
    
    return measurements


@router.get("/stats")
async def get_machine_stats(
    start: Optional[datetime] = Query(None, description="Start datetime for statistics"),
    end: Optional[datetime] = Query(None, description="End datetime for statistics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated statistics for all machines within a time window
    Protected endpoint - requires authentication
    """
    try:
        # Build query
        query = db.query(Measurement)
        
        # Apply time filters
        if start:
            query = query.filter(Measurement.timestamp >= start)
        if end:
            query = query.filter(Measurement.timestamp <= end)
        
        # Get all measurements in the time window
        measurements = query.all()
        
        # If no data, return zeros
        if not measurements:
            return {
                "total_production": 0,
                "avg_temperature": 0.0,
                "max_temperature": 0.0,
                "min_temperature": 0.0,
                "avg_vibration": 0.0,
                "max_vibration": 0,
                "min_vibration": 0,
                "fault_count": 0,
                "total_readings": 0,
                "time_window": {
                    "start": start.isoformat() if start else None,
                    "end": end.isoformat() if end else None
                }
            }
        
        # Calculate aggregations
        total_prod = sum(m.production_count or 0 for m in measurements)
        temps = [float(m.temperature) for m in measurements if m.temperature is not None]
        vibs = [int(m.vibration) for m in measurements if m.vibration is not None]
        faults = sum(1 for m in measurements if m.fault)
        
        return {
            "total_production": total_prod,
            "avg_temperature": round(sum(temps) / len(temps), 2) if temps else 0.0,
            "max_temperature": round(max(temps), 2) if temps else 0.0,
            "min_temperature": round(min(temps), 2) if temps else 0.0,
            "avg_vibration": round(sum(vibs) / len(vibs), 2) if vibs else 0.0,
            "max_vibration": max(vibs) if vibs else 0,
            "min_vibration": min(vibs) if vibs else 0,
            "fault_count": faults,
            "total_readings": len(measurements),
            "time_window": {
                "start": start.isoformat() if start else None,
                "end": end.isoformat() if end else None
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")


@router.get("/measurements")
async def get_all_measurements(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(1000, le=5000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get measurements for all machines within a time window
    Used for CSV export
    Protected endpoint - requires authentication
    """
    try:
        query = db.query(Measurement)
        
        if start:
            query = query.filter(Measurement.timestamp >= start)
        if end:
            query = query.filter(Measurement.timestamp <= end)
        
        measurements = query.order_by(
            desc(Measurement.timestamp)
        ).limit(limit).all()
        
        return {
            "count": len(measurements),
            "measurements": [
                {
                    "machine_id": m.machine_id,
                    "temperature": float(m.temperature) if m.temperature else None,
                    "vibration": int(m.vibration) if m.vibration else None,
                    "production_count": int(m.production_count) if m.production_count else None,
                    "fault": m.fault,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in measurements
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving measurements: {str(e)}")
    
@router.get("/export/csv")
async def export_measurements_csv(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export measurements as CSV file
    Protected endpoint - requires authentication
    """
    try:
        query = db.query(Measurement)
        
        if start:
            query = query.filter(Measurement.timestamp >= start)
        if end:
            query = query.filter(Measurement.timestamp <= end)
        
        measurements = query.order_by(desc(Measurement.timestamp)).limit(5000).all()
        
        # Create CSV
        csv_content = "Machine ID,Temperature (°C),Vibration,Production Count (units/min),Fault,Timestamp\n"
        
        for m in measurements:
            csv_content += f"{m.machine_id},{m.temperature or 0},{m.vibration or 0},{m.production_count or 0},{m.fault},{m.timestamp.isoformat()}\n"
        
        # Create filename with timestamp
        now = datetime.utcnow()
        filename = f"production_report_{now.strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Return as downloadable file
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting CSV: {str(e)}")