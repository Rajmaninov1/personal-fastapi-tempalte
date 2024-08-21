from fastapi import FastAPI, APIRouter

from .db_examples import router as db_examples_routes_router


def include_router(app: FastAPI):
    api_router = APIRouter()
    api_router.include_router(db_examples_routes_router, prefix='', tags=['DB Examples'])
    app.include_router(api_router, prefix='/db-examples')
