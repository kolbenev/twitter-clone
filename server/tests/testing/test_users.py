import random

import pytest
import requests
from faker import Faker

from server.database.models import User
from server.tests.utils import get_dict_about_user
from server.tests.getter_variables import TEST_APIKEY, API_URL


Faker = Faker()
USER_NOT_FOUND = {"detail": "User not found"}
USER_NOT_FOUND_INVALID_API = {"detail": "User not found, invalid API key"}
RESULT_TRUE = {"result": True}
HEADERS = {"api-key": TEST_APIKEY}
INVALID_HEADERS = {"api-key": Faker.password()}
URL = f"{API_URL}/users"


@pytest.mark.usefixtures("init_user")
class TestGetMe:
    """
    Тестирование GET /api/users/me
    """

    def test_get_me(self, init_user: User):
        """
        Проверяет успешное получение информации
        о пользователе.
        """
        user: User = init_user

        url = f"{URL}/me"
        response = requests.get(url=url, headers=HEADERS)

        true_answer = get_dict_about_user(user=user)

        assert response.status_code == 200
        assert response.json() == true_answer

    # Проверка неверных сценариев

    def test_get_me_wrong_apikey(self):
        """
        Проверяет неудачный запрос на получение
        информации о пользователе с несуществующим
        APIKEY.
        """
        url = f"{URL}/me"
        response = requests.get(url=url, headers=INVALID_HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API

    def test_get_users_me_keyless(self):
        """
        Проверяет неудачный запрос получения
        информации о пользователе без ключа.
        """
        url = f"{URL}/me"
        response2 = requests.get(url=url)

        assert response2.status_code == 422


@pytest.mark.usefixtures("init_user")
class TestGetUserById:
    """
    Тестирование GET /api/users/{user_id}
    """

    def test_get_user_by_id(self, init_user: User):
        """
        Проверяет успешное получение пользователя по ID.
        """
        user: User = init_user

        url = f"{URL}/{user.id}"
        response = requests.get(url=url, headers=HEADERS)

        true_answer = get_dict_about_user(user=user)

        assert response.status_code == 200
        assert response.json() == true_answer

    # Проверка неверных сценариев.

    def test_get_user_by_wrong_id(self):
        """
        Проверяет неудачный запрос с
        несуществующим ID.
        """
        url = f"{URL}/{random.randint(8888, 9999)}"
        response = requests.get(url=url)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND

    def test_get_user_wrond_input_id(self):
        """
        Проверяет неудачный запрос с неверным
        вводом ID.
        """
        url = f"{URL}/{Faker.word()}"
        response = requests.get(url=url)

        assert response.status_code == 422


@pytest.mark.usefixtures("init_user")
class TestPostUserFollow:
    """
    Тестирование POST /api/users/{user_id}/follow
    """

    @pytest.mark.usefixtures("random_user_for_func")
    def test_post_user_follow(self, init_user: User, random_user_for_func: User):
        """
        Проверяет успешное оформление подписки.
        """
        test_user: User = init_user
        new_user: User = random_user_for_func

        url = f"{URL}/{new_user.id}/follow"
        response = requests.post(url=url, headers=HEADERS)

        assert response.status_code == 200
        assert response.json() == RESULT_TRUE
        assert test_user in new_user.followers

    # Проверка неверных сценариев подписки.

    @pytest.mark.usefixtures("random_user_for_func")
    def test_post_user_follow_wrong_id(self, init_user, random_user_for_func):
        """
        Неверный ID.
        """
        new_user: User = random_user_for_func

        invalid_user_id = new_user.id + 9999
        url = f"{URL}/{invalid_user_id}/follow"
        response = requests.post(url=url, headers=HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND

    @pytest.mark.usefixtures("random_user_for_func")
    def test_post_user_follow_wrong_apikey(self, init_user, random_user_for_func):
        """
        Неверный APIKEY.
        """
        new_user: User = random_user_for_func

        url = f"{URL}/{new_user.id}/follow"
        response = requests.post(url=url, headers=INVALID_HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API

    def test_post_user_follow_retry_to_subscribe(
        self, init_user: User, random_user_for_func: User
    ):
        """
        Повторная подписка
        """
        test_user: User = init_user
        new_user: User = random_user_for_func

        url = f"{URL}/{new_user.id}/follow"
        response = requests.post(url=url, headers=HEADERS)
        response = requests.post(url=url, headers=HEADERS)

        assert response.status_code == 400
        assert response.json() == {
            "detail": f"{test_user.name} is already subscribed to {new_user.name}"
        }

    def test_post_follow_to_yourself(self, init_user: User):
        """
        Подписка на самого себя
        """
        user: User = init_user

        url = f"{URL}/{user.id}/follow"
        response = requests.post(url=url, headers=HEADERS)

        assert response.status_code == 400
        assert response.json() == {"detail": "Trying to subscribe to yourself"}


@pytest.mark.usefixtures("init_user")
class TestDeleteUserUnfollow:
    """
    Тестирование DELETE /api/users/{user_id}/follow
    """

    @pytest.mark.usefixtures("random_user_for_func")
    def test_delete_user_unfollow(self, init_user: User, random_user_for_func: User):
        """
        Проверяет успешное удаление подписки пользователя.
        """
        test_user: User = init_user
        new_user: User = random_user_for_func

        follow_url = f"{URL}/{new_user.id}/follow"
        requests.post(url=follow_url, headers=HEADERS)

        unfollow_url = f"{URL}/{new_user.id}/follow"
        response = requests.delete(url=unfollow_url, headers=HEADERS)
        expected_response = RESULT_TRUE

        assert response.status_code == 200
        assert response.json() == expected_response
        assert test_user not in new_user.followers

    # Проверка неудачных сценариев на отписку.

    @pytest.mark.usefixtures("init_followers")
    def test_delete_user_follow_wrong_id(self, init_followers):
        """
        Неверный ID.
        """
        user, following = init_followers

        invalid_user_id = user.id + 9999
        url = f"{URL}/{invalid_user_id}/follow"
        response = requests.post(url=url, headers=HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND

    def test_delete_user_follow_wrong_apikey(self, init_followers: (User, User)):
        """
        Неверный APIKEY.
        """
        user, following = init_followers

        url = f"{URL}/{following.id}/follow"
        response = requests.post(url=url, headers=INVALID_HEADERS)

        assert response.status_code == 404
        assert response.json() == USER_NOT_FOUND_INVALID_API

    def test_delete_user_follow_retry_to_subscribe(self, init_followers: (User, User)):
        """
        Повторная отписка.
        """
        user, following = init_followers

        url = f"{URL}/{following.id}/follow"
        response = requests.post(url=url, headers=HEADERS)
        response = requests.post(url=url, headers=HEADERS)

        assert response.status_code == 400
        assert response.json() == {
            "detail": f"{user.name} is already subscribed to {following.name}"
        }
