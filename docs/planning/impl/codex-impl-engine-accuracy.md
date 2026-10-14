# Codex 구현 지시 — 분석 엔진 3건: 어드레스·피니시 정확도 / 연습 스윙 구분 / 60fps 지원 (브랜치 `feature/engine-accuracy`, 기준 `release/2026-10-14` b8eace6)

## 0. 배경
- 작업 폴더는 이 worktree(`~/PycharmProjects/golf_swing_engine`)만. **`~/PycharmProjects/golf_swing`(중간발표 시연용, 8010·4173·ngrok 실행 중)과 다른 worktree는 쓰지 않는다**. 8010·8011·4173·5173 포트 사용 금지
- 현재 상태: 단계 분할 회귀 수정(`docs/research/phase_train/REPORT_fix.md`) 적용, X-Factor 점수·화면은 2D(3D는 기록만). GolfDB 기준 Address·Finish 적중률이 낮다(0~20%대 — 보고서 수치로 재확인)
- 이전 실험 도구: `tools/phase_train/`(cache·replay·apps·fix_*), 데이터 `/Users/mose/datasets/golfdb`, `/Users/mose/datasets/golfdb_pose`, 앱 영상 `/Users/mose/datasets/test_videos/pexels_*.mp4` + 레포 `golf_swing_analyzer/video/{일반,프로,프로2}.mp4`

## 1. 먼저 읽을 것
- `docs/research/phase_train/REPORT.md`, `REPORT_fix.md`, `PROTOCOL_fix.md`
- `docs/research/phase_diag/REPORT.md`, `AFTER.md`
- `golf_swing_analyzer/analyzer/phase_detector.py`, `phase_parameters.py`, `pipeline.py`, `video_signal.py`

## 2. 규칙 (위반 시 실패)
| # | 규칙 |
|---|---|
| E1 | 수정 가능: `golf_swing_analyzer/analyzer/**`, `tools/**`, `tests/**`(새 테스트 추가), `docs/research/**`, `web/public/samples/*`·`tests/snapshots/*`(아래 E6 절차로만). `server/`·`web/src/` 변경은 E7 경우만 |
| E2 | **GolfDB split 4는 사용 금지**(이미 2회 노출). 튜닝·판정은 split 1~3 교차검증(fold별)과 앱 영상 7개로만 |
| E3 | 비악화 게이트: 앱 영상 7개의 기존 결과(시연 영상 8065880 임팩트 158~159·점수 72, 6541855 톱 118 등 `REPORT_fix.md` 기준)가 나빠지면 그 변경은 채택하지 않는다. split 1~3 평균 PCE가 1%p 넘게 떨어져도 불채택 |
| E4 | 의존성 추가 금지. 새 학습 모델(신경망) 도입 금지 — 규칙·신호처리·파라미터 수준에서 |
| E5 | 수치를 지어내지 않는다. 모든 수치는 실행 산출물(JSON/로그) 경로와 함께 |
| E6 | 결과가 바뀌면 샘플·스냅샷은 Docker `golf-server:baseline`에서 재생성하고, 바뀐 이유를 보고서에 기록 |
| E7 | 연습 스윙 구분 결과를 사용자에게 알려야 하면 서버 응답에 **필드 추가만**(기존 필드 의미 변경 금지) + `web/src`에 안내 한 줄(i18n KO·EN). 그 외 웹 변경 금지 |
| E8 | git 커밋하지 않는다. 보고에 커밋 묶음 제안(묶음당 200줄 이하) |

## 3. 작업
1. **어드레스·피니시 정확도:** 현재 split 1~3 기준 Address·Finish PCE를 먼저 재측정해 기준선으로 기록 → 원인 분석(경계 정의 차이: GolfDB Address/Finish 이벤트 정의 vs 앱의 구간 경계 정의 포함) → 개선안 적용 → fold별 결과·앱 영상 비악화 확인. 정의 차이 때문에 수치 비교 자체가 부적절하면 그 사실과 근거를 보고
2. **연습 스윙 vs 실제 샷 구분:** 영상만으로 공 타격 여부를 판별할 수 있는지 조사(예: 임팩트 직후 공 위치 영역의 변화, 클럽-공 접촉 후 객체 이동). 앱 영상 7개와 GolfDB에서 판별 가능성을 실측. **신뢰도가 확인된 경우에만** 서버 응답에 `shot_type: "practice" | "shot" | "unknown"` + 근거 수치 추가. 판별 불가·불안정이면 구현하지 말고 보고서에 실측 근거와 함께 "불가"로
3. **60fps 지원:** 현재 `sample_rate`(프레임 간격)와 시간 기반 창이 30fps를 가정하는 곳을 전수 확인 → 시간 기준(초)으로 일관되게. 60fps 테스트 영상이 없으면 `ffmpeg`로 앱 영상을 60fps로 변환(프레임 복제/보간 각각)해 30fps 원본과 단계 경계(초 단위)·점수가 같은지 비교. 실제 60fps 촬영본 검증은 "미확인"으로

## 4. 완료 기준 (직접 실행)
1. Docker pytest 전부 통과:
   `docker run --rm --platform linux/amd64 --network none -e PYTHONDONTWRITEBYTECODE=1 -e PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 -e PYTHONPATH=/testdeps -v "$PWD":/work:ro -v /private/tmp/phase_testdeps:/testdeps:ro -w /work golf-server:baseline python -m pytest -p no:cacheprovider -q`
2. 각 작업에 대한 새 테스트 추가(작업 2를 "불가"로 판정했다면 제외)
3. E3 비악화 표(앱 영상 7개 × 기존/변경, split 1~3 fold별 PCE)
4. `cd web && npm run build` exit 0 (E7로 웹을 건드린 경우)
5. `node tests/phase_web_compat.mjs` PASS
6. `git status --short` 변경이 E1 경로 안

## 5. 보고 (`docs/research/engine_accuracy/REPORT.md`)
작업별: 기준선 → 원인 → 변경 → 결과(수치+산출물 경로) → 채택/불채택, 완료 기준 1~6 PASS/FAIL/미확인, 남은 한계, 커밋 묶음 제안
