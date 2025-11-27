from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.machine import Alert
from ..schemas.machine import AlertResponse
from ..utils.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    machine_id: Optional[str] = Query(None, description="Filter by machine ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alerts, optionally filtered by resolved status and machine"""
    query = db.query(Alert)
    
    if resolved is not None:
        query = query.filter(Alert.resolved == resolved)
    
    if machine_id:
        query = query.filter(Alert.machine_id == machine_id)
    
    alerts = query.order_by(desc(Alert.created_at)).all()
    
    return alerts


@router.patch("/clear")
async def clear_all_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all unresolved alerts as resolved"""
    try:
        updated = db.query(Alert).filter(
            Alert.resolved == False
        ).update({
            "resolved": True,
            "resolved_at": datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Cleared {updated} alerts"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific alert as resolved"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Alert resolved",
        "alert_id": alert_id
    }