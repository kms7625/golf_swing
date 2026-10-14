"""Confirm development caches still match the production sampling/cut clock."""
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/phase_train'))
from common import DATA, annotations, dump
from analyzer.video_clock import analysis_step
from analyzer.video_signal import SceneCuts


def main():
    cv2.setNumThreads(1)
    records = []
    for row in annotations([1, 2, 3]):
        with np.load(DATA/'cache'/f"{row['id']}.npz", allow_pickle=False) as cache:
            fps, total = float(cache['fps']), int(cache['total'])
            prefix = 'adaptive_' if 'adaptive_step' in cache else ''
            expected_step = int(cache[prefix+'step'])
            cut = SceneCuts(fps)
            actual = []
            for i, gray in enumerate(cache['cut_gray']):
                if cut.update(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), i): actual.append(i)
            expected_cuts = cache['cut_frames'].tolist()
            records.append(dict(id=row['id'], split=row['split'], fps=fps, total=total,
                 step_before=expected_step, step_after=analysis_step(total, fps),
                 cuts_before=expected_cuts, cuts_after=actual,
                 parity=expected_step == analysis_step(total, fps) and expected_cuts == actual))
    dump(DATA/'engine_accuracy_20261014/cache_clock.json', dict(records=records, splits=[1, 2, 3]))
    print('clock parity', sum(r['parity'] for r in records), '/', len(records), flush=True)
    if not all(r['parity'] for r in records): raise SystemExit(1)


if __name__ == '__main__':
    main()
