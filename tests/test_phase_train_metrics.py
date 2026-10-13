"""Independent examples for GolfDB coordinates and rejection denominators."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/phase_train'))
from common import ground_truth, measure, summary


def row():
    return dict(id=42, split=1, view='face-on',
                events=[100, 110, 118, 125, 133, 137, 140, 155, 170, 180])


def test_original_offset_and_existing_tolerance():
    gt, tolerance = ground_truth(row())
    assert gt == dict(Address=10, Top=33, Impact=40, Finish=70)
    assert tolerance == 1
    assert measure(row(), dict(Address=11, Top=35, Impact=39, Finish=70))['correct'] == {
        'Address':True, 'Top':False, 'Impact':True, 'Finish':True}


def test_rejected_clips_are_in_all_pce_and_within5_denominators():
    gt, _ = ground_truth(row())
    accepted = measure(row(), gt)
    rejected = measure(row(), {})
    result = summary([accepted, rejected])['all']
    assert result['n'] == 2 and result['rejected'] == 1
    assert result['mean_pce'] == pytest.approx(.5)
    assert all(v['pce'] == .5 and v['within5'] == .5 and v['median_abs_error'] == 0
               and v['predicted'] == 1 for v in result['events'].values())
