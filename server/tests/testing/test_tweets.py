"""
Модуль тестирования /api/tweets/
"""

import os
import random
from typing import Dict

import pytest
from sqlalchemy import and_
from fastapi.testclient import TestClient

from server.database.models import User, Tweet, Like
from server.tests.getter_variables import API_URL
from server.tests.confdb import session
from server.tests.testing.utils import (
    USER_NOT_FOUND_INVALID_API,
    RESULT_TRUE,
    HEADERS,
    INVALID_HEADERS,
    get_dict_tweet_feed,
    get_tweet_data,
)


URL = f"{API_URL}/tweets"


@pytest.mark.usefixtures("init_tweet_and_its_author")
class TestGetTweets:
    """
    Тестирование GET /api/tweet/
    """

    def test_get_tweets(self, client: TestClient):
        """
        Проверяет успешное получение ленту твитов.
        """
        url = f"{URL}/"
        response = client.get(url, headers=HEADERS)

        true_answer: Dict = get_dict_tweet_feed(session=session)
        assert response.status_code == 200
        assert response.json() == true_answer

    def test_get_tweets_fail(self, client: TestClient):
        """
        Проверяет неудачный запрос на получение
        ленты твитов с несуществующим APIKEY.
        """
        url = f"{URL}/"
        response = client.get(url, headers=INVALID_HEADERS)
        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API


@pytest.mark.usefixtures("init_user")
class TestPostTweets:
    """
    Тестирование POST /api/tweet/
    + POST /api/medias/
    """

    def test_post_tweets_success(self, init_user: User, client: TestClient):
        """
        Проверяет успешное создание твита.
        """
        url = f"{URL}/"
        tweet_data: Dict = get_tweet_data()

        response = client.post(url, headers=HEADERS, json=tweet_data)
        response_data = response.json()

        assert response.status_code == 200
        assert response_data["result"] is True
        assert "tweet_id" in response_data

        tweet = (
            session.query(Tweet)
            .where(Tweet.id == int(response_data["tweet_id"]))
            .scalar()
        )

        assert tweet is not None
        assert tweet.content == tweet_data["tweet_data"]
        assert tweet.author_id == init_user.id

        session.delete(tweet)
        session.commit()

    # Проверка неудачных сценариев создания твита.

    def test_post_tweets_empty_data(self, client: TestClient):
        """
        Проверка создание твита с пустыми данными.
        """
        url = f"{URL}/"
        tweet_data = {}
        response = client.post(url, headers=HEADERS, json=tweet_data)

        assert response.status_code == 400
        assert response.json() == {"detail": "Tweet is empty"}

    def test_post_tweets_invalid_api_key(self, client: TestClient):
        """
        Проверяет создание твита с несуществующим APIKEY.
        """
        url = f"{URL}/"
        tweet_data: Dict = get_tweet_data()
        response = client.post(url, headers=INVALID_HEADERS, json=tweet_data)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API


