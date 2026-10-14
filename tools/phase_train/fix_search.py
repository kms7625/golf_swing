"""Constrained three-fold configuration selection; never opens split 4."""
import itertools
import json
from dataclasses import asdict, replace

from common import DATA, audit, dump, measure, summary
from fix_common import (A_PARAMS, BASE, PRIOR, accepted, app_records, app_result,
                        ensure_open, window_key)
from replay import predict
from train import development


def main():
    ensure_open()
    applications = {}
    for name, record in app_records().items():
        path = DATA/'app_cache'/(window_key(name, record['window'])+'.json')
        applications[name] = json.loads(path.read_text())
    baseline = {n: app_result(c, BASE) for n, c in applications.items()}
    grid = list(itertools.product((.025, .05), (.75, 1.25), (0, .1, .2, .3)))
    audit('fix_search_start', splits=[1, 2, 3], scan='baseline',
          grid=grid, source='A single-parameter ablations; see PROTOCOL_fix.md')
    rows, signals = development()
    candidates = []
    for plateau, impact, support in grid:
        params = replace(A_PARAMS, plateau_ratio=plateau, impact_window_sec=impact,
                         address_min_valid_sec=support)
        apps = {n: app_result(c, params) for n, c in applications.items()}
        feasible = all(accepted(n, v, baseline[n]) and v['score'] >= baseline[n]['score']
                       for n, v in apps.items())
        result = dict(params=asdict(params), feasible=feasible, apps=apps)
        if feasible:
            records = [measure(r, predict(s, params)) for r, s in zip(rows, signals)]
            result['records'] = records
            result['folds'] = {str(f): summary([r for r in records if r['split'] == f])
                               for f in (1, 2, 3)}
            result['all'] = summary(records)
        candidates.append(result)
        print(params, feasible, result.get('all', {}).get('all', {}).get('mean_pce'), flush=True)
    feasible = [r for r in candidates if r['feasible']]
    assert feasible, 'Do not expose split 4 without a feasible candidate'
    folds = {}
    for fold in (1, 2, 3, 'all'):
        def training_score(c):
            return summary([r for r in c['records'] if r['split'] != fold])['all']['mean_pce']
        # Stable grid order breaks ties, preferring the smaller support guard.
        chosen = max(feasible, key=training_score)
        validation = [r for r in chosen['records'] if fold == 'all' or r['split'] == fold]
        previous = json.loads((PRIOR/f'fit_{fold}.json').read_text())
        folds[str(fold)] = dict(params=chosen['params'], train_pce=training_score(chosen),
                                validation=summary(validation), A=previous['after'])
    out = dict(folds=folds, candidates=candidates, scan='baseline',
               feasible_count=len(feasible), splits=[1, 2, 3])
    a = sum(folds[str(f)]['A']['all']['mean_pce'] for f in (1, 2, 3))/3
    fixed = sum(folds[str(f)]['validation']['all']['mean_pce'] for f in (1, 2, 3))/3
    out.update(A_fold_mean=a, fix_fold_mean=fixed, delta_pp=100*(fixed-a))
    attempt = 1+len(list(DATA.glob('selection_attempt_*.json')))
    dump(DATA/f'selection_attempt_{attempt}.json', out)
    audit('fix_search_complete', n=len(rows), feasible=len(feasible), delta_pp=out['delta_pp'],
          passed=fixed >= a-.01, attempt=attempt)
    assert fixed >= a-.01, (fixed, a)
    dump(DATA/'selection.json', out)
    dump(DATA/'fit_all.json', dict(params=folds['all']['params'], scan='baseline'))


if __name__ == '__main__':
    main()
