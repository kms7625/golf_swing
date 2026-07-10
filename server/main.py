import logging
import os
import sys
import tempfile
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# golf_swing_analyzer/를 sys.path에 추가 — analyzer 패키지는 상대 import를 쓰므로
# 최상위 패키지로 보이는 경로를 넣어줘야 golf_swing_analyzer.app_v2와 동일한 방식으로 동작한다.
_ANALYZER_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "golf_swing_analyzer")
sys.path.insert(0, os.path.abspath(_ANALYZER_ROOT))

from analyzer.pipeline import process_video, auto_detect_swing_window, trim_video
from analyzer.scoring import compute_summary, compute_score
from analyzer.coach_llm import get_llm_feedback
from analyzer.reference_db import load_ref_db
from analyzer.phase_detector import SwingPhaseDetector

import jobs
from ratelimit import rate_limited
from auth import create_token, get_current_user, get_optional_user, hash_password, validate_credentials, verify_password
from db import get_db, init_db
from models import Swing, User
from serialization import to_jsonable, extract_representative_frames, frame_to_base64_jpeg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("golf.server")

MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "200"))
FREE_COACHING_PER_MONTH = int(os.environ.get("FREE_COACHING_PER_MONTH", "10"))
# provider → 서버측 키 env (G3: BYO-key 제거 — 키는 서버만 보유)
_SERVER_LLM_KEYS = {
    "Gemini": "GEMINI_API_KEY",
    "Claude": "ANTHROPIC_API_KEY",
    "GPT": "OPENAI_API_KEY",
}

app = FastAPI(title="Golf Swing Analyzer API")

_default_origins = "http://localhost:5173,http://127.0.0.1:5173,http://localhost"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.environ.get("CORS_ORIGINS", _default_origins).split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    init_db()


def _save_upload_to_temp(file: UploadFile) -> str:
    """업로드를 청크 스트리밍으로 임시파일에 저장 — 전체 메모리 적재 금지 + 크기 상한."""
    suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
    limit = MAX_UPLOAD_MB * 1024 * 1024
    written = 0
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > limit:
                tmp_path = tmp.name
                tmp.close()
                _cleanup(tmp_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"영상이 너무 큽니다 (최대 {MAX_UPLOAD_MB}MB). 스윙 구간만 잘라서 올려주세요.",
                )
            tmp.write(chunk)
        return tmp.name


def _cleanup(*paths):
    for p in paths:
        if p and os.path.exists(p):
            try:
                os.unlink(p)
            except OSError:
                pass


def _run_analysis(analyze_path: str, sample_rate: int, job_id: Optional[str] = None) -> dict:
    """공통 분석 경로 — 동기(/analyze)와 비동기(/analyze-async) 양쪽에서 사용.

    응답 포맷은 기존 /analyze와 동일하게 유지한다 (golf-ui-ux B5: web/public/samples/*.json 호환).
    """
    if job_id:
        jobs.set_stage(job_id, "analyzing", 30)
    frame_data, annotated_frames, traj_pts, fps, phase_det, eff_sample = process_video(
        analyze_path, sample_rate, analyze_path=analyze_path
    )
    if job_id:
        jobs.set_stage(job_id, "scoring", 85)
    summary = compute_summary(frame_data)
    ref_db = load_ref_db()
    score, issues = compute_score(summary, ref_db=ref_db)

    rep_frame_map = extract_representative_frames(frame_data, annotated_frames)
    rep_frames = {ph: frame_to_base64_jpeg(frame) for ph, frame in rep_frame_map.items()}

    return to_jsonable({
        "score": score,
        "issues": [{"level": lvl, "message": msg} for lvl, msg in issues],
        "summary": summary,
        "frame_data": frame_data,
        "fps": fps,
        "eff_sample": eff_sample,
        "wrist_y_history": phase_det.wrist_y_history,
        "phase_boundaries": {ph: list(bounds) for ph, bounds in phase_det.phase_boundaries.items()},
        "rep_frames": rep_frames,
    })


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    start_sec: Optional[float] = Form(None),
    end_sec: Optional[float] = Form(None),
    sample_rate: int = Form(3),
    _rl: None = Depends(rate_limited("analyze", 12, 600)),
):
    """동기 분석 — 회귀 기준·샘플 재생성용으로 유지. 신규 프론트 흐름은 /analyze-async 사용."""
    tmp_path = None
    trim_path = None
    try:
        tmp_path = _save_upload_to_temp(file)

        analyze_path = tmp_path
        if start_sec is not None and end_sec is not None:
            trim_path = trim_video(tmp_path, start_sec, end_sec)
            analyze_path = trim_path

        return _run_analysis(analyze_path, sample_rate)
    except HTTPException:
        raise
    except Exception:
        logger.exception("/analyze failed")
        raise HTTPException(status_code=500, detail="분석 중 오류가 발생했습니다. 영상 형식을 확인하고 다시 시도해주세요.")
    finally:
        _cleanup(tmp_path, trim_path)


