from server.database.confdb import Session
from server.database.models import User
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession


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
        raise ValueError("User not found")

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
        raise ValueError("User not found")


async def lazy_get_user_by_apikey_or_id(
    session: AsyncSession, api_key: str = None, user_id: int = None
) -> User:

    if api_key:
        stmt = select(User).where(User.apikey == api_key)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            return user
        raise ValueError("User not found")

    if user_id:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            return user
        raise ValueError("User not found")


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
