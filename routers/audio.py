import os
import re
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pydub import AudioSegment

from crud.audio import CRUDAudio
from crud.user import CRUDUser
from depedences.common import RequiredRoles
from depedences.cruds import get_audio_crud, get_users_crud
from models.client import UserRole
from models.token import TokenData
from schemas.schema import AudioSchema, AudioSchemaReq, CreateUserReq

UPLOADED_FILES_PATH = "uploaded_files/"
ROUTER = APIRouter(prefix="/audio", tags=["Audio"])


async def save_file_to_uploads(user_folder, file, filename):
    try:
        os.makedirs(f"{UPLOADED_FILES_PATH}{user_folder}/")
    except FileExistsError:
        print("This directory already exists")
    with open(f"{UPLOADED_FILES_PATH}{user_folder}/{filename}", "wb") as uploaded_file:
        file_content = await file.read()
        uploaded_file.write(file_content)
        uploaded_file.close()
        AudioSegment.from_wav(f"uploaded_files/{user_folder}/{filename}").export(
            f"uploaded_files/{user_folder}/{filename.replace('.wav', '')}.mp3",
            format="mp3",
        )
        if os.path.isfile(f"{UPLOADED_FILES_PATH}{user_folder}/{filename}"):
            os.remove(f"{UPLOADED_FILES_PATH}{user_folder}/{filename}")


def generate_record_url(record_id: str, user_id: str, host: str) -> str:
    return f"http://{host}/audio/record?record_id={record_id}&user_id={user_id}"


@ROUTER.post("file/upload-file")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    token: TokenData = Depends(RequiredRoles([UserRole.user, UserRole.admin])),
    audio_crud: CRUDAudio = Depends(get_audio_crud),
):
    filename = file.filename
    user_folder = token.user_id
    mp3_path = f"uploaded_files/{user_folder}/" + filename.replace(".wav", ".mp3")
    if mp3_path in await audio_crud.get_links_from_db(token.user_id):
        raise HTTPException(status_code=400, detail="This record already exists")
    await save_file_to_uploads(file=file, filename=filename, user_folder=token.user_id)
    new_audio = AudioSchemaReq(link=mp3_path, user_id=token.user_id)
    created_audio = await audio_crud.create_audio(obj_in=new_audio)
    record_path = generate_record_url(
        user_id=str(token.user_id),
        record_id=str(created_audio.id),
        host=request.headers.get("host"),
    )
    return record_path


@ROUTER.get("/record")
async def download_audio(link: str, audio_crud: CRUDAudio = Depends(get_audio_crud)):
    try:
        link_data = re.findall(r"record_id=(.*)(&)user_id=(.*)", link)
        audio_path = await audio_crud.get_by_user_id_record_id(
            record_id=link_data[0][0], user_id=link_data[0][2]
        )
        if audio_path:
            file_name = audio_path.link[52:]
            return FileResponse(
                audio_path.link, filename=file_name, media_type="multipart/form-data"
            )
    except:
        raise HTTPException(
            status_code=404, detail="Record not found or check your link"
        )


@ROUTER.get("/audio_urls")
async def audio_urls(request: Request, audio_crud: CRUDAudio = Depends(get_audio_crud)):
    audios = await audio_crud.get_audio_info()
    all_urls = []
    for i in audios:
        url = generate_record_url(
            record_id=i.id, user_id=i.user_id, host=request.headers.get("host")
        )
        all_urls.append({i.link[52:]: url})
    return all_urls


@ROUTER.delete("/delete_audio_by_admin")
async def delete_audio(
    record_id: UUID,
    token: TokenData = Depends(RequiredRoles([UserRole.admin])),
    audio_crud: CRUDAudio = Depends(get_audio_crud),
):
    audio = await audio_crud.get_record_title(record_id=record_id)
    if not audio:
        raise HTTPException(status_code=404, detail=f"No such record as {record_id}")
    os.remove(audio.link)
    return await audio_crud.del_from_db(record_id)


@ROUTER.delete("/delete_audio_by_user")
async def user_delete_audio(
    record_id: UUID,
    token: TokenData = Depends(RequiredRoles([UserRole.user, UserRole.admin])),
    audio_crud: CRUDAudio = Depends(get_audio_crud),
):
    user_audio = await audio_crud.get_by_user_id_record_id(
        user_id=token.user_id, record_id=record_id
    )
    if not user_audio:
        raise HTTPException(status_code=404, detail=f"No such record as {record_id}")
    os.remove(user_audio.link)
    return await audio_crud.user_del_audio_from_db(
        record_id=record_id, user_id=token.user_id
    )
