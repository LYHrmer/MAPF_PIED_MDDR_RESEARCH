"""Reward-ledger verification and offline diagnosis of frozen attempt traces.

No planner is invoked. The legacy reconstruction observes a reward predicate,
not the chosen arm or its posterior (neither was logged in those old traces).
"""
from collections import Counter, deque
import hashlib
import json
import re
import struct
from pathlib import Path

COST_TOTAL_FIELDS = tuple(prefix+'_'+clock+'_ns' for prefix in (
    'candidate_validation', 'candidate_materialization', 'candidate_joint_check',
    'candidate_validation_other', 'post_search_through_settlement') for clock in ('wall', 'cpu'))


def path_identity(paths):
    """Content fingerprint under the already pinned map/model, never a proof."""
    h = hashlib.sha1()
    h.update(struct.pack('<I', len(paths)))
    for path in paths:
        h.update(struct.pack('<I', len(path)))
        for cell in path:
            if type(cell) is not int or not 0 <= cell < 2**32:
                raise ValueError('invalid path identity cell')
            h.update(struct.pack('<I', cell))
    return h.hexdigest()


def shared_search_censored(row):
    observation = row.get('execution_observations', {})
    search = observation.get('search_return')
    return (observation.get('repair_budget_contract') == 'search_then_admission' and
            isinstance(search, dict) and search.get('search_censored') is True)


def verify_execution_event(row, contract, count, posterior, plan_sha, revision):
    """Actual author updates and content identities are distinct from gain audit."""
    o = row.get('execution_observations')
    if not isinstance(o, dict) or (o.get('schema'), o.get('repair_budget_contract')) != (
            'ADDRESS_EXECUTION_OBSERVATIONS_V1', contract):
        raise ValueError('execution observation contract missing/mixed')
    entered, seed = row['repair_attempt_id'] is not None, row['seed_id']
    members, order = o.get('group_members'), o.get('repair_order')
    if (not isinstance(members, list) or not isinstance(order, list) or
            any(type(v) is not int or not 0 <= v < count for v in members+order) or
            len(members) != row['group_size'] or len(set(members)) != len(members) or
            len(order) != len(members) or set(order) != set(members)):
        raise ValueError('actual group/repair order mismatch')
    search, update = o.get('search_return'), o.get('author_update')
    if entered:
        if not isinstance(search, dict) or not isinstance(update, dict):
            raise ValueError('entered repair missing budget/posterior observations')
        for key in ('wall_ns', 'cpu_ns', 'local_remaining_wall_ns',
                    'global_remaining_wall_ns', 'global_remaining_cpu_ns'):
            if type(search.get(key)) is not int:
                raise ValueError('invalid signed search-return time')
        if search['wall_ns'] < 0 or search['cpu_ns'] < 0:
            raise ValueError('negative absolute clock')
        for key in ('search_censored', 'local_deadline_observed', 'global_deadline_observed', 'local_scope_released'):
            if type(search.get(key)) is not bool:
                raise ValueError('invalid search budget flag')
        if (search['search_censored'] != (search['local_deadline_observed'] or search['global_deadline_observed']) or
                search['local_scope_released'] != (contract == 'search_then_admission')):
            raise ValueError('search/admission scope flags disagree')
        if search['search_censored'] and (not row['censored'] or row['accepted']):
            raise ValueError('search expiry was erased at admission')
        if contract == 'search_then_admission' and (
                (search['local_deadline_observed'] and not row['local_deadline']) or
                (search['global_deadline_observed'] and not row['global_deadline'])):
            raise ValueError('recorded search deadline disappeared')
        if (type(update.get('applied')) is not bool or type(update.get('positive_predicate')) is not bool or
                type(update.get('partial_subset_soc')) is not int or update['partial_subset_soc'] < 0 or
                update.get('old_subset_soc') != row['old_subset_soc'] or
                update['positive_predicate'] != (row['old_subset_soc'] > update['partial_subset_soc'])):
            raise ValueError('author predicate lacks actual pre-rollback operands')
        if update.get('index') is not None and (type(update['index']) is not int or not 0 <= update['index'] < count):
            raise ValueError('author index invalid')
        if update['applied'] and update.get('index') != seed:
            raise ValueError('author updated a different selected seed')
        if seed is None:
            raise ValueError('repair without selected seed')
        before = (update.get('alpha_before'), update.get('beta_before'))
        after = (update.get('alpha_after'), update.get('beta_after'))
        if any(type(v) is not int or v < 1 for v in before+after) or before != posterior[seed]:
            raise ValueError('actual author posterior history is discontinuous')
        expected = (before[0]+int(update['applied'] and update['positive_predicate']),
                    before[1]+int(update['applied'] and not update['positive_predicate']))
        if after != expected:
            raise ValueError('author posterior delta differs from actual predicate')
        posterior[seed] = after
    elif search is not None or update is not None:
        raise ValueError('unentered repair has fabricated observations')
    final_posterior = o.get('selected_posterior_after_settlement')
    if seed is None:
        if final_posterior is not None:
            raise ValueError('unselected posterior recorded')
    elif final_posterior != dict(alpha=posterior[seed][0], beta=posterior[seed][1]):
        raise ValueError('committed audit replaced actual author posterior')
    identity = o.get('plan_identity', {})
    if (identity.get('encoding') != 'NATIVE_PATHS_U32LE_SHA1_V1' or identity.get('scope') !=
            'WITHIN_MANIFEST_BOUND_MODEL_NOT_SAFETY_CERTIFICATE' or
            identity.get('before_sha1') != plan_sha or identity.get('revision_before') != revision or
            type(identity.get('revision_after')) is not int or
            identity['revision_after'] != revision+int(row['accepted']) or
            not isinstance(identity.get('after_sha1'), str) or
            not re.fullmatch('[0-9a-f]{40}', identity['after_sha1'])):
        raise ValueError('committed plan identity/revision discontinuity')
    if not row['accepted'] and identity['after_sha1'] != plan_sha:
        raise ValueError('rollback/censor changed plan identity')
    if row['committed_gain'] and identity['after_sha1'] == plan_sha:
        raise ValueError('SOC changed without a changed plan fingerprint')
    return identity['after_sha1'], identity['revision_after']


