"""Regenerate the three shipped samples through the actual /analyze endpoint."""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/research/phase_diag/after'
os.environ['DATABASE_URL']='sqlite:///'+tempfile.mktemp(suffix='.db')
os.environ['JWT_SECRET']='local-phase-sample-validation-only-123456789'
for key in ('GEMINI_API_KEY','ANTHROPIC_API_KEY','OPENAI_API_KEY'):
    os.environ[key]=''
sys.path.insert(0,str(ROOT/'server'))
from fastapi.testclient import TestClient
from main import app

with TestClient(app) as client:
    for name,filename in [('il-ban','일반.mp4'),('pro','프로.mp4'),('pro2','프로2.mp4')]:
        measured=json.loads((OUT/f'after_{name}.json').read_text())
        start,end=measured['window']
        with (ROOT/'golf_swing_analyzer/video'/filename).open('rb') as f:
            res=client.post('/analyze',data={'start_sec':start,'end_sec':end,'sample_rate':3},
                            files={'file':(filename,f,'video/mp4')})
        assert res.status_code==200,res.text[:300]
        payload=res.json()
        assert payload['score']==measured['score']
        assert payload['phase_boundaries_frames']==measured['bounds']
        assert len(payload['rep_frames'])==7
        (ROOT/f'web/public/samples/{name}.json').write_text(json.dumps(payload,ensure_ascii=False))
        print(name,payload['score'],len(payload['rep_frames']),flush=True)
