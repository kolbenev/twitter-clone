from typing import Sequence

from server.database.models import User, Tweet, Like
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


async def get_user_by_apikey_or_id(
    session: AsyncSession, api_key: str = None, user_id: int = None
) -> User:
    if api_key:
        stmt = (
            select(User)
            .where(User.apikey == api_key)
            .options(joinedload(User.followers), joinedload(User.following))
        )
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            return user
        raise HTTPException(status_code=404, detail="User not found")

    if user_id:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(joinedload(User.followers), joinedload(User.following))
        )
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            return user
        raise HTTPException(status_code=404, detail="User not found")


async def lazy_get_user_by_apikey_or_id(
    session: AsyncSession, api_key: str = None, user_id: int = None
) -> User:

    if api_key:
        stmt = select(User).where(User.apikey == api_key)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            return user
        raise HTTPException(status_code=404, detail="User not found")

    if user_id:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            return user
        raise HTTPException(status_code=404, detail="User not found")


async def json_about_user(user: User) -> dict:
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


async def get_all_tweet(session: AsyncSession) -> Sequence[Tweet]:
    stmt = select(Tweet).options(
        joinedload(Tweet.author),
        joinedload(Tweet.likes).joinedload(Like.user),
        joinedload(Tweet.media),
    )
    result = await session.execute(stmt)
    tweets = result.scalars().unique().all()

    return tweets


async def get_tweet_by_id(session: AsyncSession, tweet_id: int) -> Tweet:
    stmt = (
        select(Tweet)
        .where(Tweet.id == tweet_id)
        .options(
            joinedload(Tweet.author),
            joinedload(Tweet.likes).joinedload(Like.user),
            joinedload(Tweet.media),
        )
    )
    result = await session.execute(stmt)
    tweets = result.scalars().first()

    if not tweets:
        raise HTTPException(status_code=404, detail="Tweets not found")

    return tweets


async def lazy_get_tweet_by_id(tweet_id: int, session: AsyncSession) -> Tweet:
    stmt = select(Tweet).where(Tweet.id == tweet_id)
    result = await session.execute(stmt)
    tweet = result.scalars().first()

    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    return tweet


async def get_like(tweet_id: int, user_id: int, session: AsyncSession) -> Like:
    stmt = select(Like).filter(and_(Like.user_id == user_id, Like.tweet_id == tweet_id))
    result = await session.execute(stmt)
    like = result.scalars().first()

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    return like
