import numpy as np

from .reference_db import get_ref_stats


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