def verify_candidate_validation_policy(row, expected='all'):
    """A rejected acceptance prerequisite is not a validated candidate reward."""
    policy = row.get('candidate_validation_policy')
    if expected == 'all':
        if policy is not None:
            raise ValueError('undeclared candidate validation gate')
        return False
    if expected != 'acceptance_eligible' or not isinstance(policy, dict):
        raise ValueError('missing/unknown candidate validation policy')
    if policy.get('schema') != 'ADDRESS_CANDIDATE_VALIDATION_V1' or policy.get('mode') != expected:
        raise ValueError('candidate validation policy identity')
    remaining, fresh = policy.get('remaining_agents'), policy.get('fresh_cost_sum_unvalidated')
    entered = row['repair_attempt_id'] is not None
    if entered:
        if (type(remaining) is not int or not 0 <= remaining <= row['group_size'] or
                type(fresh) is not int or fresh < 0):
            raise ValueError('candidate gate lacks actual inspection inputs')
    elif remaining is not None or fresh is not None:
        raise ValueError('unentered candidate gate has inputs')
    result, reason = policy.get('result'), policy.get('skip_reason')
    full = entered and row['fresh_paths'] == row['group_size']
    skipped = result == 'SKIPPED_ACCEPTANCE_INELIGIBLE'
    if skipped:
        if (not full or row['candidate_validated'] or row['accepted'] or row['committed_gain'] or
                row.get('candidate_subset_soc') is not None or row.get('candidate_reward') is not None):
            raise ValueError('skipped candidate became a validated/committed reward')
        expected_reason = ('REMAINING_AGENTS' if remaining != 0 else
                           'COST_EXCEEDS_OLD' if fresh > row['old_subset_soc'] else None)
        if reason != expected_reason or expected_reason is None:
            raise ValueError('candidate gate skipped despite acceptance prerequisites')
    else:
        if reason != 'NONE':
            raise ValueError('unskipped candidate has skip reason')
        if shared_search_censored(row):
            if result != 'SEARCH_CENSORED' or row['candidate_validated'] or not row['censored']:
                raise ValueError('search-censored candidate became eligible')
        elif row['candidate_validated']:
            if (result != 'VALIDATED' or remaining != 0 or fresh > row['old_subset_soc'] or
                    fresh != row['candidate_subset_soc']):
                raise ValueError('validated candidate violates acceptance gate')
        elif full:
            if result != 'DEADLINE' or not row['censored']:
                raise ValueError('unfinished gated validation lacks a deadline')
        elif result != ('INCOMPLETE_SKIPPED' if entered else 'NOT_ENTERED'):
            raise ValueError('partial/unentered candidate gate result mismatch')
    return skipped

