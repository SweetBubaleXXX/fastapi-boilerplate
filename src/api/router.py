from fastapi import APIRouter

from ..core.config import settings
from .v1.router import v1_router

api_router = APIRouter()

api_router.include_router(v1_router, prefix=settings.API_V1_STR)
