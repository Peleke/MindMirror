from sqlalchemy.orm import declarative_base

# A common base for all SQLAlchemy ORM models in the application
Base = declarative_base()

Base.metadata.schema = "journal"
