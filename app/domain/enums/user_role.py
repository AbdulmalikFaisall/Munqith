"""User role enumeration.

Defines available user roles for RBAC.
Pure domain enum - no framework dependencies.
"""
from enum import Enum


class UserRole(Enum):
    """
    User role enumeration.
    
    Roles:
    - ANALYST: Read-only access, cannot modify or invalidate
    - ADMIN: Full access including invalidation with reason
    """
    
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"
