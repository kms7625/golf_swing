from datetime import datetime

import streamlit as st


def render():
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
