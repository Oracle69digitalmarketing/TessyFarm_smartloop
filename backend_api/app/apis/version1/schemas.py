# tessyfarm_smartloop/backend_api/app/apis/version1/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any # Ensure List is imported

# ... (Existing SensorDataCreate, SensorDataResponse, YieldPredictionResponse) ...

# --- Farm Schemas ---
class FarmBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, examples=["Green Acres Farm"])
    location_text: Optional[str] = Field(None, max_length=255, examples=["123 Farm Road, Rural Town"])
    total_area_hectares: Optional[float] = Field(None, gt=0, examples=[50.5])

class FarmCreate(FarmBase):
    pass

class FarmUpdate(FarmBase):
    name: Optional[str] = Field(None, min_length=3, max_length=100) # All fields optional for update

class FarmResponse(FarmBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Field Schemas ---
class FieldBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["North Field 1"])
    area_hectares: Optional[float] = Field(None, gt=0, examples=[10.2])
    soil_type: Optional[str] = Field(None, max_length=50, examples=["Loamy Clay"])

class FieldCreate(FieldBase):
    farm_id: int # Must be provided when creating a field

class FieldUpdate(FieldBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100) # All fields optional
    farm_id: Optional[int] = None # Allow changing farm? Or disallow? For now, allow.

class FieldResponse(FieldBase):
    id: int
    farm_id: int
    created_at: datetime
    updated_at: datetime
    # Optionally, include basic farm info here later if needed
    # farm: Optional[FarmResponse] = None 

    class Config:
        from_attributes = True

# --- CropCycle Schemas ---
class CropCycleBase(BaseModel):
    crop_type: str = Field(..., max_length=100, examples=["Maize Zea mays GDD120"])
    planting_date: datetime
    expected_harvest_date: Optional[datetime] = None
    actual_harvest_date: Optional[datetime] = None
    actual_yield_tonnes: Optional[float] = Field(None, ge=0) # Must be non-negative
    notes: Optional[str] = Field(None, examples=["Late planting due to rain."])

class CropCycleCreate(CropCycleBase):
    field_id: int # Must be provided

class CropCycleUpdate(CropCycleBase):
    crop_type: Optional[str] = Field(None, max_length=100) # All fields optional
    planting_date: Optional[datetime] = None
    # Allow updating field_id? Probably not common, but possible.
    # field_id: Optional[int] = None 

class CropCycleResponse(CropCycleBase):
    id: int
    field_id: int
    created_at: datetime
    updated_at: datetime
    # Optionally include basic field info
    # field: Optional[FieldResponse] = None

    class Config:
        from_attributes = True

# Schema to list fields within a farm response
class FarmResponseWithFields(FarmResponse):
    fields: List[FieldResponse] = []

# Schema to list crop cycles within a field response
class FieldResponseWithCropCycles(FieldResponse):
    crop_cycles: List[CropCycleResponse] = []
