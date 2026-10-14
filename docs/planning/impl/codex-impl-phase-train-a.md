# Codex 지시 — 단계 인식 학습 A안 (GolfDB로 규칙 보정)

작성 2026-10-13 · 작업 위치 **`~/PycharmProjects/golf_swing_train`** (git worktree, 브랜치 `feature/phase-train`, 시작점 `3bdf45d` = dev)
배경: 중간발표(10-15)는 `~/PycharmProjects/golf_swing`(dev)의 현재 코드로 시연한다. 이 작업은 **발표 후에만 반영**할 실험 브랜치다.

## 0. 절대 규칙
| # | 규칙 |
|---|---|
| Z1 | **`~/PycharmProjects/golf_swing`(원래 폴더) 안의 파일을 읽기 외에 절대 수정하지 않는다.** 실행 중인 8010 서버를 끄거나 재시작하지 않는다 |
| Z2 | git 커밋·브랜치 변경·merge 금지(샌드박스 제약). 커밋 묶음(묶음당 200줄 이하)만 제안 |
| Z3 | 새 패키지 금지 — NumPy·SciPy·OpenCV·MediaPipe만. 필요하면 이름·이유·라이선스를 보고서에 제안만 |
| Z4 | **평가 데이터 분리:** 파라미터·정의는 GolfDB **split 1–3**에서만 정한다(필요하면 split 단위 3-fold 교차검증). **split 4는 마지막에 한 번만** 평가하고, 그 결과로 다시 조정하지 않는다. 조정 과정에서 split 4를 봤다면 보고서에 명시 |
| Z5 | GolfDB 영상·프레임·포즈 캐시는 레포 밖(`~/datasets/golfdb_pose/`)에만 저장(CC BY-NC 4.0, 비상업 평가·연구 용도) |
| Z6 | 포즈 추론은 Docker `golf-server:baseline`(linux/amd64)에서. 환경을 결과에 명시 |
| Z7 | 점수 임계값(A6)·지표 계산식 변경 금지. `.claude/skills/golf-code-change/SKILL.md` A1–A9 준수(A9 등 의도적 변경은 근거와 함께 보고) |

## 1. 먼저 읽을 것
- `docs/research/phase_diag/REPORT.md`, `AFTER.md`(9절 포함), `golf_swing_analyzer/analyzer/phase_detector.py`, `pipeline.py`, `video_signal.py`
- `tests/phase_fix_eval.py`(GolfDB 평가 방식·PCE 정의 — 그대로 재사용), `docs/research/golfdb_eval/README.md`
- GolfDB 라벨: `~/datasets/golfdb/golfdb_annotations.json` — `events[1:9]`(원본 프레임) = Address, Toe-up, Mid-backswing, Top, Mid-downswing, Impact, Mid-follow-through, Finish. `events[0]`은 클립 시작 오프셋. 영상 `~/datasets/golfdb/videos_160/{id}.mp4`

## 2. 단계
### S1. 포즈 캐시 (한 번만)
- 대상: `slow=0` 이고 view가 `face-on`/`down-the-line`인 클립 전부(split 1–3 약 407개, split 4 약 149개). 실제 fps 30±0.15가 아니면 제외하고 목록 기록
- Docker에서 현재 파이프라인과 **같은 MediaPipe 설정**으로 매 프레임 추론 → 클립별 npz: 프레임별 33관절 x,y,z,visibility, 현재 코드가 쓰는 손목 신호·몸통 길이·컷 판정 입력값
- 병렬 컨테이너 사용 가능(CPU 코어 고려). 소요 시간·실패 클립 기록

### S2. 보정 대상 정의
현재 `phase_detector.py`의 판정 요소를 파라미터로 노출(기본값 = 현재 동작과 완전히 동일, 테스트로 확인):
- 톱: 평탄 구간 허용폭(현재 몸통 5%), 톱 시점 오프셋(손목 정점 → 클럽 톱 지연 보정)
- 어드레스(앱 "백스윙" 시작 경계): GolfDB Address = 테이크어웨이 직전. 현재 onset 임계(상승폭 10%)와 시간 창
- 임팩트: 탐색 창, argmax 유지(A2)
- 피니시(앱 "피니시" 시작 경계): GolfDB Finish = 스윙을 풀기 직전 마지막 자세. 현재 follow 최소점 정의를 GolfDB 정의에 맞출 후보 규칙(예: 손목 속도가 일정 시간 이하로 떨어지는 첫 시점)
- 스무딩 창(초)
각 파라미터의 탐색 범위와 근거(문헌·데이터)를 표로

### S3. 학습(보정)
- split 1–3 캐시로 파라미터 탐색(그리드/좌표 하강 등, NumPy만). 목적함수 = 4개 이벤트 PCE 평균(허용오차는 기존과 동일) + 7개 앱 영상에서 거부 0건 제약
- split 단위 3-fold로 과적합 확인(fold별 PCE 표)
- 최종 파라미터 선택 근거

### S4. 평가 (마지막에 한 번)
- split 4 전체(약 149개): **현재 코드(3bdf45d) vs 보정 후**, 이벤트별·방향별 PCE, 오차 중앙값, 5프레임 이내 비율
- 7개 앱 영상(`golf_swing_analyzer/video/` 3개 + `~/datasets/test_videos/` 4개): 자동 창, 톱/임팩트 원본 프레임 vs `docs/research/phase_diag/data/manual_reference.json`, 점수 전/후, 거부 여부 — 악화 사례는 그대로 보고
- Docker pytest 전부 통과(스냅샷은 `tests/regen_snapshot.py`로만 재생성, 전/후 차이 보고), 웹 build·lint

### S5. B안 검토(구현하지 않음)
관절 시계열 학습 모델(예: 1D CNN/GRU로 프레임별 이벤트 확률)의 설계안: 입력 특징, 라벨, 학습/평가 분리, 필요한 패키지(PyTorch 등 버전·라이선스·이미지 크기 영향), 추론 속도 예상, A안 대비 기대치와 근거. 설치·학습 금지

## 3. 산출물
- 코드 변경: `golf_swing_analyzer/analyzer/`(파라미터화·보정값), 필요 시 `tests/`(새 테스트), `web/public/samples/*.json` 재생성
- 스크립트: `tools/phase_train/`(캐시·탐색·평가, 재실행 명령 포함)
- 보고서: `docs/research/phase_train/REPORT.md` — 한 줄 결론, split 4 전/후 표, fold 표, 7개 영상 표, 파라미터 표(전/후·근거), 한계, B안 검토, 커밋 묶음 제안
- 대용량 결과(캐시·클립별 JSON)는 레포 밖 또는 `docs/research/phase_train/data/`에 요약만

## 4. 완료 기준
1. 기본 파라미터에서 현재 동작과 결과 동일(회귀 테스트)
2. split 4 평가가 split 1–3 보정 후 단 한 번 수행됨을 로그로 증명
3. Docker pytest 통과, web build·lint exit 0
4. 7개 앱 영상 거부 0건
5. `git -C ~/PycharmProjects/golf_swing status`가 작업 전과 동일(원래 폴더 무변경)
