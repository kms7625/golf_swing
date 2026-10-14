"""Check frozen protocol, one-time holdout audit, and original-workspace safety."""
import argparse
import json
import os
import subprocess
from collections import Counter
from datetime import datetime

from common import DATA, ROOT, annotations, dump, sha


def original_state():
    original = ROOT.parent/'golf_swing'
    evidence = ROOT/'docs/research/phase_train/data'
    current = subprocess.check_output(
        ['git', '-C', str(original), 'status', '--porcelain=v1'],
        env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
    expected = (evidence/'original_status_before.txt').read_bytes()
    hashes = json.loads((evidence/'original_tracked_hashes.json').read_text())
    changed = [name for name, digest in hashes.items()
               if not (original/name).is_file() or sha(original/name) != digest]
    return dict(status_identical=current == expected, tracked_files=len(hashes),
                changed_tracked=changed,
                status_sha256=sha(evidence/'original_status_before.txt'))


def cache_summary():
    rows = annotations((1, 2, 3, 4))
    records = [json.loads(p.read_text()) for p in (DATA/'cache').glob('*.json')]
    assert {r['id'] for r in records} == {r['id'] for r in rows}
    assert all(r['status'] in ('ok', 'excluded_fps') for r in records)
    assert all(r['sha256'] == sha(DATA/'cache'/f'{r["id"]}.npz')
               for r in records if r['status'] == 'ok')
    audit_records = [json.loads(line) for line in (DATA/'audit.jsonl').read_text().splitlines()]
    done = [r['utc'] for r in audit_records if r['event'] == 'cache_shard_complete']
    assert len(done) == 3, 'Wait for all original cache workers to finish'
    launched = json.loads((DATA/'launch.json').read_text())['utc']
    wall_sec = (datetime.fromisoformat(max(done))-datetime.fromisoformat(launched)).total_seconds()
    return dict(total=len(records), status=dict(Counter(r['status'] for r in records)),
                splits={str(s): dict(Counter(r['status'] for r in records if r['split'] == s))
                        for s in (1, 2, 3, 4)},
                excluded=[r for r in records if r['status'] == 'excluded_fps'],
                adaptive_ids=[r['id'] for r in records if r.get('adaptive_step', 1) > 1],
                cache_wall_sec=wall_sec,
                cumulative_worker_sec=sum(r['elapsed_sec'] for r in records))


def verify(final=False):
    evidence = ROOT/'docs/research/phase_train/data'
    prereg = json.loads((evidence/'preregistered.json').read_text())
    assert prereg['protocol_sha256'] == sha(ROOT/'docs/research/phase_train/PROTOCOL.md')
    assert prereg['search_sha256'] == sha(ROOT/'tools/phase_train/train.py')
    records = [json.loads(line) for line in (DATA/'audit.jsonl').read_text().splitlines()]
    counts = Counter(r['event'] for r in records)
    starts = [r for r in records if r['event'] == 'training_start']
    assert len(starts) == 4 and {r['fold'] for r in starts} == {'1', '2', '3', 'all'}
    assert all(set(r['train_splits']) <= {1, 2, 3} for r in starts)
    assert all(r['script_sha'] == prereg['search_sha256'] for r in starts)
    for fold in ('1', '2', '3', 'all'):
        done = [r for r in records if r['event'] == 'training_complete' and r['fold'] == fold]
        assert len(done) == 1 and done[0]['result_sha'] == sha(DATA/f'fit_{fold}.json')
    holdout_events = [r for r in records if r['event'] in
                      ('parameters_frozen', 'split4_evaluation_started', 'split4_evaluation_completed')]
    if final:
        assert [r['event'] for r in holdout_events] == [
            'parameters_frozen', 'split4_evaluation_started', 'split4_evaluation_completed']
        assert (DATA/'split4_once.lock').is_file()
        freeze_index = next(i for i, r in enumerate(records) if r['event'] == 'parameters_frozen')
        assert not any(r['event'].startswith(('training_', 'search_')) for r in records[freeze_index:])
        from holdout import sources
        assert json.loads((DATA/'frozen.json').read_text())['sources'] == sources()
        assert holdout_events[-1]['result_sha'] == sha(DATA/'split4_summary.json')
    else:
        assert not holdout_events and not (DATA/'split4_once.lock').exists()
    state = original_state()
    assert state['status_identical'] and not state['changed_tracked']
    commands = json.loads((DATA/'validation_commands.json').read_text())
    assert {'pytest', 'web_build', 'web_lint'} <= set(commands)
    assert all(commands[name]['exit_code'] == 0 for name in ('pytest', 'web_build', 'web_lint'))
    assert all(r['log_sha256'] == sha(r['log']) for r in commands.values())
    result = dict(final=final, original=state, cache=cache_summary(),
                  audit_counts=dict(counts), holdout_events=holdout_events,
                  audit_sha256=sha(DATA/'audit.jsonl'), protocol_unchanged=True,
                  search_unchanged=True, command_results=commands)
    dump(DATA/('completion.json' if final else 'pre_holdout_checks.json'), result)
    print(json.dumps({k: v for k, v in result.items() if k != 'command_results'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--final', action='store_true')
    verify(parser.parse_args().final)
