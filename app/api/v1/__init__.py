from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.manuscripts import router as manuscripts_router
from app.api.v1.journals import router as journals_router
from app.api.v1.analysis import router as analysis_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(manuscripts_router)
api_router.include_router(journals_router)
api_router.include_router(analysis_router)

__all__ = ["api_router"]
