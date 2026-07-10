"""테스트 공용 설정 — 서버 모듈 import 전에 격리 env를 강제한다.

server/db.py는 import 시점에 DATABASE_URL을 읽고 레포 루트 .env를 로드하므로
(이미 설정된 키는 유지), 여기서 먼저 임시 SQLite·고정 시크릿·빈 LLM 키를 박아
실 DB(.env의 Supabase)와 실키가 테스트에 절대 섞이지 않게 한다.
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "server"

_tmpdir = tempfile.mkdtemp(prefix="golf_test_")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_tmpdir, "test.db").replace("\\", "/")
os.environ["JWT_SECRET"] = "test-secret-do-not-use-in-prod-0123456789"  # 32바이트+ (HS256 권장 하한)
os.environ["FREE_COACHING_PER_MONTH"] = "2"
os.environ["MAX_UPLOAD_MB"] = "200"
for _k in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    os.environ[_k] = ""

sys.path.insert(0, str(SERVER_DIR))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402  (mediapipe 포함 — 최초 import가 수 초 걸릴 수 있음)
import ratelimit  # noqa: E402
from db import Base, engine  # noqa: E402


@pytest.fixture()
def client():
    """테스트마다 빈 DB + 리셋된 레이트리밋 창으로 시작하는 TestClient."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    ratelimit._windows.clear()
    with TestClient(main.app) as c:
        yield c


@pytest.fixture()
def auth_token(client):
    """가입 완료된 사용자 토큰."""
    res = client.post("/auth/register", json={"email": "t@test.com", "password": "testpass123"})
    assert res.status_code == 200, res.text
    return res.json()["token"]


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


SAMPLE_PAYLOAD = {
    "score": 82,
    "summary": {"spine_angle_delta": 4.2, "x_factor": 38.0, "shoulder_rotation_max": 74.0},
    "issues": [],
    "wrist_y_history": [1.0, 2.0, 3.0],
    "phase_boundaries": {},
    "rep_frames": {},
    "fps": 30,
    "eff_sample": 3,
    "frame_data": [{"should": "be dropped"}],
}
