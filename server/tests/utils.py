from server.database.models import User, Tweet, Like
from faker import Faker

from typing import Dict

from sqlalchemy.orm import joinedload, Session
from sqlalchemy import select


Faker = Faker()


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
