from fastapi import APIRouter
from app.api.v1.endpoints import health, timeline, compare, trends

router = APIRouter()

# Include health endpoints
router.include_router(health.router, tags=["health"])

# Include timeline endpoints (Sprint 6)
router.include_router(timeline.router, tags=["timeline"])

# Include compare endpoints (Sprint 6)
router.include_router(compare.router, tags=["compare"])

# Include trends endpoints (Sprint 7)
router.include_router(trends.router, tags=["trends"])


