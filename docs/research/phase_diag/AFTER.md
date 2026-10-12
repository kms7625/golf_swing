# 7단계 분할·자동 구간 수정 — 검증 결과

2026-10-12 · `feature/cobalt-ui` · 기준 HEAD `21c7d51` · 커밋/스테이징 없음

**전체 판정: FAIL(미충족 항목 있음).** 원본 프레임/시간 매핑, 정지 거부, 단일 사이클 분리, 샘플링·손목 gate 분리와 양 UI 연결은 구현했다. 자동 창 IoU 악화는 1건(pro2)이며, 어려운 영상의 실제 타격 선택은 아직 실패한다. 실제 브라우저 화면 검증은 권한 부재로 미검증이다. 테스트 통과를 전체 요구 충족으로 해석하지 않는다.

## 1. 완료 기준 1–6

| 기준 | 판정 | 직접 실행 근거 |
|---|---|---|
| 1. Docker 전체 pytest | PASS | `python -m pytest -p no:cacheprovider -q`: **29 passed**, exit 0. 기존 테스트 삭제·수정·skip 추가 없음. [로그](after/pytest.log). P1 원본 ID·범위, P3 실제 f30–65의 1.2초 정지 API 422·상수 입력, P4 합성/실제 컷, ≤0.2초 결측 포함. |
| 2. 웹 build/lint | PASS | `npm run build`, `npm run lint` 모두 exit 0. 기존 번들 크기·Fast Refresh·정규식 경고는 남음. [build](after/web_build.log), [lint](after/web_lint.log). |
| 3. 7개 영상 표 | PASS(측정 완료) | 아래 자동 창·원본 Top/Impact·49장 원본 ID·점수·처리 시간 표. 정확도 미달은 P2/P4/P7에 별도 표시. [CSV](after/sample_comparison.csv). |
| 4. GolfDB split 4 PCE | PASS(측정 완료) | 정면 25 + DTL 25, 수정 전/후 동일 영상·Docker. 거부도 분모에 포함. 아래 표와 [원자료](after/split4_selection.json). |
| 5. 전/후 그림 | PASS | 7개 `after/*_comparison.png`, 직접 이미지 검토. GolfDB 영상·이미지는 저장하지 않음. |
| 6. 샘플 재생성·화면 확인 | FAIL(일부 미검증) | `/analyze`를 통해 일반·프로·프로2 JSON 재생성, 각 7장·점수·경계 assert. 대표 그림 직접 확인 및 React SSR 렌더링 통과. 실제 브라우저 화면은 미검증. [API 로그](after/sample_api.log), [SSR 로그](after/web_compat.log). |

## 2. P1–P7 구현·판정

