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


class RegisterRequest(BaseModel):
    """Register request model."""
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


@router.post("/auth/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: Session = Depends(get_db)
):
    """
    Register endpoint.

    Creates a new ANALYST user and returns a JWT token.
    """
    email = request.email.strip().lower()
    password = request.password

    if not email or "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid email is required"
        )

    if not password or len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters"
        )

    repo = UserRepository(session)
    existing = repo.get_by_email(email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_password = AuthService.hash_password(password)
    user = repo.create_user(email=email, hashed_password=hashed_password, role="ANALYST")

    access_token = AuthService.create_access_token(
        user_id=user["id"],
        role=user["role"]
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer"
    )
