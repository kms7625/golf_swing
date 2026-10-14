"""A hold interval and a club event must not silently become the same label."""
from dataclasses import replace

import numpy as np

from analyzer.phase_detector import SwingPhaseDetector
from analyzer.phase_parameters import CALIBRATED_PARAMETERS


def test_finish_hold_beginning_and_end_are_distinct_with_same_impact():
    times = np.arange(180)/30
    y = np.interp(times, [0,.8,2,2.4,3.3,4.2,5.5,6],
                  [400,400,200,410,160,160,300,300])
    result = {}
    for mode in ('settled_start', 'settled_end'):
        detector = SwingPhaseDetector(30, replace(CALIBRATED_PARAMETERS, finish_mode=mode))
        for i, value in enumerate(y):
            detector.update(i, value, value, time_sec=times[i], body_scale=200)
        detector.detect_all_phases()
        result[mode] = detector
    begin, end = result.values()
    assert begin.phase_boundaries['임팩트'] == end.phase_boundaries['임팩트']
    assert begin.phase_boundaries_sec['피니시'][0] < end.phase_boundaries_sec['피니시'][0]
    # Relaxation starts at 4.2s, but the smoothed wrist proxy can lag by its
    # positional window. It is not an exact club/whole-body relaxation label.
    assert 3.3 <= end.phase_boundaries_sec['피니시'][0] <= 4.2+CALIBRATED_PARAMETERS.smooth_sec
    assert begin.phase_boundaries['어드레스'][1] + 1 == begin.phase_boundaries['백스윙'][0]


def test_finish_without_observable_hold_keeps_fallback_inside_same_scene():
    times = np.arange(180)/30
    y = np.interp(times, [0,.8,2,2.4,3.3,6], [400,400,200,410,160,260])
    det = SwingPhaseDetector(30, replace(CALIBRATED_PARAMETERS, finish_hold_sec=10))
    for i, value in enumerate(y):
        det.update(i, value, value, source_frame=100+i, time_sec=times[i], body_scale=200)
    det.cut_frames = [240]
    det.detect_all_phases()
    assert det.phase_boundaries
    assert all(hi < 240 for lo, hi in det.phase_boundaries_frames.values())
