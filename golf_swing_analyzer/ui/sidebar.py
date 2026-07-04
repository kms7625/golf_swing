import streamlit as st


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
