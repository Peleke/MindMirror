from sqlalchemy.ext.asyncio import AsyncAttrs

from practices.repository.database import Base as DatabaseBase


class Base(AsyncAttrs, DatabaseBase):
    """Base class for all models, inheriting from the central DatabaseBase.
    This class itself is not mapped to a database table.
    """

    __abstract__ = True  # Tell SQLAlchemy this is not a mapped table

    pass


# The schema is now set on the Base in database.py,
# but models still need to know which Base to use if they don't specify a table directly.
# However, SQLAlchemy recommends setting the schema on the metadata of a single Base instance.
# Let's ensure our models use the correct Base, and schema is set in database.py on THAT Base.
# This line might be redundant if DatabaseBase.metadata already has the schema.
# For safety, we can remove it here and ensure it's set in database.py only.
# Base.metadata.schema = "practices" # This might now be redundant or cause issues.
