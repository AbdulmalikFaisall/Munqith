"""Test suite for Sprint 11 analytics modules.

Tests trajectory detection, archetype labeling, and batch analysis.
"""
import pytest
from decimal import Decimal
from datetime import date
from typing import List

# NOTE: These are example test cases that can be run to verify Sprint 11 implementation
# To run: pytest tests/analytics/test_sprint11_analytics.py


class MockSnapshot:
    """Mock snapshot object for testing (not a database model)."""
    
    def __init__(
        self,
        snapshot_date: date,
        monthly_burn: float = None,
        monthly_revenue: float = None,
        runway_months: float = None,
        operating_costs: float = None,
        cash_balance: float = None,
    ):
        self.snapshot_date = snapshot_date
        self.monthly_burn = Decimal(str(monthly_burn)) if monthly_burn is not None else None
        self.monthly_revenue = Decimal(str(monthly_revenue)) if monthly_revenue is not None else None
        self.runway_months = Decimal(str(runway_months)) if runway_months is not None else None
        self.operating_costs = Decimal(str(operating_costs)) if operating_costs is not None else None
        self.cash_balance = Decimal(str(cash_balance)) if cash_balance is not None else None


class TestTrajectoryDetector:
    """Test trajectory detection heuristics."""
    
    def test_runway_collapse_detected(self):
        """Test RUNWAY_COLLAPSE alert when runway declines and falls below 6."""
        from app.analytics.engines.trajectory_detector import TrajectoryDetector
        
        detector = TrajectoryDetector()
        
        # Create snapshots with declining runway: 12 → 9 → 7 → 5
        snapshots = [
            MockSnapshot(date(2026, 1, 1), runway_months=12),
            MockSnapshot(date(2026, 2, 1), runway_months=9),
            MockSnapshot(date(2026, 3, 1), runway_months=7),
            MockSnapshot(date(2026, 4, 1), runway_months=5),
        ]
        
        alerts = detector.detect(snapshots)
        
        assert len(alerts) > 0
        assert any(a["alert_value"] == "RUNWAY_COLLAPSE" for a in alerts)
    
    def test_burn_spike_detected(self):
        """Test BURN_SPIKE alert when burn increases >= 25%."""
        from app.analytics.engines.trajectory_detector import TrajectoryDetector
        
        detector = TrajectoryDetector()
        
        # Create snapshots with burn spike: 40k → 55k (37.5% increase)
        snapshots = [
            MockSnapshot(date(2026, 1, 1), monthly_burn=40000),
            MockSnapshot(date(2026, 2, 1), monthly_burn=55000),
        ]
        
        alerts = detector.detect(snapshots)
        
        assert len(alerts) > 0
        assert any(a["alert_value"] == "BURN_SPIKE" for a in alerts)
    
    def test_revenue_decline_streak_detected(self):
        """Test REVENUE_DECLINE_STREAK alert for 3+ consecutive declines."""
        from app.analytics.engines.trajectory_detector import TrajectoryDetector
        
        detector = TrajectoryDetector()
        
        # Create snapshots with declining revenue: 30k → 25k → 20k → 15k
        snapshots = [
            MockSnapshot(date(2026, 1, 1), monthly_revenue=30000),
            MockSnapshot(date(2026, 2, 1), monthly_revenue=25000),
            MockSnapshot(date(2026, 3, 1), monthly_revenue=20000),
            MockSnapshot(date(2026, 4, 1), monthly_revenue=15000),
        ]
        
        alerts = detector.detect(snapshots)
        
        assert len(alerts) > 0
        assert any(a["alert_value"] == "REVENUE_DECLINE_STREAK" for a in alerts)
    
    def test_no_alerts_when_healthy(self):
        """Test no alerts when trajectory is healthy."""
        from app.analytics.engines.trajectory_detector import TrajectoryDetector
        
        detector = TrajectoryDetector()
        
        # Create snapshots with healthy trajectory
        snapshots = [
            MockSnapshot(date(2026, 1, 1), monthly_burn=-5000, runway_months=20),
            MockSnapshot(date(2026, 2, 1), monthly_burn=-3000, runway_months=22),
        ]
        
        alerts = detector.detect(snapshots)
        
        # Should have no trajectory alerts
        assert all(a["alert_value"] != "RUNWAY_COLLAPSE" for a in alerts)
        assert all(a["alert_value"] != "BURN_SPIKE" for a in alerts)


