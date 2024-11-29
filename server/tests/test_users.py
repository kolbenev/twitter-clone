import random
from typing import Dict

import pytest
import requests

from string import ascii_letters

from server.database.models import User
from server.tests.utils import get_dict_about_user, get_user_by_apikey, create_new_user
from server.tests.confdb import session
from server.tests.getter_variables import TEST_APIKEY, API_URL


class TestGetMe:
    """
    Тестирование GET /api/users/me
    """
    def test_get_me(self):
        """
        Проверяет успешное получение информации
        о пользователе.
        """
        url = API_URL + "/users/me"
        user: User = get_user_by_apikey(apikey=TEST_APIKEY, session=session)
        true_answer: Dict = get_dict_about_user(user=user)
        headers = {"api-key": TEST_APIKEY,}
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 200
        assert response.json() == true_answer


    def test_get_me_fail(self):
        """
        Проверяет неудачный запрос на получение
        информации о пользователе с несуществующим
        APIKEY.
        """
        url = API_URL + "/users/me"
        headers = {"api-key": ''.join(random.choice(ascii_letters) for _ in range(10))}
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found, invalid API key"}

        response2 = requests.get(url=url)
        assert response2.status_code == 422


class TestGetUserById:
    """
    Тестирование GET /api/users/{user_id}
    """
    def test_get_user_by_id(self):
        """
        Проверяет успешное получение пользователя по ID.
        """
        user: User = get_user_by_apikey(apikey=TEST_APIKEY, session=session)
        url = API_URL + "/users/" + str(user.id)
        true_answer: Dict = get_dict_about_user(user=user)
        headers = {"api-key": TEST_APIKEY}
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 200
        assert response.json() == true_answer


    def test_get_user_by_id_fail(self):
        """
        Проверяет различные сценарии неудачных запросов
        на получения пользователя по ID.
        """

        # Несуществующий ID
        url = API_URL + "/users/" + str(random.randint(200, 300))
        response = requests.get(url=url)
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

        # Неверный ввод ID
        url = API_URL + "/users/" + ''.join(random.choice(ascii_letters) for _ in range(10))
        response2 = requests.get(url=url)
        assert response2.status_code == 422


class TestPostUserFollow:
    """
    Тестирование POST /api/users/{user_id}/follow
    """
    @pytest.mark.usefixtures("random_user_for_func")
    def test_post_user_follow(self, random_user_for_func):
        """
        Проверяет успешное оформление подписки.
        """
        test_user: User = get_user_by_apikey(apikey=TEST_APIKEY, session=session)
        new_user: User = random_user_for_func

        headers = {"api-key": TEST_APIKEY}
        url = f'{API_URL}/users/{new_user.id}/follow'
        true_answer = {"result": True}

        response = requests.post(url=url, headers=headers)

        assert response.status_code == 200
        assert response.json() == true_answer
        assert test_user in new_user.followers


    @pytest.mark.usefixtures("random_user_for_func")
    def test_post_user_follow_fail(self, random_user_for_func: User):
        """
        Проверяет различные сценарии неудачных запросов на подписку.
        """
        test_user: User = get_user_by_apikey(apikey=TEST_APIKEY, session=session)
        new_user: User = random_user_for_func

        headers = {"api-key": TEST_APIKEY}

        # Неверный ID пользователя
        invalid_user_id = new_user.id + 9999
        url = f'{API_URL}/users/{invalid_user_id}/follow'
        response = requests.post(url=url, headers=headers)
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

        # Неверный API-ключ
        headers_invalid_key = {"api-key": "invalid_key"}
        url = f'{API_URL}/users/{new_user.id}/follow'
        response = requests.post(url=url, headers=headers_invalid_key)
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found, invalid API key"}

        # Пользователь уже подписан
        response = requests.post(url=url, headers=headers)
        assert response.status_code == 200

        # Пытаемся повторно подписаться
        response = requests.post(url=url, headers=headers)
        assert response.status_code == 400
        assert response.json() == {
            "detail": f"{test_user.name} is already subscribed to {new_user.name}"
        }


class TestDeleteUserUnfollow:
    """
    Тестирование DELETE /api/users/{user_id}/follow
    """
    @pytest.mark.usefixtures("random_user_for_func")
    def test_delete_user_unfollow(self, random_user_for_func):
        """
        Проверяет успешное удаление подписки пользователя.
        """
        test_user: User = get_user_by_apikey(apikey=TEST_APIKEY, session=session)
        new_user: User = random_user_for_func

        headers = {"api-key": TEST_APIKEY}
        follow_url = f"{API_URL}/users/{new_user.id}/follow"
        requests.post(url=follow_url, headers=headers)

        unfollow_url = f"{API_URL}/users/{new_user.id}/follow"
        response = requests.delete(url=unfollow_url, headers=headers)
        expected_response = {"result": True}

        assert response.status_code == 200
        assert response.json() == expected_response
        assert test_user not in new_user.followers

    @pytest.mark.usefixtures("random_user_for_func")
    def test_delete_user_unfollow_fail(self, random_user_for_func):
        """
        Проверяет различные сценарии неудачных запросов на отписку.
        """
        test_user: User = get_user_by_apikey(apikey=TEST_APIKEY, session=session)
        new_user: User = random_user_for_func

        headers = {"api-key": TEST_APIKEY}

        # Неверный ID пользователя
        invalid_user_id = new_user.id + 9999
        unfollow_url_invalid_user = f"{API_URL}/users/{invalid_user_id}/follow"
        response = requests.delete(url=unfollow_url_invalid_user, headers=headers)
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

        # Неверный API-ключ
        headers_invalid_key = {"api-key": "invalid_key"}
        unfollow_url_valid_user = f"{API_URL}/users/{new_user.id}/follow"
        response = requests.delete(url=unfollow_url_valid_user, headers=headers_invalid_key)
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found, invalid API key"}

        # Отписка от пользователя, на которого нет подписки
        response = requests.delete(url=unfollow_url_valid_user, headers=headers)
        assert response.status_code == 400
        assert response.json() == {
            "detail": f"{test_user.name} doesn't follow {new_user.name}"
        }


