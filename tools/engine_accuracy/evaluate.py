"""Development-only replay and fold selection. Never load split 4 caches."""
import argparse
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/phase_train'))
from common import DATA, annotations, dump, measure, sha, summary
from replay import load_signal, make_detector, predict
from analyzer.phase_parameters import CALIBRATED_PARAMETERS as CURRENT
from analyzer.scoring import compute_score, compute_summary

OUT = DATA/'engine_accuracy_20261014'
FIX = DATA/'fix_20261014'
REF = json.loads((ROOT/'docs/research/phase_train/data/manual_reference.json').read_text())


def apps(params):
    previous = json.loads((FIX/'apps_after.json').read_text())
    result = {}
    for name, record in previous.items():
        key = name+'_'+('_'.join(f'{v:.3f}' for v in record['window']))
        cache = json.loads((FIX/'app_cache'/f'{key}.json').read_text())
        signal = cache['signal']
        available = {r['local_idx'] for r in cache['rows']}
        signal['metric_available'] = [i in available for i in signal['local_idx']]
        det = make_detector(signal, params)
        det.detect_all_phases()
        rows = [dict(r, phase=det.get_phase_for_frame(r['local_idx'])) for r in cache['rows']]
        rows = [r for r in rows if r['phase'] in det.phase_boundaries]
        measured = compute_summary(rows) if rows else {}
        result[name] = dict(score=compute_score(measured, ref_db={})[0] if rows else None,
                            bounds=det.phase_boundaries_frames, summary=measured)
    return result


def feasible(candidate, baseline):
    for name, result in candidate.items():
        old = baseline[name]
        if len(result['bounds']) != 7 or result['score'] < old['score']:
            return False
        for event, phase in [('top', '백스윙 톱'), ('impact', '임팩트')]:
            lo, hi = REF[name][event+'_bracket']
            distance = lambda frame: max(lo-frame, 0, frame-hi)
            if distance(result['bounds'][phase][0]) > distance(old['bounds'][phase][0]):
                return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['baseline', 'search', 'final'])
    args = parser.parse_args()
    rows = annotations([1, 2, 3])
    assert rows and {r['split'] for r in rows} == {1, 2, 3}
    signals = {r['id']: load_signal(r['id']) for r in rows}
    def evaluate(params):
        return [measure(r, predict(signals[r['id']], params)) for r in rows]
    def folds(records):
        return {str(i): summary([r for r in records if r['split'] == i]) for i in (1, 2, 3)}
    baseline = evaluate(CURRENT)
    app_base = apps(CURRENT)
    if args.mode != 'search':
        dump(OUT/f'{args.mode}_development.json', dict(params=asdict(CURRENT), records=baseline,
             folds=folds(baseline), overall=summary(baseline), apps=app_base,
             splits=[1, 2, 3], caches={str(i): sha(DATA/'cache'/f'{i}.npz') for i in signals}))
        print(args.mode, {k: v['all'] for k, v in folds(baseline).items()}, flush=True)
        return
    candidates = [('current', CURRENT)]
    candidates += [(f'address_{a}_finish_{f}', replace(CURRENT, address_offset_sec=a, finish_mode=f))
                   for a in (-.30, -.25, -.20, -.15, -.10, -.05, 0.)
                   for f in ('minimum', 'settled_start', 'settled_end')
                   if (a, f) != (CURRENT.address_offset_sec, CURRENT.finish_mode)]
    results = {}
    for name, params in candidates:
        app = apps(params)
        records = evaluate(params)
        results[name] = dict(params=asdict(params), feasible=feasible(app, app_base),
                             apps=app, records=records, folds=folds(records), overall=summary(records))
        print(name, results[name]['feasible'], results[name]['overall']['all']['mean_pce'], flush=True)
    selections = {}
    for held in (1, 2, 3, None):
        eligible = [name for name in results if results[name]['feasible']]
        def objective(name):
            training = [r for r in results[name]['records'] if r['split'] != held]
            return summary(training)['all']['mean_pce']
        chosen = max(eligible, key=objective)  # current wins ties
        validation = [r for r in results[chosen]['records'] if held is None or r['split'] == held]
        selections[str(held) if held else 'all'] = dict(chosen=chosen, validation=summary(validation))
    dump(OUT/'search.json', dict(results=results, selections=selections, splits=[1, 2, 3]))
    print('selections', selections, flush=True)


if __name__ == '__main__':
    main()
