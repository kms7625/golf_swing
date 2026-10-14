"""Analysis cadence and temporal spans, separate from source-frame IDs."""
import math

# Five adjacent 30fps observations span four intervals, including both ends.
# 29.97 accommodates the established NTSC test recording without dropping one.
ANGLE_SMOOTH_SEC = 4 / 29.97
ANALYSIS_HZ = 30.0
MAX_OBSERVATIONS = 600


def analysis_step(total_frames, fps):
    """Keep ~30 pose updates/s and the 600-preview memory cap.

    High-fps decimation is deliberate: a duplicated 60fps input must not give the
    stateful pose tracker twice as many updates. Steps remain multiples of the
    rate conversion so the long-clip cap uses the same clock at 30 and 60fps.
    sample_rate is an obsolete UI hint, not a source-clock frame interval.
    """
    if not math.isfinite(fps) or fps <= 0 or total_frames < 0:
        raise ValueError('Invalid video clock')
    cadence = max(1, round(fps / ANALYSIS_HZ))
    return cadence * max(1, math.ceil(total_frames / (MAX_OBSERVATIONS * cadence)))
