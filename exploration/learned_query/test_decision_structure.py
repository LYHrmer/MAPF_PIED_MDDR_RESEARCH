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


if __name__ == "__main__":
    unittest.main()
