"""Wait for the separately authorized matrix; only audit and archive, never launch it."""
from pathlib import Path
import gc
import hashlib
import importlib.util
import json
import sys
import time

HERE = Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/published_continuous_execution_20261001_r6c')
RAW = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence') / HERE.name / 'runs'
sys.path.insert(0, str(HERE))
import audit
import summarize_results
import archive_raw

specs = json.loads((HERE / 'runs.json').read_text())['runs']
out = {}
audit_path = HERE / 'audit.json'
if audit_path.exists():
    out = json.loads(audit_path.read_text())['runs']


def write_audit():
    result = {
        'all_available_passed': all(row['passed'] for row in out.values()),
        'runs': out,
        'auditor_sha256': audit.sha(HERE / 'audit.py'),
        'mapping_replay_sha256': audit.sha(HERE / 'mapping_replay.py'),
        'orchestration_sha256': audit.sha(Path(__file__).resolve()),
        'orchestration': 'Invoke the frozen audit.check once after each finalized receipt; never start any native process.',
    }
    temporary = HERE / 'audit.json.pending'
    temporary.write_text(json.dumps(result, indent=2) + '\n')
    temporary.replace(audit_path)


print('Waiting for R6c receipts; this process never launches the matrix.', flush=True)
while len(out) < len(specs):
    for spec in specs:
        if spec['id'] in out or not (RAW / spec['id'] / 'receipt.json').exists():
            continue
        try:
            result = audit.check(spec)
        except Exception as error:
            result = {'passed': False, 'error': str(error), 'exception': type(error).__name__}
        out[spec['id']] = result
        write_audit()
        print(json.dumps({'run': spec['id'], 'passed': result['passed'], 'error': result.get('error'), 'task_services': result.get('task_services'), 'network_forward_calls': result.get('network_forward_calls'), 'completed_audits': len(out)}), flush=True)
        gc.collect()
    if len(out) < len(specs):
        time.sleep(5)
summarize_results.main()
archive_raw.main()
print('R6c all 24 receipts audited, summarized, and archived.', flush=True)
