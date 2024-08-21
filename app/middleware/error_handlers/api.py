import logging

from fastapi import FastAPI
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR

from core.exceptions import BaseAPIException

logger = logging.getLogger('_api_')


def add_handler(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request, exc):
        logger.error(f'HTTP API Error: {exc.__repr__()}')
        return await http_exception_handler(request, exc)

    # noinspection PyUnusedLocal
    @app.exception_handler(BaseAPIException)
    async def handler(request: Request, exc: BaseAPIException):
        logger.error(f'API Error: {str(exc)}')

        status_code = exc.http_status_code
        if status_code == HTTP_204_NO_CONTENT:
            return Response(status_code=status_code)
        else:
            return ORJSONResponse(status_code=status_code, content={'detail': str(exc)})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        transaction_id: str = request.headers.get('X-T-ID')

        logger.error(f'Invalid Data: {str(exc)}')

        return ORJSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={
                'detail': jsonable_encoder(exc.errors())
            } if not transaction_id else {
                'transaction_id': transaction_id,
                'detail': jsonable_encoder(exc.errors())
            },
        )

    @app.exception_handler(500)
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        transaction_id: str = request.headers.get('X-T-ID')

        logger.error(f'Uncaught Exception: {str(exc)}', exc_info=True)

        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'detail': jsonable_encoder(str(exc))
            } if not transaction_id else {
                'transaction_id': transaction_id,
                'detail': jsonable_encoder(f'{exc.__class__} - {str(exc)}')
            },
        )
