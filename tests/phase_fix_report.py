"""Render comparison figures/tables from Docker evaluation JSON (no pose inference)."""
import base64
import csv
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'docs/research/phase_diag/after'
PHASES = ['어드레스','백스윙','백스윙 톱','다운스윙','임팩트','팔로우스루','피니시']
LABELS = ['Address','Backswing','Top','Downswing','Impact','Follow','Finish']
REF = json.loads((OUT.parent/'data/manual_reference.json').read_text())


def load(path):
    return json.loads(path.read_text()) if path.exists() else {}


def iou(a,b):
    overlap=max(0,min(a[1],b[1])-max(a[0],b[0]))
    return overlap/(max(a[1],b[1])-min(a[0],b[0]))


def figure(name,before,after):
    width,height=230,305
    out=Image.new('RGB',(width*7,height*2),'#f5f5f5')
    draw=ImageDraw.Draw(out)
    for row,data in enumerate((before,after)):
        for j,(phase,label) in enumerate(zip(PHASES,LABELS)):
            x,y=j*width,row*height
            if phase in data.get('images',{}):
                im=Image.open(io.BytesIO(base64.b64decode(data['images'][phase]))).convert('RGB')
                im.thumbnail((width-8,height-50))
                out.paste(im,(x+(width-im.width)//2,y))
            source=data.get('representatives',{}).get(phase,'?')
            text=f'{"BEFORE" if row==0 else "AFTER"} {label}\nsource f{source}'
            if row==0: text=f'BEFORE {label}\noriginal UI image'
            draw.text((x+5,y+height-44),text,fill='black')
    out.save(OUT/f'{name}_comparison.png')


rows=[]
for name,ref in REF.items():
    if not isinstance(ref,dict): continue
    before=load(OUT/f'before_{name}.json');after=load(OUT/f'after_{name}.json')
    if not before or not after: continue
    figure(name,before,after)
    fps=after.get('fps',before.get('fps',30))
    manual=[v/fps for v in ref['window_frames']]
    row={'video':name,'manual_window':manual,'before_window':before.get('window'),
         'after_window':after.get('window'),'before_score':before.get('score'),
         'after_score':after.get('score'),'before_sec':before.get('elapsed_sec'),
         'after_sec':after.get('elapsed_sec'),'error':after.get('error','')}
    for version,data in [('before',before),('after',after)]:
        if data.get('window'):row[version+'_iou']=iou(data['window'],manual)
        for phase,key in [('백스윙 톱','top'),('임팩트','impact')]:
            row[version+'_'+key]=data.get('bounds',{}).get(phase,[None])[0]
    row['top_reference']=ref['top_bracket'];row['impact_reference']=ref['impact_bracket']
    row['representatives']=after.get('representatives',{})
    rows.append(row)
(OUT/'sample_comparison.json').write_text(json.dumps(rows,ensure_ascii=False))
if rows:
    with (OUT/'sample_comparison.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

selection=load(OUT/'split4_selection.json')
pce=[]
for view in ['face-on','down-the-line','all']:
    selected=[r for r in selection if view=='all' or r['view']==view]
    for version in ['before','after']:
        records=[load(OUT/f'{version}_golfdb_{r["id"]}.json') for r in selected]
        if not all(records):continue
        row={'view':view,'version':version,'n':len(records),
             'rejected':sum('error' in r for r in records)}
        for event in ['Address','Top','Impact','Finish']:
            row[event]=sum(r['correct'][event] for r in records)/len(records)*100
        pce.append(row)
(OUT/'split4_pce.json').write_text(json.dumps(pce))
print(json.dumps({'samples':len(rows),'pce':pce},indent=2))
