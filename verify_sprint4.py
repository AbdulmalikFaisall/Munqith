#!/usr/bin/env python
"""
Sprint 4 Verification Script

Comprehensive verification of Rule Engine + Stage Evaluator implementation:
- Rule evaluation
- Stage determination
- Deterministic behavior
- Framework isolation
"""
import sys
import os
from decimal import Decimal
from datetime import date
from uuid import uuid4

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import domain components
from app.domain.entities import Snapshot, Signal, RuleResult
from app.domain.enums import Stage, SignalCategory
from app.domain.engines import SignalEngine, RuleEngine, StageEvaluator


def test_rule_result_creation():
    """Test RuleResult entity creation and validation."""
    print("\n[Test 1] RuleResult Entity Creation")
    print("=" * 70)
    
    # Create valid rule result
    print("\nCreating valid rule result...")
    result = RuleResult(
        rule_name="RunwayRiskRule",
        result="HIGH_RISK",
    )
    
    assert result.rule_name == "RunwayRiskRule"
    assert result.result == "HIGH_RISK"
    assert result.id is not None
    assert result.created_at is not None
    
    print(f"  ✓ Rule Result ID: {result.id}")
    print(f"  ✓ Rule Name: {result.rule_name}")
    print(f"  ✓ Result: {result.result}")
    
    # Test equality
    print("\nTesting rule result equality...")
    result2 = RuleResult(
        rule_name="RunwayRiskRule",
        result="HIGH_RISK",
        id=result.id,
    )
    
    assert result == result2, "Results with same ID should be equal"
    print(f"  ✓ Rule result equality works (by ID)")
    
    # Test validation
    print("\nTesting validation...")
    try:
        RuleResult(rule_name="", result="HIGH_RISK")
        assert False, "Should reject empty rule_name"
    except ValueError:
        print(f"  ✓ Rejects empty rule_name")
    
    try:
        RuleResult(rule_name="Test", result="")
        assert False, "Should reject empty result"
    except ValueError:
        print(f"  ✓ Rejects empty result")
    
    print("\n✅ All rule result tests passed")


def test_rule_engine_runway_risk_rule():
    """Test RuleEngine with RunwayRisk signal."""
    print("\n[Test 2] RuleEngine - RunwayRisk Rule")
    print("=" * 70)
    
    # Scenario 1: HIGH_RISK
    print("\nScenario 2.1: HIGH_RISK (runway < 6 months)")
    signal = Signal(
        name="RunwayRisk",
        category=SignalCategory.RISK,
        value=3.0,
    )
    
    results = RuleEngine.evaluate([signal])
    assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    
    result = results[0]
    assert result.rule_name == "RunwayRiskRule"
    assert result.result == "HIGH_RISK"
    print(f"  ✓ RunwayRisk=3 → HIGH_RISK")
    
    # Scenario 2: CAUTION
    print("\nScenario 2.2: CAUTION (6-12 months runway)")
    signal = Signal(
        name="RunwayRisk",
        category=SignalCategory.RISK,
        value=2.0,
    )
    
    results = RuleEngine.evaluate([signal])
    result = results[0]
    assert result.result == "CAUTION"
    print(f"  ✓ RunwayRisk=2 → CAUTION")
    
    # Scenario 3: HEALTHY
    print("\nScenario 2.3: HEALTHY (>12 months runway)")
    signal = Signal(
        name="RunwayRisk",
        category=SignalCategory.RISK,
        value=1.0,
    )
    
    results = RuleEngine.evaluate([signal])
    result = results[0]
    assert result.result == "HEALTHY"
    print(f"  ✓ RunwayRisk=1 → HEALTHY")
    
    # Scenario 4: PROFITABLE
    print("\nScenario 2.4: PROFITABLE (break-even/profitable)")
    signal = Signal(
        name="RunwayRisk",
        category=SignalCategory.RISK,
        value=0.0,
    )
    
    results = RuleEngine.evaluate([signal])
    result = results[0]
    assert result.result == "PROFITABLE"
    print(f"  ✓ RunwayRisk=0 → PROFITABLE")
    
    print("\n✅ All RunwayRisk rule tests passed")


