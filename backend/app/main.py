import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import init_db
from app.api import practice, exam, suggestions, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite schema
    init_db()
    # Check if DB has exercises, if not auto-seed from seeds directory
    try:
        from sqlmodel import Session, select, func
        from app.database import engine
        from app.models import Exercise
        from scripts.seed import seed_database
        with Session(engine) as session:
            count = session.exec(select(func.count(Exercise.id))).one()
            if count == 0:
                print("Database is empty. Automatically running seed...")
                seed_database()
            else:
                print(f"Database ready with {count} exercises.")
    except Exception as e:
        print(f"Startup check warning: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(practice.router)
app.include_router(exam.router)
app.include_router(suggestions.router)
app.include_router(admin.router)

# Static file serving for Vue 3 frontend
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"])
    async def serve_vue_app(full_path: str):
        # Don't intercept API paths
        if full_path.startswith("api"):
            return None
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def index_placeholder():
        return {
            "message": "Cambridge B2 First Practice API is running.",
            "docs_url": "/docs",
            "frontend_status": "Build frontend with 'npm run build' inside frontend/"
        }
