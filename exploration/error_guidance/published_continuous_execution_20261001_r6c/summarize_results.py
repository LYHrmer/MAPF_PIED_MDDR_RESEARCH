"""Post-run accounting; never changes frozen experiment files or selects runs."""
from collections import Counter
from pathlib import Path
import csv
import hashlib
import json
import statistics

HERE = Path(__file__).resolve().parent
RAW = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence') / HERE.name / 'runs'


def sha(path):
    with path.open('rb') as stream:
        value = hashlib.sha256()
        for block in iter(lambda: stream.read(1 << 20), b''):
            value.update(block)
        return value.hexdigest()


def rows(path):
    if path.exists():
        with path.open() as stream:
            for line in stream:
                yield json.loads(line)


def summarize(spec, audit):
    path = RAW / spec['id']
    receipt_path = path / 'receipt.json'
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    kinds = Counter()
    admitted = {}
    services = []
    observations = Counter()
    wheels = Counter()
    last_observation = {}
    latest_tasks = {}
    pause_ticks = []
    active_triggers = []
    last_tick = None
    horizon = None
    for event in rows(path / 'events.jsonl'):
        kind = event['kind']
        kinds[kind] += 1
        last_tick = event['tick']
        if kind == 'admit':
            for action in event['actions']:
                admitted[(event['robot'], action[1])] = action
        elif kind == 'end':
            command = admitted.get((event['robot'], event['node']))
            if event['accepted'] and command is not None and command[3] == 'S':
                services.append({'task_id': event['task_id'], 'robot': event['robot'], 'tick': event['tick']})
        elif kind == 'observation':
            observations[event['robot']] += 1
            last_observation[event['robot']] = event['tick']
        elif kind == 'view':
            latest_tasks = {str(a): goals[0] for a, goals in enumerate(event['view']['mapf_instance']['goals'])}
        elif kind == 'control':
            phase = event['control']['phase']
            if phase == 'wheel_command':
                wheels[event['robot']] += 1
            elif phase == 'pause':
                pause_ticks.append(event['tick'])
            elif phase == 'active_trigger':
                active_triggers.append(event['tick'])
        elif kind == 'horizon':
            horizon = event
    durations = []
    calls = 0
    objectives = Counter()
    last_cumulative_calls = None
    for decision in rows(path / 'decisions.jsonl'):
        durations.append(decision['planner_request_wall_seconds'])
        result = decision['result']
        calls += result['network_forward_calls']
        last_cumulative_calls = result['network_forward_calls_cumulative']
        objectives[result['objective']] += 1
    completed_ids = {row['task_id'] for row in services}
    pending_tasks = [dict(task, robot=robot) for robot, task in latest_tasks.items() if task['id'] not in completed_ids]
    audit_result = audit.get(spec['id'], {})
    complete = bool(receipt and receipt['error'] is None and receipt['true_horizon_tick'] == spec['horizon_ticks'])
    eligible = complete and audit_result.get('passed', False)
    if audit_result.get('passed'):
        assert len(services) == audit_result['task_services'], spec['id']
        assert calls == audit_result['network_forward_calls'], spec['id']
    if receipt:
        assert abs(sum(durations) - receipt['planner_total_request_wall_seconds']) < 1e-8, spec['id']
    n = len(durations)
    return {
        **spec,
        'receipt_present': receipt is not None,
        'native_error': receipt['error'] if receipt else 'missing_receipt',
        'audit_passed': audit_result.get('passed', False),
        'audit_error': audit_result.get('error'),
        'true_horizon_reached': complete,
        'primary_metric_eligible': eligible,
        'normal_station_end_count': len(services),
        'task_services_per_800_seconds': len(services) if eligible else None,
        'tasks_per_second': len(services) / 800 if eligible else None,
        'partial_service_count_on_failed_or_unaudited_run': None if eligible else len(services),
        'services_by_owner': dict(Counter(row['robot'] for row in services)),
        'pending_current_task_count': len(pending_tasks),
        'pending_current_tasks_at_last_observed_view': pending_tasks,
        'horizon_unfinished_nodes': horizon['snapshot']['unfinished'] if horizon else None,
        'last_event_tick': last_tick,
        'observations_by_robot': dict(observations),
        'last_observation_tick_by_robot': last_observation,
        'issued_wheel_records_by_robot': dict(wheels),
        'native_event_counts': dict(kinds),
        'planner_requests': n,
        'planner_wall_total_seconds': sum(durations),
        'planner_wall_p50_seconds': statistics.median(durations) if n else None,
        'planner_wall_p95_seconds': sorted(durations)[min(n - 1, __import__('math').ceil(.95 * n) - 1)] if n else None,
        'network_forward_calls': calls,
        'network_forward_calls_cumulative_last': last_cumulative_calls,
        'official_objective_counts': dict(objectives),
        'actual_active_trigger_ticks': active_triggers,
        'actual_pause_ticks': pause_ticks,
        'strict_all_ACK_points_passed': audit_result.get('strict_all_ACK_points_passed', False),
        'maximum_ACK_endpoint_error_m': max((row['endpoint_error_m'] for row in audit_result.get('ends', [])), default=None),
        'wall_seconds': receipt['wall_seconds'] if receipt else None,
        'processes': receipt['processes'] if receipt else None,
        'receipt_sha256': sha(receipt_path) if receipt else None,
    }