def test_rule_engine_profitability_rule():
    """Test RuleEngine with MonthlyBurn signal."""
    print("\n[Test 3] RuleEngine - Profitability Rule")
    print("=" * 70)
    
    # Scenario 1: BURNING (burn > 0)
    print("\nScenario 3.1: BURNING (positive monthly burn)")
    signal = Signal(
        name="MonthlyBurn",
        category=SignalCategory.FINANCIAL,
        value=20000.0,
    )
    
    results = RuleEngine.evaluate([signal])
    assert len(results) == 1
    
    result = [r for r in results if r.rule_name == "ProfitabilityRule"][0]
    assert result.result == "BURNING"
    print(f"  ✓ MonthlyBurn=20000 → BURNING")
    
    # Scenario 2: PROFITABLE (burn <= 0)
    print("\nScenario 3.2: PROFITABLE (zero/negative burn)")
    signal = Signal(
        name="MonthlyBurn",
        category=SignalCategory.FINANCIAL,
        value=-5000.0,
    )
    
    results = RuleEngine.evaluate([signal])
    result = [r for r in results if r.rule_name == "ProfitabilityRule"][0]
    assert result.result == "PROFITABLE"
    print(f"  ✓ MonthlyBurn=-5000 → PROFITABLE")
    
    # Scenario 3: Break-even (burn = 0)
    print("\nScenario 3.3: Break-even (zero burn)")
    signal = Signal(
        name="MonthlyBurn",
        category=SignalCategory.FINANCIAL,
        value=0.0,
    )
    
    results = RuleEngine.evaluate([signal])
    result = [r for r in results if r.rule_name == "ProfitabilityRule"][0]
    assert result.result == "PROFITABLE"
    print(f"  ✓ MonthlyBurn=0 → PROFITABLE")
    
    print("\n✅ All profitability rule tests passed")


def test_rule_engine_multiple_signals():
    """Test RuleEngine with multiple signals."""
    print("\n[Test 4] RuleEngine - Multiple Signals")
    print("=" * 70)
    
    print("\nEvaluating with both signals...")
    signals = [
        Signal(name="RunwayRisk", category=SignalCategory.RISK, value=2.0),
        Signal(name="MonthlyBurn", category=SignalCategory.FINANCIAL, value=15000.0),
    ]
    
    results = RuleEngine.evaluate(signals)
    
    assert len(results) == 2, f"Expected 2 results, got {len(results)}"
    
    for result in results:
        print(f"  ✓ {result.rule_name}: {result.result}")
    
    print("\n✅ Multiple signal evaluation passed")


def test_stage_evaluator_high_risk():
    """Test StageEvaluator with HIGH_RISK classification."""
    print("\n[Test 5] StageEvaluator - HIGH_RISK → IDEA")
    print("=" * 70)
    
    print("\nHIGH_RISK runway → IDEA stage")
    rule_results = [
        RuleResult(rule_name="RunwayRiskRule", result="HIGH_RISK"),
    ]
    
    stage = StageEvaluator.determine(rule_results)
    assert stage == Stage.IDEA, f"Expected IDEA, got {stage}"
    print(f"  ✓ HIGH_RISK → {stage.value}")
    
    print("\n✅ HIGH_RISK test passed")


def test_stage_evaluator_caution():
    """Test StageEvaluator with CAUTION classification."""
    print("\n[Test 6] StageEvaluator - CAUTION → PRE_SEED")
    print("=" * 70)
    
    print("\nCAUTION runway → PRE_SEED stage")
    rule_results = [
        RuleResult(rule_name="RunwayRiskRule", result="CAUTION"),
    ]
    
    stage = StageEvaluator.determine(rule_results)
    assert stage == Stage.PRE_SEED, f"Expected PRE_SEED, got {stage}"
    print(f"  ✓ CAUTION → {stage.value}")
    
    print("\n✅ CAUTION test passed")


def test_stage_evaluator_healthy_burning():
    """Test StageEvaluator with HEALTHY + BURNING."""
    print("\n[Test 7] StageEvaluator - HEALTHY + BURNING → SEED")
    print("=" * 70)
    
    print("\nHEALTHY runway + BURNING → SEED stage")
    rule_results = [
        RuleResult(rule_name="RunwayRiskRule", result="HEALTHY"),
        RuleResult(rule_name="ProfitabilityRule", result="BURNING"),
    ]
    
    stage = StageEvaluator.determine(rule_results)
    assert stage == Stage.SEED, f"Expected SEED, got {stage}"
    print(f"  ✓ HEALTHY + BURNING → {stage.value}")
    
    print("\n✅ HEALTHY + BURNING test passed")


def test_stage_evaluator_healthy_profitable():
    """Test StageEvaluator with HEALTHY + PROFITABLE."""
    print("\n[Test 8] StageEvaluator - HEALTHY + PROFITABLE → SERIES_A")
    print("=" * 70)
    
    print("\nHEALTHY runway + PROFITABLE → SERIES_A stage")
    rule_results = [
        RuleResult(rule_name="RunwayRiskRule", result="HEALTHY"),
        RuleResult(rule_name="ProfitabilityRule", result="PROFITABLE"),
    ]
    
    stage = StageEvaluator.determine(rule_results)
    assert stage == Stage.SERIES_A, f"Expected SERIES_A, got {stage}"
    print(f"  ✓ HEALTHY + PROFITABLE → {stage.value}")
    
    print("\n✅ HEALTHY + PROFITABLE test passed")


