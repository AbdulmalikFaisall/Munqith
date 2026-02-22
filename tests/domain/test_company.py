"""
Unit tests for Company domain entity.

These tests verify Company behavior without any framework dependencies.
"""
import pytest
from uuid import uuid4
from datetime import datetime

from app.domain.entities import Company


class TestCompanyCreation:
    """Test Company entity creation and initialization."""
    
    def test_create_company_with_minimal_data(self):
        """Can create company with just id and name."""
        company_id = uuid4()
        company = Company(id=company_id, name="TechStartup")
        
        assert company.id == company_id
        assert company.name == "TechStartup"
        assert company.sector is None
        assert company.created_at is not None
    
    def test_create_company_with_all_data(self):
        """Can create company with all fields."""
        company_id = uuid4()
        now = datetime.utcnow()
        company = Company(
            id=company_id,
            name="TechStartup",
            sector="Technology",
            created_at=now,
            updated_at=now,
        )
        
        assert company.name == "TechStartup"
        assert company.sector == "Technology"
        assert company.created_at == now
    
    def test_company_name_stripped(self):
        """Company name is stripped of whitespace."""
        company = Company(id=uuid4(), name="  TechStartup  ")
        assert company.name == "TechStartup"
    
    def test_company_sector_stripped(self):
        """Company sector is stripped of whitespace."""
        company = Company(
            id=uuid4(),
            name="TechStartup",
            sector="  Technology  "
        )
        assert company.sector == "Technology"


class TestCompanyValidation:
    """Test Company validation rules."""
    
    def test_empty_name_raises_error(self):
        """Cannot create company with empty name."""
        with pytest.raises(ValueError, match="non-empty string"):
            Company(id=uuid4(), name="")
    
    def test_whitespace_only_name_raises_error(self):
        """Cannot create company with whitespace-only name."""
        with pytest.raises(ValueError, match="non-empty string"):
            Company(id=uuid4(), name="   ")
    
    def test_none_name_raises_error(self):
        """Cannot create company with None name."""
        with pytest.raises(ValueError, match="non-empty string"):
            Company(id=uuid4(), name=None)
    
    def test_non_string_name_raises_error(self):
        """Cannot create company with non-string name."""
        with pytest.raises(ValueError, match="non-empty string"):
            Company(id=uuid4(), name=123)


class TestCompanyEquality:
    """Test Company equality and hashing."""
    
    def test_same_id_equals(self):
        """Companies with same ID are equal."""
        company_id = uuid4()
        company1 = Company(id=company_id, name="Company1")
        company2 = Company(id=company_id, name="Company2")
        
        assert company1 == company2
    
    def test_different_id_not_equals(self):
        """Companies with different IDs are not equal."""
        company1 = Company(id=uuid4(), name="Company")
        company2 = Company(id=uuid4(), name="Company")
        
        assert company1 != company2
    
    def test_company_hashable(self):
        """Companies can be used in sets and dicts."""
        company_id = uuid4()
        company = Company(id=company_id, name="Company")
        
        # Should be hashable
        companies_set = {company}
        assert company in companies_set
    
    def test_company_not_equal_to_other_type(self):
        """Company not equal to other types."""
        company = Company(id=uuid4(), name="Company")
        assert company != "Company"
        assert company != 123
        assert company != None


class TestCompanyRepresentation:
    """Test Company string representation."""
    
    def test_repr_format(self):
        """Company repr shows id, name, and sector."""
        company_id = uuid4()
        company = Company(
            id=company_id,
            name="TechStartup",
            sector="Technology"
        )
        repr_str = repr(company)
        
        assert "Company" in repr_str
        assert "TechStartup" in repr_str
        assert "Technology" in repr_str
