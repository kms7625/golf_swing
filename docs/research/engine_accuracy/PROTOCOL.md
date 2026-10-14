# 엔진 정확도 실행 계획

기준 `b8eace6`, 브랜치 `feature/engine-accuracy`, 2026-10-14.
작업 worktree만 변경한다. split 4 영상·포즈 캐시·평가 산출물은 열지 않는다.
기존 미추적 `docs/planning/impl/codex-impl-engine-accuracy.md`는 보존한다.
원자료는 `/Users/mose/datasets/golfdb_pose/engine_accuracy_20261014/`.

## 측정과 선택

- split 1–3의 기존 Docker 포즈 캐시로 현재 고정 파라미터를 먼저 재측정한다.
  GT/허용오차/누락 분모는 `tools/phase_train/common.py` 그대로다.
- Address offset 후보: −.30, −.25, −.20(현재), −.15, −.10, −.05, 0초.
  Finish 후보: minimum, settled_start(현재), settled_end. 그 외 값은 고정.
  각 fold는 나머지 두 split의 PCE로 선택한다. 동점은 현재값 우선.
  최종값은 전체 개발 데이터 재적합으로 별도 표시한다.
- 앱 캐시로 거부/Top·Impact 참조 거리/점수 비악화를 먼저 검사한다.
  최종 앱 결과는 Docker 자동 스캔→트림→추론으로 재실행한다.
  점수 상승은 정확도 향상 증거가 아니다. PCE 평균 하락 >1%p는 불채택.
- GolfDB Address는 takeaway 직전, Finish는 최종 자세 이완 직전이다.
  앱의 구간 경계와 일치하지 않으면 proxy 오차와 정의 차이를 따로 보고한다.
  이 탐색은 새 독립 검증이 아닌 기존 개발 데이터의 추가 탐색이다.
- 타격 구분은 공 영역의 작은 밝은 연결요소/지속성/이동/영상 차이를 실측한다.
  앱 7개 및 split 1–3 표본을 원본 픽셀로 검사한다. 실제 샷·연습 음성 사례와
  확인 불가능 사례를 구별하고, 공이 안 보인다는 이유로 practice라 하지 않는다.
  신뢰도 입증이 없으면 제품 분류기/API/UI를 추가하지 않는다.
- 60fps는 원본 30fps 앱 클립을 ffmpeg 복제 및 motion interpolation으로 변환한다.
  고정 구간에서 같은 해상도/인코딩의 30fps 대조와 비교한다. 추론 입력 변화와
  순수 신호 재생을 구별한다. 단계 시작 초·점수를 전부 기록하고 실제 60fps는 미확인.

## A1–A9 사전 확인

| 항목 | 보존/허용된 변경 |
|---|---|
| A1 | local_idx→history 및 nearest-key 유지; 시간은 별도 좌표 |
| A2 | Top 뒤 원시 pixel Y argmax 유지 |
| A3 | 손목 pixel 신호와 정규화 각도 분리 유지 |
| A4 | edge-aware 평균 유지, zero padding 금지 |
| A5 | scoring의 Address~Impact 척추각 범위 유지 |
| A6 | 점수 임계값/DB 폴백 변경 없음; 빈 DB 확인 |
| A7 | metric⊆annotation, trajectory⊆metric의 원본 ID 정합 유지 |
| A8 | 서버/Streamlit 대표 프레임 선택 규칙 변경 없음 |
| A9 | 사용자가 승인한 60fps 작업으로 표본 정책/시간 창 점검; 비악화로 채택 판정 |

새 의존성·학습 모델·금지 포트·다른 worktree·git 커밋 사용 없음.
결과가 바뀌면 Docker baseline으로 샘플/스냅샷 재생성 후 전체 pytest/웹 호환 확인.
