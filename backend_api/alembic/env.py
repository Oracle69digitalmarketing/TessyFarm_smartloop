# tessyfarm_smartloop/backend_api/alembic/env.py
# ... other imports
from logging.config import fileConfig
import os
import sys

# Add the app directory to the Python path
# This allows Alembic to find your app's modules (models, config)
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..')))
# Now you can import from your app
from app.core.db import Base  # Your SQLAlchemy Base
from app.core.config import settings # Your application settings

# ... rest of the file

