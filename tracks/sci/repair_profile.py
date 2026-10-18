"""Prepare or summarize a fixed strong-policy diagnostic; never run a solver.

Reuse the consumed DEV's unchanged runtime. This proposal requires a NEW actual
user authorization. Positive SOC-minus-h is not an improvement label.
"""
import argparse
import json
from pathlib import Path

from prepare_repair_dev import RUNTIME, prepare_case, sha
from run_repair_dev import HERE, inspect_inputs, load, unpack, write_json

BATCH = 'repair_residual_v1'
FAMILIES = ('maze-32-32-2', 'random-32-32-10', 'warehouse-10-20-10-2-1')
CASES = tuple(f'{family}__s01__n{n:02d}' for family in FAMILIES for n in (16, 32))


def fixed_orders(agents):
    """ID blocks, both orders, then whole-task controls; no outcome-based choice."""
    ids = sorted(agents)
    if len(ids) not in (16, 32):
        raise ValueError('this proposal is limited to the preselected 16/32-agent tasks')
    orders = []
    for start in range(0, len(ids), 8):
        group = ids[start:start+8]
        orders.extend((group, group[::-1]))
    return orders + [ids, ids[::-1]]


def prepare():
    folder = HERE / 'config'
    input_path = folder / (BATCH + '_inputs.json')
    manifest_path = folder / (BATCH + '_manifest.json')
    if any(path.exists() for path in (input_path, manifest_path, HERE/'results'/BATCH)):
        raise FileExistsError('preserve the prepared proposal or consumed/failed attempt')
    cases = []
    for name in CASES:
        case = prepare_case(name)  # Verify original bytes and GIVEN paths only.
        case['orders'] = fixed_orders(case['paths'])
        case['order_roles'] = ['LOCAL_ID_BLOCK_8']*(len(case['orders'])-2) + ['WHOLE_TASK_CONTROL']*2
        cases.append(case)
    bundle = {'scope': 'EXISTING_PLAN_REPACK_NO_NEW_SOLVER',
              'selection': 'all three registered families, s01 n16/n32, no outcome-based replacement',
              'generator_sha256': sha(Path(__file__).read_bytes()),
              'imported_preparer_sha256': sha((HERE/'prepare_repair_dev.py').read_bytes()),
              'cases': cases}
    raw = (json.dumps(bundle, sort_keys=True, separators=(',', ':'))+'\n').encode()
    config = {'schema': 'repair_dev_v1', 'batch_id': BATCH, 'authorization': 'PENDING_USER',
              'input_file': input_path.name, 'input_sha256': sha(raw),
              'binary': '.native_build_checked/address_sipp_bridge',
              'code_sha256': {name: sha((HERE/name).read_bytes()) for name in RUNTIME},
              'limits': {'case_wall_s': 15, 'algorithm_wall_s': 10, 'worker_cpu_s': 10,
                         'native_cpu_s': 10, 'per_process_as_mib': 512, 'search_calls': 128},
              'retry': 0,
              'jobs': [{'id': name+'__remaining_bound', 'case': name, 'policy': 'REMAINING_BOUND'}
                       for name in CASES]}
    with input_path.open('xb') as stream:
        stream.write(raw)
    write_json(manifest_path, config)
    manifest_sha = sha(manifest_path.read_bytes())
    checked, frozen, _ = load(manifest_path, manifest_sha)
    rows = inspect_inputs(checked, frozen)  # Does not initialize NativeBackend.
    print(json.dumps({'scope': bundle['scope'], 'input_sha256': sha(raw), 'input_bytes': len(raw),
                      'manifest_sha256': manifest_sha, 'tasks': rows}, indent=2))


