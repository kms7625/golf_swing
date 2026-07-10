"""서버 엔드포인트 계약 테스트 — 인증·기록·쿼터·상한·레이트리밋.

분석 코어는 건드리지 않는 순수 API 계층 검증 (코어 회귀는 test_analyzer_snapshot.py).
"""
import math

import main
from conftest import SAMPLE_PAYLOAD, bearer


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


# ---------------------------------------------------------------- 인증

def test_register_login_roundtrip(client):
    r = client.post("/auth/register", json={"email": "A@Test.com", "password": "testpass123"})
    assert r.status_code == 200
    assert r.json()["email"] == "a@test.com"  # 소문자 정규화

    r = client.post("/auth/login", json={"email": "a@test.com", "password": "testpass123"})
    assert r.status_code == 200 and r.json()["token"]

    r = client.post("/auth/login", json={"email": "a@test.com", "password": "wrong-password"})
    assert r.status_code == 401


def test_register_validation_and_duplicate(client):
    assert client.post("/auth/register", json={"email": "bad-email", "password": "testpass123"}).status_code == 400
    assert client.post("/auth/register", json={"email": "a@test.com", "password": "short"}).status_code == 400
    assert client.post("/auth/register", json={"email": "a@test.com", "password": "testpass123"}).status_code == 200
    assert client.post("/auth/register", json={"email": "a@test.com", "password": "testpass123"}).status_code == 409


def test_auth_rate_limit(client):
    # auth 계열 10회/분 — 11번째 요청은 429
    codes = []
    for _ in range(11):
        codes.append(client.post("/auth/login", json={"email": "x@test.com", "password": "testpass123"}).status_code)
    assert codes[:10] == [401] * 10
    assert codes[10] == 429


def test_account_deletion_cascades(client, auth_token):
    client.post("/swings", json={"video_name": "a.mp4", "payload": SAMPLE_PAYLOAD}, headers=bearer(auth_token))
    assert client.delete("/auth/account", headers=bearer(auth_token)).status_code == 200
    # 토큰의 사용자 소멸 → 세션 무효
    assert client.get("/swings", headers=bearer(auth_token)).status_code == 401
    assert client.post("/auth/login", json={"email": "t@test.com", "password": "testpass123"}).status_code == 401


# ---------------------------------------------------------------- 스윙 기록

def test_swings_require_auth(client):
    assert client.get("/swings").status_code == 401
    assert client.post("/swings", json={"video_name": "a", "payload": SAMPLE_PAYLOAD}).status_code == 401


def test_swing_crud_and_frame_data_dropped(client, auth_token):
    r = client.post("/swings", json={"video_name": "스모크.mp4", "payload": SAMPLE_PAYLOAD}, headers=bearer(auth_token))
    assert r.status_code == 200
    row = r.json()
    assert row["score"] == 82.0 and row["x_factor"] == 38.0

    detail = client.get(f"/swings/{row['id']}", headers=bearer(auth_token)).json()
    assert "frame_data" not in detail["payload"]  # 행당 용량 절감 계약
    assert detail["payload"]["wrist_y_history"] == [1.0, 2.0, 3.0]

    assert client.delete(f"/swings/{row['id']}", headers=bearer(auth_token)).json() == {"ok": True}
    assert client.get("/swings", headers=bearer(auth_token)).json()["swings"] == []


def test_swing_user_isolation(client, auth_token):
    row = client.post("/swings", json={"video_name": "a", "payload": SAMPLE_PAYLOAD}, headers=bearer(auth_token)).json()
    other = client.post("/auth/register", json={"email": "other@test.com", "password": "testpass123"}).json()["token"]
    assert client.get(f"/swings/{row['id']}", headers=bearer(other)).status_code == 404
    assert client.delete(f"/swings/{row['id']}", headers=bearer(other)).status_code == 404


def test_swing_payload_cap(client, auth_token):
    fat = dict(SAMPLE_PAYLOAD, wrist_y_history=[1.0] * 400_000)  # ≈ 수 MB
    r = client.post("/swings", json={"video_name": "fat", "payload": fat}, headers=bearer(auth_token))
    assert r.status_code == 413


