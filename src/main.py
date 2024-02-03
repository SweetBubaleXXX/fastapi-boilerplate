from fastapi import FastAPI

from .api.router import api_router
from .core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
    )

    app.include_router(api_router)

    return app
