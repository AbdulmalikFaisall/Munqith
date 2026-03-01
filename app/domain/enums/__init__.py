"""Domain enums - framework-independent enumerations."""

from app.domain.enums.stage import Stage
from app.domain.enums.snapshot_status import SnapshotStatus
from app.domain.enums.signal_category import SignalCategory
from app.domain.enums.user_role import UserRole

__all__ = ["Stage", "SnapshotStatus", "SignalCategory", "UserRole"]
