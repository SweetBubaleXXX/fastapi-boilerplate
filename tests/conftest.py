import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

from src import main
from src.core.container import Container
from src.database.models import Base
from src.database.session import get_session


@pytest.fixture(scope="session")
def container():
    return main.container


@pytest.fixture(scope="session", autouse=True)
def override_db_engine(container: Container):
    db_url = container.settings().TEST_DB_URL
    engine = create_async_engine(db_url, poolclass=StaticPool)
    with container.db_engine.override(engine):
        yield


@pytest_asyncio.fixture(autouse=True)
async def setup_database(container: Container):
    engine = container.db_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(container: Container):
    session_generator = get_session(container.db_session_factory())
    async with await anext(session_generator) as session:
        yield session


@pytest.fixture(scope="session")
def app():
    app = main.create_app()
    return app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def trigger_lifespan_events(app: FastAPI):
    async with LifespanManager(app):
        yield


@pytest.fixture
def client(app: FastAPI):
    with TestClient(app) as client:
        yield client
