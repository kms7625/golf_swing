"""Actual feature-pipeline regression against frozen paired pose evaluation."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "golf_swing_analyzer"), str(ROOT)]
from analyzer.pipeline import process_video, trim_video, get_video_info
from analyzer.scoring import compute_summary, compute_score
from server.serialization import extract_representative_frames, frame_to_base64_jpeg, to_jsonable

data = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/datasets/xfactor_eval/docker")
records = []
for name, path in {"il-ban": ROOT / "golf_swing_analyzer/video/일반.mp4",
                   "pro": ROOT / "golf_swing_analyzer/video/프로.mp4",
                   "pro2": ROOT / "golf_swing_analyzer/video/프로2.mp4",
                   **{f"pexels_{n}": Path(f"/datasets/test_videos/pexels_{n}.mp4")
                      for n in (8065880, 6541855, 35546329, 34883764)}}.items():
    before = json.loads((data / f"apps_{name}.json").read_text())
    window = before["window"]
    clip = trim_video(str(path), *window)
    offset = int(window[0] * get_video_info(str(path))["fps"])
    try:
        fd, ann, traj, fps, det, eff = process_video(clip, 3, source_start_sec=offset/get_video_info(clip)["fps"]+1e-9)
    finally:
        Path(clip).unlink()
    s = compute_summary(fd)
    score, issues = compute_score(s, {})
    assert to_jsonable(s) == before["after"]["summary"], name
    assert score == before["after"]["score"], name
    assert to_jsonable(det.phase_boundaries_frames) == before["phase_boundaries_frames"], name
    assert [f["frame"] for f in fd] == [f["frame"] for f in before["raw_frame_data"]]
    assert [f["frame"] for f in traj] == before["trajectory_frames"]
    assert [f["frame"] for f in ann] == [f["frame"] for f in before["annotated_frames"]]
    image_keys = {f["frame"] for f in ann}
    assert all(f["frame"] in image_keys for f in fd)
    reps = extract_representative_frames(fd, ann)
    assert len(reps) == 7
    payload = dict(score=score, summary=s, issues=[{"level":a,"message":b} for a,b in issues],
                   frame_data=fd, fps=fps, eff_sample=eff, wrist_y_history=det.wrist_y_history,
                   phase_boundaries=det.phase_boundaries, phase_boundaries_frames=det.phase_boundaries_frames,
                   phase_boundaries_sec=det.phase_boundaries_sec, wrist_times_sec=det.wrist_times_sec,
                   rep_frames={p:frame_to_base64_jpeg(im) for p,im in reps.items()})
    if name in ("il-ban", "pro", "pro2"):
        (ROOT / f"web/public/samples/{name}.json").write_text(json.dumps(to_jsonable(payload), ensure_ascii=False, allow_nan=False)+"\n")
    records.append(dict(name=name, score=score, summary=s, phase_boundaries_frames=det.phase_boundaries_frames,
                        frames=len(fd), annotated=len(ann), trajectory=len(traj), representatives=len(reps), parity=True))
    print(name, "pipeline parity PASS", score, flush=True)
(ROOT / "docs/research/xfactor/pipeline_verification.json").write_text(json.dumps(to_jsonable(records), ensure_ascii=False)+"\n")
