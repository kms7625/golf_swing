"""Freeze the fix, then consume exactly one SECOND split-4 exposure."""
import argparse
import json
import os
import subprocess
from dataclasses import asdict

from common import DATA, ROOT, annotations, audit, dump, measure, sha, summary
from fix_common import A_PARAMS, BASE, PRIOR, accepted, ensure_open
from replay import load_signal, predict
from analyzer.phase_parameters import CALIBRATED_PARAMETERS


def sources():
    paths = list((ROOT/'golf_swing_analyzer/analyzer').glob('*.py'))
    paths += list((ROOT/'tools/phase_train').glob('*.py'))
    paths += list((ROOT/'tests').glob('*.py'))
    paths += list((ROOT/'web/public/samples').glob('*.json'))
    paths += [ROOT/'tests/snapshots/ilban_baseline.json',
              ROOT/'docs/research/phase_train/PROTOCOL_fix.md']
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}


def safety():
    start = json.loads((DATA/'start.json').read_text())
    original = ROOT.parent/'golf_swing'
    status = subprocess.check_output(['git', '-C', str(original), 'status', '--porcelain=v1'],
                                     env=dict(os.environ, GIT_OPTIONAL_LOCKS='0')).decode()
    assert status == start['original_status'], 'Original workspace status changed'
    assert all(sha(original/n) == h for n, h in start['original_hashes'].items())
    assert sha(PRIOR/'audit.jsonl') == start['prior_audit_sha']
    assert sha(PRIOR/'split4_once.lock') == start['prior_lock_sha']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip() == start['head']
    assert subprocess.check_output(['git', 'branch', '--show-current']).decode().strip() == start['branch']
    for name in ('scoring.py', 'geometry.py', 'smoothing.py', 'reference_db.py'):
        relative = 'golf_swing_analyzer/analyzer/'+name
        assert subprocess.check_output(['git', 'show', 'HEAD:'+relative]) == (ROOT/relative).read_bytes()
    return dict(original_status_identical=True, original_tracked_files=len(start['original_hashes']),
                original_hashes_identical=True, prior_audit_and_lock_unchanged=True,
                no_commit=True, score_geometry_smoothing_reference_unchanged=True)


def freeze():
    ensure_open()
    chosen = json.loads((DATA/'fit_all.json').read_text())['params']
    assert asdict(CALIBRATED_PARAMETERS) == chosen
    selection = json.loads((DATA/'selection.json').read_text())
    assert selection['delta_pp'] >= -1
    apps = json.loads((DATA/'apps_after.json').read_text())
    ablations = json.loads((DATA/'ablations.json').read_text())
    expected = next(c['apps'] for c in selection['candidates'] if c['params'] == chosen)
    assert len(apps) == 7 and set(apps) == set(expected)
    for name, r in apps.items():
        assert 'error' not in r and r['params'] == chosen
        actual = dict(r, top=r['bounds']['백스윙 톱'][0], impact=r['bounds']['임팩트'][0])
        assert accepted(name, actual, ablations['baseline'][name])
        assert r['score'] >= ablations['baseline'][name]['score']
        assert all(r[k] == expected[name][k] for k in ('window', 'bounds', 'score', 'summary'))
        assert len(r['representatives']) == 7
    commands = json.loads((DATA/'validation_commands.json').read_text())
    assert {'pytest', 'web_build', 'web_lint', 'regen_snapshot'} <= set(commands)
    assert all(r['exit_code'] == 0 and sha(r['log']) == r['log_sha256'] for r in commands.values())
    assert json.loads((DATA/'default_parity.json').read_text())['identical']
    caches = json.loads((PRIOR/'frozen.json').read_text())['caches']
    assert all(sha(DATA/'cache'/f'{ident}.npz') == digest for ident, digest in caches.items())
    frozen = dict(params=chosen, scan='baseline', sources=sources(), caches=caches,
                  selection_sha=sha(DATA/'selection.json'), apps_sha=sha(DATA/'apps_after.json'),
                  commands_sha=sha(DATA/'validation_commands.json'), safety=safety(),
                  exposure='SECOND exposure; prior split4_once.lock and audit preserved')
    dump(DATA/'frozen.json', frozen)
    audit('fix_parameters_frozen', frozen_sha=sha(DATA/'frozen.json'), exposure=2)


def evaluate():
    frozen = json.loads((DATA/'frozen.json').read_text())
    assert frozen['sources'] == sources(), 'Source changed after freeze'
    assert frozen['selection_sha'] == sha(DATA/'selection.json')
    fd = os.open(DATA/'split4_once.lock', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    os.close(fd)  # Failure also consumes this exposure; never delete/retry.
    audit('fix_split4_evaluation_started', exposure=2, frozen_sha=sha(DATA/'frozen.json'))
    records = {k: [] for k in ('baseline', 'A', 'fix')}
    for row in annotations((4,)):
        assert sha(DATA/'cache'/f'{row["id"]}.npz') == frozen['caches'][str(row['id'])]
        signal = load_signal(row['id'])
        for name, params in (('baseline', BASE), ('A', A_PARAMS), ('fix', CALIBRATED_PARAMETERS)):
            records[name].append(measure(row, predict(signal, params)))
    dump(DATA/'split4_clips.json', records)
    result = {name: summary(rows) for name, rows in records.items()}
    dump(DATA/'split4_summary.json', result)
    audit('fix_split4_evaluation_completed', exposure=2, n=len(records['fix']),
          result_sha=sha(DATA/'split4_summary.json'))
    dump(DATA/'completion.json', dict(safety=safety(), sources_unchanged=sources() == frozen['sources'],
                                     exposure=2, result_sha=sha(DATA/'split4_summary.json')))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('freeze', 'evaluate'))
    action = parser.parse_args().action
    freeze() if action == 'freeze' else evaluate()
