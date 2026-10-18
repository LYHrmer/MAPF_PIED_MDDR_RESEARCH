"""Software contracts and declared path fixtures; no solver search or benchmark."""

from dataclasses import replace
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from pp_repair import (Incumbent, Policy, RepairStatus, SearchReply, SearchStatus,
                       SearchRequest, SharedBudget, repair)
from address_backend import GridProblem, NativeBackend, PathValidationCache, MAX_TIMESTEP
from run_repair_dev import supervise, worker, write_json


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


class BackendContracts(unittest.TestCase):
    """All native replies are scripted. NativeBackend.__init__ is never called."""

    def setUp(self):
        self.problem = GridProblem(2, 3, [], {5: (0, 2), 9: (3, 5)})
        self.paths = {5: (0, 0, 1, 2), 9: (3, 3, 4, 5)}
        self.backend = NativeBackend.__new__(NativeBackend)
        self.backend.problem = self.problem
        self.backend.budget = SharedBudget(time.monotonic_ns() + 10**9, 10)
        self.backend.cache = {}
        self.backend.seed = 12
        self.backend.cost_wall_ns, self.backend.cost_python_cpu_ns = {}, {}
        self.backend.validation = PathValidationCache(self.problem)
        self.backend.validation.validate_complete(self.paths)
        self.backend.close = Mock()
        self.backend._rpc = Mock(return_value={'status': 'FOUND', 'path': [0, 1, 2],
            'num_collisions': 0, 'effective_max_cost': 2})
        self.request = SearchRequest(5, 0, 2, 2, {9: self.paths[9]}, {}, (5,),
            self.problem.model_key, 'scripted-key', self.backend.budget, self.backend.cache)

    def test_common_validator_checks_waits_endpoints_and_all_robots(self):
        self.assertIs(self.problem.validate(self.paths), True)
        for paths in ({5: self.paths[5]}, {5: (0, 1), 9: self.paths[9]},
                      {5: (False, 1, 2), 9: self.paths[9]}):
            with self.assertRaises(ValueError):
                self.problem.validate(paths)

    def test_common_validator_rejects_vertex_swap_and_later_goal_entry(self):
        examples = [
            (GridProblem(1, 3, [], {0: (0, 2), 1: (2, 0)}), {0: (0, 1, 2), 1: (2, 1, 0)}),
            (GridProblem(1, 2, [], {0: (0, 1), 1: (1, 0)}), {0: (0, 1), 1: (1, 0)}),
            (GridProblem(2, 3, [], {0: (0, 1), 1: (3, 2)}), {0: (0, 1), 1: (3, 4, 1, 2)})]
        for problem, paths in examples:
            with self.assertRaises(ValueError):
                problem.validate(paths)

    def test_grid_motion_excludes_obstacle_row_wrap_and_diagonal(self):
        problem = GridProblem(2, 3, [1], {0: (0, 5)})
        self.assertTrue(problem.validate({0: (0, 3, 4, 5)}))
        for path in ((0, 1, 2, 5), (0, 3, 2, 5), (0, 4, 5)):
            with self.assertRaises(ValueError):
                problem.validate({0: path})

    def test_author_serialization_pins_sparse_robot_mapping(self):
        grid, agents = self.problem.author_files()
        self.assertEqual(grid, b'2,3\n...\n...\n')
        self.assertEqual(agents, b'2\n0,0,0,2\n1,0,1,2\n')
        self.assertEqual(self.problem.native_ids, {5: 0, 9: 1})
        same = GridProblem(2, 3, [], {9: (3, 5), 5: (0, 2)})
        self.assertEqual(same.model_key, self.problem.model_key)

    def test_both_cap_policies_share_native_prefix_seed_and_geometry(self):
        self.assertEqual(self.backend.search(self.request).status, SearchStatus.FOUND)
        first = self.backend._rpc.call_args.args[0]
        self.backend._rpc.return_value['effective_max_cost'] = MAX_TIMESTEP
        self.backend.search(replace(self.request, max_cost=None))
        second = self.backend._rpc.call_args.args[0]
        self.assertEqual({k: v for k, v in first.items() if k != 'max_cost'},
                         {k: v for k, v in second.items() if k != 'max_cost'})

    def test_callback_costs_are_nested_observations_and_failures_are_retained(self):
        self.backend.search(self.request)
        report = self.backend.accounting()
        parts = report['parents']['search_total']
        self.assertGreater(report['wall_ns']['search_total'], 0)
        self.assertGreaterEqual(report['wall_ns']['search_total'],
                                sum(report['wall_ns'].get(name, 0) for name in parts))
        # The mocked RPC has no native/IPC time to report.
        self.assertNotIn('rpc_search_total', report['wall_ns'])
        self.assertEqual(self.backend.budget.stage_wall_ns, {})
        before = report['wall_ns']['search_total']
        with self.assertRaises(ValueError):
            self.backend.search(replace(self.request, model_key='changed'))
        self.assertGreater(report['wall_ns']['search_total'], before)

    def test_backend_rejects_missing_prefix_and_changed_shared_identity(self):
        for request in (replace(self.request, fixed_paths={}),
                        replace(self.request, order=(9, 5)),
                        replace(self.request, model_key='other'),
                        replace(self.request, shared_cache={})):
            with self.assertRaises(ValueError):
                self.backend.search(request)
        self.backend._rpc.assert_not_called()

    def test_author_found_still_requires_geometry_and_cap_checks(self):
        for answer in ({'path': [0, 4, 2]}, {'effective_max_cost': 3},
                       {'path': [0, 0, 1, 2]}, {'num_collisions': 1}):
            self.backend._rpc.return_value = dict(status='FOUND', path=[0, 1, 2],
                num_collisions=0, effective_max_cost=2)
            self.backend._rpc.return_value.update(answer)
            with self.assertRaises(ValueError):
                self.backend.search(self.request)

    def test_empty_native_result_is_censored_and_keeps_incumbent(self):
        # Missing terminal fields cannot certify exhaustion.
        self.backend._rpc.return_value = {'status': 'EMPTY_CAPPED'}
        store = Incumbent(self.paths)
        result = repair(store, (5,), {5: 2}, model_key=self.problem.model_key,
            search=self.backend.search, validate=self.backend.validate,
            budget=self.backend.budget, shared_cache=self.backend.cache)
        self.assertEqual(result.status, RepairStatus.FAILED)
        self.assertIsNone(result.improvement_label)
        self.assertIs(result.before, result.after)

    def test_completed_cap_exhaustion_is_scoped_to_that_request(self):
        self.backend._rpc.return_value = {'status': 'EMPTY_CAPPED', 'path': [], 'effective_max_cost': 2}
        reply = self.backend.search(self.request)
        self.assertEqual(reply.status, SearchStatus.EXHAUSTED_WITHIN_CAP)
        self.backend._rpc.return_value = {'status': 'EMPTY_BASE_LIMIT', 'path': [],
                                         'effective_max_cost': MAX_TIMESTEP}
        reply = self.backend.search(replace(self.request, max_cost=None))
        self.assertEqual(reply.status, SearchStatus.FAILED)

    def test_native_failure_ends_session_without_retry(self):
        self.backend._rpc.return_value = {'status': 'FAILED', 'reason': 'scripted exception'}
        self.assertEqual(self.backend.search(self.request).status, SearchStatus.FAILED)
        self.backend.close.assert_called_once()
        self.backend._rpc.assert_called_once()

    def test_rpc_timeout_is_retained_and_closes_child(self):
        self.backend.proc = Mock()
        self.backend.proc.stdin.fileno.return_value = 100
        self.backend.proc.stdout.fileno.return_value = 101
        self.backend.seq, self.backend.records, self.backend.buffer = 0, [], bytearray()
        with patch('address_backend.select.select', return_value=([], [], [])):
            with self.assertRaises(TimeoutError):
                NativeBackend._rpc(self.backend, {'op': 'search'})
        self.assertEqual(self.backend.records[0]['status'], 'TIMEOUT')
        self.assertGreater(self.backend.records[0]['wall_ns'], 0)
        self.backend.close.assert_called_once()


