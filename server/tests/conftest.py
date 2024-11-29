import pytest
from faker import Faker

from server.tests.confdb import session, engine
from server.database.models import User
from server.database.confdb import Base
from server.tests.getter_variables import TEST_APIKEY, TEST_USERNAME


Faker = Faker()


@pytest.fixture(scope="session", autouse=True)
def setup_teardown():
    try:
        Base.metadata.create_all(engine)
        yield
    finally:
        session.rollback()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="class", autouse=True)
def init_user():
    new_user = User(
        name=TEST_USERNAME,
        apikey=TEST_APIKEY,
    )
    session.add(new_user)
    session.commit()
    yield
    session.delete(new_user)
    session.commit()


@pytest.fixture(scope="function")
def random_user_for_func():
    new_user = User(
        name=Faker.name(),
        apikey=Faker.password()
    )

    session.add(new_user)
    session.commit()
    yield new_user
    session.delete(new_user)
    session.commit()