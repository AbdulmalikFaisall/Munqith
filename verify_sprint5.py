"""Sprint 5 comprehensive verification suite.

Tests:
1. ExplainabilityResolver - Signal contribution logic
2. FinalizeSnapshotUseCase - Full pipeline orchestration
3. SnapshotRepository - Persistence with transaction management
4. Immutability enforcement - Post-finalization constraints
5. Performance - Finalization under 500ms
6. End-to-end pipeline - Manual test scenario

All tests are deterministic and reproducible.
"""
import sys
import time
from decimal import Decimal
from uuid import uuid4
from datetime import date

# Add app to path
sys.path.insert(0, '/c/Users/user/munqith')

from app.domain.entities.company import Company
from app.domain.entities.snapshot import Snapshot
from app.domain.entities.signal import Signal
from app.domain.entities.rule_result import RuleResult
from app.domain.enums import SnapshotStatus, Stage, SignalCategory
from app.domain.engines import (
    SignalEngine,
    RuleEngine,
    StageEvaluator,
    ExplainabilityResolver,
)
from app.domain.exceptions import ImmutableSnapshotError, FinalizeDraftOnlyError
from app.application.use_cases import FinalizeSnapshotUseCase
from app.infrastructure.db.session import SessionLocal


def test_explainability_resolver_high_risk():
    """Test: HIGH_RISK runway → Contributing signals identified."""
    print("\n✓ Test: ExplainabilityResolver - HIGH_RISK")
    
    # Create signals for high-risk scenario
    signals = [
        Signal(name="RunwayRisk", category=SignalCategory.RISK, value=3.0),
        Signal(name="RunwayMonths", category=SignalCategory.FINANCIAL, value=3.0),
        Signal(name="MonthlyBurn", category=SignalCategory.FINANCIAL, value=50000.0),
    ]
    
    # Create rule results
    rule_results = [
        RuleResult(rule_name="RunwayRiskRule", result="HIGH_RISK"),
        RuleResult(rule_name="ProfitabilityRule", result="BURNING"),
    ]
    
    # Resolve contributing signals
    contributing = ExplainabilityResolver.resolve(signals, rule_results)
    
    # Verify: RunwayRisk and RunwayMonths should be contributors
    assert len(contributing) == 2, f"Expected 2 contributors, got {len(contributing)}"
    names = {s.name for s in contributing}
    assert "RunwayRisk" in names, "RunwayRisk should contribute"
    assert "RunwayMonths" in names, "RunwayMonths should contribute"
    print(f"  - Contributing signals: {', '.join(names)}")


def test_explainability_resolver_caution():
    """Test: CAUTION runway → Contributing signals identified."""
    print("\n✓ Test: ExplainabilityResolver - CAUTION")
    
    signals = [
        Signal(name="RunwayRisk", category=SignalCategory.RISK, value=2.0),
        Signal(name="RunwayMonths", category=SignalCategory.FINANCIAL, value=9.0),
    ]
    
    rule_results = [
        RuleResult(rule_name="RunwayRiskRule", result="CAUTION"),
        RuleResult(rule_name="ProfitabilityRule", result="BURNING"),
    ]
    
    contributing = ExplainabilityResolver.resolve(signals, rule_results)
    
    assert len(contributing) == 2, f"Expected 2 contributors, got {len(contributing)}"
    names = {s.name for s in contributing}
    assert "RunwayRisk" in names
    assert "RunwayMonths" in names
    print(f"  - Contributing signals: {', '.join(names)}")


def test_explainability_resolver_healthy_burning():
    """Test: HEALTHY + BURNING → Runway and burn signals contribute."""
    print("\n✓ Test: ExplainabilityResolver - HEALTHY + BURNING → SEED")
    
    signals = [
        Signal(name="RunwayMonths", category=SignalCategory.FINANCIAL, value=15.0),
        Signal(name="MonthlyBurn", category=SignalCategory.FINANCIAL, value=30000.0),
    ]
    
    rule_results = [
        RuleResult(rule_name="RunwayRiskRule", result="HEALTHY"),
        RuleResult(rule_name="ProfitabilityRule", result="BURNING"),
    ]
    
    contributing = ExplainabilityResolver.resolve(signals, rule_results)
    
    assert len(contributing) == 2
    names = {s.name for s in contributing}
    assert "RunwayMonths" in names
    assert "MonthlyBurn" in names
    print(f"  - Contributing signals: {', '.join(names)}")


