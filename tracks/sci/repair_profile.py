"""Prepare or summarize a fixed strong-policy diagnostic; never run a solver.

Reuse the consumed DEV's unchanged runtime. This proposal requires a NEW actual
user authorization. Positive SOC-minus-h is not an improvement label.
"""
import argparse
import json
from pathlib import Path
import subprocess

from prepare_repair_dev import RUNTIME, prepare_case, sha
from run_repair_dev import HERE, inspect_inputs, load, unpack, write_json

BATCH = 'repair_residual_v1'
FAMILIES = ('maze-32-32-2', 'random-32-32-10', 'warehouse-10-20-10-2-1')
CASES = tuple(f'{family}__s01__n{n:02d}' for family in FAMILIES for n in (16, 32))
FAILURE_SOURCE = '535ee1adf3135ab79565e0b3aa5d189348fe7ab2'


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


def first_path_conflict(left, right):
    """First discrete vertex/swap conflict, with both goals held forever."""
    for t in range(max(len(left), len(right))):
        u, v = left[min(t, len(left)-1)], right[min(t, len(right)-1)]
        if u == v:
            return {'time': t, 'kind': 'VERTEX', 'vertex': u,
                    'left_at_terminal': t >= len(left)-1, 'right_at_terminal': t >= len(right)-1}
        if t and left[min(t-1, len(left)-1)] == v and right[min(t-1, len(right)-1)] == u:
            return {'time': t, 'kind': 'OPPOSITE_EDGE', 'left_edge': [v, u], 'right_edge': [u, v],
                    'left_at_terminal': False, 'right_at_terminal': False}
    return None


def bounded_recovery_plan(problem, incumbent, order, prefix, failed_agent, bounds, *, max_suffix_calls=8):
    """Describe at most one recovery; no path search or incumbent mutation.

    This residual-h-cap rule is a prototype-host proposal, not an ADDRESS rule.
    A new order invalidates the old exhaustive-search/cap conclusion.
    """
    from address_backend import canonical
    order = tuple(order)
    position = order.index(failed_agent)
    if type(max_suffix_calls) is not int or max_suffix_calls < 0 or set(prefix) != set(order[:position]):
        raise ValueError('invalid prefix or proposed suffix allowance')
    fixed = {a: p for a, p in incumbent.items() if a not in order}
    target = sum(len(incumbent[a])-1 for a in order)-1
    old_path = incumbent[failed_agent]
    cap = target-sum(len(p)-1 for p in prefix.values())-sum(bounds[a] for a in order[position+1:])
    result = {'failed_agent': failed_agent, 'original_order': order,
        'max_candidates': 1, 'max_suffix_attempts': 1, 'max_suffix_search_calls': max_suffix_calls,
        'no_recursive_recovery': True, 'old_exhaustion_certificate_reusable': False,
        'original_failed_cap': cap, 'candidates': [], 'selected_candidate': None,
        'status': 'NOT_ELIGIBLE', 'budget_basis': 'PROPOSAL_QUOTA_NOT_A_RUN_AUTHORIZATION'}
    if len(old_path)-1 > cap:
        return dict(result, reason='OLD_PATH_OVER_ORIGINAL_CAP')
    if position+1 <= len(order)/2:
        return dict(result, reason='FAILURE_NOT_IN_SECOND_HALF')
    if any(first_path_conflict(old_path, p) for p in fixed.values()):
        return dict(result, reason='OLD_PATH_CONFLICTS_WITH_FIXED_PATHS')
    blockers = [i for i, a in enumerate(order[:position]) if first_path_conflict(old_path, prefix[a])]
    if not blockers:
        return dict(result, reason='NO_OLD_PATH_PREFIX_BLOCKER')
    # The earliest blocker is the unique insertion point preserving the longest
    # contiguous prefix compatible with this particular old path. Trying a later
    # blocker would knowingly leave an earlier one in the retained prefix.
    cut = min(blockers)
    kept = {a: prefix[a] for a in order[:cut]}
    new_order = order[:cut]+(failed_agent,)+order[cut:position]+order[position+1:]
    suffix = new_order[cut+1:]
    new_cap = target-sum(len(p)-1 for p in kept.values())-sum(bounds[a] for a in suffix)
    remaining_blockers = [a for a, p in kept.items() if first_path_conflict(old_path, p)]
    partial = {**fixed, **kept, failed_agent: old_path}
    candidate = {'order': new_order, 'cut_index': cut, 'retained_prefix_agents': list(kept),
        'retained_prefix_sha256': sha(canonical(sorted(kept.items()))),
        'fixed_paths_sha256': sha(canonical(sorted(fixed.items()))),
        'anchor_old_path_sha256': sha(canonical(old_path)),
        'new_anchor_cap': new_cap, 'suffix_to_recompute': suffix,
        'suffix_search_calls_upper_bound': len(suffix), 'remaining_old_path_blockers': remaining_blockers,
        'status': 'REJECTED_OFFLINE'}
    if remaining_blockers:
        candidate['reason'] = 'OLD_PATH_STILL_BLOCKED_BY_RETAINED_PREFIX'
    elif len(old_path)-1 > new_cap:
        candidate['reason'] = 'OLD_PATH_OVER_NEW_CAP'
    else:
        problem.validate(partial, complete=False)
        candidate['verified_partial_plan_sha256'] = sha(canonical(sorted(partial.items())))
        if len(suffix) > max_suffix_calls:
            candidate['reason'] = 'SUFFIX_EXCEEDS_PROPOSED_CALL_QUOTA'
        else:
            candidate.update(status='ELIGIBLE_PARTIAL_PLAN_ONLY', reason='NO_RECOVERY_SEARCH_PERFORMED')
    result['candidates'].append(candidate)
    if candidate['status'] == 'ELIGIBLE_PARTIAL_PLAN_ONLY':
        result.update(status='DESCRIBED_NOT_EXECUTED', selected_candidate=0,
                      reason='LONGEST_VERIFIED_PREFIX_THEN_AT_MOST_ONE_SUFFIX')
    else:
        result['reason'] = 'NO_ELIGIBLE_CANDIDATE_WITHIN_PROPOSED_QUOTA'
    return result


