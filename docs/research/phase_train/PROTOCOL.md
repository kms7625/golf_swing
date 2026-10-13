# 보정 전 고정한 실험 계획

2026-10-13. 기준 `3bdf45dfb4aa3118484bad33cb967e3810dcf46f`. split 1–3의 이벤트 점수를
계산하기 전에 작성. 생성 중인 캐시는 라벨을 사용하지 않는 전처리다.

## 분리·평가

- 대상: slow=0, face-on/down-the-line, 실제 fps 30±0.15. 메타데이터 기준 556개:
  split1 142 / split2 135 / split3 130 / split4 149. fps 제외 목록은 캐시 완료 후 집계.
- 개발: split 1–3만 사용. 3-fold 각각 나머지 두 split에서 같은 탐색 후 한 split 평가.
  fold 결과로 탐색 범위를 바꾸지 않는다. 전체 split 1–3에서 같은 탐색으로 최종 선택.
- 목적함수: 기존 `phase_fix_eval.py`의 4개 이벤트 PCE 산술 평균. GT는 events−events[0].
  오차 허용 `max(round((Impact−Address)/30),1)` 원본 프레임. 거부/누락은 오답.
- 제약: 7개 앱 영상의 baseline 자동 스캔·트림 신호 14개 모두 검출 성공.
  최종 후보는 실제 Docker 자동 스캔·트림·포즈 재추론에서도 거부 0이어야 잠금 가능.
  재추론이 거부되면 split4를 열지 않고 개발 단계로 남긴다.
- 알고리즘: baseline부터 시작, 아래 표 순서대로 2회 좌표 하강. 동점은 현재값 유지.
  전역 최적 보장 없음. 점수 상승은 목적함수가 아니다.
- 마지막에 코드/파라미터/캐시 해시를 고정하고 split4 전체 paired 평가 1회.
  원자적 lock을 만든 뒤 평가하며 실패 시에도 lock 삭제/재실행 금지.

## 후보 범위와 근거

문헌은 이벤트 의미와 시간 척도 근거다. 아래 숫자 범위 자체는 공학적 후보이며 문헌에서
검증된 최적값이라는 뜻이 아니다. GolfDB의 클럽/공 기준 이벤트는 손목만으로 직접 관측할 수 없다.

| 파라미터 | 기준값 | 사전 후보 | 근거/의미 |
|---|---:|---|---|
| plateau_ratio | .05 | 0, .025, .05, .075, .10 | 기존 몸통 5% 평탄 처리 양쪽 범위; 정지 톱 과지연 가능성 |
| top_offset_sec | 0 | 0, 1/30, 2/30, 3/30 | 손목 정점 후 클럽 반전 지연; 30fps 0–3프레임. 기존 보고서의 오프셋 관찰은 가설로만 사용 |
| onset_fraction | .10 | .02, .05, .10, .15 | 테이크어웨이 직전 정의에 맞춘 작은 상승폭부터 기존값 주변 |
| address_offset_sec | 0 | −.20, −.10, −1/30, 0 | 이미 검출된 손목 상승보다 앞선 Address; Yamamoto 2023의 선행 이동은 정성적 근거 |
| address_window_sec | 3 | 1, 2, 3 | 이전 연습 움직임 연결을 줄이면서 일반 백스윙 시간 포함 |
| impact_window_sec | 1.25 | .50, .75, 1.25 | 원 raw-Y argmax 보존; 약 .3초 다운스윙과 앱의 느린 영상 허용 |
| finish_mode | minimum | minimum, settled_start, settled_end | 기존 최소점, 첫 안정 구간 시작, 첫 안정 구간 마지막 프레임 |
| finish_speed_ratio | .20 | .10, .20, .40 | 스무딩한 pixel Y 속도를 몸통 길이/초로 정규화; 포즈 잡음 허용 후보 |
| finish_hold_sec | .20 | .10, .20, .30 | 30fps 약 3–9프레임 연속 저속; 없으면 기존 최소점 |
| finish_window_sec | 2 | 2, 3 | Impact 후 최종 자세 유지까지 포함, 컷/긴 결측은 넘지 않음 |
| smooth_sec | .10 | 1/15, .10, 1/6 | 30fps 홀수창 3 또는 5; edge-aware 보존, A9의 의도적 탐색 |

Top/Address offset은 사이클 순위 결정 후 이벤트 경계에 적용하고 순서를 보존하도록 clamp한다.
Finish는 선택된 follow 최소점 이후 첫 연속 저속 구간을 사용한다. 정지하지 않는 스윙에서는
정의와 다를 수 있다. 원 argmax·6관절 gate·각도식·점수식·대표 프레임 선택·600프레임 상한은 보존.

## 기존 평가 노출

필수 읽기 자료 `phase_diag/REPORT.md`, `AFTER.md`(9절 포함), `golfdb_eval/README.md`에
split4 일부 및 전체 split을 포함한 과거 평가가 있다. 따라서 이번 split4를 역사적으로 전혀
보지 않은 데이터라고 부르지 않는다. 이번 보정 중 새 split4 이벤트별 결과를 열거나 튜닝에
사용하지 않으며, 최종 로그는 **이번 실행의** 단회 평가만 증명한다.

## 근거

- [GolfDB 논문 §3, §4.3](https://arxiv.org/html/1903.06528): Address/Top/Finish 정의, PCE, 원 영상별 분할.
- [원 util.correct_preds](https://github.com/wmcnally/golfdb/blob/master/util.py): 허용오차.
- [Yamamoto 2023](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2023.1272038/full): 손목 신호 기반 이벤트 후보.
- [Choi 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC3941698/): 다운스윙 시간 척도. 알고리즘 정확도 보증 아님.
