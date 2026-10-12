"""Reproducible Docker-only comparison; GolfDB videos/images never written to repo.
Run in golf-server:baseline with /work, /baseline, /datasets mounts.
"""
import argparse
import json
import os
import sys
import time
import resource
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('version', choices=['before', 'after'])
parser.add_argument('task', choices=['samples', 'golfdb', 'controls'])
parser.add_argument('--names', nargs='*')
parser.add_argument('--reuse-window', action='store_true')
args = parser.parse_args()
ROOT = Path('/work')
CODE = Path('/baseline') if args.version == 'before' else ROOT
OUT = ROOT / 'docs/research/phase_diag/after'
sys.path[:0] = [str(CODE / 'golf_swing_analyzer'), str(CODE)]
import cv2
import numpy as np
from analyzer import pipeline
from analyzer.phase_detector import PHASES
from analyzer.scoring import compute_summary, compute_score
from analyzer.reference_db import load_ref_db
from server.serialization import extract_representative_frames, frame_to_base64_jpeg, to_jsonable


def dump(path, value):
    path.write_text(json.dumps(to_jsonable(value), ensure_ascii=False, indent=None))


def run(path, offset=0, save_images=False):
    t = time.perf_counter()
    source_fps = pipeline.get_video_info(str(path))['fps']
    kwargs = {'source_start_sec': offset/source_fps + 1e-9} if args.version == 'after' else {}
    fd, ann, traj, fps, det, eff = pipeline.process_video(str(path), 3, **kwargs)
    original_offset = offset if args.version == 'before' else 0
    elapsed = time.perf_counter() - t
    summary = compute_summary(fd)
    score, issues = compute_score(summary, ref_db=load_ref_db())
    if hasattr(det, 'source_frames'):
        hist_frames = det.source_frames
    else:
        local_frames = {f['local_idx']: f['frame'] for f in fd}
        hist_frames = [local_frames[k] for k in det.local_to_hist]
    bounds = {p: [hist_frames[lo] + original_offset, hist_frames[hi] + original_offset]
              for p, (lo, hi) in det.phase_boundaries.items()}
    rep = extract_representative_frames(fd, ann)
    ids = {}
    for p in PHASES:
        display_rows = ann if args.version == 'after' else fd
        rows = [(i, f) for i, f in enumerate(display_rows) if f['phase'] == p]
        if not rows:
            continue
        j = 0 if p == '임팩트' else min(len(rows)-1, int(len(rows)*.85)) if p == '다운스윙' else len(rows)//2
        idx, row = rows[j]
        ids[p] = (row['frame'] if args.version == 'after' else sorted({f['local_idx']: f['frame'] for f in fd}.values())[min(idx,len(fd)-1)]) + original_offset
    record = dict(score=score, summary=summary, bounds=bounds, representatives=ids,
                  elapsed_sec=elapsed, max_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024, fps=fps, eff_sample=eff, frame_count=len(fd),
                  quality=getattr(det, 'quality', {}), cuts=getattr(det, 'cut_frames', []))
    if args.version == 'after':
        if save_images: assert set(ids) == set(PHASES), 'all seven representative images required'
        image_ids = {a['frame'] for a in ann}
        for phase, frame_id in ids.items():
            assert bounds[phase][0] <= frame_id <= bounds[phase][1]
            assert frame_id in image_ids
    if save_images:
        record['images'] = {p: frame_to_base64_jpeg(im) for p, im in rep.items()}
    payload = dict(score=score, issues=[{'level':a,'message':b} for a,b in issues], summary=summary,
                   frame_data=fd, fps=fps, eff_sample=eff, wrist_y_history=det.wrist_y_history,
                   phase_boundaries=det.phase_boundaries, rep_frames={p:frame_to_base64_jpeg(im) for p,im in rep.items()})
    for key in ('phase_boundaries_sec', 'phase_boundaries_frames', 'wrist_times_sec'):
        if hasattr(det, key): payload[key] = getattr(det,key)
    return record, payload


