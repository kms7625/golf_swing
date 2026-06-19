import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os
import json
import time
from datetime import datetime
from collections import deque
from google import genai
from google.genai import types

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI 골프 스윙 분석기",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Space+Grotesk:wght@400;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

  .stApp { background: linear-gradient(135deg, #0f1f17 0%, #1a3a2a 100%); color: #e8f5e9; }

  .hero-header {
    text-align: center; padding: 2.5rem 1rem 1.5rem;
    border-bottom: 1px solid #2d6a4f44; margin-bottom: 2rem;
  }
  .hero-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 2.8rem;
    font-weight: 700; color: #f4c430; letter-spacing: -0.5px; margin: 0;
  }
  .hero-sub { font-size: 1rem; color: #a5d6a7; margin-top: 0.5rem; font-weight: 300; }

  .metric-card {
    background: #1e3d2e; border: 1px solid #2d6a4f; border-radius: 12px;
    padding: 1.2rem 1rem; text-align: center; transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: #f4c430; }
  .metric-label { font-size: 0.75rem; color: #a5d6a7; font-weight: 500; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 0.3rem; }
  .metric-value { font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; color: #f4c430; line-height: 1; }
  .metric-unit { font-size: 0.8rem; color: #81c784; }
  .metric-status-good { color: #69f0ae !important; }
  .metric-status-warn { color: #ffcc02 !important; }
  .metric-status-bad  { color: #ff5252 !important; }

  .score-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 1.5rem; }
  .score-ring {
    width: 140px; height: 140px; border-radius: 50%; border: 8px solid #2d6a4f;
    display: flex; align-items: center; justify-content: center; background: #0f1f17;
  }
  .score-number { font-family: 'Space Grotesk', sans-serif; font-size: 3rem; font-weight: 700; color: #f4c430; }

  .section-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600;
    color: #b7e4c7; border-left: 3px solid #f4c430; padding-left: 0.8rem;
    margin: 1.5rem 0 1rem; letter-spacing: 0.3px;
  }

  .feedback-box {
    background: #162b1f; border: 1px solid #2d6a4f; border-radius: 10px;
    padding: 1.4rem; margin: 0.8rem 0; line-height: 1.7; color: #c8e6c9; font-size: 0.95rem;
  }
  .feedback-box.critical { border-left: 4px solid #ff5252; }
  .feedback-box.warning  { border-left: 4px solid #ffcc02; }
  .feedback-box.good     { border-left: 4px solid #69f0ae; }

  .phase-chip {
    display: inline-block; background: #2d6a4f; color: #b7e4c7;
    padding: 0.25rem 0.8rem; border-radius: 20px; font-size: 0.78rem;
    font-weight: 600; letter-spacing: 0.5px; margin: 0.2rem;
  }
  .phase-chip.active { background: #f4c430; color: #0f1f17; }

  .stat-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.5rem 0; }

  .stProgress > div > div { background-color: #f4c430 !important; }

  [data-testid="stSidebar"] { background: #162b1f !important; border-right: 1px solid #2d6a4f; }
  [data-testid="stSidebar"] .stMarkdown p { color: #a5d6a7; }

  .stButton button {
    background: linear-gradient(135deg, #2d6a4f, #40916c) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; transition: all 0.2s !important;
  }
  .stButton button:hover {
    background: linear-gradient(135deg, #40916c, #52b788) !important;
    transform: translateY(-1px); box-shadow: 0 4px 12px #2d6a4f88 !important;
  }

  [data-testid="stFileUploader"] { border: 2px dashed #2d6a4f !important; border-radius: 12px !important; background: #162b1f !important; }

  hr { border-color: #2d6a4f44 !important; }

  .stTabs [data-baseweb="tab-list"] { background: #1e3d2e; border-radius: 8px; }
  .stTabs [data-baseweb="tab"] { color: #a5d6a7 !important; }
  .stTabs [aria-selected="true"] { color: #f4c430 !important; background: #2d6a4f; border-radius: 6px; }

  .streamlit-expanderHeader { color: #b7e4c7 !important; background: #1e3d2e !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 0: 기준 DB (프로/아마추어 통계 누적)
# ═══════════════════════════════════════════════════════════════════════════════

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference_db.json")
_DB_METRICS = ["spine_angle_delta", "x_factor", "shoulder_rotation_max",
               "left_elbow_top", "left_knee_addr", "right_knee_addr"]


def load_ref_db() -> dict:
    if os.path.exists(_DB_PATH):
        try:
            with open(_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_ref_db(db: dict):
    with open(_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def update_ref_db(db: dict, label: str, summary: dict) -> dict:
    """summary 하나를 label 버킷에 누적 (온라인 평균 / 분산)."""
    ps = summary.get("phase_stats", {})

    def _get(key):
        if key == "left_elbow_top":
            v = (ps.get("백스윙 톱") or {}).get("left_elbow") or \
                (ps.get("백스윙") or {}).get("left_elbow")
        elif key == "left_knee_addr":
            v = (ps.get("어드레스") or {}).get("left_knee")
        elif key == "right_knee_addr":
            v = (ps.get("어드레스") or {}).get("right_knee")
        else:
            v = summary.get(key)
        return float(v) if v is not None else None

    bucket = db.setdefault(label, {"n": 0})
    bucket["n"] += 1
    for m in _DB_METRICS:
        v = _get(m)
        if v is None:
            continue
        entry = bucket.setdefault(m, {"sum": 0.0, "sum_sq": 0.0})
        entry["sum"]    += v
        entry["sum_sq"] += v * v
    return db


def get_ref_stats(db: dict, label: str) -> dict:
    """label 버킷에서 각 지표의 mean/std 반환."""
    bucket = db.get(label, {})
    n = bucket.get("n", 0)
    if n < 1:
        return {}
    result = {}
    for m in _DB_METRICS:
        e = bucket.get(m)
        if not e:
            continue
        mean = e["sum"] / n
        var  = max(0.0, e["sum_sq"] / n - mean * mean)
        result[m] = {"mean": round(mean, 2), "std": round(var ** 0.5, 2), "n": n}
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: MediaPipe 초기화
# ═══════════════════════════════════════════════════════════════════════════════
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: 수학적 엔진 (슬라이드 5 기반)
# ═══════════════════════════════════════════════════════════════════════════════

def normalize_landmarks(landmarks, w, h):
    """
    슬라이드 5: 양 어깨 너비를 기준으로 모든 좌표 정규화
    - 어깨 중심점을 원점으로
    - 어깨 너비를 1.0 단위로 스케일링
    → 카메라 거리·해상도와 무관한 절대 각도 비교 가능
    """
    l_sh = np.array([landmarks[11].x * w, landmarks[11].y * h])
    r_sh = np.array([landmarks[12].x * w, landmarks[12].y * h])
    shoulder_center = (l_sh + r_sh) / 2
    shoulder_width  = np.linalg.norm(l_sh - r_sh) + 1e-8

    normalized = {}
    for idx, lm in enumerate(landmarks):
        px = np.array([lm.x * w, lm.y * h])
        normalized[idx] = {
            "pos": (px - shoulder_center) / shoulder_width,
            "z":   lm.z,
            "vis": lm.visibility
        }
    return normalized, shoulder_width


def angle_from_three_points(a, b, c):
    """슬라이드 5: 두 벡터의 내적 + 코사인 제2법칙으로 관절각 계산"""
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    return round(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))), 1)


def calc_spine_angle(norm):
    """척추각: 어깨 중심 → 골반 중심이 수직축과 이루는 각도"""
    sh_c  = (norm[11]["pos"] + norm[12]["pos"]) / 2
    hip_c = (norm[23]["pos"] + norm[24]["pos"]) / 2
    dy = hip_c[1] - sh_c[1]
    dx = hip_c[0] - sh_c[0]
    return round(np.degrees(np.arctan2(abs(dx), abs(dy) + 1e-8)), 1)


def calc_shoulder_rotation(norm):
    """어깨 라인 기울기 → 회전각"""
    l = norm[11]["pos"]; r = norm[12]["pos"]
    return round(np.degrees(np.arctan2(abs(r[1] - l[1]), abs(r[0] - l[0]) + 1e-8)), 1)


def calc_hip_rotation(norm):
    """골반 라인 기울기 → 회전각"""
    l = norm[23]["pos"]; r = norm[24]["pos"]
    return round(np.degrees(np.arctan2(abs(r[1] - l[1]), abs(r[0] - l[0]) + 1e-8)), 1)


def calc_knee_angle(norm, side):
    hip_i, knee_i, ankle_i = (23, 25, 27) if side == 'left' else (24, 26, 28)
    return angle_from_three_points(
        norm[hip_i]["pos"], norm[knee_i]["pos"], norm[ankle_i]["pos"]
    )


def calc_elbow_angle(norm, side):
    sh_i, el_i, wr_i = (11, 13, 15) if side == 'left' else (12, 14, 16)
    return angle_from_three_points(
        norm[sh_i]["pos"], norm[el_i]["pos"], norm[wr_i]["pos"]
    )


def visibility_ok(norm, idx, thr=0.5):
    return norm[idx]["vis"] > thr


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: 이동 평균 필터 (슬라이드 8 기반)
# ═══════════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: 7단계 스윙 페이즈 감지 (슬라이드 6 기반)
# ═══════════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: 스윙 궤적 드로잉 (슬라이드 7 핵심 기능 ②)
# ═══════════════════════════════════════════════════════════════════════════════

PHASE_COLORS = {
    "어드레스":   (150, 200, 150),
    "백스윙":     (100, 180, 255),
    "백스윙 톱":  (255, 220,  50),
    "다운스윙":   (255, 140,  50),
    "임팩트":     (255,  60,  60),
    "팔로우스루": (180, 100, 255),
    "피니시":     (80,  220, 180),
}

def draw_swing_trajectory(frame, trajectory_points, current_phase):
    """슬라이드 7: 스윙 궤적 자동 드로잉 (손목 경로 + 페이즈별 색상)"""
    overlay = frame.copy()
    if len(trajectory_points) < 2:
        return frame

    for i in range(1, len(trajectory_points)):
        pt1 = trajectory_points[i - 1]
        pt2 = trajectory_points[i]
        phase = pt2.get("phase", "어드레스")
        color = PHASE_COLORS.get(phase, (200, 200, 200))
        if pt1["pos"] is not None and pt2["pos"] is not None:
            cv2.line(overlay,
                     (int(pt1["pos"][0]), int(pt1["pos"][1])),
                     (int(pt2["pos"][0]), int(pt2["pos"][1])),
                     color, 3, cv2.LINE_AA)
            cv2.circle(overlay,
                       (int(pt2["pos"][0]), int(pt2["pos"][1])),
                       4, color, -1)

    return cv2.addWeighted(overlay, 0.85, frame, 0.15, 0)


# PIL 한글 폰트 캐시 (프레임마다 재로드 방지)
_hud_font = None

def _get_hud_font(size=20):
    global _hud_font
    if _hud_font is not None:
        return _hud_font
    try:
        from PIL import ImageFont
        import os
        for fp in ["C:/Windows/Fonts/malgun.ttf",   # 맑은 고딕 (Windows)
                   "C:/Windows/Fonts/gulim.ttc",
                   "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"]:
            if os.path.exists(fp):
                _hud_font = ImageFont.truetype(fp, size)
                return _hud_font
    except Exception:
        pass
    return None


def draw_skeleton_annotations(frame, results, norm, metrics, w, h):
    """포즈 스켈레톤 + 척추선 + 한글 HUD 오버레이"""
    mp_drawing.draw_landmarks(
        frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing.DrawingSpec(
            color=(180, 220, 100), thickness=3, circle_radius=4),
        connection_drawing_spec=mp_drawing.DrawingSpec(
            color=(60, 160, 80), thickness=2)
    )

    # 척추선 (어깨 중심 → 골반 중심)
    lms = results.pose_landmarks.landmark
    sh_cx  = int((lms[11].x + lms[12].x) / 2 * w)
    sh_cy  = int((lms[11].y + lms[12].y) / 2 * h)
    hip_cx = int((lms[23].x + lms[24].x) / 2 * w)
    hip_cy = int((lms[23].y + lms[24].y) / 2 * h)
    cv2.line(frame, (sh_cx, sh_cy), (hip_cx, hip_cy), (244, 196, 48), 3)

    # HUD: 페이즈 + 척추각 + 시간
    phase = metrics.get("phase", "")
    spine = metrics.get("spine_angle", 0)
    t_sec = metrics.get("time", 0)
    hud_text = f"{phase}  |  척추각 {spine}°  |  {t_sec:.2f}초"

    cv2.rectangle(frame, (8, 8), (400, 52), (15, 50, 30), -1)

    font = _get_hud_font(20)
    if font:
        # PIL로 한글 렌더링
        try:
            from PIL import Image, ImageDraw
            pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            ImageDraw.Draw(pil).text((14, 14), hud_text, font=font, fill=(244, 196, 48))
            frame = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
        except Exception:
            cv2.putText(frame, f"{spine}deg | {t_sec:.2f}s",
                        (14, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (244, 196, 48), 2)
    else:
        # 폰트 없으면 ASCII 폴백
        cv2.putText(frame, f"{spine}deg | {t_sec:.2f}s",
                    (14, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (244, 196, 48), 2)

    return frame


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: 영상 편집 + 처리 메인 파이프라인
# ═══════════════════════════════════════════════════════════════════════════════

def get_video_info(video_path):
    """영상 기본 정보 반환"""
    cap = cv2.VideoCapture(video_path)
    fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration     = total_frames / fps
    width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return {"fps": fps, "total_frames": total_frames,
            "duration": duration, "width": width, "height": height}


def trim_video(video_path, start_sec, end_sec):
    """
    영상 구간 트리밍 — start_sec ~ end_sec 구간만 추출하여 임시 파일로 저장
    """
    cap = cv2.VideoCapture(video_path)
    fps    = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w      = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    start_frame = int(start_sec * fps)
    end_frame   = int(end_sec   * fps)

    # 임시 출력 파일
    tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tmp_out.close()

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out    = cv2.VideoWriter(tmp_out.name, fourcc, fps, (w, h))

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frame_idx = start_frame
    while cap.isOpened() and frame_idx <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    return tmp_out.name


def auto_detect_swing_window(video_path, window_sec=6.0, padding_sec=1.0):
    """
    전체 영상에서 손목 Y 변화가 가장 큰 구간을 탐색해 스윙 시작/끝 시간을 반환.
    긴 영상(연습 영상, 레슨 영상 등)에서 배치 학습 시 자동 트리밍에 사용.
    """
    cap   = cv2.VideoCapture(video_path)
    fps   = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur   = total / fps

    # 30초 이하면 탐지 불필요 → 전체 반환
    if dur <= 30.0:
        cap.release()
        return 0.0, round(dur, 1)

    # 빠른 스캔: 최대 400프레임만 추출 (10fps 이하)
    scan_sample = max(1, total // 400)
    times, wrist_ys = [], []

    with mp_pose.Pose(min_detection_confidence=0.3,
                      min_tracking_confidence=0.3,
                      model_complexity=1) as pose:
        fi = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if fi % scan_sample == 0:
                small = cv2.resize(frame, (320, 180))
                rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                res   = pose.process(rgb)
                if res.pose_landmarks:
                    lms = res.pose_landmarks.landmark
                    wy  = (lms[15].y + lms[16].y) / 2 * 180
                    wrist_ys.append(wy)
                    times.append(fi / fps)
            fi += 1
    cap.release()

    if len(wrist_ys) < 10:
        return 0.0, round(dur, 1)

    wy_arr = np.array(wrist_ys)
    # 슬라이딩 윈도우: window_sec 폭에서 wrist Y 진폭(max-min)이 최대인 구간
    win_n = max(5, int(window_sec / (dur / len(wy_arr))))
    best_amp, best_center = 0.0, len(wy_arr) // 2
    for i in range(len(wy_arr) - win_n + 1):
        amp = float(wy_arr[i:i + win_n].max() - wy_arr[i:i + win_n].min())
        if amp > best_amp:
            best_amp   = amp
            best_center = i + win_n // 2

    center_sec = times[best_center]
    half = window_sec / 2 + padding_sec
    start = max(0.0, center_sec - half)
    end   = min(dur, center_sec + half)
    return round(start, 1), round(end, 1)


def get_thumbnail_frames(video_path, n=10):
    """미리보기용 썸네일 프레임 추출"""
    cap          = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0
    thumbs       = []

    indices = np.linspace(0, total_frames - 1, n, dtype=int)
    for fi in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 썸네일 크기 축소
            h, w = frame_rgb.shape[:2]
            scale = 160 / w
            small = cv2.resize(frame_rgb, (160, int(h * scale)))
            thumbs.append((fi / fps, small))
    cap.release()
    return thumbs


def process_video(video_path, sample_rate=3, analyze_path=None):
    cap          = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0

    # 짧은 영상은 촘촘하게, 긴 영상은 MAX_ANALYSIS_FRAMES로 상한 설정
    # 다운스윙(0.3~0.5초)이 최소 10프레임 이상 확보되어야 임팩트 감지 가능
    MAX_ANALYSIS_FRAMES = 200
    if total_frames <= 180:          # 6초 이하(30fps 기준): 매 프레임 분석
        effective_sample = 1
    elif total_frames <= 540:        # 18초 이하: 최대 2프레임 간격
        effective_sample = min(sample_rate, 2)
    else:                            # 긴 영상: 200프레임 상한
        effective_sample = max(sample_rate, total_frames // MAX_ANALYSIS_FRAMES)

    frame_data       = []
    annotated_frames = []   # 최대 20장만 저장
    trajectory_pts   = []
    phase_detector   = SwingPhaseDetector()
    ma_filter        = MovingAverageFilter(window=5)
    prev_metrics     = {}
    frame_idx        = 0
    local_idx        = 0

    # 모든 샘플링 프레임의 어노테이션 저장 (해상도 축소로 메모리 절약)
    est_local = max(total_frames // effective_sample, 1)
    preview_indices = set(range(est_local))  # 전체 저장, 해상도로 메모리 절약

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))  # 루프 밖에서 1회 생성

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % effective_sample != 0:
                frame_idx += 1
                continue

            h, w = frame.shape[:2]

            # 해상도가 크면 먼저 축소 (처리 속도 향상)
            if w > 854:
                scale = 854 / w
                frame = cv2.resize(frame, (854, int(h * scale)))
                h, w  = frame.shape[:2]

            # CLAHE 전처리
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l_ch, a_ch, b_ch = cv2.split(lab)
            l_ch   = clahe.apply(l_ch)
            enhanced_rgb = cv2.cvtColor(cv2.merge([l_ch, a_ch, b_ch]), cv2.COLOR_LAB2RGB)

            results = pose.process(enhanced_rgb)

            if results.pose_landmarks:
                lms = results.pose_landmarks.landmark

                # 슬라이드 5: 어깨 너비 기준 정규화
                norm, shoulder_width = normalize_landmarks(lms, w, h)

                key_joints = [11, 12, 23, 24, 25, 26]
                visible    = all(visibility_ok(norm, idx) for idx in key_joints)

                if visible:
                    # 손목 y좌표 (정규화 공간)
                    # 픽셀 좌표 사용 (정규화 좌표는 y부호 역전 문제 있음)
                    lms_raw = results.pose_landmarks.landmark
                    lw_y = lms_raw[15].y * h  # 픽셀 y
                    rw_y = lms_raw[16].y * h
                    lw_x = lms_raw[15].x * w  # 픽셀 x
                    rw_x = lms_raw[16].x * w
                    # 골반 중심 x (하체선행 감지용)
                    hip_cx = float((norm[23]["pos"][0] + norm[24]["pos"][0]) / 2)
                    # 어깨 회전각
                    sh_rot = calc_shoulder_rotation(norm)
                    phase_detector.update(
                        local_idx, lw_y, rw_y,
                        hip_center_x=hip_cx,
                        shoulder_rot=sh_rot,
                        wrist_x=(lw_x + rw_x) / 2
                    )

                    raw = {
                        "frame":              frame_idx,
                        "local_idx":          local_idx,
                        "time":               round(local_idx * effective_sample / fps, 2),
                        "spine_angle":        calc_spine_angle(norm),
                        "shoulder_rotation":  calc_shoulder_rotation(norm),
                        "hip_rotation":       calc_hip_rotation(norm),
                        "left_knee":          calc_knee_angle(norm, 'left'),
                        "right_knee":         calc_knee_angle(norm, 'right'),
                        "left_elbow":         calc_elbow_angle(norm, 'left'),
                        "right_elbow":        calc_elbow_angle(norm, 'right'),
                        "shoulder_width_px":  round(shoulder_width, 1),
                    }

                    # 슬라이드 8: 이동 평균 필터 적용
                    smoothed_keys = [
                        "spine_angle", "shoulder_rotation", "hip_rotation",
                        "left_knee",   "right_knee", "left_elbow", "right_elbow"
                    ]
                    metrics = raw.copy()
                    for key in smoothed_keys:
                        metrics[key] = ma_filter.smooth(key, raw[key])

                    # 페이즈는 나중에 후처리로 채움 (일단 임시)
                    metrics["phase"] = "분석중"
                    prev_metrics     = metrics.copy()
                    frame_data.append(metrics)

                    # 손목 궤적 포인트 수집 (원본 픽셀 좌표)
                    lw_px = (int(lms[15].x * w), int(lms[15].y * h))
                    trajectory_pts.append({
                        "pos":       lw_px,
                        "local_idx": local_idx,
                        "phase":     "분석중"
                    })

                else:
                    # 슬라이드 8: 신뢰도 하락 → 이전 프레임 보간
                    if prev_metrics:
                        interp = prev_metrics.copy()
                        interp["frame"]     = frame_idx
                        interp["time"]      = round(local_idx * effective_sample / fps, 2)
                        interp["phase"]     = "보간"
                        interp["local_idx"] = local_idx
                        frame_data.append(interp)

                # 어노테이션: 균등 20장만 저장 (메모리 절약)
                if local_idx in preview_indices:
                    annotated = frame.copy()
                    if visible:
                        draw_swing_trajectory(annotated, trajectory_pts, metrics.get("phase", ""))
                        annotated = draw_skeleton_annotations(annotated, results, norm, metrics, w, h)
                    # 해상도 축소 (720p → 480p급)
                    ah, aw = annotated.shape[:2]
                    if aw > 480:
                        scale = 480 / aw
                        annotated = cv2.resize(annotated, (480, int(ah * scale)))
                    annotated_frames.append(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
                local_idx += 1

            frame_idx += 1

    cap.release()

    # ── 슬라이드 6: 전체 시계열로 7단계 페이즈 후처리 ──────────────────────
    phase_detector.detect_all_phases()
    for i, fd in enumerate(frame_data):
        li = fd["local_idx"]
        fd["phase"] = phase_detector.get_phase_for_frame(li)
    for i, tp in enumerate(trajectory_pts):
        li = tp["local_idx"]
        tp["phase"] = phase_detector.get_phase_for_frame(li)

    return frame_data, annotated_frames, trajectory_pts, fps, phase_detector, effective_sample


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: 지표 요약 및 스코어링
# ═══════════════════════════════════════════════════════════════════════════════

def compute_summary(frame_data):
    if not frame_data:
        return {}

    def avg(k): return round(np.mean([f[k] for f in frame_data if k in f]), 1)
    def mx(k):  return round(np.max ([f[k] for f in frame_data if k in f]), 1)
    def mn(k):  return round(np.min ([f[k] for f in frame_data if k in f]), 1)

    spine_vals  = [f["spine_angle"] for f in frame_data]
    spine_delta = round(max(spine_vals) - min(spine_vals), 1)

    # 페이즈별 집계
    phase_groups = {}
    for f in frame_data:
        ph = f.get("phase", "")
        phase_groups.setdefault(ph, []).append(f)

    # 각 페이즈 핵심 지표 (팔꿈치·무릎 포함)
    phase_stats = {}
    for ph, frames in phase_groups.items():
        if frames:
            def ph_avg(k):
                vals = [f[k] for f in frames if k in f]
                return round(float(np.mean(vals)), 1) if vals else None
            phase_stats[ph] = {
                "spine_angle":  ph_avg("spine_angle"),
                "shoulder_rot": ph_avg("shoulder_rotation"),
                "hip_rot":      ph_avg("hip_rotation"),
                "left_elbow":   ph_avg("left_elbow"),
                "right_elbow":  ph_avg("right_elbow"),
                "left_knee":    ph_avg("left_knee"),
                "right_knee":   ph_avg("right_knee"),
                "count":        len(frames)
            }

    # 척추각 변화량: 어드레스 → 임팩트 구간만 측정 (팔로우스루/피니시 제외)
    # 전 구간 max-min은 피니시 자세까지 포함되어 프로 영상에서 과도하게 높아짐
    swing_phases = ["어드레스", "백스윙", "백스윙 톱", "다운스윙", "임팩트"]
    swing_frames = [f for f in frame_data if f.get("phase") in swing_phases]
    if swing_frames:
        sv = [f["spine_angle"] for f in swing_frames]
        spine_delta_swing = round(max(sv) - min(sv), 1)
    else:
        spine_delta_swing = spine_delta  # 폴백

    return {
        "total_frames":          len(frame_data),
        "spine_angle_avg":       avg("spine_angle"),
        "spine_angle_delta":     spine_delta_swing,   # 어드레스~임팩트 구간만
        "spine_angle_min":       mn("spine_angle"),
        "spine_angle_max":       mx("spine_angle"),
        "shoulder_rotation_avg": avg("shoulder_rotation"),
        "shoulder_rotation_max": mx("shoulder_rotation"),
        "hip_rotation_avg":      avg("hip_rotation"),
        "hip_rotation_max":      mx("hip_rotation"),
        "x_factor":              round(mx("shoulder_rotation") - mx("hip_rotation"), 1),
        "left_knee_avg":         avg("left_knee"),
        "right_knee_avg":        avg("right_knee"),
        "left_elbow_avg":        avg("left_elbow"),
        "right_elbow_avg":       avg("right_elbow"),
        "phases_detected":       list(phase_groups.keys()),
        "phase_stats":           phase_stats,
    }


def compute_score(summary, ref_db=None):
    score       = 100
    issues      = []
    phase_stats = summary.get("phase_stats", {})

    # 프로 기준 통계 (DB에 2개 이상 있으면 동적 임계값, 없으면 하드코딩 기본값)
    pro_stats = get_ref_stats(ref_db or {}, "프로") if ref_db else {}

    def _thresh(metric, default_warn, default_crit=None):
        """프로 분포 기반 임계값 반환 (mean + 1σ = warn, mean + 2σ = crit)."""
        if metric in pro_stats and pro_stats[metric]["n"] >= 2:
            m = pro_stats[metric]["mean"]
            s = pro_stats[metric]["std"]
            return m + max(s, 1.0), (m + max(s * 2, 2.0)) if default_crit is not None else None
        return default_warn, default_crit

    def ps(ph, key, fallback=None):
        return phase_stats.get(ph, {}).get(key, fallback)

    # ── 1. 척추각 안정성 (어드레스 → 임팩트 구간) ─────────────────────────
    delta = summary.get("spine_angle_delta", 0)
    t_warn, t_crit = _thresh("spine_angle_delta", 7, 12)
    if delta > t_crit:
        score -= 25
        issues.append(("critical", f"척추각 변화량 {delta}° — 헤드업·스웨이 위험. 임팩트까지 척추각을 고정하세요."))
    elif delta > t_warn:
        score -= 12
        issues.append(("warning", f"척추각 변화량 {delta}° — 약간의 상체 흔들림. {t_warn:.0f}° 이내 유지를 목표로 하세요."))
    else:
        issues.append(("good", f"척추각 안정 ({delta}°) — 견고한 회전축 유지 ✓"))

    # ── 2. X-Factor (어깨-골반 꼬임) ───────────────────────────────────────
    xf = summary.get("x_factor", 0)
    if "x_factor" in pro_stats and pro_stats["x_factor"]["n"] >= 2:
        pm = pro_stats["x_factor"]["mean"]
        ps_ = pro_stats["x_factor"]["std"]
        xf_lo = max(10.0, pm - ps_ * 2)
        xf_hi = pm + ps_ * 2
    else:
        xf_lo, xf_hi = 20.0, 80.0
    if xf < xf_lo:
        score -= 15
        issues.append(("warning", f"X-Factor {xf}° — 어깨-골반 꼬임 부족. 백스윙 시 어깨를 더 회전하세요."))
    elif xf > xf_hi:
        score -= 8
        issues.append(("warning", f"X-Factor {xf}° — 과도한 꼬임. {xf_hi:.0f}° 이하로 제한하세요."))
    else:
        issues.append(("good", f"X-Factor {xf}° — 적절한 몸통 꼬임 ✓"))

    # ── 3. 무릎 굴곡 (어드레스 페이즈 기준) ────────────────────────────────
    addr_lk = ps("어드레스", "left_knee")
    addr_rk = ps("어드레스", "right_knee")
    lk = addr_lk if addr_lk is not None else summary.get("left_knee_avg", 180)
    rk = addr_rk if addr_rk is not None else summary.get("right_knee_avg", 180)
    # 무릎은 "너무 펴짐" 이 문제 → pro 기준 하한선
    if "left_knee_addr" in pro_stats and pro_stats["left_knee_addr"]["n"] >= 2:
        knee_lo = pro_stats["left_knee_addr"]["mean"] - pro_stats["left_knee_addr"]["std"] * 1.5
    else:
        knee_lo = 165.0
    if lk > knee_lo or rk > knee_lo:
        score -= 10
        issues.append(("warning", f"어드레스 무릎 굴곡 부족 (좌 {lk}° / 우 {rk}°) — 지면 반력 활용이 제한됩니다."))
    else:
        issues.append(("good", f"어드레스 무릎 굴곡 적절 (좌 {lk}° / 우 {rk}°) ✓"))

    # ── 4. 왼팔 직선성 (백스윙 톱 기준) ────────────────────────────────────
    top_le = ps("백스윙 톱", "left_elbow")
    bs_le  = ps("백스윙",    "left_elbow")
    le = top_le if top_le is not None else (bs_le if bs_le is not None else summary.get("left_elbow_avg", 180))
    if "left_elbow_top" in pro_stats and pro_stats["left_elbow_top"]["n"] >= 2:
        elbow_lo = pro_stats["left_elbow_top"]["mean"] - pro_stats["left_elbow_top"]["std"] * 1.5
    else:
        elbow_lo = 140.0
    if le < elbow_lo:
        score -= 10
        issues.append(("warning", f"백스윙 톱 왼팔 굽힘 ({le}°) — 백스윙 아크 손실. 왼팔을 펴는 연습이 필요합니다."))
    else:
        issues.append(("good", f"백스윙 톱 왼팔 직선성 양호 ({le}°) ✓"))

    # ── 5. 어깨 회전 ────────────────────────────────────────────────────────
    sh_max = summary.get("shoulder_rotation_max", 0)
    if "shoulder_rotation_max" in pro_stats and pro_stats["shoulder_rotation_max"]["n"] >= 2:
        sh_lo = pro_stats["shoulder_rotation_max"]["mean"] - pro_stats["shoulder_rotation_max"]["std"] * 1.5
    else:
        sh_lo = 60.0
    if sh_max < sh_lo:
        score -= 8
        issues.append(("warning", f"어깨 최대 회전 {sh_max}° — 백스윙 부족으로 비거리 손실 가능성."))
    else:
        issues.append(("good", f"어깨 회전 충분 ({sh_max}°) ✓"))

    return max(0, min(100, score)), issues


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: LLM 피드백 (슬라이드 9: 투어 프로 페르소나 + 구조화 JSON)
# ═══════════════════════════════════════════════════════════════════════════════

def build_prompt(summary, issues, ref_db=None):
    """슬라이드 9: 구조화된 편차 데이터(JSON) + 투어 프로 코치 페르소나"""
    issue_text = "\n".join([f"- [{lvl.upper()}] {msg}" for lvl, msg in issues])

    # 페이즈별 통계 JSON
    phase_json = json.dumps(summary.get("phase_stats", {}), ensure_ascii=False, indent=2)

    # 프로 기준 비교 블록 (DB 있을 때만)
    ref_block = ""
    if ref_db:
        pro_s = get_ref_stats(ref_db, "prefs")  # placeholder
        pro_s = get_ref_stats(ref_db, "프로")
        am_s  = get_ref_stats(ref_db, "아마추어")
        if pro_s:
            label_map = {
                "spine_angle_delta":     "척추각 변화량",
                "x_factor":              "X-Factor",
                "shoulder_rotation_max": "어깨 최대 회전",
                "left_elbow_top":        "왼팔(백스윙톱)",
                "left_knee_addr":        "왼쪽 무릎(어드레스)",
                "right_knee_addr":       "오른쪽 무릎(어드레스)",
            }
            user_vals = {
                "spine_angle_delta":     summary.get("spine_angle_delta"),
                "x_factor":              summary.get("x_factor"),
                "shoulder_rotation_max": summary.get("shoulder_rotation_max"),
                "left_elbow_top":        (summary.get("phase_stats", {}).get("백스윙 톱") or {}).get("left_elbow"),
                "left_knee_addr":        (summary.get("phase_stats", {}).get("어드레스") or {}).get("left_knee"),
                "right_knee_addr":       (summary.get("phase_stats", {}).get("어드레스") or {}).get("right_knee"),
            }
            rows = []
            for m, lbl in label_map.items():
                if m not in pro_s:
                    continue
                pm, ps_ = pro_s[m]["mean"], pro_s[m]["std"]
                uv = user_vals.get(m)
                uv_str = f"{uv:.1f}°" if uv is not None else "-"
                am_str = f"{am_s[m]['mean']:.1f}°" if m in am_s else "-"
                rows.append(f"| {lbl} | {uv_str} | {pm:.1f}±{ps_:.1f}° | {am_str} |")
            if rows:
                n_pro = ref_db.get("프로", {}).get("n", 0)
                n_am  = ref_db.get("아마추어", {}).get("n", 0)
                ref_block = f"""
## 학습된 기준 데이터와 비교 (프로 {n_pro}명 / 아마추어 {n_am}명)
| 지표 | 이번 스윙 | 프로 기준(평균±σ) | 아마추어 평균 |
|------|-----------|-------------------|---------------|
""" + "\n".join(rows)

    return f"""당신은 20년 경력의 투어 프로 출신 골프 코치입니다.
원인과 결과를 항상 함께 설명하며, 수치 데이터에 기반한 구체적인 교정 방법을 제시합니다.

## 구조화된 스윙 분석 데이터 (JSON)
```json
{{
  "총_분석_프레임": {summary['total_frames']},
  "척추각": {{
    "평균": {summary['spine_angle_avg']}°,
    "변화량_delta": {summary['spine_angle_delta']}°,
    "최소": {summary['spine_angle_min']}°,
    "최대": {summary['spine_angle_max']}°
  }},
  "회전_분석": {{
    "어깨_최대_회전": {summary['shoulder_rotation_max']}°,
    "골반_최대_회전": {summary['hip_rotation_max']}°,
    "X_Factor_꼬임": {summary['x_factor']}°
  }},
  "관절_평균": {{
    "왼쪽_무릎": {summary['left_knee_avg']}°,
    "오른쪽_무릎": {summary['right_knee_avg']}°,
    "왼팔_팔꿈치": {summary['left_elbow_avg']}°,
    "오른팔_팔꿈치": {summary['right_elbow_avg']}°
  }},
  "7단계_페이즈별_데이터": {phase_json}
}}
```

## AI 자동 진단 이슈
{issue_text}
{ref_block}
위 데이터를 기반으로 정확히 아래 형식으로 코칭 리포트를 작성하세요:

### 🏌️ 종합 스윙 평가
(전반적인 강점과 가장 시급한 개선점을 2~3문장으로)

### ⚠️ 핵심 교정 포인트 (원인 → 결과 → 해결책)
**[1번 포인트]**: (원인) ~ 때문에, (결과) ~ 현상이 발생합니다. (해결) ~을 실천하세요.
**[2번 포인트]**: ...
**[3번 포인트]**: ...

### 💪 맞춤형 연습 드릴
**드릴 1**: (이름) — (구체적 방법과 횟수)
**드릴 2**: (이름) — (구체적 방법과 횟수)

### 🎯 다음 라운드 전 ONE THING
(가장 우선순위가 높은 단 하나의 집중 과제를 굵게 강조)

한국어로, 친절하지만 프로답게 작성해주세요."""


def get_llm_feedback(summary, issues, provider, api_key, model_name=None, ref_db=None):
    """슬라이드 9: LLM 피드백 생성 (Gemini / Claude / GPT 선택)"""
    prompt = build_prompt(summary, issues, ref_db=ref_db)

    if provider == "Gemini":
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name or "gemini-2.0-flash",
            contents=prompt
        )
        return response.text

    elif provider == "Claude":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=model_name or "claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text

    elif provider == "GPT":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model_name or "gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
        return resp.choices[0].message.content

    return "지원하지 않는 LLM 공급자입니다."


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: UI 컴포넌트
# ═══════════════════════════════════════════════════════════════════════════════

def render_hero():
    st.markdown("""
    <div class="hero-header">
      <div class="hero-title">⛳ AI 골프 스윙 분석기</div>
      <div class="hero-sub">MediaPipe 어깨폭 정규화 · 7단계 자동 세그먼테이션 · 투어 프로 LLM 코칭</div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label, value, unit="", status=""):
    sc = f"metric-status-{status}" if status else ""
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value {sc}">{value}<span class="metric-unit"> {unit}</span></div>
    </div>
    """, unsafe_allow_html=True)


def get_status(val, good_lo, good_hi, warn_lo=None, warn_hi=None):
    if good_lo <= val <= good_hi:   return "good"
    if warn_lo is not None and warn_lo <= val <= warn_hi: return "warn"
    return "bad"


def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ 설정")
        st.divider()

        provider = st.selectbox(
            "🤖 LLM 공급자",
            ["Gemini", "Claude", "GPT"],
            help="Gemini: 무료 / Claude·GPT: 유료 API"
        )

        model_options = {
            "Gemini": ["gemini-2.0-flash", "gemini-1.5-pro"],
            "Claude": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
            "GPT":    ["gpt-4o", "gpt-4o-mini"],
        }
        model_name = st.selectbox("모델 선택", model_options[provider])

        api_key = st.text_input(
            f"🔑 {provider} API 키",
            type="password",
            placeholder="API 키를 입력하세요",
            help={
                "Gemini": "aistudio.google.com → 무료 발급",
                "Claude": "console.anthropic.com",
                "GPT":    "platform.openai.com",
            }[provider]
        )

        st.divider()
        st.markdown("**📊 분석 옵션**")
        sample_rate = st.slider("프레임 샘플 간격", 1, 10, 3,
                                 help="낮을수록 정밀하지만 처리 시간 증가")

        st.divider()
        st.markdown("""
        <div style='color:#a5d6a7; font-size:0.8rem; line-height:1.8'>
        <b style='color:#b7e4c7'>📐 세미프로 기준치</b><br>
        • 척추각 변화: <b style='color:#69f0ae'>±5° 이내</b><br>
        • X-Factor: <b style='color:#69f0ae'>35° ~ 55°</b><br>
        • 무릎 굴곡: <b style='color:#69f0ae'>130° ~ 155°</b><br>
        • 왼팔 직선성: <b style='color:#69f0ae'>150°+</b><br>
        • 어깨 회전: <b style='color:#69f0ae'>80°+</b>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("""
        <div style='color:#81c784; font-size:0.78rem'>
        💡 <b>최적 촬영 조건</b><br>
        • 정면(Face-on) 또는 측면(DTL)<br>
        • 골퍼가 화면 중앙에 위치<br>
        • 밝은 조명 / 단색 배경<br>
        • 720p 이상 · 5~30초 분량
        </div>
        """, unsafe_allow_html=True)

    return provider, model_name, api_key, sample_rate


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10: 메인 앱
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    render_hero()
    provider, model_name, api_key, sample_rate = render_sidebar()

    # 기준 DB 로드 (세션 캐시)
    if "ref_db" not in st.session_state:
        st.session_state.ref_db = load_ref_db()
    ref_db = st.session_state.ref_db

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📹 영상 분석",
        "🔄 7단계 페이즈",
        "📊 상세 데이터",
        "🤖 AI 코칭 리포트",
        "📚 기준 학습",
    ])

    # ── TAB 1: 영상 업로드 & 분석 ──────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-title">골프 스윙 영상 업로드</div>', unsafe_allow_html=True)

        col_up, col_tip = st.columns([2, 1])
        with col_up:
            uploaded = st.file_uploader(
                "MP4, MOV, AVI 파일을 드롭하거나 클릭하여 선택",
                type=["mp4", "mov", "avi", "m4v"],
                label_visibility="collapsed"
            )
        with col_tip:
            st.info("💡 드라이버·아이언·퍼팅 모두 분석 가능\n\n정면 또는 측면 촬영 권장")

        if uploaded:
            # 업로드 파일 임시 저장
            if "tmp_original" not in st.session_state or \
               st.session_state.get("uploaded_name") != uploaded.name:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                    tmp.write(uploaded.read())
                    st.session_state.tmp_original  = tmp.name
                    st.session_state.uploaded_name = uploaded.name
                    st.session_state.pop("trim_path", None)   # 새 파일이면 트림 초기화

            tmp_path  = st.session_state.tmp_original
            info      = get_video_info(tmp_path)
            duration  = info["duration"]

            # ── 영상 미리보기 ──────────────────────────────────────────────
            col_vid, col_ctrl = st.columns([3, 2])
            with col_vid:
                preview_path = st.session_state.get("trim_path", tmp_path)
                st.video(preview_path)
            with col_ctrl:
                st.markdown('<div class="section-title">영상 정보</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="feedback-box good">
                ✅ 파일: <b>{uploaded.name}</b><br>
                ✅ 크기: <b>{uploaded.size/1024/1024:.1f} MB</b><br>
                ✅ 길이: <b>{duration:.1f}초</b> ({info['total_frames']}프레임)<br>
                ✅ 해상도: <b>{info['width']}×{info['height']}</b>
                </div>
                """, unsafe_allow_html=True)

            # ── ✂️ 구간 편집 UI ────────────────────────────────────────────
            st.divider()
            st.markdown('<div class="section-title">✂️ 분석 구간 선택</div>', unsafe_allow_html=True)
            st.caption("긴 영상에서 스윙 구간만 선택하여 분석 정확도를 높이세요")

            # 슬라이더
            start_sec, end_sec = st.slider(
                "구간 선택 (초)",
                min_value=0.0,
                max_value=float(round(duration, 1)),
                value=(0.0, float(round(min(duration, 30.0), 1))),
                step=0.1,
                format="%.1f초",
                help="슬라이더를 움직이면 아래에 해당 프레임이 바로 표시됩니다"
            )
            sel_duration = end_sec - start_sec

            # ── 실시간 프레임 미리보기 ──────────────────────────────────────
            col_start, col_mid, col_end = st.columns([2, 1, 2])

            def get_frame_at(video_path, sec):
                """특정 시간의 프레임 캡처"""
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(sec * fps))
                ret, frame = cap.read()
                cap.release()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w = frame_rgb.shape[:2]
                    if w > 480:
                        scale = 480 / w
                        frame_rgb = cv2.resize(frame_rgb, (480, int(h * scale)))
                    return frame_rgb
                return None

            with col_start:
                st.markdown("""<div style='text-align:center; color:#f4c430; font-weight:700;
                    font-size:0.9rem; margin-bottom:0.4rem'>▶ 시작 프레임</div>""",
                    unsafe_allow_html=True)
                start_frame = get_frame_at(tmp_path, start_sec)
                if start_frame is not None:
                    st.image(start_frame, caption=f"⏱ {start_sec:.1f}초", use_container_width=True)

            with col_mid:
                col_status = "good" if 3 <= sel_duration <= 30 else "warn"
                st.markdown(f"""
                <div style='display:flex; flex-direction:column; align-items:center;
                     justify-content:center; height:100%; padding-top:2rem; gap:0.8rem'>
                  <div class="metric-card" style="width:100%">
                    <div class="metric-label">선택 길이</div>
                    <div class="metric-value metric-status-{col_status}">{sel_duration:.1f}<span class="metric-unit">초</span></div>
                  </div>
                  <div class="metric-card" style="width:100%">
                    <div class="metric-label">프레임 수</div>
                    <div class="metric-value" style="font-size:1.4rem">{int(sel_duration * info["fps"])}<span class="metric-unit">f</span></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            with col_end:
                st.markdown("""<div style='text-align:center; color:#69f0ae; font-weight:700;
                    font-size:0.9rem; margin-bottom:0.4rem'>⏹ 끝 프레임</div>""",
                    unsafe_allow_html=True)
                end_frame = get_frame_at(tmp_path, max(0, end_sec - 0.1))
                if end_frame is not None:
                    st.image(end_frame, caption=f"⏱ {end_sec:.1f}초", use_container_width=True)

            # 구간 적용 버튼
            trim_btn = st.button("✂️ 이 구간으로 분석하기", use_container_width=True)

            # 썸네일 스트립
            with st.expander("🎞️ 전체 프레임 스트립 보기"):
                thumbs = get_thumbnail_frames(tmp_path, n=10)
                cols   = st.columns(10)
                for col, (t, img) in zip(cols, thumbs):
                    with col:
                        marker = "🟡" if start_sec <= t <= end_sec else "⚫"
                        st.image(img, caption=f"{marker}{t:.1f}s", use_container_width=True)

            # 트리밍 실행
            if trim_btn:
                if sel_duration < 1.0:
                    st.error("구간이 너무 짧습니다. 최소 1초 이상 선택하세요.")
                else:
                    with st.spinner(f"✂️ {start_sec:.1f}초 ~ {end_sec:.1f}초 구간 추출 중..."):
                        trim_path = trim_video(tmp_path, start_sec, end_sec)
                        st.session_state.trim_path = trim_path
                    st.success(f"✅ 구간 적용 완료! ({sel_duration:.1f}초) — 위 영상 미리보기가 업데이트됩니다.")
                    st.rerun()

            # 분석 대상 경로 결정
            analyze_path = st.session_state.get("trim_path", tmp_path)
            is_trimmed   = "trim_path" in st.session_state

            st.divider()
            col_info, col_go = st.columns([3, 1])
            with col_info:
                if is_trimmed:
                    trim_info = get_video_info(analyze_path)
                    st.markdown(f"""
                    <div class="feedback-box good">
                    ✂️ <b>트리밍된 구간으로 분석</b> — {trim_info['duration']:.1f}초 · {trim_info['total_frames']}프레임<br>
                    샘플링: 매 <b>{sample_rate}</b>프레임
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="feedback-box warning">
                    📹 <b>전체 영상으로 분석</b> — {duration:.1f}초<br>
                    구간을 선택하면 더 정확한 분석이 가능합니다.
                    </div>
                    """, unsafe_allow_html=True)
            with col_go:
                analyze_btn = st.button("🔍 스윙 분석 시작", use_container_width=True)

            if analyze_btn:
                prog = st.progress(0, "🦴 관절 포인트 추출 중...")
                frame_data, annotated_frames, traj_pts, fps, phase_det, eff_sample = \
                    process_video(analyze_path, sample_rate, analyze_path=analyze_path)
                prog.progress(70, "📐 각도 계산 & 페이즈 세그먼테이션...")
                summary = compute_summary(frame_data)
                prog.progress(90, "🏅 스코어 산정...")
                score, issues = compute_score(summary, ref_db=ref_db)
                prog.progress(100, "✅ 완료!")
                time.sleep(0.3); prog.empty()

                st.session_state.update({
                    "frame_data":        frame_data,
                    "annotated_frames":  annotated_frames,
                    "trajectory_pts":    traj_pts,
                    "summary":           summary,
                    "score":             score,
                    "issues":            issues,
                    "fps":               fps,
                    "phase_det":         phase_det,
                    "eff_sample":        eff_sample,
                })

            if "summary" in st.session_state:
                summary = st.session_state.summary
                score   = st.session_state.score
                issues  = st.session_state.issues

                st.divider()
                st.markdown('<div class="section-title">📊 분석 결과 요약</div>', unsafe_allow_html=True)

                col_sc, c1, c2, c3, c4, c5 = st.columns([1.4, 1, 1, 1, 1, 1])
                with col_sc:
                    color = "#69f0ae" if score >= 80 else "#ffcc02" if score >= 60 else "#ff5252"
                    grade = "S" if score >= 95 else "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D"
                    st.markdown(f"""
                    <div class="score-container">
                      <div class="score-ring" style="border-color:{color}">
                        <span class="score-number" style="color:{color}">{score}</span>
                      </div>
                      <div style="margin-top:0.7rem;font-family:'Space Grotesk';font-size:1rem;color:#b7e4c7">
                        스윙 점수 &nbsp;<span style="color:{color};font-weight:700">{grade}등급</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                with c1:
                    s = get_status(summary['spine_angle_delta'], 0, 5, 5, 10)
                    render_metric_card("척추각 변화", summary['spine_angle_delta'], "°", s)
                with c2:
                    s = get_status(summary['x_factor'], 35, 55, 20, 60)
                    render_metric_card("X-Factor", summary['x_factor'], "°", s)
                with c3:
                    render_metric_card("어깨 회전", summary['shoulder_rotation_max'], "°")
                with c4:
                    render_metric_card("골반 회전", summary['hip_rotation_max'], "°")
                with c5:
                    ph_cnt = len(summary['phases_detected'])
                    s = "good" if ph_cnt >= 5 else "warn"
                    render_metric_card("감지 페이즈", ph_cnt, "/7", s)

                st.divider()
                st.markdown('<div class="section-title">🔍 항목별 진단</div>', unsafe_allow_html=True)
                for level, msg in issues:
                    icon = "🔴" if level == "critical" else "🟡" if level == "warning" else "🟢"
                    st.markdown(f'<div class="feedback-box {level}">{icon} {msg}</div>', unsafe_allow_html=True)

                # 어노테이션 프레임 샘플 (슬라이드 7: 궤적 드로잉 포함)
                frames = st.session_state.get("annotated_frames", [])
                if frames:
                    st.divider()
                    st.markdown('<div class="section-title">🎬 스윙 궤적 분석 프레임</div>', unsafe_allow_html=True)

                    # 7단계 페이즈별 대표 프레임 추출
                    fd       = st.session_state.frame_data
                    phase_order = ["어드레스","백스윙","백스윙 톱","다운스윙","임팩트","팔로우스루","피니시"]
                    phase_frame_map = {}  # phase → annotated frame index

                    # annotated_frames는 frame_data와 1:1 대응
                    # (preview_indices = 전체 저장으로 변경됨)
                    # frame_data[i] ↔ annotated_frames[i] 직접 매핑
                    for ph in phase_order:
                        ph_fd = [(i, f) for i, f in enumerate(fd) if f.get("phase") == ph]
                        if not ph_fd:
                            continue
                        # 페이즈별 대표 프레임 위치 선택
                        # 임팩트: 첫 프레임 (순간적 접촉)
                        # 다운스윙: 75% 지점 (초반 플래토 구간 제외, 실제 급강하 구간 표시)
                        # 나머지: 중간 프레임
                        if ph == "임팩트":
                            rep_i = ph_fd[0][0]
                        elif ph == "다운스윙":
                            rep_i = ph_fd[min(len(ph_fd)-1, int(len(ph_fd)*0.85))][0]
                        else:
                            rep_i = ph_fd[len(ph_fd)//2][0]
                        ann_idx = min(rep_i, len(frames) - 1)
                        phase_frame_map[ph] = frames[ann_idx]

                    detected_phases = [ph for ph in phase_order if ph in phase_frame_map]
                    cols = st.columns(len(detected_phases))
                    for col, ph in zip(cols, detected_phases):
                        with col:
                            st.image(phase_frame_map[ph], caption=ph, use_container_width=True)

            # 임시 파일은 세션 종료 시 자동 정리됨

    # ── TAB 2: 7단계 페이즈 (슬라이드 6) ──────────────────────────────────
    with tab2:
        if "summary" not in st.session_state:
            st.info("📹 먼저 영상을 업로드하고 분석을 실행해주세요.")
        else:
            summary = st.session_state.summary
            phase_stats = summary.get("phase_stats", {})

            st.markdown('<div class="section-title">🔄 7단계 스윙 자동 세그먼테이션</div>', unsafe_allow_html=True)
            st.caption("손목 y좌표 변화율 · 속도 벡터 기반 자동 분할 (슬라이드 6 알고리즘)")

            # 페이즈 타임라인
            phase_order = ["어드레스", "백스윙", "백스윙 톱", "다운스윙", "임팩트", "팔로우스루", "피니시"]
            detected    = summary.get("phases_detected", [])

            chips_html = ""
            for ph in phase_order:
                cls = "phase-chip active" if ph in detected else "phase-chip"
                cnt = phase_stats.get(ph, {}).get("count", 0)
                chips_html += f'<span class="{cls}">{ph} ({cnt}f)</span> '
            st.markdown(f'<div class="stat-row">{chips_html}</div>', unsafe_allow_html=True)

            st.divider()

            # 페이즈별 핵심 지표 카드
            phase_display = [ph for ph in phase_order if ph in phase_stats]
            if phase_display:
                cols = st.columns(min(len(phase_display), 4))
                for i, ph in enumerate(phase_display):
                    ps = phase_stats[ph]
                    col = cols[i % 4]
                    with col:
                        spine_color = "#69f0ae" if abs(ps['spine_angle'] - summary['spine_angle_avg']) < 3 else "#ffcc02"
                        st.markdown(f"""
                        <div class="metric-card" style="margin-bottom:0.8rem">
                          <div class="metric-label">{ph}</div>
                          <div style="font-size:0.82rem; color:#a5d6a7; margin-top:0.4rem; line-height:1.8">
                            척추각 <b style="color:{spine_color}">{ps['spine_angle']}°</b><br>
                            어깨 회전 <b style="color:#81d4fa">{ps['shoulder_rot']}°</b><br>
                            골반 회전 <b style="color:#ce93d8">{ps['hip_rot']}°</b>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

            # ── 손목 Y 진단 차트 (페이즈 경계 시각화) ──────────────────
            st.divider()
            st.markdown('<div class="section-title">🔬 손목 Y 궤적 진단 (페이즈 경계 확인용)</div>', unsafe_allow_html=True)
            st.caption("차트에서 각 페이즈가 올바른 위치에 분리됐는지 확인하세요. 아래 표의 Y(px) 값이 클수록 손목이 낮은 위치(다운스윙)입니다.")

            import pandas as pd
            phase_det = st.session_state.get("phase_det")
            if phase_det and phase_det.wrist_y_history and phase_det.phase_boundaries:
                wy_hist = phase_det.wrist_y_history
                n_hist  = len(wy_hist)
                fps_val = st.session_state.get("fps", 30.0)
                eff_s   = st.session_state.get("eff_sample", 1)

                # 페이즈별 컬럼으로 손목 Y 시각화 (해당 구간만 값, 나머지 NaN)
                wy_df = pd.DataFrame(index=range(n_hist))
                for ph, (lo, hi) in phase_det.phase_boundaries.items():
                    col = [None] * n_hist
                    for k in range(max(0, lo), min(n_hist, hi + 1)):
                        col[k] = wy_hist[k]
                    wy_df[ph] = col
                # 시간축 추가
                wy_df.index = [round(i * eff_s / fps_val, 2) for i in range(n_hist)]
                wy_df.index.name = "시간(초)"
                st.line_chart(wy_df, height=220)

                # 경계 테이블
                rows = []
                for ph, (lo, hi) in phase_det.phase_boundaries.items():
                    y_lo = round(wy_hist[lo], 1)       if lo < n_hist else "-"
                    y_hi = round(wy_hist[min(hi, n_hist-1)], 1) if hi < n_hist else "-"
                    t_lo = round(lo * eff_s / fps_val, 2)
                    t_hi = round(min(hi, n_hist-1) * eff_s / fps_val, 2)
                    rows.append({
                        "페이즈": ph,
                        "시작(초)": t_lo,
                        "끝(초)":   t_hi,
                        "프레임 수": hi - lo,
                        "시작 Y(px)": y_lo,
                        "끝 Y(px)":   y_hi,
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                st.caption("💡 '백스윙' 구간 시작 Y > 끝 Y(손목 상승), '임팩트' 끝 Y ≈ 어드레스 시작 Y이면 정상입니다.")

            # 관절 각도 시계열
            st.divider()
            st.markdown('<div class="section-title">관절 각도 시계열</div>', unsafe_allow_html=True)
            fd = st.session_state.frame_data
            df = pd.DataFrame(fd)
            if "local_idx" in df.columns and len(df) > 0:
                st.line_chart(
                    df[["time", "spine_angle", "shoulder_rotation", "hip_rotation"]]
                      .set_index("time"),
                    color=["#f4c430", "#81d4fa", "#ce93d8"]
                )

            # 페이즈별 상세 분석 expander
            st.divider()
            for ph in phase_order:
                if ph not in phase_stats:
                    continue
                ps = phase_stats[ph]
                with st.expander(f"📌 {ph} 상세"):
                    cc1, cc2, cc3 = st.columns(3)
                    with cc1:
                        st.metric("척추각 평균", f"{ps['spine_angle']}°")
                    with cc2:
                        st.metric("어깨 회전", f"{ps['shoulder_rot']}°")
                    with cc3:
                        st.metric("골반 회전", f"{ps['hip_rot']}°")

    # ── TAB 3: 상세 데이터 ─────────────────────────────────────────────────
    with tab3:
        if "frame_data" not in st.session_state:
            st.info("📹 먼저 영상을 업로드하고 분석을 실행해주세요.")
        else:
            import pandas as pd
            df = pd.DataFrame(st.session_state.frame_data)

            st.markdown('<div class="section-title">관절 각도 시계열 차트</div>', unsafe_allow_html=True)

            ca, cb = st.columns(2)
            with ca:
                st.markdown("**척추각 (Spine Angle)**")
                st.line_chart(df[["time", "spine_angle"]].set_index("time"), color=["#f4c430"])
                st.markdown("**무릎 굴곡**")
                st.line_chart(df[["time", "left_knee", "right_knee"]].set_index("time"),
                              color=["#69f0ae", "#40916c"])
            with cb:
                st.markdown("**어깨 / 골반 회전 (X-Factor 꼬임)**")
                st.line_chart(df[["time", "shoulder_rotation", "hip_rotation"]].set_index("time"),
                              color=["#81d4fa", "#ce93d8"])
                st.markdown("**팔꿈치 각도**")
                st.line_chart(df[["time", "left_elbow", "right_elbow"]].set_index("time"),
                              color=["#ffab91", "#ff7043"])

            st.divider()
            st.markdown('<div class="section-title">페이즈별 평균값 테이블</div>', unsafe_allow_html=True)
            if "phase" in df.columns:
                tbl = df.groupby("phase")[
                    ["spine_angle", "shoulder_rotation", "hip_rotation", "left_knee", "right_knee", "left_elbow"]
                ].mean().round(1)
                st.dataframe(tbl, use_container_width=True)

            st.divider()
            with st.expander("📄 원시 프레임 데이터"):
                st.dataframe(df, use_container_width=True, height=300)
                csv = df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "⬇️ CSV 다운로드",
                    csv,
                    f"swing_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv"
                )

    # ── TAB 4: AI 코칭 리포트 (슬라이드 9) ────────────────────────────────
    with tab4:
        if "summary" not in st.session_state:
            st.info("📹 먼저 영상을 업로드하고 분석을 실행해주세요.")
        else:
            st.markdown(f'<div class="section-title">🤖 {provider} AI 코칭 리포트</div>', unsafe_allow_html=True)
            st.caption("슬라이드 9 알고리즘: 투어 프로 페르소나 + 구조화 JSON 데이터 → 원인-결과-해결책 피드백")

            if not api_key:
                link = {
                    "Gemini": "https://aistudio.google.com/app/apikey",
                    "Claude": "https://console.anthropic.com",
                    "GPT":    "https://platform.openai.com/api-keys",
                }[provider]
                st.warning(f"**{provider} API 키가 필요합니다.**\n\n👉 [{link}]({link}) 에서 발급 후 사이드바에 입력하세요.")
            else:
                if st.button(f"🧠 {provider} AI 코칭 피드백 생성", use_container_width=True):
                    with st.spinner(f"{provider} AI가 분석 중... (10~30초 소요)"):
                        try:
                            feedback = get_llm_feedback(
                                st.session_state.summary,
                                st.session_state.issues,
                                provider, api_key, model_name,
                                ref_db=ref_db,
                            )
                            st.session_state.ai_feedback = feedback
                            st.success("✅ 피드백 생성 완료!")
                        except Exception as e:
                            err = str(e)
                            if "API_KEY" in err or "api_key" in err.lower():
                                st.error("❌ API 키가 올바르지 않습니다. 사이드바에서 다시 확인해주세요.")
                            elif "quota" in err.lower() or "limit" in err.lower():
                                st.error("❌ API 사용량 한도 초과입니다. 잠시 후 다시 시도해주세요.")
                            elif "connect" in err.lower() or "timeout" in err.lower():
                                st.error("❌ 네트워크 연결 오류입니다. 인터넷 연결을 확인해주세요.")
                            else:
                                st.error(f"❌ 오류 발생: {err[:200]}")

            if "ai_feedback" in st.session_state:
                st.markdown(f"""
                <div class="feedback-box" style="font-size:0.96rem;line-height:2;white-space:pre-wrap">
                {st.session_state.ai_feedback}
                </div>
                """, unsafe_allow_html=True)

                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        "⬇️ 코칭 리포트 저장 (.txt)",
                        st.session_state.ai_feedback,
                        f"coaching_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        "text/plain"
                    )
                with col_dl2:
                    # JSON 요약 다운로드
                    json_data = json.dumps({
                        "summary": st.session_state.summary,
                        "score":   st.session_state.score,
                        "issues":  st.session_state.issues,
                        "feedback": st.session_state.ai_feedback,
                    }, ensure_ascii=False, indent=2)
                    st.download_button(
                        "⬇️ 분석 데이터 저장 (.json)",
                        json_data,
                        f"swing_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        "application/json"
                    )

            # API 없어도 볼 수 있는 수치 요약
            st.divider()
            with st.expander("📋 수치 요약 (API 없이 확인)"):
                s  = st.session_state.summary
                sc = st.session_state.score
                st.markdown(f"""
**종합 점수: {sc}점**

| 항목 | 측정값 | 기준 | 판정 |
|------|--------|------|------|
| 척추각 변화량 | {s['spine_angle_delta']}° | ≤ 5° | {'✅' if s['spine_angle_delta'] <= 5 else '⚠️' if s['spine_angle_delta'] <= 10 else '❌'} |
| X-Factor (꼬임) | {s['x_factor']}° | 35°~55° | {'✅' if 35 <= s['x_factor'] <= 55 else '⚠️'} |
| 어깨 최대 회전 | {s['shoulder_rotation_max']}° | 80°+ | {'✅' if s['shoulder_rotation_max'] >= 80 else '⚠️'} |
| 골반 최대 회전 | {s['hip_rotation_max']}° | — | — |
| 왼쪽 무릎 평균 | {s['left_knee_avg']}° | 130°~155° | {'✅' if 130 <= s['left_knee_avg'] <= 155 else '⚠️'} |
| 오른쪽 무릎 평균 | {s['right_knee_avg']}° | 130°~155° | {'✅' if 130 <= s['right_knee_avg'] <= 155 else '⚠️'} |
| 왼팔 평균 각도 | {s['left_elbow_avg']}° | ≥ 150° | {'✅' if s['left_elbow_avg'] >= 150 else '⚠️'} |
| 감지된 페이즈 수 | {len(s['phases_detected'])} / 7 | 5+ | {'✅' if len(s['phases_detected']) >= 5 else '⚠️'} |
                """)

    # ── TAB 5: 기준 학습 ────────────────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-title">📚 기준 데이터 학습</div>', unsafe_allow_html=True)
        st.caption("프로·아마추어 영상을 여러 개 분석해 기준 DB를 만들면, 점수 산정과 AI 피드백에 실제 데이터 기반 임계값이 적용됩니다.")

        # ── 현재 DB 현황 ──────────────────────────────────────────────────
        st.markdown('<div class="section-title">📊 현재 기준 DB 현황</div>', unsafe_allow_html=True)
        import pandas as pd

        def _show_db_stats(label, color):
            n = ref_db.get(label, {}).get("n", 0)
            if n == 0:
                st.markdown(f'<div class="feedback-box warning">⚠️ <b>{label}</b> 데이터 없음 — 영상을 추가해주세요.</div>',
                            unsafe_allow_html=True)
                return
            stats = get_ref_stats(ref_db, label)
            label_map = {
                "spine_angle_delta":     "척추각 변화량",
                "x_factor":              "X-Factor",
                "shoulder_rotation_max": "어깨 최대 회전",
                "left_elbow_top":        "왼팔(백스윙톱)",
                "left_knee_addr":        "왼무릎(어드레스)",
                "right_knee_addr":       "오른무릎(어드레스)",
            }
            rows = [{"지표": label_map.get(m, m),
                     "평균(°)": f"{v['mean']:.1f}",
                     "표준편차(°)": f"{v['std']:.1f}",
                     "샘플 수": v["n"]}
                    for m, v in stats.items()]
            st.markdown(f"**{label}** ({n}개 영상)")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        col_pro, col_am = st.columns(2)
        with col_pro:
            _show_db_stats("프로", "#f4c430")
        with col_am:
            _show_db_stats("아마추어", "#81d4fa")

        st.divider()

        # ── 배치 분석 업로드 ────────────────────────────────────────────
        st.markdown('<div class="section-title">➕ 영상 추가 분석</div>', unsafe_allow_html=True)

        learn_label = st.radio("영상 유형 선택", ["프로", "아마추어"], horizontal=True)
        learn_files = st.file_uploader(
            "MP4/MOV/AVI 파일 (여러 개 선택 가능)",
            type=["mp4", "mov", "avi", "m4v"],
            accept_multiple_files=True,
            key="learn_uploader",
        )

        if learn_files:
            st.info(f"**{len(learn_files)}개** 파일 선택됨 → **{learn_label}** 버킷에 추가됩니다.")
            if st.button("🔬 선택 영상 분석 & DB 저장", use_container_width=True):
                results_log = []
                prog = st.progress(0)
                for idx, f in enumerate(learn_files):
                    prog.progress(int(idx / len(learn_files) * 100), f"분석 중: {f.name}")
                    tmp_path = trim_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                            tmp.write(f.read())
                            tmp_path = tmp.name

                        info = get_video_info(tmp_path)
                        dur  = info["duration"]

                        # 30초 초과 영상은 스윙 구간 자동 탐지 후 트리밍
                        if dur > 30.0:
                            sw_start, sw_end = auto_detect_swing_window(tmp_path)
                            trim_path = trim_video(tmp_path, sw_start, sw_end)
                            analyze_p = trim_path
                            trim_note = f" (자동 트리밍 {sw_start:.1f}s~{sw_end:.1f}s / 원본 {dur:.0f}s)"
                        else:
                            analyze_p = tmp_path
                            trim_note = ""

                        fd, _, _, fps_, pd_, es_ = process_video(analyze_p, sample_rate,
                                                                  analyze_path=analyze_p)
                        sm = compute_summary(fd)
                        update_ref_db(st.session_state.ref_db, learn_label, sm)
                        results_log.append(
                            f"✅ {f.name}{trim_note} — 척추각변화 {sm['spine_angle_delta']}° / "
                            f"X-Factor {sm['x_factor']}° / 어깨 {sm['shoulder_rotation_max']}°"
                        )
                    except Exception as e:
                        results_log.append(f"❌ {f.name} 오류: {str(e)[:80]}")
                    finally:
                        for p in [tmp_path, trim_path]:
                            if p and os.path.exists(p):
                                try: os.unlink(p)
                                except: pass
                prog.progress(100)
                save_ref_db(st.session_state.ref_db)
                ref_db = st.session_state.ref_db   # 갱신
                st.success(f"✅ {len(learn_files)}개 영상 분석 완료 — DB 저장됨")
                for r in results_log:
                    st.markdown(r)
                st.rerun()

        st.divider()

        # ── DB 초기화 ───────────────────────────────────────────────────
        with st.expander("⚠️ DB 관리"):
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                if st.button("🗑️ 프로 데이터 초기화"):
                    st.session_state.ref_db.pop("프로", None)
                    save_ref_db(st.session_state.ref_db)
                    st.success("프로 데이터 초기화됨"); st.rerun()
            with col_r2:
                if st.button("🗑️ 아마추어 데이터 초기화"):
                    st.session_state.ref_db.pop("아마추어", None)
                    save_ref_db(st.session_state.ref_db)
                    st.success("아마추어 데이터 초기화됨"); st.rerun()
            with col_r3:
                if st.button("🗑️ 전체 DB 초기화"):
                    st.session_state.ref_db = {}
                    save_ref_db({})
                    st.success("전체 DB 초기화됨"); st.rerun()
            # DB JSON 다운로드
            st.download_button(
                "⬇️ DB 백업 (.json)",
                json.dumps(st.session_state.ref_db, ensure_ascii=False, indent=2),
                "reference_db.json",
                "application/json",
            )


if __name__ == "__main__":
    main()