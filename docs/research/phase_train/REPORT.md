# 단계 인식 A안: GolfDB 규칙 보정

2026-10-13 · `feature/phase-train` · 기준 `3bdf45d` · 발표 후 반영할 실험 브랜치

**한 줄 결론 — split 4 149개 4이벤트 평균 PCE는 41.78% → 52.35%; 7개 앱 영상 거부 0건. 아래 이벤트별·앱별 악화와 잔여 실패를 함께 판단해야 한다.**

## 1. 분리·측정 방법

- 탐색 범위·2회 좌표 하강·동점 유지 정책은 [PROTOCOL](PROTOCOL.md)에 사전 고정했다. split 1–3만 보정했고 fold 결과로 grid를 변경하지 않았다.
- GT=`events[1:9]−events[0]`, Address=앱 백스윙 시작, Top/Impact/Finish=단계 시작. 허용오차는 기존 `tests/phase_fix_eval.py`와 같은 `max(round((Impact−Address)/30),1)` 원본 프레임. 거부/누락은 PCE·≤5 분모에 포함한다.
- 오차 표는 절대오차 중앙값이며 예측이 있는 클립만 계산한다. GolfDB 8이벤트 RGB 모델의 PCE와 직접 비교하지 않는다.
- 필수 읽기 자료에는 과거 split 4 일부/전체 split 평가와 오프셋 탐색이 있다. **역사적으로 미노출인 테스트셋은 아니다.** 이번 보정 중 새 split 4 결과를 보거나 이를 근거로 재조정한 일은 없으며 최종 평가 후 코드·파라미터를 유지했다.

## 2. split 4: 기준선 대 보정 후

| 방향 | n | 이벤트 | PCE 전 | PCE 후 | 중앙 절대오차 f | ≤5프레임 |
| --- | --- | --- | --- | --- | --- | --- |
| all | 149 | Address | 0.00% | 20.13% | 14.0 → 5.0 | 0.67% → 55.03% |
| all | 149 | Top | 71.81% | 83.89% | 1.0 → 1.0 | 96.64% → 95.97% |
| all | 149 | Impact | 92.62% | 92.62% | 1.0 → 1.0 | 96.64% → 96.64% |
| all | 149 | Finish | 2.68% | 12.75% | 11.0 → 8.5 | 12.08% → 36.24% |
| face-on | 64 | Address | 0.00% | 20.31% | 14.0 → 6.0 | 1.56% → 46.88% |
| face-on | 64 | Top | 62.50% | 76.56% | 1.0 → 1.0 | 95.31% → 95.31% |
| face-on | 64 | Impact | 93.75% | 95.31% | 0.5 → 0.0 | 95.31% → 96.88% |
| face-on | 64 | Finish | 1.56% | 15.62% | 11.0 → 10.0 | 10.94% → 31.25% |
| down-the-line | 85 | Address | 0.00% | 20.00% | 13.0 → 5.0 | 0.00% → 61.18% |
| down-the-line | 85 | Top | 78.82% | 89.41% | 1.0 → 1.0 | 97.65% → 96.47% |
| down-the-line | 85 | Impact | 91.76% | 90.59% | 1.0 → 1.0 | 97.65% → 96.47% |
| down-the-line | 85 | Finish | 3.53% | 10.59% | 11.0 → 8.0 | 12.94% → 40.00% |

전체 거부: 1 → 1. 방향별 평균 PCE: face-on 39.45% → 51.95%, down-the-line 43.53% → 52.65%.

**악화도 있다.** DTL Impact는 91.76→90.59%, 전체 Top의 ≤5프레임 비율은 96.64→95.97%다. ID 1358(DTL)은 Top 오차 0→+60f, Impact −1→+64f로 크게 악화했다. Top 정답→오답은 ID 316/830/1358, Finish는 92/875/981/1215에서 발생했다. 전체 Impact 정답 수는 같지만 ID 911의 개선과 1358의 악화가 상쇄됐다.

기존 거부 ID 207은 새 결과를 생성했지만 Top −58f/Impact −45f로 여전히 틀렸다. 새 거부 ID 1370은 기존에도 Top −99f/Impact −68f였다. 따라서 거부 수만으로 품질을 평가하지 않는다. [클립 변화 요약](data/holdout_transitions.json)은 이미 수행한 단회 평가의 결과를 집계한 것이며, 재평가·재튜닝하지 않았다.

## 3. split 단위 3-fold 및 최종 선택

