from fastapi import APIRouter
from app.api.v1.endpoints import health

router = APIRouter()

# Include health endpoints
router.include_router(health.router, tags=["health"])