def diagnose(case, result):
    """Read recorded h and PP outcomes, preserving conditional/censored meanings."""
    from pp_repair import Incumbent
    problem, initial = unpack(case)
    bounds = {int(a): h for a, h in result['lower_bounds'].items()}
    final = {int(a): tuple(p) for a, p in result['final_paths'].items()}
    if set(bounds) != set(initial) or result['model_key'] != problem.model_key:
        raise ValueError('same-model lower-bound identity mismatch')
    for agent, h in bounds.items():
        if type(h) is not int or not 0 <= h <= len(initial[agent])-1:
            raise ValueError('recorded h contradicts the given initial plan')
    problem.validate(final)
    if Incumbent(final).snapshot().sha256 != result['final_sha256']:
        raise ValueError('final paths do not match the recorded SHA')
    initial_soc = sum(len(p)-1 for p in initial.values())
    final_soc = sum(len(p)-1 for p in final.values())
    if (initial_soc != result['initial_soc'] or final_soc != result['final_soc']
            or final_soc > initial_soc or any(len(final[a])-1 < h for a, h in bounds.items())):
        raise ValueError('recorded plan/cost/bound mismatch')
    attempts, total_gain = [], 0
    previous_sha = Incumbent(initial).snapshot().sha256
    for index, attempt in enumerate(result['attempts']):
        if index >= len(case['orders']) or attempt['order'] != case['orders'][index]:
            raise ValueError('unexpected attempt sequence')
        if previous_sha is not None and attempt['before_sha256'] != previous_sha:
            raise ValueError('broken incumbent chain')
        previous_sha = attempt['after_sha256']
        old, candidate = attempt['old_cost'], attempt['candidate_cost']
        group_h = sum(bounds[a] for a in attempt['order'])
        gap = None if old is None else old - group_h
        if gap is not None and gap < 0:
            raise ValueError('negative recorded neighborhood gap')
        status, calls = attempt['status'], attempt['search_calls']
        label = attempt['improvement_label']
        kind = 'UNKNOWN_OR_CENSORED'
        gain = None
        if status == 'ACCEPTED':
            if label is not True or type(candidate) is not int or not candidate < old:
                raise ValueError('invalid accepted improvement')
            kind, gain = 'COMPLETE_ACCEPTED_IMPROVEMENT', old - candidate
            total_gain += gain
        elif status == 'NO_IMPROVEMENT':
            if label is not False or attempt['before_sha256'] != attempt['after_sha256']:
                raise ValueError('non-improvement changed the incumbent or label')
            gain = 0
            if attempt['reason'] == 'remaining lower bound exceeds strict target':
                kind = 'ROOT_BOUND' if calls == 0 else 'PREFIX_BOUND'
                if calls == 0 and gap != 0:
                    raise ValueError('root bound cannot reject a positive integer gap')
            elif attempt['reason'] == 'complete search exhausted the current improvement cap':
                kind = 'CAP_EXHAUSTED_CURRENT_PREFIX_ONLY'
            else:
                kind = 'OTHER_COMPLETED_NON_IMPROVEMENT'
        elif label is not None:
            raise ValueError('failure/timeout/unknown must not become a training label')
        attempts.append({'index': index, 'role': case['order_roles'][index],
                         'order': attempt['order'], 'status': status, 'diagnosis': kind,
                         'soc_minus_static_h_before': gap, 'accepted_gain': gain,
                         'search_calls': calls, 'completed_agents': attempt['completed_agents'],
                         'wall_ns': attempt['wall_ns'], 'improvement_label': label})
    if total_gain != initial_soc-final_soc or (previous_sha and previous_sha != result['final_sha256']):
        raise ValueError('accepted gains or final incumbent chain inconsistent')
    if sum(a['search_calls'] for a in attempts) != result['search_calls']:
        raise ValueError('search accounting mismatch')
    if result['status'] == 'COMPLETE' and (len(attempts) != len(case['orders'])
                                         or result.get('final_validated') is not True):
        raise ValueError('incomplete task marked complete')
    gap = initial_soc - sum(bounds.values())
    if result['status'] != 'COMPLETE':
        decision = 'INCOMPLETE_NO_NEGATIVE_REWARD_LABEL'
    elif gap == 0:
        decision = 'ZERO_SAME_MODEL_GAP_STOP_THIS_TASK'
    elif final_soc == sum(bounds.values()):
        decision = 'CLASSICAL_POLICY_REACHES_BOUND_NO_REMAINING_SOC_HEADROOM'
    elif total_gain:
        decision = 'IMPROVABILITY_OBSERVED_BASELINE_RESIDUAL_NEEDS_DIAGNOSIS'
    else:
        decision = 'POSITIVE_BOUND_GAP_BUT_IMPROVABILITY_UNPROVEN'
    return {'case': case['id'], 'initial_soc': initial_soc, 'final_soc': final_soc,
            'static_h_sum': sum(bounds.values()), 'initial_soc_minus_h': gap,
            'final_soc_minus_h': final_soc-sum(bounds.values()),
            'accepted_gain': total_gain, 'decision': decision, 'attempts': attempts,
            'search_calls': result['search_calls'],
            'expanded': sum(r.get('response', {}).get('num_expanded', 0)
                            for r in result['rpc'] if r['op'] == 'search'),
            'stage_wall_ns': result['stage_wall_ns'],
            'bootstrap_through_native_ready_ns': result['bootstrap_through_native_ready_ns']}


