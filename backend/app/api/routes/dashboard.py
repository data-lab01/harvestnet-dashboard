from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.farm import Farm
from app.models.batch import Batch
from app.models.sensor import SensorReading
from app.models.alert import Alert
from app.api.dependencies import get_current_farm

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(
    farm: Farm = Depends(get_current_farm),
    db: AsyncSession = Depends(get_db)
):
    """Get all dashboard metrics in one request"""
    
    # Get active batches
    active_batches_query = await db.execute(
        select(Batch).where(
            Batch.farm_id == farm.id,
            Batch.status == "active"
        )
    )
    active_batches = active_batches_query.scalars().all()
    
    # Calculate safe days remaining (minimum across all batches)
    safe_days = min([b.safe_days_remaining for b in active_batches]) if active_batches else 0
    
    # Get latest sensor readings
    latest_readings = {}
    for batch in active_batches:
        reading_query = await db.execute(
            select(SensorReading)
            .where(SensorReading.batch_id == batch.id)
            .order_by(SensorReading.timestamp.desc())
            .limit(1)
        )
        reading = reading_query.scalar_one_or_none()
        if reading:
            latest_readings[batch.id] = reading
    
    # Get active alerts
    alerts_query = await db.execute(
        select(Alert)
        .where(
            Alert.farm_id == farm.id,
            Alert.resolved == False
        )
        .order_by(Alert.severity.desc(), Alert.created_at.desc())
        .limit(10)
    )
    active_alerts = alerts_query.scalars().all()
    
    # Calculate loss metrics
    loss_query = await db.execute(
        select(
            func.avg(Batch.estimated_loss_percent),
            func.sum(Batch.initial_quantity - Batch.current_quantity)
        ).where(Batch.farm_id == farm.id)
    )
    avg_loss, total_lost = loss_query.one()
    
    return {
        "summary": {
            "active_batches": len(active_batches),
            "safe_days_remaining": safe_days,
            "critical_alerts": len([a for a in active_alerts if a.severity == "critical"]),
            "avg_loss_percent": float(avg_loss or 0),
            "total_quantity_lost_kg": float(total_lost or 0),
            "estimated_value_lost": float((total_lost or 0) * 0.25)  # $0.25/kg average
        },
        "status": {
            "color": "green" if safe_days > 30 else "yellow" if safe_days > 10 else "red",
            "message": f"{safe_days} days until loss risk becomes critical"
        },
        "batches": [
            {
                "id": b.id,
                "crop_type": b.crop_type,
                "quantity_kg": b.current_quantity,
                "safe_days": b.safe_days_remaining,
                "current_temp": latest_readings.get(b.id).temperature if latest_readings.get(b.id) else None,
                "current_humidity": latest_readings.get(b.id).humidity if latest_readings.get(b.id) else None,
                "mold_risk": b.mold_risk_percent
            }
            for b in active_batches
        ],
        "alerts": [
            {
                "id": a.id,
                "severity": a.severity,
                "message": a.message,
                "created_at": a.created_at.isoformat()
            }
            for a in active_alerts
        ]
    }

@router.get("/sensor-history/{batch_id}")
async def get_sensor_history(
    batch_id: str,
    hours: int = 24,
    farm: Farm = Depends(get_current_farm),
    db: AsyncSession = Depends(get_db)
):
    """Get historical sensor data for a batch"""
    
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    readings_query = await db.execute(
        select(SensorReading)
        .where(
            SensorReading.batch_id == batch_id,
            SensorReading.timestamp >= cutoff
        )
        .order_by(SensorReading.timestamp)
    )
    readings = readings_query.scalars().all()
    
    return {
        "timestamps": [r.timestamp.isoformat() for r in readings],
        "temperatures": [r.temperature for r in readings],
        "humidities": [r.humidity for r in readings],
        "co2_levels": [r.co2 for r in readings],
        "moisture_contents": [r.moisture_content for r in readings]
    }
    