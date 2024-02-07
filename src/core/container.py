from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import Settings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.database.session",
        ],
        packages=[],
    )

    settings = providers.ThreadSafeSingleton(Settings)

    db_engine = providers.ThreadSafeSingleton(
        create_async_engine,
        settings.provided.DB_URL,
    )
    db_session_factory = providers.ThreadSafeSingleton(
        async_sessionmaker,
        db_engine.provided,
    )