class TestArchetypeLabeler:
    """Test archetype labeling."""
    
    def test_profitable_grower_label(self):
        """Test PROFITABLE_GROWER label when burn <= 0 and revenue growing."""
        from app.analytics.engines.archetype_labeler import ArchetypeLabeler
        
        labeler = ArchetypeLabeler()
        
        # Create snapshots: improving profitability with growth
        snapshots = [
            MockSnapshot(date(2026, 1, 1), monthly_burn=-2000, monthly_revenue=50000),
            MockSnapshot(date(2026, 2, 1), monthly_burn=-1000, monthly_revenue=55000),
        ]
        
        labels = labeler.label(snapshots)
        
        assert len(labels) > 0
        assert any(l["label_value"] == "PROFITABLE_GROWER" for l in labels)
    
    def test_cash_burner_label(self):
        """Test CASH_BURNER label when burn > 0 and runway < 12 months."""
        from app.analytics.engines.archetype_labeler import ArchetypeLabeler
        
        labeler = ArchetypeLabeler()
        
        snapshots = [
            MockSnapshot(date(2026, 1, 1), monthly_burn=5000, runway_months=8),
        ]
        
        labels = labeler.label(snapshots)
        
        assert len(labels) > 0
        assert any(l["label_value"] == "CASH_BURNER" for l in labels)
    
    def test_runway_critical_label(self):
        """Test RUNWAY_CRITICAL label when runway < 6 months."""
        from app.analytics.engines.archetype_labeler import ArchetypeLabeler
        
        labeler = ArchetypeLabeler()
        
        snapshots = [
            MockSnapshot(date(2026, 1, 1), runway_months=3),
        ]
        
        labels = labeler.label(snapshots)
        
        assert len(labels) > 0
        assert any(l["label_value"] == "RUNWAY_CRITICAL" for l in labels)
    
    def test_unstable_costs_label(self):
        """Test UNSTABLE_COSTS label when 2+ burn spikes detected."""
        from app.analytics.engines.archetype_labeler import ArchetypeLabeler
        
        labeler = ArchetypeLabeler()
        
        # Create snapshots with multiple burn spikes (>= 20% increases)
        snapshots = [
            MockSnapshot(date(2026, 1, 1), monthly_burn=10000),
            MockSnapshot(date(2026, 2, 1), monthly_burn=12500),  # 25% spike
            MockSnapshot(date(2026, 3, 1), monthly_burn=14000),  # 12% increase (not spike)
            MockSnapshot(date(2026, 4, 1), monthly_burn=17000),  # 21% spike
        ]
        
        labels = labeler.label(snapshots)
        
        assert len(labels) > 0
        assert any(l["label_value"] == "UNSTABLE_COSTS" for l in labels)


class TestInsightDeterminism:
    """Test that analytics outputs are deterministic."""
    
    def test_trajectory_detector_determinism(self):
        """Test trajectory detection is deterministic - same input yields same output."""
        from app.analytics.engines.trajectory_detector import TrajectoryDetector
        
        detector = TrajectoryDetector()
        
        snapshots = [
            MockSnapshot(date(2026, 1, 1), monthly_burn=40000),
            MockSnapshot(date(2026, 2, 1), monthly_burn=55000),
        ]
        
        # Run detection twice
        alerts1 = detector.detect(snapshots)
        alerts2 = detector.detect(snapshots)
        
        # Extract alert values for comparison
        vals1 = sorted([a["alert_value"] for a in alerts1])
        vals2 = sorted([a["alert_value"] for a in alerts2])
        
        assert vals1 == vals2, "Trajectory detection should be deterministic"
    
    def test_archetype_labeler_determinism(self):
        """Test archetype labeling is deterministic - same input yields same output."""
        from app.analytics.engines.archetype_labeler import ArchetypeLabeler
        
        labeler = ArchetypeLabeler()
        
        snapshots = [
            MockSnapshot(date(2026, 1, 1), monthly_burn=5000, runway_months=3),
        ]
        
        # Run labeling twice
        labels1 = labeler.label(snapshots)
        labels2 = labeler.label(snapshots)
        
        # Extract label values for comparison
        vals1 = sorted([l["label_value"] for l in labels1])
        vals2 = sorted([l["label_value"] for l in labels2])
        
        assert vals1 == vals2, "Archetype labeling should be deterministic"


