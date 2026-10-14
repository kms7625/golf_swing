"""인증 — Google 로그인 전용, JWT 발급/검증.

이메일+비밀번호 가입은 무료 코칭 횟수를 노린 계정 양산을 막기 위해 제거했다(2026-10-14).
Google ID 토큰을 PyJWT로 검증하고, 자체 JWT를 발급한다.
JWT_SECRET 미설정 시 서버 재시작마다 세션이 무효화되도록 랜덤 시크릿을 쓴다
(prod에서는 반드시 env로 고정할 것 — .env.example 참조).
"""
import os
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

_bearer = HTTPBearer(auto_error=False)

# Google 로그인 — GOOGLE_CLIENT_ID가 비어 있으면 비활성. ID 토큰은 Google 공개키(JWKS)로 PyJWT가 검증한다.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
_GOOGLE_ISSUERS = ("accounts.google.com", "https://accounts.google.com")
_google_jwks = jwt.PyJWKClient("https://www.googleapis.com/oauth2/v3/certs")
GOOGLE_PASSWORD_MARK = "google"  # password_hash 컬럼 자리값 — 비밀번호 로그인은 없음


def verify_google_credential(credential: str) -> Optional[str]:
    """Google ID 토큰을 검증해 확인된 이메일(소문자)을 돌려준다. 실패하면 None."""
    try:
        key = _google_jwks.get_signing_key_from_jwt(credential).key
        data = jwt.decode(credential, key, algorithms=["RS256"], audience=GOOGLE_CLIENT_ID)
    except jwt.PyJWTError:
        return None
    if data.get("iss") not in _GOOGLE_ISSUERS or not data.get("email_verified"):
        return None
    return str(data.get("email", "")).strip().lower() or None


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
