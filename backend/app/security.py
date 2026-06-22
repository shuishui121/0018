"""安全工具：密码哈希与 JWT"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import jwt

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def _prepare(password: str) -> bytes:
    """bcrypt 仅前 72 字节有效，UTF-8 编码后截断，避免 passlib 报错"""
    encoded = password.encode("utf-8")
    return encoded[:72]


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码：使用 bcrypt"""
    try:
        return bcrypt.checkpw(_prepare(plain), hashed.encode("utf-8"))
    except Exception:
        return False


def hash_password(plain: str) -> str:
    """哈希密码：使用 bcrypt"""
    salted = bcrypt.hashpw(_prepare(plain), bcrypt.gensalt(rounds=10))
    return salted.decode("utf-8")


def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data.get("sub")
    except Exception:
        return None
