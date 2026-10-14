"""Platform math parity on identical Docker pose inputs; NOT native pose parity."""
import copy
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "golf_swing_analyzer"))
from analyzer.rotation import apply_world_rotations
from analyzer.scoring import compute_summary, compute_score

data = Path(sys.argv[1])
rows = []
for p in sorted(data.glob("apps_*.json")):
    r = json.loads(p.read_text())
    fd = apply_world_rotations(copy.deepcopy(r["raw_frame_data"]), r["top_frame"])
    summary = compute_summary(fd)
    score, _ = compute_score(summary, {})
    assert summary == r["after"]["summary"], p.name
    assert score == r["after"]["score"], p.name
    rows.append(dict(name=r["name"], exact_summary_match=True, x_factor_difference=0., score_difference=0))
result = dict(platform=platform.platform(), python=platform.python_version(), numpy=np.__version__,
              native_pose_inference=False, input="Docker pose headings and legacy frame metrics", rows=rows)
(ROOT / "docs/research/xfactor/mac_math_parity.json").write_text(json.dumps(result, ensure_ascii=False)+"\n")
print("Math parity PASS", len(rows), "videos; native pose comparison NOT performed")
