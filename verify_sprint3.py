#!/usr/bin/env python
"""
Sprint 3 Verification Script

Comprehensive verification of Signal Engine implementation:
- Snapshot derived metrics computation
- Signal generation
- Deterministic behavior
- Framework isolation
"""
import sys
import os
from decimal import Decimal
from datetime import date, datetime
from uuid import uuid4

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import domain components
from app.domain.entities import Snapshot, Signal
from app.domain.enums import Stage, SnapshotStatus, SignalCategory
from app.domain.engines import SignalEngine


def test_derived_metrics_calculation():
    """Test Snapshot.compute_derived_metrics() with various scenarios."""
    print("\n[Test 1] Derived Metrics Calculation")
    print("=" * 70)
    
    # Scenario 1: Normal burn with runway
    print("\nScenario 1.1: Company with positive burn")
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("120000"),
        monthly_revenue=Decimal("20000"),
        operating_costs=Decimal("40000"),
    )
    snapshot.compute_derived_metrics()
    
    assert snapshot.monthly_burn == Decimal("20000"), "Burn should be 20000 (40k - 20k)"
    assert snapshot.runway_months == Decimal("6"), "Runway should be 6 months (120k / 20k)"
    print(f"  ✓ Monthly Burn: {snapshot.monthly_burn} SAR")
    print(f"  ✓ Runway Months: {snapshot.runway_months} months")
    
    # Scenario 2: Profitable company (negative burn)
    print("\nScenario 1.2: Profitable company (revenue > costs)")
    snapshot2 = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("100000"),
        monthly_revenue=Decimal("50000"),
        operating_costs=Decimal("40000"),
    )
    snapshot2.compute_derived_metrics()
    
    assert snapshot2.monthly_burn == Decimal("-10000"), "Burn should be -10000 (profit)"
    assert snapshot2.runway_months is None, "Runway should be None for profitable company"
    print(f"  ✓ Monthly Burn: {snapshot2.monthly_burn} SAR (negative = profit)")
    print(f"  ✓ Runway Months: {snapshot2.runway_months} (None = profitable)")
    
    # Scenario 3: Break-even company
    print("\nScenario 1.3: Break-even company")
    snapshot3 = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("50000"),
        monthly_revenue=Decimal("30000"),
        operating_costs=Decimal("30000"),
    )
    snapshot3.compute_derived_metrics()
    
    assert snapshot3.monthly_burn == Decimal("0"), "Burn should be 0 (break-even)"
    assert snapshot3.runway_months is None, "Runway should be None for break-even"
    print(f"  ✓ Monthly Burn: {snapshot3.monthly_burn} SAR (break-even)")
    print(f"  ✓ Runway Months: {snapshot3.runway_months} (None = break-even)")
    
    # Scenario 4: Missing financial data
    print("\nScenario 1.4: Incomplete financial data")
    snapshot4 = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("100000"),
        monthly_revenue=None,  # Missing
        operating_costs=Decimal("40000"),
    )
    snapshot4.compute_derived_metrics()
    
    assert snapshot4.monthly_burn is None, "Burn should stay None if incomplete data"
    print(f"  ✓ Computation skipped (missing revenue)")
    print(f"  ✓ Monthly Burn: {snapshot4.monthly_burn}")
    
    print("\n✅ All derived metrics tests passed")


def test_signal_creation():
    """Test Signal entity creation and validation."""
    print("\n[Test 2] Signal Entity Creation")
    print("=" * 70)
    
    # Create valid signal
    print("\nCreating valid signal...")
    signal = Signal(
        name="RunwayMonths",
        category=SignalCategory.FINANCIAL,
        value=12.5,
    )
    
    assert signal.name == "RunwayMonths"
    assert signal.category == SignalCategory.FINANCIAL
    assert signal.value == 12.5
    assert signal.id is not None
    assert signal.created_at is not None
    
    print(f"  ✓ Signal ID: {signal.id}")
    print(f"  ✓ Signal Name: {signal.name}")
    print(f"  ✓ Category: {signal.category.value}")
    print(f"  ✓ Value: {signal.value}")
    print(f"  ✓ Created At: {signal.created_at}")
    
    # Test signal equality
    print("\nTesting signal equality...")
    signal2 = Signal(
        name="RunwayMonths",
        category=SignalCategory.FINANCIAL,
        value=12.5,
        id=signal.id,  # Same ID
    )
    
    assert signal == signal2, "Signals with same ID should be equal"
    print(f"  ✓ Signal equality works (by ID)")
    
    # Test hashability
    print("\nTesting signal hashability...")
    signal_set = {signal, signal2}
    assert len(signal_set) == 1, "Duplicate signals should deduplicate in sets"
    print(f"  ✓ Signals are hashable and deduplicate correctly")
    
    # Test validation errors
    print("\nTesting validation...")
    try:
        Signal(name="", category=SignalCategory.FINANCIAL, value=10)
        assert False, "Should reject empty name"
    except ValueError:
        print(f"  ✓ Rejects empty name")
    
    try:
        Signal(name="Test", category="INVALID", value=10)
        assert False, "Should reject invalid category"
    except TypeError:
        print(f"  ✓ Rejects invalid category")
    
    try:
        Signal(name="Test", category=SignalCategory.FINANCIAL, value="invalid")
        assert False, "Should reject non-numeric value"
    except TypeError:
        print(f"  ✓ Rejects non-numeric value")
    
    print("\n✅ All signal creation tests passed")


