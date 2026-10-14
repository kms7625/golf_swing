"""Regenerate shipped artifacts through the real API in baseline Docker only."""
import hashlib
import json
import os
import runpy
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get('PHASE_DATA', '/datasets/golfdb_pose'))
OUT = DATA/'engine_accuracy_20261014'
os.environ['DATABASE_URL'] = 'sqlite:///'+tempfile.mktemp(suffix='.db')
os.environ['JWT_SECRET'] = 'engine-artifact-validation-only-123456789'
for key in ('GEMINI_API_KEY', 'ANTHROPIC_API_KEY', 'OPENAI_API_KEY'):
    os.environ[key] = ''
sys.path[:0] = [str(ROOT/'server'), str(ROOT/'golf_swing_analyzer')]


def main():
    import cv2
    cv2.setNumThreads(1)
    from fastapi.testclient import TestClient
    from main import app
    expected = json.loads((OUT/'apps_final.json').read_text())
    assert len(expected) == 7 and all('error' not in r for r in expected.values())
    records = {}
    with TestClient(app) as client:
        for name, video in [('il-ban', '일반'), ('pro', '프로'), ('pro2', '프로2')]:
            target = ROOT/'web/public/samples'/f'{name}.json'
            before = target.read_bytes()
            source = ROOT/'golf_swing_analyzer/video'/f'{video}.mp4'
            start, end = expected[name]['window']
            with source.open('rb') as f:
                response = client.post('/analyze', data={'start_sec': start, 'end_sec': end, 'sample_rate': 3},
                                       files={'file': (source.name, f, 'video/mp4')})
            assert response.status_code == 200, response.text[:300]
            payload = response.json()
            assert payload['score'] == expected[name]['score']
            assert payload['phase_boundaries_frames'] == expected[name]['bounds']
            assert len(payload['rep_frames']) == 7
            target.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False))
            records[name] = dict(before_sha256=hashlib.sha256(before).hexdigest(),
                 after_sha256=hashlib.sha256(target.read_bytes()).hexdigest(), score=payload['score'],
                 reason='Time-based angle/world filters; actual source-frame API regeneration',
                 summary_before=json.loads(before)['summary'], summary_after=payload['summary'])
            print('sample', name, payload['score'], flush=True)
    target = ROOT/'tests/snapshots/ilban_baseline.json'
    previous = json.loads(target.read_text())
    runpy.run_path(str(ROOT/'tests/regen_snapshot.py'), run_name='__main__')
    records['snapshot'] = dict(before=previous, after=json.loads(target.read_text()),
                               reason='Official regen_snapshot.py in baseline Docker')
    (OUT/'artifact_regeneration.json').write_text(json.dumps(records, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
