import cv2
import numpy as np
import tempfile

from .mp_setup import mp_pose
from .geometry import (
    normalize_landmarks, calc_spine_angle, calc_shoulder_rotation,
    calc_hip_rotation, calc_knee_angle, calc_elbow_angle, visibility_ok,
    calc_world_rotation_headings
)
from .rotation import apply_world_rotations
from .smoothing import MovingAverageFilter
from .phase_detector import SwingPhaseDetector, SwingNotFoundError
from .phase_parameters import BASELINE_PARAMETERS
from .video_signal import SceneCuts, wrist_signal
from .video_clock import ANGLE_SMOOTH_SEC, analysis_step
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
    """Aspect-preserving scan, including short clips; select one complete cycle."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Keep at least ~15 observations/s even in long videos. A fixed total-frame
    # cap made brief real swings disappear from the long pro2 recording.
    step = max(1, int(fps / 15))
    # Keep pose-tracker context stable; calibration changes event boundaries,
    # while the established conservative scan determines the inference crop.
    det = SwingPhaseDetector(fps=fps/step, params=BASELINE_PARAMETERS)
    cuts = SceneCuts(fps)
    try:
        with mp_pose.Pose(min_detection_confidence=.3, min_tracking_confidence=.3,
                          model_complexity=1) as pose:
            for fi in range(total):
                ok, frame = cap.read()
                if not ok: break
                if cuts.update(frame, fi): det.cut_frames.append(fi)
                if fi % step: continue
                h,w = frame.shape[:2]
                scale = min(1.0, 320/max(h,w))
                small = cv2.resize(frame, (max(1,round(w*scale)), max(1,round(h*scale))))
                res = pose.process(cv2.cvtColor(small,cv2.COLOR_BGR2RGB))
                y,x,body = wrist_signal(res.pose_landmarks.landmark, small.shape[1], small.shape[0]) if res.pose_landmarks else (float('nan'),0,small.shape[0]*.25)
                det.update(fi//step,y,y,wrist_x=x,source_frame=fi,time_sec=fi/fps,body_scale=body)
    finally:
        cap.release()
    if not det.detect_all_phases(): raise SwingNotFoundError()
    cycle = det.selected_cycle
    lo,hi = cycle['segment']
    # Padding stays inside the same shot and never extends beyond impact+2 s.
    # Slow media needs more pre-roll than a real-time chip. Scale padding with
    # the observed descent, but retain the same <=3 s pre-top search ceiling.
    top_sec = det.wrist_times_sec[cycle['top']]
    descent_sec = det.wrist_times_sec[cycle['impact']]-top_sec
    pre_roll = max(padding_sec, min(1.5, 2*descent_sec))
    start = max(det.wrist_times_sec[lo], top_sec-3.0,
                det.wrist_times_sec[cycle['onset']]-pre_roll)
    end = min(total/fps, det.wrist_times_sec[cycle['end']]+step/fps)
    return round(start,3), round(end,3)


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


def process_video(video_path, sample_rate=3, analyze_path=None, source_start_sec=0.0,
                  rotation_method="legacy_2d"):
    # 기본은 2D(화면·점수). 3D 값은 x_factor_3d 등으로 계속 기록 — 정면 영상에서 3D가
    # 비현실적으로 작게 나오는 사례(시연 영상 5.1° vs 2D 36.9°)를 검증하기 전까지 점수에 쓰지 않는다.
    if rotation_method not in ("world_3d", "legacy_2d"):
        raise ValueError("rotation_method must be world_3d or legacy_2d")
    cap          = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0

    source_offset = int(source_start_sec * fps)

    # Source fps and analysis cadence are separate; retain source-frame IDs.
    # sample_rate remains a compatibility hint, as in the established pipeline.
    effective_sample = analysis_step(total_frames, fps)

    frame_data       = []
    annotated_frames = []   # source frame ID + RGB image
    trajectory_pts   = []
    phase_detector   = SwingPhaseDetector(fps=fps/effective_sample)
    cuts = SceneCuts(fps)
    signal_valid = 0
    sampled = 0
    angle_valid = 0
    ma_filter        = MovingAverageFilter(window_sec=ANGLE_SMOOTH_SEC)
    prev_metrics     = {}
    frame_idx        = 0
    local_idx        = 0

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

            if cuts.update(frame, frame_idx):
                phase_detector.cut_frames.append(source_offset + frame_idx)
                ma_filter = MovingAverageFilter(window_sec=ANGLE_SMOOTH_SEC)
                prev_metrics = {}

            if frame_idx % effective_sample != 0:
                frame_idx += 1
                continue

            sampled += 1
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

                wy, wx, body_scale = wrist_signal(lms, w, h)
                signal_valid += int(np.isfinite(wy))
                angle_valid += int(visible)
                phase_detector.update(local_idx, wy, wy, wrist_x=wx,
                                      source_frame=source_offset + frame_idx, time_sec=frame_idx/fps,
                                      body_scale=body_scale)

                if visible:
                    world = getattr(results, "pose_world_landmarks", None)
                    headings, world_reason = calc_world_rotation_headings(world.landmark if world else None)
                    raw = {
                        "frame":              source_offset + frame_idx,
                        "local_idx":          local_idx,
                        "time":               frame_idx / fps,
                        "spine_angle":        calc_spine_angle(norm),
                        "shoulder_rotation":  calc_shoulder_rotation(norm),
                        "hip_rotation":       calc_hip_rotation(norm),
                        "left_knee":          calc_knee_angle(norm, 'left'),
                        "right_knee":         calc_knee_angle(norm, 'right'),
                        "left_elbow":         calc_elbow_angle(norm, 'left'),
                        "right_elbow":        calc_elbow_angle(norm, 'right'),
                        "shoulder_width_px":  round(shoulder_width, 1),
                        "world_rotation_headings": headings,
                        "world_rotation_reason": world_reason,
                    }

                    # 슬라이드 8: 이동 평균 필터 적용
                    smoothed_keys = [
                        "spine_angle", "shoulder_rotation", "hip_rotation",
                        "left_knee",   "right_knee", "left_elbow", "right_elbow"
                    ]
                    metrics = raw.copy()
                    for key in smoothed_keys:
                        metrics[key] = ma_filter.smooth(key, raw[key], time_sec=frame_idx/fps)

                    # 페이즈는 나중에 후처리로 채움 (일단 임시)
                    metrics["phase"] = "분석중"
                    prev_metrics     = metrics.copy()
                    frame_data.append(metrics)

                    # 손목 궤적 포인트 수집 (원본 픽셀 좌표)
                    lw_px = (int(lms[15].x * w), int(lms[15].y * h))
                    trajectory_pts.append({
                        "pos":       lw_px,
                        "local_idx": local_idx,
                        "frame":     source_offset + frame_idx,
                        "phase":     "분석중"
                    })

                else:
                    # 슬라이드 8: 신뢰도 하락 → 이전 프레임 보간
                    if prev_metrics:
                        interp = prev_metrics.copy()
                        interp["frame"]     = source_offset + frame_idx
                        interp["time"]      = frame_idx / fps
                        interp["phase"]     = "보간"
                        interp["local_idx"] = local_idx
                        interp["world_rotation_headings"] = None
                        interp["world_rotation_reason"] = "interpolated_2d"
                        frame_data.append(interp)

                # Bounded preview resolution; source ID, never list position.
                annotated = frame.copy()
                if visible:
                    draw_swing_trajectory(annotated, trajectory_pts, metrics.get("phase", ""))
                    annotated = draw_skeleton_annotations(annotated, results, norm, metrics, w, h)
                # 해상도 축소 (720p → 480p급)
                ah, aw = annotated.shape[:2]
                if max(ah, aw) > 480:
                    scale = 480 / max(ah, aw)
                    annotated = cv2.resize(annotated, (int(aw * scale), int(ah * scale)))
                annotated_frames.append({"frame": source_offset + frame_idx, "local_idx": local_idx, "image": cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)})
                local_idx += 1
            else:
                phase_detector.update(None, float('nan'), float('nan'), source_frame=source_offset + frame_idx,
                                      time_sec=frame_idx/fps, body_scale=h*.25)

            frame_idx += 1

    cap.release()

    # ── 슬라이드 6: 전체 시계열로 7단계 페이즈 후처리 ──────────────────────
    available = {f['local_idx'] for f in frame_data}
    inverse = {v: k for k, v in phase_detector.local_to_hist.items()}
    phase_detector.metric_available_history = [
        inverse.get(i) in available for i in range(len(phase_detector.wrist_y_history))]
    if not phase_detector.detect_all_phases():
        raise SwingNotFoundError()
    phase_detector.quality = {"sampled": sampled, "wrist_valid": signal_valid,
                              "angle_valid": angle_valid, "wrist_valid_ratio": signal_valid/max(sampled,1)}
    for i, fd in enumerate(frame_data):
        li = fd["local_idx"]
        fd["phase"] = phase_detector.get_phase_for_frame(li)
    for i, tp in enumerate(trajectory_pts):
        li = tp["local_idx"]
        tp["phase"] = phase_detector.get_phase_for_frame(li)

    # Only this one cycle reaches metrics/scoring; keep source IDs unchanged.
    frame_data = [f for f in frame_data if f["phase"] in phase_detector.phase_boundaries]
    if not frame_data:
        raise SwingNotFoundError()
    apply_world_rotations(frame_data, phase_detector.phase_boundaries_frames["백스윙 톱"][0],
                          method=rotation_method)
    for entry in annotated_frames:
        entry["phase"] = phase_detector.get_phase_for_frame(entry["local_idx"])
    annotated_frames = [f for f in annotated_frames if f["phase"] in phase_detector.phase_boundaries]
    trajectory_pts = [f for f in trajectory_pts if f["phase"] in phase_detector.phase_boundaries]
    return frame_data, annotated_frames, trajectory_pts, fps, phase_detector, effective_sample