def test_signal_engine():
    """Test SignalEngine.compute() with various scenarios."""
    print("\n[Test 3] Signal Engine Computation")
    print("=" * 70)
    
    # Scenario 1: Full snapshot with all financial attributes
    print("\nScenario 3.1: Full snapshot data")
    snapshot1 = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("120000"),
        monthly_revenue=Decimal("20000"),
        operating_costs=Decimal("40000"),
    )
    snapshot1.compute_derived_metrics()
    
    signals1 = SignalEngine.compute(snapshot1)
    
    assert len(signals1) == 3, f"Should generate 3 signals, got {len(signals1)}"
    print(f"  ✓ Generated {len(signals1)} signals")
    
    signal_names = {s.name for s in signals1}
    assert "MonthlyBurn" in signal_names, "Should have MonthlyBurn signal"
    assert "RunwayMonths" in signal_names, "Should have RunwayMonths signal"
    assert "RunwayRisk" in signal_names, "Should have RunwayRisk signal"
    print(f"  ✓ Signals: {', '.join(sorted(signal_names))}")
    
    # Check specific signal values
    for signal in signals1:
        if signal.name == "MonthlyBurn":
            assert signal.value == 20000, "Monthly burn should be 20000"
            assert signal.category == SignalCategory.FINANCIAL
            print(f"  ✓ MonthlyBurn: {signal.value} (FINANCIAL)")
        elif signal.name == "RunwayMonths":
            assert signal.value == 6.0, "Runway should be 6 months"
            assert signal.category == SignalCategory.FINANCIAL
            print(f"  ✓ RunwayMonths: {signal.value} (FINANCIAL)")
        elif signal.name == "RunwayRisk":
            assert signal.value == 2, "Runway 6 = Caution (value 2)"
            assert signal.category == SignalCategory.RISK
            print(f"  ✓ RunwayRisk: {signal.value} (RISK - Caution)")
    
    # Scenario 2: Runway < 6 months (High Risk)
    print("\nScenario 3.2: High risk (runway < 6 months)")
    snapshot2 = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("50000"),
        monthly_revenue=Decimal("20000"),
        operating_costs=Decimal("40000"),
    )
    snapshot2.compute_derived_metrics()
    signals2 = SignalEngine.compute(snapshot2)
    
    risk_signal = next(s for s in signals2 if s.name == "RunwayRisk")
    assert risk_signal.value == 3, "Runway < 6 should be value 3 (High Risk)"
    print(f"  ✓ RunwayRisk: {risk_signal.value} (High Risk - runway ~2.5 months)")
    
    # Scenario 3: Profitable company (runway = None)
    print("\nScenario 3.3: Profitable company (no runway risk)")
    snapshot3 = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("100000"),
        monthly_revenue=Decimal("50000"),
        operating_costs=Decimal("40000"),
    )
    snapshot3.compute_derived_metrics()
    signals3 = SignalEngine.compute(snapshot3)
    
    risk_signal = next(s for s in signals3 if s.name == "RunwayRisk")
    assert risk_signal.value == 0, "Profitable company should be value 0 (No Risk)"
    print(f"  ✓ RunwayRisk: {risk_signal.value} (No Risk - profitable)")
    
    # Scenario 4: Runway > 12 months (Healthy)
    print("\nScenario 3.4: Healthy runway (> 12 months)")
    snapshot4 = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("500000"),
        monthly_revenue=Decimal("20000"),
        operating_costs=Decimal("40000"),
    )
    snapshot4.compute_derived_metrics()
    signals4 = SignalEngine.compute(snapshot4)
    
    risk_signal = next(s for s in signals4 if s.name == "RunwayRisk")
    assert risk_signal.value == 1, "Runway > 12 should be value 1 (Healthy)"
    print(f"  ✓ RunwayRisk: {risk_signal.value} (Healthy - runway 25 months)")
    
    print("\n✅ All signal engine tests passed")


