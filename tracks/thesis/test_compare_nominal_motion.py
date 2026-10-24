"""Tiny complete-plan software fixtures only; never loads six task paths."""
from pathlib import Path
import unittest
import tempfile
import json
import time
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import patch

import compare_nominal_motion as compare
import nominal_motion as motion
import plan_selection as selection

HERE = Path(__file__).resolve().parent


class CompareContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sci = selection.load_fixed_sci_components(HERE.parents[1])
        cls.Grid = cls.sci['address_backend'].GridProblem

    def acceptance_fixture(self, *, clock=None):
        initial, candidate = {0: [6, 11, 12, 13, 18]}, {0: [6, 7, 8, 13, 18]}
        problem = self.Grid(5, 5, [], {0: (6, 18)})
        Budget, Expired = self.sci['pp_repair'].SharedBudget, self.sci['pp_repair']._Expired
        if clock is None:
            budget = Budget(time.monotonic_ns()+10**10, 0)
        else:
            budget = Budget(100, 0, clock_ns=lambda: clock[0], cpu_clock_ns=lambda: clock[0])
        selector = selection.MotionPlanSelector(problem, initial, self.model(), {0: 0},
            budget=budget, expired_exception=Expired)
        return problem, initial, candidate, budget, selector

    def test_motion_acceptance_worker_connects_both_policies_without_optimizer(self):
        case = dict(id='synthetic_acceptance_fixture', rows=5, cols=5, blocked=[],
            endpoints={'0': [6, 18]}, paths={'0': [6, 11, 12, 13, 18]})
        source = dict(candidates=[dict(label='one_frozen_fixture', paths={'0': [6, 7, 8, 13, 18]})],
                      data_class='SOFTWARE_FIXTURE_NOT_SCI_EVIDENCE')
        config = dict(schema=compare.ACCEPTANCE_SCHEMA, motion_model=self.model().record(),
            initial_heading_quarters=0, manifest_sha256='SOFTWARE_FIXTURE',
            arm_evaluation_wall_s=20, arm_output_reserve_s=2)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            compare.execute_worker(config, case, source, output, HERE.parents[1], 0)
            saved = json.loads((output/'result.json').read_text())
            self.assertEqual(saved['status'], 'COMPLETE')
            self.assertFalse(saved['optimizer_called'])
            self.assertEqual([r['arm'] for r in saved['rows']], list(compare.ACCEPTANCE_ARMS))
            for row in saved['rows']:
                self.assertEqual(row['attempts'][0]['status'], 'ACCEPTED')
                self.assertLess(Fraction(row['final_objective_exact_s']), Fraction(row['initial_objective_exact_s']))
                self.assertTrue(row['arm_output_within_reserve'])
                self.assertTrue((output/('arm_'+row['arm']+'.json')).exists())
            self.assertEqual(saved['rows'][0]['final_paths_sha256'], saved['rows'][1]['final_paths_sha256'])

    def test_bound_equality_rejects_without_candidate_compile_and_full_mode_evaluates(self):
        _, initial, _, _, selector = self.acceptance_fixture()
        before = selector.snapshot()
        with patch.object(selector, '_compile', side_effect=AssertionError('must not evaluate')):
            result = selector.consider(initial, label='equal', use_lower_bound=True)
        self.assertEqual(result['status'], 'LOWER_BOUND_REJECTED')
        self.assertEqual(result['lower_bound_exact_s'], before['objective_exact_s'])
        with patch.object(selector, '_compile', wraps=selector._compile) as full:
            result = selector.consider(initial, label='equal', use_lower_bound=False)
        self.assertEqual(result['status'], 'NO_STRICT_IMPROVEMENT')
        self.assertEqual(full.call_count, 1)
        self.assertEqual(selector.snapshot(), before)

    def test_candidate_deadline_during_complete_evaluation_never_commits_late(self):
        clock = [0]
        _, _, candidate, _, selector = self.acceptance_fixture(clock=clock)
        before, compile_original = selector.snapshot(), selector._compile
        def late(paths):
            answer = compile_original(paths)
            clock[0] = 100
            return answer
        with patch.object(selector, '_compile', side_effect=late):
            result = selector.consider(candidate, label='late', use_lower_bound=False)
        self.assertEqual(result['status'], 'BUDGET_CENSORED')
        self.assertEqual(selector.snapshot(), before)

    def test_invalid_path_and_unproved_certificate_retain_certified_incumbent(self):
        _, _, candidate, _, selector = self.acceptance_fixture()
        before = selector.snapshot()
        result = selector.consider({0: [6, 18]}, label='nonlocal')
        self.assertEqual(result['status'], 'INVALID_CANDIDATE')
        for kind in ['DEPENDENCY_CYCLE', 'CIRCLE_PAIR_SEPARATION_NOT_ESTABLISHED']:
            with patch.object(selector, '_compile', return_value=dict(certified_nominal_reference=False,
                                                                      reason=dict(kind=kind))):
                result = selector.consider(candidate, label=kind, use_lower_bound=False)
            self.assertEqual(result['status'], 'CERTIFICATE_NOT_ESTABLISHED')
        self.assertEqual(selector.snapshot(), before)

    def test_returned_paths_schedule_and_external_problem_cannot_mutate_certificate(self):
        problem, initial, candidate, _, selector = self.acceptance_fixture()
        before = selector.snapshot()
        exported = selector.snapshot()
        exported['paths']['0'][0] = 24
        exported['motion']['schedule']['agents']['0'].clear()
        problem.cols = 99
        initial[0].append(23)
        self.assertEqual(selector.snapshot(), before)
        self.assertEqual(selector.consider(candidate, label='private_context')['status'], 'ACCEPTED')

    def test_unexpected_type_key_and_runtime_errors_are_hard_failures_not_invalid_candidates(self):
        for error in [TypeError('broken implementation'), KeyError('missing internal value'), RuntimeError('bug')]:
            _, _, candidate, _, selector = self.acceptance_fixture()
            before = selector.snapshot()
            with patch.object(selector, '_compile', side_effect=error):
                result = selector.consider(candidate, label='broken', use_lower_bound=False)
            self.assertEqual(result['status'], 'IMPLEMENTATION_FAILED')
            self.assertEqual(selector.snapshot(), before)

    def test_initial_deadline_has_no_certified_fallback_and_hard_error_stops_other_candidates(self):
        problem, initial, candidate, budget, _ = self.acceptance_fixture()
        Expired = self.sci['pp_repair']._Expired
        expired = self.sci['pp_repair'].SharedBudget(0, 0)
        with self.assertRaises(Expired):
            selection.MotionPlanSelector(problem, initial, self.model(), {0: 0},
                budget=expired, expired_exception=Expired)
        original = selection.MotionPlanSelector._compile
        calls = []
        def broken_after_initial(instance, paths):
            calls.append(1)
            if len(calls) > 1:
                raise TypeError('unexpected candidate implementation error')
            return original(instance, paths)
        with patch.object(selection.MotionPlanSelector, '_compile', new=broken_after_initial):
            result = compare.evaluate_motion_candidates(problem, initial,
                [dict(label='broken', paths=candidate), dict(label='not_run', paths=candidate)],
                self.model(), {0: 0}, budget=budget, expired_exception=Expired, use_lower_bound=False)
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['attempts'][1]['status'], 'NOT_ATTEMPTED_AFTER_STOP')
        self.assertEqual(result['initial']['paths_sha256'], result['final']['paths_sha256'])

    def model(self, **changes):
        values = dict(cell_m='1/2', body_length_m='11/50', body_width_m='4/25',
            speed_m_s='1/2', accel_m_s2='1/2', decel_m_s2='1/2',
            turn_speed_rad_s='1', turn_accel_rad_s2='1', turn_decel_rad_s2='1')
        values.update(changes)
        return motion.MotionModel(**values)

    def test_v2_worker_fixture_keeps_padding_cost_and_reference_end_separate(self):
        from v2_motion_inputs import execute_pair_worker
        case = {'id': 'synthetic_fixture', 'rows': 5, 'cols': 5, 'blocked': [],
                'paths': {'0': [6, 7], '1': [16, 17]},
                'endpoints': {'0': [6, 7], '1': [16, 17]},
                'initial_headings': {'0': 2, '1': 1}, 'source': {'fixture_only': True},
                'coordinate_translation_m': ['0', '0'], 'data_class': 'SOFTWARE_FIXTURE'}
        config = {'manifest_sha256': 'fixture_not_a_run_manifest'}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            execute_pair_worker(config, case, {}, output, HERE.parents[1], 0, time.monotonic_ns())
            result = json.loads((output/'result.json').read_text())
            self.assertEqual(result['status'], 'COMPLETE')
            self.assertFalse(result['common_end_received'])
            self.assertTrue(result['pair']['both_arms_same_reference_time'])
            nominal, uncertain = result['rows']
            self.assertEqual(uncertain['metrics']['feasibility'], 'CERTIFIED_INITIAL_POSE_ENCLOSURE')
            self.assertEqual(nominal['metrics']['completion_sum_s'], uncertain['metrics']['completion_sum_s'])
            for row in result['rows']:
                metrics = row['metrics']
                self.assertGreater(metrics['turn_slot_padding_wait_s'], 0)
                self.assertAlmostEqual(metrics['wait_sum_s'], sum(metrics[k] for k in
                    ('turn_barrier_wait_s', 'discrete_wait_slot_s', 'turn_slot_padding_wait_s')))
                self.assertEqual(metrics['permanent_goal_hold_count'], 2)

    def test_frozen_equal_soc_proposal_is_not_silently_replaced(self):
        original, proposal = {0: (6, 7, 8, 13, 18)}, {0: (6, 11, 12, 13, 18)}
        problem = self.Grid(5, 5, [], {0: (6, 18)})
        result = compare.compare_plans(problem, original, proposal, self.model(), {0: 0})
        rows = result['rows']
        self.assertEqual([r['arm'] for r in rows], list(compare.ARMS))
        self.assertEqual(rows[1]['selection']['selected'], 'frozen_proposal')
        self.assertEqual(rows[2]['selection']['selected'], 'incumbent')
        self.assertTrue(all(r['soc'] == 4 for r in rows))
        self.assertGreater(rows[1]['metrics']['completion_sum_s'], rows[0]['metrics']['completion_sum_s'])
        self.assertTrue(all(r['motion']['initial_headings_quarters'] == {0: 0} for r in rows))
        self.assertFalse(result['optimizer_called'])

    def test_wait_partition_stops_at_completion_and_preserves_zero_step_goal(self):
        paths = {0: (6, 7), 1: (16, 16, 17), 2: (18,)}
        problem = self.Grid(5, 5, [], {a: (p[0], p[-1]) for a, p in paths.items()})
        result = compare.compare_plans(problem, paths, paths, self.model(), {a: 0 for a in paths})
        for row in result['rows']:
            metric = row['metrics']
            self.assertEqual(metric['permanent_goal_hold_count'], 3)
            self.assertEqual(metric['per_agent'][2], {'completion_s': 0.0, 'wait_s': 0.0})
            self.assertFalse(metric['goal_hold_in_wait_sum'])
            self.assertAlmostEqual(metric['wait_sum_s'], metric['turn_barrier_wait_s']+metric['discrete_wait_slot_s'])
            self.assertAlmostEqual(metric['completion_sum_s'], metric['move_s']+metric['turn_s']+metric['wait_sum_s'])
            self.assertGreater(metric['wait_sum_s'], 0)

    def test_circle_rejection_is_retained_with_unknown_time_not_collision(self):
        paths = {0: (6, 7), 1: (7, 12)}
        problem = self.Grid(5, 5, [], {a: (p[0], p[-1]) for a, p in paths.items()})
        result = compare.compare_plans(problem, paths, paths,
            self.model(cell_m='1', body_length_m='.6', body_width_m='.6'), {0: 0, 1: 0})
        self.assertEqual(result['status'], 'COMPLETE')
        for row in result['rows']:
            self.assertEqual(row['metrics']['feasibility'], 'SUFFICIENT_SEPARATION_NOT_ESTABLISHED')
            self.assertFalse(row['metrics']['collision_claim'])
            self.assertIsNone(row['metrics']['completion_sum_s'])
            self.assertIsNone(row['motion']['schedule'])

    def test_simultaneous_retention_conflict_is_rejected_before_motion(self):
        problem = self.Grid(3, 3, [], {0: (0, 4), 1: (2, 6)})
        old = {0: [0, 1, 4], 1: [2, 2, 5, 8, 7, 6]}
        new = {0: [0, 3, 4], 1: [2, 1, 0, 3, 6]}
        result = compare.compare_plans(problem, old, new, self.model(), {0: 0, 1: 0})
        selected = result['rows'][2]['selection']
        retained = next(c for c in selected['candidates'] if c['name'] == 'retain_equal_cost_batch')
        self.assertFalse(retained['valid'])
        self.assertEqual(selected['selected'], 'proposal')

    def test_changed_config_fails_before_loading_or_running_any_case(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'config.json'
            path.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'manifest SHA'):
                compare.load(path, '0'*64, HERE.parents[1])

    def test_failed_previous_case_prevents_consuming_next_case(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = root/'results'/'tiny_batch'/'case0'
            first.mkdir(parents=True)
            (first/'receipt.json').write_text(json.dumps({'status': 'FAILED_OR_INCOMPLETE',
                                                        'manifest_sha256': 'f'*64}))
            config = {'cases': ['case0', 'case1'], 'batch_id': 'tiny_batch'}
            args = SimpleNamespace(case='case1', authorization_reference='fixture-only-reference', sha256='f'*64)
            with patch.object(compare, 'HERE', root), self.assertRaisesRegex(ValueError, 'batch stopped'):
                compare.run(args, config, {}, {}, None)
            self.assertFalse((first.parent/'case1').exists())

    def test_invalid_frozen_proposal_and_missing_heading_are_not_accepted(self):
        problem = self.Grid(3, 4, [], {0: (0, 2), 1: (6, 4)})
        original = {0: (0, 1, 2), 1: (6, 5, 4)}
        with self.assertRaises(ValueError):
            compare.compare_plans(problem, original, {0: (0, 1, 2), 1: (6, 1, 4)},
                                  self.model(), {0: 0, 1: 0})
        # Missing initial orientation is invalid input, not an inconclusive
        # geometric rejection that would let a batch continue.
        with self.assertRaises(ValueError):
            compare.compare_plans(problem, original, original, self.model(), {0: 0})

    def test_scheduler_pair_keeps_same_selected_paths_and_wait_cost_partition(self):
        paths = {0: [6, 11], 1: [16, 17]}
        problem = self.Grid(5, 5, [], {a: (p[0], p[-1]) for a, p in paths.items()})
        result = compare.compare_plans(problem, paths, paths, self.model(), {0: 0, 1: 0},
                                       scheduler_comparison=True)
        self.assertEqual([row['arm'] for row in result['rows']], list(compare.SCHEDULER_ARMS))
        for global_row, local_row in zip(result['rows'][::2], result['rows'][1::2]):
            self.assertEqual(global_row['complete_paths_sha256'], local_row['complete_paths_sha256'])
            self.assertEqual(global_row['motion']['schedule']['profiles'], local_row['motion']['schedule']['profiles'])
            self.assertGreater(global_row['metrics']['completion_sum_s'], local_row['metrics']['completion_sum_s'])
            self.assertEqual(local_row['stage_wall_ns']['whole_plan_selection'], 0)
            for row in (global_row, local_row):
                metrics = row['metrics']
                self.assertAlmostEqual(metrics['completion_sum_s'], metrics['turn_s']+metrics['move_s']+metrics['wait_sum_s'])
                self.assertAlmostEqual(metrics['wait_sum_s'], sum(metrics[k] for k in
                    ('turn_barrier_wait_s', 'local_dependency_wait_s', 'discrete_wait_slot_s', 'turn_slot_padding_wait_s')))

    def test_scheduler_cycle_is_retained_and_worker_serializes_six_artifacts(self):
        paths = {0: [6, 7], 1: [7, 12], 2: [12, 11], 3: [11, 6]}
        problem = self.Grid(5, 5, [], {a: (p[0], p[-1]) for a, p in paths.items()})
        value = compare.compare_plans(problem, paths, paths, self.model(), {a: 0 for a in paths},
                                      scheduler_comparison=True)
        self.assertEqual(value['status'], 'COMPLETE')
        for row in value['rows'][1::2]:
            self.assertEqual(row['metrics']['feasibility'], 'LOCAL_CONSTRUCTION_NOT_ESTABLISHED')
            self.assertIsNone(row['metrics']['completion_sum_s'])
            self.assertFalse(row['metrics']['collision_claim'])
        case = dict(id='synthetic_scheduler_fixture', rows=5, cols=5, blocked=[],
                    paths={str(a): p for a, p in paths.items()},
                    endpoints={str(a): [p[0], p[-1]] for a, p in paths.items()})
        source = dict(final_paths=case['paths'], initial_soc=4, final_soc=4,
                      _frozen_provenance={'data_class': 'SOFTWARE_FIXTURE'}, _prior_optimizer_costs={})
        config = dict(schema=compare.SCHEDULER_SCHEMA, motion_model=self.model().record(),
                      initial_heading_quarters=0, manifest_sha256='SOFTWARE_FIXTURE')
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            compare.execute_worker(config, case, source, output, HERE.parents[1], 0)
            self.assertEqual(len(list(output.glob('arm_*.json'))), 6)
            saved = json.loads((output/'result.json').read_text())
            self.assertEqual([row['arm'] for row in saved['rows']], list(compare.SCHEDULER_ARMS))
            self.assertFalse(saved['optimizer_called'])
            self.assertFalse(saved['v2_applied'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
