"""Authentication and authorization dependencies for FastAPI."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError

from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.application.services.auth_service import AuthService
from app.domain.enums import UserRole

security = HTTPBearer()


async def get_current_user(
    credentials=Depends(security),
    session=Depends(get_db)
) -> dict:
    """
    Validate JWT token and load current user.
    
    Called on protected endpoints to ensure:
    1. Valid JWT token
    2. Token not expired
    3. User exists and is active
    
    Args:
        credentials: HTTP Bearer credentials
        session: Database session
        
    Returns:
        User dict with id, email, role, is_active
        
    Raises:
        HTTPException 401: If token invalid, expired, or user not found/inactive
    """
    token = credentials.credentials
    
    try:
        # Decode and validate token
        payload = AuthService.decode_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Load user from database
    repo = UserRepository(session)
    user = repo.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive"
        )
    
    return user


def require_role(required_role: UserRole):
    """
    Dependency factory for role-based access control.
    
    Returns a dependency that checks if current user has required role.
    
    Args:
        required_role: Required UserRole
        
    Returns:
        Dependency function
        
    Example:
        @app.post("/admin/endpoint")
        def admin_endpoint(user=Depends(require_role(UserRole.ADMIN))):
            ...
    """
    async def check_role(user: dict = Depends(get_current_user)) -> dict:
        """
        Check if user has required role.
        
        Args:
            user: Current user from get_current_user
            
        Returns:
            User dict if authorized
            
        Raises:
            HTTPException 403: If user does not have required role
        """
        if user["role"] != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You must be {required_role.value} to access this resource"
            )
        
        return user
    
    return check_role
