import pytest
import pytest_asyncio
from faker import Faker
import asyncio

from server.app.routes.utils import lazy_get_user_by_apikey_or_id
from server.tests.confdb import session, engine
from server.database.confdb import Base
from server.database.models import User

faker = Faker()
user_id = None

@pytest.fixture(scope='class', autouse=True)
async def setup_and_teardown():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def create_new_user():
    new_user = User(
        name=faker.name(),
        apikey=faker.password(),
    )

    session.add(new_user)
    await session.commit()

    yield
    await session.delete(new_user)
    await session.commit()


class TestLazy:
    async def test_get_user_lazy(self, create_new_user):
        user = await lazy_get_user_by_apikey_or_id(user_id=1, session=session)
        assert user.id == 1