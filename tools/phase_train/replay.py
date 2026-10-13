"""Replay cached signals without MediaPipe inference or frame data access."""
import json

import numpy as np

from common import DATA, EVENTS
from analyzer.phase_detector import SwingPhaseDetector


def load_signal(ident):
    with np.load(DATA/'cache'/f'{ident}.npz', allow_pickle=False) as z:
        prefix = 'adaptive_' if 'adaptive_step' in z else ''
        signal = {k: z[prefix+k].tolist() for k in
                  ('fps', 'step', 'signals', 'source_frames', 'local_idx', 'times', 'cut_frames')}
        # process_video may reject a detected cycle with no angle rows. Recreate
        # its visibility/previous-metric gate, including cuts between samples.
        visible = np.all(z[prefix+'landmarks'][:, [11,12,23,24,25,26], 3] > .5, axis=1)
        available, previous, last = [], False, -1
        for frame, local, good in zip(signal['source_frames'], signal['local_idx'], visible):
            if any(last < cut <= frame for cut in signal['cut_frames']):
                previous = False
            if local >= 0 and good:
                previous = True
            available.append(local >= 0 and previous)
            last = frame
        signal['metric_available'] = available
        return signal


def make_detector(signal, params=None, cls=SwingPhaseDetector):
    kwargs = {} if params is None else {'params': params}
    det = cls(fps=signal['fps']/signal['step'], **kwargs)
    # Bulk restore exactly the history update contract, including pose-only keys.
    det.wrist_y_history = [v[0] for v in signal['signals']]
    det.wrist_x_history = [v[1] for v in signal['signals']]
    det.body_scales = [v[2] for v in signal['signals']]
    det.source_frames = signal['source_frames']
    det.wrist_times_sec = signal['times']
    det.cut_frames = signal['cut_frames']
    det.local_to_hist = {v: i for i, v in enumerate(signal['local_idx']) if v >= 0}
    det.hip_x_history = [0.0]*len(det.source_frames)
    det.shoulder_rot_hist = [0.0]*len(det.source_frames)
    return det


def predict(signal, params=None, cls=SwingPhaseDetector):
    det = make_detector(signal, params, cls)
    det.detect_all_phases()
    if det.phase_boundaries and 'metric_available' in signal:
        start = det.phase_boundaries['어드레스'][0]
        end = det.phase_boundaries['피니시'][1]
        if not any(signal['metric_available'][start:end+1]):
            return {}
    return {event: int(det.phase_boundaries_frames[phase][0])
            for event, phase in EVENTS.items() if phase in det.phase_boundaries_frames}


def app_signals():
    records = json.loads((DATA/'apps_before.json').read_text())
    assert len(records) == 7 and all('error' not in r for r in records.values())
    return [s for r in records.values() for s in r['signals']]


def app_feasible(params, signals):
    return all(len(predict(s, params)) == 4 for s in signals)
