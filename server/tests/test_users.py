import pytest
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import requests

import os
import json

from server.database.models import User
from server.tests.confdb import session
from server.tests.getter_variables import TEST_APIKEY, API_URL


@pytest.mark.usefixtures("init_user")
class TestUsers:
    def test_get_me(self):
        url = API_URL + "/users/me"

        stmt = (
            select(User)
            .where(User.apikey == TEST_APIKEY)
            .options(joinedload(User.followers), joinedload(User.following))
        )
        user = session.execute(stmt).scalars().first()

        headers = {
            "api-key": TEST_APIKEY,
        }
        true_answer = {
            "result": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "followers": [
                    {
                        "id": follower.id,
                        "name": follower.name,
                    }
                    for follower in user.followers
                ],
                "following": [
                    {
                        "id": following.id,
                        "name": following.name,
                    }
                    for following in user.following
                ],
            },
        }

        r = requests.get(url=url, headers=headers)
        assert r.json() == true_answer
