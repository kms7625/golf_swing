"""Separate regression-fix experiment; original A audit/holdout stays immutable."""
import json
from dataclasses import asdict, replace

import common
from common import DATA, ROOT, dump
from replay import make_detector
from analyzer.phase_parameters import PhaseParameters

PRIOR = DATA.parent
common.ANNOTATIONS = PRIOR.parent/'golfdb/golfdb_annotations.json'
A_PARAMS = PhaseParameters(**json.loads((PRIOR/'fit_all.json').read_text())['params'])
BASE = PhaseParameters()
REFERENCES = json.loads((ROOT/'docs/research/phase_train/data/manual_reference.json').read_text())


def variants():
    return {'A': A_PARAMS, 'baseline': BASE, **{
        'undo_'+k: replace(A_PARAMS, **{k: v}) for k, v in asdict(BASE).items()
        if k != 'address_min_valid_sec'}}


def ensure_open():
    assert DATA.name == 'fix_20261014', 'Use the dedicated fix result root'
    assert not (DATA/'frozen.json').exists(), 'No tuning after freeze'
    assert not (DATA/'split4_once.lock').exists(), 'Second exposure already consumed'


def window(signal, params, total):
    """Exact auto_detect_swing_window post-inference logic, cached scan input."""
    det = make_detector(signal, params)
    if not det.detect_all_phases():
        return None
    c = det.selected_cycle
    lo, _ = c['segment']
    ts = det.wrist_times_sec
    top = ts[c['top']]
    pre = max(1.0, min(1.5, 2*(ts[c['impact']]-top)))
    start = max(ts[lo], top-3.0, ts[c['onset']]-pre)
    end = min(total, ts[c['end']]+1/signal['fps'])
    return [round(start, 3), round(end, 3)]


def app_records():
    return json.loads((PRIOR/'apps_before.json').read_text())


def window_key(name, bounds):
    return name+'_'+('_'.join(f'{v:.3f}' for v in bounds))


def distance(frame, bracket):
    return max(bracket[0]-frame, 0, frame-bracket[1])


def app_result(cached, params):
    """Relabel all cached angle rows; formulas and raw argmax remain unchanged."""
    from analyzer.scoring import compute_score, compute_summary
    det = make_detector(cached['signal'], params)
    available = {r['local_idx'] for r in cached['rows']}
    det.metric_available_history = [i in available for i in cached['signal']['local_idx']]
    if not det.detect_all_phases():
        return {'error': 'no cycle'}
    rows = [dict(r, phase=det.get_phase_for_frame(r['local_idx'])) for r in cached['rows']]
    rows = [r for r in rows if r['phase'] in det.phase_boundaries]
    if not rows:
        return {'error': 'no angle rows'}
    measured = compute_summary(rows)
    score, issues = compute_score(measured, ref_db={})
    return dict(window=cached['window'], bounds=det.phase_boundaries_frames,
                score=score, summary=measured, issues=issues,
                top=det.phase_boundaries_frames['백스윙 톱'][0],
                impact=det.phase_boundaries_frames['임팩트'][0])


def accepted(name, result, baseline):
    if 'error' in result:
        return False
    ref = REFERENCES[name]
    return all(distance(result[e], ref[e+'_bracket']) <=
               distance(baseline[e], ref[e+'_bracket']) for e in ('top', 'impact'))
