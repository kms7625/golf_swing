# Codex 지시 — 회전 지표(X-Factor) 3D 개선 (feature/xfactor)

작업 위치: **`~/PycharmProjects/golf_swing_xfactor`** (브랜치 feature/xfactor, 시작 3bdf45d = dev).

## 0. 절대 규칙
| # | 규칙 |
|---|---|
| Z1 | `~/PycharmProjects/golf_swing`(발표용) 읽기 외 수정 금지, 8010 서버·ngrok 건드리지 않기. 중간발표(10-15) 전 dev 반영 없음 |
| Z2 | git 커밋 금지 — 커밋 묶음(200줄 이하) 제안만, Co-Authored-By 금지 |
| Z3 | 새 패키지 금지. 포즈 수치는 Docker `golf-server:baseline`에서 |
| Z4 | **점수 임계값(A6)은 이번에 바꾸지 않는다.** 새 지표 값이 바뀌어 점수가 달라지면 영상별 전/후 표로 보고하고, 임계값 재설정은 "제안"만 |
| Z5 | golf-code-change A1–A9 준수. 7단계 분할 로직(phase_detector)은 건드리지 않는다 |

## 1. 문제
`golf_swing_analyzer/analyzer/geometry.py` L44–53: 어깨·골반 "회전"이 실제 축 회전이 아니라 **화면 2D 좌우 관절선의 기울기**(arctan2(|dy|,|dx|)). 그래서 X-Factor(= 어깨 최대 − 골반 최대, scoring.py L61)가 음수(−17.5°, −23.8°)나 환경마다 10~38° 흔들리는 값이 나온다. 근거 문서: `docs/research/04_swinglab_implications.md`, `docs/research/phase_diag/AFTER.md` 5절, `RUNNING.md`

## 2. 할 일
1. 문헌 근거 확인(이미 정리된 `docs/research/01~04`·`references.bib` 우선, 새 출처는 실제로 열어 확인): 어깨·골반 축 회전과 X-Factor의 정의(어드레스 대비, 탑에서의 차이 등)
2. MediaPipe `pose_world_landmarks`(미터 단위 3D)로 **수직축 기준 회전각** 계산: 어깨선(11→12)·골반선(23→24)을 수평면에 투영 → 어드레스 프레임 대비 회전각(부호 있는 각도, 연속 unwrap). X-Factor = 백스윙 톱(또는 최대 분리 시점)에서 어깨 회전 − 골반 회전. world_landmarks가 없거나 가시성이 낮으면 기존 방식으로 폴백하고 표시
3. 기존 2D 함수는 지우지 말고 새 함수 추가 + 파이프라인에서 선택(기본 = 새 방식), frame_data에 두 값을 모두 기록해 비교 가능하게
4. 평가(정답 데이터 없음 → 타당성 지표로): 앱 영상 7개 + GolfDB 캐시 일부(face-on·DTL 각 25)에서 (a) 음수 X-Factor 비율 (b) 정면/후방 촬영 간 값 차이 (c) 같은 영상 Mac vs Docker 차이 (d) 문헌 범위(프로·아마추어 X-Factor 대략 수십 도)와의 비교 — 구버전 vs 신버전 표
5. Docker pytest 통과(스냅샷 재생성 시 전/후 차이 보고), web build·lint
6. 보고서 `docs/research/xfactor/REPORT.md`: 정의·근거·식, 전/후 표, 점수 변화 표, 임계값 재설정 제안(적용 안 함), 한계, 커밋 묶음 제안
