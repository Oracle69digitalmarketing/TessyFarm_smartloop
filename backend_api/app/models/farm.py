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
