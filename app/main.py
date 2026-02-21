from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.v1 import router as v1_router

app = FastAPI(
    title="Munqith",
    description="Deterministic Financial Intelligence Platform for KSA Startups",
    version="0.1.0"
)

# Include routers
app.include_router(v1_router.router, prefix="/api/v1", tags=["v1"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={"status": "ok"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