class ValidationProofContracts(unittest.TestCase):
    """Geometry fixtures only: no solver, benchmark or measured speedup."""
    def setUp(self):
        self.problem = GridProblem(3, 4, [], {0: (0, 3), 1: (4, 7), 2: (8, 11)})
        self.paths = {0: (0, 1, 2, 3), 1: (4, 5, 6, 7), 2: (8, 9, 10, 11)}
        self.cache = PathValidationCache(self.problem)
        self.cache.validate_complete(self.paths)

    def test_unchanged_subset_and_progressive_prefix_reuse_without_rechecking(self):
        with patch.object(self.problem, 'validate_extension', wraps=self.problem.validate_extension) as extension:
            self.cache.validate_subset({2: self.paths[2]})
            prefix = {2: self.paths[2], 0: (0, 0, 1, 2, 3)}
            self.cache.validate_subset(prefix)
            self.cache.validate_subset(prefix)
            self.assertEqual(extension.call_count, 1)
        self.assertEqual(self.cache.counts['paths_checked'], 1)
        self.assertEqual(self.cache.counts['pair_checks'], 1)

    def test_mutable_caller_path_and_mapping_cannot_change_a_certificate(self):
        incoming = {a: list(p) for a, p in self.paths.items()}
        self.cache.validate_complete(incoming)
        incoming[0][1] = 5  # Mutates caller data, not the frozen certificate.
        with self.assertRaises(ValueError):
            self.cache.validate_subset(incoming)
        incoming[0] = (0, 0, 1, 2, 3)
        frozen = self.cache.validate_subset(incoming)
        with self.assertRaises(TypeError):
            frozen[0] = (0, 5, 2, 3)
        with self.assertRaises(TypeError):
            self.cache.complete[0] = (0, 5, 2, 3)
        incoming[0] = (0, 5, 2, 3)
        self.assertEqual(frozen[0], (0, 0, 1, 2, 3))
        incoming[0] = frozen[0]
        self.assertTrue(self.problem.validate(incoming))

    def test_replaced_path_is_checked_against_all_other_paths_and_goal_holds(self):
        problem = GridProblem(2, 3, [], {0: (0, 1), 1: (3, 2)})
        cache = PathValidationCache(problem)
        original = {0: (0, 1), 1: (3, 4, 5, 2)}
        cache.validate_complete(original)
        for changed in ({0: original[0], 1: (3, 4, 1, 2)},
                        {0: (0, 0, 1), 1: (3, 0, 1, 2)}):
            with self.assertRaises(ValueError):
                cache.validate_subset(changed)
        self.assertEqual(cache.latest, {})
        self.assertTrue(cache.validate_complete(original))

    def test_replacement_and_rollback_keep_only_content_bound_evidence(self):
        self.cache.validate_subset({0: (0, 0, 1, 2, 3), 1: self.paths[1]})
        with patch.object(self.problem, 'validate_extension', wraps=self.problem.validate_extension) as extension:
            self.cache.validate_subset(self.paths)  # Exact old complete plan can be reused.
            extension.assert_not_called()
        # Equality alone is not a certificate hit; this conservative miss is safe.
        copy = {a: tuple(list(p)) for a, p in self.paths.items()}
        checked = self.cache.counts['paths_checked']
        self.cache.validate_subset(copy)
        self.assertEqual(self.cache.counts['paths_checked'] - checked, 3)
        # The exact same tuple under a different agent is not inherited proof.
        with self.assertRaisesRegex(ValueError, 'endpoints changed'):
            self.cache.validate_subset({1: self.paths[0]})

    def test_complete_validation_never_uses_cached_subset_instead(self):
        with patch.object(self.problem, 'validate', wraps=self.problem.validate) as full:
            self.assertTrue(self.cache.validate_complete(self.paths))
            full.assert_called_once()
        with self.assertRaises(ValueError):
            self.cache.validate_complete({0: self.paths[0]})

    def test_changed_model_is_rejected_and_other_task_starts_without_proof(self):
        other = PathValidationCache(GridProblem(3, 4, [], {0: (0, 3), 1: (4, 7), 2: (8, 11)}))
        other.validate_subset(self.paths)
        self.assertEqual(other.counts['paths_reused'], 0)
        other.problem = self.problem  # Equal geometry does not transfer a task-local certificate.
        with self.assertRaisesRegex(ValueError, 'problem changed'):
            other.validate_subset(self.paths)
        self.problem.blocked = frozenset({1})
        with self.assertRaisesRegex(ValueError, 'problem changed'):
            self.cache.validate_subset(self.paths)

    def test_incremental_rejects_opposite_edges_with_distinct_endpoints(self):
        problem = GridProblem(2, 3, [], {0: (0, 2), 1: (1, 4)})
        cache = PathValidationCache(problem)
        cache.validate_subset({0: (0, 1, 2)})
        with self.assertRaisesRegex(ValueError, 'opposite-edge'):
            cache.validate_subset({0: (0, 1, 2), 1: (1, 0, 3, 4)})


