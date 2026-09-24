"""Exact controls separating estimation from decision logic; no learned data.

Each case holds the true outcome distribution fixed across its four cells.
The estimators here are stipulated, not fitted. Exact probabilities paired
with a heuristic do not form a performance upper bound. Query, inference and
maintenance costs have NOT been mapped to the original execution system.
"""

from dataclasses import replace
from fractions import Fraction as F
import json

from .decision_structure import GraphCase, complementarity_case, solve


def compare(case, coarse):
    """Return the same-world 2x2 comparison with exact expected rewards."""
    truth = dict(case.probabilities)
    cells = []
    for estimator, estimates in (("stipulated_coarse", coarse),
                                 ("exact_probability", truth)):
        for policy, lookahead in (("soft_lexicographic", False),
                                  ("adaptive_lookahead", True)):
            value, first = solve(case, lookahead=lookahead, estimates=estimates)
            mse = sum((estimates[key] - p) ** 2 for key, p in truth.items())
            cells.append({
                "estimator": estimator,
                "policy": policy,
                "mean_squared_probability_error": str(mse / len(truth)),
                "expected_admitted_demands": str(value),
                "first_query": first,
            })
    return {
        "true_probabilities": {key: str(p) for key, p in truth.items()},
        "coarse_estimates": {key: str(p) for key, p in coarse.items()},
        "demands": [sorted(owners) for owners in case.demands],
        "query_budget": case.query_budget,
        "cells": cells,
    }


def report():
    single = GraphCase((("A", F(4, 5)), ("B", F(1, 5))),
                       (frozenset({"A"}), frozenset({"B"})), 1)
    complementary = complementarity_case()
    return {
        "status": "exact_synthetic_factorial_diagnostic",
        "learned_model_evaluated": False,
        "probability_error_is_against_stipulated_truth_not_observed_labels": True,
        "assumptions": [
            "independent Bernoulli outcomes, valid responses, each owner queried at most once",
            "equal query cost and delay, no exogenous graph changes",
            "reward is demand admission, not robot task completion",
        ],
        "cases": {
            "prediction_order": compare(single, {"A": F(1, 5), "B": F(4, 5)}),
            "decision_complementarity": compare(
                complementary, {"A": F(1), "B": F(1), "C": F(1, 2)}),
            "accuracy_can_hurt_soft_lex": compare(
                complementary, {"A": F(1), "B": F(1), "C": F(0)}),
            "enough_budget": compare(
                replace(complementary, query_budget=3),
                {"A": F(1), "B": F(1), "C": F(0)}),
        },
        "resource_overhead": "unmeasured; no B1 cost mapping or net-benefit claim",
        "real_data_or_throughput_evidence": False,
    }


def main():
    print(json.dumps(report(), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
