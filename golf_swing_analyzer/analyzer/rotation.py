"""Address-relative horizontal rotations; phase detection is a read-only input."""
import numpy as np


def apply_world_rotations(frames, top_frame, method="world_3d"):
    """Keep legacy values and select paired 3D rotations after cycle selection.

    Unwrap the valid directed headings before subtraction/smoothing. Missing
    observations remain missing; unwrap assumes <180° between valid estimates.
    A shared sign makes the shoulder's backswing positive, preserving negative
    separation when the pelvis actually turns farther than the shoulders.
    """
    if method not in ("world_3d", "legacy_2d"):
        raise ValueError("rotation_method must be world_3d or legacy_2d")
    good = []
    rejected = set()
    previous = None
    for i, f in enumerate(frames):
        heading = f.get("world_rotation_headings")
        if heading is None:
            continue
        heading = np.asarray(heading)
        step = (heading - previous + 180) % 360 - 180 if previous is not None else np.zeros(2)
        # A near-half-turn between accepted observations is ambiguous (common
        # left/right pose flips). Reject both segments, retaining the last good
        # orientation so one bad frame cannot add a persistent full revolution.
        # 120° is a conservative reliability guard, not a scoring threshold.
        if np.any(np.abs(step) >= 120):
            rejected.add(i)
            continue
        good.append(i)
        previous = heading
    address = [i for i in good if frames[i].get("phase") == "어드레스"]
    reference = address[0] if address else None
    angles = {}
    sign = 1
    if reference is not None:
        continuous = np.degrees(np.unwrap(np.radians(
            [frames[i]["world_rotation_headings"] for i in good]), axis=0))
        continuous -= continuous[good.index(reference)].copy()
        angles = dict(zip(good, continuous))
        top = [angles[i][0] for i in good if frames[i]["frame"] == top_frame]
        backswing = [angles[i][0] for i in good if frames[i].get("phase") == "백스윙"]
        direction = top[0] if top else (np.median(backswing) if backswing else 0)
        sign = -1 if direction < 0 else 1
    buffer = []
    previous_time = None
    for i, f in enumerate(frames):
        for key in ("shoulder_rotation", "hip_rotation"):
            f.setdefault(key + "_2d", f[key])
            f[key + "_3d"] = None
            f[key + "_3d_signed"] = None
        f["rotation_at_top"] = f["frame"] == top_frame
        f["rotation_reference_frame"] = frames[reference]["frame"] if reference is not None else None
        f["rotation_sign"] = sign
        f["rotation_gap_sec"] = None
        if i in angles:
            gap = f["time"] - previous_time if previous_time is not None else 0
            if gap > .2:
                buffer = []
            f["rotation_gap_sec"] = round(gap, 4)
            buffer.append(angles[i] * sign)
            buffer = buffer[-5:]
            smoothed = np.mean(buffer, axis=0)
            for j, key in enumerate(("shoulder_rotation", "hip_rotation")):
                f[key + "_3d_signed"] = round(float(angles[i][j]), 1)
                f[key + "_3d"] = round(float(smoothed[j]), 1)
            previous_time = f["time"]
        else:
            buffer = []  # Never blend 2D fallback into a 3D smoothing window.
        reason = f.get("world_rotation_reason")
        if i in rejected:
            reason = "world_heading_jump"
        if reference is None:
            reason = "missing_address_world"
        elif i not in angles:
            reason = reason or "missing_world"
        f["rotation_method"] = "world_3d" if method == "world_3d" and i in angles else "legacy_2d"
        f["rotation_fallback_reason"] = reason if method == "world_3d" else "requested_legacy"
        for key in ("shoulder_rotation", "hip_rotation"):
            f[key] = f[key + ("_3d" if f["rotation_method"] == "world_3d" else "_2d")]
    return frames


def rotation_summary(frames):
    """Same-time top separation, with an explicit whole-metric legacy fallback.

    Old/live payloads lack the new fields and keep their historical semantics.
    Shoulder maxima for scoring use address→top in 3D, never finish overshoot.
    """
    if not any("rotation_method" in f for f in frames):
        return {}
    legacy_sh = [f["shoulder_rotation_2d"] for f in frames]
    legacy_hp = [f["hip_rotation_2d"] for f in frames]
    legacy_x = round(max(legacy_sh) - max(legacy_hp), 1)
    top = next((f for f in frames if f.get("rotation_at_top")), None)
    usable_top = top is not None and top.get("rotation_method") == "world_3d"
    world_top = top is not None and top.get("shoulder_rotation_3d") is not None
    world = [f for f in frames if f.get("shoulder_rotation_3d") is not None]
    backswing = [f for f in world if f.get("phase") in ("어드레스", "백스윙", "백스윙 톱")]
    xf_top = round(top["shoulder_rotation_3d"] - top["hip_rotation_3d"], 1) if world_top else None
    separation = [f for f in world if f.get("phase") in ("백스윙 톱", "다운스윙")]
    peak = max(separation, key=lambda f: f["shoulder_rotation_3d"] - f["hip_rotation_3d"], default=None)
    result = {
        "x_factor": xf_top if usable_top else legacy_x,
        "x_factor_2d": legacy_x,
        "x_factor_3d": xf_top,
        "x_factor_method": "world_3d_top" if usable_top else "legacy_2d",
        "x_factor_frame": top["frame"] if usable_top else None,
        "x_factor_fallback_reason": None if usable_top else (
            top.get("rotation_fallback_reason") or "invalid_top_world" if top else "missing_top_frame"),
        "rotation_world_valid_ratio": round(len(world) / len(frames), 4),
        "rotation_fallback_frames": sum(f["rotation_method"] != "world_3d" for f in frames),
        "x_factor_3d_max_separation": round(peak["shoulder_rotation_3d"] - peak["hip_rotation_3d"], 1) if peak else None,
        "x_factor_3d_max_frame": peak["frame"] if peak else None,
    }
    # A summary never mixes legacy slopes with signed 3D angles in an aggregate.
    for key in ("shoulder_rotation", "hip_rotation"):
        legacy = [f[key + "_2d"] for f in frames]
        vals = [f[key + "_3d"] for f in world] if usable_top else legacy
        max_vals = [f[key + "_3d"] for f in backswing] if usable_top else legacy
        result[key + "_avg"] = round(float(np.mean(vals)), 1)
        result[key + "_max"] = round(float(max(max_vals)), 1)
        result[key + "_max_2d"] = max(legacy)
    return result
