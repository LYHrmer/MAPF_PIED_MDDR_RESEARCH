"""Cross-robot causality and paired evidence, separate from frozen T1 wire API."""
from fractions import Fraction as Q
from protocol import exact


class CausalClock:
    """One event frontier for the entire session, not one clock per robot."""
    def __init__(self):
        self.frontier = Q(0)

    def validate(self, now, *, deliveries=()):
        now = exact(now)
        if now < self.frontier or any(exact(d) > now for d in deliveries):
            raise ValueError('RETROSPECTIVE_EVENT_OR_UNDELIVERED_INFORMATION')
        return now

    def commit(self, now):
        self.frontier = self.validate(now)


def construction_comparison(reference, candidate):
    """Operation-count evidence only; cannot manufacture elapsed-cost evidence."""
    if reference['commitment'] != candidate['commitment']:
        raise ValueError('different motion/geometry/feedback inputs are not a paired comparison')
    if reference['constraints'] != candidate['constraints']:
        raise ValueError('changed allowed windows; not an equivalent construction comparison')
    a, b = reference['phase_cells'], candidate['phase_cells']
    if any(type(x) is not int or x < 0 for x in (a, b)):
        raise ValueError('nonnegative measured operation counts required')
    return {'same_constraints': True, 'reference_phase_cells': a, 'candidate_phase_cells': b,
            'saved_phase_cells': a-b, 'fraction_saved': str(Q(a-b, a)) if a else None,
            'total_process_wall_cpu': None, 'runtime_speedup_claim_allowed': False,
            'comparison_identity': 'local_exhaustive_vs_endpoint_implementation_not_external_method_performance'}


def fixed_session_comparison(left, right):
    """Fairness and behavior audit for fixed public-message fixtures only."""
    if left['arm'] == right['arm'] or any(left[k] != right[k] for k in ('task', 'commitment', 'constraint_signature')):
        raise ValueError('pair requires distinct arms with identical qualified task and constraints')
    if left['public_wire_sha256'] != right['public_wire_sha256']:
        raise ValueError('different public information; not a same-information pair')
    starts = lambda r: {x['robot']: x['start'] for x in r['commands']}
    return {'both_success': left['success'] is True and right['success'] is True,
            'same_launches': starts(left) == starts(right),
            'same_completion': left['completion'] == right['completion'],
            'same_core_work': left['operations'] == right['operations'],
            'same_public_information': True,
            'new_relative_guarantee': False,
            'total_process_cost_status': 'UNKNOWN_NOT_MEASURED',
            'scope': 'STATIC_FIXED_MESSAGES_NOT_INDEPENDENT_TASK_RESULTS'}


def task_ledger(planned, receipts, *, horizon):
    """Retain every planned task/arm, including absent and failed results.

    This successor's declared failure penalty is (n+1)*H, greater than the
    maximum successful sum n*H. It does not rewrite frozen T1 metrics.
    """
    horizon = exact(horizon)
    if horizon <= 0 or not planned:
        raise ValueError('nonempty predeclared tasks and positive horizon required')
    keys = [(p['task'], p['arm']) for p in planned]
    if len(set(keys)) != len(keys):
        raise ValueError('duplicate planned task/arm')
    indexed = {}
    for r in receipts:
        key = (r['task'], r['arm'])
        if key not in keys or key in indexed:
            raise ValueError('foreign or duplicate result; do not silently average/drop it')
        indexed[key] = r
    rows = []
    for p, key in zip(planned, keys):
        robots = tuple(p['robots'])
        if not robots or len(set(robots)) != len(robots):
            raise ValueError('complete unique robot list required')
        r = indexed.get(key)
        completion = dict.fromkeys(robots) if r is None else r['completion']
        if set(completion) != set(robots):
            raise ValueError('robot outcome omitted from receipt')
        times = [None if completion[k] is None else exact(completion[k]) for k in robots]
        if any(t is not None and not 0 <= t <= horizon for t in times):
            raise ValueError('completion outside fixed horizon')
        success = r is not None and r['success'] is True
        if success and (r['status'] != 'SUCCESS' or any(t is None for t in times)):
            raise ValueError('contradictory success record')
        censored = sum(horizon if t is None else t for t in times)
        rows.append({'task': key[0], 'arm': key[1], 'status': 'NOT_REPORTED' if r is None else r['status'],
                     'success': success, 'failure_retained': not success, 'completion': completion,
                     'censored_sum_completion': str(censored),
                     'penalized_sum_completion': str(censored if success else (len(robots)+1)*horizon),
                     'penalty_is_not_measured_completion': not success})
    return {'rows': rows, 'planned_count': len(rows), 'success_count': sum(r['success'] for r in rows),
            'failure_or_missing_count': sum(not r['success'] for r in rows),
            'failed_rows_excluded': 0, 'horizon': str(horizon)}
