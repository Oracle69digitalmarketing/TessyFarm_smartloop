# tessyfarm_smartloop/iot_listener/listener.py
import os
import json
import logging
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from pydantic import BaseModel, Field, ValidationError # For data validation from MQTT
from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func

# --- Configuration ---
# Similar to backend_api/app/core/config.py for Pydantic settings
class ListenerSettings(BaseSettings):
    PROJECT_NAME: str = "Tessyfarm IoT Listener"

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"

    MQTT_BROKER_HOST: str
    MQTT_BROKER_PORT: int
    MQTT_CLIENT_ID: str = "tessyfarm_iot_listener"
    MQTT_TOPIC_PREFIX: str = "tessyfarm/data/" # e.g., tessyfarm/data/device_id

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def ASSEMBLED_DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

# It's important that the .env file path is correct when listener.py runs.
# Docker Compose will pass environment variables directly from the .env file in the project root.
settings = ListenerSettings()

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Database Setup (similar to backend_api/app/core/db.py and models/farm.py) ---
SQLALCHEMY_DATABASE_URL = settings.ASSEMBLED_DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Model (identical to backend_api/app/models/farm.py SensorReading) ---
class SensorReadingDB(Base): # Renamed to avoid potential import confusion if ever in same namespace
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    soil_moisture = Column(Float, nullable=True)
    custom_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    received_at = Column(DateTime, default=func.now())

# Create tables if they don't exist (Alembic in backend_api handles this, but good for standalone robustness)
# In a production setup, migrations should be the sole source of truth for schema.
# This line is mostly for ensuring the table exists if the listener starts before migrations run or in isolated tests.
# However, it's generally better to rely on migrations run by the backend service.
# Base.metadata.create_all(bind=engine) # Consider if this is truly needed or if we rely on backend migrations

# --- Pydantic Model for incoming MQTT Data (similar to backend_api schemas) ---
class MQTTSensorData(BaseModel):
    # device_id will be extracted from MQTT topic
    temperature: Optional[float] = Field(None, examples=[25.5])
    humidity: Optional[float] = Field(None, examples=[60.2])
    soil_moisture: Optional[float] = Field(None, examples=[0.45])
    custom_data: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) # Expect ISO format string, Pydantic converts


# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Successfully connected to MQTT Broker: {settings.MQTT_BROKER_HOST}")
        subscription_topic = f"{settings.MQTT_TOPIC_PREFIX}#"
        client.subscribe(subscription_topic)
        logger.info(f"Subscribed to topic: {subscription_topic}")
    else:
        logger.error(f"Failed to connect to MQTT Broker, return code {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload_str = msg.payload.decode()
    logger.info(f"Received message on topic {topic}: {payload_str}")

    try:
        # Extract device_id from topic, assuming topic is like "tessyfarm/data/device_id_actual"
        if not topic.startswith(settings.MQTT_TOPIC_PREFIX):
            logger.warning(f"Message topic '{topic}' does not match prefix '{settings.MQTT_TOPIC_PREFIX}'. Skipping.")
            return
        
        device_id_str = topic[len(settings.MQTT_TOPIC_PREFIX):]
        if not device_id_str:
            logger.warning(f"Could not extract device_id from topic '{topic}'. Skipping.")
            return

        data_dict = json.loads(payload_str)
        
        # Validate data using Pydantic model
        try:
            mqtt_data = MQTTSensorData(**data_dict)
        except ValidationError as e:
            logger.error(f"Data validation error for device {device_id_str} on topic {topic}: {e}. Payload: {payload_str}")
            return

        # Store in database
        db = SessionLocal()
        try:
            db_sensor_reading = SensorReadingDB(
                device_id=device_id_str,
                temperature=mqtt_data.temperature,
                humidity=mqtt_data.humidity,
                soil_moisture=mqtt_data.soil_moisture,
                custom_data=mqtt_data.custom_data,
                timestamp=mqtt_data.timestamp
            )
            db.add(db_sensor_reading)
            db.commit()
            logger.info(f"Successfully stored data for device {device_id_str} from topic {topic} to database.")
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while storing data for device {device_id_str} from topic {topic}: {e}")
        finally:
            db.close()

    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from topic {topic}: {payload_str}")
    except Exception as e:
        logger.error(f"An unexpected error occurred in on_message for topic {topic}: {e}")

def on_disconnect(client, userdata, rc):
    logger.warning(f"Disconnected from MQTT Broker with result code {rc}. Attempting to reconnect...")
    # Reconnection logic is often handled by client.loop_forever() or manually if needed.

# --- Main Execution ---
if __name__ == "__main__":
    logger.info(f"Starting {settings.PROJECT_NAME}...")
    logger.info(f"Attempting to connect to MQTT Broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=settings.MQTT_CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    # Optional: Set username and password if your MQTT broker requires authentication
    # mqtt_client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    
    retry_interval = 5 # seconds
    while True:
        try:
            mqtt_client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
            mqtt_client.loop_forever() # Blocks until client disconnects
        except ConnectionRefusedError:
            logger.error(f"Connection refused by MQTT broker. Retrying in {retry_interval} seconds...")
        except socket.gaierror: # Host not found
             logger.error(f"MQTT broker host not found ({settings.MQTT_BROKER_HOST}). Retrying in {retry_interval} seconds...")
        except Exception as e:
            logger.error(f"An MQTT connection error occurred: {e}. Retrying in {retry_interval} seconds...")
        
        # If loop_forever() exits (e.g., due to disconnect not handled by paho-mqtt auto-reconnect)
        logger.info(f"Loop exited. Attempting to reconnect in {retry_interval} seconds...")
        time.sleep(retry_interval)

