"""Trajectory detector for deterministic trend analysis.

Analyzes snapshot sequences to detect failure trajectories.
Pure analytics engine - no side effects, deterministic output.
"""
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.infrastructure.db.models.snapshot import Snapshot as SnapshotModel


class TrajectoryDetector:
    """
    Detects failure trajectories from snapshot history.
    
    Responsibilities:
    - Analyze snapshot sequences
    - Identify deterministic trajectory patterns
    - Return alerts as dicts (not entities)
    
    Detections:
    1. RUNWAY_COLLAPSE: Steady runway decline + final < 6 months
    2. BURN_SPIKE: Monthly burn increase >= 25%
    3. REVENUE_DECLINE_STREAK: Revenue decreasing 3+ consecutive snapshots
    
    Key principle:
    - Deterministic: same input → same output
    - No randomness, no external calls
    - Each detection is independent
    """
    
    def detect(self, snapshots: List[SnapshotModel]) -> List[dict]:
        """
        Analyze snapshot sequence and detect trajectory alerts.
        
        Args:
            snapshots: List of SnapshotModel objects (should be chronologically sorted)
            
        Returns:
            List of alert dicts with keys:
                - alert_type: str (e.g., RUNWAY_COLLAPSE)
                - alert_value: str (e.g., RUNWAY_COLLAPSE)
                - details: str (optional reason/details)
                - confidence: str (HIGH, MEDIUM, LOW)
        """
        alerts = []
        
        if len(snapshots) < 2:
            return []  # Not enough data for trajectory analysis
        
        # Detection 1: Runway Collapse
        runway_collapse = self._detect_runway_collapse(snapshots)
        if runway_collapse:
            alerts.append(runway_collapse)
        
        # Detection 2: Burn Spike
        burn_spike = self._detect_burn_spike(snapshots)
        if burn_spike:
            alerts.append(burn_spike)
        
        # Detection 3: Revenue Decline Streak
        revenue_decline = self._detect_revenue_decline_streak(snapshots)
        if revenue_decline:
            alerts.append(revenue_decline)
        
        return alerts
    
    def _detect_runway_collapse(
        self, snapshots: List[SnapshotModel]
    ) -> Optional[dict]:
        """
        Detect RUNWAY_COLLAPSE alert.
        
        Condition:
        - Last 3 snapshots have runway data
        - Runway decreasing each month
        - Last runway < 6 months
        
        Returns:
            Alert dict or None if condition not met
        """
        if len(snapshots) < 3:
            return None
        
        # Get last 3 snapshots
        last_3 = snapshots[-3:]
        
        # Check all have runway data
        runways = [s.runway_months for s in last_3]
        if any(r is None for r in runways):
            return None
        
        # Convert to float for comparison
        runway_values = [float(r) for r in runways]
        
        # Check decreasing trend
        is_decreasing = (
            runway_values[0] > runway_values[1]
            and runway_values[1] > runway_values[2]
        )
        
        # Check final < 6 months
        is_critical = runway_values[2] < 6
        
        if is_decreasing and is_critical:
            return {
                "alert_type": "TRAJECTORY_ALERT",
                "alert_value": "RUNWAY_COLLAPSE",
                "details": f"Runway declined from {runway_values[0]:.1f} to {runway_values[2]:.1f} months and is below 6-month threshold",
                "confidence": "HIGH",
            }
        
        return None
    
    def _detect_burn_spike(
        self, snapshots: List[SnapshotModel]
    ) -> Optional[dict]:
        """
        Detect BURN_SPIKE alert.
        
        Condition:
        - Last 2 snapshots have burn data
        - Current burn >= previous burn * 1.25 (25% increase)
        
        Returns:
            Alert dict or None if condition not met
        """
        if len(snapshots) < 2:
            return None
        
        # Get last 2 snapshots
        prev_snapshot = snapshots[-2]
        curr_snapshot = snapshots[-1]
        
        prev_burn = prev_snapshot.monthly_burn
        curr_burn = curr_snapshot.monthly_burn
        
        # Both must have burn data
        if prev_burn is None or curr_burn is None:
            return None
        
        # Convert to float for comparison
        prev_burn_val = float(prev_burn)
        curr_burn_val = float(curr_burn)
        
        # Skip zero or negative burns (data quality issue)
        if prev_burn_val <= 0:
            return None
        
        # Check if spike >= 25%
        spike_threshold = prev_burn_val * 1.25
        
        if curr_burn_val >= spike_threshold:
            increase_pct = ((curr_burn_val - prev_burn_val) / prev_burn_val) * 100
            return {
                "alert_type": "TRAJECTORY_ALERT",
                "alert_value": "BURN_SPIKE",
                "details": f"Monthly burn increased {increase_pct:.1f}% from {prev_burn_val:,.0f} to {curr_burn_val:,.0f} SAR",
                "confidence": "HIGH",
            }
        
        return None
    
    def _detect_revenue_decline_streak(
        self, snapshots: List[SnapshotModel]
    ) -> Optional[dict]:
        """
        Detect REVENUE_DECLINE_STREAK alert.
        
        Condition:
        - Revenue decreasing in 3+ consecutive snapshots
        
        Returns:
            Alert dict or None if condition not met
        """
        if len(snapshots) < 3:
            return None
        
        # Extract revenues
        revenues = [s.monthly_revenue for s in snapshots]
        
        # Find consecutive decline streaks
        max_streak = 0
        current_streak = 1
        
        for i in range(1, len(revenues)):
            prev_rev = revenues[i - 1]
            curr_rev = revenues[i]
            
            # Skip if either is None
            if prev_rev is None or curr_rev is None:
                current_streak = 1
                continue
            
            # Check if declining
            if float(curr_rev) < float(prev_rev):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        # Alert only if 3+ consecutive declines
        if max_streak >= 3:
            return {
                "alert_type": "TRAJECTORY_ALERT",
                "alert_value": "REVENUE_DECLINE_STREAK",
                "details": f"Revenue declined for {max_streak} consecutive snapshots",
                "confidence": "HIGH",
            }
        
        return None
