# 재현 명령

작업 CWD: `/Users/mose/PycharmProjects/golf_swing_xfactor`. 새 패키지 설치 없음, 포트 공개 없음. 아래 baseline 디렉터리는 변경 전 `3bdf45d`의 analyzer/server/tests 복사본이다. 다시 준비할 때는 해당 Git revision의 코드만 별도 디렉터리에 추출한다. 실제 발표용 레포는 변경하지 않는다.

기존 pytest 의존성 복사본 `/private/tmp/phase_testdeps`는 이번에도 그대로 사용했다. 데이터셋 `/Users/mose/datasets`는 입력이며, capture 출력은 `/Users/mose/datasets/xfactor_eval/docker`다. 동일 결과 파일을 덮어 새 capture를 주장하지 않으려면 별도 output 디렉터리를 지정한다.

## 기준 포즈 수집

```bash
docker run --rm --network none --platform linux/amd64 \
  -v /Users/mose/PycharmProjects/golf_swing_xfactor:/work:ro \
  -v /private/tmp/xfactor_baseline_3bdf45d:/baseline:ro \
  -v /Users/mose/datasets:/datasets:ro \
  -v /Users/mose/datasets/xfactor_eval/docker:/output \
  -w /work -e PYTHONDONTWRITEBYTECODE=1 golf-server:baseline \
  python tools/xfactor_eval.py capture --group apps
```

같은 명령의 마지막 인자를 `--group golfdb` 또는 `--group snapshot`으로 바꿔 실행한다. GolfDB 선택은 selection.json에 고정돼 있으며 기존 결과가 있으면 건너뛴다. before 수치와 feature 수치는 같은 pose stream에서 나온다. world NPZ도 별도 output에 저장한다.

최신 feature 계산식을 같은 pose에 적용할 때는 `capture` 대신 `summarize`를 쓰고 group을 동일하게 지정한다. 이 명령은 해당 group의 JSON after 결과와 `results_<group>.json`만 다시 계산하며 새로운 포즈 추론을 하지 않는다.

## 실제 feature 파이프라인 및 public samples

```bash
docker run --rm --network none --platform linux/amd64 \
  -v /Users/mose/PycharmProjects/golf_swing_xfactor:/work \
  -v /Users/mose/datasets:/datasets:ro \
  -w /work -e PYTHONDONTWRITEBYTECODE=1 golf-server:baseline \
  python tools/xfactor_verify.py
```

apps capture를 최신 feature로 summarize한 뒤 실행한다. 7개 전체 summary·점수·단계 경계·frame/annotated/trajectory 원본 키를 대조하고 대표 사진 7개를 검사한다. public samples 3개와 pipeline_verification.json을 갱신한다. 기존 서버를 띄우거나 8010에 요청하지 않는다.

## Docker pytest 및 스냅샷

```bash
docker run --rm --network none --platform linux/amd64 \
  -v /Users/mose/PycharmProjects/golf_swing_xfactor:/work:ro \
  -v /private/tmp/phase_testdeps:/testdeps:ro \
  -w /work -e PYTHONPATH=/testdeps -e PYTHONDONTWRITEBYTECODE=1 \
  -e PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 golf-server:baseline \
  python -m pytest -q -p no:cacheprovider
```

의도된 변경 이후의 스냅샷 재생성은 위 `/work` mount를 writable로 바꾸고 마지막 명령을 `python tests/regen_snapshot.py`로 바꾼다. 재생성 전/후 차이를 REPORT에 기록하고 마지막에 전체 pytest를 실행한다. 현재 스냅샷은 이미 이 절차로 재생성돼 있다.

## Mac 비교의 범위

Native 비교 시도 명령은 아래와 같았으며 7개 모두 OpenGL 생성 실패로 포즈 출력이 없었다. 아래 capture는 패키지와 venv를 읽기만 하고 결과는 별도 디렉터리에 쓴다.

```bash
.venv/bin/python -B tools/xfactor_eval.py capture \
  --root /Users/mose/PycharmProjects/golf_swing_xfactor \
  --baseline /private/tmp/xfactor_baseline_3bdf45d \
  --datasets /Users/mose/datasets \
  --output /Users/mose/datasets/xfactor_eval/mac --group apps
```

같은 Docker pose 입력의 수치 계산만 확인하는 명령:

```bash
.venv/bin/python -B tools/xfactor_math_parity.py /Users/mose/datasets/xfactor_eval/docker
```

이 결과는 native Mac MediaPipe의 정확도·차이 검증이 아니다. native capture가 실패 상태이면 측정 불가로 남긴다. Streamlit도 설치되어 있지 않아 기동 검증을 수행하지 못했다.

## Web build/lint와 발표용 symlink 보호

`web/node_modules`는 발표용 node_modules를 읽는 symlink다. 아래 표준 라이브러리 스크립트는 TypeScript build info 경로만 임시로 바꾸고 항상 복원한다. Vite runner loader를 지정해 외부 node_modules에 config 번들 임시 파일을 쓰지 않는다. 출력은 이 작업 폴더의 `web/dist`, 로그는 보고서 폴더다.

```python
from pathlib import Path
import re, subprocess
root = Path.cwd()
web = root / "web"
logs = root / "docs/research/xfactor"
configs = [web / "tsconfig.app.json", web / "tsconfig.node.json"]
originals = {p: p.read_text() for p in configs}
try:
    for p in configs:
        p.write_text(re.sub(r'"tsBuildInfoFile": "[^"]+"',
            f'"tsBuildInfoFile": "/private/tmp/xfactor-{p.stem}.tsbuildinfo"', originals[p]))
    with (logs / "web_build.log").open("w") as log:
        subprocess.run(["npm", "run", "build", "--", "--configLoader", "runner"],
                       cwd=web, stdout=log, stderr=subprocess.STDOUT, check=True)
finally:
    for p, value in originals.items():
        p.write_text(value)
with (logs / "web_lint.log").open("w") as log:
    subprocess.run(["npm", "run", "lint"], cwd=web,
                   stdout=log, stderr=subprocess.STDOUT, check=True)
```

`comparison.csv`는 results_apps.json/results_golfdb.json의 각 before/after summary·score를 영상별로 추출한 표다. metrics.json은 같은 기록의 그룹별 음수 수, mean/median/min/max, 기존 20–80° 포함 수를 요약한다. valid_3d 집합은 after의 `x_factor_method == "world_3d_top"`인 영상으로 양 버전 모두 동일하게 제한했다.