def verify_deadline_observations(data):
    """Check sampled deadline evidence; never infer the true crossing instant."""
    if (data.get('wall_clock') != 'STEADY_ABSOLUTE_NS' or
            data.get('cpu_clock') != 'PROCESS_CPU_ABSOLUTE_NS'):
        raise ValueError('deadline observation clock identity')
    observations = [data.get('first_observed_'+kind) for kind in
                    ('deadline', 'local_deadline', 'global_deadline')]
    for o in observations:
        if o is None:
            continue
        flags = [o.get(k+'_triggered') for k in ('local_wall', 'global_wall', 'global_cpu')]
        if any(type(v) is not bool for v in flags) or not any(flags):
            raise ValueError('deadline observation trigger flags')
        local, wall, cpu = flags
        for key in ('observed_wall_ns', 'observed_cpu_ns', 'global_wall_limit_ns', 'global_cpu_limit_ns'):
            if type(o.get(key)) is not int or o[key] < 0:
                raise ValueError('deadline observation clock value')
        limit = o.get('local_wall_limit_ns')
        if limit is not None and (type(limit) is not int or limit < 0):
            raise ValueError('deadline observation local limit')
        if ((local and (limit is None or o['observed_wall_ns'] < limit)) or
                (wall and o['observed_wall_ns'] < o['global_wall_limit_ns']) or
                (cpu and o['observed_cpu_ns'] < o['global_cpu_limit_ns'])):
            raise ValueError('deadline observed before triggered limit')
        # Conversion from double seconds truncates sub-nanosecond differences.
        if ((not local and limit is not None and o['observed_wall_ns'] > limit) or
                (not wall and o['observed_wall_ns'] > o['global_wall_limit_ns']) or
                (not cpu and o['observed_cpu_ns'] > o['global_cpu_limit_ns'])):
            raise ValueError('deadline observation omits an exceeded trigger')
        scope = 'LOCAL_AND_GLOBAL' if local and (wall or cpu) else 'LOCAL' if local else 'GLOBAL'
        resource = 'WALL_AND_CPU' if (local or wall) and cpu else 'WALL' if local or wall else 'CPU'
        if (o.get('scope') != scope or o.get('resource') != resource or
                not isinstance(o.get('stage'), str) or o['stage'] in ('', 'NONE')):
            raise ValueError('deadline observation identity')
    first, local, global_ = observations
    if first is None:
        if local is not None or global_ is not None:
            raise ValueError('missing first observed deadline')
    else:
        if (local is None and global_ is None or
                local is not None and not local['local_wall_triggered'] or
                global_ is not None and not (global_['global_wall_triggered'] or global_['global_cpu_triggered'])):
            raise ValueError('deadline observation scope mismatch')
        if first not in (local, global_):
            raise ValueError('first deadline is not the first local/global observation')
        for o in observations:
            if o is not None and ((o['local_wall_triggered'] and local is None) or
                    ((o['global_wall_triggered'] or o['global_cpu_triggered']) and global_ is None)):
                raise ValueError('triggered deadline missing its first scoped observation')
        if ((first['local_wall_triggered'] and local != first) or
                ((first['global_wall_triggered'] or first['global_cpu_triggered']) and global_ != first)):
            raise ValueError('simultaneous first scoped deadline overwritten')
        for o in observations:
            if o is None:
                continue
            for triggered, saved in ((o['local_wall_triggered'], local),
                    (o['global_wall_triggered'] or o['global_cpu_triggered'], global_)):
                if triggered and any(saved[key] > o[key] for key in ('observed_wall_ns', 'observed_cpu_ns')):
                    raise ValueError('scoped deadline overwritten by later observation')
        for later in (local, global_):
            if later is not None and any(later[key] < first[key] for key in ('observed_wall_ns', 'observed_cpu_ns')):
                raise ValueError('first deadline overwritten by a later observation')


