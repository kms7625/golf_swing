"""Frozen before/after comparison from one pose stream, with separate world cache.

Docker: /work (feature), /baseline (3bdf45d code), /datasets, /output.
Mac is used ONLY for the requested platform comparison. No network or installs.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import platform
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("task", choices=["capture", "summarize"])
parser.add_argument("--root", type=Path, default=Path("/work"))
parser.add_argument("--baseline", type=Path, default=Path("/baseline"))
parser.add_argument("--datasets", type=Path, default=Path("/datasets"))
parser.add_argument("--output", type=Path, default=Path("/output"))
parser.add_argument("--group", choices=["apps", "golfdb", "snapshot"], default="apps")
parser.add_argument("--names", nargs="*")
args = parser.parse_args()
sys.path[:0] = [str(args.baseline / "golf_swing_analyzer"), str(args.baseline)]
import cv2
import mediapipe
import numpy as np
from analyzer import pipeline
from analyzer.scoring import compute_score, compute_summary
from server.serialization import extract_representative_frames, frame_to_base64_jpeg, to_jsonable


def feature_module(name):
    spec = importlib.util.spec_from_file_location(name, args.root / f"golf_swing_analyzer/analyzer/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


geometry = feature_module("geometry")
rotation = feature_module("rotation")
sys.modules["analyzer.rotation"] = rotation
spec = importlib.util.spec_from_file_location("analyzer.xfactor_scoring", args.root / "golf_swing_analyzer/analyzer/scoring.py")
feature_scoring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feature_scoring)
args.output.mkdir(parents=True, exist_ok=True)


def dump(path, obj):
    path.write_text(json.dumps(to_jsonable(obj), ensure_ascii=False, allow_nan=False) + "\n")


def evaluate(raw, baseline, top_frame):
    frames = rotation.apply_world_rotations(copy.deepcopy(raw), top_frame)
    summary = feature_scoring.compute_summary(frames)
    score, issues = compute_score(summary, {})
    legacy = copy.deepcopy(frames)
    for f in legacy:
        for key in ("shoulder_rotation", "hip_rotation"):
            f[key] = f[key + "_2d"]
        f.pop("rotation_method")
    assert compute_summary(legacy) == baseline["summary"], "Legacy replay must be exact"
    return dict(summary=summary, score=score, issues=issues, frame_data=frames)


original_pose = pipeline.mp_pose.Pose
observations = []


class CapturePose:
    def __init__(self, **kwargs):
        self.pose = original_pose(**kwargs)

    def __enter__(self):
        self.pose.__enter__()
        return self

    def __exit__(self, *exc):
        return self.pose.__exit__(*exc)

    def process(self, image):
        result = self.pose.process(image)
        if result.pose_landmarks:
            world = result.pose_world_landmarks
            observations.append([[lm.x, lm.y, lm.z, lm.visibility] for lm in world.landmark] if world else None)
        return result


if args.task == "capture":
    if args.group == "golfdb":
        selection = json.loads((args.root / "docs/research/xfactor/selection.json").read_text())
        jobs = [(str(r["id"]), args.datasets / f'golfdb/videos_160/{r["id"]}.mp4', None, r) for r in selection]
    else:
        windows = json.loads((args.datasets / "golfdb_pose/apps_before.json").read_text())
        paths = {"il-ban": args.root / "golf_swing_analyzer/video/일반.mp4",
                 "pro": args.root / "golf_swing_analyzer/video/프로.mp4",
                 "pro2": args.root / "golf_swing_analyzer/video/프로2.mp4"}
        paths.update({f"pexels_{n}": args.datasets / f"test_videos/pexels_{n}.mp4"
                      for n in (8065880, 6541855, 35546329, 34883764)})
        jobs = [(name, p, windows[name]["window"], {}) for name, p in paths.items()]
        if args.group == "snapshot":
            jobs = [("snapshot", paths["il-ban"], None, {})]
    pipeline.mp_pose.Pose = CapturePose
    for name, path, window, annotation in jobs:
        if args.names and name not in args.names:
            continue
        target = args.output / f"{args.group}_{name}.json"
        if target.exists():
            continue
        observations.clear()
        started = time.perf_counter()
        trimmed = pipeline.trim_video(str(path), *window) if window else str(path)
        offset = int(window[0] * pipeline.get_video_info(str(path))["fps"]) if window else 0
        try:
            fd, ann, traj, fps, det, eff = pipeline.process_video(trimmed, 3, source_start_sec=offset / pipeline.get_video_info(trimmed)["fps"] + 1e-9)
            summary = compute_summary(fd)
            score, issues = compute_score(summary, {})
            baseline = dict(summary=summary, score=score, issues=issues)
            observed = {t["local_idx"] for t in traj}
            for f in fd:
                world = observations[f["local_idx"]]
                from types import SimpleNamespace
                lms = [SimpleNamespace(x=p[0], y=p[1], z=p[2], visibility=p[3]) for p in world] if world else None
                heads, reason = geometry.calc_world_rotation_headings(lms)
                # Legacy interpolation was a hold; never count held world as new evidence.
                if f["local_idx"] not in observed:
                    heads, reason = None, "interpolated_2d"
                f.update(world_rotation_headings=heads, world_rotation_reason=reason)
            top_frame = det.phase_boundaries_frames["백스윙 톱"][0]
            after = evaluate(fd, baseline, top_frame)
            reps = extract_representative_frames(fd, ann)
            record = dict(name=name, annotation=annotation, window=window, before=baseline,
                          raw_frame_data=fd, after=after, top_frame=top_frame,
                          phase_boundaries_frames=det.phase_boundaries_frames,
                          phase_boundaries=det.phase_boundaries, quality=det.quality,
                          trajectory_frames=[f["frame"] for f in traj],
                          annotated_frames=[{k:v for k,v in f.items() if k != "image"} for f in ann],
                          fps=fps, eff_sample=eff, elapsed_sec=time.perf_counter()-started,
                          environment=dict(platform=platform.platform(), python=platform.python_version(),
                                           mediapipe=mediapipe.__version__, numpy=np.__version__, opencv=cv2.__version__),
                          video_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            dump(target, record)
            np.savez_compressed(args.output / f"{args.group}_{name}_world.npz",
                                world=np.asarray([p if p else np.full((33, 4), np.nan) for p in observations]))
            if args.group == "apps" and name in ("il-ban", "pro", "pro2"):
                payload = dict(score=after["score"], issues=[{"level":a,"message":b} for a,b in after["issues"]],
                               summary=after["summary"], frame_data=after["frame_data"], fps=fps, eff_sample=eff,
                               wrist_y_history=det.wrist_y_history, phase_boundaries=det.phase_boundaries,
                               phase_boundaries_frames=det.phase_boundaries_frames, phase_boundaries_sec=det.phase_boundaries_sec,
                               wrist_times_sec=det.wrist_times_sec, rep_frames={p:frame_to_base64_jpeg(im) for p,im in reps.items()})
                dump(args.output / f"sample_{name}.json", payload)
            print(name, score, after["score"], summary["x_factor"], after["summary"]["x_factor"], flush=True)
        except Exception as exc:
            dump(target, dict(name=name, annotation=annotation, error=repr(exc)))
            print(name, repr(exc), flush=True)
        finally:
            if window:
                Path(trimmed).unlink()
else:
    records = []
    for path in sorted(args.output.glob(f"{args.group}_*.json")):
        rec = json.loads(path.read_text())
        if "error" not in rec:
            rec["after"] = evaluate(rec["raw_frame_data"], rec["before"], rec["top_frame"])
            dump(path, rec)
        records.append(rec)
    compact = [{k:v for k,v in r.items() if k not in ("raw_frame_data", "annotated_frames", "trajectory_frames")} for r in records]
    for r in compact:
        if "after" in r:
            r["after"].pop("frame_data")
    dump(args.output / f"results_{args.group}.json", compact)
    print("summary", args.group, len(records))
