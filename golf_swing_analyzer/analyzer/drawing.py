import cv2
import numpy as np

from .mp_setup import mp_pose, mp_drawing

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