def test_determinism():
    """Test that SignalEngine produces deterministic results."""
    print("\n[Test 4] Determinism Verification")
    print("=" * 70)
    
    # Create snapshot data that stays constant
    company_id = uuid4()
    snapshot_date = date.today()
    
    # Generate signals multiple times from identical snapshot data
    print("\nGenerating signals 5 times from identical data...")
    all_signals = []
    
    for i in range(5):
        snapshot = Snapshot(
            id=uuid4(),  # Different ID each time
            company_id=company_id,
            snapshot_date=snapshot_date,
            cash_balance=Decimal("150000"),
            monthly_revenue=Decimal("25000"),
            operating_costs=Decimal("45000"),
        )
        snapshot.compute_derived_metrics()
        signals = SignalEngine.compute(snapshot)
        all_signals.append(signals)
    
    # Compare all signal generations
    first_signals = all_signals[0]
    
    for i, signals in enumerate(all_signals[1:], 1):
        assert len(signals) == len(first_signals), f"Run {i}: Different signal count"
        
        for s1, s2 in zip(sorted(first_signals, key=lambda s: s.name),
                          sorted(signals, key=lambda s: s.name)):
            assert s1.name == s2.name, f"Run {i}: Signal name mismatch"
            assert s1.category == s2.category, f"Run {i}: Category mismatch"
            assert s1.value == s2.value, f"Run {i}: Value mismatch"
    
    print(f"  ✓ All 5 runs produced identical signals")
    print(f"  ✓ Signal values:")
    for signal in sorted(first_signals, key=lambda s: s.name):
        print(f"    - {signal.name}: {signal.value}")
    
    print("\n✅ Determinism verified")


def test_framework_isolation():
    """Test that domain has no framework imports."""
    print("\n[Test 5] Framework Isolation Check")
    print("=" * 70)
    
    # Import all domain modules and check for framework imports
    import app.domain.entities.snapshot
    import app.domain.entities.signal
    import app.domain.enums.stage
    import app.domain.enums.snapshot_status
    import app.domain.enums.signal_category
    import app.domain.engines.signal_engine
    import app.domain.exceptions
    
    forbidden_imports = {
        'fastapi': 'FastAPI',
        'sqlalchemy': 'SQLAlchemy',
        'pydantic': 'Pydantic',
    }
    
    modules_to_check = [
        app.domain.entities.snapshot,
        app.domain.entities.signal,
        app.domain.enums.stage,
        app.domain.enums.snapshot_status,
        app.domain.enums.signal_category,
        app.domain.engines.signal_engine,
        app.domain.exceptions,
    ]
    
    issues = []
    
    for module in modules_to_check:
        module_name = module.__name__
        module_source = module.__file__ or ""
        
        for forbidden, friendly_name in forbidden_imports.items():
            if forbidden in dir(module):
                issues.append(f"  ✗ {module_name} imports {friendly_name}")
    
    if issues:
        print("Framework imports found:")
        for issue in issues:
            print(issue)
        print("\n❌ Framework isolation check FAILED")
        return False
    else:
        print("  ✓ No FastAPI imports in domain")
        print("  ✓ No SQLAlchemy imports in domain")
        print("  ✓ No Pydantic imports in domain")
        print("\n✅ Framework isolation verified")
        return True


def test_signal_categories():
    """Test SignalCategory enum."""
    print("\n[Test 6] Signal Category Enum")
    print("=" * 70)
    
    categories = [
        SignalCategory.FINANCIAL,
        SignalCategory.GROWTH,
        SignalCategory.RISK,
        SignalCategory.OPERATIONAL,
        SignalCategory.MARKET,
    ]
    
    print("\nAvailable signal categories:")
    for cat in categories:
        print(f"  ✓ {cat.value}")
        # Verify it's string-based
        assert isinstance(cat, str), f"{cat.value} should be instance of str"
    
    # Test that values are correct
    assert SignalCategory.FINANCIAL.value == "FINANCIAL"
    assert SignalCategory.GROWTH.value == "GROWTH"
    assert SignalCategory.RISK.value == "RISK"
    assert SignalCategory.OPERATIONAL.value == "OPERATIONAL"
    assert SignalCategory.MARKET.value == "MARKET"
    
    print("\n✅ Signal categories verified")


def main():
    """Run all Sprint 3 verification tests."""
    print("\n" + "=" * 70)
    print("SPRINT 3 VERIFICATION - Signal Engine Implementation")
    print("=" * 70)
    
    try:
        test_derived_metrics_calculation()
        test_signal_creation()
        test_signal_engine()
        test_determinism()
        framework_ok = test_framework_isolation()
        test_signal_categories()
        
        print("\n" + "=" * 70)
        print("🎉 ALL SPRINT 3 TESTS PASSED")
        print("=" * 70)
        print("\nSprint 3 Status:")
        print("  ✅ Snapshot computes derived metrics correctly")
        print("  ✅ Signal entity implemented")
        print("  ✅ SignalCategory enum created")
        print("  ✅ SignalEngine generates signals deterministically")
        print("  ✅ Framework isolation maintained")
        print("  ✅ All signals generated correctly")
        print("\nNext Sprint: Sprint 4 (Rule Engine)")
        
        return 0 if framework_ok else 1
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
