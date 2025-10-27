from pydantic import BaseModel


class UserRole(BaseModel):
    """Represents a single role assignment for a user."""

    role: str
    domain: str
