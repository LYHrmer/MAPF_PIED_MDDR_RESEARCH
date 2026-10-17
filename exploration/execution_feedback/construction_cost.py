"""Audit solver-cost completeness using existing Costs and runner receipts.

Pure receipt processing: no timers, sessions, public-protocol fields or runner
changes. Missing timings stay unknown. Diagnostic nested segments are never
summed. This audit cannot authenticate measurements or establish a speedup.
"""
import hashlib
import json


COMMON_FIELDS = (
    'source', 'paths_order', 'geometry', 'analytic_fast_path', 'feedback_events',
    'motion_clocks', 'safety_precision', 'cache_policy', 'fallback_budget',
)
COMPONENTS = (
    'source_and_input_validation', 'geometry_and_support', 'analytic_and_derivatives',
    'witness_validation', 'queue_and_branch_selection', 'cache_lookup_invalidation',
    'fallback_and_discarded_work', 'feedback_and_constraint_update',
    'control_to_END', 'serialization_and_log_IO',
)
MANDATORY = {'source_and_input_validation', 'geometry_and_support',
             'control_to_END', 'serialization_and_log_IO'}
PROCESS_SCOPE = 'spawn through child exit, including imports, final serialization and log I/O'


def common_key(commitments):
    """Commit to the SAME common kernels/policies, not just the same map."""
    if set(commitments) != set(COMMON_FIELDS):
        raise ValueError('complete common comparison commitments required')
    if any(not isinstance(v, str) or len(v) != 64 or any(c not in '0123456789abcdef' for c in v)
           for v in commitments.values()):
        raise ValueError('each common commitment must be a SHA256 digest')
    return hashlib.sha256(json.dumps(commitments, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def cache_key(commitments, *, task, pair, offsets, allowed_set_sha256, precision, kernel_sha256):
    """Changing feedback domain or action clocks invalidates reuse.

    allowed_set must identify the full JOINT parameter domain, not only its
    axis projections. The algorithm/kernel identity remains part of the key.
    Generating a key does not prove that a caller used a valid joint set.
    """
    from protocol import exact
    if (not isinstance(task, str) or not task or len(pair) != 2
            or any(not isinstance(x, str) or not x for x in pair) or len(offsets) != 2):
        raise ValueError('task, ordered action pair and both physical offsets required')
    if exact(precision) <= 0:
        raise ValueError('positive time precision required')
    for value in (allowed_set_sha256, kernel_sha256):
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('joint allowed-set and kernel SHA256 required')
    payload = [common_key(commitments), task, list(pair), [str(exact(x)) for x in offsets],
               allowed_set_sha256, str(exact(precision)), kernel_sha256]
    return hashlib.sha256(json.dumps(payload, separators=(',', ':')).encode()).hexdigest()


def cost_coverage(costs, process, coverage):
    """coverage maps each component to existing diagnostic segment names.

    A component absent by design may use {'not_used': 'concrete reason'}.
    This is a completeness audit, not proof that declarations are truthful.
    Future scientific evidence still needs raw receipts and independent review.
    """
    if set(coverage)-set(COMPONENTS):
        raise ValueError('unknown construction-cost component')
    missing = []
    segments = {}
    if costs is None:
        missing.append('INNER_COST_ENVELOPE')
    else:
        if costs.get('aggregation') != 'OUTER_ENVELOPE_ONLY_DO_NOT_SUM_NESTED':
            raise ValueError('nested segments must not be added to total cost')
        for k in ('wall_ns', 'cpu_ns'):
            if type(costs.get(k)) is not int or costs[k] < 0:
                raise ValueError('nonnegative measured cost required')
        for row in costs['segments']:
            if (not isinstance(row.get('name'), str) or not row['name']
                    or type(row.get('depth')) is not int or row['depth'] < 0
                    or any(type(row.get(k)) is not int or not 0 <= row[k] <= costs[k]
                           for k in ('wall_ns', 'cpu_ns'))):
                raise ValueError('invalid diagnostic segment')
            segments.setdefault(row['name'], []).append(row)
    for name in COMPONENTS:
        declaration = coverage.get(name)
        if (isinstance(declaration, dict) and set(declaration) == {'not_used'}
                and isinstance(declaration['not_used'], str) and declaration['not_used'].strip()):
            if name in MANDATORY:
                missing.append(name)
            continue
        if (not isinstance(declaration, list) or not declaration
                or any(not isinstance(s, str) or s not in segments for s in declaration)):
            missing.append(name)
    total = None
    if process is None:
        missing.append('SPAWN_TO_EXIT_PROCESS_ENVELOPE')
    else:
        if process.get('cost_scope') != PROCESS_SCOPE:
            raise ValueError('process cost omits imports or final I/O')
        keys = ('total_process_wall_ns', 'total_process_cpu_ns')
        if any(type(process.get(k)) is not int or process[k] < 0 for k in keys):
            raise ValueError('nonnegative outer process measurements required')
        if type(process.get('process_success')) is not bool or type(process.get('failure_retained')) is not bool:
            raise ValueError('process outcome and retained failure required')
        if not process['process_success'] and not process['failure_retained']:
            raise ValueError('failed process omitted from ledger')
        # Wall is comparable across these envelopes; process CPU may use a
        # different OS clock/rounding, so do not demand bitwise CPU containment.
        if costs is not None and costs['wall_ns'] > process['total_process_wall_ns']:
            raise ValueError('inner wall envelope outside process lifetime')
        total = {k: process[k] for k in keys}
    return {'status': 'COMPLETE_DECLARED_COVERAGE' if not missing else 'INCOMPLETE_COST_EVIDENCE',
            'missing': missing, 'process_totals': total,
            'aggregation': 'PROCESS_ENVELOPE_ONLY_NO_NESTED_SUM',
            'measurement_authentication': 'NOT_PERFORMED', 'runtime_speedup_claim_allowed': False}


def paired_cost_readiness(left, right):
    """Return all deficiencies and failures; never silently filter one arm."""
    if left['arm'] == right['arm'] or left['task'] != right['task']:
        raise ValueError('distinct arms of the same task required')
    if common_key(left['common']) != common_key(right['common']):
        raise ValueError('geometry/fast path/feedback/cache/fallback comparison mismatch')
    audits = {r['arm']: cost_coverage(r.get('costs'), r.get('process'), r.get('coverage', {}))
              for r in (left, right)}
    complete = all(a['status'] == 'COMPLETE_DECLARED_COVERAGE' for a in audits.values())
    success = all(r.get('process') is not None and r['process']['process_success'] for r in (left, right))
    return {'task': left['task'], 'arms': audits, 'both_success': success,
            'all_arm_outcomes_retained': True,
            'ready_for_outcome_and_cost_review': complete and success,
            'runtime_speedup_claim_allowed': False,
            'outcome_precision_and_safety': 'REQUIRE_SEPARATE_CERTIFICATE_REVIEW'}
