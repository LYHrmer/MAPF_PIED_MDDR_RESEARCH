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
