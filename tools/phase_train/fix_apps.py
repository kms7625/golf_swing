"""Ablate each parameter with cached scans and fresh unique-trim pose inference."""
import argparse
import json
import os
import sys
import time

from common import DATA, ROOT, audit, dump
from fix_common import (A_PARAMS, BASE, PRIOR, app_records, app_result, ensure_open,
                        variants, window, window_key)


def plan():
    ensure_open()
    before = app_records()
    after = json.loads((PRIOR/'apps_after.json').read_text())
    result = {}
    for name, record in before.items():
        scan = record['signals'][0]
        total = scan['times'][-1]+1/scan['fps']
        for p, expected in ((BASE, record['window']), (A_PARAMS, after[name]['window'])):
            assert window(scan, p, total) == expected, (name, expected)
        result[name] = {key: window(scan, p, total) for key, p in variants().items()}
        assert all(result[name].values()), name
    dump(DATA/'ablation_windows.json', result)
    audit('ablation_plan', variants={k: p.__dict__ for k, p in variants().items()},
          scan_parity=True, splits=[1, 2, 3], holdout_access=False)
    return result


def infer(name, bounds):
    """Keep all metric rows before phase filtering; no production code changes."""
    sys.path[:0] = [str(ROOT/'golf_swing_analyzer'), str(ROOT/'server')]
    from analyzer import pipeline
    from serialization import to_jsonable
    base = pipeline.SwingPhaseDetector

    class Capture(base):
        def __init__(self, *args, **kw):
            super().__init__(*args, params=BASE, **kw)

        def get_phase_for_frame(self, local_idx):
            return '어드레스'  # retain all rows for subsequent independent relabeling

    paths = dict(zip(('il-ban', 'pro', 'pro2'), ('일반', '프로', '프로2')))
    path = (ROOT/'golf_swing_analyzer/video'/f'{paths[name]}.mp4' if name in paths
            else PRIOR.parent/'test_videos'/f'{name}.mp4')
    pipeline.SwingPhaseDetector = Capture
    started = time.perf_counter()
    clip = pipeline.trim_video(str(path), *bounds)
    try:
        rows, ann, traj, fps, det, eff = pipeline.process_video(clip, source_start_sec=bounds[0])
        inverse = {v: k for k, v in det.local_to_hist.items()}
        signal = dict(fps=det.fps, step=1, source_frames=det.source_frames,
                      local_idx=[inverse.get(i, -1) for i in range(len(det.source_frames))],
                      times=det.wrist_times_sec, cut_frames=det.cut_frames,
                      signals=list(zip(det.wrist_y_history, det.wrist_x_history, det.body_scales)))
        # Current visibility fallback permits extra annotated frames; source IDs
        # must still align, and trajectory IDs must refer to valid angle rows.
        assert {r['frame'] for r in rows} <= {r['frame'] for r in ann}
        assert {r['frame'] for r in traj} <= {r['frame'] for r in rows}
        return to_jsonable(dict(window=bounds, rows=rows, signal=signal,
                                elapsed_sec=time.perf_counter()-started))
    finally:
        os.unlink(clip)
        pipeline.SwingPhaseDetector = base


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infer', action='store_true')
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=1)
    args = parser.parse_args()
    ensure_open()
    path = DATA/'ablation_windows.json'
    windows = json.loads(path.read_text()) if path.exists() else plan()
    jobs = {(name, tuple(w)) for name, vv in windows.items() for w in vv.values()}
    for i, (name, bounds) in enumerate(sorted(jobs)):
        target = DATA/'app_cache'/(window_key(name, bounds)+'.json')
        if i % args.shards != args.shard or target.exists():
            continue
        if not args.infer:
            print('missing', name, bounds)
            continue
        dump(target, infer(name, bounds))
        print('inferred', name, bounds, flush=True)
    if args.shards > 1:
        return
    if all((DATA/'app_cache'/(window_key(n, w)+'.json')).exists() for n, w in jobs):
        results = {key: {} for key in variants()}
        for name, vv in windows.items():
            for key, w in vv.items():
                cached = json.loads((DATA/'app_cache'/(window_key(name, w)+'.json')).read_text())
                results[key][name] = app_result(cached, variants()[key])
        dump(DATA/'ablations.json', results)
        audit('ablations_complete', unique_trims=len(jobs))


if __name__ == '__main__':
    main()
