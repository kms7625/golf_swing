import cv2
import numpy as np
import tempfile

from .mp_setup import mp_pose
from .geometry import (
    normalize_landmarks, calc_spine_angle, calc_shoulder_rotation,
    calc_hip_rotation, calc_knee_angle, calc_elbow_angle, visibility_ok
)
from .smoothing import MovingAverageFilter
from .phase_detector import SwingPhaseDetector
from .drawing import draw_swing_trajectory, draw_skeleton_annotations


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


def auto_detect_swing_window(video_path, padding_sec=1.0):
    """
    전체 영상에서 가장 완전한 단일 스윙 사이클을 감지해 시작/끝 시간을 반환.

    알고리즘: 고정 창 슬라이딩이 아닌 스윙 사이클 단위 탐색
      1. 빠른 스캔으로 손목 Y 시계열 추출
      2. 로컬 최솟값(백스윙 톱) 후보 탐색 + 근접 최솟값 병합
      3. 각 후보에서 임팩트(이후 4초 내 최댓값)까지의 상승 진폭 계산
      4. 진폭 최대 스윙 1개 선택 → 어드레스 시작~피니시 끝 반환
    여러 스윙이 있어도 가장 완전한 1개 사이클만 추출.
    """
    cap   = cv2.VideoCapture(video_path)
    fps   = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur   = total / fps

    # 8초 이하면 이미 스윙 구간만 있는 것으로 간주 → 전체 반환
    if dur <= 8.0:
        cap.release()
        return 0.0, round(dur, 1)

    # 빠른 스캔: 최대 400프레임만 추출
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
                    wrist_ys.append((lms[15].y + lms[16].y) / 2 * 180)
                    times.append(fi / fps)
            fi += 1
    cap.release()

    if len(wrist_ys) < 15:
        return 0.0, round(dur, 1)

    wy  = np.array(wrist_ys, dtype=float)
    n   = len(wy)
    sps = n / dur   # 초당 샘플 수

    # 경계 인식 스무딩 (0.5초 창)
    k    = max(3, int(sps * 0.5))
    half = k // 2
    wy_s = np.array([np.mean(wy[max(0, i-half):min(n, i+half+1)]) for i in range(n)])

    y_range = float(wy_s.max() - wy_s.min()) + 1e-8
    min_amp = y_range * 0.25   # 유효 스윙 최소 진폭 (전체 범위의 25%)

    s15 = max(2, int(sps * 1.5))   # 1.5초 (로컬 최솟값 탐색 창)
    s4  = max(3, int(sps * 4.0))   # 4초  (임팩트 탐색 창)
    s5  = max(3, int(sps * 5.0))   # 5초  (어드레스 역방향 탐색 창)
    s2p = max(2, int(sps * 2.0))   # 2초  (피니시 여유)

    # ── 1. 로컬 최솟값 탐색 (백스윙 톱 후보) ──────────────────────────────
    raw_mins = [i for i in range(s15, n - s15)
                if wy_s[i] <= wy_s[max(0, i-s15):min(n, i+s15+1)].min() + y_range * 0.02]

    # ── 2. 근접 최솟값 병합 (1.5초 내 가장 깊은 것만 유지) ────────────────
    merged, seen = [], set()
    for idx in raw_mins:
        if idx in seen:
            continue
        group = [j for j in raw_mins if abs(j - idx) <= s15]
        best  = min(group, key=lambda x: wy_s[x])
        if not merged or merged[-1] != best:
            merged.append(best)
        for j in group:
            seen.add(j)

    if not merged:
        return 0.0, round(dur, 1)

    # ── 3. 각 백스윙 톱 후보에서 스윙 사이클 평가 ────────────────────────
    candidates = []
    for top_i in merged:
        # 임팩트: 이후 4초 내 최댓값
        post = wy_s[top_i: min(n, top_i + s4)]
        if len(post) < 2:
            continue
        impact_i = top_i + int(np.argmax(post))
        rise     = float(wy_s[impact_i] - wy_s[top_i])

        if rise < min_amp:
            continue

        # 어드레스 시작: 이전 5초에서 Y ≥ (top + 75% rise) 인 마지막 지점
        addr_thresh = float(wy_s[top_i] + rise * 0.75)
        start_i     = max(0, top_i - s5)
        for j in range(top_i - 1, max(-1, top_i - s5 - 1), -1):
            if wy_s[j] >= addr_thresh:
                start_i = j
                break

        # 피니시 끝: 임팩트 이후 2초
        end_i = min(n - 1, impact_i + s2p)
        candidates.append((rise, start_i, end_i))

    if not candidates:
        return 0.0, round(dur, 1)

    # ── 4. 임팩트 진폭 최대 스윙 선택 ────────────────────────────────────
    candidates.sort(key=lambda x: x[0], reverse=True)
    _, start_i, end_i = candidates[0]

    start_sec = max(0.0, times[start_i] - padding_sec)
    end_sec   = min(dur,  times[end_i]  + padding_sec)
    return round(start_sec, 1), round(end_sec, 1)


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
