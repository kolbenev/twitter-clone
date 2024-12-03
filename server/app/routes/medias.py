"""
Модуль роута /api/medias/
"""

import os
from urllib.parse import urljoin
import random
import string
import aiofiles

from fastapi import APIRouter, Header, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from server.database.confdb import session
from server.database.models import User, Media
from server.app.routes.utils import lazy_get_user_by_apikey
from server.app.loggerconf import logger


router = APIRouter()
BASE_URL = "http://127.0.0.1"


@router.post("/")
async def post_medias(file: UploadFile, api_key: str = Header(...)) -> JSONResponse:
    """
    Загружает медиафайл на сервер.

    Функция позволяет пользователю загрузить медиафайл
    на сервер. Если файл не был загружен, возвращается
    ошибка с кодом 400. Файл сохраняется в директории,
    привязанной к пользователю, и генерируется уникальное
    имя для файла. После успешной загрузки медиафайл
    сохраняется в базе данных, и возвращается ответ с
    результатом операции и ID нового медиафайла.

    :param file: Загружаемый файл.
    :param api_key: API-ключ текущего пользователя, использующего функцию.
    :return: Ответ в формате JSON с результатом операции и ID загруженного медиафайла.
    :raises HTTPException: Если файл не был загружен.
    """
    user: User = await lazy_get_user_by_apikey(api_key=api_key, session=session)

    if not file:
        logger.warning(
            f"User {user.name}:{user.id} attempted to upload a media file but no file was provided."
        )
        raise HTTPException(status_code=400, detail="No file upload")

    media_dir = f"server/medias/{user.id}"
    os.makedirs(media_dir, exist_ok=True)

    file_format = file.filename.split(".")[-1]
    new_file_name = f"{''.join(random.choice(string.ascii_letters) for _ in range(10))}.{file_format}"

    file_path = os.path.join(media_dir, new_file_name)

    async with aiofiles.open(file_path, "wb") as medias_file:
        content = await file.read()
        await medias_file.write(content)
        logger.info(f"User {user.name}:{user.id} uploaded a new file: {file_path}")

    file_url = urljoin(BASE_URL, f"medias/{user.id}/{new_file_name}")

    new_media = Media(file_path=file_path, file_url=file_url)
    session.add(new_media)
    await session.flush()
    logger.info(f"Media file saved to database with ID: {new_media.id}")

    return JSONResponse({"result": True, "media_id": new_media.id})