def verify_event_cost(row, candidate_validation='all'):
    d = row['cost_diagnostics']
    if (d.get('schema') != 'ADDRESS_REWARD_COST_V1' or d.get('cost_scope') !=
            'VALIDATION_SUBSET_OF_POST_SEARCH_SUBSET_OF_SELECTION_BEFORE_LOG'):
        raise ValueError('reward cost schema/scope mismatch')
    verify_deadline_observations(d)
    if (d['first_observed_deadline'] is not None) != row['censored']:
        raise ValueError('censor missing first-observed deadline')
    for flag in ('search_return_observed', 'inspection_entered', 'validation_entered', 'seed_pool_completed'):
        if type(d.get(flag)) is not bool:
            raise ValueError('invalid reward cost flag')
    pool = d.get('eligible_topk_candidates')
    if ((type(pool) is int and pool >= 0) != d['seed_pool_completed'] or
            not d['seed_pool_completed'] and pool is not None):
        raise ValueError('partial seed pool cannot be a completed opportunity count')
    if row['seed_id'] is not None and (not d['seed_pool_completed'] or pool < 1):
        raise ValueError('selected seed lacks a completed nonempty pool')
    entered = row['repair_attempt_id'] is not None
    if d['search_return_observed'] != entered or d['inspection_entered'] != entered:
        raise ValueError('repair/search-return/inspection identity mismatch')
    remaining = d.get('remaining_at_search_return')
    if entered:
        if type(remaining) is not int or not 0 <= remaining <= row['group_size']:
            raise ValueError('invalid remaining agents after search')
        if d.get('search_loop_exit_stop') not in ('COMPLETE', 'COST_STOP', 'DEADLINE',
                'START_BLOCKED', 'FOCAL_DRAINED_EMPTY', 'EMPTY_UNCLASSIFIED', 'UNKNOWN'):
            raise ValueError('unknown search-loop return status')
        if d.get('raw_primary_stop_before_finalization') not in ('FOUND', 'COST_STOP', 'DEADLINE',
                'START_BLOCKED', 'FOCAL_DRAINED_EMPTY', 'EMPTY_UNCLASSIFIED', 'UNKNOWN'):
            raise ValueError('unknown raw last search return status')
        if (d['search_loop_exit_stop'] == 'COMPLETE') and remaining != 0:
            raise ValueError('partial search cannot be complete')
    elif remaining is not None or d.get('search_loop_exit_stop') != 'NOT_ENTERED':
        raise ValueError('unentered search has return data')
    full = entered and row['fresh_paths'] == row['group_size']
    search_censored = shared_search_censored(row)
    if d['validation_entered'] != (full and not search_censored):
        raise ValueError('candidate validation entry/fresh-path mismatch')
    result = d.get('validation_result')
    stage = d.get('validation_last_stage')
    skipped = verify_candidate_validation_policy(row, candidate_validation)
    if candidate_validation != 'all' and row['candidate_validation_policy']['remaining_agents'] != remaining:
        raise ValueError('candidate gate differs from actual search-return remaining count')
    if search_censored:
        if result != 'SEARCH_CENSORED' or stage != 'SEARCH_CENSORED' or row['candidate_validated']:
            raise ValueError('search expiry silently resumed validation')
    elif skipped:
        if result != 'SKIPPED_ACCEPTANCE_INELIGIBLE' or stage != 'ACCEPTANCE_GATE':
            raise ValueError('candidate gate/diagnostic result mismatch')
    elif row['candidate_validated']:
        if result != 'VALIDATED' or stage != 'COMPLETE':
            raise ValueError('validated candidate lacks completion state')
    elif full:
        if result != 'DEADLINE' or stage not in ('ENTRY_CHECKPOINT', 'PATH_MATERIALIZATION',
                'MAP_MATERIALIZATION', 'JOINT_CHECK', 'FINAL_CHECKPOINT') or not row['censored']:
            raise ValueError('unfinished validation lacks observed deadline')
    elif result != ('INCOMPLETE_SKIPPED' if entered else 'NOT_ENTERED') or stage != 'NOT_ENTERED':
        raise ValueError('unentered validation state mismatch')
    for clock in ('wall', 'cpu'):
        keys = ['candidate_validation_'+clock+'_ns', 'post_search_through_settlement_'+clock+'_ns',
                'post_search_other_'+clock+'_ns']
        if any(type(d.get(key)) is not int or d[key] < 0 for key in keys):
            raise ValueError('invalid cost diagnostic duration')
        validation, post, other = (d[key] for key in keys)
        if (validation+other != post or post > row['selection_'+clock+'_before_log_ns'] or
                (not full or search_censored) and validation or not entered and post):
            raise ValueError('nested cost diagnostic does not close')
        parts = [d.get('candidate_'+phase+'_'+clock+'_ns') for phase in
                 ('materialization', 'joint_check', 'validation_other')]
        if any(type(value) is not int or value < 0 for value in parts) or sum(parts) != validation:
            raise ValueError('exclusive validation phases do not close')
        if skipped and (parts[0] or parts[1]):
            raise ValueError('skipped candidate still materialized or jointly validated')
    return d


