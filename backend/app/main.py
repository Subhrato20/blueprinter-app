"""Blueprint Snap Backend - FastAPI application with LangGraph orchestration."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import ask, cursor_link, plan, plan_patch
from app.supabase_client import get_supabase_client

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting Blueprint Snap Backend")
    
    # Initialize Supabase client
    await get_supabase_client()
    
    yield
    
    logger.info("Shutting down Blueprint Snap Backend")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Blueprint Snap API",
        description="Dev DNA Edition: One-line idea → Plan JSON + style-adapted scaffolds + Ask-Copilot + Cursor deep link",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.localhost"],
    )

    # Include routers
    app.include_router(plan.router, prefix="/api", tags=["plan"])
    app.include_router(ask.router, prefix="/api", tags=["ask"])
    app.include_router(plan_patch.router, prefix="/api", tags=["plan-patch"])
    app.include_router(cursor_link.router, prefix="/api", tags=["cursor-link"])

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "blueprint-snap-backend"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true",
    )
