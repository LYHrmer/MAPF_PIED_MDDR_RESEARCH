"""Pure software contracts with scripted callbacks; no MAPF solver or instance."""

import unittest

from pp_repair import (Incumbent, Policy, RepairStatus, SearchReply, SearchStatus,
                       SharedBudget, repair)


class Clock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


class RepairContracts(unittest.TestCase):
    def setUp(self):
        # Opaque software values, not a map/trajectory/safety experiment.
        self.original = {0: (0, 0, 0, 1, 2), 1: (3, 3, 4, 5), 2: (8, 9)}
        self.store = Incumbent(self.original)
        self.clock = Clock()
        self.budget = SharedBudget(100, 10, self.clock, self.clock)
        self.cache = {}
        self.paths = {0: (0, 1, 2), 1: (3, 4, 5)}

    def run_repair(self, search=None, validate=None, **kwargs):
        return repair(self.store, kwargs.pop("order", (0, 1)),
                      kwargs.pop("lower_bounds", {0: 2, 1: 2}),
                      model_key="software-fixture-v1", budget=self.budget,
                      shared_cache=self.cache,
                      search=search or (lambda req: SearchReply(SearchStatus.FOUND, self.paths[req.agent])),
                      validate=validate or (lambda req: True), **kwargs)

    def test_complete_only_commit_and_residual_caps(self):
        before, requests = self.store.snapshot(), []

        def search(req):
            requests.append(req)
            self.assertIs(self.store.snapshot(), before)
            self.assertIs(req.shared_cache, self.cache)
            self.assertEqual(set(req.fixed_paths), {2})
            with self.assertRaises(TypeError):
                req.fixed_paths[2] = (8, 8, 9)
            self.clock.now += 2
            return SearchReply(SearchStatus.FOUND, self.paths[req.agent])

        def validate(req):
            self.assertIs(self.store.snapshot(), before)
            self.assertEqual(set(req.paths), {0, 1, 2})
            self.assertEqual(req.paths[2], before.paths[2])
            self.assertIs(req.shared_cache, self.cache)
            self.clock.now += 3
            return True

        result = self.run_repair(search, validate)
        self.assertEqual(result.status, RepairStatus.ACCEPTED)
        self.assertEqual([req.max_cost for req in requests], [4, 4])
        self.assertEqual(dict(requests[0].prefix_paths), {})
        self.assertEqual(dict(requests[1].prefix_paths), {0: self.paths[0]})
        self.assertNotEqual(requests[0].constraint_key, requests[1].constraint_key)
        self.assertEqual((result.old_cost, result.candidate_cost), (7, 4))
        self.assertEqual(result.after.version, 1)
        self.assertIs(result.improvement_label, True)
        self.assertEqual(self.budget.stage_wall_ns["search"], 4)
        self.assertEqual(self.budget.stage_wall_ns["validate"], 3)
        self.assertEqual(result.wall_ns, 7)

    def test_lower_bound_closes_strict_improvement_before_search(self):
        result = self.run_repair(lower_bounds={0: 4, 1: 3})
        self.assertEqual(result.status, RepairStatus.NO_IMPROVEMENT)
        self.assertEqual(result.search_calls, 0)
        self.assertIs(result.after, result.before)
        self.assertIs(result.improvement_label, False)
        self.assertIn("FIXED_PREFIX", result.scope)

    def test_cap_exhaustion_is_not_unrestricted_infeasibility(self):
        result = self.run_repair(lambda req: SearchReply(SearchStatus.EXHAUSTED_WITHIN_CAP))
        self.assertEqual(result.status, RepairStatus.NO_IMPROVEMENT)
        self.assertIn("cap", result.reason)
        self.assertIs(result.after, result.before)

    def test_capped_backend_cannot_claim_unrestricted_infeasibility(self):
        result = self.run_repair(lambda req: SearchReply(SearchStatus.INFEASIBLE))
        self.assertEqual(result.status, RepairStatus.FAILED)
        self.assertIsNone(result.improvement_label)

    def test_original_prefix_control_and_residual_cap_differ(self):
        # Same scripted repair oracle, differing only in its provided cap.
        def search(req):
            path = self.original[req.agent]
            if req.max_cost is not None and len(path) - 1 > req.max_cost:
                return SearchReply(SearchStatus.EXHAUSTED_WITHIN_CAP)
            return SearchReply(SearchStatus.FOUND, path)

        bounded = self.run_repair(search, lower_bounds={0: 2, 1: 3})
        original = self.run_repair(search, lower_bounds={0: 2, 1: 3}, policy=Policy.ORIGINAL_PREFIX)
        self.assertEqual(bounded.status, RepairStatus.NO_IMPROVEMENT)
        self.assertEqual(original.status, RepairStatus.NO_IMPROVEMENT)
        self.assertEqual((bounded.search_calls, original.search_calls), (1, 2))
        self.assertEqual(original.candidate_cost, 7)
        self.assertIs(self.store.snapshot(), bounded.before)

    def test_partial_failure_never_gets_positive_or_negative_training_label(self):
        def search(req):
            if req.agent == 0:
                return SearchReply(SearchStatus.FOUND, self.paths[0])
            return SearchReply(SearchStatus.FAILED, reason="incomplete backend result")

        result = self.run_repair(search)
        self.assertEqual(result.status, RepairStatus.FAILED)
        self.assertEqual(result.completed_agents, 1)
        self.assertIsNone(result.improvement_label)
        self.assertIs(result.after, result.before)

    def test_late_callback_cannot_commit(self):
        def search(req):
            self.clock.now = 100
            return SearchReply(SearchStatus.FOUND, self.paths[req.agent])

        result = self.run_repair(search)
        self.assertEqual(result.status, RepairStatus.TIMEOUT)
        self.assertIs(result.after, result.before)
        self.assertIsNone(result.improvement_label)
        self.assertEqual(self.budget.stage_wall_ns["search"], 100)

    def test_late_validation_cannot_commit(self):
        def validate(req):
            self.clock.now = 100
            return True

        result = self.run_repair(validate=validate)
        self.assertEqual(result.status, RepairStatus.TIMEOUT)
        self.assertIs(result.after, result.before)

    def test_exception_is_charged_and_preserves_incumbent(self):
        def search(req):
            self.clock.now += 8
            raise RuntimeError("scripted failure")

        result = self.run_repair(search)
        self.assertEqual(result.status, RepairStatus.FAILED)
        self.assertEqual(self.budget.stage_wall_ns["search"], 8)
        self.assertIs(result.after, result.before)

    def test_shared_call_budget_is_not_reset_by_a_failed_attempt(self):
        self.budget.max_search_calls = 1
        first = self.run_repair(lambda req: SearchReply(SearchStatus.FAILED))
        second = self.run_repair()
        self.assertEqual(first.search_calls, 1)
        self.assertEqual(second.status, RepairStatus.TIMEOUT)
        self.assertEqual(second.search_calls, 0)
        self.assertEqual(self.budget.search_calls, 1)

    def test_invalid_goal_or_over_cap_or_common_validator_cannot_commit(self):
        for path in ((0, 1, 99), (0, 0, 0, 0, 1, 2)):
            result = self.run_repair(lambda req: SearchReply(SearchStatus.FOUND, path))
            self.assertEqual(result.status, RepairStatus.FAILED)
            self.assertIs(result.after, result.before)
        result = self.run_repair(validate=lambda req: 1)
        self.assertEqual(result.status, RepairStatus.FAILED)
        self.assertIs(result.after, result.before)

    def test_bad_bounds_or_duplicate_order_cannot_run_search(self):
        for options in ({"lower_bounds": {0: True, 1: 2}},
                        {"lower_bounds": {0: 5, 1: 2}}, {"order": (0, 0)}):
            result = self.run_repair(**options)
            self.assertEqual(result.status, RepairStatus.FAILED)
            self.assertEqual(result.search_calls, 0)

    def test_concurrent_incumbent_replacement_is_not_overwritten(self):
        def validate(req):
            self.store._commit(self.store.snapshot(), self.original, self.budget)
            return True

        result = self.run_repair(validate=validate)
        self.assertEqual(result.status, RepairStatus.STALE)
        self.assertEqual(result.after.version, 1)
        self.assertEqual(dict(result.after.paths), self.original)
        self.assertIsNone(result.improvement_label)


if __name__ == "__main__":
    unittest.main()
