from typing import AsyncIterator, Callable

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from src.core.config import settings
from src.core.database import get_session
from src.main import create_app
from src.models.base import Base


@pytest.fixture(scope="session")
def db_engine():
    return create_async_engine(settings.TEST_DB_URL, poolclass=StaticPool)


@pytest.fixture(scope="session")
def db_session_factory(db_engine: AsyncEngine):
    return async_sessionmaker(db_engine)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(db_engine: AsyncEngine):
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def override_get_session(db_session_factory):
    async def get_session() -> AsyncIterator[AsyncSession]:
        async with db_session_factory() as session:
            yield session

    return get_session


@pytest_asyncio.fixture
async def db_session(override_get_session: Callable[[], AsyncIterator[AsyncSession]]):
    async with await anext(override_get_session()) as session:
        yield session


@pytest.fixture(scope="session")
def app(override_get_session: Callable[[], AsyncIterator[AsyncSession]]):
    app = create_app()
    app.dependency_overrides[get_session] = override_get_session
    return app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def trigger_lifespan_events(app: FastAPI):
    async with LifespanManager(app):
        yield


@pytest.fixture
def client(app: FastAPI):
    with TestClient(app) as client:
        yield client
