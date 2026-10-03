"""Run the eight preselected, unmodified author configurations sequentially."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / 'vendor' / 'STPG'
registration = json.loads((ROOT / 'REGISTERED_CASES.json').read_text())
safety = {'address_space_bytes': 4 * 1024**3, 'cpu_seconds': 90,
          'author_search_limit_seconds': 16, 'outer_timeout_seconds': 120,
          'parallelism': 1, 'scope': 'R0 executable preflight, not full paper replication',
          'difference_from_author_batch': '4 GiB address space instead of author batch 16 GiB',
          'registered_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
(ROOT / 'EXECUTION_LIMITS.json').write_text(json.dumps(safety, indent=2)+'\n')
results = []
for case in registration['cases']:
    for key, digest in [('path', 'path_sha256'), ('situation_file', 'situation_sha256')]:
        assert hashlib.sha256((VENDOR / case[key]).read_bytes()).hexdigest() == case[digest]
    for method, settings in registration['methods'].items():
        name = case['map'] + '__' + method
        folder = ROOT / 'commands' / name
        folder.mkdir(parents=True, exist_ok=False)
        algorithm, branch, group, heuristic, early, incremental, weight = settings
        command = ['rtk', 'proxy', 'prlimit', '--as='+str(safety['address_space_bytes']),
                   '--cpu=90', '--', './build/simulate', '-p', case['path'], '-s', case['situation_file'],
                   '-t', '16', '-a', algorithm, '-b', branch, '-g', group, '-h', heuristic,
                   '-e', early, '-i', incremental, '--w_astar', '1.0', '--w_focal', str(weight),
                   '--random_seed', '10', '-o', str(folder/'stats.json'), '-n', str(folder/'new_paths.txt')]
        start = time.monotonic()
        with (folder/'stdout.log').open('w') as out, (folder/'stderr.log').open('w') as err:
            try:
                process = subprocess.run(command, cwd=VENDOR, stdout=out, stderr=err, timeout=120)
                record = {'returncode': process.returncode}
            except subprocess.TimeoutExpired:
                record = {'returncode': None, 'timeout_seconds': 120}
        record.update(case=case['map'], agents=case['agents'], method=method, command=command,
                      cwd=str(VENDOR), elapsed_seconds=time.monotonic()-start,
                      completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        (folder/'receipt.json').write_text(json.dumps(record, indent=2)+'\n')
        if (folder/'stats.json').exists():
            record['stats'] = json.loads((folder/'stats.json').read_text())
        results.append(record)
        (ROOT/'RESULTS.json').write_text(json.dumps(results, indent=2)+'\n')
        print(json.dumps({k:v for k,v in record.items() if k not in ['command','cwd','stats']}, ensure_ascii=False), flush=True)