| 검증 split | 학습 n | 평가 n | 후보 수 | 평균 PCE 전→후 | 이벤트별 전→후 |
| --- | --- | --- | --- | --- | --- |
| 1 | 265 | 142 | 51 | 41.90% → 52.11% | Address 0.00%→16.20%, Top 71.13%→83.10%, Impact 92.96%→92.96%, Finish 3.52%→16.20% |
| 2 | 272 | 135 | 53 | 41.11% → 49.63% | Address 0.74%→12.59%, Top 71.11%→82.22%, Impact 91.11%→91.85%, Finish 1.48%→11.85% |
| 3 | 277 | 130 | 53 | 40.58% → 49.62% | Address 0.00%→9.23%, Top 70.00%→84.62%, Impact 92.31%→92.31%, Finish 0.00%→12.31% |
| all | 407 | 407 | 53 | 41.22% → 50.68% | Address 0.25%→12.78%, Top 70.76%→83.78%, Impact 92.14%→92.38%, Finish 1.72%→13.76% |

`all`은 개발 데이터 재적합 성능이며 독립 평가가 아니다. 최종값은 split 1–3 전체에서 동일한 탐색을 적용해 고른 제약 충족 최고값이다. 전역 최적은 보장하지 않으며 앱 회귀 신호 14개는 학습의 거부 제약에 쓰였다.

클립 수로 가중한 out-of-fold PCE: 41.22% → 50.49%. 세 fold에서 개선됐지만 과적합 부재나 스마트폰 영상 일반화를 보장하지 않는다. Top의 양의 고정 오프셋은 선택되지 않았고 평탄 허용폭·스무딩 보정이 채택됐다.

## 4. 파라미터

| 파라미터 | 기준값 | 선택값 | 사전 후보 |
| --- | --- | --- | --- |
| plateau_ratio | 0.05 | 0.025 | 0.0, 0.025, 0.05, 0.075, 0.1 |
| top_offset_sec | 0.0 | 0.0 | 0.0, 0.03333333333333333, 0.06666666666666667, 0.1 |
| onset_fraction | 0.1 | 0.02 | 0.02, 0.05, 0.1, 0.15 |
| address_offset_sec | 0.0 | -0.2 | -0.2, -0.1, -0.03333333333333333, 0.0 |
| address_window_sec | 3.0 | 2.0 | 1.0, 2.0, 3.0 |
| impact_window_sec | 1.25 | 0.75 | 0.5, 0.75, 1.25 |
| finish_mode | minimum | settled_start | minimum, settled_start, settled_end |
| finish_speed_ratio | 0.2 | 0.4 | 0.1, 0.2, 0.4 |
| finish_hold_sec | 0.2 | 0.1 | 0.1, 0.2, 0.3 |
| finish_window_sec | 2.0 | 2.0 | 2.0, 3.0 |
| smooth_sec | 0.1 | 0.16666666666666666 | 0.06666666666666667, 0.1, 0.16666666666666666 |

각 범위의 근거는 [사전 계획](PROTOCOL.md)의 대응 표에 있다. 문헌은 이벤트 의미·시간 척도의 근거이고 범위 자체는 공학적 후보다. Top/Address 오프셋은 후보 순위 결정 후 순서를 보존하여 적용한다. 안정 Finish는 손목 정지의 대리 지표이며 적격 유지 구간이 없으면 기존 최소점으로 폴백한다.

## 5. 7개 앱 영상: 실제 Docker 자동 창→트림→재추론

창은 원본 초, Top/Impact는 0-based 원본 프레임이며 대표 이미지와 구별한다. 참조는 한 명의 기존 탐색 범위이며 GolfDB 정답처럼 취급하지 않는다.

| 영상 | 자동 창 전→후(초) | Top 전→후 / 참조 | Impact 전→후 / 참조 | 점수 전→후 | 거부 |
| --- | --- | --- | --- | --- | --- |
| il-ban | 1.467–5.067 → 1.400–5.067 | 83 → 83 / [82, 84] | 90 → 90 / [89, 91] | 45 → 45 | 0 → 0 |
| pro | 8.647–11.818 → 8.647–11.818 | 306 → 305 / [299, 307] | 314 → 314 / [311, 317] | 52 → 52 | 0 → 0 |
| pro2 | 38.172–42.075 → 38.006–42.075 | 1192 → 1192 / [3690, 3705] | 1201 → 1201 / [3725, 3735] | 77 → 82 | 0 → 0 |
| pexels_8065880 | 2.833–8.583 → 2.708–8.417 | 138 → 134 / [132, 138] | 160 → 152 / [159, 162] | 72 → 72 | 0 → 0 |
| pexels_6541855 | 1.640–7.640 → 2.160–7.640 | 118 → 127 / [112, 117] | 140 → 140 / [138, 140] | 90 → 90 | 0 → 0 |
| pexels_35546329 | 10.467–14.467 → 10.133–14.467 | 365 → 364 / [360, 364] | 371 → 371 / [375, 377] | 55 → 45 | 0 → 0 |
| pexels_34883764 | 6.000–9.800 → 5.933–9.800 | 223 → 223 / [630, 633] | 231 → 232 / [641, 644] | 90 → 90 | 0 → 0 |

