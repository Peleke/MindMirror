from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from habits.app.config import get_settings


class Base(DeclarativeBase):
    # Use configurable schema from settings (defaults to "habits")
    metadata = MetaData(schema=get_settings().database_schema)

