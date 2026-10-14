# 분석 엔진 정확도 실행 보고

2026-10-14 · `feature/engine-accuracy` · 기준/현재 HEAD `b8eace6` · 커밋 없음.

**채택: 업로드 영상의 시간 기준 필터·60fps 추론 간격. 불채택: Address/Finish 추가 튜닝. 타격 구분: 현재 제약에서 신뢰도 입증 불가, 제품 분류기 미구현.**
완료 검증은 통과했지만 Address/Finish 정확도 향상 목표는 달성하지 못했다. 실제 60fps 촬영본은 미확인이다.

이하 원자료 루트 **R=`/Users/mose/datasets/golfdb_pose/engine_accuracy_20261014/`**.
각 표 아래의 `R/파일`이 실행 JSON/로그다. [집계 JSON](summary.json), [사전 계획](PROTOCOL.md), [재현 도구](../../../tools/engine_accuracy/README.md).
모든 새 GolfDB 실행은 split 1–3만 사용했다. split 4 영상/캐시/평가를 실행하거나 열지 않았다.
지정된 과거 보고서의 split 4 수치는 역사 자료로만 읽었고 선택에 사용하지 않았다.

## 1. Address·Finish: 기준선 → 원인 → 후보 → 불채택

현재 고정 파라미터로 기존 Docker 포즈 캐시를 재생했다. GT=`events[1:9]−events[0]`,
허용오차=`max(round((GT Impact−GT Address)/30),1)` 원본 프레임. 누락/거부는 PCE 분모에 포함한다.
평가 매핑은 이전 실험 그대로 Address=백스윙 시작, 나머지=해당 단계 시작이다.
이 표는 **현재 고정값의 재측정**이며, 과거 학습의 out-of-fold 결과와 구별한다.

| split | n | 거부 | Address PCE | Top PCE | Impact PCE | Finish PCE | 평균 PCE 전→최종 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 142 | 1 | 14.79% | 82.39% | 92.25% | 16.20% | 51.41→51.41% |
| 2 | 135 | 2 | 13.33% | 77.78% | 91.85% | 11.85% | 48.70→48.70% |
| 3 | 130 | 0 | 7.69% | 83.85% | 92.31% | 12.31% | 49.04→49.04% |

근거: `R/baseline_development.json`, `R/final_development.json`. split 산술 평균 **49.72→49.72%, 차이 0.00%p**.
Address 절대오차 중앙값은 split별 6/5/5프레임, Finish는 8/9/8프레임(예측 존재 클립만).
이전 REPORT_fix의 고정값 전체 개발 결과와 일치한다. 이전 표의 fold 2 Address 11.85%는 그 fold에서 선택한 support=.2의 결과이고, 현재 support=.3 재측정은 13.33%다.

