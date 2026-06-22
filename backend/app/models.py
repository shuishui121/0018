"""ORM 数据模型"""
from sqlalchemy import (
    Column, Integer, String, Text, Date, ForeignKey, Index
)
from sqlalchemy.orm import relationship

from .database import Base


class Genre(Base):
    """剧种"""
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    pinyin = Column(String(128), nullable=True)
    history = Column(Text, nullable=True)
    art_features = Column(Text, nullable=True)
    classic_plays = Column(Text, nullable=True)
    main_schools = Column(Text, nullable=True)
    distribution_areas = Column(Text, nullable=True)
    cover_image = Column(String(256), nullable=True)

    inheritors = relationship("Inheritor", back_populates="genre")
    troupes = relationship("Troupe", back_populates="genre")
    plays = relationship("Play", back_populates="genre")


class Inheritor(Base):
    """传承人"""
    __tablename__ = "inheritors"
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    pinyin_initial = Column(String(1), nullable=True, index=True)
    gender = Column(String(8), nullable=True)
    birth_date = Column(Date, nullable=True)
    age_group = Column(String(16), nullable=True, index=True)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=True, index=True)
    role_type = Column(String(32), nullable=True, index=True)
    region = Column(String(64), nullable=True, index=True)
    master_id = Column(Integer, ForeignKey("inheritors.id"), nullable=True, index=True)
    avatar = Column(String(256), nullable=True)
    bio = Column(Text, nullable=True)

    genre = relationship("Genre", back_populates="inheritors")
    master = relationship("Inheritor", remote_side=[id])
    learning = relationship("Learning", back_populates="inheritor", cascade="all, delete-orphan")
    plays_link = relationship("InheritorPlay", back_populates="inheritor", cascade="all, delete-orphan")
    awards = relationship("Award", back_populates="inheritor", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="inheritor", cascade="all, delete-orphan")


class Play(Base):
    """剧目"""
    __tablename__ = "plays"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=True)
    description = Column(Text, nullable=True)

    genre = relationship("Genre", back_populates="plays")


class InheritorPlay(Base):
    """传承人-剧目关联（含饰演角色）"""
    __tablename__ = "inheritor_plays"
    id = Column(Integer, primary_key=True)
    inheritor_id = Column(Integer, ForeignKey("inheritors.id", ondelete="CASCADE"), nullable=False)
    play_id = Column(Integer, ForeignKey("plays.id"), nullable=True)
    role_name = Column(String(64), nullable=True)

    inheritor = relationship("Inheritor", back_populates="plays_link")
    play = relationship("Play")


class Learning(Base):
    """学艺经历"""
    __tablename__ = "learning"
    id = Column(Integer, primary_key=True)
    inheritor_id = Column(Integer, ForeignKey("inheritors.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=True)
    title = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)

    inheritor = relationship("Inheritor", back_populates="learning")


class Award(Base):
    """获奖"""
    __tablename__ = "awards"
    id = Column(Integer, primary_key=True)
    inheritor_id = Column(Integer, ForeignKey("inheritors.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(128), nullable=True)
    year = Column(Integer, nullable=True)
    level = Column(String(32), nullable=True)

    inheritor = relationship("Inheritor", back_populates="awards")


class Media(Base):
    """录音录像资料"""
    __tablename__ = "media"
    id = Column(Integer, primary_key=True)
    inheritor_id = Column(Integer, ForeignKey("inheritors.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(16), nullable=True)
    title = Column(String(128), nullable=True)
    file_path = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)

    inheritor = relationship("Inheritor", back_populates="media")


class Troupe(Base):
    """剧团"""
    __tablename__ = "troupes"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=True)
    region = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)

    genre = relationship("Genre", back_populates="troupes")


class InheritorRelation(Base):
    """传承人多维度关系（除师徒外的亲属、同门等）"""
    __tablename__ = "inheritor_relations"
    id = Column(Integer, primary_key=True)
    from_inheritor_id = Column(Integer, ForeignKey("inheritors.id", ondelete="CASCADE"), nullable=False, index=True)
    to_inheritor_id = Column(Integer, ForeignKey("inheritors.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(32), nullable=False, index=True)
    description = Column(String(256), nullable=True)

    from_inheritor = relationship("Inheritor", foreign_keys=[from_inheritor_id])
    to_inheritor = relationship("Inheritor", foreign_keys=[to_inheritor_id])

    __table_args__ = (
        Index("idx_relation_pair", "from_inheritor_id", "to_inheritor_id", "relation_type", unique=True),
    )


class User(Base):
    """管理员用户"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(16), default="admin")
