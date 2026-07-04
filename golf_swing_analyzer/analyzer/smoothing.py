import numpy as np
from collections import deque


class MovingAverageFilter:
    """슬라이드 8: 이동 평균 필터로 흔들림 보정"""
    def __init__(self, window=5):
        self.window = window
        self.buffers = {}

    def smooth(self, key, value):
        if key not in self.buffers:
            self.buffers[key] = deque(maxlen=self.window)
        self.buffers[key].append(value)
        return round(float(np.mean(self.buffers[key])), 1)

    def interpolate(self, key, prev_value):
        """슬라이드 8: 신뢰도 하락 시 이전 프레임 기반 선형 보간"""
        if key not in self.buffers or len(self.buffers[key]) == 0:
            return prev_value
        return round(float(np.mean(list(self.buffers[key])[-3:])), 1)
