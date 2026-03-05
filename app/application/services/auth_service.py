"""Authentication service for password operations."""
from passlib.context import CryptContext
from typing import Tuple
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

# Password hashing context using PBKDF2 (more stable than bcrypt)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


class AuthService:
    """
    Authentication service.
    
    Responsibilities:
    - Hash passwords using bcrypt
    - Verify passwords against hashes
    - Create JWT tokens
    - Validate JWT tokens
    """
    
    # JWT configuration
    # NOTE: SECRET_KEY MUST be set via environment variable
    # DO NOT use default value in production
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        env = os.getenv("ENV", "development")
        if env == "production":
            raise ValueError(
                "CRITICAL: SECRET_KEY environment variable is required in production. "
                "Set SECRET_KEY to a strong random string."
            )
        # Development default (never use in production)
        SECRET_KEY = "dev-key-change-in-production"
    
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain password using bcrypt.
        
        Args:
            password: Plain password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hash.
        
        Args:
            plain_password: Plain password from user
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @classmethod
    def create_access_token(cls, user_id: str, role: str) -> str:
        """
        Create JWT access token.
        
        Args:
            user_id: User UUID
            role: User role (ANALYST or ADMIN)
            
        Returns:
            JWT token
        """
        payload = {
            "sub": user_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def decode_token(cls, token: str) -> dict:
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Token payload (sub, role, exp)
            
        Raises:
            JWTError: If token is invalid or expired
        """
        return jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