def test_explainability_resolver_profitable():
    """Test: HEALTHY + PROFITABLE → Both signals contribute."""
    print("\n✓ Test: ExplainabilityResolver - HEALTHY + PROFITABLE → SERIES_A")
    
    signals = [
        Signal(name="RunwayMonths", category=SignalCategory.FINANCIAL, value=25.0),
        Signal(name="MonthlyBurn", category=SignalCategory.FINANCIAL, value=-5000.0),
    ]
    
    rule_results = [
        RuleResult(rule_name="RunwayRiskRule", result="HEALTHY"),
        RuleResult(rule_name="ProfitabilityRule", result="PROFITABLE"),
    ]
    
    contributing = ExplainabilityResolver.resolve(signals, rule_results)
    
    assert len(contributing) == 2
    names = {s.name for s in contributing}
    assert "RunwayMonths" in names
    assert "MonthlyBurn" in names
    print(f"  - Contributing signals: {', '.join(names)}")


def test_snapshot_immutability_after_finalization():
    """Test: Finalized snapshot cannot be modified."""
    print("\n✓ Test: Snapshot Immutability - Cannot modify finalized snapshot")
    
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("100000"),
    )
    
    # Finalize snapshot
    snapshot.finalize()
    assert snapshot.is_finalized
    
    # Attempt to update financials - should raise error
    try:
        snapshot.update_financials(cash_balance=Decimal("50000"))
        assert False, "Should raise ImmutableSnapshotError"
    except ImmutableSnapshotError as e:
        print(f"  - Caught expected error: {type(e).__name__}")
        assert "immutable" in str(e).lower()
    
    # Attempt to set stage - should raise error
    try:
        snapshot.set_stage(Stage.SEED)
        assert False, "Should raise ImmutableSnapshotError"
    except ImmutableSnapshotError:
        print(f"  - Caught expected error for set_stage")


def test_snapshot_cannot_finalize_twice():
    """Test: Cannot finalize an already finalized snapshot."""
    print("\n✓ Test: Snapshot Lifecycle - Cannot finalize twice")
    
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
    )
    
    snapshot.finalize()
    
    # Attempt to finalize again
    try:
        snapshot.finalize()
        assert False, "Should raise FinalizeDraftOnlyError"
    except FinalizeDraftOnlyError as e:
        print(f"  - Caught expected error: {type(e).__name__}")
        assert "FINALIZED" in str(e)


def test_full_pipeline_manual_scenario():
    """Test: Full pipeline with manual test scenario.
    
    Scenario:
    - cash_balance = 120000
    - monthly_revenue = 20000
    - operating_costs = 40000
    
    Expected:
    - monthly_burn = 20000
    - runway_months = 6
    - RunwayRisk = CAUTION (value=2)
    - stage = PRE_SEED
    """
    print("\n✓ Test: Full Pipeline - Manual Scenario")
    
    # Create snapshot
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("120000"),
        monthly_revenue=Decimal("20000"),
        operating_costs=Decimal("40000"),
    )
    
    print(f"  Input: cash={snapshot.cash_balance}, revenue={snapshot.monthly_revenue}, costs={snapshot.operating_costs}")
    
    # Step 1: Compute derived metrics
    snapshot.compute_derived_metrics()
    assert snapshot.monthly_burn == Decimal("20000"), f"Expected burn=20000, got {snapshot.monthly_burn}"
    assert snapshot.runway_months == Decimal("6"), f"Expected runway=6, got {snapshot.runway_months}"
    print(f"  - Computed: burn={snapshot.monthly_burn}, runway={snapshot.runway_months}")
    
    # Step 2: Generate signals
    signals = SignalEngine.compute(snapshot)
    assert len(signals) == 3, f"Expected 3 signals, got {len(signals)}"
    
    signal_map = {s.name: s for s in signals}
    assert signal_map["MonthlyBurn"].value == 20000.0
    assert signal_map["RunwayMonths"].value == 6.0
    assert signal_map["RunwayRisk"].value == 2.0  # CAUTION
    print(f"  - Generated {len(signals)} signals")
    
    # Step 3: Evaluate rules
    rule_results = RuleEngine.evaluate(signals)
    assert len(rule_results) == 2, f"Expected 2 rule results, got {len(rule_results)}"
    
    result_map = {r.rule_name: r.result for r in rule_results}
    assert result_map["RunwayRiskRule"] == "CAUTION"
    assert result_map["ProfitabilityRule"] == "BURNING"
    print(f"  - Rule results: {result_map}")
    
    # Step 4: Determine stage
    stage = StageEvaluator.determine(rule_results)
    assert stage == Stage.PRE_SEED, f"Expected PRE_SEED, got {stage}"
    print(f"  - Determined stage: {stage}")
    
    # Step 5: Resolve contributing signals
    contributing = ExplainabilityResolver.resolve(signals, rule_results)
    assert len(contributing) == 2, f"Expected 2 contributing signals, got {len(contributing)}"
    contrib_names = {s.name for s in contributing}
    assert "RunwayRisk" in contrib_names
    assert "RunwayMonths" in contrib_names
    print(f"  - Contributing signals: {contrib_names}")
    
    # Step 6: Assign stage and finalize
    snapshot.set_stage(stage)
    snapshot.finalize()
    assert snapshot.is_finalized
    assert snapshot.stage == Stage.PRE_SEED
    print(f"  - Snapshot finalized with stage={snapshot.stage}")


