from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import asyncio
import os

from app.api.routes import auth, farms, batches, sensors, alerts, dashboard
from app.api.websocket import ConnectionManager
from app.core.database import init_db
from app.services.alert_engine import AlertEngine

manager = ConnectionManager()
alert_engine = AlertEngine()

# Get allowed origins from environment
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3025").split(",")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    asyncio.create_task(alert_engine.run_continuous())
    yield
    # Shutdown
    await manager.close_all()

app = FastAPI(
    title="HarvestNet API",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware - Updated CORS for port 3025
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(farms.router, prefix="/api/farms", tags=["farms"])
app.include_router(batches.router, prefix="/api/batches", tags=["batches"])
app.include_router(sensors.router, prefix="/api/sensors", tags=["sensors"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

# WebSocket
@app.websocket("/ws/{farm_id}")
async def websocket_endpoint(websocket: WebSocket, farm_id: str):
    await manager.connect(websocket, farm_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_sensor_update(farm_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, farm_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)