from sqlalchemy import select

from fastapi import APIRouter, Header


from app.routes.utils import get_user_by_apikey_or_id, json_about_user, lazy_get_user_by_apikey_or_id
from database.confdb import Session
from database.models import User

router = APIRouter()

@router.get('/me')
async def get_me(api_key: str = Header(...)):
    """
    Получение информации о своем профиле.
    HTTP-Params: api-key: str

    В ответ получаем json файл со всей информацией или ошибку.
    """
    try:
        user: User = await get_user_by_apikey_or_id(api_key=api_key)
        result: dict = await json_about_user(user)

        return result

    except Exception as error:
        return {
            "result": False,
            "error_type": type(error).__name__,
            "error_messages": str(error)
        }


@router.get('/{user_id}')
async def user_by_id(user_id:int):
    try:
        user: User = await get_user_by_apikey_or_id(user_id=user_id)
        result: dict = await json_about_user(user)

        return result

    except Exception as error:
        return {
            "result": False,
            "error_type": type(error).__name__,
            "error_messages": str(error)
        }

@router.post('/{user_id}/follow')
async def post_users_follow(user_id:int, api_key:str=Header(...)):
    """
    Пользователь может зафоловить другого пользователя.

    POST /api/users/<id>/follow
    HTTP-Params:
    api-key: str

    В ответ должно вернуться сообщение о статусе операции.
    {
        “result”: true
    }
    """
    try:
        async with Session() as session:
            user: User = await get_user_by_apikey_or_id(api_key=api_key)
            follow: User = await lazy_get_user_by_apikey_or_id(user_id=user_id)

            if follow not in user.following:
                user.following.append(follow)
            else:
                raise ValueError('The user is already subscribed to this user')

            await session.commit()
            return {"result": True}


    except Exception as error:
        return {
            "result": False,
            "error_type": type(error).__name__,
            "error_messages": str(error)
        }



