# Codex 구현 지시 — 7단계 분할·자동 구간 수정 (브랜치 `feature/cobalt-ui`)

작성 2026-10-12 · 근거 `docs/research/phase_diag/REPORT.md`(원인 순위·해결책 A–G) · 사용자 결정: **중간발표(10-15) 전에 전부 수정**
안전장치: 이전 동작 버전 = 태그 `midterm-safe`, 현재 브랜치 HEAD `21c7d51`. 끝나면 Claude가 독립 검증·커밋.

## 1. 먼저 읽을 것
- `docs/research/phase_diag/REPORT.md` 전체, `docs/research/phase_diag/data/manual_reference.json`(7개 영상 수동 참조 Top/Impact 범위)
- `.claude/skills/golf-code-change/SKILL.md`(A1–A9, B 검증) — 이번 작업은 **A7·A8·A9를 의도적으로 변경**한다(사용자 승인). 나머지 A1–A6은 그대로 지킨다
- `CLAUDE.md`, `tools/diag_phase/README.md`(Docker 실행 방법 — Mac `.venv` MediaPipe는 이 환경에서 실패했으므로 포즈 수치는 `golf-server:baseline` Docker로)

## 2. 구현 항목 (REPORT 3절 후보 기호)
| # | 내용 | 완료 판정 |
|---|---|---|
| P1 (A) | 대표 장면 이미지를 **원본 프레임 기준**으로 조회. `frame_data` 각 항목과 `annotated_frames` 각 항목에 원본 프레임 번호를 붙이고, 대표 장면은 그 번호로 매칭. 규칙(임팩트=첫, 다운스윙=85%, 나머지=중간)은 유지. 복제 3곳(`server/serialization.py`, `golf_swing_analyzer/ui/tab_analysis.py`, `CLAUDE.md` 설명) 동시 수정 | 모든 단계의 대표 이미지 원본 프레임이 그 단계 경계(원본 프레임) 안에 있다 — 테스트로 assert |
| P2 (B) | 단계 경계를 **원본 시간(초)** 으로도 응답: 예 `phase_boundaries_sec: {단계: [시작초, 끝초]}`(분석 구간 기준). 웹 `SwingReplay`·파형은 이 값이 있으면 사용, 없으면(옛 저장 JSON) 기존 근사로 폴백. `types.ts`에 선택 필드로 추가 | 빨간 셔츠(`pexels_35546329`) 전체 분석에서 타임라인 임팩트 위치가 실제 시각(약 11.3초)과 0.2초 이내 |
| P3 (C) | **스윙 존재·순서 검증**: 손목 상승 폭이 몸 크기 기준(예: 어깨폭 또는 영상 높이 비율, 근거를 주석에) 미만이거나, 경계가 역전/빈 단계면 "스윙을 찾지 못함"으로 처리. 서버는 422 + 한국어 메시지("스윙 동작을 찾지 못했어요. 구간을 다시 선택해 주세요."), 점수·코칭 생성 안 함. 웹은 이 메시지를 결과 대신 표시하고 구간 선택으로 돌아갈 버튼 제공 | 정지 클립(일반 f30–65, 1.2초 정지 클립)과 상수 입력 → 422/거부. 실제 스윙 7개 영상은 거부되지 않음 |
| P4 (D) | **스윙 한 번만 분석**: (1) 장면 전환(컷) 검출 — 연속 프레임 차이(예: 축소 회색조 히스토그램/평균 절대차)로 컷 지점을 찾아 구간을 컷에서 끊는다 (2) 단계 검출 탐색 창을 **영상 길이 비율이 아니라 시간(초)·fps 기준**으로: 가장 큰 톱→임팩트 하강 사이클 하나를 고르고, 어드레스는 톱 이전 최대 약 3초, 임팩트는 톱 이후 약 1초 이내, 피니시는 임팩트 이후 약 2초 이내. 수치는 문헌(다운스윙 약 0.3초, REPORT L4) 근거를 주석으로. 임팩트는 그 창 안의 argmax(wy) 유지(A2) | 일반·프로·프로2: 경계가 첫 완전 스윙 안에 있음(일반 Top f79–87·Impact f87–93 원본 기준, 프로 Top f299–307·Impact f311–317 ±3) |
| P5 (F, A9) | 분석 샘플링: **선택 구간은 원본 fps로 매 프레임 분석**(상한은 메모리·시간 실측 후 결정, 예 30fps 기준 20초=600프레임까지 매 프레임, 그 이상만 간격). 스무딩 창 `k`를 fps 기준 시간(예 약 0.1–0.15초)으로 | 일반 1.5–9.7초 구간 Impact 경계 f90±3. 10초 30fps 구간 분석 시간 측정값 보고(현재 대비 배율) |
| P6 (G) | 손목 신호 품질과 6관절 각도 품질 분리: 단계 검출용 손목 y는 **손목 가시도 기준**으로 기록, 6관절 gate는 각도 지표에만. 짧은 결측(≤0.2초)만 시간 기반 보간, 긴 결측은 채우지 않음 | 빨간 셔츠·어려운 영상의 손목 신호 유효율 보고(현재 68.2%/38.6% 대비) |
| P7 (E + 자동 구간) | `auto_detect_swing_window`: 종횡비 유지 축소, 8초 이하도 감지 수행(스윙 1회만 있으면 그 구간), 컷 경계 반영, 실제 공 타격 스윙을 연습 스윙보다 우선(진폭·속도 기준, 근거 주석) | 7개 영상 자동 창 vs `manual_reference.json` IoU 표 — 현재(REPORT 10절) 대비 악화 0건, `pexels_34883764` IoU > 0 목표(미달 시 이유 보고) |

