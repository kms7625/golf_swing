import numpy as np

PHASES = ["어드레스", "백스윙", "백스윙 톱", "다운스윙", "임팩트", "팔로우스루", "피니시"]

class SwingPhaseDetector:
    """
    손목 y좌표 시계열 분석으로 7단계 자동 세그먼테이션
    핵심 원리:
    - 어드레스: 초반 안정 구간 (손목 움직임 최소)
    - 백스윙 톱: 손목 속도 부호 변화 (음→양) = 위로 올라가다 내려오기 시작하는 지점
    - 임팩트: 다운스윙 최대 속도 + 어드레스 높이 복귀 융합
    - local_to_hist: local_idx → 히스토리 인덱스 매핑 (비가시 프레임 인덱스 불일치 방지)
    """
    def __init__(self):
        self.wrist_y_history  = []
        self.frame_phases     = []
        self.phase_boundaries = {}
        self.local_to_hist    = {}   # local_idx → history index 매핑

    def update(self, frame_idx, left_wrist_y, right_wrist_y,
               hip_center_x=None, shoulder_rot=None, wrist_x=None):
        self.local_to_hist[frame_idx] = len(self.wrist_y_history)  # 인덱스 매핑 저장
        self.wrist_y_history.append((left_wrist_y + right_wrist_y) / 2)
        if not hasattr(self, "hip_x_history"):
            self.hip_x_history      = []
            self.shoulder_rot_hist  = []
            self.wrist_x_history    = []
        self.hip_x_history.append(hip_center_x if hip_center_x is not None else 0.0)
        self.shoulder_rot_hist.append(shoulder_rot if shoulder_rot is not None else 0.0)
        self.wrist_x_history.append(wrist_x if wrist_x is not None else 0.0)

    def _smooth(self, arr, k=5):
        """경계 인식 이동평균 (np.convolve mode='same'은 경계에서 0-패딩으로 값이 왜곡됨)"""
        arr = np.array(arr, dtype=float)
        n = len(arr)
        if n < 3 or k < 2:
            return arr.copy()
        k = min(k, n)
        half = k // 2
        result = np.empty(n)
        for i in range(n):
            lo = max(0, i - half)
            hi = min(n, i + half + 1)
            result[i] = np.mean(arr[lo:hi])
        return result

    def detect_all_phases(self):
        """
        손목 y 위치 기반 7단계 경계 확정
        ────────────────────────────────────────────────────────────
        addr_end   : 초기 위치에서 y_range 10% 이상 상승 = 백스윙 시작
        top_idx    : addr_end ~ 75% 범위 y 최솟값 = 백스윙 톱
        impact_idx : 톱 이후 어드레스 높이(5% 허용) 첫 복귀 = 임팩트
        follow_idx : 임팩트 이후 두 번째 y 최솟값 = 팔로우스루 정점
        """
        wy = np.array(self.wrist_y_history, dtype=float)
        n  = len(wy)
        if n < 8:
            self.frame_phases = ["어드레스"] * n
            return {}

        wy_s = self._smooth(wy, k=5)
        wy_v = self._smooth(np.gradient(wy_s), k=3)

        # y_range는 raw 값 기준 (smoothing 경계 왜곡 방지)
        y_range   = wy.max() - wy.min() + 1e-8

        # ── 1. 어드레스 끝: raw 초기 위치에서 10% 이상 상승 ───────────
        head      = max(3, int(n * 0.05))
        y_initial = float(np.mean(wy[:head]))        # raw 기준
        addr_end  = head
        for i in range(head, int(n * 0.75)):
            if y_initial - wy_s[i] > y_range * 0.10:   # 픽셀 y 감소 = 손목 상승
                addr_end = max(2, i - 1)
                break
        addr_end = min(addr_end, int(n * 0.70))

        # ── 2. 백스윙 톱: 속도 부호 변환(음→양) 우선, 폴백은 전반부 argmin ─
        # 팔로우스루 종료가 백스윙 톱보다 높은 경우 argmin 전체 탐색은 오탐
        s        = addr_end + 1
        min_rise = y_range * 0.20   # 어드레스 대비 최소 20% 상승해야 톱으로 인정
        min_dv   = y_range * 0.01   # 다운스윙 시작 최소 속도 (노이즈 제거)

        top_idx = None
        for i in range(s + 2, min(n - 2, int(n * 0.92))):
            prev_vel = float(np.mean(wy_v[max(s, i - 2):i]))
            next_vel = float(np.mean(wy_v[i:min(n, i + 5)]))
            # 직전이 음(상승), 직후가 양(하강) + 어드레스 대비 충분히 올라간 경우
            if prev_vel < 0 and next_vel > min_dv:
                if wy_s[addr_end] - wy_s[i] > min_rise:
                    top_idx = i
                    break

        if top_idx is None:
            # 폴백: addr_end 이후 70% 이내에서만 argmin (팔로우스루 오탐 방지)
            e_half  = min(n - 2, addr_end + max(5, int((n - addr_end) * 0.70)))
            top_idx = s + int(np.argmin(wy_s[s:e_half]))
            top_idx = max(s, min(top_idx, e_half))

        top_width = max(1, int(n * 0.03))

        # ── 3. 임팩트: 백스윙 톱 이후 wy 최댓값 = 손목 최저점 = 실제 임팩트 ──
        # 근거: 다운스윙에서 손목이 가장 낮이 내려오는 순간이 임팩트.
        # - 어드레스 높이 복귀 방식: 프로 영상처럼 임팩트 wy < 어드레스 wy이면 오탐
        # - 속도 피크 방식: 빠른 가속 구간(임팩트 직전)을 잡아 0.1s 오차 발생
        # - argmax(wy) 방식: 두 케이스 모두 올바르게 작동 (범용)
        y_addr  = float(np.mean(wy[:max(3, head)]))  # 진단용으로만 사용

        # top_idx+1 부터 이후 70% 구간에서 wy 최댓값 탐색
        imp_end = min(n - 2, top_idx + max(3, int((n - top_idx) * 0.70)))
        if imp_end > top_idx + 1:
            impact_idx = (top_idx + 1) + int(np.argmax(wy[top_idx + 1:imp_end]))
        else:
            impact_idx = top_idx + 2

        impact_idx   = max(top_idx + 2, min(impact_idx, n - 3))
        impact_width = max(1, int(n * 0.02))

        # ── 4. 팔로우스루 정점 ─────────────────────────────────────────
        fol_start  = impact_idx + impact_width + 1
        fol_end    = min(n - 1, fol_start + max(3, (n - fol_start) * 3 // 4))
        if fol_end > fol_start:
            follow_idx = fol_start + int(np.argmin(wy_s[fol_start:fol_end]))
        else:
            follow_idx = min(fol_start + max(2, int(n * 0.08)), n - 2)
        follow_idx = max(fol_start, follow_idx)

        # ── 5. 경계 딕셔너리 ───────────────────────────────────────────
        self.phase_boundaries = {
            "어드레스":   (0,                           addr_end),
            "백스윙":     (addr_end,                   top_idx),
            "백스윙 톱":  (top_idx,                    top_idx + top_width),
            "다운스윙":   (top_idx + top_width,        impact_idx),
            "임팩트":     (impact_idx,                 impact_idx + impact_width),
            "팔로우스루": (impact_idx + impact_width,  follow_idx),
            "피니시":     (follow_idx,                 n - 1),
        }

        # ── 6. frame_phases 배열 채우기 ────────────────────────────────
        self.frame_phases = ["피니시"] * n
        for ph in reversed(["어드레스", "백스윙", "백스윙 톱",
                             "다운스윙", "임팩트", "팔로우스루", "피니시"]):
            lo, hi = self.phase_boundaries[ph]
            for i in range(max(0, lo), min(n, hi + 1)):
                self.frame_phases[i] = ph

        return self.phase_boundaries

    def get_phase_for_frame(self, local_idx):
        """local_to_hist 매핑으로 정확한 히스토리 인덱스 조회 (비가시 프레임 불일치 방지)"""
        if not self.frame_phases:
            return "어드레스"
        if self.local_to_hist:
            if local_idx in self.local_to_hist:
                hist_idx = self.local_to_hist[local_idx]
            else:
                keys        = np.array(list(self.local_to_hist.keys()))
                nearest_key = keys[np.argmin(np.abs(keys - local_idx))]
                hist_idx    = self.local_to_hist[nearest_key]
        else:
            hist_idx = local_idx
        hist_idx = max(0, min(hist_idx, len(self.frame_phases) - 1))
        return self.frame_phases[hist_idx]
