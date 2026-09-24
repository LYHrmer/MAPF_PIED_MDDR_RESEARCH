"""Check analytic finite-graph results, not simulated robot performance."""

from dataclasses import replace
from fractions import Fraction as F
import unittest

from .decision_structure import GraphCase, complementarity_case, solve


class DecisionStructureTests(unittest.TestCase):
    def test_tiny_positive_immediate_reward_defeats_large_complementary_reward(self):
        case = complementarity_case()
        self.assertEqual(solve(case, lookahead=False), (F(1, 1000), "C"))
        self.assertEqual(solve(case, lookahead=True), (F(2), "A"))

    def test_adaptive_second_query_accounts_for_failed_first_chain_query(self):
        case = complementarity_case(chain_probability=F(4, 5))
        # On first success, query B; on first failure, query C.
        expected = F(4, 5) * F(4, 5) * 2 + F(1, 5) * F(1, 1000)
        self.assertEqual(solve(case, lookahead=True), (expected, "A"))
        self.assertEqual(solve(case, lookahead=False)[0], F(1, 1000))

    def test_one_step_single_owner_problem_has_no_artificial_lookahead_gain(self):
        case = GraphCase((("A", F(1, 5)), ("B", F(4, 5))),
                         (frozenset({"A"}), frozenset({"B"})), 1)
        self.assertEqual(solve(case, lookahead=False), (F(4, 5), "B"))
        self.assertEqual(solve(case, lookahead=True), (F(4, 5), "B"))

    def test_varying_true_probability_preserves_structural_order(self):
        for p in (F(1, 1000), F(1, 2), F(1)):
            with self.subTest(probability=p):
                case = complementarity_case(rare_probability=p)
                self.assertEqual(solve(case, lookahead=False), (p, "C"))
                self.assertEqual(solve(case, lookahead=True), (F(2), "A"))

    def test_budget_for_all_queries_removes_the_complementarity_gap(self):
        case = replace(complementarity_case(), query_budget=3)
        expected = F(2) + F(1, 1000)
        self.assertEqual(solve(case, lookahead=False)[0], expected)
        self.assertEqual(solve(case, lookahead=True)[0], expected)

    def test_prediction_order_is_evaluated_under_the_same_true_distribution(self):
        case = GraphCase((("A", F(4, 5)), ("B", F(1, 5))),
                         (frozenset({"A"}), frozenset({"B"})), 1)
        for lookahead in (False, True):
            with self.subTest(lookahead=lookahead):
                self.assertEqual(solve(case, lookahead=lookahead,
                                       estimates={"A": F(1, 5), "B": F(4, 5)}),
                                 (F(1, 5), "B"))
                self.assertEqual(solve(case, lookahead=lookahead), (F(4, 5), "A"))

    def test_accurate_probabilities_are_not_an_upper_bound_for_soft_lex(self):
        case = complementarity_case()
        estimates = {"A": F(1), "B": F(1), "C": F(0)}
        self.assertEqual(solve(case, lookahead=False, estimates=estimates), (F(2), "A"))
        self.assertEqual(solve(case, lookahead=False), (F(1, 1000), "C"))
        self.assertEqual(solve(case, lookahead=True, estimates=estimates), (F(2), "A"))
        self.assertEqual(solve(case, lookahead=True), (F(2), "A"))

    def test_evaluation_does_not_reoptimize_the_second_query_using_truth(self):
        demands = (frozenset({"A"}), frozenset({"A"}),
                   frozenset({"B"}), frozenset({"C"}))
        estimates = {"A": F(1), "B": F(3, 4), "C": F(1, 4)}
        for lookahead in (False, True):
            for b, c, expected in ((1, 0, 3), (0, 1, 2)):
                with self.subTest(lookahead=lookahead, b=b):
                    case = GraphCase((("A", F(1)), ("B", F(b)), ("C", F(c))),
                                     demands, 2)
                    self.assertEqual(solve(case, lookahead=lookahead,
                                           estimates=estimates), (F(expected), "A"))

    def test_policy_remains_defined_after_an_estimated_impossible_failure(self):
        case = GraphCase((("A", F(0)), ("B", F(1)), ("C", F(0))),
                         (frozenset({"A"}), frozenset({"A"}),
                          frozenset({"B"}), frozenset({"C"})), 2)
        estimates = {"A": F(1), "B": F(3, 4), "C": F(1, 4)}
        for lookahead in (False, True):
            with self.subTest(lookahead=lookahead):
                self.assertEqual(solve(case, lookahead=lookahead, estimates=estimates),
                                 (F(1), "A"))

    def test_policy_remains_defined_after_an_estimated_impossible_success(self):
        case = GraphCase((("A", F(1)), ("B", F(1))),
                         (frozenset({"A", "B"}),), 2)
        self.assertEqual(solve(case, lookahead=True,
                               estimates={"A": F(0), "B": F(1)}), (F(1), "A"))

    def test_estimates_require_exact_owner_coverage_and_valid_probabilities(self):
        case = complementarity_case()
        for estimates in ({"A": F(1)}, {"A": F(1), "B": F(1), "C": F(0), "D": F(1)},
                          {"A": F(1), "B": F(1), "C": 0.1},
                          {"A": F(1), "B": F(1), "C": F(-1)},
                          {"A": F(1), "B": F(1), "C": F(2)}, (F(1), F(1), F(0))):
            with self.subTest(estimates=estimates), self.assertRaises(ValueError):
                solve(case, lookahead=True, estimates=estimates)


if __name__ == "__main__":
    unittest.main()
