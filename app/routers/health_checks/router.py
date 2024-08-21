from fastapi import FastAPI, APIRouter

from .health_checks import router as sample_routes_router


def include_router(app: FastAPI):
    api_router = APIRouter()
    api_router.include_router(sample_routes_router, prefix='', tags=['Health Check'])
    app.include_router(api_router, prefix='/health-check')
