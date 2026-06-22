"""剧种路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/genres", tags=["剧种"])


def _inheritor_to_list(ih: models.Inheritor) -> schemas.InheritorListItem:
    return schemas.InheritorListItem(
        id=ih.id,
        name=ih.name,
        pinyin_initial=ih.pinyin_initial,
        gender=ih.gender,
        birth_date=ih.birth_date,
        age_group=ih.age_group,
        genre_id=ih.genre_id,
        genre_name=ih.genre.name if ih.genre else None,
        role_type=ih.role_type,
        region=ih.region,
        avatar=ih.avatar,
        master_id=ih.master_id,
        master_name=ih.master.name if ih.master else None,
        bio=ih.bio,
    )


@router.get("", response_model=List[schemas.Genre])
def list_genres(db: Session = Depends(get_db)):
    genres = db.query(models.Genre).order_by(models.Genre.id.asc()).all()
    return genres


@router.get("/{genre_id}", response_model=schemas.GenreDetail)
def get_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="剧种不存在")
    inheritors = [_inheritor_to_list(ih) for ih in genre.inheritors]
    return schemas.GenreDetail(
        id=genre.id,
        name=genre.name,
        pinyin=genre.pinyin,
        history=genre.history,
        art_features=genre.art_features,
        classic_plays=genre.classic_plays,
        main_schools=genre.main_schools,
        distribution_areas=genre.distribution_areas,
        cover_image=genre.cover_image,
        inheritors=inheritors,
        troupes=genre.troupes,
    )
