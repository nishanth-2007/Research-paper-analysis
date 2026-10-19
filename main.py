import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import *  # Import all models to register with Base
from app.api.v1 import api_router
from app.api.v1.journals import ensure_journals_seeded

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("research_platform")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and journals are seeded
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        ensure_journals_seeded(db)
        logger.info("Official journal knowledge base seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding journal knowledge base: {e}")
    finally:
        db.close()

    yield
    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-minded AI-powered research paper automation and journal-readiness platform. "
        "Coordinates parallel Deterministic Verification, Isolated Journal Knowledge Base (RAG), "
        "and Academic Quality Evaluation (LLM) to produce explainable readiness scores and official reports."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dir = Path(__file__).parent / "frontend"
dist_dir = frontend_dir / "dist"

if (dist_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")

if (frontend_dir / "css").exists():
    app.mount("/css", StaticFiles(directory=frontend_dir / "css"), name="css")
if (frontend_dir / "js").exists():
    app.mount("/js", StaticFiles(directory=frontend_dir / "js"), name="js")


@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path == "/" or path.endswith((".js", ".css", ".html")):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


@app.get("/", include_in_schema=False)
def serve_frontend_ui():
    dist_index = dist_dir / "index.html"
    if dist_index.exists():
        return FileResponse(
            dist_index,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(
            index_file,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    return JSONResponse(content={"platform": settings.APP_NAME, "status": "operational"})


@app.get("/api-info", tags=["Root"])
def root_info():
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "documentation": "/docs",
        "api_v1_prefix": settings.API_V1_PREFIX,
        "capabilities": [
            "Deterministic citation-to-reference matching",
            "Missing required manuscript sections & word counts",
            "Figure & table numbering, captions & mentions cross-check",
            "Isolated Journal RAG guideline compliance verification",
            "LLM qualitative academic rigor, novelty & validity evaluation",
            "Explainable 0-100 readiness scoring with category deductions",
            "Downloadable PDF and DOCX publication audit reports",
        ],
    }


@app.get("/{full_path:path}", include_in_schema=False)
def catch_all_spa(full_path: str):
    if (
        full_path.startswith("api/")
        or full_path.startswith("docs")
        or full_path.startswith("redoc")
        or full_path.startswith("openapi.json")
        or full_path.startswith("assets/")
        or full_path.startswith("css/")
        or full_path.startswith("js/")
    ):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    dist_index = dist_dir / "index.html"
    if dist_index.exists():
        return FileResponse(dist_index)
    return JSONResponse(content={"platform": settings.APP_NAME, "status": "operational"})


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 10000))
    is_debug = os.environ.get("DEBUG", "false").lower() == "true"
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=is_debug)