def reconstruct_failures(case, result, *, recovery_plans=None):
    """Replay recorded paths and hashes only; never invoke the search backend."""
    from address_backend import canonical, MAX_TIMESTEP
    from pp_repair import Incumbent
    checked = diagnose(case, result)
    problem, incumbent = unpack(case)
    bounds = {int(a): h for a, h in result['lower_bounds'].items()}
    failures = []
    for index, (attempt, diagnosis) in enumerate(zip(result['attempts'], checked['attempts'])):
        order = tuple(attempt['order'])
        if Incumbent(incumbent).snapshot().sha256 != attempt['before_sha256']:
            raise ValueError('cannot reconstruct incumbent before attempt')
        old_cost = sum(len(incumbent[a])-1 for a in order)
        if old_cost != attempt['old_cost']:
            raise ValueError('incumbent group cost mismatch')
        fixed = {a: p for a, p in incumbent.items() if a not in order}
        prefix, prefix_cost, prefix_rows = {}, 0, []
        lo, hi = attempt['rpc_indices']
        calls = result['rpc'][lo:hi]
        if len(calls) != attempt['search_calls'] or any(r['op'] != 'search' for r in calls):
            raise ValueError('attempt RPC slice mismatch')
        for position, rpc in enumerate(calls):
            agent = order[position]
            cap = old_cost-1-prefix_cost-sum(bounds[a] for a in order[position+1:])
            constraints = {**fixed, **prefix}
            seed_key = (case['seed'], agent, order, sorted(constraints.items()))
            seed = int(sha(canonical(seed_key))[:8], 16) % MAX_TIMESTEP
            reply = rpc['response']
            request = {'op': 'search', 'seq': reply['seq'], 'agent': problem.native_ids[agent],
                'seed': seed, 'max_cost': cap,
                'fixed_paths': [{'agent': problem.native_ids[a], 'path': p} for a, p in sorted(constraints.items())]}
            wire = canonical(request)+b'\n'
            response_wire = canonical(reply)+b'\n'
            if (sha(wire) != rpc['request_sha256'] or len(wire) != rpc['request_bytes']
                    or sha(response_wire) != rpc['response_sha256']
                    or len(response_wire) != rpc['response_bytes']
                    or reply['effective_max_cost'] != cap):
                raise ValueError('reconstructed native request/response differs from frozen bytes')
            if reply['status'] == 'FOUND':
                path = tuple(reply['path'])
                problem.validate({**constraints, agent: path}, complete=False)
                cost = len(path)-1
                if not bounds[agent] <= cost <= cap or reply['num_collisions'] != 0:
                    raise ValueError('recorded prefix violates its model/cap')
                prefix[agent] = path
                prefix_cost += cost
                prefix_rows.append({'agent': agent, 'cost': cost, 'path_sha256': sha(canonical(path)),
                                    'rpc_index': lo+position})
                continue
            if (reply['status'] != 'EMPTY_CAPPED' or reply['path'] != [] or position != len(calls)-1
                    or diagnosis['diagnosis'] != 'CAP_EXHAUSTED_CURRENT_PREFIX_ONLY'
                    or attempt['completed_agents'] != len(prefix)):
                raise ValueError('unexpected or incomplete failure in frozen complete batch')
            old_path = incumbent[agent]
            if recovery_plans is not None:
                plan = bounded_recovery_plan(problem, incumbent, order, prefix, agent, bounds)
                recovery_plans.append(dict(plan, case=case['id'], attempt_index=index,
                    before_incumbent_sha256=attempt['before_sha256']))
            blockers = []
            for other, path in constraints.items():
                conflict = first_path_conflict(old_path, path)
                if conflict is not None:
                    blockers.append({'agent': other, 'scope': 'PREFIX' if other in prefix else 'FIXED',
                                     'prefix_index': order.index(other) if other in prefix else None,
                                     'first_conflict': conflict})
            blockers.sort(key=lambda x: (x['first_conflict']['time'], x['agent']))
            prefix_blockers = [b['agent'] for b in blockers if b['scope'] == 'PREFIX']
            # Candidate descriptions only: no new path, order evaluation or search.
            moves = []
            if prefix_blockers:
                indices = sorted(order.index(a) for a in prefix_blockers)
                for label, cut in (('LATEST_OLD_PATH_BLOCKER', indices[-1]),
                                   ('EARLIEST_OLD_PATH_BLOCKER', indices[0])):
                    if any(m['cut_index'] == cut for m in moves):
                        continue
                    new_order = order[:cut]+(agent,)+order[cut:position]+order[position+1:]
                    moves.append({'rule': label, 'cut_index': cut, 'order': new_order,
                        'reusable_prefix_agents': list(order[:cut]),
                        'suffix_agents_requiring_new_joint_check_or_replan': list(new_order[cut:]),
                        'remaining_old_path_prefix_blockers': [a for a in prefix_blockers if order.index(a) < cut],
                        'status': 'UNEVALUATED_ORDER_DESCRIPTION_NOT_A_RECOVERY'})
            rpc_wall = sum(r['wall_ns'] for r in calls)
            if rpc_wall > attempt['wall_ns']:
                raise ValueError('nested RPC exceeds attempt wall time')
            failures.append({'case': case['id'], 'attempt_index': index, 'role': diagnosis['role'],
                'before_incumbent_sha256': attempt['before_sha256'],
                'unchanged_after_sha256': attempt['after_sha256'],
                'order': order, 'group_size': len(order), 'old_group_cost': old_cost,
                'strict_group_target': old_cost-1, 'successful_prefix': prefix_rows,
                'successful_prefix_cost': prefix_cost, 'failed_agent': agent, 'failed_order_position_1based': position+1,
                'completed_fraction': len(prefix)/len(order), 'failure_strictly_after_half': position+1 > len(order)/2,
                'failed_cap': cap, 'failed_static_h': bounds[agent], 'cap_minus_h': cap-bounds[agent],
                'failed_old_path_cost': len(old_path)-1,
                'failed_old_path_within_cap': len(old_path)-1 <= cap,
                'failed_old_path_sha256': sha(canonical(old_path)),
                'old_path_blockers': blockers, 'earliest_old_path_conflict': blockers[0] if blockers else None,
                'bounded_order_descriptions': moves,
                'search_calls': len(calls), 'found_calls': len(prefix), 'empty_capped_calls': 1,
                'attempt_wall_ns': attempt['wall_ns'], 'attempt_python_cpu_ns': attempt['cpu_ns'],
                'search_rpc_wall_ns': rpc_wall, 'prefix_found_rpc_wall_ns': sum(r['wall_ns'] for r in calls[:-1]),
                'failed_rpc_wall_ns': rpc['wall_ns'], 'attempt_outside_rpc_wall_ns': attempt['wall_ns']-rpc_wall,
                'expanded': sum(r['response']['num_expanded'] for r in calls),
                'failed_expanded': reply['num_expanded']})
        if attempt['status'] == 'ACCEPTED':
            if len(prefix) != len(order) or prefix_cost != attempt['candidate_cost']:
                raise ValueError('accepted repair reconstruction incomplete')
            incumbent = {**fixed, **prefix}
            problem.validate(incumbent)
        if Incumbent(incumbent).snapshot().sha256 != attempt['after_sha256']:
            raise ValueError('reconstructed after incumbent SHA differs')
    if incumbent != {int(a): tuple(p) for a, p in result['final_paths'].items()}:
        raise ValueError('reconstructed full final plan differs')
    return failures


