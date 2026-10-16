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
