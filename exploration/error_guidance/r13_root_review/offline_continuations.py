"""Replay all saved continuations in a relocated package using only publication members."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib, json, shutil, subprocess, time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'gses_online_adoption_20261004_r13'

def main():
    manifest = json.loads((SOURCE / 'PUBLICATION_MEMBERS.json').read_text())
    rows = json.loads((SOURCE / 'RESULTS.json').read_text())
    started = time.time_ns()
    with TemporaryDirectory(prefix='r13-relocated-continuations-') as tmp:
        target = Path(tmp)
        for name, expected in manifest['files'].items():
            relative = Path(name)
            assert not relative.is_absolute() and '..' not in relative.parts
            raw = (SOURCE / relative).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == expected
            (target / relative).parent.mkdir(parents=True, exist_ok=True)
            (target / relative).write_bytes(raw)
        shutil.copyfile(SOURCE / 'PUBLICATION_MEMBERS.json', target / 'PUBLICATION_MEMBERS.json')
        command = ['rtk', 'proxy', 'python3', str(target / 'reproduce.py'), '--replay', 'all']
        result = subprocess.run(command, cwd=target, capture_output=True, text=True)
        successes = [line.removesuffix(' exact replay PASS') for line in result.stdout.splitlines() if line.endswith(' exact replay PASS')]
        output = {'passed': result.returncode == 0 and set(successes) == {r['id'] for r in rows},
                  'started_unix_ns': started, 'finished_unix_ns': time.time_ns(), 'exit_code': result.returncode,
                  'runs': len(successes), 'relocated_publication_members': len(manifest['files']),
                  'publication_manifest_sha256': hashlib.sha256((SOURCE / 'PUBLICATION_MEMBERS.json').read_bytes()).hexdigest(),
                  'complete_trace_exact_replay': True, 'new_solver_calls': 0,
                  'scope': 'Portable saved-checkpoint replay with existing author replies; independent geometry/dependency audit is separate.',
                  'stdout': result.stdout, 'stderr': result.stderr}
        (ROOT / 'ROOT_OFFLINE_CONTINUATIONS.json').write_text(json.dumps(output, indent=2) + '\n')
        assert output['passed'], result.stderr
        print('Relocated complete continuation replay PASS', len(successes), flush=True)

if __name__ == '__main__': main()
