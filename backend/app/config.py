"""全局配置"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_AVATARS_DIR = UPLOAD_DIR / "avatars"
UPLOAD_AUDIO_DIR = UPLOAD_DIR / "audio"
UPLOAD_VIDEO_DIR = UPLOAD_DIR / "video"

for d in (UPLOAD_AVATARS_DIR, UPLOAD_AUDIO_DIR, UPLOAD_VIDEO_DIR):
    d.mkdir(parents=True, exist_ok=True)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/lydc",
)

SECRET_KEY = os.getenv("SECRET_KEY", "lydc-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "10080"))  # 一周 = 60 * 24 * 7

DEFAULT_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