@app.post("/analyze-async")
async def analyze_async(
    file: UploadFile = File(...),
    start_sec: Optional[float] = Form(None),
    end_sec: Optional[float] = Form(None),
    sample_rate: int = Form(3),
    _rl: None = Depends(rate_limited("analyze", 12, 600)),
):
    """비동기 분석 시작 — job_id 반환, 진행률은 GET /jobs/{job_id} 폴링."""
    tmp_path = _save_upload_to_temp(file)  # 상한 초과 시 여기서 413
    job_id = jobs.create_job()

    def _work():
        trim_path = None
        try:
            analyze_path = tmp_path
            if start_sec is not None and end_sec is not None:
                jobs.set_stage(job_id, "trimming", 15)
                trim_path = trim_video(tmp_path, start_sec, end_sec)
                analyze_path = trim_path
            result = _run_analysis(analyze_path, sample_rate, job_id=job_id)
            jobs.finish(job_id, result)
        finally:
            _cleanup(tmp_path, trim_path)

    jobs.run_in_thread(job_id, _work)
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
async def job_status(job_id: str):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다. 다시 분석을 시작해주세요.")
    return job


@app.post("/auto-window")
async def auto_window(file: UploadFile = File(...), _rl: None = Depends(rate_limited("analyze", 12, 600))):
    tmp_path = None
    try:
        tmp_path = _save_upload_to_temp(file)
        start_sec, end_sec = auto_detect_swing_window(tmp_path)
        return {"start_sec": start_sec, "end_sec": end_sec}
    except HTTPException:
        raise
    except Exception:
        logger.exception("/auto-window failed")
        raise HTTPException(status_code=500, detail="스윙 구간 자동 감지에 실패했습니다. 구간을 직접 선택해주세요.")
    finally:
        _cleanup(tmp_path)


class DetectPhasesRequest(BaseModel):
    wrist_y: list[float]


_MAX_LIVE_FRAMES = 20_000  # 라이브 장시간 촬영 폭주 방지 (rAF ~60fps 기준 5분+)


@app.post("/detect-phases")
async def detect_phases(body: DetectPhasesRequest, _rl: None = Depends(rate_limited("live", 30, 60))):
    if len(body.wrist_y) > _MAX_LIVE_FRAMES:
        raise HTTPException(status_code=400, detail="촬영이 너무 깁니다. 스윙 구간만 다시 촬영해주세요.")
    detector = SwingPhaseDetector()
    for i, wy in enumerate(body.wrist_y):
        detector.update(i, wy, wy)
    boundaries = detector.detect_all_phases()
    return to_jsonable({ph: list(bounds) for ph, bounds in boundaries.items()})


# 라이브 프레임이 보내는 각도 키 — analyzer/scoring.py compute_summary가 읽는 키와 동일
_LIVE_ANGLE_KEYS = (
    "spine_angle", "shoulder_rotation", "hip_rotation",
    "left_knee", "right_knee", "left_elbow", "right_elbow",
)


class ScoreLiveRequest(BaseModel):
    wrist_y: list[float]
    frames: list[dict]  # wrist_y와 1:1 — 온디바이스(geometry.ts)에서 계산된 프레임별 각도


