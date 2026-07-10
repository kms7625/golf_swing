"""분석 코어 회귀 스냅샷 — golf-analysis-quality의 수동 3영상 대조를 자동화한 최소판.

기준값은 tests/snapshots/ilban_baseline.json (2026-07-10, 일반.mp4 전체 구간·sample_rate 3).
analyzer/를 수정한 커밋은 이 테스트가 지키고, 의도된 변경이면
`python tests/regen_snapshot.py`로 기준값을 재생성해 함께 커밋한다.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "golf_swing_analyzer" / "video" / "일반.mp4"
SNAP = Path(__file__).parent / "snapshots" / "ilban_baseline.json"


@pytest.mark.skipif(not VIDEO.exists(), reason="테스트 영상 없음")
@pytest.mark.skipif(not SNAP.exists(), reason="스냅샷 기준값 없음 — tests/regen_snapshot.py 먼저 실행")
def test_ilban_regression():
    # conftest가 server/를 sys.path에 넣고 main을 import하면서 analyzer 경로도 잡혀 있다
    from analyzer.pipeline import process_video
    from analyzer.reference_db import load_ref_db
    from analyzer.scoring import compute_score, compute_summary

    frame_data, annotated, traj, fps, det, eff = process_video(str(VIDEO), 3, analyze_path=str(VIDEO))
    summary = compute_summary(frame_data)
    score, issues = compute_score(summary, ref_db=load_ref_db())

    base = json.loads(SNAP.read_text(encoding="utf-8"))

    assert score == base["score"], f"점수 회귀: {score} != {base['score']}"
    assert sorted(det.phase_boundaries.keys()) == sorted(base["phases"])
    for key in ("spine_angle_delta", "x_factor", "shoulder_rotation_max", "total_frames"):
        assert abs(summary[key] - base["summary"][key]) <= 0.5, f"{key}: {summary[key]} vs {base['summary'][key]}"
    # frame_data ↔ annotated_frames 1:1 불변식 (golf-code-change A7)
    assert len(frame_data) == len(annotated)
