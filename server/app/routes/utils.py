from typing import Sequence

from server.database.models import User, Tweet, Like
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


async def get_user_by_apikey(session: AsyncSession, api_key: str) -> User:
    """
    Получает пользователя по API-ключу, подгружая его подписки и подписчиков.

    Если пользователь найден, возвращается объект User.
    В противном случае вызывается исключение HTTPException
    с кодом 404 и сообщением "User not found".

    :param session: Асинхронная сессия SQLAlchemy.
    :param api_key: API-ключ пользователя.
    :return: Объект User.
    :raises HTTPException: Если пользователь не найден.
    """
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


async def get_user_by_id(user_id: int, session: AsyncSession) -> User:
    """
    Получает пользователя по его ID, подгружая его подписки и подписчиков.

    Если пользователь найден, возвращается объект User.
    В противном случае вызывается исключение HTTPException
    с кодом 404 и сообщением "User not found".

    :param session: Асинхронная сессия SQLAlchemy.
    :param api_key: API-ключ пользователя.
    :return: Объект User.
    :raises HTTPException: Если пользователь не найден.
    """
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


async def get_user_by_apikey_with_following(
    session: AsyncSession, api_key: str
) -> User:
    """
    Получает пользователя по API-ключу, подгружая его подписки.

    Если пользователь найден, возвращается объект User.
    В противном случае вызывается исключение HTTPException
    с кодом 404 и сообщением "User not found".

    :param session: Асинхронная сессия SQLAlchemy.
    :param api_key: API-ключ пользователя.
    :return: Объект User.
    :raises HTTPException: Если пользователь не найден.
    """
    stmt = (
        select(User).where(User.apikey == api_key).options(joinedload(User.following))
    )
    result = await session.execute(stmt)
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


async def make_tweet_feed(tweets: Sequence[Tweet]) -> dict:
    """
    Формирует структуру данных для ленты твитов.

    :param tweets: Список твитов, для которых будет сформирована лента.
    :return: Словарь с данными о твитах, включая их контент, медиа, авторов и лайки.
    """
    return {
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


async def lazy_get_user_by_apikey(session: AsyncSession, api_key: str) -> User:
    """
    Получает пользователя по API-ключу без подгрузки дополнительных данных.

    Если пользователь найден, возвращается объект User.
    В противном случае вызывается исключение HTTPException
    с кодом 404 и сообщением "User not found".

    :param session: Асинхронная сессия SQLAlchemy.
    :param api_key: API-ключ пользователя.
    :return: Объект User.
    :raises HTTPException: Если пользователь не найден.
    """
    stmt = select(User).where(User.apikey == api_key)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


async def lazy_get_user_by_id(session: AsyncSession, user_id: int) -> User:
    """
    Получает пользователя по его ID без подгрузки дополнительных данных.

    Если пользователь найден, возвращается объект User.
    В противном случае вызывается исключение HTTPException
    с кодом 404 и сообщением "User not found".

    :param session: Асинхронная сессия SQLAlchemy.
    :param api_key: API-ключ пользователя.
    :return: Объект User.
    :raises HTTPException: Если пользователь не найден.
    """
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


async def json_about_user(user: User) -> dict:
    """
    Формирует словарь с информацией о пользователе и его подписках.

    :param user: Объект пользователя, содержащий данные о подписках и подписчиках.
    :return: Словарь с данными о пользователе, подписчиках и подписках.
    """
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
    """
    Функция получает все твиты из базы данных,
    подгружает все зависимые таблицы.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: Последовательность моделей твитов.
    """
    stmt = select(Tweet).options(
        joinedload(Tweet.author),
        joinedload(Tweet.likes).joinedload(Like.user),
        joinedload(Tweet.media),
    )
    result = await session.execute(stmt)
    tweets = result.scalars().unique().all()

    return tweets


async def get_tweet_by_id(session: AsyncSession, tweet_id: int) -> Tweet:
    """
    Функция получает твит по его ID и подгружает все зависимые таблицы.

    В случае если твит не найден, вызывается исключение
    HTTPException с кодом 404 и сообщением "Tweet not found".

    :param session: Асинхронная сессия SQLAlchemy.
    :param tweet_id: ID Твита.
    :return: Модель твита.
    """
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
        raise HTTPException(status_code=404, detail="Tweet not found")

    return tweets


async def lazy_get_tweet_by_id(tweet_id: int, session: AsyncSession) -> Tweet:
    """
    Функция получает твит по его ID без дополнительной подгрузки данных.

    В случае если твит не найден, вызывается исключение
    HTTPException с кодом 404 и сообщением "Tweet not found".

    :param session: Асинхронная сессия SQLAlchemy.
    :param tweet_id: ID Твита.
    :return: Модель твита.
    """
    stmt = select(Tweet).where(Tweet.id == tweet_id)
    result = await session.execute(stmt)
    tweet = result.scalars().first()

    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    return tweet


async def get_like(tweet_id: int, user_id: int, session: AsyncSession) -> Like:
    """
    Получает лайк на твите пользователя.

    Функция ищет лайк для конкретного твита, который
    поставил указанный пользователь. Если лайк не найден,
    генерируется исключение HTTPException с кодом 404 и
    сообщением "Like not found".

    :param tweet_id: ID твита, для которого ищется лайк.
    :param user_id: ID пользователя, который поставил лайк.
    :param session: Асинхронная сессия SQLAlchemy.
    :return: Объект Like, если лайк найден.
    :raises HTTPException: Если лайк не найден.
    """
    stmt = select(Like).filter(and_(Like.user_id == user_id, Like.tweet_id == tweet_id))
    result = await session.execute(stmt)
    like = result.scalars().first()

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    return like
