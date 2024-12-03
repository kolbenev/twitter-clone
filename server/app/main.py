"""
Модуль запуска приложения FastAPI.

Запуск происходит из корневой папки, с помощью uvicorn.
"""

from fastapi import FastAPI

from server.app.routes.users import router as users_router
from server.app.routes.tweets import router as tweets_router
from server.app.routes.medias import router as medias_router


app = FastAPI()

app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(tweets_router, prefix="/api/tweets", tags=["tweets"])
app.include_router(medias_router, prefix="/api/medias", tags=["medias"])
