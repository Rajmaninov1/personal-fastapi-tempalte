from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials, HTTPAuthorizationCredentials

from routers.common.depends import get_current_user, security_bearer_cognito, security_bearer, security_basic

router = APIRouter()


@router.get("/basic_auth/")
async def read_items(credentials: Annotated[HTTPBasicCredentials, Depends(security_basic)]):
    return {"logged user": credentials.username}


@router.get("/bearer_token/")
async def read_items(token: Annotated[HTTPAuthorizationCredentials, Depends(security_bearer)]):
    return {"token": token}


@router.get("/cognito_token/")
async def read_items(token: Annotated[HTTPAuthorizationCredentials, Depends(security_bearer_cognito)]):
    return {"token": token}


@router.get("/using_get_current_user/")
async def read_items(token: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)]):
    return {"token": token}
