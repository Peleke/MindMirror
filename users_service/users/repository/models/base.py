from users.repository.database import Base as DatabaseBase


class Base(DatabaseBase):
    """Base class for all models, inheriting from the central DatabaseBase.
    This class itself is not mapped to a database table.
    """

    __abstract__ = True  # Tell SQLAlchemy this is not a mapped table