**정의 차이:** [GolfDB 원 논문 §3·§6.3](https://arxiv.org/html/1903.06528)은 Address를 takeaway가 보이기 직전 프레임, Finish를 최종 자세 이완 직전 순간으로 정의한다.
앱 Address는 각도 집계를 위한 유지 구간이고 평가에서는 그 다음 백스윙 시작을 썼다.
엄밀한 이벤트 대응은 Address 마지막 관측에 가깝지만, 손목 높이 변화가 클럽 takeaway와 동시라는 보장은 없다.
한 프레임 매핑 차이만으로 현재 Address 중앙 오차를 설명할 수 없다.
앱 Finish 시작은 손목 상승 극값 뒤 첫 저속 유지 시점이다. GolfDB의 **유지 종료/자세 이완**과 다른 사건이다.
따라서 Finish 시작 PCE를 골퍼의 피니시 구간 정확도로 해석하거나 GolfDB 8이벤트 모델 PCE와 직접 비교하는 것은 부적절하다.
손목 Y만으로 클럽과 전신 이완을 직접 관측할 수 없어, 상수 오프셋만으로 해결됐다는 주장도 하지 않는다.

Address offset 7개×Finish mode 3개의 후보를 고정했다. 앱 캐시에서 거부/Top·Impact 참조 거리/점수를 먼저 검사하고,
각 검증 split을 제외한 두 split의 PCE로 선택했다. 현재값 우선 동점 처리, 기타 파라미터 고정이다.

| 검증 split | 선택 후보 | 기존 평균 PCE | 후보 평균 PCE | 후보 Address PCE |
|---|---|---:|---:|---:|
| 1 | offset −.30, settled_start | 51.41% | 49.65% | 7.75% |
| 2 | offset −.30, settled_start | 48.70% | 49.07% | 14.81% |
| 3 | 현재값 | 49.04% | 49.04% | 7.69% |

근거: `R/search.json`, `R/logs/search.log`, `R/boundary_diagnostics.json`.
후보 fold 산술 평균 **49.25%, 기존 대비 −0.46%p**로 E3 평균 제한은 통과한다.
그러나 Address fold 산술 평균은 **11.94→10.08%**로 낮아졌고 Finish는 변화가 없어 개선안으로 채택하지 않았다.
개발 전체 재적합의 최고 후보는 평균 49.94%(현재 49.75%)지만 독립 검증이 아니다.
Finish를 settled_end로 바꾼 현재 offset 후보의 전체 재적합 평균은 46.87%로 낮아졌다.
추가 모델·파라미터 확대 탐색 없이 중단했다. 새 테스트는 유지 시작/끝의 차이, 원시 Impact 보존, 컷 내 폴백을 검사한다.
**최종 phase_parameters/phase_detector는 변경하지 않았다. 정확도 개선은 미달이며 기존 동작을 유지한다.**

## 2. 연습 스윙과 실제 타격: 조사·실측 → 불가

영상에서 타격 전 공이 지속해서 보이고 이후 이동하면 타격의 근거가 될 수 있다.
하지만 일반적인 차영상은 움직인 물체의 종류를 알려주지 않는다([OpenCV 공식 설명](https://docs.opencv.org/4.10.0/d1/dc5/tutorial_background_subtraction.html)).
클럽/발/그림자/잔디 변화도 같은 신호에 들어간다. 공이 보이지 않는 것은 practice의 증거가 아니다.

앱 선택 Impact와 기존 수동 참조 각각에서 −.3/−.2/−.1초 및 +.1/+.2/+.3초를 원본 픽셀로 읽었다.
아래쪽 45% 영역에서 밝기 임계값 180/220의 지속 소형 연결요소와 이후 소실을 기록했다.
GolfDB는 split당 ID 순 첫 10개(합계 30개)의 GT Impact를 사용했다. ID·영상 크기·좌표·영역 차이·객체별 소실이 모두 원자료에 있다.
이는 공 검출 정답이나 분류 정확도가 아니며, GT Impact를 준 유리한 조건에서의 가능성 조사다.

| 앱 선택 구간 | 밝기 180: 지속 후보/소실 | 밝기 220: 지속 후보/소실 |
|---|---:|---:|
| 일반 | 313 / 26 | 26 / 5 |
| 프로 | 17 / 1 | 68 / 5 |
| 프로2 | 513 / 79 | 77 / 10 |
| 8065880 | 131 / 5 | 0 / 0 |
| 6541855 | 912 / 62 | 830 / 62 |
| 35546329 | 692 / 86 | 54 / 29 |
| 34883764 | 46 / 12 | 9 / 8 |

근거: `R/shot_probe.json`, `R/shot_sheets/*_selected.jpg`, `*_manual_reference.jpg`(직접 검토).
34883764 선택 f225–237에서는 공이 지면에 남지만 소실 후보가 12/8개다. “소실 있음=shot”은 연습 스윙을 오판한다.
같은 영상 수동 참조 f636–648에서는 공이 지면을 떠나는 것이 보인다. 선택/참조의 차이를 눈으로 확인할 수 있는 사례다.
8065880은 공 이동이 보이지만 밝기 220 후보는 없어서 “검출 없음=practice” 역시 잘못된다.
프로2의 선택 사이클과 수동 참조가 다르다는 사실만으로 선택 사이클을 practice라고 확정하지 않는다.

| GolfDB 명목 타격 30개 | 밝기 180 | 밝기 220 |
|---|---:|---:|
| 후보 없음 | 1 | 5 |
| 후보 여러 개 | 26 | 21 |
| 소실 없음 | 5 | 11 |
| 소실 여러 개 | 10 | 6 |

근거: `R/shot_probe.json`, `R/summary.json`의 `shot_golfdb`.
GolfDB에는 practice/shot 정답이 없고, 현재 앱 음성 사례도 대표 검증 표본이 아니다.
물체 소실만으로 접촉/발사 객체 궤적을 입증하지 못했고 안정적인 precision/recall을 산출할 정답도 부족하다.
**판정: 현재 규칙·영상 조건으로 신뢰할 제품 분류는 불가. 분류기/shot_type/API/i18n 안내를 추가하지 않았다.**
특정 영상에서 수동 공 영역을 지정한 분류 가능성까지 부정하는 결론은 아니다.

## 3. 60fps: 시간 처리 수정 → 합성 검증 통과

| 점검 지점 | 변경/판정 |
|---|---|
| process_video의 총 프레임/600 | 고fps의 ~30회/초 추론 간격과 메모리 상한을 함께 계산. 60fps는 기본 step=2; 긴 영상도 그 배수로 간격 증가 |
| sample_rate 인자 | 기존부터 무시하던 UI 호환 힌트. 실제 eff_sample을 반환하며 고정 3프레임 간격으로 해석하지 않음 |
| 각도 MA 5개 | 최근 4/29.97초의 유효 관측 평균. 균일 30fps에서 5개 평균과 같고 오래된 가시성 결측 전 값은 제외 |
| 기록용 3D 평균 5개 | 같은 시간 창 적용. 2D 점수 선택/3D 기록 분리 유지 |
| SceneCuts 최근 차이 15개 | .5초 이력, 영상 차이 관측 ~30회/초. fade 및 cooldown .2초 유지 |
| phase_detector/phase_parameters | 이미 초 기반 창/원본 시간 사용. 홀수 edge-aware 스무딩, ≤.2초 결측, 이벤트 .05초 폭 유지 |
| 최소 8개/단계 간 2개 등의 검사 | 빈 단계 방지를 위한 관측 개수/배열 경계 검사이며 초 단위 시간 창이 아님 |
| 30fps 기본값/legacy count filter | fps 없는 이전 호출의 호환 기본값. 생산 업로드 경로는 영상 fps와 명시적 time_sec를 전달 |
| smoothing.interpolate의 last3 | 레포 내 호출 없는 legacy helper; 업로드 분석에서 사용하지 않음 |
| 서버 live 입력 | fps/시간 정보 없이 기본 30으로 호출하는 기존 제약 유지. E7 밖 서버 변경을 하지 않아 live 60fps는 미지원/미검증 |

근거: analyzer diff, `R/cache_clock.json`, `tests/test_engine_clock.py`. 개발 캐시 **407/407**의 샘플 간격·컷이 일치하므로 기존 포즈 재생으로 최종 PCE를 측정할 수 있다.
local_idx 매핑·원본 frame/time·대표 프레임 규칙·raw Y argmax·점수 임계값은 유지했다. 상한은 여전히 600관측이다.

앱 고정 구간을 ffmpeg/FFV1의 공통 30fps 대조로 만들고 복제와 motion interpolation으로 각각 60fps를 생성했다.
24/25/29.97fps 원본의 30fps 변환과 트림/재인코딩이 포함돼 **대조 점수는 원본 앱 점수와 다르다**.
초안 Matroska는 ms 시계 양자화로 원본 시점까지 미세 보간되는 것을 발견했다.
exact 1/60000 시계로 보간하고 끝 프레임을 패딩했다. AVI로 무재인코딩 재포장해 OpenCV의 명시적 30/60fps 읽기를 맞췄다.
원 초안/실패는 `R/fps_baseline.json`, `fps_final.json`, `fps_*_aligned.json`에 보존했고 최종 성공과 혼합하지 않았다.

| 클립 | 30fps 대조 점수 | 60 복제 점수 | 60 보간 점수 | 모든 단계 시작/끝 최대 오차(초) |
|---|---:|---:|---:|---:|
| 일반 | 60 | 60 | 60 | 0.000 / 0.000 |
| 프로 | 65 | 65 | 65 | 0.000 / 0.000 |
| 프로2 | 92 | 92 | 92 | 0.000 / 0.000 |
| 8065880 | 80 | 80 | 80 | 0.000 / 0.000 |
| 6541855 | 90 | 90 | 90 | 0.000 / 0.000 |
| 35546329 | 55 | 55 | 55 | 0.000 / 0.000 |
| 34883764 | 90 | 90 | 90 | 0.000 / 0.000 |

근거: `R/fps_final_avi.json`(각 단계 초·점수·step·파일 SHA), `R/summary.json`의 `fps`.
명령: `R/fps_commands.json`, `fps_commands_aligned.json`, `fps_rewrap_commands.json`.
합성 60fps의 추가 프레임을 활용한 정확도 향상이 아니라, 같은 입력 시계에서의 결과 일관성 검증이다.
**시간 처리 변경 채택. 실제 60fps 촬영본 검증은 미확인**이며 센서 블러/새 관측/실제 공 접촉 정밀도를 보장하지 않는다.

## 4. E3 앱 7개 비악화와 E6 재생성

아래는 **원본 앱 영상의 실제 Docker 자동 스캔→트림→추론**이다. Top/Impact는 0-based 원본 프레임.

| 영상 | 기존 Top/Impact/점수 | 변경 Top/Impact/점수 | E3 |
|---|---|---|---|
| 일반 | 83 / 90 / 45 | 83 / 90 / 45 | PASS |
| 프로 | 306 / 314 / 52 | 306 / 314 / 52 | PASS |
| 프로2 | 1193 / 1201 / 77 | 1193 / 1201 / 77 | PASS |
| 8065880 | 137 / 160 / 72 | 137 / 160 / 80 | PASS |
| 6541855 | 118 / 140 / 90 | 118 / 140 / 90 | PASS |
| 35546329 | 365 / 371 / 55 | 365 / 371 / 55 | PASS |
| 34883764 | 224 / 231 / 90 | 224 / 231 / 90 | PASS |

근거: `R/apps_baseline.json`, `R/apps_final.json`, `R/summary.json`. 자동 구간·7단계 전체 경계도 모두 동일, 거부 0→0.
시연 영상 Impact는 REPORT_fix 및 새 실행에서 160이다. 지시문 예시 158–159로 수치를 바꾸지 않았다.
8065880은 기존 5개 평균이 실제 24fps에서 더 긴 시간을 섞었다. 새 시간 창으로 어깨 최대값 58.8→63.5°가 되며 기존 60° 점수 문턱을 넘어 72→80이다.
프로도 결측 이전 관측을 제외해 척추 변화량 12.2→12.9°, 2D X-factor 2.0→−2.8°지만 점수 52는 같다.
이는 각도 신호처리 변경이며 자세/정확도 개선 근거가 아니다. 빈 reference_db의 하드코딩 폴백 점수다.

샘플 3개는 실제 `/analyze`를 통해 baseline Docker에서 재생성했다. 프로는 각도/3D 기록/이슈/일부 HUD 이미지가 바뀌었다.
일반·프로2는 의미상 JSON 내용이 같고 API 키 순서/끝 newline만 달라졌다.
공식 `tests/regen_snapshot.py` 재실행 결과는 기존과 같아 snapshot 파일 diff가 없다.
근거: `R/artifact_regeneration.json`(전후 해시·summary·변경 필드), `R/logs/regenerate.log`.

## 5. 완료 기준·남은 한계

| 기준 | 판정 | 직접 실행 근거 |
|---|---|---|
| 1. 지정 Docker 전체 pytest | PASS | 104 passed, exit 0; `R/logs/pytest.log`. 삭제/완화/skip 없음 |
| 2. 작업별 새 테스트 | PASS | event 정의/컷 폴백 및 cadence·필터·컷·원본 ID: 새 10개 사례. 작업 2는 불가로 제외 |
| 3. E3 표 | PASS | 위 앱 7개·split별 표, 평균 PCE 차이 0.00%p; `R/summary.json` |
| 4. E7 웹 build | PASS(조건 비해당) | server/web/src 변경 없음. build 실행하지 않음 |
| 5. node 웹 호환 | PASS | 지정 명령 exit 0, PASS; `R/logs/web_compat.log` |
| 6. 변경 경로 | PASS | 새 변경은 E1만. 시작부터 있던 미추적 계획서는 보존하고 작업 diff에서 제외; `R/final_checks.json` |

포즈 환경: 기존 golf-server:baseline linux/amd64, Python 3.11.17/MediaPipe .10.21/OpenCV 4.10.0/NumPy 1.26.4(`R/environment.json`).
탐색/집계는 기존 host Python 3.13.3/NumPy 2.2.4 및 표준 라이브러리. 설치/학습 모델/포트 개방/다른 worktree/커밋 없음.
A1–A9는 [계획](PROTOCOL.md)의 근거로 보존했다. A9의 고fps 간격 변경은 이번 사용자 지시로 승인된 범위다.
Streamlit 기동은 기존 Docker에 패키지가 없어 미확인. 서버 import·업로드 분석은 pytest/API로 검증했다.
Address/Finish 개선 미달, 공 타격 분류 미구현, 실촬영 60fps 및 live 시계가 남은 한계다.

## 6. 커밋 묶음 제안(실행하지 않음)

추가+삭제 합계, 신규 파일 전체 줄 수를 포함한다. 대용량 영상/원자료는 레포 밖에 유지한다.

| 묶음 | 파일 | 변경 줄 수 |
|---|---|---:|
| 1 | analyzer 4개 diff + video_clock.py + test_engine_clock.py | 158 |
| 2 | evaluate.py + test_engine_event_definitions.py + cache_clock.py | 174 |
| 3 | fps_video.py + regenerate.py | 168 |
| 4 | shot_probe.py + summarize.py + summary.json + 샘플 3개 | 195 |
| 5 | PROTOCOL.md + tools README | 93 |
| 6 | REPORT.md | 189 |

최종 실측 줄 수/파일 목록은 `R/commit_bundles.json`에 기록한다. 기존 미추적 계획서·.git은 수정하지 않았다.
