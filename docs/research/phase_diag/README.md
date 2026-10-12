# 7단계 진단 산출물

[REPORT.md](REPORT.md)가 최종 보고서다. [LITERATURE.md](LITERATURE.md)는 실제 열어 확인한 문헌/라이선스 기록이며 보고서에도 포함했다. 앱 코드 변경 없이 기존 함수를 import하거나 진단용 메모리 복사본으로 실행했다.

```bash
cd ~/PycharmProjects/golf_swing
.venv/bin/python tools/diag_phase/diagnose.py all
.venv/bin/python tools/diag_phase/visual_match.py
.venv/bin/python tools/diag_phase/summarize.py
.venv/bin/python tools/diag_phase/refresh_figures.py
.venv/bin/python tools/diag_phase/build_report.py
.venv/bin/python tools/diag_phase/validate.py
```

`diagnose.py`는 Mac에서 기존 `golf-server:baseline`의 Docker CPU 추론을 자동 실행한다. 이미지 빌드/패키지 설치/모델 다운로드를 하지 않는다. 기존 `.venv`의 NumPy/OpenCV/MediaPipe/Pillow/Matplotlib 및 기존 Docker 이미지가 필요하다. 모든 데이터셋은 `~/datasets`에 이미 존재해야 한다. 이번 Mac MediaPipe는 OpenGL 초기화가 실패하여 수치는 전부 Docker 기준이다.

중간 JSON이 존재하면 해당 추론을 건너뛴다. 독립 검증을 위해 처음부터 계산할 때는 기존 결과 폴더를 따로 보관한 후 재실행할 **해당 실험 JSON**을 지우고 실행한다. `manual_reference.json`, `windows.json`은 평가 입력이므로 남긴다. 코드나 환경이 바뀌면 기존 캐시와 혼합하지 않는다. 각 task 단독 실행도 가능하다:

```bash
.venv/bin/python tools/diag_phase/diagnose.py inventory
.venv/bin/python tools/diag_phase/diagnose.py auto
.venv/bin/python tools/diag_phase/diagnose.py samples --names il-ban pro pro2
.venv/bin/python tools/diag_phase/diagnose.py golfdb --limit 50
.venv/bin/python tools/diag_phase/diagnose.py controls
.venv/bin/python tools/diag_phase/diagnose.py snapshots
.venv/bin/python tools/diag_phase/diagnose.py snapshot_rates
.venv/bin/python tools/diag_phase/diagnose.py s2case
.venv/bin/python tools/diag_phase/diagnose.py s2_candidates
```

`all`은 inventory→auto→samples→snapshots→controls→S2 탐색→snapshot_rates→GolfDB를 실행한다. 처음부터 포즈 추론을 하면 수십 분 걸릴 수 있다. `summarize.py`/그림/보고서/감사는 위 순서로 별도 실행한다. 문헌 확인은 자동 재검색하지 않으며 2026-10-12의 확인 기록이다.

| 파일 | 내용·좌표 기준 |
|---|---|
| `data/environment_*.json` | 환경/패키지 버전, 앱 핵심 소스 SHA256 |
| `data/manual_reference.json` | 7개 비GolfDB 영상의 수동 탐색 참조/불확실성 범위. 원본 프레임 0-based |
| `data/windows.json` | H2 원본 interval. 프로/프로2만 지정, 나머지는 전체 원본 |
| `data/*_s1/s2/s3/sadaptive.json`, `*_trace.csv` | 새 포즈 추론, 가시도·경계·대표 매핑. frame은 interval 내, source_frame은 원본 기준 |
| `data/*_snapshot.json`, `il-ban_snapshot_rate*.json` | 실제 trim 재인코딩 입력. frame/source_frame은 trim 기준; `source_offset_frame`을 더하면 원본 |
| `data/s2_screenshot_matches.json` | 스크린샷 7장과 원본 최근접 후보. 확정 세션 프레임 아님 |
| `data/s2_candidate_*.json`, `s2_reconstruction*.json` | 원래 세션 trim을 모르는 상태에서 실시한 탐색. `source_offset_frame` 있는 파일만 번호에 offset 추가. 7.6초 시작에서 6장 오류 재현 |
| `data/sample_boundaries.csv`, `representative_mapping.csv`, `pose_metrics.csv` | 비교/집계 테이블. boundary frame/초 및 `*_absolute_frame`은 원본 기준 |
| `data/golfdb_selection.json`, `golfdb/{id}_s{step}.json` | 동일한 50개 선정 정보, 150회 추론 숫자 원자료. 영상·프레임 이미지 없음 |
| `data/golfdb_results.json`, `golfdb_summary.*` | GT·허용오차·PCE·다운스윙 관측 수 |
| `data/golfdb_ablations.csv`, `golfdb_ablation_summary.json` | 30fps 포즈 고정 후 솎기/시간 스무딩/선형 결측 채우기 탐색; RIFE 실험 아님 |
| `data/auto_window_comparison.csv`, `auto_*.json` | 7개 원본 × 현행/비율 보존, 초 단위 자동/수동 창 비교 |
| `data/control_*.json`, `control_summary.csv` | 실제 정지·0/1/3초 양끝 패딩 클립. 임시 영상은 실행 후 삭제 |
| `data/signal_invariants.json` | 좌우 교환 평균 불변, 상수 신호 7경계/역전, S1 컷 점프 |
| `figures/*_signals.png` | 좌/우/평균 Y, visibility, pose/gate; 실선 원본 시간 매핑, 점선 현재 UI 시간. refresh 후 snapshot/candidate도 원본 초 사용 |
| `figures/*_representatives.png` | 위 현행 이미지 선택, 아래 local_idx 조회. **단계 검출 자체를 고친 결과가 아님**. refresh 후 원본 f 사용 |
| `figures/*_snapshot_annotated.png` | 실제 imported process_video의 그려진 이미지. HUD 시간은 앱의 trim/local 규칙 그대로 |
| `figures/*_manual.png`, `*_overview.png` | 비GolfDB 원본 contact sheet. 수동 판단의 검토 근거 |
| `data/validation.json`, `git_status_final.txt` | 산출물/50개 paired/소스 불변/허용 경로 감사 |

판독 주의: representative Impact는 경계 시작과 inclusive 라벨 겹침으로 한 샘플 차이 날 수 있다. phase_boundaries의 숫자는 원본 frame이 아닌 **valid wrist history index**다. `local_idx`는 pose가 있는 샘플 순번이고, `rep_i`는 frame_data 순번이다. 이번 진단의 가장 중요한 구별이다.

S2는 원본 영상과 최근접 원본 장면을 확인하고 같은 결함을 재현했으나 원래 UI 선택 구간·서버 환경·응답 JSON은 제공되지 않았다. 이 세션 전체를 완전 재현했다고 주장하지 않는다. 시작 시 있던 G1 밖 `.DS_Store`와 `docs/research/phase-segmentation-diagnosis-prompt.md`도 보존했다.
