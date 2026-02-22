"""
Domain-specific exceptions.

These exceptions represent business logic violations in the domain layer.
They are framework-independent and deterministic.
"""


class DomainException(Exception):
    """Base exception for all domain logic violations."""
    pass


class InvalidSnapshotTransition(DomainException):
    """
    Raised when attempting an invalid snapshot status transition.
    
    Example:
        - FINALIZED → DRAFT (not allowed)
        - FINALIZED → FINALIZED (cannot finalize twice)
        - INVALIDATED → FINALIZED (cannot restore)
    """
    
    def __init__(self, current_status: str, attempted_status: str, reason: str = ""):
        msg = f"Invalid snapshot transition: {current_status} → {attempted_status}"
        if reason:
            msg += f". {reason}"
        super().__init__(msg)
        self.current_status = current_status
        self.attempted_status = attempted_status


class ImmutableSnapshotError(DomainException):
    """
    Raised when attempting to modify a finalized (immutable) snapshot.
    
    Example:
        - Updating financial data after finalization
        - Changing stage after finalization
        - Modifying status directly
    """
    
    def __init__(self, snapshot_id: str, attempted_action: str):
        msg = f"Cannot {attempted_action}: snapshot {snapshot_id} is immutable (already finalized)"
        super().__init__(msg)
        self.snapshot_id = snapshot_id
        self.attempted_action = attempted_action


class InvalidateDraftSnapshotError(DomainException):
    """
    Raised when attempting to invalidate a DRAFT snapshot.
    
    Only FINALIZED snapshots can be invalidated.
    """
    
    def __init__(self, snapshot_id: str, current_status: str):
        msg = f"Cannot invalidate snapshot {snapshot_id}: must be FINALIZED, but is {current_status}"
        super().__init__(msg)
        self.snapshot_id = snapshot_id
        self.current_status = current_status


class FinalizeDraftOnlyError(DomainException):
    """
    Raised when attempting to finalize a snapshot that isn't in DRAFT status.
    """
    
    def __init__(self, snapshot_id: str, current_status: str):
        msg = f"Cannot finalize snapshot {snapshot_id}: only DRAFT snapshots can be finalized, but is {current_status}"
        super().__init__(msg)
        self.snapshot_id = snapshot_id
        self.current_status = current_status
