import numpy as np


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
