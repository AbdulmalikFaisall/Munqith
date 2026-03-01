"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.application.services.auth_service import AuthService

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str


@router.post("/auth/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: Session = Depends(get_db)
):
    """
    Login endpoint.
    
    Authenticates user with email and password.
    Returns JWT access token on success.
    
    Args:
        request: LoginRequest with email and password
        session: Database session
        
    Returns:
        LoginResponse with access_token and token_type
        
    Raises:
        HTTPException 401: If email not found or password incorrect
    """
    # Load user from database
    repo = UserRepository(session)
    user = repo.get_by_email(request.email)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not AuthService.verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive"
        )
    
    # Create JWT token
    access_token = AuthService.create_access_token(
        user_id=user["id"],
        role=user["role"]
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer"
    )
