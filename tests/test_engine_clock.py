"""Clock invariants with controlled observations, separate from pose accuracy."""
import numpy as np
import pytest

from analyzer.phase_detector import SwingPhaseDetector
from analyzer.smoothing import MovingAverageFilter
from analyzer.video_clock import ANGLE_SMOOTH_SEC, analysis_step
from analyzer.video_signal import SceneCuts


@pytest.mark.parametrize('duration', [4, 20, 20.1, 41])
def test_duplicate_60fps_uses_same_observation_clock_and_memory_bound(duration):
    clocks = []
    for fps in (30, 60):
        total = round(duration*fps)
        step = analysis_step(total, fps)
        clocks.append(np.arange(0, total, step)/fps)
        assert len(clocks[-1]) <= 600
    np.testing.assert_array_equal(*clocks)


def test_short_native_24_and_25fps_are_not_decimated():
    for fps in (24, 25, 29.97, 30):
        assert analysis_step(round(6*fps), fps) == 1
    with pytest.raises(ValueError):
        analysis_step(120, 0)


def test_temporal_angle_filter_matches_30fps_and_expires_a_visibility_gap():
    old = MovingAverageFilter(window=5)
    new = MovingAverageFilter(window_sec=ANGLE_SMOOTH_SEC)
    for i, value in enumerate([5, 7, 11, 20, 25, 40, 70, 80]):
        assert old.smooth('knee', value) == new.smooth('knee', value, i/30)
    assert new.smooth('knee', 160, 2.) == 160
    # The previous observations are outside the same temporal span at 24fps.
    new = MovingAverageFilter(window_sec=ANGLE_SMOOTH_SEC)
    for i, value in enumerate([0, 0, 0, 0, 100]):
        result = new.smooth('x', value, i/24)
    assert result == 25
    with pytest.raises(ValueError):
        new.smooth('x', 0, .1)


def test_cut_clock_is_unchanged_by_duplicate_frames():
    times = []
    for fps in (30, 60):
        detector = SceneCuts(fps)
        found = []
        for i in range(2*fps):
            # Continuous small brightness change followed by a genuine cut.
            value = i//(fps//30) % 10 if i < fps else 200
            if detector.update(np.full((64,64,3), value, np.uint8), i):
                found.append(i/fps)
        times.append(found)
    assert times == [[1.], [1.]]


def test_duplicate_source_ids_preserve_all_phase_times_and_local_mapping():
    times = np.arange(180)/30
    values = np.interp(times, [0,.8,2,2.4,3.3,6], [400,400,200,410,160,160])
    detectors = []
    for fps in (30,60):
        det = SwingPhaseDetector(fps=30)
        for local, (t, y) in enumerate(zip(times, values)):
            det.update(local, y, y, source_frame=round((t+10)*fps), time_sec=t, body_scale=200)
        det.detect_all_phases()
        detectors.append(det)
    assert detectors[0].phase_boundaries_sec == detectors[1].phase_boundaries_sec
    assert detectors[0].local_to_hist == detectors[1].local_to_hist
    for phase, pair in detectors[0].phase_boundaries_frames.items():
        assert detectors[1].phase_boundaries_frames[phase] == tuple(2*v for v in pair)
