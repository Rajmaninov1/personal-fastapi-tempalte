from fastapi import APIRouter

from core.utils import pydantic_orjson_result

router = APIRouter()


# don't need authorization for health check
@router.get("/", )
@pydantic_orjson_result
async def health_check() -> dict:
    return {'status': 200, 'message': 'the service is working'}
