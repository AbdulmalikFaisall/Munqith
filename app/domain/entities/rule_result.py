"""Rule result domain entity for Sprint 4 Rule Engine."""
from typing import Optional
from datetime import datetime
from uuid import UUID
import uuid


class RuleResult:
    """
    RuleResult entity - represents the output of a deterministic rule.
    
    A RuleResult captures:
    - Which rule was evaluated
    - What classification was produced
    - When it was created
    
    Purpose:
    - Input to Stage Evaluator
    - Record of rule evaluation
    - Explanation material for decisions
    
    Properties:
    - Immutable (created once, never changed)
    - Hashable (can use in sets/dicts)
    - Pure data structure (no logic)
    """
    
    def __init__(
        self,
        rule_name: str,
        result: str,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
    ):
        """
        Initialize a RuleResult entity.
        
        Args:
            rule_name: Name of the rule that produced this result
                      Examples: "RunwayRiskRule", "ProfitabilityRule"
            result: Classification result as string
                   Examples: "HIGH_RISK", "CAUTION", "HEALTHY", "PROFITABLE"
            id: Unique identifier (UUID, optional - auto-generated if not provided)
            created_at: Timestamp of creation (optional - auto-generated if not provided)
            
        Raises:
            ValueError: If rule_name or result are empty
            TypeError: If types are invalid
        """
        if not isinstance(rule_name, str) or len(rule_name.strip()) == 0:
            raise ValueError("rule_name must be a non-empty string")
        
        if not isinstance(result, str) or len(result.strip()) == 0:
            raise ValueError("result must be a non-empty string")
        
        self.id = id or uuid.uuid4()
        self.rule_name = rule_name.strip()
        self.result = result.strip()
        self.created_at = created_at or datetime.utcnow()
    
    # ==================== Utilities ====================
    
    def __repr__(self) -> str:
        return (
            f"RuleResult(rule_name={self.rule_name!r}, "
            f"result={self.result!r}, id={self.id})"
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, RuleResult):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
