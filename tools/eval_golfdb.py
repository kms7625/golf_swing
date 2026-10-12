"""GolfDB 이벤트 기준으로 analyzer 단계 검출 정확도(PCE) 측정 — analyzer 무변경, 읽기 전용 평가.

docs/research/04_swinglab_implications.md P1. 데이터: GolfDB(McNally et al., CVPRW 2019, CC BY-NC 4.0)
저자 제공 160×160 클립 + golfDB.mat. 클립 프레임 0 = 원본 events[0], 정답 이벤트 = events[1:9] - events[0].
PCE 허용 오차는 GolfDB util.correct_preds와 동일: max(round((impact - address) / 30), 1) 프레임.

대응(앱 → GolfDB): 백스윙 시작 → Address, 백스윙 톱 시작 → Top, 임팩트 시작 → Impact, 피니시 시작 → Finish.
Toe-up·Mid-backswing·Mid-downswing·Mid-follow-through는 앱에 대응 이벤트가 없어 제외.

사용(배포 기준 환경 Docker linux/amd64):
  python tools/eval_golfdb.py --data ~/datasets/golfdb --out docs/research/golfdb_eval [--limit N]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "golf_swing_analyzer"))

from analyzer.pipeline import process_video  # noqa: E402

GOLFDB_EVENTS = ["Address", "Toe-up", "Mid-backswing", "Top", "Mid-downswing", "Impact", "Mid-follow-through", "Finish"]
MAPPING = {"Address": "백스윙", "Top": "백스윙 톱", "Impact": "임팩트", "Finish": "피니시"}  # 앱 구간의 시작 = 이벤트


def predict(clip_path):
    frame_data, _ann, _traj, fps, det, eff = process_video(str(clip_path), 1, analyze_path=str(clip_path))
    hist_to_local = {h: l for l, h in det.local_to_hist.items()}
    local_to_frame = {f["local_idx"]: f["frame"] for f in frame_data}
    preds = {}
    for ev, phase in MAPPING.items():
        bounds = det.phase_boundaries.get(phase)
        if bounds is None:
            continue
        local = hist_to_local.get(int(bounds[0]))
        if local is None or local not in local_to_frame:
            continue
        preds[ev] = int(local_to_frame[local])
    detected = len(det.wrist_y_history)
    return preds, eff, detected, len(frame_data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    data, out = Path(a.data).expanduser(), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = [r for r in json.load(open(data / "golfdb_annotations.json")) if r["view"] == "face-on" and r["slow"] == 0]
    if a.limit:
        rows = rows[: a.limit]

    results = []
    for i, r in enumerate(rows):
        clip = data / "videos_160" / f"{r['id']}.mp4"
        ev = [e - r["events"][0] for e in r["events"][1:9]]
        gt = dict(zip(GOLFDB_EVENTS, ev))
        tol = int(max(round((gt["Impact"] - gt["Address"]) / 30), 1))
        rec = {"id": r["id"], "club": r["club"], "tol": tol, "gt": {k: gt[k] for k in MAPPING}}
        t0 = time.time()
        try:
            preds, eff, detected, n = predict(clip)
            rec.update(pred=preds, eff_sample=eff, pose_frames=detected, frames=n)
            rec["delta"] = {k: preds[k] - gt[k] for k in MAPPING if k in preds}
            rec["correct"] = {k: int(abs(d) <= tol) for k, d in rec["delta"].items()}
        except Exception as e:  # 클립 단위 실패는 기록하고 계속
            rec["error"] = f"{type(e).__name__}: {e}"
        rec["sec"] = round(time.time() - t0, 1)
        results.append(rec)
        print(f"[{i + 1}/{len(rows)}] id={r['id']} {rec.get('correct', rec.get('error'))}", flush=True)
        json.dump(results, open(out / "results.json", "w"), ensure_ascii=False)

    ok = [x for x in results if "correct" in x]
    summary = {"clips_total": len(results), "clips_evaluated": len(ok), "clips_failed": len(results) - len(ok), "per_event": {}}
    for k in MAPPING:
        c = [x["correct"][k] for x in ok if k in x["correct"]]
        d = sorted(abs(x["delta"][k]) for x in ok if k in x["delta"])
        summary["per_event"][k] = {
            "n": len(c),
            "pce": round(sum(c) / len(c), 3) if c else None,
            "median_abs_err_frames": d[len(d) // 2] if d else None,
            "within_5_frames": round(sum(v <= 5 for v in d) / len(d), 3) if d else None,
        }
    main_ev = [x["correct"][k] for x in ok for k in ("Top", "Impact") if k in x["correct"]]
    summary["pce_top_impact"] = round(sum(main_ev) / len(main_ev), 3) if main_ev else None
    json.dump(summary, open(out / "summary.json", "w"), ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
