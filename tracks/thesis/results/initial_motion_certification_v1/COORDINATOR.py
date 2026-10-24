"""One-shot serial coordinator; invokes existing frozen scientific runners."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


parser = argparse.ArgumentParser()
parser.add_argument('--repo', type=Path, required=True)
parser.add_argument('--manifest', required=True)
parser.add_argument('--sha256', required=True)
parser.add_argument('--commit', required=True)
parser.add_argument('--kind', choices=('sci', 'thesis'), required=True)
args = parser.parse_args()
root = args.repo.resolve()
manifest_path = root / args.manifest
raw = manifest_path.read_bytes()
assert digest(raw) == args.sha256
config = json.loads(raw)
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip() == args.commit
track = root / 'tracks' / args.kind
batch = track / 'results' / config['batch_id']
assert not batch.exists(), 'one-shot batch already exists'
quote = '验证SCI新旧预算合同的实际行为，以及硕士初始认证的预算可行性，再开展收益比较'
reference = 'CURRENT_USER_REQUEST_20261025_BUDGET_CONTRACT_AND_INITIAL_CERTIFICATION'
if args.kind == 'sci':
    identifiers = [job['id'] for job in config['jobs']]
    assert len(identifiers) == 4
    assert config['limits']['total_wall_s'] == 5
    assert config['external_command_guard']['term_after_s'] == 10
    assert config['external_command_guard']['kill_grace_s'] == 2
    runner = 'tracks/sci/run_address_adapter.py'
    selector = '--job'
    term, grace = 10, 2
else:
    identifiers = config['cases']
    assert len(identifiers) == 2
    assert config['limits']['total_admission_wall_s'] == 26
    assert config['limits']['outer_term_s'] == 28
    assert config['limits']['outer_kill_after_s'] == 2
    runner = 'tracks/thesis/compare_nominal_motion.py'
    selector = '--case'
    term, grace = 28, 2
batch.mkdir(parents=True)
save(batch / 'AUTHORIZATION.json', {
    'authorization_reference': reference,
    'actual_user_instruction': quote,
    'authorization_source': 'Current user message in the active conversation',
    'scope': 'Minimal actual contract verification or initial certification feasibility; no benefit batch',
    'arrangement_owner': 'Assistant selected and froze the minimal inputs, item count and limits before execution',
    'not_a_claim_user_individually_approved_each_numeric_parameter': True,
    'manifest_sha256': args.sha256,
    'scientific_code_commit': args.commit,
    'planned_items': identifiers,
    'limits': config['limits'],
    'external_term_s': term,
    'external_kill_grace_s': grace,
    'retries': 0,
    'stop_batch_on_first_unsuccessful_receipt': True,
    'old_authorization_reused': False,
    'file_itself_is_not_authority': True,
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'pre_execution_load_average': os.getloadavg(),
})
coordinator = Path(__file__).read_bytes()
(batch / 'COORDINATOR.py').write_bytes(coordinator)
records = []
stopped = False
for identifier in identifiers:
    if stopped:
        records.append({'id': identifier, 'status': 'NOT_RUN_AFTER_FAILURE', 'retry_allowed': False})
        continue
    command = ['timeout', '--signal=TERM', '--kill-after=' + str(grace) + 's', str(term) + 's',
               sys.executable, '-B', runner, 'run', '--manifest', args.manifest,
               '--sha256', args.sha256, selector, identifier, '--authorization-reference', reference]
    print('START', args.kind, identifier, flush=True)
    started = time.monotonic_ns()
    result = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    elapsed = time.monotonic_ns() - started
    receipt_path = batch / identifier / 'receipt.json'
    receipt_raw = receipt_path.read_bytes() if receipt_path.exists() else None
    try:
        receipt = json.loads(receipt_raw) if receipt_raw else {}
    except ValueError:
        receipt = {}
    complete = result.returncode == 0 and receipt.get('status') == 'COMPLETE'
    stopped = not complete
    row = {
        'id': identifier, 'command': command, 'cwd': str(root), 'exit_code': result.returncode,
        'outer_wall_ns': elapsed, 'stdout': result.stdout.decode(errors='replace'),
        'stderr': result.stderr.decode(errors='replace'), 'receipt_sha256': digest(receipt_raw) if receipt_raw else None,
        'status': 'COMPLETE' if complete else 'FAILED_OR_INCOMPLETE', 'retry_allowed': False,
    }
    save(batch / (identifier + '.outer.json'), row)
    records.append(row)
    print('END', args.kind, identifier, row['status'], 'seconds', round(elapsed / 1e9, 3), flush=True)
save(batch / 'OUTER_EXECUTION.json', {
    'manifest_sha256': args.sha256, 'scientific_code_commit': args.commit,
    'coordinator_sha256': digest(coordinator), 'jobs': records,
    'status': 'STOPPED_AFTER_FAILURE' if stopped else 'ALL_COMPLETE',
    'authorization_consumed_or_closed': True, 'retries': 0,
    'administration_outside_each_outer_command_is_not_claimed_as_scientific_cost': True,
})
sys.exit(2 if stopped else 0)