# ---------------------------------------------------------------- AI 코칭 (쿼터·환불)

def _coach(client, token):
    return client.post(
        "/coaching",
        json={"summary": SAMPLE_PAYLOAD["summary"], "issues": [], "provider": "Gemini"},
        headers=bearer(token),
    )


def test_coaching_requires_login_and_server_key(client, auth_token):
    r = client.post("/coaching", json={"summary": {}, "issues": [], "provider": "Gemini"})
    assert r.status_code == 401
    # 서버 키 미설정(conftest에서 빈 값) → 503
    assert _coach(client, auth_token).status_code == 503


def test_coaching_quota_and_refund(client, auth_token, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy")

    # 실패는 쿼터를 소모하지 않는다 (환불)
    monkeypatch.setattr(main, "get_llm_feedback", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    assert _coach(client, auth_token).status_code == 502

    # 성공 2회 = FREE_COACHING_PER_MONTH(테스트 env=2) 소진 — 환불이 없었다면 1회만 가능했을 것
    monkeypatch.setattr(main, "get_llm_feedback", lambda *a, **k: "### 리포트\n**좋음**")
    r1 = _coach(client, auth_token)
    assert r1.status_code == 200 and r1.json()["remaining"] == 1
    r2 = _coach(client, auth_token)
    assert r2.status_code == 200 and r2.json()["remaining"] == 0
    assert _coach(client, auth_token).status_code == 429


def test_coaching_attaches_to_swing(client, auth_token, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy")
    monkeypatch.setattr(main, "get_llm_feedback", lambda *a, **k: "저장되는 리포트")
    row = client.post("/swings", json={"video_name": "a", "payload": SAMPLE_PAYLOAD}, headers=bearer(auth_token)).json()
    r = client.post(
        "/coaching",
        json={"summary": {}, "issues": [], "provider": "Gemini", "swing_id": row["id"]},
        headers=bearer(auth_token),
    )
    assert r.status_code == 200
    detail = client.get(f"/swings/{row['id']}", headers=bearer(auth_token)).json()
    assert detail["feedback"] == "저장되는 리포트"


# ---------------------------------------------------------------- 라이브 점수화

def _synthetic_swing(n=120):
    """어드레스→백스윙(상승)→다운스윙(하강 y증가)→팔로우 형태의 손목 Y + 상수형 각도."""
    wy = []
    for i in range(n):
        if i < 30:
            wy.append(400 + math.sin(i * 0.2) * 2)
        elif i < 60:
            wy.append(400 - (i - 30) * 6)
        elif i < 80:
            wy.append(220 + (i - 60) * 11)
        else:
            wy.append(440 - (i - 80) * 4)
    frames = [{
        "spine_angle": 25 + math.sin(i * 0.1) * 3,
        "shoulder_rotation": 20 + (i % 60) * 0.5,
        "hip_rotation": 10 + (i % 60) * 0.2,
        "left_knee": 172.0, "right_knee": 173.0,
        "left_elbow": 150.0, "right_elbow": 152.0,
    } for i in range(n)]
    return wy, frames


def test_score_live_full_phases(client):
    wy, frames = _synthetic_swing()
    r = client.post("/score-live", json={"wrist_y": wy, "frames": frames})
    assert r.status_code == 200
    data = r.json()
    assert set(data["phase_boundaries"].keys()) == {
        "어드레스", "백스윙", "백스윙 톱", "다운스윙", "임팩트", "팔로우스루", "피니시",
    }
    assert 0 <= data["score"] <= 100
    assert data["summary"]["total_frames"] == len(wy)


def test_score_live_input_guards(client):
    wy, frames = _synthetic_swing()
    assert client.post("/score-live", json={"wrist_y": wy, "frames": frames[:-1]}).status_code == 400
    assert client.post("/score-live", json={"wrist_y": wy, "frames": [{}] * len(wy)}).status_code == 400
    big = [1.0] * 20_001
    assert client.post("/detect-phases", json={"wrist_y": big}).status_code == 400
