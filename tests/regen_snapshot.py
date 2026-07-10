"""회귀 스냅샷 기준값 재생성 — analyzer/를 의도적으로 변경했을 때만 실행.

사용: python tests/regen_snapshot.py
결과: tests/snapshots/ilban_baseline.json 갱신 (테스트와 함께 커밋할 것)
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "golf_swing_analyzer"))

from analyzer.pipeline import process_video  # noqa: E402
from analyzer.reference_db import load_ref_db  # noqa: E402
from analyzer.scoring import compute_score, compute_summary  # noqa: E402

VIDEO = ROOT / "golf_swing_analyzer" / "video" / "일반.mp4"
OUT = Path(__file__).parent / "snapshots" / "ilban_baseline.json"


def main() -> None:
    frame_data, annotated, traj, fps, det, eff = process_video(str(VIDEO), 3, analyze_path=str(VIDEO))
    summary = compute_summary(frame_data)
    score, issues = compute_score(summary, ref_db=load_ref_db())
    baseline = {
        "video": VIDEO.name,
        "sample_rate": 3,
        "score": score,
        "phases": sorted(det.phase_boundaries.keys()),
        "summary": {
            "spine_angle_delta": summary["spine_angle_delta"],
            "x_factor": summary["x_factor"],
            "shoulder_rotation_max": summary["shoulder_rotation_max"],
            "total_frames": summary["total_frames"],
        },
    }
    os.makedirs(OUT.parent, exist_ok=True)
    OUT.write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
    print("baseline written:", OUT)
    print(json.dumps(baseline, ensure_ascii=False))


if __name__ == "__main__":
    main()
