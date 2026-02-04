from fastapi import APIRouter

from ..models.user import User
from ..services.user_service import get_users

router = APIRouter()


@router.get("/users", response_model=list[User])
def list_users():
    """Return a small list of example users."""
    return get_users()
