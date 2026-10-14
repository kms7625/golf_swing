"""Research probe only: bright ground objects and their persistence, no classifier.

Absence of a visible ball is never evidence of a practice swing. GolfDB has no
practice/shot labels; its Impact annotation supplies nominal positive windows.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/phase_train'))
from common import DATA, annotations, dump, ground_truth

OUT = DATA/'engine_accuracy_20261014'


def probe(path, impact):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width, height = [int(cap.get(v)) for v in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT)]
    frames = {}
    # Three before/after observations, separated from the club occlusion window.
    for dt in (-.3, -.2, -.1, .1, .2, .3):
        fi = max(0, round(impact+dt*fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ok, frame = cap.read()
        if ok:
            frames[dt] = frame
    cap.release()
    if len(frames) != 6:
        return dict(error='insufficient frames', fps=fps)
    # Broad lower-image ROI avoids hand-picking a favorable ball location.
    # It also admits shoes/tees/grass: ambiguity is measured, not hidden.
    ys, xs = slice(round(.55*height), height), slice(0, width)
    before = [cv2.cvtColor(frames[dt][ys, xs], cv2.COLOR_BGR2GRAY) for dt in (-.3, -.2, -.1)]
    after = [cv2.cvtColor(frames[dt][ys, xs], cv2.COLOR_BGR2GRAY) for dt in (.1, .2, .3)]
    results = {}
    for threshold in (180, 220):
        masks = [a > threshold for a in before]
        stable = np.logical_and.reduce(masks).astype(np.uint8)
        count, labels, stats, centers = cv2.connectedComponentsWithStats(stable)
        objects = []
        for i in range(1, count):
            x, y, w, h, area = stats[i]
            if not 1 <= area <= max(9, .0005*width*height) or max(w, h) > max(6, .035*width):
                continue
            cy, cx = round(centers[i][1]), round(centers[i][0])
            region = (slice(max(0, cy-2), min(stable.shape[0], cy+3)),
                      slice(max(0, cx-2), min(width, cx+3)))
            retained = [bool(np.any(a[region] > threshold)) for a in after]
            objects.append(dict(x=float(centers[i][0]), y=float(centers[i][1]+ys.start),
                                area=int(area), after_retained=retained))
        results[str(threshold)] = dict(stable_candidates=len(objects),
             disappeared=sum(not any(o['after_retained']) for o in objects), objects=objects)
    delta = np.abs(np.median(after, axis=0)-np.median(before, axis=0))
    return dict(fps=fps, size=[width, height], impact_frame=impact, roi=[0, ys.start, width, height],
                mean_absolute_difference=float(delta.mean()), changed_fraction=float(np.mean(delta > 25)),
                thresholds=results)


def sheet(path, impact, target):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    tiles = []
    for dt in (-.2, -.1, 0, .1, .2):
        fi = round(impact+dt*fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ok, frame = cap.read()
        if not ok: continue
        h, w = frame.shape[:2]
        frame = cv2.resize(frame, (320, round(320*h/w)))
        cv2.putText(frame, f'f{fi} {dt:+.1f}s', (5, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 1)
        tiles.append(frame)
    cap.release()
    cv2.imwrite(str(target), np.hstack(tiles))


def main():
    cv2.setNumThreads(1)
    apps = json.loads((OUT/'apps_baseline.json').read_text())
    ref = json.loads((ROOT/'docs/research/phase_train/data/manual_reference.json').read_text())
    names = {'il-ban': '일반', 'pro': '프로', 'pro2': '프로2'}
    records = []
    sheets = OUT/'shot_sheets'
    sheets.mkdir(exist_ok=True)
    for name, result in apps.items():
        path = (ROOT/'golf_swing_analyzer/video'/f'{names[name]}.mp4' if name in names
                else DATA.parent/'test_videos'/f'{name}.mp4')
        for kind, impact in [('selected', result['bounds']['임팩트'][0]),
                             ('manual_reference', round(np.mean(ref[name]['impact_bracket'])))]:
            record = dict(dataset='app', name=name, kind=kind, measurement=probe(path, impact))
            records.append(record)
            sheet(path, impact, sheets/f'{name}_{kind}.jpg')
    rows = annotations([1, 2, 3])
    for split in (1, 2, 3):
        selected = sorted([r for r in rows if r['split'] == split], key=lambda r: r['id'])[:10]
        for row in selected:
            gt, _ = ground_truth(row)
            path = DATA.parent/'golfdb/videos_160'/f"{row['id']}.mp4"
            records.append(dict(dataset='golfdb', id=row['id'], split=split,
                                label='nominal Impact; no practice label', measurement=probe(path, gt['Impact'])))
    dump(OUT/'shot_probe.json', dict(records=records, splits=[1, 2, 3],
         warning='Bright objects are hypotheses, not ball detections; no practice classifier validated.'))
    print('records', len(records), flush=True)


if __name__ == '__main__':
    main()
