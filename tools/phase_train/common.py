"""Shared paths, audit log and the unchanged phase_fix_eval PCE contract."""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get('PHASE_DATA', '/datasets/golfdb_pose'))
ANNOTATIONS = DATA.parent / 'golfdb/golfdb_annotations.json'
EVENTS = dict(zip(('Address', 'Top', 'Impact', 'Finish'),
                  ('백스윙', '백스윙 톱', '임팩트', '피니시')))
sys.path.insert(0, str(ROOT / 'golf_swing_analyzer'))


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(event, **fields):
    DATA.mkdir(parents=True, exist_ok=True)
    record = dict(utc=datetime.now(timezone.utc).isoformat(), event=event, **fields)
    with (DATA / 'audit.jsonl').open('a') as f:
        f.write(json.dumps(record, ensure_ascii=False, allow_nan=False)+'\n')


def annotations(splits):
    # Drop other splits immediately; callers must not inspect held-out events.
    return [r for r in json.loads(ANNOTATIONS.read_text())
            if r['split'] in splits and not r['slow']
            and r['view'] in ('face-on', 'down-the-line')]


def ground_truth(row):
    # Exactly tests/phase_fix_eval.py: local clip frames = events - clip offset.
    all_events = [x-row['events'][0] for x in row['events'][1:9]]
    gt = dict(zip(EVENTS, (all_events[i] for i in (0, 3, 5, 7))))
    return gt, max(round((gt['Impact']-gt['Address'])/30), 1)


def measure(row, prediction):
    gt, tolerance = ground_truth(row)
    errors = {e: int(prediction[e]-gt[e]) if e in prediction else None for e in EVENTS}
    return dict(id=row['id'], split=row['split'], view=row['view'], gt=gt,
                pred=prediction, tolerance=tolerance, errors=errors,
                correct={e: v is not None and abs(v) <= tolerance for e, v in errors.items()})


def summary(records):
    result = {}
    for view in ('all', 'face-on', 'down-the-line'):
        rows = [r for r in records if view == 'all' or r['view'] == view]
        events = {}
        for e in EVENTS:
            errors = [abs(r['errors'][e]) for r in rows if r['errors'][e] is not None]
            events[e] = dict(pce=sum(r['correct'][e] for r in rows)/max(len(rows), 1),
                             median_abs_error=float(np.median(errors)) if errors else None,
                             within5=sum(x <= 5 for x in errors)/max(len(rows), 1),
                             predicted=len(errors))
        result[view] = dict(n=len(rows), rejected=sum(not r['pred'] for r in rows),
                            events=events, mean_pce=float(np.mean([v['pce'] for v in events.values()])))
    return result
