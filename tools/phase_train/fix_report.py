"""Render compact fix evidence after the one-time second holdout exposure."""
import json
import re
import subprocess

from common import DATA, ROOT, dump
from fix_common import PRIOR, REFERENCES


def read(name):
    return json.loads((DATA/name).read_text())


def main():
    ab = read('ablations.json')
    selected = read('selection.json')
    apps = read('apps_after.json')
    hold = read('split4_summary.json')
    lines = ['# 학습 A안 보정 — 앱 영상 회귀 수정', '',
             '기준 `3bdf45d` / A안 `090dd9f` / 수정안 미커밋. 2026-10-14.', '',
             '앱 7개 Top/Impact 참조 거리 비악화·거부 0·점수 비하락과 3-fold 평균 PCE 하락 ≤1%p를 통과했다.',
             '**split 4는 두 번째 노출**이다. 기존 A 평가를 본 뒤 수행한 보정이므로 독립 최초 holdout이 아니다.', '',
             '## 1. 단독 되돌림 원인 표', '',
             '셀은 **Top / Impact / 점수**(0-based 원본 프레임). 각 행은 A의 해당 파라미터 하나만 복원한다.',
             '자동 스캔 신호는 재사용하고 서로 다른 트림 20개를 Docker에서 재추론했다.',
             '기준선/A의 전체 summary·경계·점수가 이전 실제 실행과 정확히 일치했다.', '']
    names = list(apps)
    lines += ['| 복원 파라미터 | '+' | '.join(names)+' |',
              '|---|'+'---|'*len(names)]
    for key, values in ab.items():
        cells = [f"{values[n]['top']}/{values[n]['impact']}/{values[n]['score']}" for n in names]
        lines.append('| '+key+' | '+' | '.join(cells)+' |')
    lines += ['', '단독 실험의 효과는 다른 파라미터가 A값일 때의 조건부 효과다. 상호작용의 기여율로 해석하지 않는다.', '',
              '- Impact 창 `.75→1.25`는 8065880 Impact `152→158`, 6541855 Top `127→115`를 만든다. 짧은 창이 이른 Top 후보도 탈락시켰다.',
              '- plateau `.025→.05` 단독은 8065880 Impact 155, 6541855 Impact 136으로 충분하지 않다.',
              '- smooth `1/6→.1` 단독은 6541855를 Top 157 / Impact 170으로 악화시킨다. 스무딩 전체 복원은 채택하지 않았다.',
              '- Address offset `−.2→0`만 붉은 옷 영상 점수를 `45→55`로 복원한다. 기존 창의 어드레스 유효 각도 행 4→10, 오른 무릎 평균 165.6→163.8°로 기존 165° 기준 통과 여부가 달라졌다.', '',
              '## 2. 선택 근거', '',
              '자동 스캔은 기준선 설정으로 고정해 MediaPipe 크롭·추적 문맥을 유지한다. 분석 plateau=.05, impact 창=1.25초.',
              'Address offset=−.2초는 남는 유효 관측량이 .3초 미만이고 원 onset으로 .3초 이상 회복될 때만 생략한다.',
              '가드는 기존 visibility/이전값 유지 행의 개수×시간 간격만 사용한다. 각도값·영상 ID·점수는 조건에 쓰지 않는다.',
              '나머지는 A값이다. 기본 PhaseParameters는 기존값을 유지하고 새 가드 기본값은 0(비활성)이다.', '',
              '첫 가드는 회복 불가능한 비가시 구간까지 onset을 복원해 3-fold −2.01%p로 탈락했다.',
              '회복 가능 조건을 추가한 동일 16개 후보 중 앱 경계·거부·점수 제약을 통과한 2개를 비교했다.',
              '각 fold는 나머지 두 split PCE로 선택하고 마지막에 407개 전체에서 재선택했다. 탐색적 선택이며 전역 최적을 보장하지 않는다.',
              '[계획·A1–A9](PROTOCOL_fix.md), 원자료 `~/datasets/golfdb_pose/fix_20261014/selection.json`.', '',
              '## 3. 앱 영상 7개 실제 재실행', '',
              '셀: `자동 창 초; Top/Impact; 점수`. 마지막 열은 수동 Top / Impact 범위다.', '',
              '| 영상 | 3bdf45d | A안 | 수정안 | 참조 |', '|---|---|---|---|---|']
    prior = json.loads((PRIOR/'apps_after.json').read_text())
    baseline = json.loads((PRIOR/'apps_before.json').read_text())
    for n in names:
        cells = []
        for r in (baseline[n], prior[n], apps[n]):
            cells.append(f"{r['window'][0]:.3f}–{r['window'][1]:.3f}; {r['bounds']['백스윙 톱'][0]}/{r['bounds']['임팩트'][0]}; {r['score']}")
        ref = REFERENCES[n]
        lines.append('| '+n+' | '+' | '.join(cells)+f" | {ref['top_bracket']} / {ref['impact_bracket']} |")
    lines += ['', '세 버전 모두 거부 0. 수정안 대표 이미지 49장 모두 해당 원본 프레임 경계 안에 있다.',
              '점수는 빈 reference_db의 기존 하드코딩 폴백이다. 점수 상승은 정확도 향상 증거가 아니다.',
              '6541855 Top 118은 여전히 참조 상한보다 1프레임 늦다. pro2/34883764는 기존과 같은 이른 연습 스윙을 선택하며 수동 참조의 실제 타격과 다르다.',
              '참조는 기존 한 사람의 탐색 범위이며 수정하지 않았다. 비악화 판정은 실제 타격 정확도 성공을 의미하지 않는다.', '',
              '## 4. GolfDB split 1–3 교차검증', '',
              '| 검증 split | n | A 원 fold 선택 PCE | 수정 fold 선택 PCE | 차이 %p | support 초 |',
              '|---|---:|---:|---:|---:|---:|']
    for f in ('1', '2', '3', 'all'):
        r = selected['folds'][f]
        a, b = r['A']['all']['mean_pce'], r['validation']['all']['mean_pce']
        lines.append(f"| {f} | {r['validation']['all']['n']} | {100*a:.2f}% | {100*b:.2f}% | {100*(b-a):+.2f} | {r['params']['address_min_valid_sec']} |")
    a, b = selected['A_fold_mean'], selected['fix_fold_mean']
    n = sum(selected['folds'][str(f)]['validation']['all']['n'] for f in (1, 2, 3))
    weighted = [sum(selected['folds'][str(f)]['validation']['all']['n']*
                    selected['folds'][str(f)][key]['all']['mean_pce'] for f in (1, 2, 3))/n
                for key in ('A', 'validation')]
    lines += ['', f'3-fold 산술 평균 {100*a:.2f}%→{100*b:.2f}%（{100*(b-a):+.2f}%p）. fold 2는 단독으로 1%p 이상 하락하므로 모든 fold 비열등을 주장하지 않는다.',
              f'클립 수 가중 out-of-fold 평균 {100*weighted[0]:.2f}%→{100*weighted[1]:.2f}%.',
              'all 행은 전체 개발 재적합이며 독립 평가가 아니다. 고정 A 전체 개발 PCE와 최종 수정안 비교도 all 행에 표시했다.', '',
              '| 검증 split | Address A→수정 | Top A→수정 | Impact A→수정 | Finish A→수정 |', '|---|---|---|---|---|']
    for f in ('1', '2', '3'):
        r = selected['folds'][f]
        lines.append('| '+f+' | '+' | '.join(f"{100*r['A']['all']['events'][e]['pce']:.2f}%→{100*r['validation']['all']['events'][e]['pce']:.2f}%" for e in ('Address', 'Top', 'Impact', 'Finish'))+' |')
    lines += ['',
              '## 5. split 4 — 마지막 1회, 두 번째 노출', '',
              '| 방향/버전 | n | 거부 | Address | Top | Impact | Finish | 평균 PCE |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
    for view in ('all', 'face-on', 'down-the-line'):
        for name in ('baseline', 'A', 'fix'):
            r = hold[name][view]
            cells = [f"{100*r['events'][e]['pce']:.2f}%" for e in ('Address', 'Top', 'Impact', 'Finish')]
            lines.append(f"| {view}/{name} | {r['n']} | {r['rejected']} | "+' | '.join(cells)+f" | {100*r['mean_pce']:.2f}% |")
    lines += ['', '각 셀은 `오차 중앙값 프레임 / 5프레임 이내 비율`이다. 거부는 PCE·within5 분모에 포함한다.', '',
              '| 방향/버전 | Address | Top | Impact | Finish |', '|---|---|---|---|---|']
    for view in ('all', 'face-on', 'down-the-line'):
        for name in ('baseline', 'A', 'fix'):
            ev = hold[name][view]['events']
            lines.append(f'| {view}/{name} | '+' | '.join(f"{ev[e]['median_abs_error']:g} / {100*ev[e]['within5']:.2f}%" for e in ('Address', 'Top', 'Impact', 'Finish'))+' |')
    lines += ['', '평가 전에 소스·선택 결과·캐시를 동결하고 원자적 lock을 소비했다. 평가 후 재조정하지 않았다.',
              '감사 원자료: 새 결과 루트의 `frozen.json`, `audit.jsonl`, `split4_once.lock`, `completion.json`. 기존 A 잠금·audit는 보존했다.', '',
              '## 6. 완료 검증', '', '| 검증 | 결과 |', '|---|---|']
    for n, r in read('validation_commands.json').items():
        lines.append(f"| {n} | exit {r['exit_code']}; {r['log']} |")
    pytest_log = (DATA/'logs/pytest.log').read_text()
    passed = re.search(r'(\d+) passed', pytest_log).group(1)
    before = read('snapshot_before.json')
    after = json.loads((ROOT/'tests/snapshots/ilban_baseline.json').read_text())
    lines += ['', f'Docker 전체 pytest **{passed} passed**, skip 없음.',
              f"스냅샷 점수 {before['score']}→{after['score']}, summary `{before['summary']}`→`{after['summary']}`.",
              '기본값은 407개 개발 캐시·기존 합성 oracle 테스트에서 3bdf45d와 동일하다. 기존 테스트 삭제·완화·skip 추가 없음.',
              '새 가드는 15/30/60fps, 관측 충분/부족/회복 불가, 메타데이터 없는 live 호환성을 검사했다.',
              '샘플 3개와 스냅샷은 실제 Docker로 재생성했다. 웹 SSR에서 이전/새 샘플 각 7장·NaN 없음도 확인했다.',
              '포즈 환경은 기존 golf-server:baseline linux/amd64, Python 3.11.17/MP .10.21/OpenCV 4.10.0.84/NumPy 1.26.4, CPU 에뮬레이션이다.',
              '새 설치 없음. Streamlit 패키지는 기존 환경에 없어 기동 미검증이며 서버 import/분석은 pytest로 검증했다.',
              '발표용 저장소 status·추적 316개 해시 동일, HEAD 090dd9f 유지. 8010/ngrok 제어·dev 반영·커밋 없음.', '',
              '## 7. 커밋 묶음 제안 (실행하지 않음)', '',
              '각 묶음은 추가+삭제 합계 ≤200줄이다. 생성 샘플은 compact JSON이며 이미지 변경으로 바이트 diff는 크다.', '',
              '| 묶음 | 파일/내용 |', '|---|---|',
              '| 1 | analyzer 3개 + replay.py + test_phase_address_support.py |',
              '| 2 | fix_common.py + fix_apps.py |',
              '| 3 | fix_search.py + apps.py 변경 + PROTOCOL_fix.md |',
              '| 4 | fix_holdout.py |',
              '| 5 | fix_report.py |',
              '| 6 | 샘플 3개 + 공식 스냅샷 |',
              '| 7 | REPORT_fix.md + fix_summary.json(compact) |',
              '| 8 | tools README 보정 안내 |', '',
              '기존 미추적 .venv 링크·작업지시서·codex 로그는 제외한다. 대용량 캐시/클립 결과는 레포 밖에 유지한다.']
    text = '\n'.join(lines)+'\n'
    (ROOT/'docs/research/phase_train/REPORT_fix.md').write_text(text)
    groups = [
        ['golf_swing_analyzer/analyzer/'+n for n in ('phase_detector.py', 'phase_parameters.py', 'pipeline.py')]+['tools/phase_train/replay.py', 'tests/test_phase_address_support.py'],
        ['tools/phase_train/'+n for n in ('fix_common.py', 'fix_apps.py')],
        ['tools/phase_train/fix_search.py', 'tools/phase_train/apps.py', 'docs/research/phase_train/PROTOCOL_fix.md'],
        ['tools/phase_train/fix_holdout.py'], ['tools/phase_train/fix_report.py'],
        ['web/public/samples/'+n+'.json' for n in ('il-ban', 'pro', 'pro2')]+['tests/snapshots/ilban_baseline.json'],
        ['docs/research/phase_train/REPORT_fix.md', 'docs/research/phase_train/data/fix_summary.json'],
        ['tools/phase_train/README.md']]
    compact = dict(selection={k: v for k, v in selected.items() if k != 'candidates'},
                   split4=hold, completion=read('completion.json'))
    (ROOT/'docs/research/phase_train/data/fix_summary.json').write_text(
        json.dumps(compact, ensure_ascii=False, separators=(',', ':'))+'\n')
    counts = []
    for files in groups:
        count = 0
        for name in files:
            result = subprocess.check_output(['git', 'diff', '--numstat', '--', name]).decode().strip()
            tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', name], capture_output=True).returncode == 0
            count += sum(map(int, result.split()[:2])) if result else (0 if tracked else len((ROOT/name).read_text().splitlines()))
        counts.append(count)
    counts[6] += 2  # blank line plus the measured-count line appended below
    assert max(counts) <= 200, counts
    dump(DATA/'commit_bundles.json', [dict(files=f, changed_lines=c) for f, c in zip(groups, counts)])
    output = ROOT/'docs/research/phase_train/REPORT_fix.md'
    output.write_text(output.read_text()+'\n실측 추가+삭제 줄 수(묶음 1–8): '+', '.join(map(str, counts))+'.\n')


if __name__ == '__main__':
    main()
