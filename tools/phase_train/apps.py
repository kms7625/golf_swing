"""Seven actual automatic-window → trim → process comparisons in Docker."""
import argparse
import json
import os
import sys
import time

from common import DATA, ROOT, audit, dump


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('version', choices=('before', 'after'))
    parser.add_argument('--params')
    parser.add_argument('--export', action='store_true')
    args = parser.parse_args()
    code = DATA/'baseline' if args.version == 'before' else ROOT
    sys.path[:0] = [str(code/'golf_swing_analyzer'), str(code/'server')]
    from analyzer import pipeline
    from analyzer.scoring import compute_score, compute_summary
    from analyzer.reference_db import load_ref_db
    from serialization import extract_representative_frames, frame_to_base64_jpeg, to_jsonable
    params = None
    if args.params:
        from analyzer.phase_parameters import PhaseParameters
        params = PhaseParameters(**json.loads(open(args.params).read())['params'])
    base = pipeline.SwingPhaseDetector
    signals = []

    class Capture(base):
        def __init__(self, *a, **kw):
            if params is not None:
                kw['params'] = params
            super().__init__(*a, **kw)

        def detect_all_phases(self):
            result = super().detect_all_phases()
            inverse = {v: k for k, v in self.local_to_hist.items()}
            signals.append(dict(fps=self.fps, step=1, source_frames=self.source_frames,
                                local_idx=[inverse.get(i, -1) for i in range(len(self.source_frames))],
                                times=self.wrist_times_sec, cut_frames=self.cut_frames,
                                signals=list(zip(self.wrist_y_history, self.wrist_x_history, self.body_scales))))
            return result

    pipeline.SwingPhaseDetector = Capture
    paths = {n: ROOT/'golf_swing_analyzer/video'/f'{k}.mp4'
             for n, k in [('il-ban', '일반'), ('pro', '프로'), ('pro2', '프로2')]}
    paths.update({f'pexels_{n}': DATA.parent/'test_videos'/f'pexels_{n}.mp4'
                  for n in (8065880, 6541855, 35546329, 34883764)})
    records = {}
    for name, path in paths.items():
        signals.clear()
        started = time.perf_counter()
        try:
            window = pipeline.auto_detect_swing_window(str(path))
            clip = pipeline.trim_video(str(path), *window)
            try:
                fd, ann, traj, fps, det, eff = pipeline.process_video(clip, source_start_sec=window[0])
            finally:
                os.unlink(clip)
            summary = compute_summary(fd)
            score, issues = compute_score(summary, ref_db=load_ref_db())
            reps = extract_representative_frames(fd, ann)
            assert len(reps) == 7
            by_image = {id(a['image']): a['frame'] for a in ann}
            ids = {p: by_image[id(im)] for p, im in reps.items()}
            for phase, frame in ids.items():
                lo, hi = det.phase_boundaries_frames[phase]
                assert lo <= frame <= hi
            assert {f['frame'] for f in fd} <= {f['frame'] for f in ann}
            records[name] = dict(window=window, fps=fps, score=score, summary=summary,
                                 bounds=det.phase_boundaries_frames, representatives=ids,
                                 eff_sample=eff, quality=det.quality, signals=list(signals))
            if hasattr(det, 'params'):
                records[name]['params'] = det.params.__dict__
            if args.export and name in ('il-ban', 'pro', 'pro2'):
                payload = dict(score=score, summary=summary, issues=[{'level':a, 'message':b} for a,b in issues],
                               frame_data=fd, fps=fps, eff_sample=eff,
                               wrist_y_history=det.wrist_y_history, phase_boundaries=det.phase_boundaries,
                               phase_boundaries_frames=det.phase_boundaries_frames,
                               phase_boundaries_sec=det.phase_boundaries_sec, wrist_times_sec=det.wrist_times_sec,
                               rep_frames={p: frame_to_base64_jpeg(im) for p,im in reps.items()})
                # Keep generated samples separate until selection is frozen.
                dump(DATA/'samples'/f'{name}.json', to_jsonable(payload))
        except Exception as exc:
            records[name] = dict(error=repr(exc))
        records[name]['elapsed_sec'] = time.perf_counter()-started
        dump(DATA/f'apps_{args.version}.json', to_jsonable(records))
        print(name, {k:v for k,v in records[name].items() if k not in ('signals','summary')}, flush=True)
    audit('apps_complete', version=args.version, rejected=sum('error' in r for r in records.values()))
    if any('error' in r for r in records.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
