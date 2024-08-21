from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .error_handlers.api import add_handler as api_add_handler
from .error_handlers.pydantic_error import pydantic_add_handler


def add_error_handlers(app: FastAPI) -> None:
    api_add_handler(app)
    pydantic_add_handler(app)


def add_cors(app: FastAPI):
    # origins = settings.ORIGINS
    origins = ['*']
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
