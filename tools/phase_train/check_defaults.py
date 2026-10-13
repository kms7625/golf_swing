"""Exact baseline parity on development caches; never opens split 4."""
import importlib.util
import json

from common import DATA, annotations, audit, dump
from replay import load_signal, make_detector
from analyzer.phase_parameters import PhaseParameters

spec = importlib.util.spec_from_file_location(
    'baseline', DATA/'baseline/golf_swing_analyzer/analyzer/phase_detector.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
checked = []
for row in annotations((1, 2, 3)):
    status = json.loads((DATA/'cache'/f'{row["id"]}.json').read_text())
    if status['status'] == 'excluded_fps':
        continue
    assert status['status'] == 'ok'
    signal = load_signal(row['id'])
    before = make_detector(signal, cls=module.SwingPhaseDetector)
    after = make_detector(signal, PhaseParameters())
    before.detect_all_phases()
    after.detect_all_phases()
    for attr in ('phase_boundaries', 'phase_boundaries_frames', 'phase_boundaries_sec',
                 'frame_phases', 'local_to_hist'):
        assert getattr(before, attr) == getattr(after, attr), (row['id'], attr)
    assert before.candidates() == after.candidates(), row['id']
    checked.append(row['id'])
dump(DATA/'default_parity.json', dict(n=len(checked), splits=[1,2,3], identical=True))
audit('default_parity_passed', n=len(checked), splits=[1,2,3])
print('Exact original parity:', len(checked))
