from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, date
from typing import List
import uuid

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://harvestnet:password123@postgres:5432/harvestnet"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class BatchCreate(BaseModel):
    crop_type: str
    variety: str
    quantity_kg: float
    storage_location: str
    harvest_date: str
    expected_sell_by: str

class BatchResponse(BaseModel):
    id: str
    crop_type: str
    variety: str
    quantity_kg: float
    storage_location: str
    harvest_date: str
    expected_sell_by: str
    safe_days: int
    mold_risk: float

# Initialize database
def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS farms (
                id UUID PRIMARY KEY,
                name VARCHAR NOT NULL,
                location VARCHAR,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS batches (
                id UUID PRIMARY KEY,
                farm_id UUID REFERENCES farms(id),
                crop_type VARCHAR NOT NULL,
                variety VARCHAR,
                initial_quantity_kg FLOAT NOT NULL,
                current_quantity_kg FLOAT NOT NULL,
                storage_location VARCHAR,
                harvest_date DATE,
                expected_sell_by DATE,
                safe_days_remaining INTEGER DEFAULT 0,
                mold_risk_percent FLOAT DEFAULT 0,
                status VARCHAR DEFAULT 'active',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Insert demo farm
        conn.execute(text("""
            INSERT INTO farms (id, name, location) 
            VALUES ('11111111-1111-1111-1111-111111111111', 'Demo Farm', 'Kenya')
            ON CONFLICT (id) DO NOTHING
        """))
        
        # Insert demo batches if empty
        result = conn.execute(text("SELECT COUNT(*) FROM batches"))
        if result.scalar() == 0:
            conn.execute(text("""
                INSERT INTO batches (id, farm_id, crop_type, variety, initial_quantity_kg, current_quantity_kg, storage_location, harvest_date, expected_sell_by, safe_days_remaining, mold_risk_percent, status) VALUES 
                (gen_random_uuid(), '11111111-1111-1111-1111-111111111111', '🌽 Maize', 'DK 777', 2500, 2500, 'Warehouse A', '2024-04-01', '2024-06-15', 45, 8, 'active'),
                (gen_random_uuid(), '11111111-1111-1111-1111-111111111111', '🍚 Rice', 'Basmati', 1800, 1800, 'Warehouse B', '2024-04-05', '2024-07-01', 60, 4, 'active'),
                (gen_random_uuid(), '11111111-1111-1111-1111-111111111111', '🌾 Wheat', 'Sharbati', 3200, 3200, 'Silo 1', '2024-04-10', '2024-06-30', 30, 12, 'active'),
                (gen_random_uuid(), '11111111-1111-1111-1111-111111111111', '🍅 Tomato', 'Cherry', 500, 500, 'Cold Storage', '2024-04-12', '2024-04-30', 7, 25, 'active'),
                (gen_random_uuid(), '11111111-1111-1111-1111-111111111111', '🥔 Potato', 'Russet', 4500, 4500, 'Root Cellar', '2024-03-25', '2024-07-15', 90, 3, 'active')
            """))
        conn.commit()

init_db()

# API Endpoints
@app.get("/")
def root():
    return {"message": "HarvestNet API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/batches", response_model=List[BatchResponse])
def get_batches():
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT id::text, crop_type, variety, current_quantity_kg, storage_location, 
                   harvest_date, expected_sell_by, safe_days_remaining, mold_risk_percent
            FROM batches WHERE status = 'active' ORDER BY created_at DESC
        """))
        return [
            {
                "id": row[0],
                "crop_type": row[1],
                "variety": row[2] or "",
                "quantity_kg": float(row[3]),
                "storage_location": row[4] or "",
                "harvest_date": row[5].isoformat() if row[5] else "",
                "expected_sell_by": row[6].isoformat() if row[6] else "",
                "safe_days": row[7],
                "mold_risk": float(row[8])
            }
            for row in result
        ]
    finally:
        db.close()

@app.post("/api/batches")
def create_batch(batch: BatchCreate):
    db = SessionLocal()
    try:
        batch_id = str(uuid.uuid4())
        farm_id = "11111111-1111-1111-1111-111111111111"
        
        # Calculate safe days
        sell_by = datetime.strptime(batch.expected_sell_by, '%Y-%m-%d')
        safe_days = max(0, (sell_by - datetime.now()).days)
        
        db.execute(text("""
            INSERT INTO batches (id, farm_id, crop_type, variety, initial_quantity_kg, current_quantity_kg,
                               storage_location, harvest_date, expected_sell_by, safe_days_remaining, mold_risk_percent, status)
            VALUES (:id, :farm_id, :crop_type, :variety, :quantity, :quantity,
                    :location, :harvest_date, :sell_by, :safe_days, 0, 'active')
        """), {
            "id": batch_id,
            "farm_id": farm_id,
            "crop_type": batch.crop_type,
            "variety": batch.variety,
            "quantity": batch.quantity_kg,
            "location": batch.storage_location,
            "harvest_date": batch.harvest_date,
            "sell_by": batch.expected_sell_by,
            "safe_days": safe_days
        })
        db.commit()
        return {"id": batch_id, "message": "Batch created", "safe_days": safe_days}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.delete("/api/batches/{batch_id}")
def delete_batch(batch_id: str):
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM batches WHERE id = :id"), {"id": batch_id})
        db.commit()
        return {"message": "Deleted"}
    finally:
        db.close()

@app.get("/api/dashboard/summary")
def dashboard_summary():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT COUNT(*) FROM batches WHERE status = 'active'"))
        count = result.scalar() or 0
        return {"summary": {"active_batches": count}, "batches": []}
    finally:
        db.close()

from fastapi import HTTPException
