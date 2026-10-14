"""Verify development-only replay against the real baseline pipeline in Docker."""
import importlib.util
import json
import sys

import numpy as np

from common import DATA, annotations, audit, dump
from replay import load_signal, make_detector, predict

spec = importlib.util.spec_from_file_location(
    'original_phase', DATA/'baseline/golf_swing_analyzer/analyzer/phase_detector.py')
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
from analyzer import pipeline
pipeline.SwingPhaseDetector = original.SwingPhaseDetector

development = {r['id'] for r in annotations((1, 2, 3))}
ids = [int(v) for v in sys.argv[1:]] or [6, 14, 21]
target = DATA/'cache_pipeline_parity.json'
records = json.loads(target.read_text()) if target.exists() else []
checked = {r['id'] for r in records}
for ident in ids:
    assert ident in development
    if ident in checked:
        continue
    signal = load_signal(ident)
    path = DATA.parent/'golfdb/videos_160'/f'{ident}.mp4'
    fd, ann, traj, fps, actual, eff = pipeline.process_video(str(path))
    replay = make_detector(signal, cls=original.SwingPhaseDetector)
    replay.detect_all_phases()
    np.testing.assert_array_equal(actual.wrist_y_history, replay.wrist_y_history)
    assert actual.cut_frames == replay.cut_frames
    assert actual.local_to_hist == replay.local_to_hist
    assert actual.phase_boundaries_frames == replay.phase_boundaries_frames
    assert eff == signal['step']
    records.append(dict(id=ident, exact_signal=True, exact_bounds=True, effective_sample=eff))
dump(target, records)
audit('cache_pipeline_parity_passed', ids=ids)
print(json.dumps(records))