def verify_reward_trace(raw, native, job, count, require_cost_diagnostics=False,
                        initial_paths=None, final_paths=None):
    """Reconcile every selection, retained plan, censor and memory summary."""
    if raw and not raw.endswith(b'\n'):
        raise ValueError('partial reward trace')
    summary = native.get('reward_contract', {})
    mode, width = job['reward_memory'], job['reward_window']
    candidate_validation = job.get('candidate_validation_policy', 'all')
    execution_contract = job.get('repair_budget_contract')
    execution = summary.get('execution_observations')
    if execution_contract is None:
        if execution is not None:
            raise ValueError('undeclared execution observations')
    elif (execution_contract not in ('legacy', 'search_then_admission') or mode != 'author' or
          not isinstance(execution, dict) or execution.get('schema') != 'ADDRESS_EXECUTION_OBSERVATIONS_V1' or
          execution.get('repair_budget_contract') != execution_contract or
          initial_paths is None or final_paths is None):
        raise ValueError('explicit common budget contract and bound paths required')
    if candidate_validation not in ('all', 'acceptance_eligible') or (
            candidate_validation != 'all' and mode != 'author'):
        raise ValueError('unsupported candidate validation policy/memory')
    expected = {'schema': 'ADDRESS_REWARD_V1', 'memory': mode, 'window': width,
                'decision': 'VEHICLE_SEED_PROJECT_ADAPTATION',
                'reward': 'COMMITTED_GAIN_POSITIVE_BERNOULLI', 'prior_alpha': 1, 'prior_beta': 1,
                'posterior_rule': 'AUTHOR_ATTEMPT_BEFORE_ROLLBACK' if mode == 'author' else 'POST_COMMIT_BERNOULLI'}
    if any(summary.get(key) != value for key, value in expected.items()):
        raise ValueError('reward summary identity mismatch')
    def integer(value, minimum=0):
        return type(value) is int and value >= minimum
    arms = [{'seed': seed, 'completed': 0, 'censored': 0,
             'retained_successes': 0, 'retained_failures': 0} for seed in range(count)]
    recent = [deque() for _ in range(count)]
    previous = native['initial_soc']
    selections = repairs = gain = wall = cpu = skipped_candidates = 0
    outcomes = Counter()
    cost_totals = Counter({key: 0 for key in COST_TOTAL_FIELDS})
    diagnostic = 'cost_diagnostics' in summary
    if execution is not None:
        if not diagnostic or (execution.get('initial_plan_sha1'), execution.get('final_plan_sha1')) != (
                path_identity(initial_paths), path_identity(final_paths)):
            raise ValueError('execution plan identity differs from pinned initial/final paths')
        if (type(execution.get('final_revision')) is not int or execution['final_revision'] < 0 or
                any(type(execution.get(k)) is not int or execution[k] < 0 for k in ('identity_wall_ns', 'identity_cpu_ns')) or
                execution.get('identity_cost_is_nested_in_recorded_total') is not True):
            raise ValueError('execution identity cost/revision invalid')
        posterior = [(1, 1) for _ in range(count)]
        plan_sha, revision = execution['initial_plan_sha1'], 0
    first_stages, validation_results, pool_sizes = Counter(), Counter(), Counter()
    if require_cost_diagnostics and not diagnostic:
        raise ValueError('required reward cost diagnostics missing')
    if diagnostic:
        verify_deadline_observations(native['deadline_observations'])
    if candidate_validation == 'all' and 'candidate_validation_policy' in summary:
        raise ValueError('native used undeclared candidate gate')
    for line in raw.splitlines():
        row = json.loads(line)
        if ('execution_observations' in row) != (execution is not None):
            raise ValueError('mixed/missing per-event execution observations')
        selections += 1
        if (row.get('schema') != 'ADDRESS_REWARD_V1' or
                type(row.get('selection_id')) is not int or row['selection_id'] != selections or
                type(row.get('operator_id')) is not int or row['operator_id'] != 0):
            raise ValueError('reward selection identity/duplicate settlement')
        seed, repair = row.get('seed_id'), row.get('repair_attempt_id')
        if seed is not None and (not integer(seed) or seed >= count):
            raise ValueError('invalid reward seed')
        for key in ('old_task_soc', 'group_size', 'fresh_paths', 'committed_task_soc',
                    'committed_gain', 'selection_wall_before_log_ns', 'selection_cpu_before_log_ns'):
            if not integer(row.get(key)):
                raise ValueError('invalid reward integer '+key)
        for key in ('accepted', 'censored', 'candidate_validated', 'local_deadline',
                    'global_deadline', 'memory_eligible'):
            if type(row.get(key)) is not bool:
                raise ValueError('invalid reward flag '+key)
        if (row['old_task_soc'] != previous or row['committed_task_soc'] > previous or
                row['committed_gain'] != previous-row['committed_task_soc']):
            raise ValueError('retained-plan SOC ledger does not close')
        size, fresh = row['group_size'], row['fresh_paths']
        if repair is None:
            if size or fresh or row.get('old_subset_soc') is not None:
                raise ValueError('unentered repair has subset data')
        else:
            repairs += 1
            if (not integer(repair, 1) or repair != repairs or not 0 < size <= count or fresh > size or
                    not integer(row.get('old_subset_soc')) or row['old_subset_soc'] > previous):
                raise ValueError('repair identity / complete candidate mismatch')
        if row['candidate_validated']:
            if (repair is None or fresh != size or not integer(row.get('candidate_subset_soc')) or
                    type(row.get('candidate_reward')) is not int or
                    row['candidate_reward'] != row['old_subset_soc']-row['candidate_subset_soc']):
                raise ValueError('candidate reward is not a complete validated subset')
        elif row.get('candidate_subset_soc') is not None or row.get('candidate_reward') is not None:
            raise ValueError('partial candidate must not have a reward')
        censored = row['local_deadline'] or row['global_deadline']
        if row['censored'] != censored or (censored and row['accepted']):
            raise ValueError('budget censor / acceptance mismatch')
        outcome = 'CENSORED' if censored else 'ACCEPTED' if row['accepted'] else 'NO_GROUP' if repair is None else 'ROLLED_BACK'
        if row.get('outcome') != outcome:
            raise ValueError('incomplete/error reward outcome')
        if row['accepted']:
            if not row['candidate_validated'] or row['committed_gain'] != row['candidate_reward']:
                raise ValueError('accepted gain differs from complete candidate')
        elif row['committed_gain']:
            raise ValueError('rollback/no-group/censor changed the retained plan')
        eligible = seed is not None and not censored
        reward = int(row['committed_gain'] > 0) if eligible else None
        if (row['memory_eligible'] != eligible or row.get('bernoulli_reward') != reward or
                (eligible and type(row.get('bernoulli_reward')) is not int)):
            raise ValueError('memory update includes censor/unselected arm or wrong gain')
        if not isinstance(row.get('stop'), str) or not row['stop']:
            raise ValueError('missing reward stop site')
        if (row.get('deadline_resource') not in ('NONE', 'WALL', 'CPU', 'WALL_AND_CPU') or
                not isinstance(row.get('deadline_stage'), str) or
                (not censored and (row['deadline_resource'] != 'NONE' or row['deadline_stage'] != 'NONE')) or
                (row['global_deadline'] and row['deadline_resource'] == 'NONE')):
            raise ValueError('invalid reward deadline metadata')
        if seed is not None:
            arm = arms[seed]
            if censored:
                arm['censored'] += 1
            else:
                arm['completed'] += 1
                arm['retained_successes' if reward else 'retained_failures'] += 1
                if mode == 'window':
                    recent[seed].append(reward)
                    if len(recent[seed]) > width:
                        old = recent[seed].popleft()
                        arm['retained_successes' if old else 'retained_failures'] -= 1
        if execution is not None:
            plan_sha, revision = verify_execution_event(row, execution_contract, count, posterior, plan_sha, revision)
        previous = row['committed_task_soc']
        gain += row['committed_gain']
        wall += row['selection_wall_before_log_ns']
        cpu += row['selection_cpu_before_log_ns']
        outcomes[outcome] += 1
        if ('cost_diagnostics' in row) != diagnostic:
            raise ValueError('mixed/missing per-event cost diagnostics')
        skipped_candidates += verify_candidate_validation_policy(row, candidate_validation)
        if diagnostic:
            d = verify_event_cost(row, candidate_validation)
            for key in COST_TOTAL_FIELDS:
                cost_totals[key] += d[key]
            first = d['first_observed_deadline']
            first_stages[first['stage'] if first is not None else 'NONE'] += 1
            validation_results[d['validation_result']] += 1
            pool_sizes[str(d['eligible_topk_candidates']) if d['seed_pool_completed'] else 'UNKNOWN'] += 1
    if (previous != native['final_soc'] or gain != native['initial_soc']-native['final_soc'] or
            selections != summary.get('selections') or selections != summary.get('settlements') or
            selections != native.get('group_calls') or repairs != native.get('repair_attempts') or
            summary.get('arms') != arms):
        raise ValueError('reward ledger/native summary does not close')
    for key in ('log_wall_ns', 'log_cpu_ns'):
        if not integer(summary.get(key)):
            raise ValueError('missing reward logging cost')
    if diagnostic and summary['cost_diagnostics'] != dict(schema='ADDRESS_REWARD_COST_V1', **cost_totals):
        raise ValueError('reward cost summary does not close')
    if execution is not None and (plan_sha != execution['final_plan_sha1'] or revision != execution['final_revision']):
        raise ValueError('final committed identity/revision does not close')
    if candidate_validation != 'all' and summary.get('candidate_validation_policy') != dict(
            schema='ADDRESS_CANDIDATE_VALIDATION_V1', mode=candidate_validation,
            skipped_acceptance_ineligible=skipped_candidates):
        raise ValueError('candidate validation gate summary does not close')
    result = {'schema': 'ADDRESS_REWARD_DIAGNOSTIC_V1', 'selections': selections, 'repairs': repairs,
            'outcomes': dict(outcomes), 'actual_committed_gain': gain,
            'selection_wall_before_log_ns': wall, 'selection_cpu_before_log_ns': cpu,
            'log_wall_ns': summary['log_wall_ns'], 'log_cpu_ns': summary['log_cpu_ns'],
            'scope': 'SELECTION_INTERVALS_NOT_TOTAL_RUN_COST',
            'author_arm_summary_is_committed_outcome_audit_not_author_posterior': mode == 'author'}
    if diagnostic:
        result['cost_diagnostics'] = dict(cost_totals,
            first_observed_deadline_stage_counts=dict(first_stages),
            validation_result_counts=dict(validation_results),
            completed_eligible_topk_size_counts=dict(pool_sizes),
            timings_are_nested_not_additive=True,
            historical_uninstrumented_runs_are_not_a_paired_speed_baseline=True)
    if candidate_validation != 'all':
        result['candidate_validation_policy'] = dict(mode=candidate_validation,
            skipped_acceptance_ineligible=skipped_candidates,
            skipped_candidate_reward_is_unknown=True)
    if execution is not None:
        result['execution_observations'] = dict(execution,
            author_posterior_final=[dict(seed=i, alpha=p[0], beta=p[1]) for i, p in enumerate(posterior)],
            observation_scope='MATCHED_EXPLICIT_INSTRUMENTATION_NOT_COUNTERFACTUAL_REPLAY')
    return result


