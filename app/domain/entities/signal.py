"""Signal domain entity for Sprint 3 Signal Engine."""
from typing import Optional
from datetime import datetime
from uuid import UUID
import uuid

from app.domain.enums.signal_category import SignalCategory


class Signal:
    """
    Signal entity - represents a structured interpretation of data.
    
    A Signal is:
    - Generated from snapshot financial attributes
    - NOT a duplicate of raw financial data
    - A computed or derived metric with semantic meaning
    - Immutable once created (used for computation only)
    
    Signals are the input to the Rule Engine (Sprint 4).
    
    Examples:
    - RunwayMonths: Months of cash runway (FINANCIAL)
    - MonthlyBurn: Monthly cash burn rate (FINANCIAL)
    - RunwayRisk: Risk classification based on runway (RISK)
    
    Pure data structure - no business logic.
    """
    
    def __init__(
        self,
        name: str,
        category: SignalCategory,
        value: float,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
    ):
        """
        Initialize a Signal entity.
        
        Args:
            name: Human-readable signal name (e.g., "RunwayMonths")
            category: Category of this signal (SignalCategory enum)
            value: Numeric value of the signal (float)
            id: Unique identifier (UUID, optional - auto-generated if not provided)
            created_at: Timestamp of creation (optional - auto-generated if not provided)
            
        Raises:
            ValueError: If name is empty or value type is invalid
            TypeError: If category is not SignalCategory
        """
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Signal name must be a non-empty string")
        
        if not isinstance(category, SignalCategory):
            raise TypeError(f"category must be SignalCategory, got {type(category)}")
        
        if not isinstance(value, (int, float)):
            raise TypeError(f"value must be numeric (int or float), got {type(value)}")
        
        self.id = id or uuid.uuid4()
        self.name = name.strip()
        self.category = category
        self.value = float(value)
        self.created_at = created_at or datetime.utcnow()
    
    # ==================== Utilities ====================
    
    def __repr__(self) -> str:
        return (
            f"Signal(name={self.name!r}, category={self.category.value}, "
            f"value={self.value}, id={self.id})"
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Signal):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
