"""인증 — 이메일+비밀번호 자체 계정, JWT 발급/검증.

외부 IdP 없이 동작하는 자체 완결 구성(pbkdf2 해시 + PyJWT).
Supabase Auth로 갈아탈 경우 이 모듈만 교체하면 된다.
JWT_SECRET 미설정 시 서버 재시작마다 세션이 무효화되도록 랜덤 시크릿을 쓴다
(prod에서는 반드시 env로 고정할 것 — .env.example 참조).
"""
import hashlib
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from db import get_db
from models import User

JWT_SECRET = os.environ.get("JWT_SECRET") or secrets.token_hex(32)
JWT_ALGO = "HS256"
TOKEN_TTL_DAYS = int(os.environ.get("TOKEN_TTL_DAYS", "30"))

_PBKDF2_ITER = 240_000
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _PBKDF2_ITER).hex()
    return f"pbkdf2${_PBKDF2_ITER}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt, digest = stored.split("$")
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iters)).hex()
        return secrets.compare_digest(candidate, digest)
    except (ValueError, TypeError):
        return False


def validate_credentials(email: str, password: str) -> Optional[str]:
    """가입 입력 검증 — 문제 없으면 None, 있으면 한국어 사유(서버 메시지는 한국어 원칙)."""
    if not _EMAIL_RE.match(email):
        return "올바른 이메일 형식이 아닙니다."
    if len(password) < 8:
        return "비밀번호는 8자 이상이어야 합니다."
    return None


def create_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user.id), "email": user.email, "iat": now, "exp": now + timedelta(days=TOKEN_TTL_DAYS)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def _decode(token: str) -> Optional[int]:
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return int(data["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """로그인 필수 의존성."""
    if creds is None:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    user_id = _decode(creds.credentials)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었습니다. 다시 로그인해주세요.")
    return user


def get_optional_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """비로그인도 허용하는 의존성 (게스트 분석 흐름 유지)."""
    if creds is None:
        return None
    user_id = _decode(creds.credentials)
    return db.get(User, user_id) if user_id is not None else None
