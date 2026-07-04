import time
import tempfile

import cv2
import streamlit as st

from analyzer.pipeline import get_video_info, trim_video, get_thumbnail_frames, process_video
from analyzer.scoring import compute_summary, compute_score
from analyzer.reference_db import update_ref_db, save_ref_db
from ui.components import render_metric_card, get_status


def render(sample_rate, ref_db):
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

        # ── 기준 DB 즉시 추가 ────────────────────────────────────────────
        if "summary" in st.session_state:
            st.divider()
            st.markdown('<div class="section-title">📚 이 분석 결과를 기준 DB에 추가</div>', unsafe_allow_html=True)
            col_lbl, col_btn = st.columns([2, 1])
            with col_lbl:
                db_label = st.radio(
                    "유형 선택",
                    ["프로", "아마추어"],
                    horizontal=True,
                    key="tab1_db_label",
                )
            with col_btn:
                if st.button("➕ 기준 DB에 추가", use_container_width=True, key="tab1_db_add"):
                    update_ref_db(st.session_state.ref_db, db_label,
                                  st.session_state.summary)
                    save_ref_db(st.session_state.ref_db)
                    n = st.session_state.ref_db.get(db_label, {}).get("n", 0)
                    st.success(f"✅ {db_label} DB에 추가됨 (누적 {n}개)")

    # 임시 파일은 세션 종료 시 자동 정리됨
