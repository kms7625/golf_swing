# Codex 지시 — 학습 A안 보정: 앱 영상 회귀 수정 (feature/phase-train)

작업 위치: **`~/PycharmProjects/golf_swing_train`** (브랜치 feature/phase-train, HEAD 090dd9f). 근거: `docs/research/phase_train/REPORT.md` 5절.

## 0. 절대 규칙
| # | 규칙 |
|---|---|
| Z1 | `~/PycharmProjects/golf_swing`(발표용, dev 3bdf45d) 읽기 외 수정 금지. 8010 서버·ngrok 건드리지 않기. **중간발표(2026-10-15) 전까지 dev에 반영 없음** |
| Z2 | git 커밋 금지 — 커밋 묶음(200줄 이하) 제안만. 커밋 메시지에 Co-Authored-By 넣지 않음 |
| Z3 | 새 패키지 금지(NumPy·SciPy·OpenCV·MediaPipe). 포즈 추론은 Docker `golf-server:baseline`, 기존 캐시 `~/datasets/golfdb_pose/` 재사용 |
| Z4 | **split 4는 이미 한 번 평가에 사용됨.** 이번 보정은 split 1–3(fold 교차검증)과 앱 영상 7개로만 판단하고, split 4 재평가는 마지막 1회만 하되 "두 번째 노출"임을 보고서에 명시 |
| Z5 | 점수 임계값(A6)·지표 계산식 변경 금지. golf-code-change A1–A9 준수 |

## 1. 문제 (REPORT 5절)
| 영상 | 3bdf45d | A안(090dd9f) | 수동 참조 |
|---|---|---|---|
| pexels_8065880(시연 영상) Impact | 160 | **152** | 159–162 |
| pexels_6541855 Top | 118 | **127** | 112–117 |
| pexels_35546329 점수 | 55 | **45** | — |
| DTL Impact PCE(split 4) | 91.8% | 90.6% | — |
유력 원인: `impact_window_sec` 1.25→0.75, `plateau_ratio`·`smooth_sec` 변경. 원인을 파라미터별 단독 되돌림 실험으로 확인할 것.

## 2. 할 일
1. 앱 영상 7개 × 파라미터 단독 되돌림(each param back to 3bdf45d value) 표 — 어느 파라미터가 회귀를 만드는지 수치로
2. 회귀를 없애는 수정(파라미터 범위 제약·조건부 규칙 등)을 split 1–3 교차검증으로 선택. 목표: 앱 영상 7개가 3bdf45d보다 나빠지지 않음(Top/Impact 참조 범위 기준, 거부 0) **그리고** split 1–3 평균 PCE가 A안 대비 1%p 이상 떨어지지 않음
3. 마지막에 split 4 1회 평가(두 번째 노출 명시), Docker pytest 전부 통과, 샘플·스냅샷 재생성, web build·lint
4. 보고서 `docs/research/phase_train/REPORT_fix.md`: 원인 표, 선택 근거, 앱 영상 7개 전/후(3bdf45d·A안·수정안 3열), GolfDB fold·split4, 커밋 묶음 제안
