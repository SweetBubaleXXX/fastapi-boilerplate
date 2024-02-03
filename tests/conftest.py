from typing import AsyncIterator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.core.config import settings
from src.core.database import get_session
from src.main import create_app
from src.models.base import Base

engine = create_async_engine(settings.TEST_DB_URL, poolclass=StaticPool)
async_session_factory = async_sessionmaker(engine)


async def override_get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.dependency_overrides[get_session] = override_get_session
    return app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def trigger_lifespan_events(app: FastAPI):
    async with LifespanManager(app):
        yield


@pytest_asyncio.fixture
async def database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield override_get_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(database):
    async with database() as session:
        yield session


@pytest.fixture
def client(app: FastAPI, database):
    with TestClient(app) as client:
        yield client
