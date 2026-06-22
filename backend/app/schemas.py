"""Pydantic Schema —— 严格与前端 api.ts 字段对齐"""
from typing import Optional, List, Generic, TypeVar
from datetime import date

from pydantic import BaseModel, Field

T = TypeVar("T")


# ==================== 公共 ====================
class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int


# ==================== 剧种 ====================
class Genre(BaseModel):
    id: int
    name: str
    pinyin: Optional[str] = None
    history: Optional[str] = None
    art_features: Optional[str] = None
    classic_plays: Optional[str] = None
    main_schools: Optional[str] = None
    distribution_areas: Optional[str] = None
    cover_image: Optional[str] = None

    class Config:
        from_attributes = True


class Troupe(BaseModel):
    id: int
    name: str
    genre_id: Optional[int] = None
    region: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== 传承人 ====================
class InheritorListItem(BaseModel):
    id: int
    name: str
    pinyin_initial: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    age_group: Optional[str] = None
    genre_id: Optional[int] = None
    genre_name: Optional[str] = None
    role_type: Optional[str] = None
    region: Optional[str] = None
    avatar: Optional[str] = None
    master_id: Optional[int] = None
    master_name: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True


class Learning(BaseModel):
    id: int
    year: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class InheritorPlay(BaseModel):
    id: int
    play_id: Optional[int] = None
    play_name: Optional[str] = None
    role_name: Optional[str] = None

    class Config:
        from_attributes = True


class Award(BaseModel):
    id: int
    name: Optional[str] = None
    year: Optional[int] = None
    level: Optional[str] = None

    class Config:
        from_attributes = True


class Media(BaseModel):
    id: int
    type: Optional[str] = None
    title: Optional[str] = None
    file_path: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class InheritorDetail(InheritorListItem):
    learning: List[Learning] = Field(default_factory=list)
    plays: List[InheritorPlay] = Field(default_factory=list)
    awards: List[Award] = Field(default_factory=list)
    media: List[Media] = Field(default_factory=list)


class InheritorInput(BaseModel):
    name: str
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    age_group: Optional[str] = None
    genre_id: Optional[int] = None
    role_type: Optional[str] = None
    region: Optional[str] = None
    master_id: Optional[int] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None


# ==================== 剧种详情 ====================
class GenreDetail(Genre):
    inheritors: List[InheritorListItem] = Field(default_factory=list)
    troupes: List[Troupe] = Field(default_factory=list)


# ==================== 批量导入 ====================
class BatchImportResult(BaseModel):
    total: int
    success: int
    failed: int
    errors: List[str] = Field(default_factory=list)
    elapsed_ms: int


# ==================== 上传 ====================
class UploadResult(BaseModel):
    url: str
    filename: str
    size: int


# ==================== 鉴权 ====================
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
