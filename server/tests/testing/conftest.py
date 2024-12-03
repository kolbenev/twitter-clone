"""
Модуль фикстур pytest
"""

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from server.tests.getter_variables import TEST_APIKEY, TEST_USERNAME
from server.tests.confdb import session, engine
from server.database.models import User, Tweet
from server.database.confdb import Base
from server.app.main import app


Faker = Faker()


@pytest.fixture(scope="session", autouse=True)
def setup():
    """
    Фикстура для создания таблиц в базе данных.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@pytest.fixture(scope="session", autouse=True)
def client() -> TestClient:
    """
    Фикстура для получения тестового клиента FastAPI.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="class")
def init_user() -> User:
    """
    Фикстура инициализации тестового пользователя,
    с использованием apikey и username заданного в
    переменных окружения.
    """
    new_user = User(
        name=TEST_USERNAME,
        apikey=TEST_APIKEY,
    )
    session.add(new_user)
    session.commit()

    yield new_user

    session.delete(new_user)
    session.commit()


@pytest.fixture(scope="function")
def random_user_for_func() -> User:
    """
    Фикстура для создания пользователя со
    случайным именем и apikey. Используется
    только в рамках функции.
    """
    new_user = User(name=Faker.name(), apikey=Faker.password())
    session.add(new_user)
    session.commit()

    yield new_user

    session.delete(new_user)
    session.commit()


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("init_user")
def init_tweet_and_its_author(init_user: User) -> (Tweet, User):
    """
    Фикстура для создания твита в авторстве
    тестового пользователя.
    """
    new_tweet = Tweet(
        author_id=init_user.id,
        content=Faker.text(),
    )
    session.add(new_tweet)
    session.commit()

    yield new_tweet, init_user

    session.delete(new_tweet)
    session.commit()


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("init_user")
@pytest.mark.usefixtures("random_user_for_func")
def init_followers(init_user: User, random_user_for_func: User) -> (User, User):
    """
    Фикстура для создания рандомного пользователя, на
    которого подписывается тестовый пользователь.
    """
    user: User = init_user
    following: User = random_user_for_func
    user.following.append(user)

    yield user, following

    user.following.remove(user)