class CaseHostContracts(unittest.TestCase):
    """The watchdog sees only trivial Python children, never ADDRESS/search."""
    def test_normal_subprocess_is_reaped_and_receipt_write_is_exclusive(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            cost = supervise([sys.executable, '-c', 'print("software contract")'], path,
                             wall_s=2, cpu_s=1, memory_mib=128)
            self.assertEqual(cost['exit_code'], 0)
            self.assertFalse(cost['forced_cleanup'])
            self.assertEqual(len(cost['reaped']), 1)
            write_json(path/'receipt.json', cost)
            with self.assertRaises(FileExistsError):
                write_json(path/'receipt.json', {'replacement': True})
            self.assertEqual(json.loads((path/'receipt.json').read_text()), cost)

    def test_timeout_kills_and_accounts_for_orphan_grandchild(self):
        code = 'import os,time; p=os.fork(); print(os.getpid(),flush=True); time.sleep(10)'
        with tempfile.TemporaryDirectory() as folder:
            cost = supervise([sys.executable, '-c', code], Path(folder),
                             wall_s=0.3, cpu_s=1, memory_mib=128)
            self.assertTrue(cost['forced_cleanup'])
            self.assertEqual(len(cost['reaped']), 2)
            for child in cost['reaped']:
                self.assertEqual(child['exit_code'], -9)
                with self.assertRaises(ProcessLookupError):
                    os.kill(child['pid'], 0)
            self.assertGreaterEqual(cost['all_descendant_user_s'], 0)

    def test_interruption_reaps_child_and_records_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch('run_repair_dev.time.sleep', side_effect=KeyboardInterrupt('scripted stop')):
                cost = supervise([sys.executable, '-c', 'import time; time.sleep(10)'], Path(folder),
                                 wall_s=2, cpu_s=1, memory_mib=128)
            self.assertTrue(cost['forced_cleanup'])
            self.assertIn('scripted stop', cost['interruption'])
            self.assertEqual(cost['exit_code'], -9)

    def test_worker_serializes_complete_fixture_with_fake_backend_only(self):
        class ScriptedBackend:
            def __init__(self, problem, initial, binary, receipt, output, budget, **kwargs):
                self.problem, self.cache, self.records = problem, {}, []
                self.lower_bounds = {5: 2, 9: 2}
                self.proc, self.child_usage = None, {'scope': 'MOCK_NO_PROCESS'}
            def search(self, request):
                return SearchReply(SearchStatus.FOUND, (0, 1, 2))
            def validate(self, request):
                return self.problem.validate(request.paths)
            def close(self):
                pass
        case = {'id': 'software-fixture', 'rows': 2, 'cols': 3, 'blocked': [],
                'endpoints': {'5': [0, 2], '9': [3, 5]},
                'paths': {'5': [0, 0, 1, 2], '9': [3, 3, 4, 5]},
                'orders': [[5]], 'seed': 0}
        config = {'manifest_sha256': 'scripted', 'limits': {'search_calls': 2,
                  'native_cpu_s': 1, 'per_process_as_mib': 128}}
        with tempfile.TemporaryDirectory() as folder:
            good = worker(config, case, 'REMAINING_BOUND', 'NO_BINARY', Path(folder),
                          time.monotonic_ns()+10**9, backend_factory=ScriptedBackend)
            payload = json.loads((Path(folder)/'result.json').read_text())
            self.assertTrue(good)
            self.assertEqual(payload['final_soc'], 5)
            self.assertEqual(payload['initial_soc'], 6)
            self.assertTrue(payload['final_validated'])
            self.assertEqual(payload['native_usage']['scope'], 'MOCK_NO_PROCESS')


class ResidualProfileContracts(unittest.TestCase):
    """Recorded software fixtures only; no native solver or benchmark calls."""

    def fixture(self, *, accepted=False, gap=True):
        initial = {0: [0, 0, 1, 2] if gap else [0, 1, 2], 1: [3, 4, 5]}
        final = {**initial, 0: [0, 1, 2]} if accepted else initial
        before = Incumbent(initial).snapshot().sha256
        after = Incumbent(final).snapshot().sha256
        case = {'id': 'SOFTWARE_FIXTURE', 'rows': 2, 'cols': 3, 'blocked': [],
                'endpoints': {0: [0, 2], 1: [3, 5]}, 'paths': initial,
                'orders': [[0]], 'order_roles': ['LOCAL_ID_BLOCK_8']}
        problem = GridProblem(2, 3, [], case['endpoints'])
        calls = 1 if accepted or gap else 0
        attempt = {'order': [0], 'before_sha256': before, 'after_sha256': after,
                   'old_cost': len(initial[0])-1, 'candidate_cost': 2 if accepted else None,
                   'status': 'ACCEPTED' if accepted else 'NO_IMPROVEMENT',
                   'improvement_label': accepted, 'search_calls': calls,
                   'completed_agents': 1 if accepted else 0, 'wall_ns': 123,
                   'reason': 'complete strict improvement accepted' if accepted else (
                       'complete search exhausted the current improvement cap' if gap else
                       'remaining lower bound exceeds strict target')}
        result = {'case': case['id'], 'model_key': problem.model_key,
                  'lower_bounds': {'0': 2, '1': 2}, 'initial_soc': sum(len(p)-1 for p in initial.values()),
                  'final_soc': sum(len(p)-1 for p in final.values()), 'final_paths': final,
                  'final_sha256': after, 'attempts': [attempt], 'status': 'COMPLETE',
                  'final_validated': True, 'search_calls': calls, 'rpc': [],
                  'stage_wall_ns': {}, 'bootstrap_through_native_ready_ns': 1}
        return case, result

    def test_positive_gap_is_not_improvement_or_global_infeasibility(self):
        from repair_profile import diagnose
        case, result = self.fixture()
        row = diagnose(case, result)
        self.assertEqual(row['decision'], 'POSITIVE_BOUND_GAP_BUT_IMPROVABILITY_UNPROVEN')
        self.assertEqual(row['attempts'][0]['diagnosis'], 'CAP_EXHAUSTED_CURRENT_PREFIX_ONLY')
        self.assertEqual(row['accepted_gain'], 0)

    def test_root_closure_and_complete_improvement_are_distinct(self):
        from repair_profile import diagnose
        case, result = self.fixture(gap=False)
        self.assertEqual(diagnose(case, result)['decision'], 'ZERO_SAME_MODEL_GAP_STOP_THIS_TASK')
        case, result = self.fixture(accepted=True)
        row = diagnose(case, result)
        self.assertEqual(row['accepted_gain'], 1)
        self.assertEqual(row['decision'], 'CLASSICAL_POLICY_REACHES_BOUND_NO_REMAINING_SOC_HEADROOM')

    def test_timeout_is_unknown_and_bad_label_is_rejected(self):
        from repair_profile import diagnose
        case, result = self.fixture()
        result['status'] = result['attempts'][0]['status'] = 'TIMEOUT'
        result['attempts'][0]['improvement_label'] = None
        row = diagnose(case, result)
        self.assertIsNone(row['attempts'][0]['improvement_label'])
        self.assertEqual(row['decision'], 'INCOMPLETE_NO_NEGATIVE_REWARD_LABEL')
        result['attempts'][0]['improvement_label'] = False
        with self.assertRaises(ValueError):
            diagnose(case, result)

    def test_wrong_final_path_hash_and_broken_incumbent_chain_rejected(self):
        from repair_profile import diagnose
        case, result = self.fixture()
        result['final_sha256'] = 'bad'
        with self.assertRaises(ValueError):
            diagnose(case, result)
        case, result = self.fixture()
        result['attempts'][0]['before_sha256'] = 'bad'
        with self.assertRaises(ValueError):
            diagnose(case, result)

    def test_fixed_scope_covers_every_agent_without_outcome_selection(self):
        from repair_profile import fixed_orders
        for n in (16, 32):
            orders = fixed_orders(range(n))
            self.assertEqual(sum(map(len, orders)), n*4)
            self.assertEqual(orders[-2], list(range(n)))
            self.assertEqual(orders[-1], list(reversed(range(n))))
            self.assertEqual(set(a for order in orders[:-2] for a in order), set(range(n)))
            for first, reverse in zip(orders[::2], orders[1::2]):
                self.assertEqual(first, reverse[::-1])
        with self.assertRaises(ValueError):
            fixed_orders(range(8))


if __name__ == "__main__":
    unittest.main()
