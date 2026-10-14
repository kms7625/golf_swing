import numpy as np
from .phase_parameters import CALIBRATED_PARAMETERS

PHASES = ["어드레스", "백스윙", "백스윙 톱", "다운스윙", "임팩트", "팔로우스루", "피니시"]
NO_SWING_MESSAGE = "스윙 동작을 찾지 못했어요. 구간을 다시 선택해 주세요."


class SwingNotFoundError(ValueError):
    def __init__(self):
        super().__init__(NO_SWING_MESSAGE)


class SwingPhaseDetector:
    """One wrist rise/descent cycle, on the source clock (pixel Y increases down).

    local_to_hist continues to map pose-only local_idx to history; source frame IDs
    and seconds are separate coordinates, never substitutes for that mapping.
    """
    def __init__(self, fps=30.0, params=None):
        self.fps = fps
        self.params = CALIBRATED_PARAMETERS if params is None else params
        self.wrist_y_history = []
        self.frame_phases = []
        self.phase_boundaries = {}
        self.phase_boundaries_frames = {}
        self.phase_boundaries_sec = {}
        self.local_to_hist = {}
        self.source_frames = []
        self.wrist_times_sec = []
        self.body_scales = []
        self.cut_frames = []
        self.hip_x_history = []
        self.shoulder_rot_hist = []
        self.wrist_x_history = []
        self.metric_available_history = []

    def update(self, frame_idx, left_wrist_y, right_wrist_y,
               hip_center_x=None, shoulder_rot=None, wrist_x=None,
               source_frame=None, time_sec=None, body_scale=None):
        if frame_idx is not None:
            self.local_to_hist[frame_idx] = len(self.wrist_y_history)
        self.wrist_y_history.append((left_wrist_y + right_wrist_y) / 2)
        source = len(self.source_frames) if source_frame is None else source_frame
        self.source_frames.append(source)
        self.wrist_times_sec.append(source / self.fps if time_sec is None else time_sec)
        # Legacy live callers lack image dimensions; a conservative pixel scale.
        self.body_scales.append(body_scale if body_scale is not None else 100.0)
        self.hip_x_history.append(hip_center_x or 0.0)
        self.shoulder_rot_hist.append(shoulder_rot or 0.0)
        self.wrist_x_history.append(wrist_x or 0.0)

    def _smooth(self, arr, k=5):
        """Edge-aware mean; never pad with zero (A4)."""
        arr = np.asarray(arr, dtype=float)
        half = min(k, len(arr)) // 2
        return np.array([np.mean(arr[max(0, i-half):min(len(arr), i+half+1)])
                         for i in range(len(arr))])

    def _segments(self):
        """Interpolate only bracketed gaps <=0.2 s, never across a cut."""
        wy = np.asarray(self.wrist_y_history, dtype=float).copy()
        ts = np.asarray(self.wrist_times_sec)
        cuts = np.searchsorted(self.source_frames, self.cut_frames)
        edges = sorted(set([0, len(wy), *cuts.tolist()]))
        segments = []
        for lo, hi in zip(edges, edges[1:]):
            good = np.flatnonzero(np.isfinite(wy[lo:hi])) + lo
            for a, b in zip(good, good[1:]):
                missing_duration = ts[b] - ts[a] - 1 / self.fps
                if b > a + 1 and missing_duration <= .2 + 1e-6:
                    wy[a+1:b] = np.interp(ts[a+1:b], [ts[a], ts[b]], [wy[a], wy[b]])
            start = None
            for i in range(lo, hi):
                if np.isfinite(wy[i]):
                    if start is None: start = i
                elif start is not None:
                    segments.append((start, i)); start = None
            if start is not None: segments.append((start, hi))
        return wy, segments

    def candidates(self):
        p = self.params
        wy, segments = self._segments()
        ts = np.asarray(self.wrist_times_sec)
        candidates = []
        for lo, hi in segments:
            if hi-lo < 8: continue
            dt = float(np.median(np.diff(ts[lo:hi])))
            # ~0.10 s positional smoothing, odd width, independent of clip length.
            k = max(1, round(p.smooth_sec / dt)) | 1
            sm = self._smooth(wy[lo:hi], k)
            radius = max(1, round(.12 / dt))
            scale = max(float(np.median(self.body_scales[lo:hi])), 1e-6)
            # 15% of projected torso length rejects pose jitter while admitting
            # short chips; unlike shoulder width this remains usable in DTL views.
            min_amp = .15 * scale
            for t in range(lo+2, hi-4):
                j = t-lo
                if sm[j] > np.min(sm[max(0,j-radius):min(len(sm),j+radius+1)]): continue
                # Flat top (hands pause): use the last frame before the descent.
                # Measuring from the plateau's first frame can push impact past
                # the 1.25 s window (pexels_8065880 on Mac, 2026-10-12).
                base = sm[j]
                while t+1 < hi-4 and sm[t+1-lo] <= base + p.plateau_ratio*scale:
                    t += 1
                j = t-lo
                before = max(lo, int(np.searchsorted(ts, ts[t]-p.address_window_sec)))
                # Choi 2014, REPORT L4: downswing ~0.3 s. A 1.25 s ceiling
                # tolerates slow media, without reaching the next swing or a cut.
                end = min(hi-2, int(np.searchsorted(ts, ts[t]+p.impact_window_sec, side='right')))
                if end <= t+2 or before >= t-1: continue
                impact = t+1+int(np.argmax(wy[t+1:end]))  # A2: raw Y argmax
                amplitude = wy[impact]-sm[j]
                addr_peak = before+int(np.argmax(sm[before-lo:j]))
                # Use the most recent sufficiently high local peak. An older
                # address must not join a backswing to its follow-through apex.
                for q in range(t-2, before, -1):
                    if (sm[q-lo]-sm[j] >= min_amp and
                        sm[q-lo] >= np.max(sm[max(0,q-lo-radius):min(len(sm),q-lo+radius+1)])):
                        addr_peak = q
                        break
                rise = sm[addr_peak-lo]-sm[j]
                if min(amplitude, rise) < min_amp or impact <= t+2: continue
                # A real descent must turn upwards into follow-through, rather
                # than joining two unrelated troughs/return-to-rest movements.
                finish_end = min(hi-1, int(np.searchsorted(ts, ts[impact]+p.finish_window_sec, side='right'))-1)
                if finish_end <= impact+2: continue
                follow = impact+1+int(np.argmin(sm[impact+1-lo:finish_end+1-lo]))
                if wy[impact]-sm[follow-lo] < min_amp * .5: continue
                # Onset: last sustained address level before the rise, not the
                # initial value of an arbitrarily padded video.
                threshold = sm[addr_peak-lo] - rise*p.onset_fraction
                onset = addr_peak
                for q in range(addr_peak+1, t):
                    if sm[q-lo] < threshold:
                        onset = q; break
                start = max(before, int(np.searchsorted(ts, ts[onset]-.5)))
                if not start < onset < t: continue
                # Amplitude plus descent speed prioritizes a committed shot over
                # a slow rehearsal; wrist-only evidence cannot prove ball contact.
                duration = max(ts[impact]-ts[t], dt)
                if duration > max(.5, 1.5*(ts[t]-ts[onset])):
                    continue  # slow return from a finish is not a downswing
                strength = amplitude * (1 + .05 * min(1/duration, 3.0))
                candidates.append(dict(start=start, onset=onset, top=t, impact=impact,
                                       follow=follow, end=finish_end, strength=strength,
                                       segment=(lo,hi), amplitude=amplitude/scale))
        return candidates

    def _event_boundaries(self, chosen):
        """Apply event definitions after ranking; preserve the raw impact argmax.

        A stationary wrist is only a Finish proxy: it cannot observe club release.
        No qualifying hold falls back to the existing follow-through minimum.
        """
        p = self.params
        start, onset, top, impact, follow, end = [chosen[k] for k in
                                               ('start','onset','top','impact','follow','end')]
        ts = np.asarray(self.wrist_times_sec)
        if p.top_offset_sec:
            top = min(impact-3, max(onset+1, int(np.searchsorted(ts, ts[top]+p.top_offset_sec))))
        if p.address_offset_sec:
            shifted = min(top-1, max(start+1, int(np.searchsorted(ts, ts[onset]+p.address_offset_sec))))
            # Advancing Address must not leave an undersupported scoring hold.
            # Count the unchanged visibility/fallback rows, never their angles.
            available = self.metric_available_history
            dt = float(np.median(np.diff(ts[chosen['segment'][0]:chosen['segment'][1]])))
            supported = (sum(available[start:shifted])*dt if available else float('inf'))
            restored = sum(available[start:onset])*dt
            recoverable = supported + 1e-9 < p.address_min_valid_sec <= restored + 1e-9
            if p.address_offset_sec > 0 or not recoverable:
                onset = shifted
        if p.finish_mode != 'minimum':
            wy, _ = self._segments()
            lo, hi = chosen['segment']
            dt = float(np.median(np.diff(ts[lo:hi])))
            sm = self._smooth(wy[lo:hi], max(1, round(p.smooth_sec/dt)) | 1)
            scale = max(float(np.median(self.body_scales[lo:hi])), 1e-6)
            speed = np.abs(np.gradient(sm, ts[lo:hi])) / scale
            for q in range(follow, end+1):
                stop = int(np.searchsorted(ts, ts[q]+p.finish_hold_sec))
                if stop > end or stop <= q:
                    continue
                if np.all(speed[q-lo:stop+1-lo] <= p.finish_speed_ratio):
                    follow = q
                    if p.finish_mode == 'settled_end':
                        while stop < end and speed[stop+1-lo] <= p.finish_speed_ratio:
                            stop += 1
                        follow = stop
                    break
        return start, onset, top, impact, follow, end

    def detect_all_phases(self):
        self.phase_boundaries = {}
        self.phase_boundaries_frames = {}
        self.phase_boundaries_sec = {}
        self.frame_phases = ["준비"] * len(self.wrist_y_history)
        candidates = self.candidates()
        if not candidates: return {}
        peak = max(c['strength'] for c in candidates)
        # Near-equal replay cycles should not displace the first complete swing
        # on a few pixels of pose jitter (5% tie tolerance, not GolfDB-tuned).
        chosen = min((c for c in candidates if c['strength'] >= peak*.95),
                     key=lambda c: (c['top'], -c['strength']))
        self.selected_cycle = chosen
        start, onset, top, impact, follow, end = self._event_boundaries(chosen)
        # Event phases own their starting frame; all ranges are inclusive and
        # disjoint. Fixed time widths cannot consume the entire downswing.
        ts = self.wrist_times_sec
        top_end = min(impact-2, max(top, int(np.searchsorted(ts, ts[top]+.05))-1))
        imp_end = min(end-2, max(impact, int(np.searchsorted(ts, ts[impact]+.05))-1))
        follow = min(end, max(imp_end+2, follow))
        bounds = [(start,onset-1), (onset,top-1), (top,top_end),
                  (top_end+1,impact-1), (impact,imp_end), (imp_end+1,follow-1), (follow,end)]
        if any(a>b for a,b in bounds): return {}
        for phase, (a,b) in zip(PHASES,bounds):
            self.phase_boundaries[phase] = (a,b)
            self.phase_boundaries_frames[phase] = (self.source_frames[a],self.source_frames[b])
            self.phase_boundaries_sec[phase] = (ts[a],ts[b])
            self.frame_phases[a:b+1] = [phase]*(b-a+1)
        return self.phase_boundaries

    def get_phase_for_frame(self, local_idx):
        """Keep A1's local→history lookup, including nearest-key fallback."""
        if not self.frame_phases: return "준비"
        if self.local_to_hist:
            if local_idx in self.local_to_hist:
                hist_idx = self.local_to_hist[local_idx]
            else:
                keys = np.array(list(self.local_to_hist))
                hist_idx = self.local_to_hist[keys[np.argmin(np.abs(keys-local_idx))]]
        else:
            hist_idx = local_idx
        return self.frame_phases[max(0,min(hist_idx,len(self.frame_phases)-1))]
