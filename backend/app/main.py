"""FastAPI application entry point for PickGuard AI backend API."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import router as api_v1_router
from backend.app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Evidence-Grounded Pick Exception Resolution Agent API",
    version="1.0.0",
)

# Configure CORS Middleware for local frontend development
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_v1_router)


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "app": settings.app_name, "environment": settings.environment}
