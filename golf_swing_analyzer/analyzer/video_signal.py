"""Shared source-clock signal extraction for scan and full analysis."""
from collections import deque

import cv2
import numpy as np


class SceneCuts:
    def __init__(self, fps):
        self.fps = fps
        self.history = deque()
        self.differences = deque(maxlen=15)
        self.last_cut = -float('inf')

    def update(self, frame, source_frame):
        small = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (64,36)).astype(float)
        cut = False
        if self.history:
            delta = np.abs(small-self.history[-1][1])
            # Broad image change, not the few pixels occupied by a fast club.
            cut = float(delta.mean()) > 20 and float(np.mean(delta > 25)) > .25
            # Same-camera edited replay: the background may not change at all.
            # Require a large abrupt jump relative to recent motion, with >8%
            # of pixels affected, to distinguish it from continuous club motion.
            mad = float(delta.mean())
            if self.differences:
                cut |= mad > max(8.0, 5*np.median(self.differences)) and float(np.mean(delta > 25)) > .08
            self.differences.append(mad)
            # Fades/dissolves can distribute a cut over several adjacent frames.
            lag = np.abs(small-self.history[0][1])
            cut |= float(lag.mean()) > 25 and float(np.mean(lag > 30)) > .4
        while self.history and (source_frame-self.history[0][0])/self.fps >= .2:
            self.history.popleft()
        self.history.append((source_frame,small))
        if cut and (source_frame-self.last_cut)/self.fps > .2:
            self.last_cut = source_frame
            self.history.clear()
            self.history.append((source_frame,small))
            return True
        return False


def wrist_signal(lms, width, height):
    """Use visible wrists even if a knee/hip fails the separate angle gate.

    A single visible wrist is preferable to averaging an occluded prediction.
    Torso length is less view-dependent than projected shoulder width in DTL.
    """
    # Visibility is an occlusion estimate, not coordinate accuracy. A permissive
    # 0.1 wrist gate retains fast/occluded wrists; motion/sequence checks follow.
    wrists = [lms[i] for i in (15,16) if lms[i].visibility > .1]
    y = float(np.mean([p.y*height for p in wrists])) if wrists else float('nan')
    x = float(np.mean([p.x*width for p in wrists])) if wrists else float('nan')
    shoulder = np.array([(lms[11].x+lms[12].x)*width/2,
                         (lms[11].y+lms[12].y)*height/2])
    hip = np.array([(lms[23].x+lms[24].x)*width/2,
                    (lms[23].y+lms[24].y)*height/2])
    return y, x, max(float(np.linalg.norm(shoulder-hip)), height*.1)
