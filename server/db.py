"""DB 연결 계층 — DATABASE_URL 환경변수 하나로 dev(SQLite)↔prod(Supabase Postgres) 전환.

기본값은 server/ 옆의 SQLite 파일이라 외부 계정 없이 즉시 동작한다.
Supabase로 옮길 때는 DATABASE_URL=postgresql+psycopg://... 만 바꾸면 된다
(스키마는 SQLAlchemy가 동일하게 생성 — 상용화_검토보고서_2026-07-10.md 5장 판정).
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

_DEFAULT_SQLITE = "sqlite:///" + os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "golf.db"
).replace("\\", "/")

DATABASE_URL = os.environ.get("DATABASE_URL", _DEFAULT_SQLITE)

_engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    # FastAPI는 요청마다 스레드가 다를 수 있음 — SQLite 기본 체크 해제
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    # models를 import해야 테이블 메타데이터가 등록된다
    import models  # noqa: F401

    Base.metadata.create_all(engine)


def get_db():
    """FastAPI Depends용 세션 팩토리."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
