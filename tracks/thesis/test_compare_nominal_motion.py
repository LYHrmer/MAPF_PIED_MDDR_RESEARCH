"""Tiny complete-plan software fixtures only; never loads six task paths."""
from pathlib import Path
import unittest
import tempfile
import json
import time
from types import SimpleNamespace
from unittest.mock import patch

import compare_nominal_motion as compare
import nominal_motion as motion
import plan_selection as selection

HERE = Path(__file__).resolve().parent


class CompareContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.Grid = selection.load_grid_problem(HERE.parents[1])

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
