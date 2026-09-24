"""Exact diagnostic of query complementarity on a tiny, frozen dependency graph.

All responses are valid; 'success' means crossing every threshold associated
with that owner. Each owner is queried at most once. Independent Bernoulli
outcomes, equal positive costs/delays, no exogenous graph changes or releases,
and a query-count budget are assumptions of THIS synthetic example only.
The reward counts admitted demands, not completed robot tasks or throughput.
Neither policy is a bound or a reproduction of the real execution system.
"""

from dataclasses import dataclass
from collections.abc import Mapping
from fractions import Fraction as F
from functools import lru_cache
import json


@dataclass(frozen=True)
class GraphCase:
    probabilities: tuple[tuple[str, F], ...]
    demands: tuple[frozenset[str], ...]
    query_budget: int

    def __post_init__(self):
        keys = [key for key, _ in self.probabilities]
        if len(keys) != len(set(keys)) or any(not key for key in keys):
            raise ValueError("query keys must be nonempty and unique")
        if any(type(p) is not F or not 0 <= p <= 1 for _, p in self.probabilities):
            raise ValueError("probabilities must be Fractions in [0, 1]")
        if any(not owners or not owners <= set(keys) for owners in self.demands):
            raise ValueError("each demand needs a nonempty set of known owners")
        if type(self.query_budget) is not int or self.query_budget < 0:
            raise ValueError("query budget must be a nonnegative integer")


def solve(case, *, lookahead, estimates=None):
    """Return (exact expected final admissions, first query).

    lookahead=False evaluates adaptive soft lexicographic A/P selection.
    lookahead=True optimizes using the supplied probability estimates.
    Only evaluation uses case.probabilities (the outcome distribution).
    estimates=None explicitly selects exact probabilities for diagnosis;
    this default is not an interface to observations in the real system.
    Successful evidence removes satisfied relations. All-zero scores select
    by name here; production round-robin fallback is not reproduced.
    """
    truth = dict(case.probabilities)
    if estimates is None:
        probabilities = dict(truth)
    else:
        if not isinstance(estimates, Mapping):
            raise ValueError("estimates must be a mapping")
        probabilities = dict(estimates)
        if probabilities.keys() != truth.keys():
            raise ValueError("estimates must cover exactly the case's owners")
        if any(type(p) is not F or not 0 <= p <= 1
               for p in probabilities.values()):
            raise ValueError("estimates must be Fractions in [0, 1]")

    def reward(cleared):
        return F(sum(owners <= cleared for owners in case.demands))

    def lex_score(owner, cleared):
        immediate, partial = F(0), F(0)
        for owners in case.demands:
            remaining = owners - cleared
            if owner not in remaining:
                continue
            p = probabilities[owner]
            if len(remaining) == 1:
                immediate += p
            partial += p / len(remaining)
        # Equal work and delay give every query the same positive denominator.
        return immediate, partial

    @lru_cache(maxsize=None)
    def plan(available, cleared, budget):
        if budget == 0 or not available:
            return reward(cleared), None

        def outcome(owner):
            rest = tuple(key for key in available if key != owner)
            p = probabilities[owner]
            # Define the continuation on BOTH observations, including those
            # assigned zero estimated probability. They can occur in truth.
            success = plan(rest, cleared | {owner}, budget - 1)[0]
            failure = plan(rest, cleared, budget - 1)[0]
            return p * success + (1 - p) * failure

        if not lookahead:
            owner = min(available, key=lambda key: (
                -lex_score(key, cleared)[0], -lex_score(key, cleared)[1], key))
            return outcome(owner), owner
        values = [(outcome(owner), owner) for owner in available]
        return min(values, key=lambda item: (-item[0], item[1]))

    @lru_cache(maxsize=None)
    def evaluate(available, cleared, budget):
        if budget == 0 or not available:
            return reward(cleared)
        # No maximization here: follow the estimated policy at every step.
        owner = plan(available, cleared, budget)[1]
        rest = tuple(key for key in available if key != owner)
        p = truth[owner]
        return (p * evaluate(rest, cleared | {owner}, budget - 1)
                + (1 - p) * evaluate(rest, cleared, budget - 1))

    initial = tuple(sorted(probabilities)), frozenset(), case.query_budget
    return evaluate(*initial), plan(*initial)[1]


def complementarity_case(rare_probability=F(1, 1000), chain_probability=F(1)):
    return GraphCase(
        (("A", chain_probability), ("B", chain_probability),
         ("C", rare_probability)),
        (frozenset({"A", "B"}), frozenset({"A", "B"}), frozenset({"C"})),
        query_budget=2,
    )


def main():
    case = complementarity_case()
    greedy_value, greedy_first = solve(case, lookahead=False)
    lookahead_value, lookahead_first = solve(case, lookahead=True)
    print(json.dumps({
        "status": "exact_synthetic_graph_diagnostic",
        "assumptions": [
            "all responses valid; success means sufficient release evidence",
            "each owner queried at most once; independent outcomes",
            "equal work and delay; at most two queries",
            "no exogenous graph changes, automatic releases or additional conflicts",
        ],
        "soft_lexicographic": {
            "first_query": greedy_first, "expected_admitted_demands": str(greedy_value),
        },
        "adaptive_lookahead": {
            "first_query": lookahead_first, "expected_admitted_demands": str(lookahead_value),
        },
        "claim": "accurate probabilities alone cannot repair the lexicographic objective",
        "physical_realizability_in_original_system": "not_demonstrated",
        "robot_throughput_or_real_system_bound": False,
    }, indent=2))


if __name__ == "__main__":
    main()
