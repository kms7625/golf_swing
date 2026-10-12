import base64

import cv2
import numpy as np

PHASE_ORDER = ["어드레스", "백스윙", "백스윙 톱", "다운스윙", "임팩트", "팔로우스루", "피니시"]


def to_jsonable(obj):
    """numpy 스칼라/배열, tuple 등을 JSON 직렬화 가능한 순수 파이썬 타입으로 변환."""
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return float(obj) if np.isfinite(obj) else None
    if isinstance(obj, np.ndarray):
        return to_jsonable(obj.tolist())
    return obj


def extract_representative_frames(frame_data, annotated_frames):
    """
    7단계 대표 프레임 선택 — golf_swing_analyzer/ui/tab_analysis.py L.238-269와
    반드시 동일하게 유지할 것 (golf-code-change A8 불변식). 이 로직을 바꾸려면
    UI 쪽도 함께 바꿔야 한다 — 의도적으로 analyzer/ 패키지가 아닌 각 프론트 계층에
    복제돼 있다.

    임팩트: 첫 프레임 (순간적 접촉)
    다운스윙: 85% 지점 (초반 플래토 구간 제외, 실제 급강하 구간 표시)
    나머지: 중간 프레임
    """
    phase_frame_map = {}
    images_by_frame = {entry["frame"]: entry["image"] for entry in annotated_frames}
    # Phase-only pose frames remain displayable when the angle gate fails.
    # Never synthesize joint angles just to obtain a representative image.
    entries = {entry["frame"]: entry for entry in frame_data}
    entries.update({entry["frame"]: entry for entry in annotated_frames if "phase" in entry})
    for ph in PHASE_ORDER:
        ph_fd = sorted((f for f in entries.values() if f.get("phase") == ph), key=lambda f: f["frame"])
        if not ph_fd:
            continue
        if ph == "임팩트":
            representative = ph_fd[0]
        elif ph == "다운스윙":
            representative = ph_fd[min(len(ph_fd) - 1, int(len(ph_fd) * 0.85))]
        else:
            representative = ph_fd[len(ph_fd) // 2]
        source_frame = representative["frame"]
        if source_frame in images_by_frame:
            phase_frame_map[ph] = images_by_frame[source_frame]
    return phase_frame_map


def frame_to_base64_jpeg(rgb_frame: np.ndarray) -> str:
    bgr = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
    ok, buf = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        raise ValueError("JPEG 인코딩 실패")
    return base64.b64encode(buf.tobytes()).decode("ascii")
