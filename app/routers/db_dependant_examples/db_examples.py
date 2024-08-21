from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from routers.common.depends import get_current_user, get_db

router = APIRouter()


@router.get("/basic_auth/")
async def read_items(
        credentials: Annotated[HTTPBasicCredentials, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)]  # noqa
):
    return {
        "logged user": credentials.username,
        "db": "db is connected"
    }
