import logging

from fastapi import FastAPI
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

logger = logging.getLogger('_api_')


def pydantic_add_handler(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        logger.error(f'Invalid Pydantic Data: {str(exc)}')

        error = {
            'uri': request.url.path,
            'message': f'Error in internal data validation, please contact technical support\n{str(exc)}'.splitlines()
        }

        return ORJSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                'detail': jsonable_encoder(error)
            },
        )
