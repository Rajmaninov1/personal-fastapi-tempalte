from typing import Annotated

import structlog
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from core.database import Session
from middleware.fastapi.security.bearer_cognito import JWTBearer
from schemas.entity_sample.schema_example import User

logger = structlog.get_logger('_api_')

security_basic = HTTPBasic()
security_bearer = HTTPBearer()
security_bearer_cognito = JWTBearer()


async def get_db() -> AsyncSession:
    """
    WARNING: not use this with "asyncio.gather" without wrap with asynccontextmanager
    or will get these errors:
        https://docs.sqlalchemy.org/en/20/errors.html#error-isce
        https://github.com/sqlalchemy/sqlalchemy/discussions/9609

    The correct for to use with that is:
        internal_db = asynccontextmanager(get_internal_db)
        async with internal_db() as session:
            await method(session)

    :return:
    """
    async_session = Session
    async with async_session() as session:
        yield session


def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )


async def get_current_user(
        request: Request,
        token: Annotated[str, Depends(security_bearer)]
):
    logger.info(request.headers)  # show headers
    try:
        user = fake_decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=f'Invalid token',
        )
    return user