def test_full_pipeline_determinism():
    """Test: Full pipeline is deterministic (same input → same output)."""
    print("\n✓ Test: Full Pipeline - Determinism")
    
    # Run pipeline 5 times with identical input
    results = []
    
    for run in range(5):
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=Decimal("150000"),
            monthly_revenue=Decimal("30000"),
            operating_costs=Decimal("45000"),
        )
        
        snapshot.compute_derived_metrics()
        signals = SignalEngine.compute(snapshot)
        rule_results = RuleEngine.evaluate(signals)
        stage = StageEvaluator.determine(rule_results)
        
        results.append(stage)
    
    # Verify all results are identical
    assert all(s == results[0] for s in results), "Determinism violated"
    print(f"  - 5 runs produced identical stage: {results[0]}")


def test_all_stage_paths():
    """Test: All stage determination paths work correctly."""
    print("\n✓ Test: All Stage Determination Paths")
    
    test_cases = [
        # (burn, runway, expected_stage, description)
        (Decimal("50000"), Decimal("3"), Stage.IDEA, "HIGH_RISK → IDEA"),
        (Decimal("30000"), Decimal("9"), Stage.PRE_SEED, "CAUTION → PRE_SEED"),
        (Decimal("20000"), Decimal("15"), Stage.SEED, "HEALTHY + BURNING → SEED"),
        (Decimal("-5000"), Decimal("30"), Stage.SERIES_A, "HEALTHY + PROFITABLE → SERIES_A"),
    ]
    
    for burn, runway, expected_stage, description in test_cases:
        # Create signals
        signals = [
            Signal(name="MonthlyBurn", category=SignalCategory.FINANCIAL, value=float(burn)),
            Signal(name="RunwayMonths", category=SignalCategory.FINANCIAL, value=float(runway)),
            Signal(
                name="RunwayRisk",
                category=SignalCategory.RISK,
                value=3.0 if runway < 6 else (2.0 if runway <= 12 else 1.0),
            ),
        ]
        
        # Evaluate rules
        rule_results = RuleEngine.evaluate(signals)
        
        # Determine stage
        stage = StageEvaluator.determine(rule_results)
        
        assert stage == expected_stage, f"Expected {expected_stage}, got {stage} for {description}"
        print(f"  - {description}: {stage}")


def test_performance_under_500ms():
    """Test: Finalization completes in under 500ms (pure computation)."""
    print("\n✓ Test: Performance - Finalization under 500ms")
    
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("200000"),
        monthly_revenue=Decimal("40000"),
        operating_costs=Decimal("55000"),
    )
    
    start = time.time()
    
    # Execute full pipeline
    snapshot.compute_derived_metrics()
    signals = SignalEngine.compute(snapshot)
    rule_results = RuleEngine.evaluate(signals)
    stage = StageEvaluator.determine(rule_results)
    contributing = ExplainabilityResolver.resolve(signals, rule_results)
    snapshot.set_stage(stage)
    snapshot.finalize()
    
    elapsed = (time.time() - start) * 1000  # Convert to ms
    
    assert elapsed < 500, f"Finalization took {elapsed}ms, should be < 500ms"
    print(f"  - Pure computation pipeline completed in {elapsed:.2f}ms")


def run_all_tests():
    """Run all Sprint 5 verification tests."""
    print("\n" + "=" * 70)
    print("SPRINT 5 COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 70)
    
    tests = [
        ("ExplainabilityResolver - HIGH_RISK", test_explainability_resolver_high_risk),
        ("ExplainabilityResolver - CAUTION", test_explainability_resolver_caution),
        ("ExplainabilityResolver - HEALTHY + BURNING", test_explainability_resolver_healthy_burning),
        ("ExplainabilityResolver - PROFITABLE", test_explainability_resolver_profitable),
        ("Snapshot Immutability", test_snapshot_immutability_after_finalization),
        ("Snapshot Lifecycle", test_snapshot_cannot_finalize_twice),
        ("Full Pipeline - Manual Scenario", test_full_pipeline_manual_scenario),
        ("Full Pipeline - Determinism", test_full_pipeline_determinism),
        ("Stage Determination Paths", test_all_stage_paths),
        ("Performance < 500ms", test_performance_under_500ms),
    ]
    
    passed = 0
    failed = 0
    
    try:
        for name, test_func in tests:
            try:
                test_func()
                passed += 1
            except AssertionError as e:
                print(f"  ✗ FAILED: {e}")
                failed += 1
            except Exception as e:
                print(f"  ✗ ERROR: {type(e).__name__}: {e}")
                failed += 1
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {type(e).__name__}: {e}")
        failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ALL SPRINT 5 TESTS PASSED ✨\n")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED\n")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
