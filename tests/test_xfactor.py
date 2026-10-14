"""Rotation contracts use known geometry, not asserted pose-estimation accuracy."""
import copy
from types import SimpleNamespace

import numpy as np
import pytest

from analyzer.geometry import calc_world_rotation_headings
from analyzer.rotation import apply_world_rotations, rotation_summary
from analyzer.scoring import compute_summary, compute_score


def landmarks(shoulder, hip, camera=0):
    lms = [SimpleNamespace(x=0., y=0., z=0., visibility=.99) for _ in range(33)]
    for left, right, angle in ((11, 12, shoulder), (23, 24, hip)):
        r = np.radians(angle + camera)
        lms[left].x, lms[left].z = -.2*np.cos(r), .2*np.sin(r)
        lms[right].x, lms[right].z = .2*np.cos(r), -.2*np.sin(r)
        lms[left].y = lms[right].y = -.5 if left == 11 else 0.
    return lms


def frames(shoulder=90, hip=40, camera=0, sign=1):
    result = []
    # Hold at the top long enough for the trailing 5-frame mean to settle.
    for i, t in enumerate([0]*5 + [1]*5 + [1]):
        headings, reason = calc_world_rotation_headings(landmarks(sign*shoulder*t, sign*hip*t, camera))
        result.append(dict(frame=i, local_idx=i, time=i/30, phase="어드레스" if i<5 else "백스윙" if i<10 else "백스윙 톱",
                           world_rotation_headings=headings, world_rotation_reason=reason,
                           spine_angle=5., shoulder_rotation=10., hip_rotation=30.,
                           left_knee=160., right_knee=160., left_elbow=170., right_elbow=170.))
    return result


@pytest.mark.parametrize("camera", [0, 90, 170, -90])
@pytest.mark.parametrize("sign", [1, -1])
def test_camera_yaw_and_handedness_preserve_top_separation(camera, sign):
    fd = apply_world_rotations(frames(camera=camera, sign=sign), 10)
    s = compute_summary(fd)
    assert s["x_factor"] == 50
    assert s["x_factor_method"] == "world_3d_top"
    assert fd[-1]["shoulder_rotation_3d_signed"] == sign*90
    assert fd[-1]["shoulder_rotation"] == 90
    assert fd[0]["shoulder_rotation"] == 0
    assert s["x_factor_2d"] == -20


def test_unwrap_crosses_180_without_discontinuity():
    fd = frames()
    fd = fd[:1] + [dict(fd[-1], frame=i+1, time=(i+1)/30,
                       world_rotation_headings=[a, h])
                   for i, (a, h) in enumerate([(90, 45), (170, 85), (-170, 95), (-100, 130)])]
    apply_world_rotations(fd, 2)
    assert [f["shoulder_rotation_3d_signed"] for f in fd] == [0, 90, 170, 190, 260]


def test_same_time_difference_and_finish_do_not_supply_peak():
    fd = frames()
    fd.append(dict(fd[-1], frame=11, time=11/30, phase="피니시", world_rotation_headings=[160, -100]))
    s = compute_summary(apply_world_rotations(fd, 10))
    assert s["x_factor"] == 50
    assert s["x_factor_frame"] == 10
    assert s["shoulder_rotation_max"] == 90


def test_negative_separation_is_not_absolute_or_clipped():
    s = compute_summary(apply_world_rotations(frames(shoulder=30, hip=70), 10))
    assert s["x_factor"] == -40


@pytest.mark.parametrize("failure", ["missing_world", "low_world_visibility", "nonfinite_world", "degenerate_projection"])
def test_geometry_rejects_invalid_world_pairs(failure):
    lms = landmarks(90, 40)
    if failure == "missing_world":
        lms = None
    elif failure == "low_world_visibility":
        lms[23].visibility = .5
    elif failure == "nonfinite_world":
        lms[12].z = float("nan")
    else:
        lms[12].x, lms[12].z = lms[11].x, lms[11].z
    assert calc_world_rotation_headings(lms) == (None, failure)


def test_missing_address_does_not_use_a_late_backswing_reference():
    fd = frames()
    for f in fd[:5]:
        f["world_rotation_headings"] = None
    s = compute_summary(apply_world_rotations(fd, 10))
    assert s["x_factor"] == -20
    assert s["x_factor_3d"] is None
    assert s["x_factor_fallback_reason"] == "missing_address_world"


def test_invalid_exact_top_falls_back_and_does_not_choose_a_better_neighbor():
    fd = frames()
    fd[-1].update(world_rotation_headings=None, world_rotation_reason="interpolated_2d")
    s = compute_summary(apply_world_rotations(fd, 10))
    assert s["x_factor"] == -20
    assert s["x_factor_method"] == "legacy_2d"
    assert s["x_factor_fallback_reason"] == "interpolated_2d"
    assert s["phase_stats"]["백스윙 톱"]["shoulder_rot"] == 10


def test_missing_top_row_is_explicit():
    s = compute_summary(apply_world_rotations(frames(), 1234))
    assert s["x_factor_method"] == "legacy_2d"
    assert s["x_factor_fallback_reason"] == "missing_top_frame"


def test_fallback_does_not_blend_methods_in_smoothing_or_phase_stats():
    fd = frames()
    fd[7].update(world_rotation_headings=None, world_rotation_reason="low_world_visibility")
    apply_world_rotations(fd, 10)
    assert fd[7]["shoulder_rotation"] == 10
    assert fd[7]["shoulder_rotation_3d"] is None
    assert fd[8]["shoulder_rotation_3d"] == 90
    # Valid 3D values are 18, 36, 90, 90; the held 2D value 10 is excluded.
    assert compute_summary(fd)["phase_stats"]["백스윙"]["shoulder_rot"] == 58.5


def test_explicit_legacy_mode_and_old_live_payload_preserve_scores():
    fd = frames()
    old = compute_summary(fd)
    score = compute_score(old, {})
    legacy = compute_summary(apply_world_rotations(copy.deepcopy(fd), 10, "legacy_2d"))
    for k, v in old.items():
        assert legacy[k] == v
    assert compute_score(legacy, {}) == score
    assert rotation_summary(fd) == {}


def test_mode_validation():
    with pytest.raises(ValueError):
        apply_world_rotations(frames(), 10, "unknown")


def test_pose_half_turn_flip_cannot_add_an_extra_revolution():
    fd = frames()
    fd[6]["world_rotation_headings"] = [-90, -140]
    apply_world_rotations(fd, 10)
    assert fd[6]["shoulder_rotation_3d"] is None
    assert fd[6]["rotation_fallback_reason"] == "world_heading_jump"
    assert fd[7]["shoulder_rotation_3d_signed"] == 90
    assert compute_summary(fd)["x_factor"] == 50