@pytest.mark.usefixtures("init_tweet_and_its_author")
class TestPostLike:
    def test_post_like_success(
        self, init_tweet_and_its_author: (Tweet, User), client: TestClient
    ):
        tweet, user = init_tweet_and_its_author

        url = f"{URL}/{tweet.id}/likes"
        response = client.post(url, headers=HEADERS)

        assert response.status_code == 200
        assert response.json() == RESULT_TRUE

        like = (
            session.query(Like)
            .where(and_(tweet.id == Like.tweet_id, user.id == Like.user_id))
            .scalar()
        )
        assert like is not None

        session.delete(like)
        session.commit()

    # Проверка неудачных сценариев поставить лайк.

    def test_post_like_wrong_apikey(
        self, init_tweet_and_its_author: (Tweet, User), client: TestClient
    ):
        """
        Проверка неверного APIKEY.
        """
        tweet, user = init_tweet_and_its_author

        url = f"{URL}/{tweet.id}/likes"
        response = client.post(url, headers=INVALID_HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API

    def test_post_like_invalid_tweet_id(
        self, init_tweet_and_its_author: (Tweet, User), client: TestClient
    ):
        """
        Неверный ID твита.
        """
        url = f"{URL}/{random.randint(8888, 9999)}/likes"
        response = client.post(url, headers=HEADERS)

        assert response.status_code == 404
        assert response.json() == {"detail": "Tweet not found"}

    def test_post_like_again(
        self, init_tweet_and_its_author: (Tweet, User), client: TestClient
    ):
        """
        Попытка поставить лайк второй раз.
        """
        tweet, user = init_tweet_and_its_author

        url = f"{URL}/{tweet.id}/likes"
        response = client.post(url, headers=HEADERS)
        response = client.post(url, headers=HEADERS)

        assert response.status_code == 400
        assert response.json() == {"detail": "Already liked the tweet"}


@pytest.mark.usefixtures("init_tweet_and_its_author")
class TestDeleteLike:
    def test_delete_like_success(
        self, init_tweet_and_its_author: (Tweet, User), client: TestClient
    ):
        """
        Успешное удаление лайка с твита.
        """
        tweet, user = init_tweet_and_its_author

        url = f"{URL}/{tweet.id}/likes"
        response = client.post(url, headers=HEADERS)
        assert response.status_code == 200

        response = client.delete(url, headers=HEADERS)
        assert response.status_code == 200
        assert response.json() == RESULT_TRUE

        like = (
            session.query(Like)
            .where(and_(tweet.id == Like.tweet_id, user.id == Like.user_id))
            .scalar()
        )
        assert like is None

    def test_delete_like_wrong_apikey(
        self, init_tweet_and_its_author: (Tweet, User), client: TestClient
    ):
        """
        Проверка неверного APIKEY при удалении лайка.
        """
        tweet, user = init_tweet_and_its_author

        url = f"{URL}/{tweet.id}/likes"
        response = client.delete(url, headers=INVALID_HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API

    def test_delete_like_invalid_tweet_id(
        self, init_tweet_and_its_author: (User, User), client: TestClient
    ):
        """
        Удаление лайка с несуществующего твита.
        """
        url = f"{URL}/{random.randint(8888, 9999)}/likes"
        response = client.delete(url, headers=HEADERS)

        assert response.status_code == 404
        assert response.json() == {"detail": "Tweet not found"}

    def test_delete_like_not_liked(
        self, init_tweet_and_its_author: (Tweet, User), client: TestClient
    ):
        """
        Удаление лайка с твита, который пользователь не лайкал.
        """
        tweet, user = init_tweet_and_its_author

        url = f"{URL}/{tweet.id}/likes"
        response = client.delete(url, headers=HEADERS)

        assert response.status_code == 404
        assert response.json() == {"detail": "Like not found"}


@pytest.mark.usefixtures("init_tweet_and_its_author")
class TestDeleteTweet:
    def test_delete_tweet_success(
        self, init_tweet_and_its_author: (Tweet, User), client: TestClient
    ):
        """
        Успешное удаление твита автором.
        """
        tweet, user = init_tweet_and_its_author
        url = f"{URL}/{tweet.id}"

        response = client.delete(url, headers=HEADERS)

        assert response.status_code == 200
        assert response.json() == {"result": True}

        deleted_tweet = session.query(Tweet).filter_by(id=tweet.id).first()
        assert deleted_tweet is None

        for media in tweet.media:
            assert not os.path.exists(media.file_path)

    # Проверка неудачных сценариев.

    def test_delete_tweet_not_author(
        self, init_tweet_and_its_author: (Tweet, User), client: TestClient
    ):
        """
        Попытка удалить твит, автором которого не является пользователь.
        """
        tweet, user = init_tweet_and_its_author

        another_user = User(name="OtherUser", apikey="other_api_key")
        session.add(another_user)
        session.commit()

        url = f"{URL}/{tweet.id}"
        headers = {"api-key": another_user.apikey}
        response = client.delete(url, headers=headers)

        assert response.status_code == 403
        assert response.json() == {"detail": "The user is not the author of the tweet"}

        existing_tweet = session.query(Tweet).filter_by(id=tweet.id).first()
        assert existing_tweet is not None

        session.delete(another_user)
        session.commit()

    def test_delete_tweet_invalid_tweet_id(self, client: TestClient):
        """
        Попытка удалить несуществующий твит.
        """
        invalid_tweet_id = random.randint(8888, 9999)
        url = f"{URL}/{invalid_tweet_id}"

        response = client.delete(url, headers=HEADERS)

        assert response.status_code == 404
        assert response.json() == {"detail": "Tweet not found"}

    def test_delete_tweet_wrong_apikey(
        self, init_tweet_and_its_author: (Tweet, User), client: TestClient
    ):
        """
        Проверка удаления твита с неверным API-ключом.
        """
        tweet, user = init_tweet_and_its_author
        url = f"{URL}/{tweet.id}"

        response = client.delete(url, headers=INVALID_HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API
