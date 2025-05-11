# tessyfarm_smartloop/backend_api/app/models/farm.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func # For server-side default timestamps
from ..core.db import Base # Import Base from our db core module
from datetime import datetime

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    soil_moisture = Column(Float, nullable=True)
    
    custom_data = Column(JSON, nullable=True) # For any other dynamic sensor data
    
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow) # Timestamp from the device or when data was generated
    received_at = Column(DateTime, default=func.now()) # Timestamp when data was received by server (db default)

    def __repr__(self):
        return f"<SensorReading(id={self.id}, device_id='{self.device_id}', timestamp='{self.timestamp}')>"

# tessyfarm_smartloop/backend_api/app/models/farm.py
# ... (existing SensorReading model and imports) ...
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB # For storing structured JSON

# ... (SensorReading class definition) ...

class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    location_text = Column(String, nullable=True) # Simple text for now
    total_area_hectares = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    fields = relationship("Field", back_populates="farm")

class Field(Base):
    __tablename__ = "fields"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    area_hectares = Column(Float, nullable=True)
    soil_type = Column(String, nullable=True) # E.g., "Loamy", "Clay", "Sandy"
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    farm = relationship("Farm", back_populates="fields")
    crop_cycles = relationship("CropCycle", back_populates="field")

class CropCycle(Base):
    __tablename__ = "crop_cycles"
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    crop_type = Column(String, index=True, nullable=False) # E.g., "Maize GDD120", "Tomato Roma"
    planting_date = Column(DateTime, nullable=False)
    expected_harvest_date = Column(DateTime, nullable=True) # Initial estimate
    actual_harvest_date = Column(DateTime, nullable=True) # For historical data
    actual_yield_tonnes = Column(Float, nullable=True) # TARGET VARIABLE for training
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    field = relationship("Field", back_populates="crop_cycles")

class YieldPrediction(Base):
    __tablename__ = "yield_predictions"
    id = Column(Integer, primary_key=True, index=True)
    crop_cycle_id = Column(Integer, ForeignKey("crop_cycles.id"), nullable=False, unique=True) # One prediction per cycle
    model_version = Column(String, nullable=False)
    prediction_date = Column(DateTime, default=func.now())
    predicted_yield_tonnes = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=True) # Optional
    input_features_summary = Column(JSONB, nullable=True) # Store a summary of features used for this prediction
    
    crop_cycle = relationship("CropCycle") # No back_populates needed if one-way from prediction
