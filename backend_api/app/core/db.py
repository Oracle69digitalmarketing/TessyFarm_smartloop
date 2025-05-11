# tessyfarm_smartloop/backend_api/app/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # updated import
from .config import settings

# Construct the database URL
# DATABASE_URL should now be correctly assembled by Pydantic settings
SQLALCHEMY_DATABASE_URL = settings.ASSEMBLED_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() # This will be used by our models

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

