# tessyfarm_smartloop/backend_api/app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .core.config import settings
from .apis.version1 import api_router as api_v1_router
# from .core import db # Will uncomment when db connection is set up

# In-memory store for simple startup/shutdown events, if needed
# This is a simple example; for real applications, use proper logging and setup/teardown logic.
app_lifespan_events = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app_lifespan_events.append("Application startup: Connecting to resources...")
    print("Application startup: Connecting to resources...")
    # Simulate connecting to DB or other services
    # await db.connect_to_database() # Example for database connection
    yield
    # Shutdown
    print("Application shutdown: Cleaning up resources...")
    # await db.close_database_connection() # Example for database disconnection
    app_lifespan_events.append("Application shutdown: Cleaning up resources...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan # Use the lifespan context manager
)

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy", "message": "Tessyfarm API is running!"}

# Include the API version 1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# You can add other global middleware or event handlers here if needed
