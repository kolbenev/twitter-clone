import pytest

from server.tests.confdb import session, engine
from server.database.models import User
from server.database.confdb import Base
from server.tests.getter_variables import TEST_APIKEY, TEST_USERNAME


@pytest.fixture(scope="session", autouse=True)
def setup_teardown():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="class")
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
