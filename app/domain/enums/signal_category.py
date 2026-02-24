"""Signal category enumeration for Sprint 3 Signal Engine."""
from enum import Enum


class SignalCategory(str, Enum):
    """
    Enumeration of signal categories.
    
    Signals are classified by type:
    - FINANCIAL: Calculated from financial attributes (burn, runway, etc.)
    - GROWTH: Revenue growth, user growth, market expansion indicators
    - RISK: Financial or strategic risk indicators
    - OPERATIONAL: Operational metrics (team size, efficiency, etc.)
    - MARKET: Market position, competition, market size
    
    String-based enum: inherits from both str and Enum.
    Benefits:
    - JSON-serializable directly
    - Can be used as dict keys
    - Comparable and hashable
    - Compatible with database tet matchesase values exactly
    """
    
    FINANCIAL = "FINANCIAL"
    GROWTH = "GROWTH"
    RISK = "RISK"
    OPERATIONAL = "OPERATIONAL"
    MARKET = "MARKET"
