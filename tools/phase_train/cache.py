"""Docker-only one-time pose extraction. No event labels are used here."""
import argparse
import importlib.metadata
import json
import platform
import time

import cv2
import numpy as np

from common import DATA, ROOT, annotations, audit, dump, sha
from analyzer.mp_setup import mp_pose
from analyzer.video_signal import SceneCuts, wrist_signal

SETTINGS = dict(static_image_mode=False, model_complexity=1, smooth_landmarks=True,
                min_detection_confidence=.5, min_tracking_confidence=.5)


def extract(path, step=1):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not cap.isOpened() or total <= 0:
        raise ValueError('unreadable video')
    cuts = SceneCuts(fps)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    landmarks, signals, frames, local, gray, cut_frames, sizes = [], [], [], [], [], [], []
    pose_count = 0
    try:
        with mp_pose.Pose(**SETTINGS) as pose:
            for fi in range(total):
                ok, frame = cap.read()
                if not ok:
                    raise ValueError(f'decode failed at {fi}/{total}')
                # Persist precisely the grayscale cut inputs, before resizing/CLAHE.
                gray.append(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (64, 36)))
                if cuts.update(frame, fi):
                    cut_frames.append(fi)
                if fi % step:
                    continue
                h, w = frame.shape[:2]
                if w > 854:
                    frame = cv2.resize(frame, (854, int(h*854/w)))
                    h, w = frame.shape[:2]
                lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                rgb = cv2.cvtColor(cv2.merge([clahe.apply(l), a, b]), cv2.COLOR_LAB2RGB)
                result = pose.process(rgb)
                if result.pose_landmarks:
                    lms = result.pose_landmarks.landmark
                    landmarks.append([[p.x, p.y, p.z, p.visibility] for p in lms])
                    signals.append(wrist_signal(lms, w, h))
                    local.append(pose_count)
                    pose_count += 1
                else:
                    landmarks.append(np.full((33, 4), np.nan))
                    signals.append((np.nan, 0, h*.25))
                    local.append(-1)
                frames.append(fi)
                sizes.append((w, h))
    finally:
        cap.release()
    return dict(landmarks=np.asarray(landmarks, np.float32),
                signals=np.asarray(signals, np.float64), source_frames=np.asarray(frames),
                local_idx=np.asarray(local), times=np.asarray(frames)/fps,
                cut_gray=np.asarray(gray, np.uint8), cut_frames=np.asarray(cut_frames, dtype=int),
                sizes=np.asarray(sizes), fps=fps, step=step, total=total)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--shard', type=int, default=0)
    p.add_argument('--shards', type=int, default=1)
    args = p.parse_args()
    assert platform.system() == 'Linux' and platform.machine() == 'x86_64', 'Z6: Docker amd64 required'
    cv2.setNumThreads(1)
    environment = dict(platform=platform.platform(), python=platform.python_version(),
                       versions={n: importlib.metadata.version(n) for n in ('numpy', 'mediapipe', 'opencv-contrib-python')},
                       settings=SETTINGS, pipeline_sha=sha(ROOT/'golf_swing_analyzer/analyzer/pipeline.py'))
    dump(DATA/'environment.json', environment)
    rows = annotations((1, 2, 3, 4))
    for row in sorted(rows, key=lambda r: r['id'])[args.shard::args.shards]:
        ident = row['id']
        target = DATA/'cache'/f'{ident}.npz'
        status = DATA/'cache'/f'{ident}.json'
        if status.exists():
            continue
        started = time.perf_counter()
        record = {k: row[k] for k in ('id', 'split', 'view')}
        path = DATA.parent/'golfdb/videos_160'/f'{ident}.mp4'
        try:
            cap = cv2.VideoCapture(str(path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            record.update(fps=fps, total=total)
            if not path.exists():
                record.update(status='missing')
            elif abs(fps-30) > .15:
                record.update(status='excluded_fps')
            else:
                values = extract(path)
                step = max(1, int(np.ceil(total/600)))
                if step > 1:
                    # MP tracking depends on sampled inputs: do not decimate dense poses.
                    values.update({f'adaptive_{k}': v for k, v in extract(path, step).items()})
                target.parent.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(target, **values)
                record.update(status='ok', sha256=sha(target), adaptive_step=step)
        except Exception as exc:
            record.update(status='failed', error=repr(exc))
        record['elapsed_sec'] = time.perf_counter()-started
        dump(status, record)
        print(json.dumps(record), flush=True)
    audit('cache_shard_complete', shard=args.shard, shards=args.shards)


if __name__ == '__main__':
    main()