점수는 빈 `reference_db.json`의 기존 하드코딩 폴백 기준이다. 점수 상승은 정확도 향상 판정이 아니다. 점수식·각도식·각도 스무딩을 변경하지 않았다. 원본 이미지 49장 모두 자기 단계의 경계 안에 있음을 실행 중 assert했다.

탐색 참조 대비 악화: pexels_8065880 Impact: 참조 범위까지 거리 0→7f; pexels_6541855 Top: 참조 범위까지 거리 1→10f. 범위 내 차이를 개선/악화로 단정하지 않으며 참조 자체의 불확실성도 유지한다.

`8065880`은 24fps의 느린 재생 영상이다. 선택된 0.75초 Impact 창은 Top f134 뒤 약 18프레임까지여서 참조 Impact f159–162를 포함하지 못한다. 이는 동결된 파라미터·측정 프레임에 근거한 해석이다. `6541855`는 25fps이며 Top이 9프레임 늦어졌다. 실시간 30fps GolfDB 보정이 이런 영상에 그대로 일반화하지 않는 사례다. 빨간 영상의 점수 55→45와 프로2의 77→82도 기록했으며 점수 기준을 바꾼 결과가 아니다.

## 6. 완료 검증·환경

| 검증 | 결과 |
| --- | --- |
| regen_snapshot | exit 0 · /Users/mose/datasets/golfdb_pose/logs/regen_snapshot.log |
| pytest | exit 0 · /Users/mose/datasets/golfdb_pose/logs/pytest.log |
| web_build | exit 0 · /Users/mose/datasets/golfdb_pose/logs/web_build.log |
| web_lint | exit 0 · /Users/mose/datasets/golfdb_pose/logs/web_lint.log |

**지시된 완료 기준 5개는 PASS다.** 정확도 악화와 Streamlit 미검증은 별도 한계로 남긴다.

| 완료 기준 | 증거 |
| --- | --- |
| 기본 파라미터 동일 | 개발 407개 경계·원본 frame/time·후보·매핑 정확히 동일, 합성 회귀 포함 |
| split 4 마지막 1회 | 동결→평가 시작→완료 각 1건, 평가 후 탐색 0건, 소스 해시 동일 |
| Docker pytest·웹 | **67 passed**, skip/기존 테스트 완화 없음; build·lint exit 0 |
| 앱 7개 거부 0 | 실제 자동 스캔→트림→추론 완료, 대표 이미지 49장 범위 확인 |
| 원래 폴더 무변경 | 최초 git status 및 추적 파일 316개 해시 동일 |

기본값 동일성은 [default_parity](data/default_parity.json)에 기록했다. `PhaseParameters()`는 기준선 기본값이며, 인자 없는 앱 검출기는 선택된 `CALIBRATED_PARAMETERS`를 사용한다. 변경하지 않은 `3bdf45d` 검출기를 oracle로 결측·컷·fps 회귀를 검사했다. 캐시와 실제 파이프라인의 신호·경계는 개발 ID 6/14/21(매 프레임) 및 178(2프레임 간격)에서 정확히 일치했다. [캐시 검증](data/cache_pipeline_parity.json).

캐시 556개 모두 정상: split 1/2/3/4 각각 142/135/130/149개. fps 제외·실패 0개, 600프레임 초과 별도 adaptive 추론 8개다. 누적 worker 처리 143.4분, 기존 3개 worker의 캐시 wall time 49.4분이었다. [완료 기록](data/completion.json).

포즈 추론은 기존 `golf-server:baseline` linux/amd64, Python 3.11.17, MediaPipe 0.10.21, OpenCV 4.10.0.84, NumPy 1.26.4. image ID `sha256:1ebff936e1e5f666cac7a3b451b5ecf57ba0b5ae6197424899122b9d267e2e06`. 캐시는 현재 pipeline과 같은 CLAHE·model_complexity=1·smooth_landmarks=True·detection/tracking=.5. ARM Mac 위 amd64 에뮬레이션, GPU 없음.

탐색·캐시 이벤트 재생은 Mac ARM64의 기존 Python 3.12.4/NumPy 1.26.4와 표준 라이브러리만 사용했다. 원래 폴더의 `.venv`는 `-B`/`PYTHONDONTWRITEBYTECODE=1`로 읽기 전용 사용했다. pytest는 기존 순수 Python 파일을 `/private/tmp/phase_testdeps`에서 mount했다. 설치·이미지 재빌드·새 패키지 없음. [호스트 환경](data/host_environment.json), [추론 환경](data/environment.json).

