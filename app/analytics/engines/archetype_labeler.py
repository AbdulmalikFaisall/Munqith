"""Archetype labeler for deterministic company classification.

Labels companies with risk archetypes based on financial patterns.
Pure analytics engine - no side effects, deterministic output.
"""
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.infrastructure.db.models.snapshot import Snapshot as SnapshotModel


class ArchetypeLabeler:
    """
    Labels companies with deterministic risk archetypes.
    
    Responsibilities:
    - Analyze latest/full snapshot sequence
    - Assign deterministic archetype labels
    - Return labels as dicts (not entities)
    
    Archetypes:
    1. PROFITABLE_GROWER
       - Last burn <= 0 (profitable)
       - Last revenue increasing vs previous
    
    2. CASH_BURNER
       - Last burn > 0
       - Last runway < 12 months
    
    3. RUNWAY_CRITICAL
       - Last runway < 6 months
    
    4. UNSTABLE_COSTS
       - Burn spikes multiple times in last 4 snapshots
    
    Key principle:
    - Deterministic: same input → same output
    - Simple, readable logic
    - No randomness, no external calls
    """
    
    def label(self, snapshots: List[SnapshotModel]) -> List[dict]:
        """
        Label company archetype(s) based on snapshot history.
        
        A company can have multiple labels (e.g., both CASH_BURNER and RUNWAY_CRITICAL).
        
        Args:
            snapshots: List of SnapshotModel objects (should be chronologically sorted)
            
        Returns:
            List of label dicts with keys:
                - label_type: str (RISK_ARCHETYPE)
                - label_value: str (e.g., PROFITABLE_GROWER)
                - scope: str (e.g., LATEST_SNAPSHOT, COMPANY_TRAJECTORY)
                - details: str (optional explanation)
        """
        labels = []
        
        if not snapshots:
            return []
        
        # Get latest snapshot for current state analysis
        latest = snapshots[-1]
        
        # Check each archetype
        if self._is_profitable_grower(snapshots, latest):
            labels.append({
                "label_type": "RISK_ARCHETYPE",
                "label_value": "PROFITABLE_GROWER",
                "scope": "LATEST_SNAPSHOT",
                "details": "Positive cash flow and growing revenue",
            })
        
        if self._is_cash_burner(latest):
            labels.append({
                "label_type": "RISK_ARCHETYPE",
                "label_value": "CASH_BURNER",
                "scope": "LATEST_SNAPSHOT",
                "details": "Negative cash flow with limited runway",
            })
        
        if self._is_runway_critical(latest):
            labels.append({
                "label_type": "RISK_ARCHETYPE",
                "label_value": "RUNWAY_CRITICAL",
                "scope": "LATEST_SNAPSHOT",
                "details": "Operating runway below critical 6-month threshold",
            })
        
        if self._is_unstable_costs(snapshots):
            labels.append({
                "label_type": "RISK_ARCHETYPE",
                "label_value": "UNSTABLE_COSTS",
                "scope": "COMPANY_TRAJECTORY",
                "details": "Operating costs show high volatility and spikes",
            })
        
        return labels
    
    def _is_profitable_grower(
        self, snapshots: List[SnapshotModel], latest: SnapshotModel
    ) -> bool:
        """
        Check if company is PROFITABLE_GROWER.
        
        Conditions:
        - Latest burn <= 0 (profitable or break-even)
        - Latest revenue > previous revenue (or previous is None)
        """
        # Latest must have burn data and be non-positive (profitable)
        if latest.monthly_burn is None or float(latest.monthly_burn) > 0:
            return False
        
        # Check revenue growth
        if len(snapshots) < 2:
            # Only one snapshot - can't verify growth
            return float(latest.monthly_burn) <= 0
        
        prev_snapshot = snapshots[-2]
        
        # If previous has no revenue, can't compare growth
        if prev_snapshot.monthly_revenue is None:
            return False
        
        if latest.monthly_revenue is None:
            return False
        
        latest_revenue = float(latest.monthly_revenue)
        prev_revenue = float(prev_snapshot.monthly_revenue)
        
        # Both conditions for PROFITABLE_GROWER
        return latest_revenue > prev_revenue
    
    def _is_cash_burner(self, latest: SnapshotModel) -> bool:
        """
        Check if company is CASH_BURNER.
        
        Conditions:
        - Latest burn > 0 (negative cash flow)
        - Latest runway < 12 months (or no runway)
        """
        if latest.monthly_burn is None:
            return False
        
        burn_val = float(latest.monthly_burn)
        
        # Must be burning cash
        if burn_val <= 0:
            return False
        
        # Check runway < 12 or missing
        if latest.runway_months is None:
            return True  # Burning cash but no runway = burner
        
        runway_val = float(latest.runway_months)
        return runway_val < 12
    
    def _is_runway_critical(self, latest: SnapshotModel) -> bool:
        """
        Check if company has RUNWAY_CRITICAL status.
        
        Condition:
        - Latest runway < 6 months
        """
        if latest.runway_months is None:
            return False
        
        runway_val = float(latest.runway_months)
        return runway_val < 6
    
    def _is_unstable_costs(self, snapshots: List[SnapshotModel]) -> bool:
        """
        Check if company has UNSTABLE_COSTS archetype.
        
        Condition:
        - Multiple burn spikes detected in last 4 snapshots
        - A spike is defined as: burn increase >= 20% month-over-month
        """
        if len(snapshots) < 3:
            return False
        
        # Analyze last 4 snapshots (or fewer if not available)
        window_size = min(4, len(snapshots))
        window = snapshots[-window_size:]
        
        spike_count = 0
        
        for i in range(1, len(window)):
            prev_burn = window[i - 1].monthly_burn
            curr_burn = window[i].monthly_burn
            
            # Skip if missing data
            if prev_burn is None or curr_burn is None:
                continue
            
            prev_val = float(prev_burn)
            curr_val = float(curr_burn)
            
            # Skip if previous is zero or negative
            if prev_val <= 0:
                continue
            
            # Check if spike (>= 20% increase)
            increase_pct = ((curr_val - prev_val) / prev_val) * 100
            if increase_pct >= 20:
                spike_count += 1
        
        # Unstable if 2+ spikes in recent history
        return spike_count >= 2
