from fastapi import FastAPI

from .health_checks.router import include_router as health_check_include_router
from .authorization_examples.router import include_router as authorization_examples_include_router
from .db_dependant_examples.router import include_router as db_examples_include_router


def add_routers(app: FastAPI) -> None:
    health_check_include_router(app)
    authorization_examples_include_router(app)
    db_examples_include_router(app)