def diagnose_legacy(rows):
    """Reconstruct author's pre-rollback predicate, including partial prefixes."""
    output = []
    for row in rows:
        returned = row['primary_returns']
        partial = sum(call['path_cost'] for call in returned if not call['empty'])
        fresh = sum(not call['empty'] for call in returned)
        gain = row['old_group_cost']-row['final_group_cost']
        censored = row['local_deadline_reached'] or row['global_deadline_reached']
        output.append({'attempt_id': row['attempt_id'], 'stop': row['primary_stop'],
            'fresh_paths': fresh, 'group_size': row['group_size'],
            'all_fresh_paths_returned': fresh == row['group_size'],
            'joint_candidate_validation_recorded': False,
            'pre_rollback_cost_difference': row['old_group_cost']-partial,
            'pre_rollback_positive_predicate': row['old_group_cost'] > partial,
            'committed_gain': gain, 'censored': censored,
            'positive_predicate_with_zero_commit': row['old_group_cost'] > partial and gain == 0,
            'attempt_wall_before_trace_ns': row['cost']['attempt_wall_before_trace_ns'],
            'attempt_cpu_before_trace_ns': row['cost']['attempt_cpu_before_trace_ns']})
    return {'attempts': len(output),
            'positive_predicate_zero_commit_ids': [r['attempt_id'] for r in output if r['positive_predicate_with_zero_commit']],
            'censored_attempts': sum(r['censored'] for r in output),
            'committed_gain': sum(r['committed_gain'] for r in output), 'rows': output}


