# tessyfarm_smartloop/backend_api/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Tessyfarm SmartLoop - API"
    API_V1_STR: str = "/api/v1"

    # Database settings (will be used in next step)
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: str | None = None # Assembled URL

    # MQTT Settings
    MQTT_BROKER_HOST: str = "mqtt_broker"
    MQTT_BROKER_PORT: int = 1883

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def ASSEMBLED_DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

@lru_cache() # Cache the settings object
def get_settings() -> Settings:
    # Load .env file from the project root if it exists
    # This helps when running locally without Docker using backend_api as CWD
    # Docker compose already loads it via env_file directive
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
    if os.path.exists(dotenv_path):
        return Settings(_env_file=dotenv_path)
    return Settings()

settings = get_settings()
