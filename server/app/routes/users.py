from fastapi import APIRouter, Header


from server.app.routes.utils import (
    get_user_by_apikey_or_id,
    json_about_user,
    lazy_get_user_by_apikey_or_id,
)
from server.database.confdb import Session, session
from server.database.models import User

router = APIRouter()


@router.get("/me")
async def get_me(api_key: str = Header(...)):
    """
    Получение информации о своем профиле.

    В ответ получаем json файл со всей информацией или ошибку.
    """

    try:
        user: User = await get_user_by_apikey_or_id(api_key=api_key, session=session)
        result: dict = await json_about_user(user)

        return result

    except Exception as error:
        return {
            "result": False,
            "error_type": type(error).__name__,
            "error_messages": str(error),
        }


@router.get("/{user_id}")
async def user_by_id(user_id: int):
    """
    Получение информации о пользователе по id.
    """

    try:
        user: User = await get_user_by_apikey_or_id(user_id=user_id, session=session)
        result: dict = await json_about_user(user)

        return result

    except Exception as error:
        return {
            "result": False,
            "error_type": type(error).__name__,
            "error_messages": str(error),
        }


@router.post("/{user_id}/follow")
async def post_users_follow(user_id: int, api_key: str = Header(...)):
    """
    Подписка на другого пользователя.
    """

    try:
        async with Session() as session:
            user: User = await get_user_by_apikey_or_id(
                api_key=api_key, session=session
            )
            follow: User = await lazy_get_user_by_apikey_or_id(
                user_id=user_id, session=session
            )

            if follow not in user.following:
                user.following.append(follow)
            else:
                raise ValueError(f"{user.name} is already subscribed to {follow.name}")

            await session.commit()
            return {"result": True}

    except Exception as error:
        return {
            "result": False,
            "error_type": type(error).__name__,
            "error_messages": str(error),
        }


@router.delete("/{user_id}/follow")
async def delete_users_follow(user_id: int, api_key: str = Header(...)):
    """
    Отписка от пользователя.
    """

    try:
        async with Session() as session:
            user: User = await get_user_by_apikey_or_id(
                api_key=api_key, session=session
            )
            follow: User = await lazy_get_user_by_apikey_or_id(
                user_id=user_id, session=session
            )

            if follow in user.following:
                user.following.remove(follow)
            else:
                raise ValueError(f"{user.name} doesn't follow {follow.name}")

            await session.commit()
            return {"result": True}

    except Exception as error:
        return {
            "result": False,
            "error_type": type(error).__name__,
            "error_messages": str(error),
        }