def committed_magnitude_feedback(rows, initial_soc, final_soc):
    """Project a verified ledger; no selector update or policy estimation.

    A constant task denominator preserves the terminal SOC objective. The
    realized gain of a rolled-back censor is known; its unfinished candidate
    and the counterfactual outcome with more time remain unknown.
    """
    if any(type(v) is not int or v < 0 for v in (initial_soc, final_soc)):
        raise ValueError('invalid task SOC')
    previous, gained, wall, events, zero_wall = initial_soc, 0, 0, 0, 0
    censored, candidate_unknown, censored_wall = 0, 0, 0
    gains, arms = Counter(), {}
    for row in rows:
        before, after, gain, cost = (row[k] for k in (
            'old_task_soc', 'committed_task_soc', 'committed_gain',
            'selection_wall_before_log_ns'))
        if (any(type(v) is not int or v < 0 for v in (before, after, gain, cost))
                or before != previous or after > before or gain != before-after):
            raise ValueError('nonmonotone or broken retained-plan SOC ledger')
        if row['outcome'] not in ('ACCEPTED', 'ROLLED_BACK', 'NO_GROUP', 'CENSORED'):
            raise ValueError('unsettled/invalid event cannot become a reward')
        if (row['censored'] != (row['outcome'] == 'CENSORED') or
                (gain and (not row['accepted'] or not row['candidate_validated'] or row['censored']))):
            raise ValueError('uncommitted candidate cannot become an actual reward')
        seed = row['seed_id']
        if seed is not None and (type(seed) is not int or seed < 0):
            raise ValueError('invalid seed')
        key = 'unselected' if seed is None else str(seed)
        arm = arms.setdefault(key, {'events': 0, 'committed_gain': 0, 'positive_gain_events': 0,
                                   'censored_events': 0, 'recorded_selection_wall_ns': 0})
        arm['events'] += 1
        arm['committed_gain'] += gain
        arm['positive_gain_events'] += int(gain > 0)
        arm['censored_events'] += int(row['censored'])
        arm['recorded_selection_wall_ns'] += cost
        censored += int(row['censored'])
        if row['censored']:
            censored_wall += cost
            candidate_unknown += int(not row['candidate_validated'])
        gains[gain] += 1
        previous, gained, wall, events = after, gained+gain, wall+cost, events+1
        zero_wall += int(cost == 0)
    if previous != final_soc or gained != initial_soc-final_soc:
        raise ValueError('magnitude rewards do not close against final task SOC')
    denominator = max(1, initial_soc)
    return {'schema': 'OFFLINE_COMMITTED_MAGNITUDE_V1', 'events': events,
        'fixed_task_denominator': denominator, 'normalized_reward_sum_exact': [gained, denominator],
        'committed_gain': gained, 'positive_gain_events': events-gains[0],
        'gain_event_counts': dict(sorted(gains.items())), 'per_seed': arms,
        'censored_events': censored, 'censored_actual_committed_gain': 0,
        'censored_candidate_gain_unobserved_events': candidate_unknown,
        'counterfactual_gain_if_given_more_time': None,
        'recorded_selection_wall_ns': wall, 'censored_selection_wall_ns': censored_wall,
        'zero_recorded_wall_events': zero_wall,
        'cost_scope': 'SELECTION_INTERVALS_BEFORE_LOG_NOT_COMPLETE_ATTEMPT_COST',
        'continuous_reward_passed_to_beta': False,
        'online_selector_changed': False, 'policy_performance_estimated': False}


