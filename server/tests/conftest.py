import pytest_asyncio
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from server.app.routes.utils import lazy_get_user_by_apikey_or_id
from server.database.models import Base
from server.database.models import User

database_url = "postgresql+asyncpg://test:test@localhost:5433/test_twitter"
engine = create_async_engine(url=database_url, echo=True)
session_factory = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
session = session_factory()


@pytest.fixture
async def setup_teardown():
    async with engine.begin() as conn:
        print('Создание таблиц')
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        print('Удаление таблиц')
        await conn.run_sync(Base.metadata.drop_all)


async def test_get_lazy_user_api(setup_teardown):

    new_user = User(
        name="michael",
        apikey='test',
    )
    session.add(new_user)
    await session.flush()

    user: User = await lazy_get_user_by_apikey_or_id(user_id=new_user.id, session=session)
    assert user.id == new_user.id