| 항목 | 판정 | 변경 파일·동작 |
|---|---|---|
| P1 | PASS | `pipeline.py`, `serialization.py`, `ui/tab_analysis.py`, `CLAUDE.md`: 이미지마다 원본 `frame`/`local_idx`/`phase` 보존. 원본 ID로 조회. 임팩트 첫·다운 85%·나머지 중간 유지. 각도 지표가 없는 포즈도 이미지 단계 정보로 조회하므로 프로2 어드레스가 빠지지 않는다. 49장 모두 해당 원본 경계 내임을 assert. |
| P2 | 기능 PASS / 11.3초 문구 FAIL | `phase_detector.py`, `pipeline.py`, `server/main.py`, `types.ts`, `SwingReplay.tsx`, `Waveform.tsx`, `ResultScreen.tsx`: `phase_boundaries_sec`, `phase_boundaries_frames`, `wrist_times_sec`. 초는 분석 구간 기준, frame은 트림 offset 포함 원본 기준. 구형 JSON은 기존 인덱스 근사로 폴백. 11.3초는 보고서의 **과거 오검출 경계**가 대응한 원본 시각이며 수동 실제 Impact 참조 f375–377(12.50–12.57초)와 다르다. 새 전체 분석 Impact f371=12.367초. 시간 매핑 오차는 0, 실제 타격 수동 참조의 시작 f375와는 0.133초 차이(0.2초 이내)다. |
| P3 | PASS | 몸통 길이의 15% 미만 손목 상승·하강, 후보 없음, 역전/빈 단계 거부. `SwingNotFoundError` → 동기 분석/자동 창/라이브/실패 job 조회 **422 + 지정 한국어 메시지**. scoring 전에 종료. 웹 KO/EN 메시지·구간 재선택 버튼, 업로드/선택 상태 보존. 7개 실제 영상은 모두 결과 생성. |
| P4 | 부분 PASS / 프로2 참조 FAIL | `video_signal.py`, `phase_detector.py`, `pipeline.py`: 프레임 차이/최근 변화량으로 컷, 컷·긴 손목 결측마다 분리. 톱 전 ≤3초, 톱 후 ≤1.25초 raw `argmax(wy)`, 임팩트 후 ≤2초. 유사 진폭 후보는 먼저 나온 완전 사이클 우선. 일반 Top83/Impact90, 프로 Top305/Impact314. 프로2는 참조 앞 f3689 컷 때문에 다른 완전 사이클을 선택한다. |
| P5 | PASS | ≤600 원본 프레임 매 프레임, 이후 `ceil(total/600)` 간격. 단계 신호 스무딩 약 0.10초 홀수 창·edge-aware. 일반 1.5–9.7초 Impact f90. 아래 고립 실행 10초 벤치마크·메모리 수치. 관절각의 기존 5프레임 필터와 각도 계산식은 유지. |
| P6 | 손목 신호 PASS | `video_signal.py`, `pipeline.py`, `phase_detector.py`: 손목 visibility >0.1인 관절만 평균(한쪽만 있으면 한쪽); 6관절 gate는 각도 지표용. 손목 결측 ≤0.2초만 양끝 관측으로 보간하고 컷을 넘지 않음. 긴 결측은 null로 응답하고 파형도 끊음. 각도 지표의 기존 이전 값 유지 정책은 이번 손목 보간 정책과 별개로 보존했으며 잔여 한계다. |
| P7 | FAIL | `auto_detect_swing_window`: 비율 보존 축소, 짧은 영상도 검사, 시간 기준 스캔, 컷 안에서 창 반환, 진폭+하강 속도 후보 순위. 느린 미디어는 하강 시간에 따라 pre-roll을 최대 1.5초까지 늘리되 톱 전 3초 제한. IoU 악화 1건. 어려운 영상은 여전히 연습 스윙 선택, IoU=0; 손목 진폭·속도로 공 접촉을 확정할 수 없음. |

파일별 실제 +/− 줄 수는 7절에 있다. 같은 파일이 여러 P 항목을 구현하므로 항목별 합계로 중복 가산하지 않았다.

## 3. 7개 영상 측정

초는 원본 영상 기준. f는 0-based 원본 프레임. Top/Impact는 경계 시작이며 대표 이미지 ID와 다르다. 수동 참조는 원 REPORT의 단일 검토자 탐색 범위를 변경하지 않았다. 시간은 `process_video`(포즈+HUD+이미지)만으로, 자동 스캔·트림은 제외한다. 이 표의 전/후 실행은 다른 평가 작업과 병행했으므로 속도 배율의 통제 실험으로 쓰지 않는다.

| 영상 | 자동 창 전 → 후(초) | IoU 전 → 후 | Top 전 → 후 / 참조 | Impact 전 → 후 / 참조 | 점수 전 → 후 | 분석 초 전 → 후 |
|---|---|---|---|---|---|---|
| 일반 | 1.500–9.700 → 1.467–5.067 | 0.467 → 0.923 | 79 → 83 / [82, 84] | 167 → 90 / [89, 91] | 55 → 45 | 6.47 → 6.17 |
| 프로 | 8.300–15.400 → 8.647–11.818 | 0.480 → 0.931 | 298 → 305 / [299, 307] | 374 → 314 / [311, 317] | 67 → 52 | 5.21 → 4.47 |
| 프로2 | 123.500–131.500 → 38.172–42.075 | 0.348 → 0.000 | 3767 → 1190 / [3690, 3705] | 3847 → 1201 / [3725, 3735] | 42 → 77 | 5.80 → 5.71 |
| pexels_8065880 | 2.600–9.600 → 2.833–8.583 | 0.866 → 0.920 | 189 → 124 / [132, 138] | 217 → 154 / [159, 162] | 57 → 72 | 8.97 → 6.31 |
| pexels_6541855 | 2.400–8.500 → 1.660–7.560 | 0.787 → 0.814 | 125 → 107 / [112, 117] | 140 → 138 / [138, 140] | 90 → 90 | 7.75 → 8.89 |
| pexels_35546329 | 10.600–19.500 → 10.467–14.467 | 0.433 → 0.984 | 360 → 364 / [360, 364] | 372 → 371 / [375, 377] | 67 → 55 | 8.51 → 11.06 |
| pexels_34883764 | 2.800–10.100 → 6.000–9.800 | 0.000 → 0.000 | 100 → 221 / [630, 633] | 110 → 231 / [641, 644] | 100 → 90 | 5.97 → 7.33 |

