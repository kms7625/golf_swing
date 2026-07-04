import streamlit as st


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
