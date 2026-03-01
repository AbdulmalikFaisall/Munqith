"""
Financial validator for snapshot sanity checks.

Pure business logic - no DB calls, no frameworks.
Deterministic validation rules for financial data.
"""
from decimal import Decimal
from typing import Optional
from app.domain.entities.snapshot import Snapshot
from app.domain.exceptions import FinancialSanityError


class FinancialValidator:
    """
    Validator for financial attributes in snapshots.
    
    Enforces:
    - Non-negative values for cash, revenue, costs
    - Logical consistency (costs and revenue must be non-negative)
    - Extreme value guards (configurable thresholds)
    
    All validation is deterministic and framework-independent.
    """
    
    # Configurable thresholds for extreme value detection
    # These are SAR amounts that would be unrealistic for startups
    MAX_CASH_BALANCE = Decimal("1e12")  # 1 trillion SAR
    MAX_MONTHLY_REVENUE = Decimal("1e12")  # 1 trillion SAR
    MAX_MONTHLY_COSTS = Decimal("1e12")  # 1 trillion SAR
    
    @classmethod
    def validate_snapshot_inputs(cls, snapshot: Snapshot) -> None:
        """
        Validate financial inputs of a snapshot.
        
        Enforces:
        1. Cash balance is non-negative
        2. Monthly revenue is non-negative
        3. Operating costs is non-negative
        4. No extreme/unrealistic values
        
        Args:
            snapshot: Snapshot entity to validate
            
        Raises:
            FinancialSanityError: If validation fails
        """
        # Validate cash balance
        if snapshot.cash_balance is not None:
            cls._validate_cash_balance(snapshot.cash_balance)
        
        # Validate monthly revenue
        if snapshot.monthly_revenue is not None:
            cls._validate_monthly_revenue(snapshot.monthly_revenue)
        
        # Validate operating costs
        if snapshot.operating_costs is not None:
            cls._validate_operating_costs(snapshot.operating_costs)
    
    @classmethod
    def _validate_cash_balance(cls, cash_balance: Decimal) -> None:
        """
        Validate cash balance is non-negative and realistic.
        
        Args:
            cash_balance: Cash balance amount in SAR
            
        Raises:
            FinancialSanityError: If validation fails
        """
        if cash_balance < 0:
            raise FinancialSanityError(
                field="cash_balance",
                value=cash_balance,
                reason="Cash balance cannot be negative."
            )
        
        if cash_balance > cls.MAX_CASH_BALANCE:
            raise FinancialSanityError(
                field="cash_balance",
                value=cash_balance,
                reason=f"Cash balance exceeds realistic threshold ({cls.MAX_CASH_BALANCE} SAR)."
            )
    
    @classmethod
    def _validate_monthly_revenue(cls, monthly_revenue: Decimal) -> None:
        """
        Validate monthly revenue is non-negative and realistic.
        
        Args:
            monthly_revenue: Monthly revenue amount in SAR
            
        Raises:
            FinancialSanityError: If validation fails
        """
        if monthly_revenue < 0:
            raise FinancialSanityError(
                field="monthly_revenue",
                value=monthly_revenue,
                reason="Monthly revenue cannot be negative."
            )
        
        if monthly_revenue > cls.MAX_MONTHLY_REVENUE:
            raise FinancialSanityError(
                field="monthly_revenue",
                value=monthly_revenue,
                reason=f"Monthly revenue exceeds realistic threshold ({cls.MAX_MONTHLY_REVENUE} SAR)."
            )
    
    @classmethod
    def _validate_operating_costs(cls, operating_costs: Decimal) -> None:
        """
        Validate operating costs is non-negative and realistic.
        
        Args:
            operating_costs: Monthly operating costs in SAR
            
        Raises:
            FinancialSanityError: If validation fails
        """
        if operating_costs < 0:
            raise FinancialSanityError(
                field="operating_costs",
                value=operating_costs,
                reason="Operating costs cannot be negative."
            )
        
        if operating_costs > cls.MAX_MONTHLY_COSTS:
            raise FinancialSanityError(
                field="operating_costs",
                value=operating_costs,
                reason=f"Operating costs exceeds realistic threshold ({cls.MAX_MONTHLY_COSTS} SAR)."
            )
