from typing import Dict
from io import BytesIO

from sqlalchemy.orm import joinedload, Session
from sqlalchemy import select
from faker import Faker

from server.tests.getter_variables import TEST_APIKEY
from server.database.models import User, Tweet, Like


Faker = Faker()
USER_NOT_FOUND = {"detail": "User not found"}
USER_NOT_FOUND_INVALID_API = {"detail": "User not found, invalid API key"}
RESULT_TRUE = {"result": True}
HEADERS = {"api-key": TEST_APIKEY}
INVALID_HEADERS = {"api-key": Faker.password()}


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


def get_dict_tweet_feed(session: Session) -> Dict:
    stmt = select(Tweet).options(
        joinedload(Tweet.author),
        joinedload(Tweet.likes).joinedload(Like.user),
        joinedload(Tweet.media),
    )
    result = session.execute(stmt)
    tweets = result.scalars().unique().all()

    tweet_feed = {
        "result": True,
        "tweets": [
            {
                "id": tweet.id,
                "content": tweet.content,
                "attachments": [media.file_url for media in tweet.media],
                "author": {
                    "id": tweet.author.id,
                    "name": tweet.author.name,
                },
                "likes": [
                    {
                        "user_id": like.user_id,
                        "name": like.user.name,
                    }
                    for like in tweet.likes
                ],
            }
            for tweet in tweets
        ],
    }

    return tweet_feed


def get_valid_image() -> Dict:
    image_content = b"test content"
    image_file = BytesIO(image_content)
    files = {"file": ("image.jpg", image_file)}

    return files


def get_tweet_data() -> Dict:
    tweet_data = {
        "tweet_data": Faker.text(),
        "tweet_media_ids": [],
    }
    return tweet_data
