"""
Модуль роутов /api/users/
"""

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from server.app.loggerconf import logger
from server.app.routes.utils import (
    get_user_by_apikey,
    get_user_by_id,
    json_about_user,
    lazy_get_user_by_id,
)
from server.database.confdb import session
from server.database.models import User

router = APIRouter()


@router.get("/me")
async def get_me(api_key: str = Header(...)) -> JSONResponse:
    """
    Получает информацию о текущем пользователе по API-ключу.

    Функция извлекает данные о пользователе с помощью переданного API-ключа,
    а затем формирует ответ с информацией о пользователе, включая его подписчиков и подписки.

    :param api_key: API-ключ пользователя.
    :return: Ответ в формате JSON с информацией о пользователе.
    """
    user: User = await get_user_by_apikey(api_key=api_key, session=session)
    result: dict = await json_about_user(user)

    return JSONResponse(result)


@router.get("/{user_id}")
async def user_by_id(user_id: int) -> JSONResponse:
    """
    Получает информацию о текущем пользователе по его ID.

    Функция извлекает данные о пользователе с помощью переданного ID,
    а затем формирует ответ с информацией о пользователе, включая его подписчиков и подписки.

    :param user_id: ID пользователя.
    :return: Ответ в формате JSON с информацией о пользователе.
    """
    user: User = await get_user_by_id(user_id=user_id, session=session)
    result: dict = await json_about_user(user)

    return JSONResponse(result)


@router.post("/{user_id}/follow")
async def post_users_follow(user_id: int, api_key: str = Header(...)) -> JSONResponse:
    """
    Подписка на другого пользователя.

    Функция позволяет пользователю подписаться на другого пользователя по его ID.
    Если пользователь уже подписан, возвращается ошибка с кодом 400 и сообщением,
    {user.name} is already subscribed to {follow.name}

    :param user_id: ID пользователя, на которого нужно подписаться.
    :param api_key: API-ключ текущего пользователя, использующего функцию.
    :return: Ответ в формате JSON с результатом операции.
    :raises HTTPException: Если пользователь уже подписан на другого.
    """
    user: User = await get_user_by_apikey(api_key=api_key, session=session)
    follow: User = await lazy_get_user_by_id(user_id=user_id, session=session)

    if user.id == follow.id:
        raise HTTPException(
            status_code=400,
            detail=f"Trying to subscribe to yourself",
        )
    elif follow not in user.following:
        user.following.append(follow)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"{user.name} is already subscribed to {follow.name}",
        )

    logger.info(f"{user.name} subscribed to {follow.name}")
    await session.commit()
    return JSONResponse({"result": True})


@router.delete("/{user_id}/follow")
async def delete_users_follow(user_id: int, api_key: str = Header(...)) -> JSONResponse:
    """
    Отписка от пользователя.

    Функция позволяет пользователю отписаться от другого пользователя по его ID.
    Если пользователь не подписан, возвращается ошибка с кодом 400 и сообщением,
    {user.name} doesn't follow {follow.name}

    :param user_id: ID пользователя, на которого нужно подписаться.
    :param api_key: API-ключ текущего пользователя, использующего функцию.
    :return: Ответ в формате JSON с результатом операции.
    :raises HTTPException: Если пользователь уже подписан на другого.
    """
    user: User = await get_user_by_apikey(api_key=api_key, session=session)
    follow: User = await lazy_get_user_by_id(user_id=user_id, session=session)

    if follow in user.following:
        user.following.remove(follow)
    else:
        raise HTTPException(
            status_code=400, detail=f"{user.name} doesn't follow {follow.name}"
        )

    logger.info(f"{user.name} unfollowed {follow.name}")
    await session.commit()

    return JSONResponse({"result": True})
