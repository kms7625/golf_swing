"""Behavioral oracle: untouched 3bdf45d detector, including missing/cut clocks."""
import importlib.util
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from analyzer.phase_detector import SwingPhaseDetector
from analyzer.phase_parameters import PhaseParameters

_spec = importlib.util.spec_from_file_location(
    'phase_3bdf45d', Path(__file__).parent/'fixtures/phase_detector_3bdf45d.py')
_baseline = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_baseline)


def populate(cls, y, fps, cuts, **kwargs):
    det = cls(fps=fps, **kwargs)
    local = 0
    for i, value in enumerate(y):
        detected = np.isfinite(value)
        det.update(local if detected else None, value, value,
                   source_frame=55+i*2, time_sec=i/fps, body_scale=200)
        local += int(detected)
    det.cut_frames = [55+c*2 for c in cuts]
    det.detect_all_phases()
    return det


@pytest.mark.parametrize('fps', [15, 24, 29.97, 30, 60])
@pytest.mark.parametrize('case', ['swing', 'jitter', 'short_gap', 'long_gap', 'cut', 'plateau'])
def test_default_parameters_exactly_match_original(fps, case):
    rng = np.random.default_rng(1234)
    y = np.interp(np.arange(180), [0,25,60,70,95,179], [400,400,200,410,160,160])
    y += rng.normal(0, .2, len(y))
    cuts = []
    if case == 'jitter':
        y = 400 + rng.normal(0, 1, len(y))
    elif case == 'short_gap':
        y[40:42] = np.nan
    elif case == 'long_gap':
        y[40:59] = np.nan
    elif case == 'cut':
        cuts = [65]
    elif case == 'plateau':
        y = np.r_[y[:60], np.full(20, 200), y[60:]]
    before = populate(_baseline.SwingPhaseDetector, y, fps, cuts)
    after = populate(SwingPhaseDetector, y, fps, cuts, params=PhaseParameters())
    for attr in ('phase_boundaries', 'phase_boundaries_frames', 'phase_boundaries_sec',
                 'frame_phases', 'local_to_hist'):
        assert getattr(before, attr) == getattr(after, attr)
    assert before.candidates() == after.candidates()
    assert [before.get_phase_for_frame(i) for i in range(len(y))] == [
        after.get_phase_for_frame(i) for i in range(len(y))]


def test_event_offsets_keep_raw_impact_and_order():
    y = np.interp(np.arange(180), [0,25,60,75,95,179], [400,400,200,410,160,160])
    params = replace(PhaseParameters(), top_offset_sec=2/30, address_offset_sec=-.1)
    old = populate(SwingPhaseDetector, y, 30, [], params=PhaseParameters())
    new = populate(SwingPhaseDetector, y, 30, [], params=params)
    assert new.phase_boundaries['임팩트'][0] == old.phase_boundaries['임팩트'][0]
    assert new.phase_boundaries['백스윙 톱'][0] == old.phase_boundaries['백스윙 톱'][0]+2
    ranges = list(new.phase_boundaries.values())
    assert all(lo <= hi for lo, hi in ranges)
    assert all(a[1] < b[0] for a, b in zip(ranges, ranges[1:]))


def test_finish_hold_respects_cut_and_falls_back_without_hold():
    y = np.interp(np.arange(180), [0,25,60,75,95,140,179], [400,400,200,410,160,160,300])
    params = replace(PhaseParameters(), finish_mode='settled_end')
    det = populate(SwingPhaseDetector, y, 30, [130], params=params)
    assert det.phase_boundaries
    assert det.phase_boundaries['피니시'][1] < 130
    assert det.phase_boundaries['피니시'][0] >= 95
    fallback = populate(SwingPhaseDetector, y, 30, [], params=replace(params, finish_hold_sec=10))
    baseline = populate(SwingPhaseDetector, y, 30, [], params=PhaseParameters())
    assert fallback.phase_boundaries == baseline.phase_boundaries


@pytest.mark.parametrize('kwargs', [{'smooth_sec':0}, {'plateau_ratio':float('nan')},
                                   {'onset_fraction':1}, {'finish_mode':'unknown'}])
def test_invalid_parameters_rejected(kwargs):
    with pytest.raises(ValueError):
        PhaseParameters(**kwargs)