def summarize(manifest, expected_sha):
    raw = manifest.read_bytes()
    if sha(raw) != expected_sha:
        raise ValueError('manifest SHA mismatch')
    config = json.loads(raw)
    if config['batch_id'] != BATCH:
        raise ValueError('this entry cannot rewrite another batch')
    input_raw = (manifest.parent/config['input_file']).read_bytes()
    if sha(input_raw) != config['input_sha256']:
        raise ValueError('input SHA mismatch')
    bundle = json.loads(input_raw)
    root, rows = HERE/'results'/BATCH, []
    if not root.is_dir():
        raise FileNotFoundError('no attempt exists; cannot manufacture a result directory')
    for job in config['jobs']:
        folder = root/job['id']
        row = {'job': job, 'status': 'NOT_RUN'}
        if folder.exists():
            row['status'] = 'INCOMPLETE_ARTIFACTS_RETAINED'
            receipt_path = folder/'receipt.json'
            if receipt_path.exists():
                receipt_raw = receipt_path.read_bytes()
                receipt = json.loads(receipt_raw)
                if receipt['job'] != job or receipt['manifest_sha256'] != expected_sha:
                    raise ValueError('receipt identity mismatch')
                for name, pin in receipt['artifacts'].items():
                    relative = Path(name)
                    if relative.is_absolute() or '..' in relative.parts:
                        raise ValueError('artifact path escapes attempt')
                    data = (folder/relative).read_bytes()
                    if sha(data) != pin['sha256'] or len(data) != pin['bytes']:
                        raise ValueError('changed artifact: '+str(folder/relative))
                row.update({'status': receipt['status'], 'receipt_sha256': sha(receipt_raw),
                            'costs': receipt['costs'],
                            'supervisor_inclusive_before_final_receipt_ns': receipt['supervisor_entry_through_artifact_hash_ns'],
                            'supervisor_self_cpu_s': receipt['supervisor_self_cpu_s']})
                if (folder/'result.json').exists():
                    result = json.loads((folder/'result.json').read_bytes())
                    if (result['manifest_sha256'] != expected_sha or result['case'] != job['case']
                            or result['policy'] != 'REMAINING_BOUND'):
                        raise ValueError('result identity mismatch')
                    # Initialization can fail before producing h: retain unknown.
                    if 'lower_bounds' in result:
                        case = next(c for c in bundle['cases'] if c['id'] == job['case'])
                        row['diagnostic'] = diagnose(case, result)
                    else:
                        row['diagnostic'] = {'decision': 'NATIVE_INITIALIZATION_INCOMPLETE_NO_LABEL'}
        rows.append(row)
    summary = {'scope': 'ONE_STRONG_POLICY_DIAGNOSTIC_NO_SPEEDUP_COMPARISON',
               'manifest_sha256': expected_sha, 'input_sha256': sha(input_raw),
               'postprocessor_sha256': sha(Path(__file__).read_bytes()), 'rows': rows,
               'independent_performance_or_learning_evidence': False}
    write_json(root/'summary.json', summary)
    print(json.dumps({'output': str(root/'summary.json'), 'jobs': len(rows)}))