@app.post("/score-live")
async def score_live(body: ScoreLiveRequest, _rl: None = Depends(rate_limited("live", 30, 60))):
    """라이브 세션 점수화 (golf-realtime 방향 A 확장) — 코어 함수를 그대로 호출.

    프레임 각도는 geometry.ts(파이썬 geometry.py와 수치 동일 검증된 포팅)가 계산했고,
    페이즈 부여·요약·점수는 업로드 경로와 같은 detect_all_phases/compute_summary/compute_score.
    """
    if len(body.frames) != len(body.wrist_y):
        raise HTTPException(status_code=400, detail="프레임 수와 손목 좌표 수가 일치하지 않습니다.")
    if len(body.wrist_y) > _MAX_LIVE_FRAMES:
        raise HTTPException(status_code=400, detail="촬영이 너무 깁니다. 스윙 구간만 다시 촬영해주세요.")
    detector = SwingPhaseDetector()
    for i, wy in enumerate(body.wrist_y):
        detector.update(i, wy, wy)
    boundaries = detector.detect_all_phases()

    frame_data = []
    for i, fr in enumerate(body.frames):
        try:
            entry = {k: float(fr[k]) for k in _LIVE_ANGLE_KEYS}
        except (KeyError, TypeError, ValueError):
            raise HTTPException(status_code=400, detail="프레임 각도 형식이 올바르지 않습니다.")
        entry["phase"] = detector.get_phase_for_frame(i)
        frame_data.append(entry)

    summary = compute_summary(frame_data)
    score, issues = compute_score(summary, ref_db=load_ref_db())
    return to_jsonable({
        "score": score,
        "issues": [{"level": lvl, "message": msg} for lvl, msg in issues],
        "summary": summary,
        "phase_boundaries": {ph: list(bounds) for ph, bounds in boundaries.items()},
    })


# ---------------------------------------------------------------- 인증 (G2)

class AuthRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/register")
async def register(
    body: AuthRequest,
    db: Session = Depends(get_db),
    _rl: None = Depends(rate_limited("auth", 10, 60)),
):
    email = body.email.strip().lower()
    problem = validate_credentials(email, body.password)
    if problem:
        raise HTTPException(status_code=400, detail=problem)
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status_code=409, detail="이미 가입된 이메일입니다.")
    user = User(email=email, password_hash=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # select 검사와 insert 사이 동시 가입 레이스 — unique 제약이 최종 심판
        db.rollback()
        raise HTTPException(status_code=409, detail="이미 가입된 이메일입니다.")
    return {"token": create_token(user), "email": user.email}


@app.post("/auth/login")
async def login(
    body: AuthRequest,
    db: Session = Depends(get_db),
    _rl: None = Depends(rate_limited("auth", 10, 60)),
):
    email = body.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    return {"token": create_token(user), "email": user.email}


@app.delete("/auth/account")
async def delete_account(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """회원 탈퇴 — 계정과 저장된 스윙 전부 삭제 (개인정보처리방침 5조 셀프서비스)."""
    db.delete(user)  # swings는 cascade="all, delete-orphan"으로 함께 파기
    db.commit()
    return {"ok": True}


# ---------------------------------------------------------------- 스윙 기록 (G1)

class SwingCreateRequest(BaseModel):
    video_name: str = ""
    payload: dict  # score/issues/summary/wrist_y_history/phase_boundaries/rep_frames/fps/eff_sample


def _swing_row(s: Swing) -> dict:
    return {
        "id": s.id,
        "created_at": s.created_at.isoformat(),
        "video_name": s.video_name,
        "score": s.score,
        "spine_angle_delta": s.spine_angle_delta,
        "x_factor": s.x_factor,
        "shoulder_rotation_max": s.shoulder_rotation_max,
        "has_feedback": bool(s.feedback),
    }


@app.post("/swings")
async def save_swing(
    body: SwingCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = dict(body.payload)
    payload.pop("frame_data", None)  # 재표시에 불필요 — 행당 용량 절감
    import json as _json

    if len(_json.dumps(payload)) > 2_000_000:
        raise HTTPException(status_code=413, detail="저장할 결과가 너무 큽니다.")
    summary = payload.get("summary") or {}
    swing = Swing(
        user_id=user.id,
        video_name=body.video_name[:255],
        score=float(payload.get("score") or 0),
        payload=payload,
        spine_angle_delta=float(summary.get("spine_angle_delta") or 0),
        x_factor=float(summary.get("x_factor") or 0),
        shoulder_rotation_max=float(summary.get("shoulder_rotation_max") or 0),
    )
    db.add(swing)
    db.commit()
    return _swing_row(swing)


@app.get("/swings")
async def list_swings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Swing).where(Swing.user_id == user.id).order_by(Swing.created_at.desc()).limit(100)
    ).all()
    return {"swings": [_swing_row(s) for s in rows]}


@app.get("/swings/{swing_id}")
async def get_swing(swing_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    swing = db.get(Swing, swing_id)
    if swing is None or swing.user_id != user.id:
        raise HTTPException(status_code=404, detail="저장된 스윙을 찾을 수 없습니다.")
    return {**_swing_row(swing), "payload": swing.payload, "feedback": swing.feedback}


@app.delete("/swings/{swing_id}")
async def delete_swing(swing_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    swing = db.get(Swing, swing_id)
    if swing is None or swing.user_id != user.id:
        raise HTTPException(status_code=404, detail="저장된 스윙을 찾을 수 없습니다.")
    db.delete(swing)
    db.commit()
    return {"ok": True}


# ---------------------------------------------------------------- AI 코칭 (G3)

class CoachingRequest(BaseModel):
    summary: dict
    issues: list[list]
    provider: str
    model_name: Optional[str] = None
    swing_id: Optional[int] = None  # 저장된 스윙에 리포트를 붙일 때
    api_key: Optional[str] = None  # dev/BYO 폴백 — 프로덕션 UI는 보내지 않음


def _month_key() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m")


@app.post("/coaching")
async def coaching(
    body: CoachingRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    api_key = (body.api_key or "").strip()
    remaining: Optional[int] = None
    charged = False  # 서버측 키 경로에서 쿼터를 차감했는지 — 실패 시 환불용

    if not api_key:
        # 서버측 키 경로: 로그인 + 월 무료 횟수 차감
        if user is None:
            raise HTTPException(status_code=401, detail="AI 코칭은 로그인 후 이용할 수 있습니다.")
        env_name = _SERVER_LLM_KEYS.get(body.provider)
        api_key = os.environ.get(env_name, "") if env_name else ""
        if not api_key:
            raise HTTPException(status_code=503, detail=f"{body.provider} 코칭이 아직 설정되지 않았습니다. 다른 공급자를 선택해주세요.")
        month = _month_key()
        if user.coaching_month != month:
            user.coaching_month = month
            user.coaching_used = 0
        if user.coaching_used >= FREE_COACHING_PER_MONTH:
            raise HTTPException(status_code=429, detail=f"이번 달 무료 코칭 {FREE_COACHING_PER_MONTH}회를 모두 사용했습니다. 다음 달에 초기화됩니다.")
        user.coaching_used += 1
        db.commit()
        charged = True
        remaining = FREE_COACHING_PER_MONTH - user.coaching_used

    try:
        issues_tuples = [(lvl, msg) for lvl, msg in body.issues]
        feedback = get_llm_feedback(
            body.summary, issues_tuples, body.provider, api_key, body.model_name,
            ref_db=load_ref_db(),
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("/coaching failed (provider=%s)", body.provider)
        if charged and user is not None:
            # 생성 실패에 무료 횟수를 소모시키지 않는다 — 차감분 환불
            user.coaching_used = max(user.coaching_used - 1, 0)
            db.commit()
        raise HTTPException(status_code=502, detail="AI 코칭 생성에 실패했습니다. 잠시 후 다시 시도해주세요.")

    if body.swing_id is not None and user is not None:
        swing = db.get(Swing, body.swing_id)
        if swing is not None and swing.user_id == user.id:
            swing.feedback = feedback
            db.commit()

    return {"feedback": feedback, "remaining": remaining}


@app.get("/health")
async def health():
    return {"status": "ok"}
