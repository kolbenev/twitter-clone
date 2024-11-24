# import pytest
# import pytest_asyncio
# from faker import Faker
#
# from server.tests.confdb import get_session, engine
# from server.database.confdb import Base
# from server.database.models import User
#
# faker = Faker()
#
# @pytest_asyncio.fixture()
# async def setup_and_teardown():
#     print("Запуск фикстуры setup_and_teardown")
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#     yield
#
#     print("Запуск фикстуры teardown")
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#
# async def test_hello(setup_and_teardown):
#     assert True
