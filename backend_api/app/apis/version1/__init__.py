# tessyfarm_smartloop/backend_api/app/apis/version1/__init__.py
from fastapi import APIRouter
from .endpoints import farm_data # Existing sensor data endpoints
from .endpoints import farm_management # New endpoints for farms, fields, cycles
from .endpoints import predictions # Assuming you created predictions.py, or add prediction routes here

api_router = APIRouter()
api_router.include_router(farm_data.router, prefix="/farm-data", tags=["Sensor & Farm Data"]) # Existing
api_router.include_router(farm_management.router, prefix="", tags=["Farm & Crop Cycle Management"]) # New - prefix might be /management
api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"]) # Assuming predictions.py
