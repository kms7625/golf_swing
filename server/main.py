import os
import sys
import tempfile
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# golf_swing_analyzer/를 sys.path에 추가 — analyzer 패키지는 상대 import를 쓰므로
# 최상위 패키지로 보이는 경로를 넣어줘야 golf_swing_analyzer.app_v2와 동일한 방식으로 동작한다.
_ANALYZER_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "golf_swing_analyzer")
sys.path.insert(0, os.path.abspath(_ANALYZER_ROOT))

from analyzer.pipeline import process_video, auto_detect_swing_window, trim_video
from analyzer.scoring import compute_summary, compute_score
from analyzer.coach_llm import get_llm_feedback
from analyzer.reference_db import load_ref_db
from analyzer.phase_detector import SwingPhaseDetector

from serialization import to_jsonable, extract_representative_frames, frame_to_base64_jpeg

app = FastAPI(title="Golf Swing Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",  # Capacitor Android WebView origin (androidScheme: http, set for dev to avoid mixed-content blocking)
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _save_upload_to_temp(file: UploadFile) -> str:
    suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        return tmp.name


def _cleanup(*paths):
    for p in paths:
        if p and os.path.exists(p):
            try:
                os.unlink(p)
            except OSError:
                pass


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    start_sec: Optional[float] = Form(None),
    end_sec: Optional[float] = Form(None),
    sample_rate: int = Form(3),
):
    tmp_path = None
    trim_path = None
    try:
        tmp_path = _save_upload_to_temp(file)

        analyze_path = tmp_path
        if start_sec is not None and end_sec is not None:
            trim_path = trim_video(tmp_path, start_sec, end_sec)
            analyze_path = trim_path

        frame_data, annotated_frames, traj_pts, fps, phase_det, eff_sample = process_video(
            analyze_path, sample_rate, analyze_path=analyze_path
        )
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        _cleanup(tmp_path, trim_path)


@app.post("/auto-window")
async def auto_window(file: UploadFile = File(...)):
    tmp_path = None
    try:
        tmp_path = _save_upload_to_temp(file)
        start_sec, end_sec = auto_detect_swing_window(tmp_path)
        return {"start_sec": start_sec, "end_sec": end_sec}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        _cleanup(tmp_path)


class DetectPhasesRequest(BaseModel):
    wrist_y: list[float]


@app.post("/detect-phases")
async def detect_phases(body: DetectPhasesRequest):
    detector = SwingPhaseDetector()
    for i, wy in enumerate(body.wrist_y):
        detector.update(i, wy, wy)
    boundaries = detector.detect_all_phases()
    return to_jsonable({ph: list(bounds) for ph, bounds in boundaries.items()})


class CoachingRequest(BaseModel):
    summary: dict
    issues: list[list]
    provider: str
    api_key: str
    model_name: Optional[str] = None


@app.post("/coaching")
async def coaching(body: CoachingRequest):
    try:
        issues_tuples = [(lvl, msg) for lvl, msg in body.issues]
        feedback = get_llm_feedback(
            body.summary, issues_tuples, body.provider, body.api_key, body.model_name,
            ref_db=load_ref_db(),
        )
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
