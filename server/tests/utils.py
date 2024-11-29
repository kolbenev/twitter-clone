from server.database.models import User
from faker import Faker

from typing import Dict

from sqlalchemy.orm import joinedload, Session
from sqlalchemy import select

Faker = Faker()


def create_new_user(session: Session) -> User:
    new_user = User(
        name=Faker.name(),
        apikey=Faker.password(),
    )

    session.add(new_user)
    session.commit()
    return new_user


def get_user_by_apikey(apikey: str, session: Session) -> User:
    stmt = (
        select(User)
        .where(User.apikey == apikey)
        .options(joinedload(User.followers), joinedload(User.following))
    )
    user = session.execute(stmt).scalars().first()
    return user


def get_dict_about_user(user: User) -> Dict:
    return {
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