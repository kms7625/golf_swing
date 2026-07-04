import json
from datetime import datetime

import streamlit as st

from analyzer.coach_llm import get_llm_feedback


def render(provider, model_name, api_key, ref_db):
    if "summary" not in st.session_state:
        st.info("📹 먼저 영상을 업로드하고 분석을 실행해주세요.")
    else:
        st.markdown(f'<div class="section-title">🤖 {provider} AI 코칭 리포트</div>', unsafe_allow_html=True)
        st.caption("슬라이드 9 알고리즘: 투어 프로 페르소나 + 구조화 JSON 데이터 → 원인-결과-해결책 피드백")

        if not api_key:
            link = {
                "Gemini": "https://aistudio.google.com/app/apikey",
                "Claude": "https://console.anthropic.com",
                "GPT":    "https://platform.openai.com/api-keys",
            }[provider]
            st.warning(f"**{provider} API 키가 필요합니다.**\n\n👉 [{link}]({link}) 에서 발급 후 사이드바에 입력하세요.")
        else:
            if st.button(f"🧠 {provider} AI 코칭 피드백 생성", use_container_width=True):
                with st.spinner(f"{provider} AI가 분석 중... (10~30초 소요)"):
                    try:
                        feedback = get_llm_feedback(
                            st.session_state.summary,
                            st.session_state.issues,
                            provider, api_key, model_name,
                            ref_db=ref_db,
                        )
                        st.session_state.ai_feedback = feedback
                        st.success("✅ 피드백 생성 완료!")
                    except Exception as e:
                        err = str(e)
                        if "API_KEY" in err or "api_key" in err.lower():
                            st.error("❌ API 키가 올바르지 않습니다. 사이드바에서 다시 확인해주세요.")
                        elif "quota" in err.lower() or "limit" in err.lower():
                            st.error("❌ API 사용량 한도 초과입니다. 잠시 후 다시 시도해주세요.")
                        elif "connect" in err.lower() or "timeout" in err.lower():
                            st.error("❌ 네트워크 연결 오류입니다. 인터넷 연결을 확인해주세요.")
                        else:
                            st.error(f"❌ 오류 발생: {err[:200]}")

        if "ai_feedback" in st.session_state:
            st.markdown(f"""
            <div class="feedback-box" style="font-size:0.96rem;line-height:2;white-space:pre-wrap">
            {st.session_state.ai_feedback}
            </div>
            """, unsafe_allow_html=True)

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    "⬇️ 코칭 리포트 저장 (.txt)",
                    st.session_state.ai_feedback,
                    f"coaching_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    "text/plain"
                )
            with col_dl2:
                # JSON 요약 다운로드
                json_data = json.dumps({
                    "summary": st.session_state.summary,
                    "score":   st.session_state.score,
                    "issues":  st.session_state.issues,
                    "feedback": st.session_state.ai_feedback,
                }, ensure_ascii=False, indent=2)
                st.download_button(
                    "⬇️ 분석 데이터 저장 (.json)",
                    json_data,
                    f"swing_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    "application/json"
                )

        # API 없어도 볼 수 있는 수치 요약
        st.divider()
        with st.expander("📋 수치 요약 (API 없이 확인)"):
            s  = st.session_state.summary
            sc = st.session_state.score
            st.markdown(f"""
**종합 점수: {sc}점**

| 항목 | 측정값 | 기준 | 판정 |
|------|--------|------|------|
| 척추각 변화량 | {s['spine_angle_delta']}° | ≤ 5° | {'✅' if s['spine_angle_delta'] <= 5 else '⚠️' if s['spine_angle_delta'] <= 10 else '❌'} |
| X-Factor (꼬임) | {s['x_factor']}° | 35°~55° | {'✅' if 35 <= s['x_factor'] <= 55 else '⚠️'} |
| 어깨 최대 회전 | {s['shoulder_rotation_max']}° | 80°+ | {'✅' if s['shoulder_rotation_max'] >= 80 else '⚠️'} |
| 골반 최대 회전 | {s['hip_rotation_max']}° | — | — |
| 왼쪽 무릎 평균 | {s['left_knee_avg']}° | 130°~155° | {'✅' if 130 <= s['left_knee_avg'] <= 155 else '⚠️'} |
| 오른쪽 무릎 평균 | {s['right_knee_avg']}° | 130°~155° | {'✅' if 130 <= s['right_knee_avg'] <= 155 else '⚠️'} |
| 왼팔 평균 각도 | {s['left_elbow_avg']}° | ≥ 150° | {'✅' if s['left_elbow_avg'] >= 150 else '⚠️'} |
| 감지된 페이즈 수 | {len(s['phases_detected'])} / 7 | 5+ | {'✅' if len(s['phases_detected']) >= 5 else '⚠️'} |
            """)
