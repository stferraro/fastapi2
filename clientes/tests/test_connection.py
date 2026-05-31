import pytest

from clientes.database.connection import async_session_maker, engine

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"

async def test_get_session():
    async with async_session_maker() as session:
        assert session is not None, "Failed to establish a database session"
    await engine.dispose()