# tessyfarm_smartloop/backend_api/app/apis/version1/endpoints/farm_data.py
from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from typing import List, Dict # Keep Dict if you still intend to group by device_id in Python

from ..schemas import SensorDataCreate, SensorDataResponse
from ....core.db import get_db # Navigate up to core.db
from ....models.farm import SensorReading # Navigate up to models.farm

router = APIRouter()

# Remove the DUMMY_SENSOR_DATA_STORE and DUMMY_DB_ID_COUNTER

@router.post("/sensor-data/", response_model=SensorDataResponse, status_code=201)
async def receive_sensor_data(
    data: SensorDataCreate = Body(...), 
    db: Session = Depends(get_db)
):
    """
    Receive sensor data and store it in the database.
    """
    print(f"Received sensor data for device {data.device_id}: {data.model_dump()}")
    
    db_sensor_reading = SensorReading(
        device_id=data.device_id,
        temperature=data.temperature,
        humidity=data.humidity,
        soil_moisture=data.soil_moisture,
        custom_data=data.custom_data,
        timestamp=data.timestamp
        # received_at is handled by database default
    )
    
    db.add(db_sensor_reading)
    db.commit()
    db.refresh(db_sensor_reading)
    
    return db_sensor_reading # FastAPI will automatically convert this to match SensorDataResponse due to from_attributes


@router.get("/sensor-data/{device_id}", response_model=List[SensorDataResponse])
async def get_sensor_data_for_device(
    device_id: str, 
    db: Session = Depends(get_db)
):
    """
    Retrieve all sensor data for a specific device from the database.
    """
    readings = db.query(SensorReading).filter(SensorReading.device_id == device_id).order_by(SensorReading.timestamp.desc()).all()
    if not readings:
        # It's better to return an empty list than a 404 if the device *could* exist but just has no data.
        # A 404 might be appropriate if devices themselves were registered entities and this one wasn't found.
        # For now, an empty list is fine.
        return []
    return readings


@router.get("/sensor-data/", response_model=Dict[str, List[SensorDataResponse]])
async def get_all_sensor_data(db: Session = Depends(get_db)):
    """
    Retrieve all sensor data from the database, grouped by device_id.
    """
    all_readings = db.query(SensorReading).order_by(SensorReading.device_id, SensorReading.timestamp.desc()).all()
    
    grouped_data: Dict[str, List[SensorDataResponse]] = {}
    for reading in all_readings:
        # Convert SQLAlchemy model instance to Pydantic model instance for consistent response
        # This happens automatically if response_model is correctly defined and using from_attributes
        pydantic_reading = SensorDataResponse.model_validate(reading) # Explicit validation for clarity
        if reading.device_id not in grouped_data:
            grouped_data[reading.device_id] = []
        grouped_data[reading.device_id].append(pydantic_reading)
        
    return grouped_data
    
