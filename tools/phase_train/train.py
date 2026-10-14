"""Fixed two-pass coordinate search, three split folds, then all development data.

No held-out cache or labels are evaluated. Ties keep the current parameter.
"""
import argparse
import json
from dataclasses import asdict, replace

import numpy as np

from common import DATA, annotations, audit, dump, ground_truth, measure, sha, summary
from replay import app_feasible, app_signals, load_signal, predict
from analyzer.phase_parameters import PhaseParameters

# Prespecified before any development or held-out scoring; units are seconds or
# fractions of torso/rise. Ranges are engineering hypotheses, not literature facts.
GRID = {
    'plateau_ratio': [0.0, .025, .05, .075, .10],
    'top_offset_sec': [0.0, 1/30, 2/30, 3/30],
    'onset_fraction': [.02, .05, .10, .15],
    'address_offset_sec': [-.20, -.10, -1/30, 0.0],
    'address_window_sec': [1.0, 2.0, 3.0],
    'impact_window_sec': [.50, .75, 1.25],
    'finish_mode': ['minimum', 'settled_start', 'settled_end'],
    'finish_speed_ratio': [.10, .20, .40],
    'finish_hold_sec': [.10, .20, .30],
    'finish_window_sec': [2.0, 3.0],
    'smooth_sec': [1/15, .10, 1/6],
}


def development():
    rows, signals = [], []
    for row in annotations((1, 2, 3)):
        status_path = DATA/'cache'/f'{row["id"]}.json'
        if not status_path.exists():
            raise RuntimeError(f'Cache not complete: {row["id"]}')
        status = json.loads(status_path.read_text())
        if status['status'] == 'excluded_fps':
            continue
        if status['status'] != 'ok':
            raise RuntimeError(f'Cache failure must be resolved, not silently dropped: {status}')
        rows.append(row)
        signals.append(load_signal(row['id']))
    return rows, signals


def fit(rows, signals, indices, applications, label):
    params = PhaseParameters()
    memo = {}

    def objective(p):
        if p in memo:
            return memo[p]
        if not app_feasible(p, applications):
            score = -1.0
        else:
            correct = 0
            for i in indices:
                pred = predict(signals[i], p)
                gt, tol = ground_truth(rows[i])
                correct += sum(e in pred and abs(pred[e]-v) <= tol for e, v in gt.items())
            score = correct/(4*len(indices))
        memo[p] = score
        audit('search_candidate', fold=label, params=asdict(p), score=score)
        return score

    best = objective(params)
    for turn in range(2):
        for key, values in GRID.items():
            origin = params
            for value in values:
                candidate = replace(origin, **{key: value})
                score = objective(candidate)
                if score > best:
                    params, best = candidate, score
            print(label, turn, key, round(best, 5), flush=True)
    return params, best, len(memo)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fold', choices=('1', '2', '3', 'all'), required=True)
    args = parser.parse_args()
    if (DATA/'split4_once.lock').exists() or (DATA/'frozen.json').exists():
        raise RuntimeError('Calibration is locked; do not tune after final evaluation')
    rows, signals = development()
    applications = app_signals()
    fold = int(args.fold) if args.fold != 'all' else None
    train = [i for i, r in enumerate(rows) if r['split'] != fold]
    validation = [i for i, r in enumerate(rows) if r['split'] == fold] if fold else train
    audit('training_start', fold=args.fold, train_splits=sorted({rows[i]['split'] for i in train}),
          grid=GRID, rows=len(train), script_sha=sha(__file__))
    params, score, count = fit(rows, signals, train, applications, args.fold)
    before = [measure(rows[i], predict(signals[i], PhaseParameters())) for i in validation]
    after = [measure(rows[i], predict(signals[i], params)) for i in validation]
    result = dict(fold=args.fold, params=asdict(params), train_pce=score, candidates=count,
                  train_n=len(train), validation_n=len(validation),
                  before=summary(before), after=summary(after), app_cached_rejected=0)
    dump(DATA/f'fit_{args.fold}.json', result)
    dump(DATA/f'validation_{args.fold}.json', dict(before=before, after=after))
    audit('training_complete', fold=args.fold, result_sha=sha(DATA/f'fit_{args.fold}.json'))


if __name__ == '__main__':
    main()
