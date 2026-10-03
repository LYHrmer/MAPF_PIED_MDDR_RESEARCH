"""Run a bounded author-build/preflight step with an immutable receipt."""
from pathlib import Path
import datetime
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
name, cwd, *command = sys.argv[1:]
folder = ROOT / 'commands' / name
folder.mkdir(parents=True, exist_ok=False)
start = time.monotonic()
with (folder / 'stdout.log').open('w') as out, (folder / 'stderr.log').open('w') as err:
    try:
        process = subprocess.run(['rtk', 'proxy', *command], cwd=cwd, stdout=out, stderr=err, timeout=600)
        result = {'returncode': process.returncode}
    except subprocess.TimeoutExpired:
        result = {'timeout': 600, 'returncode': None}
result.update(command=command, cwd=cwd, elapsed_seconds=time.monotonic()-start,
              completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(folder / 'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
if result['returncode']:
    print((folder / 'stderr.log').read_text()[-2200:])
