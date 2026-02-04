from fastapi import FastAPI

from .api.v1 import router as api_router
from .core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"])
def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
