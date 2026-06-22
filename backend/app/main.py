"""FastAPI 主入口"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import UPLOAD_DIR, BASE_DIR
from .database import init_db, SessionLocal
from .seed import seed
from .routers import auth, genres, inheritors, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    """生命周期：启动时建表 + 种子数据"""
    init_db()
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(
    title="梨园典藏 · 戏曲传承人口齿录管理系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# 静态文件（头像、音视频）
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 路由
app.include_router(auth.router, prefix="/api")
app.include_router(genres.router, prefix="/api")
app.include_router(inheritors.router, prefix="/api")
app.include_router(upload.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "梨园典藏 API"}
