# tessyfarm_smartloop/backend_api/app/apis/version1/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any

class SensorDataCreate(BaseModel):
    device_id: str = Field(..., examples=["device_soil_A1"])
    temperature: Optional[float] = Field(None, examples=[25.5])
    humidity: Optional[float] = Field(None, examples=[60.2])
    soil_moisture: Optional[float] = Field(None, examples=[0.45])
    # Add other sensor types as needed
    custom_data: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SensorDataResponse(SensorDataCreate):
    id: int # Assuming an ID from the database later
    received_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        # This was for Pydantic v1, for v2 orm_mode is replaced by from_attributes
        # orm_mode = True
        from_attributes = True # For Pydantic V2, enables ORM mode like behavior

# --- Define Pydantic Schemas for Predictions ---
# In backend_api/app/apis/version1/schemas.py:
class YieldPredictionResponse(BaseModel):
    id: int
    crop_cycle_id: int
    model_version: str
    prediction_date: datetime
    predicted_yield_tonnes: float
    confidence_score: Optional[float] = None
    input_features_summary: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
