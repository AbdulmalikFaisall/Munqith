"""
Stage enumeration for company development stages.

These values match exactly with database stage_definitions table.
"""
from enum import Enum


class Stage(str, Enum):
    """Company development stage - string-based enum for JSON serialization."""
    
    IDEA = "IDEA"
    PRE_SEED = "PRE_SEED"
    SEED = "SEED"
    SERIES_A = "SERIES_A"
    GROWTH = "GROWTH"

    def __str__(self) -> str:
        return self.value