def costs(manifest, expected_sha):
    """Derive nested cost intervals from completed receipts; no re-timing/search."""
    raw = manifest.read_bytes()
    if sha(raw) != expected_sha:
        raise ValueError('manifest SHA mismatch')
    config = json.loads(raw)
    if config['batch_id'] != BATCH:
        raise ValueError('unexpected batch')
    root = HERE/'results'/BATCH
    summary_raw = (root/'summary.json').read_bytes()
    summary = json.loads(summary_raw)
    if summary['manifest_sha256'] != expected_sha:
        raise ValueError('summary manifest mismatch')
    rows = []
    for row in summary['rows']:
        folder = root/row['job']['id']
        receipt_raw = (folder/'receipt.json').read_bytes()
        receipt = json.loads(receipt_raw)
        if sha(receipt_raw) != row['receipt_sha256'] or receipt['job'] != row['job']:
            raise ValueError('receipt changed')
        for name, pin in receipt['artifacts'].items():
            relative = Path(name)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('invalid artifact path')
            data = (folder/relative).read_bytes()
            if sha(data) != pin['sha256'] or len(data) != pin['bytes']:
                raise ValueError('artifact changed')
        result = json.loads((folder/'result.json').read_bytes())
        callback = result['stage_wall_ns'].get('search', 0)
        rpc = sum(r['wall_ns'] for r in result['rpc'] if r['op'] == 'search')
        if rpc > callback:
            raise ValueError('nested RPC interval exceeds callback interval')
        groups = {}
        for a, recorded in zip(row['diagnostic']['attempts'], result['attempts']):
            group = groups.setdefault(a['diagnosis'], {'attempts': 0, 'search_calls': 0,
                                                      'completed_agents': 0, 'attempt_wall_ns': 0})
            group['attempts'] += 1
            group['search_calls'] += a['search_calls']
            group['completed_agents'] += a['completed_agents']
            group['attempt_wall_ns'] += a['wall_ns']
            lo, hi = recorded['rpc_indices']
            calls = [r for r in result['rpc'][lo:hi] if r['op'] == 'search']
            if len(calls) != a['search_calls']:
                raise ValueError('RPC slice/call mismatch')
        usage = receipt['costs']
        rows.append({'case': result['case'], 'status': receipt['status'], 'groups': groups,
            'search_callback_wall_ns': callback, 'search_rpc_wall_ns': rpc,
            'callback_outside_rpc_wall_ns': callback-rpc,
            'callback_outside_rpc_fraction': (callback-rpc)/callback if callback else None,
            'worker_import_to_exit_wall_ns': usage['wall_ns'],
            'supervisor_inclusive_before_receipt_ns': receipt['supervisor_entry_through_artifact_hash_ns'],
            'all_descendant_cpu_s': usage['all_descendant_user_s']+usage['all_descendant_system_s'],
            'supervisor_self_cpu_s': receipt['supervisor_self_cpu_s'],
            'combined_cpu_before_receipt_s': receipt['supervisor_self_cpu_s']+usage['all_descendant_user_s']+usage['all_descendant_system_s'],
            'native_usage_nested_in_descendants': result['native_usage'],
            'largest_child_maxrss_kib': usage['largest_child_maxrss_kib']})
    value = {'scope': 'OFFLINE_DERIVATION_OF_RECORDED_NESTED_INTERVALS',
        'manifest_sha256': expected_sha, 'summary_sha256': sha(summary_raw),
        'postprocessor_sha256': sha(Path(__file__).read_bytes()), 'rows': rows,
        'interpretation': 'RPC includes pipe wait, native table construction/search and response decode; callback minus RPC includes host validation, hashes and serialization, not a measured breakdown of these components. Worker/supervisor and native/descendant intervals are nested, do not add them. One sample per case, no speedup comparison.'}
    write_json(root/'costs.json', value)
    print(json.dumps({'output': str(root/'costs.json'), 'sha256': sha((root/'costs.json').read_bytes())}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'summarize', 'costs'))
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--sha256')
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare()
    elif args.manifest and args.sha256:
        (costs if args.mode == 'costs' else summarize)(args.manifest, args.sha256)
    else:
        parser.error('summarize requires --manifest and --sha256')
