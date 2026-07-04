import streamlit as st

from analyzer.reference_db import load_ref_db
from ui.styles import inject_css, render_hero
from ui.sidebar import render_sidebar
from ui import tab_analysis, tab_phases, tab_data, tab_coaching, tab_learning

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI 골프 스윙 분석기",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()


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

    with tab1:
        tab_analysis.render(sample_rate, ref_db)

    with tab2:
        tab_phases.render()

    with tab3:
        tab_data.render()

    with tab4:
        tab_coaching.render(provider, model_name, api_key, ref_db)

    with tab5:
        tab_learning.render(sample_rate, ref_db)


if __name__ == "__main__":
    main()