def failures(output):
    """All 17 historical cap failures, read from fixed Git objects, no solver."""
    output = output.resolve()
    if HERE/'results' in output.parents:
        raise ValueError('frozen result directories are not a derived-output destination')
    if output.exists():
        raise FileExistsError('preserve the existing offline derivation')
    pins = {}
    def read(path):
        relative = 'tracks/sci/'+path
        raw = subprocess.run(['rtk', 'proxy', 'git', 'show', FAILURE_SOURCE+':'+relative],
            cwd=HERE, check=True, stdout=subprocess.PIPE).stdout
        pins[relative] = {'sha256': sha(raw), 'bytes': len(raw)}
        return raw
    manifest_raw = read('config/'+BATCH+'_manifest.json')
    manifest_sha = sha(manifest_raw)
    config = json.loads(manifest_raw)
    input_raw = read('config/'+config['input_file'])
    if config['batch_id'] != BATCH or sha(input_raw) != config['input_sha256']:
        raise ValueError('frozen input identity mismatch')
    bundle = json.loads(input_raw)
    rows, cases = [], []
    for job in config['jobs']:
        stem = 'results/'+BATCH+'/'+job['id']+'/'
        receipt = json.loads(read(stem+'receipt.json'))
        if (receipt['status'] != 'COMPLETE' or receipt['job'] != job
                or receipt['manifest_sha256'] != manifest_sha):
            raise ValueError('expected a complete fixed-source receipt')
        for name, pin in receipt['artifacts'].items():
            relative = Path(name)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('artifact path escape')
            raw = read(stem+name)
            if sha(raw) != pin['sha256'] or len(raw) != pin['bytes']:
                raise ValueError('frozen artifact differs from receipt')
        result = json.loads(read(stem+'result.json'))
        case = next(c for c in bundle['cases'] if c['id'] == job['case'])
        if result['manifest_sha256'] != manifest_sha or result['case'] != case['id']:
            raise ValueError('result identity mismatch')
        reconstructed = reconstruct_failures(case, result)
        rows.extend(reconstructed)
        cases.append({'case': case['id'], 'attempts': len(result['attempts']),
                      'cap_failures': len(reconstructed), 'all_attempts_and_final_plan_reconstructed': True})
    if len(rows) != 17:
        raise ValueError('fixed-source all-failure sample differs from the recorded 17')
    totals = {'failures': len(rows), 'found_prefix_calls': sum(r['found_calls'] for r in rows),
        'all_search_calls_in_failed_attempts': sum(r['search_calls'] for r in rows),
        'failures_strictly_after_half': sum(r['failure_strictly_after_half'] for r in rows),
        'no_old_path_conflict': sum(not r['old_path_blockers'] for r in rows),
        'old_path_over_cap': sum(not r['failed_old_path_within_cap'] for r in rows),
        'old_path_fixed_blockers': sum(sum(b['scope'] == 'FIXED' for b in r['old_path_blockers']) for r in rows),
        'attempt_wall_ns': sum(r['attempt_wall_ns'] for r in rows),
        'search_rpc_wall_ns': sum(r['search_rpc_wall_ns'] for r in rows),
        'prefix_found_rpc_wall_ns': sum(r['prefix_found_rpc_wall_ns'] for r in rows),
        'failed_rpc_wall_ns': sum(r['failed_rpc_wall_ns'] for r in rows)}
    value = {'scope': 'OFFLINE_RECONSTRUCTION_OF_FIXED_HOST_CAP_FAILURES',
        'source_commit': FAILURE_SOURCE, 'source_objects': pins,
        'generator_sha256': sha(Path(__file__).read_bytes()), 'new_scientific_run': False,
        'cases': cases, 'totals': totals, 'failures': rows,
        'limits': ['These fixed ID groups and residual-h caps are not the full ADDRESS recommended policy.',
                   'Old-incumbent-path conflicts do not explain exhaustive SIPP failure, certify recovery or prove global infeasibility.',
                   'Attempt and RPC intervals are nested; prefix RPC is not measured recoverable cost.',
                   'Described priority moves are unevaluated. No incumbent or frozen result was changed.']}
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, value)
    print(json.dumps({'output': str(output), 'sha256': sha(output.read_bytes()), 'totals': totals}, indent=2))


def recoveries(output):
    """Describe a fixed-quota recovery candidate from the existing diagnosis."""
    output = output.resolve()
    if HERE/'results' in output.parents or output.exists():
        raise ValueError('use a fresh derived path outside frozen results')
    diagnosis_raw = (HERE/'derived'/'late_failure_diagnosis.json').read_bytes()
    diagnosis = json.loads(diagnosis_raw)
    if diagnosis['source_commit'] != FAILURE_SOURCE:
        raise ValueError('wrong diagnosis source')
    def read(relative):
        raw = subprocess.run(['rtk', 'proxy', 'git', 'show', FAILURE_SOURCE+':'+relative],
            cwd=HERE, check=True, stdout=subprocess.PIPE).stdout
        pin = diagnosis['source_objects'][relative]
        if sha(raw) != pin['sha256'] or len(raw) != pin['bytes']:
            raise ValueError('source differs from fixed diagnostic input')
        return json.loads(raw)
    bundle = read('tracks/sci/config/'+BATCH+'_inputs.json')
    plans = []
    for case in bundle['cases']:
        result = read('tracks/sci/results/'+BATCH+'/'+case['id']+'__remaining_bound/result.json')
        reconstruct_failures(case, result, recovery_plans=plans)
    if len(plans) != len(diagnosis['failures']):
        raise ValueError('all failure cases must be retained')
    value = {'scope': 'OFFLINE_BOUNDED_RECOVERY_ORDER_DESCRIPTIONS_NO_SEARCH',
        'source_commit': FAILURE_SOURCE, 'diagnosis_sha256': sha(diagnosis_raw),
        'generator_sha256': sha(Path(__file__).read_bytes()), 'new_scientific_run': False,
        'limits': 'Residual-h-cap Python host only; adapt actual ADDRESS stopping/reward semantics before comparisons.',
        'plans': plans, 'described_not_executed': sum(p['selected_candidate'] is not None for p in plans)}
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, value)
    print(json.dumps({'output': str(output), 'sha256': sha(output.read_bytes()),
                      'described_not_executed': value['described_not_executed']}, indent=2))


