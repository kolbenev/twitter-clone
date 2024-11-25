import pytest
import pytest_asyncio

from server.database.confdb import Base

from confdb import async_engine

@pytest_asyncio.fixture
async def setup_db():
    async with async_engine.begin() as  conn:
        conn.run_sync(Base.metadata.create_all)


async def test_setup(setup_db):
    assert True