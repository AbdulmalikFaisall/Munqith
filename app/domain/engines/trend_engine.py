"""Trend engine for time-series analysis of company financials.

Builds deterministic time-series data and basic trend indicators.
Domain layer - pure Python, no DB calls, no framework imports.
"""
from typing import List, Optional, Dict
from decimal import Decimal

from app.domain.entities.snapshot import Snapshot


class TrendEngine:
    """
    Time-series trend analysis engine.
    
    Responsibilities:
    - Build time-series from snapshots
    - Compute revenue growth % deterministically
    - Identify basic trend indicators
    - Handle edge cases (None values, zero divisions)
    
    Constraints:
    - Domain layer only (no DB, no FastAPI, no SQLAlchemy)
    - Linear time complexity for all operations
    - Works with any number of snapshots
    - Deterministic (same input = same output)
    """
    
    @staticmethod
    def build_time_series(snapshots: List[Snapshot]) -> Dict:
        """
        Build time-series data and trend indicators from snapshots.
        
        Given finalized snapshots (already chronologically ordered),
        produces time-series with growth calculations and trend indicators.
        
        Args:
            snapshots: List of Snapshot entities, ordered by snapshot_date ASC
                      (Must be finalized snapshots only - caller responsibility)
                      
        Returns:
            Dictionary with:
            {
                "time_series": [
                    {
                        "date": "2026-01-15",
                        "runway_months": 5.00,
                        "monthly_burn": 40000.00,
                        "monthly_revenue": 10000.00,
                        "revenue_growth_percent": null  # First snapshot
                    },
                    {
                        "date": "2026-02-15",
                        "runway_months": 6.00,
                        "monthly_burn": 35000.00,
                        "monthly_revenue": 15000.00,
                        "revenue_growth_percent": 50.00  # (15k - 10k) / 10k * 100
                    },
                    ...
                ],
                "indicators": {
                    "revenue_trend": "UP",  # UP/DOWN/FLAT
                    "burn_trend": "DOWN",
                    "runway_trend": "UP"
                },
                "snapshot_count": 3
            }
        """
        if not snapshots:
            return {
                "time_series": [],
                "indicators": {
                    "revenue_trend": None,
                    "burn_trend": None,
                    "runway_trend": None
                },
                "snapshot_count": 0
            }
        
        # Build time-series data points
        time_series = []
        previous_revenue = None
        
        for snapshot in snapshots:
            # Get metric values (safe for None)
            runway = float(snapshot.runway_months) if snapshot.runway_months else None
            burn = float(snapshot.monthly_burn) if snapshot.monthly_burn else None
            revenue = float(snapshot.monthly_revenue) if snapshot.monthly_revenue else None
            
            # Calculate revenue growth %
            revenue_growth = TrendEngine._calculate_growth(revenue, previous_revenue)
            
            # Build data point
            data_point = {
                "date": snapshot.snapshot_date.isoformat(),
                "runway_months": runway,
                "monthly_burn": burn,
                "monthly_revenue": revenue,
                "revenue_growth_percent": revenue_growth
            }
            
            time_series.append(data_point)
            
            # Update previous for next iteration
            previous_revenue = revenue
        
        # Compute trend indicators from last 3 snapshots
        indicators = TrendEngine._compute_indicators(time_series)
        
        return {
            "time_series": time_series,
            "indicators": indicators,
            "snapshot_count": len(snapshots)
        }
    
    @staticmethod
    def _calculate_growth(
        current_value: Optional[float],
        previous_value: Optional[float]
    ) -> Optional[float]:
        """
        Calculate percentage growth between two values.
        
        Formula: (current - previous) / previous * 100
        
        Returns None if:
        - Either value is None
        - Previous value is 0 (division by zero)
        
        Args:
            current_value: Current metric value
            previous_value: Previous metric value
            
        Returns:
            Growth percentage (rounded to 2 decimals) or None
        """
        if current_value is None or previous_value is None:
            return None
        
        if previous_value == 0:
            return None
        
        growth = ((current_value - previous_value) / previous_value) * 100
        
        # Round to 2 decimals for determinism
        return round(growth, 2)
    
    @staticmethod
    def _compute_indicators(time_series: List[Dict]) -> Dict[str, Optional[str]]:
        """
        Compute trend indicators from time-series.
        
        Indicators:
        - revenue_trend: UP/DOWN/FLAT based on last 3 revenues
        - burn_trend: UP/DOWN/FLAT based on last 3 burns
        - runway_trend: UP/DOWN/FLAT based on last 3 runways
        
        Rules:
        - Need at least 2 data points for UP/DOWN (strict increase/decrease)
        - If fewer than 2 points, return None
        - Ignore None values (skip them)
        
        Args:
            time_series: List of data point dictionaries
            
        Returns:
            Dictionary with trend indicators (or None if insufficient data)
        """
        indicators = {
            "revenue_trend": None,
            "burn_trend": None,
            "runway_trend": None
        }
        
        if len(time_series) < 2:
            return indicators
        
        # Get last 3 data points
        last_n = min(3, len(time_series))
        recent_points = time_series[-last_n:]
        
        # Extract values, filtering None
        revenues = [p["monthly_revenue"] for p in recent_points if p["monthly_revenue"] is not None]
        burns = [p["monthly_burn"] for p in recent_points if p["monthly_burn"] is not None]
        runways = [p["runway_months"] for p in recent_points if p["runway_months"] is not None]
        
        # Determine trends
        if len(revenues) >= 2:
            indicators["revenue_trend"] = TrendEngine._determine_trend(revenues)
        
        if len(burns) >= 2:
            indicators["burn_trend"] = TrendEngine._determine_trend(burns)
        
        if len(runways) >= 2:
            indicators["runway_trend"] = TrendEngine._determine_trend(runways)
        
        return indicators
    
    @staticmethod
    def _determine_trend(values: List[float]) -> str:
        """
        Determine trend direction from sequence of values.
        
        Rules:
        - UP: Strictly increasing (each value > previous)
        - DOWN: Strictly decreasing (each value < previous)
        - FLAT: Otherwise (same, mixed, etc)
        
        Args:
            values: List of numeric values (already filtered for None)
            
        Returns:
            "UP", "DOWN", or "FLAT"
        """
        if len(values) < 2:
            return "FLAT"
        
        # Check if strictly increasing
        is_increasing = all(values[i] < values[i + 1] for i in range(len(values) - 1))
        if is_increasing:
            return "UP"
        
        # Check if strictly decreasing
        is_decreasing = all(values[i] > values[i + 1] for i in range(len(values) - 1))
        if is_decreasing:
            return "DOWN"
        
        return "FLAT"
