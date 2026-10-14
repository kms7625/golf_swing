"""Sparse visibility must not turn an Address correction into a tiny score hold."""
from dataclasses import replace

import numpy as np
import pytest

from analyzer.phase_detector import SwingPhaseDetector
from analyzer.phase_parameters import PhaseParameters


def detector(fps, params):
    times = np.arange(round(6*fps))/fps
    y = np.interp(times, [0, .8, 2, 2.4, 3.3, 6], [400, 400, 200, 410, 160, 160])
    det = SwingPhaseDetector(fps=fps, params=params)
    for i, value in enumerate(y):
        det.update(i, value, value, source_frame=100+2*i, time_sec=times[i], body_scale=200)
    det.detect_all_phases()
    return det


@pytest.mark.parametrize('fps', [15, 30, 60])
def test_sparse_address_uses_uncorrected_onset_without_moving_top_or_impact(fps):
    original = PhaseParameters()
    shifted = replace(original, address_offset_sec=-.2)
    plain = detector(fps, original)
    guarded = detector(fps, replace(shifted, address_min_valid_sec=.2))
    onset = guarded.phase_boundaries['백스윙'][0]
    # Only two observable rows survive the proposed early Address boundary.
    guarded.metric_available_history = [i >= onset-2 for i in range(len(guarded.wrist_times_sec))]
    guarded.detect_all_phases()
    assert guarded.phase_boundaries == plain.phase_boundaries
    assert guarded.local_to_hist == plain.local_to_hist
    assert guarded.phase_boundaries_frames['임팩트'] == plain.phase_boundaries_frames['임팩트']
    # With enough unchanged angle rows, retain the learned Address correction.
    guarded.metric_available_history = [True]*len(guarded.wrist_times_sec)
    guarded.detect_all_phases()
    assert guarded.phase_boundaries == detector(fps, shifted).phase_boundaries
    # A longer phase cannot repair a wholly unobservable Address interval.
    guarded.metric_available_history = [False]*len(guarded.wrist_times_sec)
    guarded.detect_all_phases()
    assert guarded.phase_boundaries == detector(fps, shifted).phase_boundaries


def test_missing_support_metadata_keeps_live_caller_compatibility():
    params = replace(PhaseParameters(), address_offset_sec=-.2)
    old = detector(30, params)
    new = detector(30, replace(params, address_min_valid_sec=.2))
    assert old.phase_boundaries == new.phase_boundaries
    with pytest.raises(ValueError):
        replace(params, address_min_valid_sec=-.1)
