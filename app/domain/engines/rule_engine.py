"""Rule evaluation engine for Sprint 4.

Deterministic rule engine that interprets signals and produces rule results.
Pure business logic - no DB calls, no external state.
"""
from typing import List

from app.domain.entities.signal import Signal
from app.domain.entities.rule_result import RuleResult
from app.domain.enums.signal_category import SignalCategory


class RuleEngine:
    """
    Rule evaluation engine.
    
    Responsibilities:
    - Accept list of signals
    - Apply deterministic rules
    - Return rule results
    - Never modify signals
    - Never access database
    
    Requirements:
    - Deterministic (same signals → same results)
    - Pure function behavior
    - No external state
    - No circular dependencies
    
    Rules Implemented (Sprint 4):
    1. RunwayRiskRule: Interpret RunwayRisk signal
    2. ProfitabilityRule: Interpret MonthlyBurn signal
    """
    
    @staticmethod
    def evaluate(signals: List[Signal]) -> List[RuleResult]:
        """
        Evaluate signals using deterministic rules.
        
        This is a pure function: same signals → same rule results always.
        Does not access database, modify signals, or depend on external state.
        
        Args:
            signals: List of Signal objects to evaluate
            
        Returns:
            List of RuleResult objects from rule evaluation
            
        Raises:
            TypeError: If signals is not a list or contains non-Signal items
        """
        if not isinstance(signals, list):
            raise TypeError(f"signals must be a list, got {type(signals)}")
        
        for signal in signals:
            if not isinstance(signal, Signal):
                raise TypeError(f"All items must be Signal, got {type(signal)}")
        
        rule_results: List[RuleResult] = []
        
        # Build signal lookup for quick access by name
        signal_map = {signal.name: signal for signal in signals}
        
        # Rule 1: Runway Risk Rule
        # Interpret the RunwayRisk signal (RISK category)
        rule_1_result = RuleEngine._evaluate_runway_risk_rule(signal_map)
        if rule_1_result:
            rule_results.append(rule_1_result)
        
        # Rule 2: Profitability Rule
        # Interpret the MonthlyBurn signal (FINANCIAL category)
        rule_2_result = RuleEngine._evaluate_profitability_rule(signal_map)
        if rule_2_result:
            rule_results.append(rule_2_result)
        
        return rule_results
    
    @staticmethod
    def _evaluate_runway_risk_rule(signal_map: dict) -> RuleResult:
        """
        RunwayRiskRule: Interpret RunwayRisk signal to determine runway status.
        
        Input: RunwayRisk signal (RISK category)
        
        Mapping:
        - value == 3 → HIGH_RISK (runway < 6 months)
        - value == 2 → CAUTION (6 ≤ runway ≤ 12 months)
        - value == 1 → HEALTHY (runway > 12 months)
        - value == 0 → PROFITABLE (no runway concern)
        
        Args:
            signal_map: Dictionary of signal_name -> Signal
            
        Returns:
            RuleResult for runway risk classification, or None if signal missing
        """
        if "RunwayRisk" not in signal_map:
            return None
        
        signal = signal_map["RunwayRisk"]
        risk_value = int(signal.value)
        
        if risk_value == 3:
            result = "HIGH_RISK"
        elif risk_value == 2:
            result = "CAUTION"
        elif risk_value == 1:
            result = "HEALTHY"
        elif risk_value == 0:
            result = "PROFITABLE"
        else:
            # Fallback for unexpected values
            result = "UNKNOWN"
        
        return RuleResult(
            rule_name="RunwayRiskRule",
            result=result,
        )
    
    @staticmethod
    def _evaluate_profitability_rule(signal_map: dict) -> RuleResult:
        """
        ProfitabilityRule: Interpret MonthlyBurn signal to assess profitability.
        
        Input: MonthlyBurn signal (FINANCIAL category)
        
        Logic:
        - If burn <= 0 (profit or break-even) → PROFITABLE
        - If burn > 0 (losing money) → BURNING
        
        Args:
            signal_map: Dictionary of signal_name -> Signal
            
        Returns:
            RuleResult for profitability status, or None if signal missing
        """
        if "MonthlyBurn" not in signal_map:
            return None
        
        signal = signal_map["MonthlyBurn"]
        burn_value = float(signal.value)
        
        if burn_value <= 0:
            result = "PROFITABLE"
        else:
            result = "BURNING"
        
        return RuleResult(
            rule_name="ProfitabilityRule",
            result=result,
        )