대표 ID 순서는 **어드레스 / 백스윙 / 톱 / 다운 / 임팩트 / 팔로우 / 피니시**다. 전/후 사진은 각 버전이 실제 선택한 이미지를 썼다. 원래 버전의 잘못된 순번 조회를 사후 교정하지 않았다.

| 영상 | 수정 후 대표 7장 원본 f | 직접 검토 그림 |
|---|---|---|
| 일반 | 65 / 78 / 84 / 89 / 90 / 112 / 141 | [비교 그림](after/il-ban_comparison.png) |
| 프로 | 277 / 294 / 306 / 312 / 314 / 320 / 339 | [비교 그림](after/pro_comparison.png) |
| 프로2 | 1166 / 1181 / 1191 / 1199 / 1201 / 1207 / 1236 | [비교 그림](after/pro2_comparison.png) |
| pexels_8065880 | 96 / 113 / 125 / 149 / 154 / 177 / 201 | [비교 그림](after/pexels_8065880_comparison.png) |
| pexels_6541855 | 72 / 92 / 108 / 133 / 138 / 148 / 172 | [비교 그림](after/pexels_6541855_comparison.png) |
| pexels_35546329 | 340 / 355 / 365 / 370 / 371 / 388 / 417 | [비교 그림](after/pexels_35546329_comparison.png) |
| pexels_34883764 | 201 / 215 / 222 / 229 / 231 / 239 / 268 | [비교 그림](after/pexels_34883764_comparison.png) |

그림 검토: 일반은 다운·임팩트가 첫 스윙으로 복구되었고 프로는 다음 정면 장면이 섞이지 않는다. 프로2는 새로 선택한 한 스윙의 7장이다. 손목 기반 Top/Impact가 클럽 이벤트와 완전히 일치한다는 판정은 아니다. 손목 가시성이 낮은 영상의 어드레스 시점 및 미세 자세는 여전히 불안정하다.

**프로2 참조 충돌:** [f3570–3700 원본 그림](after/pro2_onset.png)에서 f3600–3688은 앞 스윙의 다운/피니시이고 **f3689에서 이미 톱인 다른 자세로 편집 컷**된다. 기존 [수동 참조](data/manual_reference.json)의 창 f3600–3820은 이 컷을 포함한다. 따라서 같은 창의 Top3690–3705와 ‘컷을 넘지 않는 완전한 어드레스→피니시’를 동시에 충족하지 못한다. 참조는 수정하지 않았으며, 사용자에게 충돌을 알리고 별도 완전 스윙을 선택했다. 이를 기존 IoU 성공으로 바꾸어 계산하지 않았다.

## 4. GolfDB split 4: 수정 전/후

`slow=0`, 실제 fps가 30±0.15, 로컬 영상 존재, ID 순으로 **split 4만** 정면/DTL 각 25개. 선택 ID는 [selection](after/split4_selection.json), 개별 숫자는 `after/before_golfdb_*.json`, `after/after_golfdb_*.json`. 영상·이미지는 레포에 없음. ID 순 표본이므로 전체 split 4의 대표 표본이라고 보장하지 않는다. GPU 없이 동일 Docker CPU 추론. 수정 전 코드는 작업 시작 전에 `/private/tmp/phase_fix_baseline`에 복사한 HEAD 코드다.

