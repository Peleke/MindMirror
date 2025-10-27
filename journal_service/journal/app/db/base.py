"""SQLAlchemy declarative base for journal service."""
from sqlalchemy.orm import declarative_base

# Base class for models
Base = declarative_base()

# Set the schema for all tables
Base.metadata.schema = "journal"
