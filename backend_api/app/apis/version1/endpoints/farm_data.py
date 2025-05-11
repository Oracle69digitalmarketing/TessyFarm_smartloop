# tessyfarm_smartloop/backend_api/app/apis/version1/endpoints/farm_data.py
from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict
from datetime import datetime

from ..schemas import SensorDataCreate, SensorDataResponse # Use .. to go up one level

router = APIRouter()

# In-memory store for now (will be replaced by database interaction)
# This is NOT suitable for production or multiple workers.
DUMMY_SENSOR_DATA_STORE: Dict[str, List[Dict]] = {}
DUMMY_DB_ID_COUNTER = 1

@router.post("/sensor-data/", response_model=SensorDataResponse, status_code=201)
async def receive_sensor_data(data: SensorDataCreate = Body(...)):
    """
    Receive sensor data from IoT devices or listeners.
    (Currently stores in-memory - for demo only)
    """
    global DUMMY_DB_ID_COUNTER
    print(f"Received sensor data for device {data.device_id}: {data.model_dump()}")

    if data.device_id not in DUMMY_SENSOR_DATA_STORE:
        DUMMY_SENSOR_DATA_STORE[data.device_id] = []

    # Simulate database entry
    db_entry = data.model_dump()
    db_entry["id"] = DUMMY_DB_ID_COUNTER
    db_entry["received_at"] = datetime.utcnow()
    DUMMY_SENSOR_DATA_STORE[data.device_id].append(db_entry)
    DUMMY_DB_ID_COUNTER +=1

    return SensorDataResponse(**db_entry)


@router.get("/sensor-data/{device_id}", response_model=List[SensorDataResponse])
async def get_sensor_data_for_device(device_id: str):
    """
    Retrieve all sensor data for a specific device.
    (Currently retrieves from in-memory store - for demo only)
    """
    if device_id not in DUMMY_SENSOR_DATA_STORE:
        raise HTTPException(status_code=404, detail=f"No data found for device_id: {device_id}")
    
    # Convert stored dicts to SensorDataResponse model
    # This is a bit manual here due to the dummy store. ORM would handle this.
    response_data = []
    for entry in DUMMY_SENSOR_DATA_STORE[device_id]:
        try:
            response_data.append(SensorDataResponse(**entry))
        except Exception as e: # Catch if dict doesn't match model perfectly
            print(f"Error converting entry for {device_id}: {entry}, error: {e}")
            # Skip faulty entries for now in this dummy setup
            pass 
            
    return response_data

@router.get("/sensor-data/", response_model=Dict[str, List[SensorDataResponse]])
async def get_all_sensor_data():
    """
    Retrieve all sensor data grouped by device ID.
    (Currently retrieves from in-memory store - for demo only)
    """
    # Similar conversion as above for all devices
    all_data_response = {}
    for device_id, entries in DUMMY_SENSOR_DATA_STORE.items():
        device_response_data = []
        for entry in entries:
            try:
                device_response_data.append(SensorDataResponse(**entry))
            except Exception:
                pass # Skip faulty entries
        all_data_response[device_id] = device_response_data
    return all_data_response