GT=`events[1:9]−events[0]`; Address는 백스윙 시작, Top/Impact/Finish는 해당 단계 시작. 허용오차는 원 REPORT와 동일한 `max(round((GT Impact−GT Address)/30),1)` 원본 프레임. 누락/거부는 오답. 이 정의는 GolfDB 8이벤트 모델 전체 PCE와 동일하지 않다.

| 방향 | 버전 | n | Address | Top | Impact | Finish | 거부/오류 |
|---|---|---|---|---|---|---|---|
| face-on | before | 25 | 0% | 12% | 92% | 4% | 0 |
| face-on | after | 25 | 0% | 48% | 92% | 0% | 0 |
| down-the-line | before | 25 | 0% | 16% | 36% | 4% | 0 |
| down-the-line | after | 25 | 0% | 76% | 84% | 4% | 0 |
| all | before | 50 | 0% | 14% | 64% | 4% | 0 |
| all | after | 50 | 0% | 62% | 88% | 2% | 0 |

임계값을 GolfDB로 맞추지 않았다. 개발 중 확인한 것은 7개 탐색 영상과 합성/정지 테스트이며 split 1–3 학습·튜닝도 하지 않았다. split 4 결과로 검출 임계값을 재조정하지 않았다. 회귀 테스트 실패로 중단한 실행과 표시 메타데이터 수정 전 실행은 `after/exploratory/`에 분리하고 최종 표에서 제외했다. [고정 소스 해시](after/frozen_sources.json).

## 5. 시간·메모리·신호 품질·스냅샷

10초/30fps 벤치마크는 일반 원본 f0–299를 같은 `trim_video`로 재인코딩한 **300프레임**, 다른 평가 컨테이너 종료 후 전/후를 순차 실행했다. 각 1회이므로 안정적인 장기 평균이 아니다.

| 10초 벤치마크 | 수정 전 | 수정 후 |
|---|---|---|
| effective_sample | 2 | 1 |
| process_video 시간 | 7.063초 | 13.371초 |
| 프로세스 최대 RSS | 566.8 MiB | 502.1 MiB |

시간 배율 **1.89배**. 영상 디코딩/포즈/그리기 포함, 트림·자동 스캔 제외. 메모리는 Python/MediaPipe 전체 프로세스 high-water RSS다. 최대 변 480px preview와 600프레임 상한을 채택했다. 600프레임의 RGB 배열 자체 최대치는 약 412 MiB(480×480×3×600), 세로 9:16이면 약 222 MiB이며 전체 프로세스 메모리는 더 크다. 600 초과는 간격을 늘리므로 60fps에서는 10초까지만 원본 fps다.

| 전체 영상 손목 유효율 | REPORT 기존 6관절 gate | 수정 후 손목 gate | 수정 후 sampled 수 |
|---|---|---|---|
| 빨간 `35546329` | 68.2% | 72.5% | 585 |
| 어려운 `34883764` | 38.6% | 100.0% | 413 |

분모·샘플링 정책이 바뀐 전/후 비교이며 동일 프레임 집합에 대한 gate만의 인과 비교는 아니다. 585프레임 빨간 영상 실행의 프로세스 최대 RSS는 760.9 MiB였다. visibility 0.1은 빠른 동작의 가림으로 신호 전체를 지우지 않으려는 완화 기준이며 좌표 정확도 보증이 아니다. [red](after/after_control_red_full.json), [difficult](after/after_control_difficult_full.json).

스냅샷은 Docker `python tests/regen_snapshot.py`로만 재생성했다. 전체 일반 영상 스냅샷: 점수 **50→45**, spine delta **14.7→9.0**, X-factor **11.5→−23.8**, 어깨 최대 **72.4→33.9**, 집계 프레임 **266→93**. 자동 트림 샘플의 55→45와 별개다. `scoring.py`/`geometry.py`/점수 임계값은 변경하지 않았다. 선택 사이클·단계별 집계 대상 및 원본 fps 관측이 달라진 결과이며 점수 상승을 성능 목표로 삼지 않았다.

## 6. 환경·재현·미검증

