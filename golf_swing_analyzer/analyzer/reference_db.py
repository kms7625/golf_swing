import os
import json

# app_v2.py와 같은 golf_swing_analyzer/ 디렉터리에 reference_db.json이 위치하도록
# analyzer/ 서브패키지 기준 한 단계 위로 경로를 잡는다.
_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
_DB_PATH = os.path.join(os.path.dirname(_PACKAGE_DIR), "reference_db.json")
_DB_METRICS = ["spine_angle_delta", "x_factor", "shoulder_rotation_max",
               "left_elbow_top", "left_knee_addr", "right_knee_addr"]


def load_ref_db() -> dict:
    if os.path.exists(_DB_PATH):
        try:
            with open(_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_ref_db(db: dict):
    with open(_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def update_ref_db(db: dict, label: str, summary: dict) -> dict:
    """summary 하나를 label 버킷에 누적 (온라인 평균 / 분산)."""
    ps = summary.get("phase_stats", {})

    def _get(key):
        if key == "left_elbow_top":
            v = (ps.get("백스윙 톱") or {}).get("left_elbow") or \
                (ps.get("백스윙") or {}).get("left_elbow")
        elif key == "left_knee_addr":
            v = (ps.get("어드레스") or {}).get("left_knee")
        elif key == "right_knee_addr":
            v = (ps.get("어드레스") or {}).get("right_knee")
        else:
            v = summary.get(key)
        return float(v) if v is not None else None

    bucket = db.setdefault(label, {"n": 0})
    bucket["n"] += 1
    for m in _DB_METRICS:
        v = _get(m)
        if v is None:
            continue
        entry = bucket.setdefault(m, {"sum": 0.0, "sum_sq": 0.0})
        entry["sum"]    += v
        entry["sum_sq"] += v * v
    return db


def get_ref_stats(db: dict, label: str) -> dict:
    """label 버킷에서 각 지표의 mean/std 반환."""
    bucket = db.get(label, {})
    n = bucket.get("n", 0)
    if n < 1:
        return {}
    result = {}
    for m in _DB_METRICS:
        e = bucket.get(m)
        if not e:
            continue
        mean = e["sum"] / n
        var  = max(0.0, e["sum_sq"] / n - mean * mean)
        result[m] = {"mean": round(mean, 2), "std": round(var ** 0.5, 2), "n": n}
    return result
