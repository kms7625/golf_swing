"""Assemble measured gates, preserving raw execution artifacts and failures."""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get('PHASE_DATA', '/datasets/golfdb_pose'))
OUT = DATA/'engine_accuracy_20261014'


def read(name):
    return json.loads((OUT/name).read_text())


def main():
    baseline, final = read('apps_baseline.json'), read('apps_final.json')
    reference = json.loads((ROOT/'docs/research/phase_train/data/manual_reference.json').read_text())
    assert len(baseline) == len(final) == 7
    app_gates = {}
    for name, before in baseline.items():
        after = final[name]
        good = 'error' not in after and after['score'] >= before['score']
        for event, phase in [('top', '백스윙 톱'), ('impact', '임팩트')]:
            lo, hi = reference[name][event+'_bracket']
            distance = lambda frame: max(lo-frame, frame-hi, 0)
            good &= distance(after['bounds'][phase][0]) <= distance(before['bounds'][phase][0])
        app_gates[name] = dict(pass_gate=bool(good), score_before=before['score'], score_after=after['score'],
             bounds_before=before['bounds'], bounds_after=after['bounds'], window_before=before['window'],
             window_after=after['window'], summary_before=before['summary'], summary_after=after['summary'])
    before_dev, after_dev = read('baseline_development.json'), read('final_development.json')
    folds = {str(i): dict(before=before_dev['folds'][str(i)]['all'], after=after_dev['folds'][str(i)]['all'])
             for i in (1, 2, 3)}
    mean_delta = sum(v['after']['mean_pce']-v['before']['mean_pce'] for v in folds.values())/3
    fps = read('fps_final_avi.json')
    assert len(fps) == 21
    fps_comparison = {}
    for name in baseline:
        control = fps[name+'_30']
        entries = {}
        for kind in ('dup', 'mci_aligned'):
            candidate = fps[name+'_60_'+kind]
            if 'error' in candidate or 'error' in control:
                entries[kind] = dict(error=candidate.get('error', control.get('error')))
                continue
            deltas = {phase: [candidate['bounds_sec'][phase][j]-pair[j] for j in (0, 1)]
                      for phase, pair in control['bounds_sec'].items()}
            entries[kind] = dict(score=candidate['score'], boundaries_sec=candidate['bounds_sec'],
                 deltas_sec=deltas, max_abs_delta_sec=max(abs(v) for pair in deltas.values() for v in pair),
                 equal_score=candidate['score'] == control['score'])
        fps_comparison[name] = dict(control_score=control.get('score'),
             control_boundaries_sec=control.get('bounds_sec'), variants=entries)
    shot = read('shot_probe.json')['records']
    golf = [r for r in shot if r['dataset'] == 'golfdb']
    shot_summary = {}
    for threshold in ('180', '220'):
        values = [r['measurement']['thresholds'][threshold] for r in golf]
        shot_summary[threshold] = dict(n=len(values), no_candidates=sum(v['stable_candidates'] == 0 for v in values),
             multiple_candidates=sum(v['stable_candidates'] > 1 for v in values),
             no_disappearance=sum(v['disappeared'] == 0 for v in values),
             multiple_disappearances=sum(v['disappeared'] > 1 for v in values))
    result = dict(apps=app_gates, folds=folds, fold_mean_delta=mean_delta,
                  pass_e3=all(r['pass_gate'] for r in app_gates.values()) and mean_delta >= -.01,
                  cache_clock_parity=all(r['parity'] for r in read('cache_clock.json')['records']),
                  fps=fps_comparison, shot_golfdb=shot_summary,
                  artifacts={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.json') if p.name != 'summary.json'})
    (OUT/'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    compact = {k:v for k,v in result.items() if k != 'artifacts'}
    (ROOT/'docs/research/engine_accuracy/summary.json').write_text(
        json.dumps(compact, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n')
    print('E3', result['pass_e3'], 'cache clock', result['cache_clock_parity'], flush=True)
    if not result['pass_e3'] or not result['cache_clock_parity']: sys.exit(1)


if __name__ == '__main__':
    main()
