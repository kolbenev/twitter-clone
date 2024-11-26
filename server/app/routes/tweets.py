import os
from typing import Sequence

from sqlalchemy.future import select

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse

from server.app.routes.utils import (
    lazy_get_user_by_apikey,
    get_all_tweet,
    get_user_by_apikey,
    lazy_get_tweet_by_id,
    get_like,
    get_tweet_by_id,
    make_tweet_feed,
)
from server.database.confdb import session
from server.database.models import Tweet, User, Media, Like


router = APIRouter()


@router.get("/")
async def tweets(api_key: str = Header(...)) -> JSONResponse:
    """
    Получает ленту твитов для текущего пользователя.

    Функция извлекает все твиты из базы данных и формирует ленту твитов.
    Лента включает в себя информацию о контенте твитов, медиа-материалах
    и лайках. Для получения данных используется API-ключ текущего пользователя.

    :param api_key: API-ключ текущего пользователя, используемый для аутентификации.
    :return: Ответ в формате JSON с лентой твитов.
    """
    user: User = await lazy_get_user_by_apikey(session=session, api_key=api_key)
    tweets: Sequence[Tweet] = await get_all_tweet(session=session)
    tweet_feed: dict = await make_tweet_feed(tweets=tweets)

    return JSONResponse(tweet_feed)


@router.post("/")
async def post_tweets(tweet_data: dict, api_key: str = Header(...)) -> JSONResponse:
    """
    Создает новый твит.

    Функция создает новый твит с предоставленным контентом и
    прикрепленными медиа-материалами. Если твит не содержит
    данных, выбрасывается ошибка с кодом 400. После успешного
    добавления твита в базу данных возвращается ответ с результатом
    операции и ID созданного твита.

    :param tweet_data: Данные твита, включая текст твита и список ID медиа-материалов.
    :param api_key: API-ключ текущего пользователя, использующего функцию.
    :return: Ответ в формате JSON с результатом операции и ID созданного твита.
    :raises HTTPException: Если твит пустой (отсутствует контент).
    """
    user: User = await lazy_get_user_by_apikey(session=session, api_key=api_key)

    if not tweet_data:
        raise HTTPException(status_code=400, detail="Tweet is empty")

    content = tweet_data.get("tweet_data")
    new_tweet = Tweet(content=content, author_id=user.id)
    session.add(new_tweet)
    await session.flush()

    media_ids = tweet_data.get("tweet_media_ids", [])
    if media_ids:
        media_query = await session.execute(
            select(Media).where(Media.id.in_(media_ids))
        )
        media_items = media_query.scalars().all()
        for media in media_items:
            media.tweet_id = new_tweet.id
            session.add(media)

    await session.commit()

    return JSONResponse({"result": True, "tweet_id": new_tweet.id})


@router.post("/{tweet_id}/likes")
async def like_the_tweet(tweet_id: int, api_key: str = Header(...)) -> JSONResponse:
    """
    Лайк твита.

    Функция позволяет пользователю поставить лайк на твит.
    Если пользователь уже поставил лайк, возвращается
    ошибка с кодом 400. Если лайк еще не поставлен,
    он добавляется в базу данных.

    :param tweet_id: ID твита, на который ставится лайк.
    :param api_key: API-ключ текущего пользователя, использующего функцию.
    :return: Ответ в формате JSON с результатом операции.
    :raises HTTPException: Если твит уже был лайкнут пользователем.
    """
    user: User = await lazy_get_user_by_apikey(session=session, api_key=api_key)
    tweet: Tweet = await lazy_get_tweet_by_id(tweet_id=tweet_id, session=session)

    try:
        like: Like = await get_like(user_id=user.id, tweet_id=tweet.id, session=session)
    except HTTPException:
        session.add(Like(user_id=user.id, tweet_id=tweet.id))
        await session.commit()

        return JSONResponse({"result": True})

    raise HTTPException(status_code=400, detail="Already liked the tweet")


@router.delete("/{tweet_id}/likes")
async def delete_like_on_the_tweet(
    tweet_id: int, api_key: str = Header(...)
) -> JSONResponse:
    """
    Удаление лайка с твита.

    Функция позволяет пользователю удалить свой лайк с твита.
    Если лайк существует, он удаляется из базы данных.
    В случае успешного выполнения возвращается ответ с
    результатом операции.

    :param tweet_id: ID твита, с которого удаляется лайк.
    :param api_key: API-ключ текущего пользователя, использующего функцию.
    :return: Ответ в формате JSON с результатом операции.
    :raises HTTPException: Если лайк не был найден.
    """
    user: User = await lazy_get_user_by_apikey(session=session, api_key=api_key)
    tweet: Tweet = await lazy_get_tweet_by_id(tweet_id=tweet_id, session=session)
    like: Like = await get_like(user_id=user.id, tweet_id=tweet.id, session=session)

    await session.delete(like)
    await session.commit()

    return JSONResponse({"result": True})


@router.delete("/{tweet_id}")
async def delete_tweet(tweet_id: int, api_key: str = Header(...)) -> JSONResponse:
    """
    Удаление твита.

    Функция позволяет пользователю удалить твит,
    если он является автором этого твита. При удалении
    твита также удаляются связанные медиафайлы с сервера.
    Если пользователь не является автором твита, возвращается
    ошибка с кодом 403.

    :param tweet_id: ID твита, который нужно удалить.
    :param api_key: API-ключ текущего пользователя, использующего функцию.
    :return: Ответ в формате JSON с результатом операции.
    :raises HTTPException: Если пользователь не является автором твита.
    """
    user: User = await get_user_by_apikey(api_key=api_key, session=session)
    tweet: Tweet = await get_tweet_by_id(tweet_id=tweet_id, session=session)

    if tweet.author_id == user.id:
        for media in tweet.media:
            if os.path.exists(media.file_path):
                os.remove(media.file_path)

        await session.delete(tweet)
        await session.commit()

        return JSONResponse({"result": True})

    else:
        raise HTTPException(
            status_code=403, detail="The user is not the author of the tweet"
        )