- 모든 포즈 숫자: **`golf-server:baseline`, linux/amd64**, image `sha256:1ebff936e1e5f666cac7a3b451b5ecf57ba0b5ae6197424899122b9d267e2e06`, Python 3.11.17, MediaPipe 0.10.21, OpenCV 4.10.0.84, NumPy 1.26.4. Mac은 집계·Pillow 그림만 수행. 네트워크 없는 Docker, 데이터셋 read-only mount.
- 이미지에는 pytest가 없어 이미 설치되어 있던 Mac `.venv`의 순수 Python pytest/pluggy/iniconfig/packaging/pygments/py 파일을 `/private/tmp/phase_testdeps`에 복사하여 read-only mount·`PYTHONPATH=/testdeps`로 사용했다. 설치·이미지 변경·새 패키지 추가 없음. `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`로 외부 플러그인 자동 로딩만 끔; 기존 테스트는 모두 실행.
- `tests/phase_fix_eval.py before|after samples|golfdb|controls`, `tests/phase_sample_api.py`, `tests/phase_fix_report.py`, `node tests/phase_web_compat.mjs`가 재현 스크립트다. 평가 JSON이 있으면 건너뛰므로 새 실행은 새 결과 경로/기존 산출물 별도 보관 후 수행한다. 실행 커맨드는 [재현 명령](after/commands.md).
- 브라우저 연결 목록이 비었고 Chrome 컴퓨터 사용 도구가 `Computer Use was not approved to use Google Chrome`으로 거부되어 실제 화면 클릭·재생·재선택 동작은 미검증. React SSR은 옛/새 3개 JSON의 7장 렌더·NaN 표시 없음, timeline 11.3초 우선/구형 5.1초 폴백을 확인했지만 브라우저 E2E 대체라고 주장하지 않는다.
- Streamlit 패키지가 Docker 및 Mac `.venv`에 없어 기동 확인은 미검증. 새 패키지 금지에 따라 설치하지 않았다. 선택 규칙은 서버와 같은 원본 ID 방식으로 함께 변경했다.
- 지시된 `tools/diag_phase/README.md`는 없어서 `docs/research/phase_diag/README.md`와 실행 코드를 읽었다. 보고서·그림 저장은 R1 열거 밖이지만 완료 기준 5와 보고 항목이 명시적으로 요구한 경로에 한정했다.
- 지시와 다른 수치: 톱→임팩트 탐색 상한은 느린 미디어를 고려해 1.25초. 근거 시간 척도는 REPORT L4의 다운스윙 약 0.3초이며 이 상한 자체가 논문 검증값은 아니다. 손목 진폭은 DTL 어깨폭 축소를 피하려고 영상 내 몸통 길이로 정규화한다.
- 남은 한계: 손목만으로 실제 공 타격/연습 및 클럽 Top·Finish를 확정하기 어렵다. 긴 가림 구간은 분석 거부가 늘 수 있다. 각도 지표의 이전 값 유지 정책과 라이브 입력의 기본 30fps 가정은 남아 있다. 프로/프로2처럼 긴 영상의 원본 시간 기반 자동 스캔은 과거 400프레임 스캔보다 오래 걸린다.

## 7. 변경 파일·줄 수

`git diff --numstat` + 신규 구현/검증 파일 전체 줄 수. 생성 JSON은 기존처럼 1줄 JSON으로 저장하므로 줄 수가 작아도 내용은 크다. 보고/PNG/원자료는 별도 산출물이다.

| 파일 | 변경 줄 수 |
|---|---|
| `.claude/skills/golf-code-change/SKILL.md` | +18 / −9 |
| `CLAUDE.md` | +10 / −0 |
| `golf_swing_analyzer/analyzer/phase_detector.py` | +158 / −140 |
| `golf_swing_analyzer/analyzer/pipeline.py` | +94 / −167 |
| `golf_swing_analyzer/ui/tab_analysis.py` | +21 / −12 |
| `server/jobs.py` | +7 / −2 |
| `server/main.py` | +23 / −8 |
| `server/serialization.py` | +14 / −8 |
| `tests/snapshots/ilban_baseline.json` | +5 / −5 |
| `web/public/samples/il-ban.json` | +1 / −1 |
| `web/public/samples/pro.json` | +1 / −1 |
| `web/public/samples/pro2.json` | +1 / −1 |
| `web/src/App.tsx` | +12 / −6 |
| `web/src/components/ResultScreen.tsx` | +3 / −1 |
| `web/src/components/SwingReplay.tsx` | +8 / −5 |
| `web/src/components/Waveform.tsx` | +11 / −6 |
| `web/src/lib/i18n.tsx` | +4 / −0 |
| `web/src/lib/types.ts` | +4 / −1 |
| `golf_swing_analyzer/analyzer/video_signal.py` | +58 / −0 |
| `tests/test_phase_contract.py` | +172 / −0 |
| `tests/phase_fix_eval.py` | +164 / −0 |
| `tests/phase_fix_report.py` | +81 / −0 |
| `tests/phase_sample_api.py` | +31 / −0 |
| `tests/phase_web_compat.mjs` | +40 / −0 |