def main():
    specs = json.loads((HERE / 'runs.json').read_text())['runs']
    audit_path = HERE / 'audit.json'
    audit = json.loads(audit_path.read_text())['runs'] if audit_path.exists() else {}
    results = [summarize(spec, audit) for spec in specs]
    paired = []
    for trained in results:
        if trained['policy'] != 'trained':
            continue
        baseline = next(r for r in results if r['policy'] == 'hm_GPIBT' and all(r[k] == trained[k] for k in ('map', 'N', 'condition')))
        eligible = trained['primary_metric_eligible'] and baseline['primary_metric_eligible']
        paired.append({
            'map': trained['map'], 'N': trained['N'], 'condition': trained['condition'],
            'both_primary_metrics_eligible': eligible,
            'hm_GPIBT_tasks_per_800s': baseline['task_services_per_800_seconds'],
            'trained_tasks_per_800s': trained['task_services_per_800_seconds'],
            'trained_minus_hm_tasks_per_800s': trained['normal_station_end_count'] - baseline['normal_station_end_count'] if eligible else None,
            'hm_GPIBT_planner_wall_seconds': baseline['planner_wall_total_seconds'],
            'trained_planner_wall_seconds': trained['planner_wall_total_seconds'],
        })
    output = {
        'planned_runs': len(specs), 'receipts_present': sum(r['receipt_present'] for r in results),
        'true_horizon_reached': sum(r['true_horizon_reached'] for r in results),
        'audit_passed': sum(r['audit_passed'] for r in results),
        'native_failures': [r['id'] for r in results if r['native_error']],
        'audit_failures': [r['id'] for r in results if not r['audit_passed']],
        'metric_definition': 'Actual accepted normal STATION END count during 800 physical seconds; primary value withheld if incomplete or causal audit fails. All planned runs remain listed.',
        'censoring_definition': 'Revealed current FIFO tasks lacking normal STATION END at horizon are right-censored. Unrevealed future stream entries are not exposed tasks.',
        'scope': 'Synchronous one-step joint-settled S1 pilot; transferred frozen sortation-trained quad560 flow model; not an error predictor, asynchronous LMAPF benchmark, or continuous safety proof.',
        'freeze_sha256': sha(HERE / 'freeze.json'),
        'audit_sha256': sha(audit_path) if audit_path.exists() else None,
        'summary_script_sha256': sha(Path(__file__).resolve()),
        'runs': results, 'paired_comparisons': paired,
    }
    (HERE / 'summary.json').write_text(json.dumps(output, indent=2) + '\n')
    fields = ['id', 'map', 'N', 'policy', 'condition', 'native_error', 'audit_passed', 'true_horizon_reached', 'task_services_per_800_seconds', 'pending_current_task_count', 'planner_requests', 'planner_wall_total_seconds', 'planner_wall_p50_seconds', 'planner_wall_p95_seconds', 'network_forward_calls', 'strict_all_ACK_points_passed', 'maximum_ACK_endpoint_error_m', 'wall_seconds']
    with (HERE / 'summary.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
    print(json.dumps({k: v for k, v in output.items() if k not in ('runs', 'paired_comparisons')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
