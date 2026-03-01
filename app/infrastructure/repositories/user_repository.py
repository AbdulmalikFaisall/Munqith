"""User repository for persistence layer."""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.infrastructure.db.models.user import User as UserModel
from app.domain.enums import UserRole


class UserRepository:
    """
    Repository for user persistence and queries.
    
    Responsibilities:
    - Load users from database
    - Save users to database
    - Query by email
    - Query by ID
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.session = session
    
    def get_by_email(self, email: str) -> Optional[dict]:
        """
        Load user by email.
        
        Args:
            email: User email
            
        Returns:
            User dict with id, email, hashed_password, role, is_active or None
        """
        model = self.session.query(UserModel).filter(
            UserModel.email == email
        ).first()
        
        if not model:
            return None
        
        return self._model_to_dict(model)
    
    def get_by_id(self, user_id: UUID) -> Optional[dict]:
        """
        Load user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User dict with id, email, role, is_active or None
        """
        model = self.session.query(UserModel).filter(
            UserModel.id == str(user_id)
        ).first()
        
        if not model:
            return None
        
        return self._model_to_dict(model)
    
    def create_user(
        self,
        email: str,
        hashed_password: str,
        role: str = "ANALYST"
    ) -> dict:
        """
        Create a new user.
        
        Args:
            email: User email (must be unique)
            hashed_password: Hashed password
            role: User role (ANALYST or ADMIN)
            
        Returns:
            User dict with id, email, role, is_active
            
        Raises:
            Exception: If email already exists or database error
        """
        try:
            user = UserModel(
                email=email,
                hashed_password=hashed_password,
                role=role,
                is_active=True
            )
            self.session.add(user)
            self.session.commit()
            
            return self._model_to_dict(user)
        
        except Exception:
            self.session.rollback()
            raise
    
    @staticmethod
    def _model_to_dict(model: UserModel) -> dict:
        """
        Convert ORM model to dictionary.
        
        Args:
            model: ORM UserModel
            
        Returns:
            Dictionary with user data
        """
        return {
            "id": str(model.id),
            "email": model.email,
            "hashed_password": model.hashed_password,
            "role": model.role,
            "is_active": model.is_active,
        }