def prepare_seed_comparison():
    """Freeze two comparison protocols using GIVEN paths; construct no solver."""
    from run_address_adapter import load as load_address
    folder = HERE/'config'
    batches = ('address_seed_fixed_v1', 'address_seed_time_v1')
    targets = [folder/(batch+'_manifest.json') for batch in batches]
    if any(p.exists() for p in targets) or any((HERE/'results'/b).exists() for b in batches):
        raise FileExistsError('preserve existing proposals/results; no implicit regeneration')
    source_input = folder/'repair_residual_v1_inputs.json'
    expected_input = 'be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b'
    if sha(source_input.read_bytes()) != expected_input:
        raise ValueError('given DEV input changed')
    receipt_name = 'seed_admission_build_receipt.json'
    receipt = json.loads((HERE/receipt_name).read_bytes())
    binary = HERE/'../../.address_seed_admission_build/build/address'
    if sha(binary.read_bytes()) != receipt['binary_sha256']:
        raise ValueError('new comparison build differs from receipt')
    base = {'schema': 'address_common_initial_dev_v1', 'authorization': 'PENDING_USER',
            'comparison_protocol': 'seed_admission_v1', 'variant': 'budget_guard',
            'attempt_trace': False, 'phase_profile': False, 'retry': 0,
            'stop_batch_on_any_failure': True, 'previous_authorization_reusable': False,
            'input_file': source_input.name, 'input_sha256': expected_input,
            'binary': '../../.address_seed_admission_build/build/address',
            'binary_sha256': receipt['binary_sha256'], 'build_receipt': receipt_name,
            'code_sha256': {name: sha((HERE/name).read_bytes()) for name in
                ('run_address_adapter.py','run_repair_dev.py','address_backend.py','pp_repair.py',
                 'repair_profile.py',receipt_name)},
            'build_source_sha256': {name: sha((HERE/name).read_bytes()) for name in
                ('build_address_full.py','address_adapter.py','address_adapter_support.h',
                 'address_loop_guard.py','address_budget.py','address_budget_support.h')},
            'scope_limits': ['no new initial solver or tasks', 'no recovery, training or world',
                             'zero retries; first hard failure closes all remaining jobs in both protocols'],
            'evidence_limits': ['existing random32/maze32 are development tasks, never holdout',
                'two policies use the same binary, inputs, low-level solver and per-protocol resource bounds',
                'seed0 does not imply the same candidate sequence after filtering',
                'fixed-count timing is censored unless both arms complete the target',
                'total-budget mode has no repair-count cap; early exact SOC bound is reported',
                'all host, filtering, grouping, repair, verification and output costs remain inside budgets',
                'single DEV pair is not stable speedup, generalization or novelty evidence']}
    configs = []
    cases = ('random-32-32-10__s01__n32', 'maze-32-32-2__s01__n32')
    for batch,mode,budget,outer in ((batches[0],'fixed_repairs',15,20),
                                     (batches[1],'total_budget',5,10)):
        config = dict(base, batch_id=batch, purpose='Simple positive-delay initial-seed control; '+mode,
            limits={'total_wall_s':budget,'worker_cpu_s':10,'native_cpu_s':10,
                    'native_cpu_reserve_s':1,'per_process_as_mib':512,
                    'external_final_reserve_s':.5,'inner_final_reserve_s':1},
            external_command_guard={'required':True,'tool':'timeout','term_after_s':outer,'kill_grace_s':2},
            jobs=[{'id':case+'__'+mode+'__'+policy,'case':case,'seed':0,'top_k':32,
                   'iterations':16 if mode=='fixed_repairs' else 0,
                   'seed_admission':policy,'effort_mode':mode}
                  for case in cases for policy in ('all','positive_delay')])
        config['combined_proposal_order'] = list(batches)
        configs.append(config)
    outputs = []
    for path,config in zip(targets,configs):
        with path.open('x') as stream:
            stream.write(json.dumps(config,indent=2,sort_keys=True)+'\n')
        pin = sha(path.read_bytes())
        checked,bundle,_ = load_address(path,pin)
        by_id = {c['id']:c for c in bundle['cases']}
        for job in checked['jobs']:
            problem,paths = unpack(by_id[job['case']])
            if len(paths)!=32 or job['top_k']!=32:
                raise ValueError('unexpected fixed DEV domain')
        outputs.append({'path':str(path),'sha256':pin,'jobs':len(config['jobs'])})
    print(json.dumps({'proposals':outputs,'scientific_search_executed':False,'new_authorization_required':True},indent=2))


