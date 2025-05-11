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

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    # ...
    """
    # url = config.get_main_option("sqlalchemy.url") # Original line
    url = settings.ASSEMBLED_DATABASE_URL # Use Pydantic settings
    context.configure(
        url=url, # Use the URL from settings
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    # ...

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    # ...
    """
    # connectable = engine_from_config( # Original lines
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )

    # Create a new engine instance using your settings
    from sqlalchemy import create_engine
    connectable = create_engine(settings.ASSEMBLED_DATABASE_URL) # Use Pydantic settings

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        # ...


