# 엔진 정확도 연구 재현

기준 `b8eace6` / `feature/engine-accuracy`. 결과는 레포 밖
`/Users/mose/datasets/golfdb_pose/engine_accuracy_20261014/`에 저장한다.
split 4 캐시/영상/평가 파일은 사용하지 않는다. 새 설치와 포트 개방은 없다.

`evaluate.py`는 split 1–3만 읽어 기준선·고정 최종값·fold 선택을 기록한다.
`cache_clock.py`는 같은 개발 영상의 저장된 grayscale로 컷·표본 간격을 검증한다.
`shot_probe.py`는 앱 선택/수동 참조 구간 및 개발 split당 첫 10개를 조사한다.
공 분류기가 아니며 밝은 물체 개수/소실을 공 접촉 정답으로 사용하지 않는다.

Docker 공통 실행(실제 경로는 현재 worktree와 datasets뿐):

```sh
docker run --rm --platform linux/amd64 --network none \
  -e PYTHONDONTWRITEBYTECODE=1 -e PHASE_DATA=/datasets/golfdb_pose \
  -v "$PWD":/work:ro -v /Users/mose/datasets:/datasets:ro \
  -v /Users/mose/datasets/golfdb_pose/engine_accuracy_20261014:/datasets/golfdb_pose/engine_accuracy_20261014 \
  -w /work golf-server:baseline python tools/engine_accuracy/evaluate.py final
```

마지막 Python 인자를 `cache_clock.py`, `shot_probe.py`, `fps_video.py final --avi`로
바꾸어 해당 산출물을 만든다. 기존 결과를 덮어쓰므로 원 실행 보존 시 먼저 산출물을 별도 보관한다.
`baseline_analyzer/`는 변경 전에 현재 worktree의 analyzer만 동결 복사한 자료이며 별도 worktree가 아니다.
`fps_video.py baseline`은 이 동결 패키지를 사용한다. fold 탐색은 기존 호스트 Python/NumPy로 수행했다.

```sh
PHASE_DATA=/Users/mose/datasets/golfdb_pose PYTHONDONTWRITEBYTECODE=1 python3 tools/engine_accuracy/evaluate.py search
PHASE_DATA=/Users/mose/datasets/golfdb_pose python3 tools/engine_accuracy/fps_video.py prepare
PHASE_DATA=/Users/mose/datasets/golfdb_pose python3 tools/engine_accuracy/fps_video.py prepare --aligned
PHASE_DATA=/Users/mose/datasets/golfdb_pose python3 tools/engine_accuracy/fps_video.py rewrap
PHASE_DATA=/Users/mose/datasets/golfdb_pose python3 tools/engine_accuracy/summarize.py
```

최종 비교는 AVI의 명시적 30/60fps 시계를 사용한다. Matroska 초안과 실패도 보존한다.
`fps_commands*.json`, `fps_rewrap_commands.json`에 ffmpeg 명령과 변환 근거가 있다.
원본 24/25/29.97fps는 먼저 같은 30fps 대조로 변환한다. 재인코딩 대조의 점수는 원본 앱 점수와 다르다.
보간은 exact input clock 및 마지막 프레임 패딩 후 수행한다. 새로운 촬영 정보가 생긴 것은 아니다.

앱 전/후 실행은 `tools/phase_train/apps.py after --output apps_baseline.json|apps_final.json`을 사용했다.
`PHASE_DATA=/results`, `PHASE_SOURCE_DATA=/datasets/golfdb_pose`, 결과 루트를 `/results`로 writable mount한다.
최종 실행은 `cv2.setNumThreads(1)` 후 같은 스크립트를 runpy로 실행했다(추론/필터 설정은 동일).
샘플 재생성은 공통 Docker 명령에 samples와 snapshots의 해당 하위 폴더만 writable mount하고
`tools/engine_accuracy/regenerate.py`를 실행한다. 실제 `/analyze` 및 공식 `tests/regen_snapshot.py`를 사용한다.
API는 임시 SQLite·빈 LLM 키의 TestClient이며 서버 포트를 열지 않는다.

완료 검증은 사용자 지정 Docker 전체 pytest 및 `node tests/phase_web_compat.mjs`다.
산출물 요약은 `docs/research/engine_accuracy/summary.json`, 해석은 `REPORT.md`를 참조한다.
