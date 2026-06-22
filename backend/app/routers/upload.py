"""文件上传路由：头像、音视频"""
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import UPLOAD_AVATARS_DIR, UPLOAD_AUDIO_DIR, UPLOAD_VIDEO_DIR
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/upload", tags=["上传"])

ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
ALLOWED_AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
ALLOWED_VIDEO_EXT = {".mp4", ".webm", ".mov", ".mkv", ".avi"}


def _save(file: UploadFile, dest_dir: Path, allowed: set[str]) -> tuple[str, str, int]:
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型：{ext}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    new_name = f"{uuid.uuid4().hex}{ext}"
    full_path = dest_dir / new_name
    size = 0
    with open(full_path, "wb") as f:
        while chunk := file.file.read(1024 * 1024):
            f.write(chunk)
            size += len(chunk)
    return new_name, filename, size


@router.post("/avatar", response_model=schemas.UploadResult)
def upload_avatar(file: UploadFile = File(...), _user=Depends(get_current_user)):
    new_name, original, size = _save(file, UPLOAD_AVATARS_DIR, ALLOWED_IMAGE_EXT)
    url = f"/uploads/avatars/{new_name}"
    return {"url": url, "filename": original, "size": size}


@router.post("/media", response_model=schemas.Media)
def upload_media(
    file: UploadFile = File(...),
    inheritor_id: int = Form(...),
    type: str = Form(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    inheritor = db.query(models.Inheritor).filter(models.Inheritor.id == inheritor_id).first()
    if not inheritor:
        raise HTTPException(status_code=404, detail="传承人不存在")
    media_type = type.lower()
    if media_type == "audio":
        dest = UPLOAD_AUDIO_DIR
        allowed = ALLOWED_AUDIO_EXT
        sub = "audio"
    elif media_type == "video":
        dest = UPLOAD_VIDEO_DIR
        allowed = ALLOWED_VIDEO_EXT
        sub = "video"
    else:
        raise HTTPException(status_code=400, detail="type 必须是 audio 或 video")
    new_name, _, size = _save(file, dest, allowed)
    file_path = f"/uploads/{sub}/{new_name}"
    obj = models.Media(
        inheritor_id=inheritor_id,
        type=media_type,
        title=title,
        file_path=file_path,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return schemas.Media(
        id=obj.id, type=obj.type, title=obj.title, file_path=obj.file_path,
        description=obj.description,
    )
