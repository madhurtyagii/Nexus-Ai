"""Nexus AI - Database Configuration.

This module sets up the SQLAlchemy ORM infrastructure, including the 
engine, session local factory, and the Base class for all models.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine with connection timeout and pooling
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "connect_timeout": 10,  # 10 seconds timeout
        "application_name": "nexus_ai_api"
    }
)


# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


def get_db():
    """Dependency for providing a database session to FastAPI routes.
    
    Yields:
        db (Session): A SQLAlchemy database session that is automatically 
            closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
