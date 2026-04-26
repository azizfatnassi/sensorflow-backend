from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import ws

from app.core.config import settings
from app.api.routes import auth 
from app.api.routes import devices
from app.api.routes import alerts
from app.api.routes import readings
app = FastAPI(
    title="SensorFlow API",

    description = "Iot Device Monitoring Platform",
    version = "1.0.0"
    
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://sensorflow-frontend.vercel.app",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(alerts.router)
app.include_router(ws.router)
app.include_router(readings.router)
@app.get("/")
def root():
    return {"message": "SensorFlow API is running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}