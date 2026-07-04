import streamlit as st

_CSS = """
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
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def render_hero():
    st.markdown("""
    <div class="hero-header">
      <div class="hero-title">⛳ AI 골프 스윙 분석기</div>
      <div class="hero-sub">MediaPipe 어깨폭 정규화 · 7단계 자동 세그먼테이션 · 투어 프로 LLM 코칭</div>
    </div>
    """, unsafe_allow_html=True)
