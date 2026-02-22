"""
Company domain entity.

Represents a Saudi-based startup company.
Pure business logic - no DB calls, no HTTP, no frameworks.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID


class Company:
    """
    Company entity - represents a startup company.
    
    Responsibilities:
    - Hold company metadata
    - No financial logic
    - No stage storage
    - No snapshot calculations
    """
    
    def __init__(
        self,
        id: UUID,
        name: str,
        sector: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """
        Initialize a Company entity.
        
        Args:
            id: Unique identifier (UUID)
            name: Company name
            sector: Business sector (optional)
            created_at: Creation timestamp
            updated_at: Last update timestamp
            
        Raises:
            ValueError: If name is empty or invalid
        """
        if not name or not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Company name must be a non-empty string")
        
        self.id = id
        self.name = name.strip()
        self.sector = sector.strip() if sector else None
        self.created_at = created_at
        self.updated_at = updated_at
    
    def __repr__(self) -> str:
        return f"Company(id={self.id}, name='{self.name}', sector='{self.sector}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Company):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
