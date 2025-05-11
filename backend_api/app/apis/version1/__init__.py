# tessyfarm_smartloop/backend_api/app/apis/version1/__init__.py
from fastapi import APIRouter
from .endpoints import farm_data

api_router = APIRouter()
api_router.include_router(farm_data.router, prefix="/farm-data", tags=["Farm Data"])

# Add other routers here, e.g., for automation, users, etc.
# from .endpoints import automation
# api_router.include_router(automation.router, prefix="/automation", tags=["Automation"])
