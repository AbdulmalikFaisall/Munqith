"""Stage evaluation engine for Sprint 4.

Deterministic stage evaluation from rule results.
Pure business logic - no DB calls, no external state.
"""
from typing import List
from typing import Optional

from app.domain.entities.rule_result import RuleResult
from app.domain.enums import Stage


class StageEvaluator:
    """
    Stage evaluation engine.
    
    Responsibilities:
    - Accept list of rule results
    - Determine company stage deterministically
    - Return final Stage enum value
    - Never mutate rule results
    - Never access database
    
    Requirements:
    - Deterministic (same rule results → same stage)
    - Pure function behavior
    - No external state
    - No circular dependencies
    
    Stage Logic (Sprint 4 Baseline - v1):
    Mapping rule combinations to stages:
    - HIGH_RISK → IDEA
    - CAUTION → PRE_SEED
    - HEALTHY + BURNING → SEED
    - HEALTHY + PROFITABLE → SERIES_A
    - PROFITABLE + HEALTHY → SERIES_A or GROWTH (depending on context)
    
    Philosophy:
    - Keep logic explicit and readable
    - No magic thresholds
    - Easy to audit and modify
    - Each branch clearly documented
    """
    
    @staticmethod
    def determine(rule_results: List[RuleResult]) -> Optional[Stage]:
        """
        Determine company stage from rule results.
        
        This is a pure function: same rule results → same stage always.
        Does not access database or depend on external state.
        
        Args:
            rule_results: List of RuleResult objects from RuleEngine
            
        Returns:
            Stage enum value, or None if cannot be determined
            
        Raises:
            TypeError: If rule_results is not a list or contains invalid items
        """
        if not isinstance(rule_results, list):
            raise TypeError(f"rule_results must be a list, got {type(rule_results)}")
        
        for result in rule_results:
            if not isinstance(result, RuleResult):
                raise TypeError(f"All items must be RuleResult, got {type(result)}")
        
        # Extract rule results into a lookup map for easy checking
        result_map = {}
        for rule_result in rule_results:
            result_map[rule_result.rule_name] = rule_result.result
        
        # Extract individual classifications
        runway_risk = result_map.get("RunwayRiskRule")
        profitability = result_map.get("ProfitabilityRule")
        
        # Stage determination logic
        # Uses explicit, readable conditional logic
        
        # If runway is HIGH_RISK → Stage is IDEA
        # (Company is in critical danger, earliest intervention stage)
        if runway_risk == "HIGH_RISK":
            return Stage.IDEA
        
        # If runway is CAUTION → Stage is PRE_SEED
        # (Company needs capital soon, pre-seed/seed stage thinking)
        if runway_risk == "CAUTION":
            return Stage.PRE_SEED
        
        # If runway is HEALTHY (> 12 months):
        if runway_risk == "HEALTHY":
            # If still burning cash → SEED stage
            # (Has capital but still in high burn, growth phase)
            if profitability == "BURNING":
                return Stage.SEED
            
            # If profitable → SERIES_A stage
            # (Strong unit economics, scaling phase)
            if profitability == "PROFITABLE":
                return Stage.SERIES_A
        
        # If already PROFITABLE (no runway concern):
        if runway_risk == "PROFITABLE":
            # If also burning (shouldn't happen, but edge case) → SEED
            if profitability == "BURNING":
                return Stage.SEED
            
            # If profitable and healthy → SERIES_A
            # (Healthy, profitable, sustainable business)
            if profitability == "PROFITABLE":
                return Stage.SERIES_A
        
        # If cannot determine → return None
        # (Missing required signals or unknown classification)
        return None
