"""Signal computation engine for Sprint 3.

Deterministic signal computation from snapshot data.
Pure business logic - no DB calls, no external state.
"""
from typing import List, Optional
from decimal import Decimal

from app.domain.entities.snapshot import Snapshot
from app.domain.entities.signal import Signal
from app.domain.enums.signal_category import SignalCategory


class SignalEngine:
    """
    Signal computation engine.
    
    Responsibilities:
    - Accept finalized snapshot data
    - Generate signals from snapshot fields
    - Return immutable list of Signal objects
    
    Requirements:
    - Deterministic (same snapshot → same signals)
    - No DB calls
    - No external state
    - No mutation of snapshot
    - Pure function behavior
    
    Signals Generated (Sprint 3):
    1. RunwayMonths (FINANCIAL): Cash runway in months
    2. MonthlyBurn (FINANCIAL): Monthly cash burn rate
    3. RunwayRisk (RISK): Risk classification based on runway
    """
    
    @staticmethod
    def compute(snapshot: Snapshot) -> List[Signal]:
        """
        Compute signals from snapshot data.
        
        This is a pure function: same snapshot data → same signals always.
        Does not access database, modify snapshot, or depend on external state.
        
        Args:
            snapshot: Snapshot entity with financial attributes
            
        Returns:
            List of Signal objects generated from snapshot data
            Returns empty list if required financial attributes are missing
            
        Raises:
            TypeError: If snapshot is not a Snapshot instance
        """
        if not isinstance(snapshot, Snapshot):
            raise TypeError(f"snapshot must be Snapshot, got {type(snapshot)}")
        
        signals: List[Signal] = []
        
        # Signal 1: Monthly Burn (FINANCIAL)
        if snapshot.monthly_burn is not None:
            burn_signal = Signal(
                name="MonthlyBurn",
                category=SignalCategory.FINANCIAL,
                value=float(snapshot.monthly_burn),
            )
            signals.append(burn_signal)
        
        # Signal 2: Runway Months (FINANCIAL)
        if snapshot.runway_months is not None:
            runway_signal = Signal(
                name="RunwayMonths",
                category=SignalCategory.FINANCIAL,
                value=float(snapshot.runway_months),
            )
            signals.append(runway_signal)
        
        # Signal 3: Runway Risk (RISK)
        # KSA Context:
        # - runway < 6 months → High Risk (value=3)
        # - 6 ≤ runway ≤ 12 months → Caution (value=2)
        # - runway > 12 months → Healthy (value=1)
        # - runway is None (profitable/break-even) → No risk (value=0)
        risk_value = SignalEngine._compute_runway_risk(snapshot.runway_months)
        risk_signal = Signal(
            name="RunwayRisk",
            category=SignalCategory.RISK,
            value=risk_value,
        )
        signals.append(risk_signal)
        
        return signals
    
    @staticmethod
    def _compute_runway_risk(runway_months: Optional[Decimal]) -> int:
        """
        Compute runway risk classification.
        
        KSA Startup Risk Classification:
        - Profitable/break-even (runway=None) → 0 (No Risk)
        - runway < 6 months → 3 (High Risk)
        - 6 ≤ runway ≤ 12 months → 2 (Caution)
        - runway > 12 months → 1 (Healthy)
        
        Interpretation:
        - Value 3 (High Risk): Company has less than 6 months to find new capital
            or achieve profitability. Critical time frame.
        - Value 2 (Caution): Company has 6-12 months. Should be raising capital
            or moving toward profitability. Moderate concern.
        - Value 1 (Healthy): Company has over 12 months of runway. Stable
            for medium-term planning.
        - Value 0 (No Risk): Company is already profitable or break-even.
            No runway concern.
        
        Args:
            runway_months: Runway in months (Optional Decimal)
            
        Returns:
            Risk value as integer (0, 1, 2, or 3)
        """
        if runway_months is None:
            # Profitable or break-even
            return 0
        
        runway_float = float(runway_months)
        
        if runway_float < 6:
            return 3  # High Risk
        elif runway_float <= 12:
            return 2  # Caution
        else:
            return 1  # Healthy