## 3. 규칙 (위반 시 실패)
| # | 규칙 |
|---|---|
| R1 | 수정 허용: `golf_swing_analyzer/analyzer/`, `golf_swing_analyzer/ui/tab_analysis.py`, `server/`, `web/src/`, `tests/`(새 테스트 추가·스냅샷 재생성만), `web/public/samples/*.json`(재생성만), `CLAUDE.md`(A8 설명), `.claude/skills/golf-code-change/SKILL.md`(A7·A8·A9 문구를 새 동작에 맞게) |
| R2 | **점수 판정 기준(A6 임계값)·지표 계산식 변경 금지.** 점수 숫자가 바뀌는 것은 구간이 바뀐 결과로만 허용하고, 영상별 전/후 점수를 표로 보고 |
| R3 | 기존 테스트를 지우거나 스킵하지 않는다. 스냅샷은 `python tests/regen_snapshot.py`로만 재생성하고 전/후 차이를 보고 |
| R4 | 새 패키지 금지(OpenCV·NumPy·MediaPipe로). git 커밋 금지 — 대신 **커밋 묶음 제안(묶음당 200줄 이하)** |
| R5 | 임계값을 GolfDB로 정할 때 **split 1–3에서만 정하고 split 4로 보고**(같은 데이터로 맞춘 수치를 성능이라 하지 않음). GolfDB 영상은 레포에 넣지 않음(CC BY-NC) |
| R6 | 포즈가 들어간 수치는 Docker `golf-server:baseline`(linux/amd64)에서. 환경을 결과에 명시 |
| R7 | 웹: 새 문구 i18n KO·EN 동시, 빌드·린트 통과, 기존 저장 기록(옛 JSON)도 화면이 깨지지 않음 |

## 4. 완료 기준 (직접 실행해 결과를 보고서에 붙일 것)
1. Docker에서 `python -m pytest` 전부 통과(새 테스트 포함: P1 대표 이미지 범위, P3 정지 거부, P4 컷 분리)
2. `cd web && npm run build && npm run lint` exit 0
3. 7개 영상(일반·프로·프로2·pexels 4개) 표: 자동 창, Top/Impact 원본 프레임 vs 수동 참조, 대표 장면 7장 원본 프레임, 점수 전/후, 분석 시간 전/후
4. GolfDB split 4 face-on·DTL 각 25개 이상(가능하면 전부) PCE: 수정 전 코드 vs 수정 후(같은 Docker) — Address/Top/Impact/Finish
5. 대표 장면 비교 그림(수정 전/후)을 `docs/research/phase_diag/after/`에 저장
6. `web/public/samples/*.json` 재생성(일반·프로·프로2), 샘플 화면에서 7장이 각 단계 자세인지 그림으로 확인

## 5. 보고 (`docs/research/phase_diag/AFTER.md`)
기준 1–6 PASS/FAIL + 근거, 항목 P1–P7별 변경 파일·줄 수, 시안·규칙과 다르게 한 점과 이유, 남은 한계, 커밋 묶음 제안
