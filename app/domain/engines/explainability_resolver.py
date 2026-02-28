"""Explainability resolver for Sprint 5.

Determines which signals contributed to the final stage determination.
Pure business logic - no DB calls, no external state.
"""
from typing import List

from app.domain.entities.signal import Signal
from app.domain.entities.rule_result import RuleResult


class ExplainabilityResolver:
    """
    Explainability resolver.
    
    Responsibilities:
    - Accept signals and rule results
    - Determine which signals influenced the final stage
    - Return contributing signals for transparency
    
    Requirements:
    - Deterministic (same signals/rules → same contributing signals)
    - Pure function behavior
    - No external state
    - No database calls
    
    Purpose:
    - Explain stage decision to investors
    - Provide regulatory transparency
    - Build audit trail
    - Enable stakeholder understanding
    """
    
    @staticmethod
    def resolve(
        signals: List[Signal],
        rule_results: List[RuleResult],
    ) -> List[Signal]:
        """
        Resolve contributing signals from execution pipeline.
        
        This determines which signals actually influenced the stage determination.
        
        Logic:
        - If RunwayRiskRule produced HIGH_RISK or CAUTION → RunwayMonths/RunwayRisk contributed
        - If RunwayRiskRule produced HEALTHY + ProfitabilityRule produced BURNING → RunwayMonths contributed
        - If ProfitabilityRule evaluated → MonthlyBurn contributed
        
        Args:
            signals: List of all signals generated from snapshot
            rule_results: List of all rule results from evaluation
            
        Returns:
            List of contributors - signals that influenced stage
            Empty list if no contributing signals identified
            
        Raises:
            TypeError: If arguments are invalid types
        """
        if not isinstance(signals, list):
            raise TypeError(f"signals must be list, got {type(signals)}")
        
        if not isinstance(rule_results, list):
            raise TypeError(f"rule_results must be list, got {type(rule_results)}")
        
        # Build signal lookup by name
        signal_map = {signal.name: signal for signal in signals}
        
        # Build rule results lookup by name
        result_map = {}
        for result in rule_results:
            result_map[result.rule_name] = result.result
        
        # Track contributing signals
        contributing_signals: List[Signal] = []
        
        # Extract runway and profitability classifications
        runway_risk = result_map.get("RunwayRiskRule")
        profitability = result_map.get("ProfitabilityRule")
        
        # ===================== Decision Logic =====================
        # This mirrors the stage determination logic from StageEvaluator
        # to identify which signals actually affected the outcome.
        
        # HIGH_RISK → IDEA stage
        # RunwayRisk signal was the key contributor
        if runway_risk == "HIGH_RISK":
            if "RunwayRisk" in signal_map:
                contributing_signals.append(signal_map["RunwayRisk"])
            if "RunwayMonths" in signal_map:
                contributing_signals.append(signal_map["RunwayMonths"])
        
        # CAUTION → PRE_SEED stage
        # RunwayRisk signal was the key contributor
        elif runway_risk == "CAUTION":
            if "RunwayRisk" in signal_map:
                contributing_signals.append(signal_map["RunwayRisk"])
            if "RunwayMonths" in signal_map:
                contributing_signals.append(signal_map["RunwayMonths"])
        
        # HEALTHY + BURNING → SEED stage
        # Both runway and burn are contributors
        elif runway_risk == "HEALTHY":
            if profitability == "BURNING":
                if "RunwayMonths" in signal_map:
                    contributing_signals.append(signal_map["RunwayMonths"])
                if "MonthlyBurn" in signal_map:
                    contributing_signals.append(signal_map["MonthlyBurn"])
            
            # HEALTHY + PROFITABLE → SERIES_A stage
            # RunwayMonths shows healthy position, Profitable shows sustainability
            elif profitability == "PROFITABLE":
                if "RunwayMonths" in signal_map:
                    contributing_signals.append(signal_map["RunwayMonths"])
                if "MonthlyBurn" in signal_map:
                    contributing_signals.append(signal_map["MonthlyBurn"])
        
        # PROFITABLE + PROFITABLE → SERIES_A or GROWTH
        # Both signals confirm strong fundamentals
        elif runway_risk == "PROFITABLE":
            if profitability == "PROFITABLE":
                if "MonthlyBurn" in signal_map:
                    contributing_signals.append(signal_map["MonthlyBurn"])
                # Also include runway if available for context
                if "RunwayMonths" in signal_map:
                    contributing_signals.append(signal_map["RunwayMonths"])
        
        return contributing_signals
