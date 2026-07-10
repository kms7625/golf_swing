"""DB 연결 계층 — DATABASE_URL 환경변수 하나로 dev(SQLite)↔prod(Supabase Postgres) 전환.

기본값은 server/ 옆의 SQLite 파일이라 외부 계정 없이 즉시 동작한다.
Supabase로 옮길 때는 DATABASE_URL=postgresql+psycopg://... 만 바꾸면 된다
(스키마는 SQLAlchemy가 동일하게 생성 — 상용화_검토보고서_2026-07-10.md 5장 판정).
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def _load_dotenv() -> None:
    """레포 루트 .env를 os.environ에 주입 (이미 설정된 키는 유지).

    docker-compose는 .env를 자체 처리하지만, 로컬 `uvicorn main:app` 개발 실행에서도
    같은 파일 하나로 DATABASE_URL/JWT_SECRET/LLM 키가 먹히도록 한다. 외부 의존성 없음.
    """
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value


_load_dotenv()

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