원래 폴더: 최초 status와 동일, tracked 316개 해시 동일. 8010 서버 제어 없음. 커밋·브랜치 변경·merge 없음.

Streamlit 기동은 기존 Docker에 패키지가 없어 미검증이다. 새 패키지 금지에 따라 설치하지 않았으며 서버 import와 분석은 pytest로 확인했다. 웹 build의 번들 크기 경고와 lint의 기존 경고는 남아 있고 exit code는 0이다.

스냅샷은 `tests/regen_snapshot.py`로만 재생성했다. [전/후 원자료](data/snapshot_comparison.json).

| 스냅샷 지표 | 전 | 후 |
| --- | --- | --- |
| 점수 | 45 | 45 |
| 척추각 변화량 | 9.0 | 9.1 |
| X-factor | −23.8 | −23.8 |
| 어깨 최대 회전 | 33.9 | 33.9 |
| 집계 프레임 | 93 | 95 |

## 7. 단회 평가 증거

| UTC | 감사 이벤트 |
| --- | --- |
| 2026-10-13T05:40:21.750965+00:00 | parameters_frozen |
| 2026-10-13T05:40:28.812012+00:00 | split4_evaluation_started |
| 2026-10-13T05:40:29.542031+00:00 | split4_evaluation_completed |

`~/datasets/golfdb_pose/audit.jsonl`, `frozen.json`, `split4_once.lock`이 원자료다. lock은 실패 시에도 재평가를 막는다. [completion](data/completion.json)에 감사 로그 해시·횟수·순서·소스 동일성·원본 폴더 검증을 저장했다.

## 8. 한계·B안

손목 Y만으로 클럽 반전, 공 접촉, 최종 자세 이완을 직접 관측하지 못한다. Address/Finish 정의 차이, 저해상도 포즈 오차, 컷과 잘못된 스윙 선택이 남는다. pro2 참조는 컷을 포함하고 어려운 영상은 실제 타격 대신 연습 스윙을 선택하므로 7개 거부 0건을 실제 타격 정확도 성공으로 해석하지 않는다. A9의 스무딩 창은 승인된 보정 대상으로 탐색했으며 600프레임 상한과 결측 규칙은 보존했다.
B안은 [B_DESIGN](B_DESIGN.md)에 입력·라벨·분리·1D CNN/GRU·PyTorch 버전/라이선스·이미지 크기/속도 예산을 정리했다. 설치·모델 구현·학습은 수행하지 않았다. 속도는 가설이고 A안 대비 개선 수치는 근거가 없어 예측하지 않았다.

평균 PCE 개선은 확인했지만 Address 20.13%와 Finish 12.75%는 여전히 낮다. 느린 앱 영상 2개와 GolfDB의 큰 오차 사례가 있어 즉시 제품 반영을 권하지 않는다. 이번 결과로 다시 파라미터를 조정하거나 split 4를 재평가하지 않았으며, 발표용 원본 dev는 유지했다.

## 9. 재실행·커밋 묶음

명령과 경로는 [tools README](../../../tools/phase_train/README.md). 기존 결과의 잠금을 지워 반복하지 않는다. 이번 결과 루트는 보존한다. 원자료/캐시는 CC BY-NC 4.0 비상업 연구·평가 용도로 레포 밖에만 둔다.

커밋은 실행하지 않았다. 아래는 추가+삭제 ≤200줄의 제안이며 최종 결합 상태에서 검증한다.

기존 `.venv` 링크·작업 지시서와 실행 중 수집된 `codex_run*.log`는 변경 묶음에서 제외한다. 아래 보고서는 자동 표 생성 후 단회 결과 해석을 추가한 최종본이다.

| 묶음 | 내용 | 변경 줄 상한 |
| --- | --- | --- |
| 1 | phase_parameters.py + phase_detector.py diff | 130 |
| 2–3 | baseline oracle fixture: 두 구간으로 나눔 | 각 150 |
| 4 | test_phase_parameters.py + test_phase_train_metrics.py | 120 |
| 5 | common.py + replay.py | 140 |
| 6 | cache.py + verify_cache.py | 170 |
| 7 | train.py + check_defaults.py | 150 |
| 8 | apps.py + 스냅샷 + 샘플 3개(compact JSON) | 160 |
| 9 | holdout.py + provenance.py | 200 |
| 10 | report.py | 200 |
| 10b | checks.py | 60 |
| 11 | PROTOCOL.md + B_DESIGN.md | 150 |
| 12 이후 | REPORT.md/README/요약 JSON·로그: 파일·hunk별 분할 | 각 ≤200 |
