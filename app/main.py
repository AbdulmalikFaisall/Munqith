from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

# Initialize logging early
from app.infrastructure.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

from app.api.v1 import router as v1_router

app = FastAPI(
    title="Munqith",
    description="Deterministic Financial Intelligence Platform for KSA Startups",
    version="1.0.0"
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(v1_router.router, prefix="/api/v1", tags=["v1"])

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    logger.debug("Health check requested")
    return JSONResponse(
        status_code=200,
        content={"status": "ok"}
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Munqith application")
    uvicorn.run(app, host="0.0.0.0", port=8000)