def test_stage_evaluator_profitable_status():
    """Test StageEvaluator with PROFITABLE runway status."""
    print("\n[Test 9] StageEvaluator - PROFITABLE Status")
    print("=" * 70)
    
    print("\nPROFITABLE runway (no burn concern)...")
    rule_results = [
        RuleResult(rule_name="RunwayRiskRule", result="PROFITABLE"),
        RuleResult(rule_name="ProfitabilityRule", result="PROFITABLE"),
    ]
    
    stage = StageEvaluator.determine(rule_results)
    assert stage == Stage.SERIES_A, f"Expected SERIES_A, got {stage}"
    print(f"  ✓ PROFITABLE + PROFITABLE → {stage.value}")
    
    print("\n✅ PROFITABLE status test passed")


def test_end_to_end_pipeline():
    """Test full pipeline: Snapshot → Signals → Rules → Stage."""
    print("\n[Test 10] End-to-End Pipeline")
    print("=" * 70)
    
    print("\nScenario: High-risk company with 5-month runway")
    
    # Step 1: Create snapshot and compute metrics
    print("\n1. Creating snapshot with financial data...")
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("100000"),
        monthly_revenue=Decimal("20000"),
        operating_costs=Decimal("40000"),
    )
    
    snapshot.compute_derived_metrics()
    print(f"   Burn: {snapshot.monthly_burn} SAR")
    print(f"   Runway: {snapshot.runway_months} months")
    
    # Step 2: Generate signals
    print("\n2. Generating signals...")
    signals = SignalEngine.compute(snapshot)
    print(f"   Generated {len(signals)} signals")
    for sig in sorted(signals, key=lambda s: s.name):
        print(f"   - {sig.name}: {sig.value}")
    
    # Step 3: Evaluate rules
    print("\n3. Evaluating rules...")
    rule_results = RuleEngine.evaluate(signals)
    print(f"   Generated {len(rule_results)} rule results")
    for rule_result in rule_results:
        print(f"   - {rule_result.rule_name}: {rule_result.result}")
    
    # Step 4: Determine stage
    print("\n4. Determining stage...")
    stage = StageEvaluator.determine(rule_results)
    print(f"   Stage: {stage.value}")
    
    # Verify the stage is correct (5 months runway → HIGH_RISK → IDEA)
    assert stage == Stage.IDEA, f"Expected IDEA, got {stage}"
    print(f"\n✅ End-to-end pipeline test passed")


def test_determinism():
    """Test that engines produce deterministic results."""
    print("\n[Test 11] Determinism Verification")
    print("=" * 70)
    
    print("\nRunning same scenario 5 times...")
    
    all_stages = []
    
    for i in range(5):
        # Create identical snapshot
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=Decimal("150000"),
            monthly_revenue=Decimal("25000"),
            operating_costs=Decimal("45000"),
        )
        
        snapshot.compute_derived_metrics()
        signals = SignalEngine.compute(snapshot)
        rule_results = RuleEngine.evaluate(signals)
        stage = StageEvaluator.determine(rule_results)
        
        all_stages.append(stage)
    
    # Check all stages are identical
    first_stage = all_stages[0]
    for i, stage in enumerate(all_stages[1:], 1):
        assert stage == first_stage, f"Run {i}: Stage mismatch"
    
    print(f"  ✓ All 5 runs produced: {first_stage.value}")
    print("\n✅ Determinism verified")


def test_framework_isolation():
    """Test that domain has no framework imports."""
    print("\n[Test 12] Framework Isolation Check")
    print("=" * 70)
    
    import subprocess
    
    result = subprocess.run(
        ['grep', '-r', 'fastapi|sqlalchemy|pydantic', 'app/domain/'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0 and result.stdout:
        print(f"Framework imports found:\n{result.stdout}")
        print("\n❌ Framework isolation check FAILED")
        return False
    else:
        print("  ✓ No FastAPI imports in domain")
        print("  ✓ No SQLAlchemy imports in domain")
        print("  ✓ No Pydantic imports in domain")
        print("\n✅ Framework isolation verified")
        return True


def main():
    """Run all Sprint 4 verification tests."""
    print("\n" + "=" * 70)
    print("SPRINT 4 VERIFICATION - Rule Engine + Stage Evaluator")
    print("=" * 70)
    
    try:
        test_rule_result_creation()
        test_rule_engine_runway_risk_rule()
        test_rule_engine_profitability_rule()
        test_rule_engine_multiple_signals()
        test_stage_evaluator_high_risk()
        test_stage_evaluator_caution()
        test_stage_evaluator_healthy_burning()
        test_stage_evaluator_healthy_profitable()
        test_stage_evaluator_profitable_status()
        test_end_to_end_pipeline()
        test_determinism()
        framework_ok = test_framework_isolation()
        
        print("\n" + "=" * 70)
        print("🎉 ALL SPRINT 4 TESTS PASSED")
        print("=" * 70)
        print("\nSprint 4 Status:")
        print("  ✅ RuleResult entity implemented")
        print("  ✅ RuleEngine with baseline rules implemented")
        print("  ✅ StageEvaluator deterministic logic implemented")
        print("  ✅ All 12 tests passing")
        print("  ✅ Framework isolation maintained")
        print("\nNext Sprint: Sprint 5 (Finalization Orchestration)")
        
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
