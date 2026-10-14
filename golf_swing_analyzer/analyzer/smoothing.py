import numpy as np
from collections import deque


class MovingAverageFilter:
    """슬라이드 8: 이동 평균 필터로 흔들림 보정"""
    def __init__(self, window=5, window_sec=None):
        if window_sec is not None and (not np.isfinite(window_sec) or window_sec <= 0):
            raise ValueError('Smoothing duration must be finite and positive')
        self.window = window
        self.window_sec = window_sec
        self.buffers = {}

    def smooth(self, key, value, time_sec=None):
        if key not in self.buffers:
            self.buffers[key] = deque(maxlen=self.window if self.window_sec is None else None)
        buffer = self.buffers[key]
        if self.window_sec is None:
            buffer.append(value)
            values = buffer
        else:
            if time_sec is None or not np.isfinite(time_sec):
                raise ValueError('Time-based smoothing requires a finite timestamp')
            if buffer and time_sec < buffer[-1][0]:
                raise ValueError('Smoothing timestamps must be monotonic')
            buffer.append((time_sec, value))
            while buffer and time_sec-buffer[0][0] > self.window_sec+1e-9:
                buffer.popleft()
            values = [v for _, v in buffer]
        return round(float(np.mean(values)), 1)

    def interpolate(self, key, prev_value):
        """슬라이드 8: 신뢰도 하락 시 이전 프레임 기반 선형 보간"""
        if key not in self.buffers or len(self.buffers[key]) == 0:
            return prev_value
        values = list(self.buffers[key])[-3:]
        if self.window_sec is not None:
            values = [v for _, v in values]
        return round(float(np.mean(values)), 1)
