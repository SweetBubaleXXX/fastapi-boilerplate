from typing import Annotated, AsyncIterator

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..core.container import Container


@inject
def get_session_factory(
    session_factory: async_sessionmaker[AsyncSession] = Depends(
        Provide[Container.db_session_factory]
    ),
):
    return session_factory


async def get_session(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_factory)
    ]
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_session)]
