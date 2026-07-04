import streamlit as st


def render():
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
