from fastapi import FastAPI, APIRouter

from .authorization_examples import router as authorization_examples_routes_router


def include_router(app: FastAPI):
    api_router = APIRouter()
    api_router.include_router(authorization_examples_routes_router, prefix='', tags=['Authorization Examples'])
    app.include_router(api_router, prefix='/authorization-examples')