def prepare_reward_comparison():
    """Freeze four historical test tasks, chosen by IDs, not reward outcomes.

    These complete scenarios were absent from s01 reward/seed development, but
    have prior R18 provenance. They are not unseen maps or untouched new data.
    """
    from prepare_repair_dev import ROOT
    from run_address_adapter import load as load_address
    batch = 'address_reward_holdout_v1'
    target = HERE/'config'/(batch+'_manifest.json')
    input_path = HERE/'config'/(batch+'_inputs.json')
    if target.exists() or input_path.exists() or (HERE/'results'/batch).exists():
        raise FileExistsError('preserve prepared inputs/manifests and all attempts')
    chosen = tuple(f'{family}__s{scenario:02d}__n{count:02d}'
                   for family in FAMILIES[:2] for scenario, count in ((4, 16), (5, 32)))
    freeze_raw = (ROOT/'DATA_FREEZE.json').read_bytes()
    freeze = json.loads(freeze_raw)
    cases = []
    for name in chosen:
        case = prepare_case(name)  # Reads and validates frozen plans; no search.
        if case['old_split'] != 'test':
            raise ValueError('expected the historical scenario4/5 test partition')
        for path, pin in case['source_files'].items():
            if freeze['files'].get(path) != pin:
                raise ValueError('repacked input differs from original DATA_FREEZE: '+path)
        case['orders'] = []  # Shared input schema; ADDRESS constructs its own neighbourhoods.
        case['current_split'] = 'HISTORICAL_TEST_HELD_OUT_FROM_S01_REWARD_DESIGN'
        cases.append(case)
    bundle = {'scope': 'FROZEN_COMPLETE_INITIAL_PLANS_NO_NEW_SEARCH',
              'selection': 'two existing maps; scenario4/n16 and scenario5/n32, fixed by IDs before outcomes',
              'historical_dataset_freeze_sha256': sha(freeze_raw),
              'historical_data_never_claimed_untouched': True,
              'independent_task_units': 4, 'new_maps': False,
              'density_and_scenario_effects_not_separately_identifiable': True,
              'generator_sha256': sha(Path(__file__).read_bytes()), 'cases': cases}
    write_json(input_path, bundle)
    receipt_name = 'reward_contract_build_receipt.json'
    receipt = json.loads((HERE/receipt_name).read_bytes())
    modes = ('author', 'cumulative', 'window')
    jobs = []
    # Every seed block contains all modes; Latin rotation balances within-block
    # execution position. Identical seeds do not imply identical neighbourhoods.
    for seed in (0, 1, 2):
        for index, case in enumerate(cases):
            offset = (seed+index) % 3
            for mode in modes[offset:]+modes[:offset]:
                jobs.append({'id': case['id']+f'__seed{seed}__'+mode, 'case': case['id'],
                    'seed': seed, 'iterations': 0, 'top_k': len(case['paths']),
                    'seed_admission': 'positive_delay', 'effort_mode': 'total_budget',
                    'reward_memory': mode, 'reward_window': 16 if mode == 'window' else 0})
    config = {'schema': 'address_common_initial_dev_v1', 'authorization': 'PENDING_USER',
        'batch_id': batch, 'comparison_protocol': 'reward_memory_v1', 'variant': 'reward_contract',
        'evidence_scope': 'HELD_OUT_FROM_REWARD_DESIGN_HISTORICAL_TASK_PILOT',
        'input_file': input_path.name, 'input_sha256': sha(input_path.read_bytes()),
        'binary': '.address_reward_build/final/build/address', 'binary_sha256': receipt['binary_sha256'],
        'build_receipt': receipt_name,
        'code_sha256': {name: sha((HERE/name).read_bytes()) for name in
            ('run_address_adapter.py', 'run_repair_dev.py', 'address_backend.py', 'pp_repair.py',
             'repair_profile.py', 'reward_analysis.py', receipt_name)},
        'build_source_sha256': {name: sha((HERE/name).read_bytes()) for name in
            ('build_address_full.py', 'address_adapter.py', 'address_adapter_support.h',
             'address_loop_guard.py', 'address_budget.py', 'address_budget_support.h',
             'address_reward.py', 'address_reward_support.h')},
        'limits': {'total_wall_s': 5, 'worker_cpu_s': 10, 'native_cpu_s': 10,
                   'per_process_as_mib': 512, 'external_final_reserve_s': 1,
                   'inner_final_reserve_s': 1, 'native_cpu_reserve_s': 1},
        'external_command_guard': {'tool': 'timeout', 'required': True,
                                   'term_after_s': 10, 'kill_grace_s': 2},
        'retry': 0, 'attempt_trace': False, 'phase_profile': False,
        'stop_batch_on_any_failure': True, 'previous_authorization_reusable': False,
        'new_initial_search': False, 'training': False, 'world': False, 'jobs': jobs,
        'contrasts': ['author_vs_cumulative: settlement semantics including censor/empty group',
                      'cumulative_vs_window16: same committed Bernoulli reward, memory only'],
        'primary_endpoint': 'final_validated_full_plan_SOC_within_total_admission_budget',
        'secondary_endpoints': ['makespan', 'full_cost', 'censor_rate', 'failure', 'per_selection_gain_and_cost'],
        'decision_rule': 'repair counts alone are not benefit; retain all losses/zero differences; no W tuning or added seeds in this batch'}
    write_json(target, config)
    load_address(target, sha(target.read_bytes()))
    print(json.dumps({'manifest': str(target), 'manifest_sha256': sha(target.read_bytes()),
                      'input_sha256': config['input_sha256'], 'jobs': len(jobs),
                      'tasks': len(cases), 'scientific_search_executed': False}))


def shared_budget_coverage(rows, contract):
    """Project already-verified events; no search or counterfactual replay.

    Validation duration starts after search_return. Exceeding its nonnegative
    local margin by >2 ns is a sufficient (not necessary) crossing witness;
    the guard avoids promoting integer-ns rounding into coverage.
    """
    if contract not in ('legacy', 'search_then_admission'):
        raise ValueError('unknown shared budget contract')
    common = contract == 'search_then_admission'
    witnesses = {key: [] for key in ('search_local_cutoff_rollback', 'search_global_cutoff_rollback',
        'global_cutoff_rollback', 'validated_then_global_cutoff_rollback',
        'normal_complete_search_validated', 'normal_complete_search_committed',
        'legacy_admission_local_cutoff_global_remaining',
        'common_validation_proven_beyond_local_margin', 'common_commit_proven_beyond_local_margin')}
    unproven = 0
    for row in rows:
        o, d = row['execution_observations'], row['cost_diagnostics']
        if o['repair_budget_contract'] != contract:
            raise ValueError('coverage contract differs from verified event')
        search, identity = o['search_return'], o['plan_identity']
        def mark(key): witnesses[key].append(row['selection_id'])
        if row['censored']:
            if (row['accepted'] or identity['revision_after'] != identity['revision_before'] or
                    identity['after_sha1'] != identity['before_sha1']):
                raise ValueError('cutoff changed committed plan')
        if row['global_deadline']:
            mark('global_cutoff_rollback')
            if row['candidate_validated']: mark('validated_then_global_cutoff_rollback')
        if search is None:
            continue
        if search['local_deadline_observed']: mark('search_local_cutoff_rollback')
        if search['global_deadline_observed']: mark('search_global_cutoff_rollback')
        complete = (not search['search_censored'] and row['fresh_paths'] == row['group_size'] > 0
                    and d['remaining_at_search_return'] == 0)
        if not complete:
            continue
        if row['candidate_validated']: mark('normal_complete_search_validated')
        if row['accepted']: mark('normal_complete_search_committed')
        local = d['first_observed_local_deadline']
        if (not common and local is not None and
                (local['stage'].startswith('REWARD_VALIDATION') or local['stage'] == 'ACCEPT') and
                local['global_wall_limit_ns'] > local['observed_wall_ns'] + 2 and
                local['global_cpu_limit_ns'] > local['observed_cpu_ns'] + 2 and
                not local['global_wall_triggered'] and not local['global_cpu_triggered']):
            mark('legacy_admission_local_cutoff_global_remaining')
        if common and row['candidate_validated']:
            margin = search['local_remaining_wall_ns']
            proven = margin >= 0 and d['candidate_validation_wall_ns'] > margin + 2
            if proven:
                mark('common_validation_proven_beyond_local_margin')
                if row['accepted']: mark('common_commit_proven_beyond_local_margin')
            else:
                unproven += 1
    def summarize(key, ids):
        applicable = not ((common and key.startswith('legacy_')) or (not common and key.startswith('common_')))
        return dict(status=('NOT_APPLICABLE' if not applicable else 'EXERCISED' if ids else 'NOT_EXERCISED'),
                    count=len(ids),example_selection_ids=ids[:8])
    return dict(schema='ADDRESS_SHARED_BUDGET_FUNCTIONAL_COVERAGE_V1',repair_budget_contract=contract,
        coverage={key: summarize(key, ids) for key, ids in witnesses.items()},
        common_validated_events_without_direct_crossing_proof=unproven,
        unproven_event_interpretation='UNKNOWN_NOT_EVIDENCE_OF_NO_CROSSING',
        cutoff_rejection_identity_checked=True,rounding_guard_ns=2,
        settlement_time_not_used_as_commit_time=True,between_run_candidate_identity_assumed=False,
        evidence_scope='KNOWN_TASK_SINGLE_SEED_FUNCTIONAL_NOT_BENEFIT_COMPARISON')


