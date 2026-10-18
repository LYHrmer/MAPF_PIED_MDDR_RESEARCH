"""Summarize frozen motion-run bytes; no optimizer or motion construction."""

import argparse
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_SHA = 'dfac22c05d73e712cadc8937e2ccc4a855e2764ef8f2b4c5f4f9546dd33b3b7c'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(a, b):
    return math.isfinite(a) and math.isfinite(b) and math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-7)


def audit_arm(arm):
    metrics = arm['metrics']
    motion = arm['motion']
    require(not motion['error_model_applied'], 'unexpected error model')
    if metrics['feasibility'] == 'SUFFICIENT_SEPARATION_NOT_ESTABLISHED':
        require(not motion['certified_nominal_reference'], 'inconsistent rejection')
        require(metrics['completion_sum_s'] is None and metrics['makespan_s'] is None,
                'rejected reference must not report timing benefit')
        return dict(metrics)
    require(metrics['feasibility'] == 'CERTIFIED_NOMINAL_REFERENCE'
            and motion['certified_nominal_reference'], 'unknown feasibility')
    schedule = motion['schedule']
    totals = dict(move_s=0.0, turn_s=0.0, turn_barrier_wait_s=0.0,
                  discrete_wait_slot_s=0.0)
    counts = dict(move_actions=0, turn_actions=0, turn_quarters_including_initial=0,
                  discrete_wait_actions=0)
    completions = {}
    for agent, actions in schedule['agents'].items():
        previous_end = 0.0
        wait = 0.0
        require(actions[-1]['kind'] == 'GOAL_HOLD', 'missing permanent hold')
        for index, action in enumerate(actions):
            require(close(action['start_s'], previous_end), 'action gap or overlap')
            kind = action['kind']
            if kind == 'GOAL_HOLD':
                require(index == len(actions)-1 and action['end_s'] is None,
                        'nonterminal or finite goal hold')
                break
            duration = action['end_s'] - action['start_s']
            require(duration >= 0 and math.isfinite(duration), 'invalid duration')
            if kind == 'MOVE':
                key = 'move_s'
                counts['move_actions'] += 1
            elif kind == 'TURN':
                key = 'turn_s'
                counts['turn_actions'] += 1
                counts['turn_quarters_including_initial'] += abs(action['signed_quarters'])
            else:
                require(kind == 'WAIT', 'unknown action')
                key = {'TURN_BARRIER': 'turn_barrier_wait_s',
                       'DISCRETE_WAIT_SLOT': 'discrete_wait_slot_s'}[action['reason']]
                wait += duration
                if action['reason'] == 'DISCRETE_WAIT_SLOT':
                    counts['discrete_wait_actions'] += 1
            totals[key] += duration
            previous_end = action['end_s']
        completions[agent] = previous_end
        require(close(previous_end, schedule['completion_s'][agent])
                and close(previous_end, metrics['per_agent'][agent]['completion_s'])
                and close(wait, metrics['per_agent'][agent]['wait_s']),
                'per-agent completion/wait mismatch')
    for key, value in totals.items():
        require(close(value, metrics[key]), 'time partition mismatch: '+key)
    require(close(sum(completions.values()), metrics['completion_sum_s'])
            and close(max(completions.values()), metrics['makespan_s'])
            and close(sum(totals.values()), metrics['completion_sum_s'])
            and close(totals['turn_barrier_wait_s']+totals['discrete_wait_slot_s'], metrics['wait_sum_s']),
            'aggregate timing mismatch')
    require(counts['move_actions']+counts['discrete_wait_actions'] == arm['soc'],
            'discrete action count/SOC mismatch')
    return {key: metrics[key] for key in ('feasibility', 'completion_sum_s', 'makespan_s',
            'wait_sum_s', 'move_s', 'turn_s', 'turn_barrier_wait_s', 'discrete_wait_slot_s')} | counts


