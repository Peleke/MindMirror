from sqlalchemy.orm import declarative_base

# A common base for all SQLAlchemy ORM models in the journal service
Base = declarative_base()

# Set the schema for journal service models
Base.metadata.schema = "journal"
