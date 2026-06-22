"""数据库连接与会话"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def ensure_extensions():
    """启用 pg_trgm 扩展"""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.commit()


def create_indexes():
    """创建必要的索引（包含 GIN 模糊搜索索引）"""
    from sqlalchemy import Index, text
    from . import models  # noqa: F401

    with engine.connect() as conn:
        index_statements = [
            "CREATE INDEX IF NOT EXISTS idx_inheritors_name_trgm ON inheritors USING GIN (name gin_trgm_ops)",
            "CREATE INDEX IF NOT EXISTS idx_inheritors_genre ON inheritors(genre_id)",
            "CREATE INDEX IF NOT EXISTS idx_inheritors_role ON inheritors(role_type)",
            "CREATE INDEX IF NOT EXISTS idx_inheritors_region ON inheritors(region)",
            "CREATE INDEX IF NOT EXISTS idx_inheritors_age ON inheritors(age_group)",
            "CREATE INDEX IF NOT EXISTS idx_inheritors_pinyin ON inheritors(pinyin_initial)",
            "CREATE INDEX IF NOT EXISTS idx_inheritors_master ON inheritors(master_id)",
            "CREATE INDEX IF NOT EXISTS idx_inheritors_name ON inheritors(name)",
        ]
        for stmt in index_statements:
            conn.execute(text(stmt))
        conn.commit()


def init_db():
    """初始化数据库表结构"""
    ensure_extensions()
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    create_indexes()


def get_db():
    """依赖项：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