def summarize(stop_reason=None):
    manifest_path = HERE/'config/nominal_motion_v1_manifest.json'
    require(sha(manifest_path) == MANIFEST_SHA, 'manifest changed')
    manifest = read(manifest_path)
    for name, digest in manifest['runtime_sha256'].items():
        require(sha(HERE/name) == digest, 'runtime/lock changed: '+name)
    batch = HERE/'results'/manifest['batch_id']
    auth = read(batch/'AUTHORIZATION.json')
    require(auth['manifest_sha256'] == MANIFEST_SHA, 'authorization manifest mismatch')
    rows = []
    incident_path = batch/'ADMINISTRATIVE_INCIDENT.json'
    artifacts = {'AUTHORIZATION.json': sha(batch/'AUTHORIZATION.json'),
                 'ADMINISTRATIVE_INCIDENT.json': sha(incident_path)}
    missing_seen = False
    for case in manifest['cases']:
        folder = batch/case
        receipt_path = folder/'receipt.json'
        if not receipt_path.exists():
            missing_seen = True
            require(bool(stop_reason), 'unfinished batch requires explicit closing reason')
            rows.append({'case': case, 'status': 'NOT_RUN' if not folder.exists() else 'FAILED_OR_INCOMPLETE',
                         'reason': stop_reason})
            continue
        require(not missing_seen, 'case skipped in ordered batch')
        receipt = read(receipt_path)
        require(receipt['case'] == case and receipt['manifest_sha256'] == MANIFEST_SHA,
                'receipt identity mismatch')
        artifacts[case+'/receipt.json'] = sha(receipt_path)
        for name, expected in receipt['artifacts'].items():
            path = folder/name
            require(path.stat().st_size == expected['bytes'] and sha(path) == expected['sha256'],
                    'artifact changed: '+str(path))
        if receipt['status'] != 'COMPLETE':
            missing_seen = True
            require(bool(stop_reason), 'failed batch requires closing reason')
            rows.append({'case': case, 'status': receipt['status'], 'reason': stop_reason})
            continue
        costs = receipt['worker_costs']
        require(costs['exit_code'] == 0 and not costs['forced_cleanup'], 'unaccepted process result')
        require(receipt['entry_through_import_input_validation_output_and_hash_ns'] <= 60*10**9,
                'admission deadline exceeded')
        require(costs['all_descendant_user_s']+costs['all_descendant_system_s'] <= 45,
                'CPU limit exceeded')
        result = read(folder/'result.json')
        require(result['status'] == 'COMPLETE' and result['sci_commit'] == manifest['sci_commit'],
                'invalid source/result status')
        require([r['arm'] for r in result['rows']] == manifest['arms'], 'arm set/order mismatch')
        arms = []
        for row in result['rows']:
            arm = read(folder/('arm_'+row['arm']+'.json'))
            require(all(arm[key] == value for key, value in row.items()), 'arm/result mismatch')
            arms.append({'arm': row['arm'], 'soc': row['soc'], 'grid_makespan': row['grid_makespan'],
                         'selection': row['selection'], 'metrics': audit_arm(arm),
                         'stage_wall_ns': row['stage_wall_ns']})
        rows.append({'case': case, 'status': 'COMPLETE', 'arms': arms,
                     'entry_through_output_and_hash_s': receipt['entry_through_import_input_validation_output_and_hash_ns']/1e9,
                     'worker_costs': costs, 'supervisor_self_cpu_s': receipt['supervisor_self_cpu_s']})
    counts = {state: sum(r['status'] == state for r in rows)
              for state in ('COMPLETE', 'FAILED_OR_INCOMPLETE', 'NOT_RUN')}
    return {'schema': 'thesis_nominal_motion_batch_summary_v1',
            'status': 'ALL_COMPLETE' if counts['COMPLETE'] == len(rows) else 'CLOSED_PARTIAL',
            'scope': 'OFFLINE_SUMMARY_OF_AUTHORIZED_DEV_NO_NEW_SCIENTIFIC_EXECUTION',
            'independent_performance_experiment': False, 'manifest_sha256': MANIFEST_SHA,
            'scientific_code_commit': auth['scientific_code_commit'], 'sci_commit': manifest['sci_commit'],
            'summarizer_sha256': sha(Path(__file__)), 'source_artifact_sha256': artifacts,
            'counts': counts, 'rows': rows, 'closing_reason': stop_reason,
            'authorization_consumed_or_closed': True, 'retries': 0,
            'administrative_recording_incident': auth.get('recording_incident'),
            'administrative_incident_disposition': read(incident_path)['parent_disposition'],
            'validation_scope': 'Artifact SHA/size, budget/exit, arm/result consistency and independent arithmetic over saved actions. Continuous geometric certificate is the frozen runtime result, not independently re-proved here.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stop-reason')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.stop_reason)
    with args.output.open('x') as output:
        output.write(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'counts': result['counts'],
                      'output': str(args.output), 'sha256': sha(args.output)}))
