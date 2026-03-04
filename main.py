"""
TaskVerse — User Task Management API
Main application entry point with CORS, structured logging, and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from logging_config import setup_logging
from routes.task_routes import router as task_router
from routes.user_routes import router as user_router
from routes.auth_routes import router as auth_router

# ── Logging ───────────────────────────────────────────────
setup_logging(debug=settings.debug)

# ── App ───────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description=(
        "A professional task management API built with FastAPI, "
        "featuring JWT authentication, pagination, filtering, "
        "tags, subtasks, and analytics."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])


@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }