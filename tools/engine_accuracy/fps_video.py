"""Matched lossless 30/60fps controls; actual 60fps acquisition is not tested."""
import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get('PHASE_DATA', '/datasets/golfdb_pose'))
OUT = DATA/'engine_accuracy_20261014'


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def prepare(aligned=False):
    videos = OUT/'fps_videos'
    videos.mkdir(exist_ok=True)
    previous = json.loads((DATA/'fix_20261014/apps_after.json').read_text())
    commands = []
    names = {'il-ban': '일반', 'pro': '프로', 'pro2': '프로2'}
    for name, record in previous.items():
        path = (ROOT/'golf_swing_analyzer/video'/f'{names[name]}.mp4' if name in names
                else DATA.parent/'test_videos'/f'{name}.mp4')
        start, end = record['window']
        control = videos/f'{name}_30.mkv'
        # Same spatial transform and lossless codec for all three test conditions.
        command = ['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-ss', str(start), '-i', str(path),
                   '-t', str(end-start), '-an', '-vf', "scale=w='min(854,iw)':h=-2,fps=30",
                   '-c:v', 'ffv1', str(control)]
        commands.append(command)
        if not control.exists(): subprocess.run(command, check=True)
        for label, filt in [('dup', 'fps=60'), ('mci', 'minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1')]:
            if aligned:
                if label == 'dup': continue
                frames = int(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                    '-count_frames', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(control)], text=True))
                # Matroska millisecond timestamps otherwise interpolate even the
                # original frame instants. Restore an exact clock before MCI.
                filt = ('tpad=stop=2:stop_mode=clone,settb=1/60000,setpts=N/(30*TB),'+filt+
                        f',trim=end_frame={2*frames},setpts=PTS-STARTPTS')
                label = 'mci_aligned'
            target = videos/f'{name}_60_{label}.mkv'
            command = ['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', str(control),
                       '-an', '-vf', filt, '-c:v', 'ffv1', str(target)]
            commands.append(command)
            if not target.exists(): subprocess.run(command, check=True)
        print('prepared', name, flush=True)
    write(OUT/('fps_commands_aligned.json' if aligned else 'fps_commands.json'), dict(commands=commands,
          ffmpeg_version=subprocess.check_output(['ffmpeg', '-version'], text=True).splitlines()[0],
          warning='24/25/29.97fps inputs first converted to matched 30fps controls; not new observations.'))


def rewrap():
    destination = OUT/'fps_videos_avi'
    destination.mkdir(exist_ok=True)
    commands = []
    for source in sorted((OUT/'fps_videos').glob('*.mkv')):
        if source.stem.endswith('_60_mci'): continue
        rate = '30' if source.stem.endswith('_30') else '60'
        command = ['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', str(source),
                   '-an', '-c:v', 'copy', '-r', rate, str(destination/(source.stem+'.avi'))]
        subprocess.run(command, check=True)
        commands.append(command)
    write(OUT/'fps_rewrap_commands.json', dict(commands=commands,
          reason='AVI preserves the declared 30/60fps clock; no pixel re-encoding.'))


def infer(stage, aligned=False, avi=False):
    import cv2
    cv2.setNumThreads(1)
    sys.path[:0] = [str(ROOT/'golf_swing_analyzer'), str(OUT)]
    package = 'baseline_analyzer' if stage == 'baseline' else 'analyzer'
    pipeline = importlib.import_module(package+'.pipeline')
    scoring = importlib.import_module(package+'.scoring')
    videos = OUT/('fps_videos_avi' if avi else 'fps_videos')
    result = {}
    pattern = '*.avi' if avi else '*_60_mci_aligned.mkv' if aligned else '*.mkv'
    for path in sorted(videos.glob(pattern)):
        try:
            rows, ann, traj, fps, det, step = pipeline.process_video(str(path))
            assert {r['frame'] for r in rows} <= {r['frame'] for r in ann}
            assert {r['frame'] for r in traj} <= {r['frame'] for r in rows}
            measured = scoring.compute_summary(rows)
            result[path.stem] = dict(fps=fps, step=step, score=scoring.compute_score(measured, {})[0],
                 bounds_sec=det.phase_boundaries_sec, summary=measured,
                 decoded_frames=pipeline.get_video_info(str(path))['total_frames'],
                 sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        except Exception as exc:
            result[path.stem] = dict(error=repr(exc))
        write(OUT/f"fps_{stage}{'_avi' if avi else '_aligned' if aligned else ''}.json", result)
        print(stage, path.stem, {k:v for k,v in result[path.stem].items() if k != 'summary'}, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare', 'rewrap', 'baseline', 'final'])
    parser.add_argument('--aligned', action='store_true')
    parser.add_argument('--avi', action='store_true')
    args = parser.parse_args()
    if args.mode == 'prepare': prepare(args.aligned)
    elif args.mode == 'rewrap': rewrap()
    else: infer(args.mode, args.aligned, args.avi)


if __name__ == '__main__':
    main()
