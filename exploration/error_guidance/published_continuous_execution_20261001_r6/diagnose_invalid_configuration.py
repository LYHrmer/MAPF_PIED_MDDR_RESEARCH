"""Retain and label the accidentally launched, preflight-invalid R6 matrix."""
from pathlib import Path
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
RAW = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence') / HERE.name / 'runs'
runs = []
for spec in json.loads((HERE / 'runs.json').read_text())['runs']:
    path = RAW / spec['id']
    receipt = json.loads((path / 'receipt.json').read_text())
    expected = json.loads((HERE / 'inputs' / spec['map'] / 'environment.json').read_text())['starts'][:spec['N']]
    first_view = None
    first_merge = None
    first_offpoint = None
    for line in (path / 'events.jsonl').open():
        event = json.loads(line)
        if event['kind'] == 'view' and first_view is None:
            actual = [row['location'] for row in event['view']['mapf_instance']['starts']]
            first_view = {'tick': event['tick'], 'actual_initial_starts': actual, 'registered_scenario_starts': expected, 'matches_registered': actual == expected}
        elif event['kind'] == 'control' and event['control']['phase'] == 'front' and event['control']['type'] == 0 and len(event['control']['nodes']) > 1 and first_merge is None:
            first_merge = event
        elif event['kind'] == 'end' and event['accepted'] and not event['task'] and first_offpoint is None:
            observation, goal = event['observation'], event['goal']
            error = math.hypot(observation['x'] + goal[1], observation['y'] + goal[0])
            if error >= .03:
                first_offpoint = {'event': event, 'endpoint_error_m': error}
        if first_view is not None and first_merge is not None and first_offpoint is not None:
            break
    runs.append({
        **spec,
        'configuration_valid': False,
        'eligible_for_registered_S1_comparison': False,
        'native_attempt_retained': True,
        'native_error': receipt['error'],
        'native_horizon_tick': receipt['true_horizon_tick'],
        'native_decisions': receipt['decisions'],
        'first_view_registration': first_view,
        'first_merged_MOVE_front': first_merge,
        'first_offpoint_accepted_END': first_offpoint,
        'bridge_log': (path / 'process2.log').read_text() if receipt['error'] else None,
        'receipt_sha256': hashlib.sha256((path / 'receipt.json').read_bytes()).hexdigest(),
    })
result = {
    'status': 'INVALID_CONFIGURATION_NATIVE_RUNS_RETAINED',
    'planned_runs': 24,
    'native_attempts_retained': len(runs),
    'native_horizon_completed': sum(r['native_horizon_tick'] == 8000 for r in runs),
    'native_runtime_failures': sum(r['native_error'] is not None for r in runs),
    'registered_S1_eligible_runs': 0,
    'reasons': ['Remaining per-tick controller MOVE merging violates the declared strict-point S1 adapter', 'Physical starts/obstacles were transposed relative to the author parser and registered scenario'],
    'timing_note': 'R6 was launched when an earlier approval completed after preflight corrections had been prepared. All resulting attempts are retained. Statements that R6 had zero native runs described the earlier preparation time and are superseded by this current census.',
    'replacement': '../published_continuous_execution_20261001_r6c',
    'no_old_data_in_replacement_primary_table': True,
    'parent_freeze_unchanged_sha256': hashlib.sha256((HERE / 'freeze.json').read_bytes()).hexdigest(),
    'runs': runs,
}
(HERE / 'invalid_configuration_diagnosis.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'runs'}, indent=2))