def address_results(manifest, expected_sha, output=None):
    """Audit the completed/stopped ADDRESS batch; never launch or retry a job."""
    manifest = manifest.resolve()
    raw = manifest.read_bytes()
    if sha(raw) != expected_sha:
        raise ValueError('ADDRESS manifest SHA mismatch')
    config = json.loads(raw)
    if config['schema'] != 'address_common_initial_dev_v1' or config['retry'] != 0:
        raise ValueError('unexpected ADDRESS batch contract')
    raw_inputs = (manifest.parent/config['input_file']).read_bytes()
    if sha(raw_inputs) != config['input_sha256']:
        raise ValueError('ADDRESS input identity changed')
    cases = {case['id']: case for case in json.loads(raw_inputs)['cases']}
    batch = HERE/'results'/config['batch_id']
    output = output or batch/'RUN_RECEIPT.json'
    if output.exists():
        raise FileExistsError('preserve original batch audit; choose a new output')
    auth = json.loads((batch/'AUTHORIZATION.json').read_bytes())
    if auth['manifest_sha256'] != expected_sha or auth['jobs'] != [j['id'] for j in config['jobs']]:
        raise ValueError('authorization record / manifest mismatch')
    rows, failed_job = [], None
    for job in config['jobs']:
        folder = batch/job['id']
        problem, initial = unpack(cases[job['case']])
        row = {'job': job['id'], 'case': job['case'],
               'initial_soc': sum(len(p)-1 for p in initial.values()),
               'initial_makespan': max(len(p)-1 for p in initial.values()),
               'final_soc': None, 'final_makespan': None, 'improvement': None}
        if not folder.exists():
            if failed_job is None:
                raise ValueError('unattempted job before a recorded batch stop')
            row['status'] = 'NOT_RUN_AFTER_BATCH_STOP'
            rows.append(row)
            continue
        if failed_job is not None:
            raise ValueError('job attempted after the first failure')
        missing, unreadable, records, terminal_bytes = [], [], {}, {}
        for name in ('receipt.json', 'result.json', 'attempt.json'):
            if not (folder/name).is_file():
                missing.append(name)
                continue
            terminal_bytes[name] = (folder/name).read_bytes()
            try:
                record = json.loads(terminal_bytes[name])
            except (ValueError, UnicodeDecodeError):
                unreadable.append(name)
                continue
            if not isinstance(record, dict):
                unreadable.append(name)
                continue
            if record.get('job') != job or record.get('manifest_sha256') != expected_sha:
                raise ValueError('ADDRESS job identity mismatch')
            records[name] = record
        receipt, result = records.get('receipt.json'), records.get('result.json')
        if receipt is not None:
            if receipt.get('status') not in ('COMPLETE', 'FAILED_OR_INCOMPLETE'):
                raise ValueError('unknown ADDRESS terminal status')
            for name, pin in receipt['artifacts'].items():
                relative = Path(name)
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('artifact path escape')
                if not (folder/relative).is_file():
                    if name not in missing:
                        missing.append(name)
                    continue
                artifact = (folder/relative).read_bytes()
                if sha(artifact) != pin['sha256'] or len(artifact) != pin['bytes']:
                    raise ValueError('ADDRESS evidence bytes changed: '+name)
            row.update(receipt_sha256=sha(terminal_bytes['receipt.json']),
                       total_entry_through_output_validation_and_hash_ns=
                           receipt['total_entry_through_output_validation_and_hash_ns'],
                       costs=receipt['costs'])
        if missing or unreadable:
            # A killed writer can leave no JSON or a truncated JSON. Verify all
            # available identities/pins first, then retain real supervisor costs.
            failed_job = job['id']
            row.update(status='FAILED_OR_INCOMPLETE', missing_artifacts=missing,
                       unreadable_artifacts=unreadable,
                       reason='incomplete terminal evidence after external stop',
                       initial_retained_is_not_a_successful_final_output=True,
                       stage_wall_ns=result.get('stage_wall_ns') if result else None)
            if receipt is None:
                row.update(total_entry_through_output_validation_and_hash_ns=None, costs=None)
            rows.append(row)
            continue
        if result['case'] != job['case'] or result['initial_soc'] != row['initial_soc']:
            raise ValueError('ADDRESS initial plan identity mismatch')
        row.update(status=receipt['status'], stage_wall_ns=result['stage_wall_ns'])
        if receipt['status'] == 'COMPLETE':
            final = {int(a): tuple(p) for a, p in result['final_paths'].items()}
            problem.validate(final)  # Offline audit, outside the recorded run timing.
            soc = sum(len(p)-1 for p in final.values())
            makespan = max(len(p)-1 for p in final.values())
            if (result['status'] != 'COMPLETE' or not result['final_validated']
                or receipt['costs']['exit_code'] != 0 or receipt['costs']['forced_cleanup']
                or row['total_entry_through_output_validation_and_hash_ns'] >= config['limits']['total_wall_s']*1e9
                or soc != result['final_soc'] or makespan != result['final_makespan']
                or soc > row['initial_soc']):
                raise ValueError('ADDRESS complete result violates its contract')
            row.update({'final_soc': soc, 'final_makespan': makespan,
                        'improvement': row['initial_soc']-soc})
            if config.get('attempt_trace', False):
                from run_address_adapter import verify_attempt_trace
                summary = verify_attempt_trace((folder/'attempts.jsonl').read_bytes(),
                                               result['native_receipt'], len(problem.ids))
                if summary != result.get('attempt_diagnostics'):
                    raise ValueError('offline attempt diagnosis disagrees with worker')
                row['attempt_diagnostics'] = summary
            if config.get('phase_profile', False):
                from run_address_adapter import verify_phase_profile
                profile = verify_phase_profile(result['native_receipt'], config)
                if profile != result.get('phase_diagnostics'):
                    raise ValueError('offline phase accounting disagrees with worker')
                row['phase_diagnostics'] = profile
            if config.get('comparison_protocol'):
                from run_address_adapter import verify_budget_receipt, verify_seed_comparison
                verify_budget_receipt(result['native_receipt'], config)
                summary = verify_seed_comparison(result['native_receipt'], config, job)
                if summary != result.get('comparison_diagnostics'):
                    raise ValueError('offline seed comparison differs from worker')
                row['comparison_diagnostics'] = summary
            if config.get('comparison_protocol') in ('reward_memory_v1', 'reward_cost_diagnostic_v1', 'candidate_validation_v1', 'shared_budget_v1'):
                from reward_analysis import verify_reward_trace
                summary = verify_reward_trace((folder/'rewards.jsonl').read_bytes(),
                                              result['native_receipt'], job, len(problem.ids),
                                              require_cost_diagnostics=config.get('cost_diagnostics', False),
                                              initial_paths=[initial[a] for a in problem.ids] if config.get('execution_observations') else None,
                                              final_paths=[final[a] for a in problem.ids] if config.get('execution_observations') else None)
                if summary != result.get('reward_diagnostics'):
                    raise ValueError('offline reward ledger differs from worker')
                row['reward_diagnostics'] = summary
                row['reward_memory'], row['reward_window'], row['solver_seed'] = (
                    job['reward_memory'], job['reward_window'], job['seed'])
                if config.get('comparison_protocol') in ('candidate_validation_v1', 'shared_budget_v1'):
                    row['candidate_validation_policy'] = job['candidate_validation_policy']
                if config.get('comparison_protocol') == 'shared_budget_v1':
                    row['repair_budget_contract'] = job['repair_budget_contract']
                    row['functional_coverage'] = shared_budget_coverage(
                        [json.loads(line) for line in (folder/'rewards.jsonl').read_bytes().splitlines()],
                        job['repair_budget_contract'])
        elif receipt['status'] == 'FAILED_OR_INCOMPLETE':
            failed_job = job['id']
            row['reason'] = result.get('reason', 'missing success validation')
            row['initial_retained_is_not_a_successful_final_output'] = True
        else:
            raise ValueError('unknown ADDRESS terminal status')
        rows.append(row)
    artifacts = {str(p.relative_to(batch)): {'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
                 for p in sorted(batch.rglob('*')) if p.is_file()}
    reward_comparison = config.get('comparison_protocol') == 'reward_memory_v1'
    cost_diagnostic = config.get('comparison_protocol') == 'reward_cost_diagnostic_v1'
    validation_comparison = config.get('comparison_protocol') == 'candidate_validation_v1'
    shared_budget = config.get('comparison_protocol') == 'shared_budget_v1'
    value = {'scope': 'ADDRESS_SHARED_BUDGET_CONTRACT_DEV' if shared_budget else
                     'ADDRESS_COMMON_ENGINEERING_VALIDATION_GATE_DEV' if validation_comparison else
                     'ADDRESS_REWARD_COST_KNOWN_TASK_DIAGNOSTIC' if cost_diagnostic else
                     'ADDRESS_REWARD_HELDOUT_TASK_PILOT' if reward_comparison else 'ADDRESS_FUNCTIONAL_DEV_STOPPED_BATCH_AUDIT',
        'manifest_sha256': expected_sha, 'scientific_code_commit': auth['scientific_code_commit'],
        'analyzer_sha256': sha(Path(__file__).read_bytes()), 'new_search_by_analyzer': False,
        'status': 'STOPPED_ON_FIRST_FAILURE' if failed_job else 'ALL_COMPLETE',
        'first_failed_job': failed_job, 'jobs': rows, 'artifacts': artifacts,
        'counts': {status: sum(row['status'] == status for row in rows)
                   for status in ('COMPLETE', 'FAILED_OR_INCOMPLETE', 'NOT_RUN_AFTER_BATCH_STOP')},
        'authorization_consumed_or_closed': True, 'retry_allowed': False,
        'remaining_jobs_require_new_authorization': bool(failed_job),
        'limits': [('explicit shared budget contract and matched observations; candidate audit policy is a separate declared factor; no innovation or unseen-task claim'
                    if shared_budget else 'two known design tasks; seed zero; all versus acceptance_eligible validation in the same binary; common engineering DEV, not a new reward method'
                    if validation_comparison else 'two known design tasks; three within-task seeds; author mode only; observations do not establish a new policy benefit'
                    if cost_diagnostic else 'four held-out-from-reward-design historical tasks; solver seeds are within-task repeats; no offline training'
                    if reward_comparison else 'single functional DEV, no candidate recovery or learning'),
                   'historical fixed-ID probe times are not paired performance baselines',
                   'failures and unattempted jobs retained; no survivor-only aggregate',
                   'nested native/worker/entry timings must not be added',
                   'offline audit timing is separate from recorded scientific run costs']}
    if reward_comparison:
        # Fixed paired contrasts. Missing/failing arms remain explicit, and seed
        # repeats never turn four task instances into twelve independent tasks.
        by_id = {row['job']: row for row in rows}
        paired = []
        for case in dict.fromkeys(j['case'] for j in config['jobs']):
            for seed in sorted({j['seed'] for j in config['jobs'] if j['case'] == case}):
                group = {j['reward_memory']: by_id[j['id']] for j in config['jobs']
                         if j['case'] == case and j['seed'] == seed}
                for first, second in (('author', 'cumulative'), ('cumulative', 'window')):
                    a, b = group[first], group[second]
                    complete = a['status'] == b['status'] == 'COMPLETE'
                    paired.append({'case': case, 'solver_seed': seed, 'first': first, 'second': second,
                        'statuses': [a['status'], b['status']], 'both_complete': complete,
                        'soc_first_minus_second': a['final_soc']-b['final_soc'] if complete else None,
                        'makespan_first_minus_second': a['final_makespan']-b['final_makespan'] if complete else None})
        value['paired_contrasts'] = paired
    if validation_comparison:
        pairs = []
        for first, second in zip(rows[::2], rows[1::2]):
            both = first['status'] == second['status'] == 'COMPLETE'
            pairs.append({'case': first['case'], 'first': 'all', 'second': 'acceptance_eligible',
                'statuses': [first['status'], second['status']], 'both_complete': both,
                'soc_first_minus_second': first['final_soc']-second['final_soc'] if both else None,
                'makespan_first_minus_second': first['final_makespan']-second['final_makespan'] if both else None,
                'scope': 'FINAL_QUALITY_AT_COMMON_TOTAL_BUDGET_NOT_EQUAL_WORK_SPEEDUP'})
        value['paired_contrasts'] = pairs
    write_json(output, value)
    print(json.dumps({'output': str(output), 'sha256': sha(output.read_bytes()),
                      'status': value['status'], 'counts': value['counts'], 'jobs': rows}, indent=2))


def outside_repair(output=None):
    """Analyze frozen trace bytes and pinned source; no solver or new timings."""
    source_commit = '7e77e9a4310928a7a273d4dac458d5536e7450d4'
    batch = HERE/'results/address_attempt_trace_v1'
    expected = '308e5a65e98270b6049336dff0c50da88bbbf137755fc2875a9203d91d5a8632'
    raw = (batch/'RUN_RECEIPT.json').read_bytes()
    if sha(raw) != expected:
        raise ValueError('frozen trace batch changed')
    receipt = json.loads(raw)
    for name, pin in receipt['artifacts'].items():
        artifact = (batch/name).read_bytes()
        if sha(artifact) != pin['sha256'] or len(artifact) != pin['bytes']:
            raise ValueError('frozen trace artifact changed: '+name)
    # Read the actual compiled overlay, not current mutable budget source.
    build = json.loads((HERE/'budget_trace_build_receipt.json').read_bytes())
    source = HERE.parents[1]/'.address_attempt_trace_build/source_overlay/src/LNS.cpp'
    source_raw = source.read_bytes()
    source_pin = build['extension_sources']['address_budget']['src/LNS.cpp']['sha256']
    if sha(source_raw) != source_pin:
        raise ValueError('frozen compiled LNS source changed')
    source_text = source_raw.decode()
    for anchor in ('if(!succ)\n            continue;', 'a = i;',
                   'if (neighbor.sum_of_costs >= neighbor.old_sum_of_costs)'):
        if anchor not in source_text:
            raise ValueError('fixed source anchor missing')
    rows = []
    for item in receipt['jobs']:
        folder = batch/item['job']
        result = json.loads((folder/'result.json').read_bytes())
        native = result['native_receipt']
        attempts = [json.loads(line) for line in (folder/'attempts.jsonl').read_text().splitlines()]
        attempt_ns = sum(a['cost']['attempt_wall_before_trace_ns'] for a in attempts)
        inner_ns = round(native['inner_wall_before_receipt_s']*1e9)
        trace_ns = native['trace_io_wall_ns']
        if inner_ns < attempt_ns+trace_ns:
            raise ValueError('nested times exceed native window')
        formed = [a['group_calls_so_far'] for a in attempts]
        rows.append({'job': item['job'], 'total_entry_ns': item['total_entry_through_output_validation_and_hash_ns'],
            'native_window_ns': inner_ns, 'recorded_attempt_wall_before_trace_ns': attempt_ns,
            'trace_io_wall_ns': trace_ns,
            'native_outside_recorded_attempt_and_trace_ns': inner_ns-attempt_ns-trace_ns,
            'residual_is_not_group_time_or_savable_time': True,
            'group_calls': native['group_calls'], 'formed_group_call_indices': formed,
            'calls_after_last_recorded_repair': native['group_calls']-(formed[-1] if formed else 0),
            'calls_after_last_repair_may_include_interrupted_call': True,
            'sipp_calls': native['sipp_calls'],
            'phases_unmeasured': ['preprocessing', 'top_k', 'beta_sampling', 'walk',
                                  'budget_clock_overhead', 'outer_loop_other']})
    value = {'scope': 'FROZEN_TRACE_AND_SOURCE_ANALYSIS_NO_NEW_SCIENTIFIC_RUN',
        'source_evidence_commit': source_commit, 'batch_receipt_sha256': expected,
        'frozen_compiled_lns_sha256': source_pin, 'analyzer_sha256': sha(Path(__file__).read_bytes()),
        'new_search': False, 'new_runtime_measurement': False, 'jobs': rows,
        'source_findings': [
            'Failed group construction continues before iteration_stats grows.',
            'For n=k=32 each completed bernoulie call has 96 per-element budget checks across heap build, extraction and beta sampling; this is a source-derived count, not a measured time.',
            'Top-k heap and its extraction order are rebuilt even if incumbent paths have not changed.',
            'Random-walk continuation uses set-position i as agent ID instead of element n; any correction is a shared baseline change requiring explicit validation.',
            'Do not change clock frequency, tie order, RNG, reward or acceptance while measuring phases.'],
        'decision': 'Add opt-in disjoint phase accounting and bounded clock sampling before choosing an optimization.'}
    output = output or batch/'NONREPAIR_ANALYSIS.json'
    if output.exists():
        raise FileExistsError('preserve prior offline analysis; choose another output')
    write_json(output, value)
    print(json.dumps({'output': str(output), 'sha256': sha(output.read_bytes()),
                      'new_search': False, 'jobs': rows}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'summarize', 'costs', 'failures', 'recoveries', 'address', 'outside_repair', 'prepare_seed_comparison', 'prepare_reward_comparison'))
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--sha256')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.mode == 'outside_repair':
        outside_repair(args.output)
    elif args.mode == 'prepare_seed_comparison':
        prepare_seed_comparison()
    elif args.mode == 'prepare_reward_comparison':
        prepare_reward_comparison()
    elif args.mode == 'prepare':
        prepare()
    elif args.mode == 'failures':
        failures(args.output or HERE/'derived'/'late_failure_diagnosis.json')
    elif args.mode == 'recoveries':
        recoveries(args.output or HERE/'derived'/'late_failure_recovery_candidates.json')
    elif args.mode == 'address' and args.manifest and args.sha256:
        address_results(args.manifest, args.sha256, args.output)
    elif args.manifest and args.sha256:
        (costs if args.mode == 'costs' else summarize)(args.manifest, args.sha256)
    else:
        parser.error('summarize requires --manifest and --sha256')