def magnitude_report():
    """Read the frozen 36-item batch; no new actions, fitting or search."""
    root = Path(__file__).resolve().parent
    batch = root/'results/address_reward_holdout_v1'
    raw = (batch/'RUN_RECEIPT.json').read_bytes()
    source_sha = 'e7a131d70d573f87c734ce467282b7835e7f1a74f9c8ca0d6f814903018fe16c'
    if hashlib.sha256(raw).hexdigest() != source_sha:
        raise ValueError('frozen reward comparison receipt changed')
    source = json.loads(raw)
    if source['status'] != 'ALL_COMPLETE':
        raise ValueError('this offline projection expects the frozen complete batch')
    def read(relative):
        raw = (batch/relative).read_bytes()
        pin = source['artifacts'][relative]
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise ValueError('changed frozen reward source: '+relative)
        return raw
    jobs = []
    for entry in source['jobs']:
        stem = entry['job']+'/'
        result = json.loads(read(stem+'result.json'))
        native = json.loads(read(stem+'native_receipt.json'))
        ledger = read(stem+'rewards.jsonl')
        verify_reward_trace(ledger, native, result['job'], len(result['final_paths']))
        projected = committed_magnitude_feedback(
            [json.loads(line) for line in ledger.splitlines()],
            result['initial_soc'], result['final_soc'])
        total = entry['total_entry_through_output_validation_and_hash_ns']
        if projected['recorded_selection_wall_ns'] > total:
            raise ValueError('recorded selection time exceeds complete entry cost')
        jobs.append({'job': entry['job'], 'case': entry['case'],
            'solver_seed': entry['solver_seed'], 'executed_reward_memory': entry['reward_memory'],
            'initial_soc': result['initial_soc'], 'final_soc': result['final_soc'],
            'feedback': projected, 'total_entry_wall_ns': total,
            'reward_log_wall_ns': native['reward_contract']['log_wall_ns'],
            'wall_outside_selection_intervals_ns': total-projected['recorded_selection_wall_ns'],
            'outside_time_is_not_claimed_savable': True})
    return {'scope': 'OFFLINE_FEEDBACK_SEMANTICS_NOT_NEW_POLICY_EVALUATION',
        'source_receipt_sha256': source_sha, 'source_scientific_code_commit': source['scientific_code_commit'],
        'new_scientific_run': False, 'training': False, 'new_selection_or_search': False,
        'formula': 'r_t=(C_before-C_after)/max(1,C_initial); fixed denominator per task',
        'cost_is_recorded_separately': True, 'cost_adjusted_reward_not_computed': True,
        'source_tasks_are_now_design_data_for_this_candidate': True,
        'cross_task_mean_is_not_equivalent_to_unweighted_SOC': True,
        'missing_cost_fields': ['per_event_reward_logging', 'separate_candidate_validation',
                               'first_observed_deadline_site'],
        'jobs': jobs}


def legacy_report():
    from run_address_adapter import verify_attempt_trace
    root = Path(__file__).resolve().parent
    report = {'scope': 'OFFLINE_FROZEN_TRACE_REANALYSIS', 'new_scientific_run': False,
              'distinct_tasks': 2, 'runs_are_not_independent_replicates': True,
              'selected_seed_and_actual_posterior_unobserved': True,
              'build_and_group_cost_not_in_attempt_intervals': True, 'sources': []}
    for batch, suffix in (('address_attempt_trace_v1', 'attempt_trace'), ('address_phase_profile_v1', 'phase_profile')):
        for task in ('maze-32-32-2', 'random-32-32-10'):
            folder = root/'results'/batch/(task+'__s01__n32__'+suffix)
            receipt_raw = (folder/'receipt.json').read_bytes()
            receipt = json.loads(receipt_raw)
            if receipt['status'] != 'COMPLETE':
                raise ValueError('legacy run was not complete')
            source = {'folder': str(folder.relative_to(root)), 'receipt_sha256': hashlib.sha256(receipt_raw).hexdigest()}
            objects = {}
            for name in ('attempts.jsonl', 'native_receipt.json', 'result.json'):
                raw = (folder/name).read_bytes()
                pin = receipt['artifacts'][name]
                if hashlib.sha256(raw).hexdigest() != pin['sha256'] or len(raw) != pin['bytes']:
                    raise ValueError('changed frozen trace '+str(folder/name))
                source[name] = pin
                objects[name] = raw
            native = json.loads(objects['native_receipt.json'])
            verify_attempt_trace(objects['attempts.jsonl'], native, 32)
            source['diagnosis'] = diagnose_legacy([json.loads(line) for line in objects['attempts.jsonl'].splitlines()])
            result = json.loads(objects['result.json'])
            if source['diagnosis']['committed_gain'] != result['initial_soc']-result['final_soc']:
                raise ValueError('legacy committed gain does not match full task')
            report['sources'].append(source)
    return report


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument('--legacy-output', type=Path)
    targets.add_argument('--magnitude-output', type=Path)
    args = parser.parse_args()
    report = legacy_report() if args.legacy_output else magnitude_report()
    report['generator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with (args.legacy_output or args.magnitude_output).open('x') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'sources': len(report.get('sources', report.get('jobs', []))),
                      'distinct_tasks': report.get('distinct_tasks', 4), 'new_scientific_run': False,
                      'output': str(args.legacy_output or args.magnitude_output)}))
