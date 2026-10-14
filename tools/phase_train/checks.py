"""Run the final Docker/web gates and record exact commands and exit codes."""
import argparse
import os
import subprocess
import time

from common import DATA, ROOT, dump, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--regen-snapshot', action='store_true')
    args = parser.parse_args()
    assert not (DATA/'frozen.json').exists(), 'Run validation before freezing'
    testdeps = '/private/tmp/phase_testdeps'
    assert os.path.isdir(testdeps), 'Use existing copied pytest files; do not install'
    docker = ['docker', 'run', '--rm', '--platform', 'linux/amd64', '--network', 'none',
              '--cpus', '2', '-e', 'PYTHONDONTWRITEBYTECODE=1',
              '-e', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD=1', '-e', 'PYTHONPATH=/testdeps',
              '-e', 'OPENBLAS_NUM_THREADS=1', '-e', 'OMP_NUM_THREADS=1',
              '-v', f'{ROOT}:/work', '-v', f'{testdeps}:/testdeps:ro',
              '-w', '/work', 'golf-server:baseline', 'python']
    commands = []
    if args.regen_snapshot:
        commands.append(('regen_snapshot', docker+['tests/regen_snapshot.py'], ROOT))
    commands += [('pytest', docker+['-m', 'pytest', '-p', 'no:cacheprovider', '-q'], ROOT),
                 ('web_build', ['npm', 'run', 'build'], ROOT/'web'),
                 ('web_lint', ['npm', 'run', 'lint'], ROOT/'web')]
    results = {}
    for name, command, cwd in commands:
        target = DATA/'logs'/f'{name}.log'
        target.parent.mkdir(parents=True, exist_ok=True)
        started = time.perf_counter()
        print('Running', name, flush=True)
        with target.open('w') as log:
            result = subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                                    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        results[name] = dict(command=command, cwd=str(cwd), exit_code=result.returncode,
                             log=str(target), log_sha256=sha(target),
                             elapsed_sec=time.perf_counter()-started)
        dump(DATA/'validation_commands.json', results)
        print(name, 'exit', result.returncode, flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
