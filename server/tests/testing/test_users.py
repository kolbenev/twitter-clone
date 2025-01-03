"""
Модуль тестирования /api/users/
"""

import random
from typing import Dict

import pytest
from fastapi.testclient import TestClient

from server.database.models import User
from server.tests.testing.utils import get_dict_about_user
from server.tests.getter_variables import API_URL
from server.tests.testing.utils import (
    Faker,
    USER_NOT_FOUND,
    USER_NOT_FOUND_INVALID_API,
    RESULT_TRUE,
    HEADERS,
    INVALID_HEADERS,
)


URL = f"{API_URL}/users"


@pytest.mark.usefixtures("init_user")
class TestGetMe:
    """
    Тестирование GET /api/users/me
    """

    def test_get_me(self, init_user: User, client: TestClient):
        """
        Проверяет успешное получение информации
        о пользователе.
        """
        user: User = init_user

        url = f"{URL}/me"
        response = client.get(url, headers=HEADERS)
        true_answer: Dict = get_dict_about_user(user=user)

        assert response.status_code == 200
        assert response.json() == true_answer

    # Проверка неверных сценариев

    def test_get_me_wrong_apikey(self, client: TestClient):
        """
        Проверяет неудачный запрос на получение
        информации о пользователе с несуществующим
        APIKEY.
        """
        url = f"{URL}/me"
        response = client.get(url=url, headers=INVALID_HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API

    def test_get_users_me_keyless(self, client: TestClient):
        """
        Проверяет неудачный запрос получения
        информации о пользователе без ключа.
        """
        url = f"{URL}/me"
        response2 = client.get(url=url)

        assert response2.status_code == 422


@pytest.mark.usefixtures("init_user")
class TestGetUserById:
    """
    Тестирование GET /api/users/{user_id}
    """

    def test_get_user_by_id(self, init_user: User, client: TestClient):
        """
        Проверяет успешное получение пользователя по ID.
        """
        user: User = init_user

        url = f"{URL}/{user.id}"
        response = client.get(url=url, headers=HEADERS)
        true_answer = get_dict_about_user(user=user)

        assert response.status_code == 200
        assert response.json() == true_answer

    # Проверка неверных сценариев.

    def test_get_user_by_wrong_id(self, client: TestClient):
        """
        Проверяет неудачный запрос с
        несуществующим ID.
        """
        url = f"{URL}/{random.randint(8888, 9999)}"
        response = client.get(url=url)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND

    def test_get_user_wrond_input_id(self, client: TestClient):
        """
        Проверяет неудачный запрос с неверным
        вводом ID.
        """
        url = f"{URL}/{Faker.word()}"
        response = client.get(url=url)

        assert response.status_code == 422


@pytest.mark.usefixtures("init_user")
class TestPostUserFollow:
    """
    Тестирование POST /api/users/{user_id}/follow
    """

    @pytest.mark.usefixtures("random_user_for_func")
    def test_post_user_follow(
        self, init_user: User, random_user_for_func: User, client: TestClient
    ):
        """
        Проверяет успешное оформление подписки.
        """
        test_user: User = init_user
        new_user: User = random_user_for_func

        url = f"{URL}/{new_user.id}/follow"
        response = client.post(url=url, headers=HEADERS)

        assert response.status_code == 200
        assert response.json() == RESULT_TRUE
        assert test_user in new_user.followers

    # Проверка неверных сценариев подписки.

    @pytest.mark.usefixtures("random_user_for_func")
    def test_post_user_follow_wrong_id(self, client: TestClient):
        """
        Неверный ID.
        """
        invalid_user_id = 9999
        url = f"{URL}/{invalid_user_id}/follow"
        response = client.post(url=url, headers=HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND

    @pytest.mark.usefixtures("random_user_for_func")
    def test_post_user_follow_wrong_apikey(
        self, random_user_for_func, client: TestClient
    ):
        """
        Неверный APIKEY.
        """
        new_user: User = random_user_for_func

        url = f"{URL}/{new_user.id}/follow"
        response = client.post(url=url, headers=INVALID_HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API

    def test_post_user_follow_retry_to_subscribe(
        self, init_user: User, random_user_for_func: User, client: TestClient
    ):
        """
        Повторная подписка
        """
        test_user: User = init_user
        new_user: User = random_user_for_func

        url = f"{URL}/{new_user.id}/follow"
        response = client.post(url=url, headers=HEADERS)
        response = client.post(url=url, headers=HEADERS)

        assert response.status_code == 400
        assert response.json() == {
            "detail": f"{
                test_user.name} is already subscribed to {
                new_user.name}"
        }

    def test_post_follow_to_yourself(self, init_user: User, client: TestClient):
        """
        Подписка на самого себя
        """
        user: User = init_user

        url = f"{URL}/{user.id}/follow"
        response = client.post(url=url, headers=HEADERS)

        assert response.status_code == 400
        assert response.json() == {"detail": "Trying to subscribe to yourself"}


@pytest.mark.usefixtures("init_user")
class TestDeleteUserUnfollow:
    """
    Тестирование DELETE /api/users/{user_id}/follow
    """

    @pytest.mark.usefixtures("random_user_for_func")
    def test_delete_user_unfollow(
        self, init_user: User, random_user_for_func: User, client: TestClient
    ):
        """
        Проверяет успешное удаление подписки пользователя.
        """
        test_user: User = init_user
        new_user: User = random_user_for_func

        follow_url = f"{URL}/{new_user.id}/follow"
        client.post(url=follow_url, headers=HEADERS)

        unfollow_url = f"{URL}/{new_user.id}/follow"
        response = client.delete(url=unfollow_url, headers=HEADERS)
        expected_response = RESULT_TRUE

        assert response.status_code == 200
        assert response.json() == expected_response
        assert test_user not in new_user.followers

    # Проверка неудачных сценариев на отписку.

    @pytest.mark.usefixtures("init_followers")
    def test_delete_user_follow_wrong_id(self, client: TestClient):
        """
        Неверный ID.
        """
        invalid_user_id = 9999
        url = f"{URL}/{invalid_user_id}/follow"
        response = client.post(url=url, headers=HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND

    def test_delete_user_follow_wrong_apikey(
        self, init_followers: (User, User), client: TestClient
    ):
        """
        Неверный APIKEY.
        """
        user, following = init_followers

        url = f"{URL}/{following.id}/follow"
        response = client.post(url=url, headers=INVALID_HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API

    def test_delete_user_follow_retry_to_subscribe(
        self, init_followers: (User, User), client: TestClient
    ):
        """
        Повторная отписка.
        """
        user, following = init_followers

        url = f"{URL}/{following.id}/follow"
        response = client.post(url=url, headers=HEADERS)
        response = client.post(url=url, headers=HEADERS)

        assert response.status_code == 400
        assert response.json() == {
            "detail": f"{user.name} is already subscribed to {following.name}"
        }