# Manual test scenarios from Sprint 11 spec
# These can be modified and run for validation:

def manual_test_scenario_1():
    """
    MANUAL TEST SCENARIO 1: Runway Collapse
    
    Given 4 finalized snapshots with:
        runway: 12 → 9 → 7 → 5
    
    Expect alert: RUNWAY_COLLAPSE
    """
    from app.analytics.engines.trajectory_detector import TrajectoryDetector
    
    detector = TrajectoryDetector()
    snapshots = [
        MockSnapshot(date(2026, 1, 1), runway_months=12),
        MockSnapshot(date(2026, 2, 1), runway_months=9),
        MockSnapshot(date(2026, 3, 1), runway_months=7),
        MockSnapshot(date(2026, 4, 1), runway_months=5),
    ]
    
    alerts = detector.detect(snapshots)
    
    print("\n=== MANUAL TEST: Runway Collapse ===")
    print(f"Input: runway trajectory 12 → 9 → 7 → 5 months")
    print(f"Alerts generated: {len(alerts)}")
    for alert in alerts:
        print(f"  - {alert['alert_value']}: {alert.get('details', '')}")
    
    assert any(a["alert_value"] == "RUNWAY_COLLAPSE" for a in alerts)
    print("✓ RUNWAY_COLLAPSE detected as expected")


def manual_test_scenario_2():
    """
    MANUAL TEST SCENARIO 2: Burn Spike
    
    Given burn increases from 40k → 55k:
    Expect alert: BURN_SPIKE
    """
    from app.analytics.engines.trajectory_detector import TrajectoryDetector
    
    detector = TrajectoryDetector()
    snapshots = [
        MockSnapshot(date(2026, 1, 1), monthly_burn=40000),
        MockSnapshot(date(2026, 2, 1), monthly_burn=55000),
    ]
    
    alerts = detector.detect(snapshots)
    
    print("\n=== MANUAL TEST: Burn Spike ===")
    print(f"Input: burn increases 40k → 55k (37.5% increase)")
    print(f"Alerts generated: {len(alerts)}")
    for alert in alerts:
        print(f"  - {alert['alert_value']}: {alert.get('details', '')}")
    
    assert any(a["alert_value"] == "BURN_SPIKE" for a in alerts)
    print("✓ BURN_SPIKE detected as expected")


def manual_test_scenario_3():
    """
    MANUAL TEST SCENARIO 3: Revenue Decline
    
    Given revenue decreasing 3+ consecutive snapshots (30k → 25k → 20k):
    Expect alert: REVENUE_DECLINE_STREAK
    """
    from app.analytics.engines.trajectory_detector import TrajectoryDetector
    
    detector = TrajectoryDetector()
    snapshots = [
        MockSnapshot(date(2026, 1, 1), monthly_revenue=30000),
        MockSnapshot(date(2026, 2, 1), monthly_revenue=25000),
        MockSnapshot(date(2026, 3, 1), monthly_revenue=20000),
    ]
    
    alerts = detector.detect(snapshots)
    
    print("\n=== MANUAL TEST: Revenue Decline Streak ===")
    print(f"Input: revenue declining 30k → 25k → 20k")
    print(f"Alerts generated: {len(alerts)}")
    for alert in alerts:
        print(f"  - {alert['alert_value']}: {alert.get('details', '')}")
    
    assert any(a["alert_value"] == "REVENUE_DECLINE_STREAK" for a in alerts)
    print("✓ REVENUE_DECLINE_STREAK detected as expected")


if __name__ == "__main__":
    # Run manual tests for verification
    try:
        manual_test_scenario_1()
        manual_test_scenario_2()
        manual_test_scenario_3()
        print("\n✓ All manual test scenarios passed!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import sys
        sys.exit(1)