## 8. 커밋 묶음 제안(실행하지 않음)

200줄은 추가+삭제 합 기준. 큰 파일은 아래 순서로 함수/hunk 단위로 나눠 적용할 것을 제안한다. 중간 상태의 상호 의존성이 있으므로 마지막까지 합친 상태에서 전체 테스트를 다시 실행한다. 생성 JSON도 예외 없이 줄 수에 센다.

| 묶음 | 내용 | 상한 |
|---|---|---|
| 1 | `video_signal.py` + 원본 프레임 DTO/이미지 조회(서버·Streamlit·A8) | ≤200 |
| 2–3 | `phase_detector.py` 신호 시간축/보간/후보 함수 추가, 각 묶음 ≤150 변경 줄로 hunk 분할 | 각 ≤200 |
| 4 | 기존 `detect_all_phases` 교체·단계 소유권/범위 매핑 | ≤200 |
| 5 | `pipeline.py` 자동 창 함수 교체 | ≤200 |
| 6 | `pipeline.py` process 샘플링/gate/단일 사이클 필터·metadata | ≤200 |
| 7 | API 422/job + web 시간축·오류/i18n/구형 폴백 | ≤200 |
| 8 | `tests/test_phase_contract.py` | 172 |
| 9 | `tests/phase_fix_eval.py` | 164 |
| 10 | `phase_fix_report.py` + `phase_sample_api.py` + `phase_web_compat.mjs` | 152 |
| 11 | A7–A9 문구 + 스냅샷 + 샘플 JSON 3개 | ≤80 |
| 12 이후 | AFTER.md, 최종 JSON/CSV/로그/PNG: 텍스트 변경 ≤180줄씩 파일/구간 묶음 | 각 ≤200 |

위는 커밋 계획이며 실제 staged patch를 만든 것은 아니다. `after/exploratory/`는 개발 중간 결과로 최종 비교 커밋에서 제외할 것을 권한다. 기존 사용자 untracked 파일·기존 진단 산출물은 보존했다. Claude 독립 검증·커밋을 위한 완료 조건은 이 보고서의 FAIL/미검증을 함께 검토하는 것이다.

## 9. 추가 수정 (Claude, 2026-10-12): 평탄한 톱 처리
- 증상: Mac 로컬 서버에서 `pexels_8065880` 자동 구간(2.8–8.6초)이 "스윙을 찾지 못함"으로 거부. 손이 톱에서 약 0.6초 멈춰 플래토 첫 프레임을 톱으로 잡으면 임팩트가 1.25초 탐색 창 밖으로 밀림
- 수정: 국소 최소 뒤 몸통 길이 5% 이내로 머무는 마지막 프레임을 톱으로 (`phase_detector.py`, +7줄)
- Docker 재측정(같은 split 4 50개): Top **62→66%**(DTL 76→84%), Impact 88% 동일, Address/Finish 동일. pytest 29 passed
- 7개 영상: 점수 전부 동일. 톱/임팩트 원본 f — 8065880 124/154 → **138/160**(참조 132–138/159–162), 6541855 107/138 → 118/140(참조 112–117/138–140), 35546329 364/371 → 365/371, 프로 305/314 → 306/314, 일반 83/90 동일
- Mac 로컬(.venv)에서도 5개 영상(테스트 3 + 일반·프로) 모두 분석 성공 확인. 샘플 JSON 3개 재생성(점수 45/52/77 동일)
