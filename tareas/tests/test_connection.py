import pytest
from sqlmodel import select

from tareas.database.connection import async_session_maker, engine

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_async_database_connection():
    async with async_session_maker() as session:
        result = await session.exec(select(1))
        assert result.one() == 1, "Database connection check failed"

    await engine.dispose()
