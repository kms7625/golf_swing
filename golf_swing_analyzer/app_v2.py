import streamlit as st
import cv2
import tempfile
import os
import json
import time
from datetime import datetime

from analyzer.reference_db import load_ref_db, save_ref_db, update_ref_db, get_ref_stats
from analyzer.pipeline import (
    get_video_info, trim_video, auto_detect_swing_window,
    get_thumbnail_frames, process_video,
)
from analyzer.scoring import compute_summary, compute_score
from analyzer.coach_llm import get_llm_feedback

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI 골프 스윙 분석기",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Space+Grotesk:wght@400;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

  .stApp { background: linear-gradient(135deg, #0f1f17 0%, #1a3a2a 100%); color: #e8f5e9; }

  .hero-header {
    text-align: center; padding: 2.5rem 1rem 1.5rem;
    border-bottom: 1px solid #2d6a4f44; margin-bottom: 2rem;
  }
  .hero-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 2.8rem;
    font-weight: 700; color: #f4c430; letter-spacing: -0.5px; margin: 0;
  }
  .hero-sub { font-size: 1rem; color: #a5d6a7; margin-top: 0.5rem; font-weight: 300; }

  .metric-card {
    background: #1e3d2e; border: 1px solid #2d6a4f; border-radius: 12px;
    padding: 1.2rem 1rem; text-align: center; transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: #f4c430; }
  .metric-label { font-size: 0.75rem; color: #a5d6a7; font-weight: 500; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 0.3rem; }
  .metric-value { font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; color: #f4c430; line-height: 1; }
  .metric-unit { font-size: 0.8rem; color: #81c784; }
  .metric-status-good { color: #69f0ae !important; }
  .metric-status-warn { color: #ffcc02 !important; }
  .metric-status-bad  { color: #ff5252 !important; }

  .score-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 1.5rem; }
  .score-ring {
    width: 140px; height: 140px; border-radius: 50%; border: 8px solid #2d6a4f;
    display: flex; align-items: center; justify-content: center; background: #0f1f17;
  }
  .score-number { font-family: 'Space Grotesk', sans-serif; font-size: 3rem; font-weight: 700; color: #f4c430; }

  .section-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600;
    color: #b7e4c7; border-left: 3px solid #f4c430; padding-left: 0.8rem;
    margin: 1.5rem 0 1rem; letter-spacing: 0.3px;
  }

  .feedback-box {
    background: #162b1f; border: 1px solid #2d6a4f; border-radius: 10px;
    padding: 1.4rem; margin: 0.8rem 0; line-height: 1.7; color: #c8e6c9; font-size: 0.95rem;
  }
  .feedback-box.critical { border-left: 4px solid #ff5252; }
  .feedback-box.warning  { border-left: 4px solid #ffcc02; }
  .feedback-box.good     { border-left: 4px solid #69f0ae; }

  .phase-chip {
    display: inline-block; background: #2d6a4f; color: #b7e4c7;
    padding: 0.25rem 0.8rem; border-radius: 20px; font-size: 0.78rem;
    font-weight: 600; letter-spacing: 0.5px; margin: 0.2rem;
  }
  .phase-chip.active { background: #f4c430; color: #0f1f17; }

  .stat-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.5rem 0; }

  .stProgress > div > div { background-color: #f4c430 !important; }

  [data-testid="stSidebar"] { background: #162b1f !important; border-right: 1px solid #2d6a4f; }
  [data-testid="stSidebar"] .stMarkdown p { color: #a5d6a7; }

  .stButton button {
    background: linear-gradient(135deg, #2d6a4f, #40916c) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; transition: all 0.2s !important;
  }
  .stButton button:hover {
    background: linear-gradient(135deg, #40916c, #52b788) !important;
    transform: translateY(-1px); box-shadow: 0 4px 12px #2d6a4f88 !important;
  }

  [data-testid="stFileUploader"] { border: 2px dashed #2d6a4f !important; border-radius: 12px !important; background: #162b1f !important; }

  hr { border-color: #2d6a4f44 !important; }

  .stTabs [data-baseweb="tab-list"] { background: #1e3d2e; border-radius: 8px; }
  .stTabs [data-baseweb="tab"] { color: #a5d6a7 !important; }
  .stTabs [aria-selected="true"] { color: #f4c430 !important; background: #2d6a4f; border-radius: 6px; }

  .streamlit-expanderHeader { color: #b7e4c7 !important; background: #1e3d2e !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: UI 컴포넌트
# ═══════════════════════════════════════════════════════════════════════════════

def render_hero():
    st.markdown("""
    <div class="hero-header">
      <div class="hero-title">⛳ AI 골프 스윙 분석기</div>
      <div class="hero-sub">MediaPipe 어깨폭 정규화 · 7단계 자동 세그먼테이션 · 투어 프로 LLM 코칭</div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label, value, unit="", status=""):
    sc = f"metric-status-{status}" if status else ""
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value {sc}">{value}<span class="metric-unit"> {unit}</span></div>
    </div>
    """, unsafe_allow_html=True)


def get_status(val, good_lo, good_hi, warn_lo=None, warn_hi=None):
    if good_lo <= val <= good_hi:   return "good"
    if warn_lo is not None and warn_lo <= val <= warn_hi: return "warn"
    return "bad"


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


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10: 메인 앱
# ═══════════════════════════════════════════════════════════════════════════════

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

    # ── TAB 1: 영상 업로드 & 분석 ──────────────────────────────────────────
    with tab1:
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

    # ── TAB 2: 7단계 페이즈 (슬라이드 6) ──────────────────────────────────
    with tab2:
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

    # ── TAB 3: 상세 데이터 ─────────────────────────────────────────────────
    with tab3:
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

    # ── TAB 4: AI 코칭 리포트 (슬라이드 9) ────────────────────────────────
    with tab4:
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

    # ── TAB 5: 기준 학습 ────────────────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-title">📚 기준 데이터 학습</div>', unsafe_allow_html=True)
        st.caption("프로·아마추어 영상을 여러 개 분석해 기준 DB를 만들면, 점수 산정과 AI 피드백에 실제 데이터 기반 임계값이 적용됩니다.")

        # ── 현재 DB 현황 ──────────────────────────────────────────────────
        st.markdown('<div class="section-title">📊 현재 기준 DB 현황</div>', unsafe_allow_html=True)
        import pandas as pd

        def _show_db_stats(label, color):
            n = ref_db.get(label, {}).get("n", 0)
            if n == 0:
                st.markdown(f'<div class="feedback-box warning">⚠️ <b>{label}</b> 데이터 없음 — 영상을 추가해주세요.</div>',
                            unsafe_allow_html=True)
                return
            stats = get_ref_stats(ref_db, label)
            label_map = {
                "spine_angle_delta":     "척추각 변화량",
                "x_factor":              "X-Factor",
                "shoulder_rotation_max": "어깨 최대 회전",
                "left_elbow_top":        "왼팔(백스윙톱)",
                "left_knee_addr":        "왼무릎(어드레스)",
                "right_knee_addr":       "오른무릎(어드레스)",
            }
            rows = [{"지표": label_map.get(m, m),
                     "평균(°)": f"{v['mean']:.1f}",
                     "표준편차(°)": f"{v['std']:.1f}",
                     "샘플 수": v["n"]}
                    for m, v in stats.items()]
            st.markdown(f"**{label}** ({n}개 영상)")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        col_pro, col_am = st.columns(2)
        with col_pro:
            _show_db_stats("프로", "#f4c430")
        with col_am:
            _show_db_stats("아마추어", "#81d4fa")

        st.divider()

        # ── 배치 분석 업로드 ────────────────────────────────────────────
        st.markdown('<div class="section-title">➕ 영상 추가 분석</div>', unsafe_allow_html=True)

        learn_label = st.radio("영상 유형 선택", ["프로", "아마추어"], horizontal=True)
        learn_files = st.file_uploader(
            "MP4/MOV/AVI 파일 (여러 개 선택 가능)",
            type=["mp4", "mov", "avi", "m4v"],
            accept_multiple_files=True,
            key="learn_uploader",
        )

        if learn_files:
            st.info(f"**{len(learn_files)}개** 파일 선택됨 → **{learn_label}** 버킷에 추가됩니다.")
            if st.button("🔬 선택 영상 분석 & DB 저장", use_container_width=True):
                results_log = []
                prog = st.progress(0)
                for idx, f in enumerate(learn_files):
                    prog.progress(int(idx / len(learn_files) * 100), f"분석 중: {f.name}")
                    tmp_path = trim_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                            tmp.write(f.read())
                            tmp_path = tmp.name

                        info = get_video_info(tmp_path)
                        dur  = info["duration"]

                        # 30초 초과 영상은 스윙 구간 자동 탐지 후 트리밍
                        if dur > 30.0:
                            sw_start, sw_end = auto_detect_swing_window(tmp_path)
                            trim_path = trim_video(tmp_path, sw_start, sw_end)
                            analyze_p = trim_path
                            trim_note = f" (자동 트리밍 {sw_start:.1f}s~{sw_end:.1f}s / 원본 {dur:.0f}s)"
                        else:
                            analyze_p = tmp_path
                            trim_note = ""

                        fd, _, _, fps_, pd_, es_ = process_video(analyze_p, sample_rate,
                                                                  analyze_path=analyze_p)
                        sm = compute_summary(fd)
                        update_ref_db(st.session_state.ref_db, learn_label, sm)
                        results_log.append(
                            f"✅ {f.name}{trim_note} — 척추각변화 {sm['spine_angle_delta']}° / "
                            f"X-Factor {sm['x_factor']}° / 어깨 {sm['shoulder_rotation_max']}°"
                        )
                    except Exception as e:
                        results_log.append(f"❌ {f.name} 오류: {str(e)[:80]}")
                    finally:
                        for p in [tmp_path, trim_path]:
                            if p and os.path.exists(p):
                                try: os.unlink(p)
                                except: pass
                prog.progress(100)
                save_ref_db(st.session_state.ref_db)
                ref_db = st.session_state.ref_db   # 갱신
                st.success(f"✅ {len(learn_files)}개 영상 분석 완료 — DB 저장됨")
                for r in results_log:
                    st.markdown(r)
                st.rerun()

        st.divider()

        # ── DB 초기화 ───────────────────────────────────────────────────
        with st.expander("⚠️ DB 관리"):
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                if st.button("🗑️ 프로 데이터 초기화"):
                    st.session_state.ref_db.pop("프로", None)
                    save_ref_db(st.session_state.ref_db)
                    st.success("프로 데이터 초기화됨"); st.rerun()
            with col_r2:
                if st.button("🗑️ 아마추어 데이터 초기화"):
                    st.session_state.ref_db.pop("아마추어", None)
                    save_ref_db(st.session_state.ref_db)
                    st.success("아마추어 데이터 초기화됨"); st.rerun()
            with col_r3:
                if st.button("🗑️ 전체 DB 초기화"):
                    st.session_state.ref_db = {}
                    save_ref_db({})
                    st.success("전체 DB 초기화됨"); st.rerun()
            # DB JSON 다운로드
            st.download_button(
                "⬇️ DB 백업 (.json)",
                json.dumps(st.session_state.ref_db, ensure_ascii=False, indent=2),
                "reference_db.json",
                "application/json",
            )


if __name__ == "__main__":
    main()