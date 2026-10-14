"""Publish summaries only, after the single frozen holdout run has completed."""
import json
import shutil
from dataclasses import asdict

from common import DATA, EVENTS, ROOT, dump
from analyzer.phase_parameters import PhaseParameters
from train import GRID

OUT = ROOT/'docs/research/phase_train'


def read(name):
    return json.loads((DATA/name).read_text())


def pct(value):
    return f'{100*value:.2f}%'


def table(headers, rows):
    return ['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |',
            *['| '+' | '.join(map(str, row))+' |' for row in rows]]


def main():
    complete = read('completion.json')
    assert complete['final'] and complete['original']['status_identical']
    results = read('split4_summary.json')
    fit = {f: read(f'fit_{f}.json') for f in ('1', '2', '3', 'all')}
    before, after = read('apps_before.json'), read('apps_after.json')
    reference = json.loads((OUT/'data/manual_reference.json').read_text())
    selected = fit['all']['params']
    b, a = results['before']['all'], results['after']['all']
    commands = complete['command_results']
    cache = complete['cache']
    snapshot = dict(before=json.loads((OUT/'data/snapshot_before.json').read_text()),
                    after=json.loads((ROOT/'tests/snapshots/ilban_baseline.json').read_text()))
    lines = ['# 단계 인식 A안: GolfDB 규칙 보정', '',
             '2026-10-13 · `feature/phase-train` · 기준 `3bdf45d` · 발표 후 반영할 실험 브랜치', '',
             f'**한 줄 결론 — split 4 {a["n"]}개 4이벤트 평균 PCE는 '
             f'{pct(b["mean_pce"])} → {pct(a["mean_pce"])}; '
             '7개 앱 영상 거부 0건. 아래 이벤트별·앱별 악화와 잔여 실패를 함께 판단해야 한다.**', '',
             '## 1. 분리·측정 방법', '',
             '- 탐색 범위·2회 좌표 하강·동점 유지 정책은 [PROTOCOL](PROTOCOL.md)에 사전 고정했다. '
             'split 1–3만 보정했고 fold 결과로 grid를 변경하지 않았다.',
             '- GT=`events[1:9]−events[0]`, Address=앱 백스윙 시작, Top/Impact/Finish=단계 시작. '
             '허용오차는 기존 `tests/phase_fix_eval.py`와 같은 '
             '`max(round((Impact−Address)/30),1)` 원본 프레임. 거부/누락은 PCE·≤5 분모에 포함한다.',
             '- 오차 표는 절대오차 중앙값이며 예측이 있는 클립만 계산한다. '
             'GolfDB 8이벤트 RGB 모델의 PCE와 직접 비교하지 않는다.',
             '- 필수 읽기 자료에는 과거 split 4 일부/전체 split 평가와 오프셋 탐색이 있다. '
             '**역사적으로 미노출인 테스트셋은 아니다.** 이번 보정 중 새 split 4 결과를 보거나 '
             '이를 근거로 재조정한 일은 없으며 최종 평가 후 코드·파라미터를 유지했다.', '',
             '## 2. split 4: 기준선 대 보정 후', '']
    rows = []
    for view in ('all', 'face-on', 'down-the-line'):
        old, new = results['before'][view], results['after'][view]
        for event in EVENTS:
            x, y = old['events'][event], new['events'][event]
            rows.append([view, old['n'], event, pct(x['pce']), pct(y['pce']),
                         f'{x["median_abs_error"]} → {y["median_abs_error"]}',
                         f'{pct(x["within5"])} → {pct(y["within5"])}'])
    lines += table(['방향', 'n', '이벤트', 'PCE 전', 'PCE 후', '중앙 절대오차 f', '≤5프레임'], rows)
    lines += ['', f'전체 거부: {b["rejected"]} → {a["rejected"]}. '
              '방향별 평균 PCE: '+', '.join(
                  f'{v} {pct(results["before"][v]["mean_pce"])} → '
                  f'{pct(results["after"][v]["mean_pce"])}' for v in ('face-on','down-the-line'))+'.', '',
              '## 3. split 단위 3-fold 및 최종 선택', '']
    rows = []
    for fold in ('1', '2', '3', 'all'):
        r = fit[fold]
        x, y = r['before']['all'], r['after']['all']
        rows.append([fold, r['train_n'], r['validation_n'], r['candidates'],
                     f'{pct(x["mean_pce"])} → {pct(y["mean_pce"])}',
                     ', '.join(f'{e} {pct(x["events"][e]["pce"])}→{pct(y["events"][e]["pce"])}'
                               for e in EVENTS)])
    lines += table(['검증 split', '학습 n', '평가 n', '후보 수', '평균 PCE 전→후', '이벤트별 전→후'], rows)
    total_n = sum(fit[f]['validation_n'] for f in ('1', '2', '3'))
    oof = {v: sum(fit[f][v]['all']['mean_pce']*fit[f]['validation_n']
                  for f in ('1', '2', '3'))/total_n for v in ('before', 'after')}
    lines += ['', '`all`은 개발 데이터 재적합 성능이며 독립 평가가 아니다. '
              '최종값은 split 1–3 전체에서 동일한 탐색을 적용해 고른 제약 충족 최고값이다. '
              '전역 최적은 보장하지 않으며 앱 회귀 신호 14개는 학습의 거부 제약에 쓰였다.', '',
              f'클립 수로 가중한 out-of-fold PCE: {pct(oof["before"])} → {pct(oof["after"])}. '
              '세 fold에서 개선됐지만 과적합 부재나 스마트폰 영상 일반화를 보장하지 않는다. '
              'Top의 양의 고정 오프셋은 선택되지 않았고 평탄 허용폭·스무딩 보정이 채택됐다.', '',
              '## 4. 파라미터', '']
    defaults = asdict(PhaseParameters())
    lines += table(['파라미터', '기준값', '선택값', '사전 후보'],
                   [[k, defaults[k], selected[k], ', '.join(map(str, v))] for k, v in GRID.items()])
    lines += ['', '각 범위의 근거는 [사전 계획](PROTOCOL.md)의 대응 표에 있다. '
              '문헌은 이벤트 의미·시간 척도의 근거이고 범위 자체는 공학적 후보다. '
              'Top/Address 오프셋은 후보 순위 결정 후 순서를 보존하여 적용한다. '
              '안정 Finish는 손목 정지의 대리 지표이며 적격 유지 구간이 없으면 기존 최소점으로 폴백한다.', '',
              '## 5. 7개 앱 영상: 실제 Docker 자동 창→트림→재추론', '',
              '창은 원본 초, Top/Impact는 0-based 원본 프레임이며 대표 이미지와 구별한다. '
              '참조는 한 명의 기존 탐색 범위이며 GolfDB 정답처럼 취급하지 않는다.', '']
    rows, app_summary, regressions = [], {}, []
    for name in before:
        x, y, ref = before[name], after[name], reference[name]
        assert 'error' not in y
        def window(r):
            return '–'.join(f'{s:.3f}' for s in r['window'])
        rows.append([name, f'{window(x)} → {window(y)}',
                     f'{x["bounds"]["백스윙 톱"][0]} → {y["bounds"]["백스윙 톱"][0]} / {ref["top_bracket"]}',
                     f'{x["bounds"]["임팩트"][0]} → {y["bounds"]["임팩트"][0]} / {ref["impact_bracket"]}',
                     f'{x["score"]} → {y["score"]}', '0 → 0'])
        app_summary[name] = {v: {k: r[k] for k in ('window','fps','score','summary','bounds','representatives','quality')}
                             for v, r in (('before',x),('after',y))}
        for event, phase, bracket in (('Top', '백스윙 톱', 'top_bracket'),
                                       ('Impact', '임팩트', 'impact_bracket')):
            lo, hi = ref[bracket]
            def distance(r):
                frame = r['bounds'][phase][0]
                return max(lo-frame, frame-hi, 0)
            if distance(y) > distance(x):
                regressions.append(f'{name} {event}: 참조 범위까지 거리 {distance(x)}→{distance(y)}f')
    lines += table(['영상', '자동 창 전→후(초)', 'Top 전→후 / 참조', 'Impact 전→후 / 참조', '점수 전→후', '거부'], rows)
    lines += ['', '점수는 빈 `reference_db.json`의 기존 하드코딩 폴백 기준이다. '
              '점수 상승은 정확도 향상 판정이 아니다. 점수식·각도식·각도 스무딩을 변경하지 않았다. '
              '원본 이미지 49장 모두 자기 단계의 경계 안에 있음을 실행 중 assert했다.', '',
              '탐색 참조 대비 악화: '+('; '.join(regressions) if regressions else '범위까지 거리 증가 없음')+'. '
              '범위 내 차이를 개선/악화로 단정하지 않으며 참조 자체의 불확실성도 유지한다.', '',
              '## 6. 완료 검증·환경', '']
    lines += table(['검증', '결과'], [[name, f'exit {r["exit_code"]} · {r["log"]}']
                                     for name, r in commands.items()])
    lines += ['', '기본값 동일성: [default_parity](data/default_parity.json) 및 변경하지 않은 '
              '`3bdf45d` 검출기를 oracle로 사용한 결측·컷·fps 회귀 테스트. '
              '캐시 대 실제 파이프라인 신호/경계 동일성은 개발 split에서 확인했다: '+
              json.dumps(read('cache_pipeline_parity.json'), ensure_ascii=False)+'.',
              f'캐시 상태 {cache["total"]}개: {cache["status"]}; split별 {cache["splits"]}. '
              f'600프레임 초과 별도 adaptive 추론 {len(cache["adaptive_ids"])}개. '
              f'누적 worker 처리 {cache["cumulative_worker_sec"]/60:.1f}분. '
              f'3개 worker 캐시 wall time {cache["cache_wall_sec"]/60:.1f}분. '
              f'fps 제외 목록: {cache["excluded"]}. 실패를 임의로 제외하지 않았다.',
              '포즈 추론은 기존 `golf-server:baseline` linux/amd64, Python 3.11.17, '
              'MediaPipe 0.10.21, OpenCV 4.10.0.84, NumPy 1.26.4. '
              'image ID `sha256:1ebff936e1e5f666cac7a3b451b5ecf57ba0b5ae6197424899122b9d267e2e06`. '
              '캐시는 현재 pipeline과 같은 CLAHE·model_complexity=1·smooth_landmarks=True·'
              'detection/tracking=.5. ARM Mac 위 amd64 에뮬레이션, GPU 없음.',
              '탐색·캐시 이벤트 재생은 호스트의 기존 NumPy와 표준 라이브러리만 사용했다: '+
              json.dumps(read('host_environment.json'), ensure_ascii=False)+'. '
              'pytest는 기존 순수 Python 파일을 `/private/tmp/phase_testdeps`에서 mount했다. '
              '설치·이미지 재빌드·새 패키지 없음.',
              f'원래 폴더: 최초 status와 동일, tracked {complete["original"]["tracked_files"]}개 해시 동일. '
              '8010 서버 제어 없음. 커밋·브랜치 변경·merge 없음.',
              'Streamlit 기동은 기존 Docker에 패키지가 없어 미검증이다. '
              '새 패키지 금지에 따라 설치하지 않았으며 서버 import와 분석은 pytest로 확인했다. '
              '웹 build의 번들 크기 경고와 lint의 기존 경고는 남아 있고 exit code는 0이다.',
              '스냅샷: `tests/regen_snapshot.py`로만 재생성. 전/후 '+
              json.dumps(snapshot, ensure_ascii=False)+'.', '',
              '## 7. 단회 평가 증거', '']
    lines += table(['UTC', '감사 이벤트'], [[r['utc'], r['event']] for r in complete['holdout_events']])
    lines += ['', '`~/datasets/golfdb_pose/audit.jsonl`, `frozen.json`, `split4_once.lock`이 원자료다. '
              'lock은 실패 시에도 재평가를 막는다. [completion](data/completion.json)에 '
              '감사 로그 해시·횟수·순서·소스 동일성·원본 폴더 검증을 저장했다.', '',
              '## 8. 한계·B안', '',
              '손목 Y만으로 클럽 반전, 공 접촉, 최종 자세 이완을 직접 관측하지 못한다. '
              'Address/Finish 정의 차이, 저해상도 포즈 오차, 컷과 잘못된 스윙 선택이 남는다. '
              'pro2 참조는 컷을 포함하고 어려운 영상은 실제 타격 대신 연습 스윙을 선택하므로 '
              '7개 거부 0건을 실제 타격 정확도 성공으로 해석하지 않는다. '
              'A9의 스무딩 창은 승인된 보정 대상으로 탐색했으며 600프레임 상한과 결측 규칙은 보존했다.',
              'B안은 [B_DESIGN](B_DESIGN.md)에 입력·라벨·분리·1D CNN/GRU·PyTorch 버전/라이선스·'
              '이미지 크기/속도 예산을 정리했다. 설치·모델 구현·학습은 수행하지 않았다. '
              '속도는 가설이고 A안 대비 개선 수치는 근거가 없어 예측하지 않았다.', '',
              '## 9. 재실행·커밋 묶음', '',
              '명령과 경로는 [tools README](../../../tools/phase_train/README.md). '
              '기존 결과의 잠금을 지워 반복하지 않는다. 이번 결과 루트는 보존한다. '
              '원자료/캐시는 CC BY-NC 4.0 비상업 연구·평가 용도로 레포 밖에만 둔다.', '',
              '커밋은 실행하지 않았다. 아래는 추가+삭제 ≤200줄의 제안이며 최종 결합 상태에서 검증한다.', '']
    lines += table(['묶음', '내용', '변경 줄 상한'], [
        [1, 'phase_parameters.py + phase_detector.py diff', 130],
        ['2–3', 'baseline oracle fixture: 두 구간으로 나눔', '각 150'],
        [4, 'test_phase_parameters.py + test_phase_train_metrics.py', 120],
        [5, 'common.py + replay.py', 140], [6, 'cache.py + verify_cache.py', 170],
        [7, 'train.py + check_defaults.py', 150], [8, 'apps.py + 스냅샷 + 샘플 3개(compact JSON)', 160],
        [9, 'holdout.py + provenance.py', 200], [10, 'report.py', 200],
        ['10b', 'checks.py', 60],
        [11, 'PROTOCOL.md + B_DESIGN.md', 150],
        ['12 이후', 'REPORT.md/README/요약 JSON·로그: 파일·hunk별 분할', '각 ≤200']])
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
    for name in ('split4_summary.json', 'default_parity.json', 'cache_pipeline_parity.json',
                 'completion.json', 'environment.json', 'host_environment.json',
                 'fit_1.json', 'fit_2.json', 'fit_3.json', 'fit_all.json'):
        (OUT/'data'/name).write_text(json.dumps(read(name), ensure_ascii=False)+'\n')
    (OUT/'data/apps_summary.json').write_text(json.dumps(app_summary, ensure_ascii=False)+'\n')
    dump(OUT/'data/snapshot_comparison.json', snapshot)
    for name, r in commands.items():
        shutil.copyfile(r['log'], OUT/'data'/f'{name}.log')
    print('Report written:', OUT/'REPORT.md')


if __name__ == '__main__':
    main()
