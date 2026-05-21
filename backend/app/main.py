"""
FastAPI Application Entry Point.
Configures CORS, includes all routers, and initializes the database on startup.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.init_db import init_db
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.invigilator import router as invigilator_router
from app.api.student import router as student_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    print(f"[STARTUP] {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    yield
    print("[SHUTDOWN] Application shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart web-based system to manage exam seating arrangements, scheduling, and monitoring.",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(invigilator_router)
app.include_router(student_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
