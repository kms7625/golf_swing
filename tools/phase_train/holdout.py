"""Freeze first; then atomically allow exactly one split-4 evaluation."""
import argparse
import importlib.util
import json
import os
from dataclasses import asdict

from common import DATA, ROOT, annotations, audit, dump, measure, sha, summary
from replay import load_signal, predict
from analyzer.phase_parameters import CALIBRATED_PARAMETERS, PhaseParameters


def sources():
    paths = list((ROOT/'golf_swing_analyzer/analyzer').glob('*.py'))
    paths += list((ROOT/'tools/phase_train').glob('*.py'))
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}


def freeze():
    if (DATA/'split4_once.lock').exists() or (DATA/'frozen.json').exists():
        raise RuntimeError('Already frozen or evaluated')
    for name in ('1', '2', '3', 'all'):
        assert (DATA/f'fit_{name}.json').exists()
    apps = json.loads((DATA/'apps_after.json').read_text())
    assert len(apps) == 7 and all('error' not in r for r in apps.values())
    selected = json.loads((DATA/'fit_all.json').read_text())['params']
    assert asdict(CALIBRATED_PARAMETERS) == selected
    assert all(r['params'] == selected for r in apps.values())
    assert json.loads((DATA/'default_parity.json').read_text())['identical']
    assert all(r['exact_bounds'] for r in json.loads((DATA/'cache_pipeline_parity.json').read_text()))
    records = [json.loads(p.read_text()) for p in (DATA/'cache').glob('*.json')]
    expected = {r['id'] for r in annotations((1, 2, 3, 4))}
    assert {r['id'] for r in records} == expected
    assert all(r['status'] in ('ok', 'excluded_fps') for r in records)
    from provenance import verify
    verify(final=False)
    frozen = dict(params=selected, sources=sources(), fit_sha=sha(DATA/'fit_all.json'),
                  apps_sha=sha(DATA/'apps_after.json'),
                  caches={str(r['id']): r.get('sha256') for r in records},
                  baseline_sha=sha(DATA/'baseline/golf_swing_analyzer/analyzer/phase_detector.py'),
                  prechecks_sha=sha(DATA/'pre_holdout_checks.json'),
                  prior_exposure='Required historical reports contain earlier split-4 results; see REPORT.')
    dump(DATA/'frozen.json', frozen)
    audit('parameters_frozen', frozen_sha=sha(DATA/'frozen.json'))


def evaluate():
    frozen = json.loads((DATA/'frozen.json').read_text())
    assert frozen['sources'] == sources(), 'Code changed since freeze'
    assert frozen['fit_sha'] == sha(DATA/'fit_all.json')
    # A failed run also consumes the holdout. No deletion/retry is permitted.
    fd = os.open(DATA/'split4_once.lock', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    os.close(fd)
    audit('split4_evaluation_started', frozen_sha=sha(DATA/'frozen.json'))
    baseline = DATA/'baseline/golf_swing_analyzer/analyzer/phase_detector.py'
    assert frozen['baseline_sha'] == sha(baseline)
    spec = importlib.util.spec_from_file_location('phase_3bdf45d', baseline)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    params = PhaseParameters(**frozen['params'])
    before, after, excluded = [], [], []
    for row in annotations((4,)):
        record = json.loads((DATA/'cache'/f'{row["id"]}.json').read_text())
        if record['status'] == 'excluded_fps':
            excluded.append(record)
            continue
        assert frozen['caches'][str(row['id'])] == sha(DATA/'cache'/f'{row["id"]}.npz')
        signal = load_signal(row['id'])
        before.append(measure(row, predict(signal, cls=module.SwingPhaseDetector)))
        after.append(measure(row, predict(signal, params)))
    dump(DATA/'split4_clips.json', dict(before=before, after=after, excluded=excluded))
    result = dict(before=summary(before), after=summary(after), excluded=excluded)
    dump(DATA/'split4_summary.json', result)
    audit('split4_evaluation_completed', n=len(before), result_sha=sha(DATA/'split4_summary.json'))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('freeze', 'evaluate'))
    args = parser.parse_args()
    freeze() if args.action == 'freeze' else evaluate()
