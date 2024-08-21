from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.exceptions import ExceptionMiddleware

from core.basckground_tasks import background_tasks
from core.logger_factory import logger_factory
from core.settings import settings, Environment
from middleware.middlewares import add_error_handlers, add_cors
from routers.routers import add_routers

logger = structlog.get_logger('_api_')

# Configure logging
logger_factory()

# Configure FastAPI
if settings.ENVIRONMENT != Environment.PROD:
    settings.WEB_APP_DESCRIPTION = f'## ENV: {settings.ENVIRONMENT}\n\n{settings.WEB_APP_DESCRIPTION}'


@asynccontextmanager
async def lifespan(lifespan_app: FastAPI):
    # Force to build middleware stack for all apps and fill the
    # "middleware_stack" property
    client = TestClient(app)
    # Main app
    client.get('/docs?__lifespan__start__')
    # Sub apps
    # client.get('/admin/docs?__lifespan__start__')

    # Hack ExceptionMiddleware to handle (500 or Exception) errors
    # Override on startup because is the moment when the middleware_stack was built
    # Breaking change, only works from 0.91.0 to upper: https://fastapi.tiangolo.com/release-notes/#0910
    # noinspection PyUnresolvedReferences
    generic_exception_handlers = {k: v for k, v in app.exception_handlers.items() if k == 500 or k == Exception}
    if generic_exception_handlers:
        _app = app.middleware_stack
        while True:
            if isinstance(_app, ExceptionMiddleware):
                _app._exception_handlers.update(generic_exception_handlers)  # noqa
                break
            elif hasattr(_app, 'app'):
                _app = _app.app
            else:
                break

    # Start task garbage collector
    await background_tasks.add_fire_and_forget_task(background_tasks.garbage_collector)

    yield

app = FastAPI(
    title=settings.WEB_APP_TITLE,
    description=settings.WEB_APP_DESCRIPTION,
    version=settings.WEB_APP_VERSION,
    servers=[
        {'url': settings.OPENAPI_SERVER, 'description': f'{settings.ENVIRONMENT} environment'},
    ] if settings.OPENAPI_SERVER else None,
    lifespan=lifespan,
    root_path=f'/endpoint-prefix' if not settings.LOCAL else None
)

# Configure HTTP Starlette server
add_error_handlers(app)

# Cors configuration
add_cors(app)

# Configure routes
add_routers(app)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