if args.task == 'samples':
    names = {'il-ban': ROOT/'golf_swing_analyzer/video/일반.mp4',
             'pro': ROOT/'golf_swing_analyzer/video/프로.mp4',
             'pro2': ROOT/'golf_swing_analyzer/video/프로2.mp4'}
    names.update({f'pexels_{n}':Path(f'/datasets/test_videos/pexels_{n}.mp4') for n in (8065880,6541855,35546329,34883764)})
    for name,path in names.items():
        if args.names and name not in args.names: continue
        target=OUT/f'{args.version}_{name}.json'
        if target.exists() and not args.reuse_window: continue
        try:
            previous=json.loads(target.read_text()) if args.reuse_window else {}
            # Record the scan signal for audit; detection/output is unchanged.
            original_detector = pipeline.SwingPhaseDetector
            if args.version == 'after':
                class CaptureDetector(original_detector):
                    def detect_all_phases(self):
                        result = super().detect_all_phases()
                        dump(OUT/f'scan_{name}.json', dict(fps=self.fps, y=self.wrist_y_history,
                             source_frames=self.source_frames, times=self.wrist_times_sec,
                             body=self.body_scales, cuts=self.cut_frames, candidates=self.candidates()))
                        return result
                pipeline.SwingPhaseDetector = CaptureDetector
            try:
                if args.reuse_window:
                    window=previous['window']; scan=previous['scan_sec']
                else:
                    t=time.perf_counter(); window=pipeline.auto_detect_swing_window(str(path)); scan=time.perf_counter()-t
            finally:
                pipeline.SwingPhaseDetector = original_detector
            trimmed=pipeline.trim_video(str(path),*window)
            try: record,payload=run(trimmed,int(window[0]*pipeline.get_video_info(str(path))['fps']),True)
            finally: os.unlink(trimmed)
            record.update(window=window,scan_sec=scan)
            dump(target,record)
            if args.version == 'after' and name in ('il-ban','pro','pro2'):
                dump(ROOT/f'web/public/samples/{name}.json',payload)
            print(name,window,record['score'],record['elapsed_sec'],flush=True)
        except Exception as e:
            dump(target,{'error':repr(e)})
            print(name,repr(e),flush=True)

elif args.task == 'golfdb':
    rows=json.loads(Path('/datasets/golfdb/golfdb_annotations.json').read_text())
    selected=[]
    for view in ('face-on','down-the-line'):
        for row in rows:
            if row['view']!=view or row['slow'] or row['split']!=4: continue
            path=Path(f'/datasets/golfdb/videos_160/{row["id"]}.mp4')
            if not path.exists() or abs(pipeline.get_video_info(str(path))['fps']-30)>.15: continue
            selected.append(row)
            if sum(r['view']==view for r in selected)>=25: break
    dump(OUT/'split4_selection.json',selected)
    events={'Address':'백스윙','Top':'백스윙 톱','Impact':'임팩트','Finish':'피니시'}
    for j,row in enumerate(selected):
        target=OUT/f'{args.version}_golfdb_{row["id"]}.json'
        if target.exists(): continue
        gt_all=[x-row['events'][0] for x in row['events'][1:9]]
        gt=dict(zip(events,[gt_all[i] for i in (0,3,5,7)]))
        tol=max(round((gt['Impact']-gt['Address'])/30),1)
        try:
            rec,_=run(Path(f'/datasets/golfdb/videos_160/{row["id"]}.mp4'))
            pred={e:rec['bounds'][p][0] for e,p in events.items() if p in rec['bounds']}
        except Exception as e: rec={'error':repr(e)};pred={}
        rec.update(id=row['id'],view=row['view'],split=4,gt=gt,pred=pred,tolerance=tol,
                   correct={e: e in pred and abs(pred[e]-gt[e])<=tol for e in events})
        dump(target,rec)
        print(j+1,len(selected),row['id'],rec['correct'],flush=True)

elif args.task == 'controls':
    video=ROOT/'golf_swing_analyzer/video/일반.mp4'
    controls=[('static',video,1.0,65/30), ('selected',video,1.5,9.7),('ten_seconds',video,0,299/30),
              ('red_full',Path('/datasets/test_videos/pexels_35546329.mp4'),None,None),
              ('difficult_full',Path('/datasets/test_videos/pexels_34883764.mp4'),None,None)]
    for name,path,start,end in controls:
        if args.names and name not in args.names: continue
        target=OUT/f'{args.version}_control_{name}.json'
        if target.exists():continue
        trimmed=pipeline.trim_video(str(path),start,end) if start is not None else str(path)
        t=time.perf_counter()
        try:
            rec,_=run(trimmed,int(start*30) if start else 0)
        except Exception as exc:rec={'error':repr(exc),'elapsed_sec':time.perf_counter()-t}
        finally:
            if start is not None:os.unlink(trimmed)
        dump(target,rec);print(name,{k:v for k,v in rec.items() if k not in ('summary','images')},flush=True)
