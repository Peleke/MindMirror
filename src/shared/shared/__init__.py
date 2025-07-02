"""
Shared package for MindMirror services.

This package contains common components used across multiple services
including authentication, data models, and HTTP clients.
"""

from .auth import CurrentUser, get_current_user, RequireRolePermission
from .data_models import UserRole

__all__ = [
    "CurrentUser",
    "get_current_user", 
    "RequireRolePermission",
    "UserRole",
] 