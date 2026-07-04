import os
import tempfile

import streamlit as st

from analyzer.pipeline import get_video_info, auto_detect_swing_window, trim_video, process_video
from analyzer.scoring import compute_summary
from analyzer.reference_db import update_ref_db, save_ref_db, get_ref_stats


def render(sample_rate, ref_db):
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
        import json
        st.download_button(
            "⬇️ DB 백업 (.json)",
            json.dumps(st.session_state.ref_db, ensure_ascii=False, indent=2),
            "reference_db.json",
            "application/json",
        )
