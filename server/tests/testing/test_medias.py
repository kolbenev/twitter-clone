"""
Модуль тестирования роута /api/medias/
"""

from io import BytesIO
from server.database.models import Media
from typing import Dict

import pytest
from fastapi.testclient import TestClient

from server.database.models import User, Tweet
from server.tests.getter_variables import API_URL
from server.tests.confdb import session
from server.tests.testing.utils import (
    Faker,
    USER_NOT_FOUND_INVALID_API,
    HEADERS,
    INVALID_HEADERS,
    get_valid_image,
)


URL = f"{API_URL}/medias/"


@pytest.mark.usefixtures("init_user")
class TestMedias:
    def test_post_media_and_tweet_post(self, init_user, client: TestClient):
        """
        Тестирует успешную загрузку медиафайла и привязку его к твиту.
        """
        files: Dict = get_valid_image()

        media_response = client.post(f"{API_URL}/medias/", files=files, headers=HEADERS)

        media_data = media_response.json()
        media_id = media_data["media_id"]

        assert media_response.status_code == 200
        assert media_data["result"] is True
        assert "media_id" in media_data

        tweet_data = {
            "tweet_data": Faker.text(),
            "tweet_media_ids": [media_id],
        }

        tweet_response = client.post(
            f"{API_URL}/tweets/", json=tweet_data, headers=HEADERS
        )
        tweet_result = tweet_response.json()

        media = session.query(Media).where(Media.id == media_id).scalar()
        tweet = (
            session.query(Tweet)
            .where(Tweet.id == tweet_response.json()["tweet_id"])
            .scalar()
        )

        assert media is not None
        assert tweet_response.status_code == 200
        assert tweet_result["result"] is True
        assert "tweet_id" in tweet_result

        session.delete(tweet)
        session.delete(media)
        session.commit()

    # Тестирование неудачных сценариев

    def test_post_media_wrong_apikey(self, client: TestClient):
        """
        Тестирование неверно переданного apikey.
        """
        image_content = b"test content"
        image_file = BytesIO(image_content)
        files = {"file": ("image.jpg", image_file)}
        # files: Dict = get_valid_image()
        response = client.post(URL, headers=INVALID_HEADERS, files=files)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API

    def test_post_media_no_file(self, client: TestClient):
        """
        Тестирование не переданного files.
        """
        response = client.post(URL, headers=HEADERS)
        assert response.status_code == 422

    def test_post_media_file_empty(self, client: TestClient):
        """
        Тестирование переданного пустого files.
        """
        response = client.post(URL, headers=HEADERS, files={"file": None})
        assert response.status_code == 400
