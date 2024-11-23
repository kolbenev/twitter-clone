import os
from urllib.parse import urljoin

from fastapi import APIRouter, Header, UploadFile, HTTPException

from server.database.confdb import session
from server.database.models import User, Media
from server.app.routes.utils import lazy_get_user_by_apikey_or_id

router = APIRouter()
BASE_URL = "http://localhost"


@router.post("/")
async def post_medias(file: UploadFile, api_key: str = Header(...)):
    user: User = await lazy_get_user_by_apikey_or_id(api_key=api_key, session=session)

    if not file:
        raise HTTPException(status_code=400, detail="No file upload")

    media_dir = f"server/medias/"
    os.makedirs(media_dir, exist_ok=True)
    file_path = os.path.join(media_dir, file.filename)

    with open(file_path, "wb") as medias_file:
        content = await file.read()
        medias_file.write(content)

    file_url = urljoin(BASE_URL, f"medias/{file.filename}")

    new_media = Media(file_path=file_path, file_url=file_url)
    session.add(new_media)
    await session.commit()

    return {"result": True, "media_id": new_media.id}
