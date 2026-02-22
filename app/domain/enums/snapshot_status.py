"""
Snapshot status enumeration.

Represents the lifecycle state of a snapshot.
Must match exactly with database snapshot.status constraint.
"""
from enum import Enum


class SnapshotStatus(str, Enum):
    """Snapshot lifecycle status - string-based enum."""
    
    DRAFT = "DRAFT"
    FINALIZED = "FINALIZED"
    INVALIDATED = "INVALIDATED"

    def __str__(self) -> str:
        return self.value
