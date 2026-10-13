# GolfDB 규칙 보정 재실행

원본 `~/PycharmProjects/golf_swing` 및 8010 서버는 사용하지 않는다. 커밋·브랜치 변경·설치 없음.
실행 위치는 이 worktree 루트. 캐시/영상/프레임/클립 결과는 모두 `~/datasets/golfdb_pose`.
GolfDB는 CC BY-NC 4.0의 비상업 연구·평가 용도로만 사용한다.

## 순서

1. `git archive 3bdf45d golf_swing_analyzer server tests web/public/samples`를
   `~/datasets/golfdb_pose/baseline`에 추출한다. 기준선 파일은 이후 수정하지 않는다.
2. 아래 Docker 실행에 `cache.py --shard 0 --shards 3` 등을 전달한다.
   shard 0/1/2를 각각 실행하고 모두 종료될 때까지 기다린다. 완료 JSON이 있는 클립은 재추론하지 않는다.
3. Docker에서 `apps.py before`, `verify_cache.py 6 14 21`을 실행한다.
4. 캐시 완료 후 `check_defaults.py`, `train.py --fold 1`, `--fold 2`, `--fold 3`, `--fold all`.
   이 단계는 NumPy/표준 라이브러리만 사용하므로 호스트의 기존 `.venv/bin/python -B`도 가능하다.
   호스트 실행 시 `PHASE_DATA=$HOME/datasets/golfdb_pose PYTHONDONTWRITEBYTECODE=1`을 설정한다.
   `.venv`는 원래 폴더에 대한 심볼릭 링크이므로 설치·바이트코드 쓰기를 금지한다.
5. `fit_all.json`의 params를 `phase_parameters.py`의 `CALIBRATED_PARAMETERS`에 반영한다.
   Docker `apps.py after --export`로 자동 스캔부터 7개 영상을 재추론한다.
   캐시 제약은 고정된 baseline 창의 신호 검사이므로 실제 재추론 0거부 확인도 필요하다.
6. Docker pytest/스냅샷/웹 확인 후 `holdout.py freeze`, 마지막으로 `holdout.py evaluate` **한 번만**.
   `frozen.json`에 소스·파라미터·캐시 해시, `audit.jsonl`에 시각이 기록된다.
   `split4_once.lock`은 실패해도 소비되며 삭제/재평가하지 않는다. 평가 후 재튜닝 금지.
7. `provenance.py --final`, `report.py`로 완료 증거와 요약 보고서를 만든다.
   `validation_commands.json`에는 실제 명령, exit code, 절대 로그 경로를 저장한다.
   freeze는 사전 계획/탐색 해시, 학습 split/횟수, 테스트 exit code, 원래 폴더 status/해시도 확인한다.

```bash
docker run --rm --platform linux/amd64 --network none --cpus 2 \
  -e PYTHONDONTWRITEBYTECODE=1 -e OPENBLAS_NUM_THREADS=1 -e OMP_NUM_THREADS=1 \
  -v "$PWD:/work:ro" -v "$HOME/datasets:/datasets" -w /work \
  golf-server:baseline python tools/phase_train/cache.py --shard 0 --shards 3
```

`apps.py`는 `before`에 실제 원본 코드, `after`에 현재 코드를 사용한다. 생성 샘플은 먼저
레포 밖 `golfdb_pose/samples`에 저장한다. 최종 채택 후 `web/public/samples`로 복사한다.
복사할 때 JSON을 compact 형식으로 저장한다(내용·이미지는 그대로 유지).
파라미터 탐색은 미리 고정한 grid의 2회 좌표 하강, 동점이면 기존 값 유지다.
fold 평가값을 보고 grid를 바꾸지 않는다. 목적함수는 4이벤트 PCE 평균, 거부도 오답이다.
`metric_available`은 각도 visibility와 컷 후 이전값 유지 규칙까지 복원한다.

## pytest 및 웹

최종값을 적용하고 샘플을 복사한 뒤 아래 명령으로 스냅샷 재생성·pytest·웹 build/lint를
순서대로 실행하고 `validation_commands.json`을 기록한다. 코드 동결 전에 실행한다.

```bash
PHASE_DATA="$HOME/datasets/golfdb_pose" PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -B tools/phase_train/checks.py --regen-snapshot
```

pytest 단독 명령:

```bash
docker run --rm --platform linux/amd64 --network none \
  -e PYTHONDONTWRITEBYTECODE=1 -e PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  -e PYTHONPATH=/testdeps -e OPENBLAS_NUM_THREADS=1 \
  -v "$PWD:/work" -v /private/tmp/phase_testdeps:/testdeps:ro -w /work \
  golf-server:baseline python -m pytest -q
```

`/private/tmp/phase_testdeps`는 기존 설치의 pytest 순수 Python 파일 복사본이다. 새 설치가 아니다.
의도한 결과 변경 시에만 같은 Docker에서 `python tests/regen_snapshot.py`를 실행한다.
`web/node_modules`가 원래 폴더를 가리키면 링크를 제거한 뒤 기존 설치를 로컬로 복사해야 한다.
설치 없이 `cd web && npm run build && npm run lint`를 실행한다.

```bash
PHASE_DATA="$HOME/datasets/golfdb_pose" PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -B tools/phase_train/holdout.py freeze
PHASE_DATA="$HOME/datasets/golfdb_pose" PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -B tools/phase_train/holdout.py evaluate
PHASE_DATA="$HOME/datasets/golfdb_pose" PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -B tools/phase_train/provenance.py --final
PHASE_DATA="$HOME/datasets/golfdb_pose" PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -B tools/phase_train/report.py
```

원래 폴더의 기존 `.venv`를 읽기 전용으로 사용하므로 호스트 Python 명령은 항상 `-B` 및
`PYTHONDONTWRITEBYTECODE=1`을 유지한다. `continue_development.py`는 556개를 기다린 뒤
4개 fit만 실행하며 freeze/evaluate는 수행하지 않는다. 기존 runner가 실행 중이면 추가 실행 금지.

## 자료 구조·한계

- NPZ: `landmarks[T,33,4]` (x,y,z,visibility), `signals[T,3]` (pixel y,x,torso),
  원본 frame/time/local_idx, 해상도, fps, grayscale 컷 입력 `[T,36,64]`, 컷 프레임.
  실제 fps 30±0.15 외에는 상태 JSON에 이유를 기록하고 제외한다.
- 600프레임 초과: 모든 프레임 cache에 더해 실제 파이프라인 간격으로 별도 추론한 `adaptive_*`.
  MP 추적은 입력 간격에 의존하므로 dense pose를 단순히 솎지 않는다.
- cache 단계의 split 4 접근은 라벨 없는 전처리다. 이벤트별 평가/오차 열람은 최종 1회뿐이다.
- 이전 진단 보고서에는 split 4 일부 평가와 전체 split을 포함한 과거 결과가 이미 있다.
  이번 실행의 단회 잠금은 과거 연구의 노출을 취소하지 않는다.
- 새로운 독립 실험은 별도 결과 루트와 사전 계획이 필요하다. 기존 잠금을 지워 재튜닝하지 않는다.
