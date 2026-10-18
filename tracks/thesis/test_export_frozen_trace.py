"""Offline contract tests against immutable evidence; no science module imports."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('trace_export', HERE / 'export_frozen_trace.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class FrozenTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = HERE.parents[1]
        cls.lock = json.loads((HERE / 'shared.lock.json').read_bytes())
        cls.evidence, _ = exporter.load_evidence(cls.repo, cls.lock)

    def setUp(self):
        self.records = [json.loads(line) for line in self.evidence['ids13_initial_events'].splitlines()]
        self.result = json.loads(self.evidence['ids13_initial_result'])

    def join(self):
        return exporter.join_records('ids13_initial', self.records, self.result)

    def reseal_evaluation_fixture(self):
        values = [r['data'] for r in self.records if r['event'] == 'evaluation_only']
        self.result['session_receipt']['evaluation_records_sha256'] = exporter.sha(exporter.canonical(values))

    def evaluation(self):
        return next(r['data']['data']['evaluation'] for r in self.records if r['event'] == 'evaluation_only')

    def test_all_frozen_cases_have_exact_coverage_and_delivered_ends(self):
        all_rows, all_ends = [], []
        for case, expected in exporter.CASES.items():
            with self.subTest(case=case):
                rows, ends, _ = exporter.parse_case(case, self.evidence[case + '_events'],
                                                    self.evidence[case + '_result'])
                self.assertEqual(len(rows), expected)
                self.assertTrue(all(r['data_scope'] == 'evaluation_only' for r in rows))
                self.assertTrue(all(r['feedback_accepted'] for r in rows))
                self.assertTrue(all(e['end_received_s'] >= e['completion_s'] for e in ends))
                all_rows.extend(rows)
                all_ends.extend(ends)
        self.assertEqual((len(all_rows), len(all_ends)), (262, 10))

    def test_join_uses_keys_not_record_position(self):
        expected = self.join()
        captures_and_deliveries = [r for r in self.records if r['event'] in ('capture', 'delivery')]
        rest = [r for r in self.records if r['event'] not in ('capture', 'delivery')]
        self.records = rest + list(reversed(captures_and_deliveries))
        self.result['session_receipt']['receive_attempts'].reverse()
        self.assertEqual(self.join(), expected)

    def test_initial_mode_control_state_and_time_semantics(self):
        rows, _ = self.join()
        first = next(r for r in rows if r['robot'] == 'agent1' and r['seq'] == 0)
        self.assertEqual(first['source_primitive_mode'], 'ACCEL')
        self.assertEqual(first['public_state_at_capture'], 'STOPPED')
        self.assertEqual(first['actual_control_phase'], 'STOPPED')
        self.assertEqual((first['v_cmd'], first['omega_cmd']), (0, 0))
        self.assertAlmostEqual(first['transmission_delay_s'], 0.1)
        self.assertIsNone(first['trajectory_time_offset_s'])
        self.assertEqual(first['trajectory_time_offset_status'], 'NOT_IDENTIFIED')
        self.assertAlmostEqual(first['tracking_x'], -0.005)
        self.assertAlmostEqual(first['localization_x'], 0.005)
        self.assertAlmostEqual(first['reported_x'], 0)
        self.assertAlmostEqual(first['tracking_y'], -0.01)
        self.assertAlmostEqual(first['localization_y'], -0.005)
        self.assertAlmostEqual(first['reported_y'], -0.015)

    def test_missing_independent_truth_never_becomes_observed_tracking(self):
        del self.evaluation()['pose_true']
        self.reseal_evaluation_fixture()
        rows, _ = self.join()
        first = next(r for r in rows if r['robot'] == 'agent1' and r['seq'] == 0)
        self.assertEqual(first['truth_status'], 'MISSING')
        for key in ('true_x', 'true_y', 'true_theta', 'tracking_x', 'tracking_y',
                    'tracking_theta', 'localization_x', 'localization_y',
                    'tracking_xy_norm', 'localization_xy_norm'):
            self.assertIsNone(first[key], key)
        self.assertAlmostEqual(first['reported_y'], -0.015)

    def test_duplicate_or_unpaired_capture_is_rejected(self):
        originals = copy.deepcopy(self.records)
        for mutation in ('duplicate_evaluation', 'missing_evaluation', 'duplicate_packet', 'missing_delivery'):
            with self.subTest(mutation=mutation):
                self.records = copy.deepcopy(originals)
                kind = 'evaluation_only' if 'evaluation' in mutation else 'capture' if 'packet' in mutation else 'delivery'
                index = next(i for i, row in enumerate(self.records) if row['event'] == kind)
                if mutation.startswith('duplicate'):
                    self.records.append(copy.deepcopy(self.records[index]))
                else:
                    self.records.pop(index)
                with self.assertRaisesRegex(ValueError, 'duplicate|coverage mismatch'):
                    self.join()

    def test_mismatched_clock_time_or_observation_is_rejected(self):
        originals = copy.deepcopy(self.records)
        for field, replacement, message in [('physical_time', '1/100', 'capture/clock'),
                                             ('shared_clock', 'another-clock', 'capture/clock'),
                                             ('controller_phase', '2', 'public interval')]:
            with self.subTest(field=field):
                self.records = copy.deepcopy(originals)
                self.evaluation()[field] = replacement
                self.reseal_evaluation_fixture()
                with self.assertRaisesRegex(ValueError, message):
                    self.join()
        self.records = copy.deepcopy(originals)
        next(r['data']['data'] for r in self.records if r['event'] == 'evaluation_only')['observation'][0] += 0.02
        self.reseal_evaluation_fixture()
        with self.assertRaisesRegex(ValueError, 'public/evaluation observation mismatch'):
            self.join()

    def test_rejected_end_cannot_support_completion(self):
        end = next(r['packet'] for r in self.records if r['event'] == 'capture' and r['packet']['kind'] == 'END')
        digest = exporter.sha(exporter.canonical(end))
        attempt = next(a for a in self.result['session_receipt']['receive_attempts'] if a['sha256'] == digest)
        attempt['accepted'] = False
        with self.assertRaisesRegex(ValueError, 'completion lacks accepted delivered END'):
            self.join()

    def test_incomplete_or_schedule_only_completion_is_rejected(self):
        self.result['session_receipt']['completion'].pop('agent3')
        self.result['completion'].pop('agent3')
        with self.assertRaisesRegex(ValueError, 'completion robot IDs mismatch'):
            self.join()
        self.setUp()
        self.result['session_receipt']['completion']['agent3'] = '18'
        self.result['completion']['agent3'] = '18'
        with self.assertRaisesRegex(ValueError, 'accepted END completion mismatch'):
            self.join()

    def test_wrong_delivery_or_acceptance_identity_is_rejected(self):
        delivery = next(r for r in self.records if r['event'] == 'delivery')
        delivery['now'] = '0'
        with self.assertRaisesRegex(ValueError, 'delivery kind/time mismatch'):
            self.join()
        self.setUp()
        self.result['session_receipt']['receive_attempts'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'unique matching packet acceptance receipt'):
            self.join()

    def test_reader_content_must_be_verified_before_execution(self):
        lock = copy.deepcopy(self.lock)
        lock['reader']['sha256'] = '0' * 64
        with patch('builtins.exec', side_effect=AssertionError('unverified reader executed')):
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch before execution'):
                exporter.load_reader(self.repo, lock)


class SciPathStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('sci_path_audit', HERE/'inspect_sci_paths.py')
        cls.audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.audit)

    def test_waits_preserve_direction_and_reversal_is_two_quarters(self):
        shape = self.audit.path_shape([0, 1, 1, 2, 1, 4], 2, 3)
        self.assertEqual((shape['moves'], shape['waits'], shape['internal_quarter_turns']), (4, 1, 3))

    def test_stationary_path_does_not_invent_heading(self):
        shape = self.audit.path_shape([0, 0], 2, 3)
        self.assertIsNone(shape['first_direction'])
        self.assertIsNone(shape['last_direction'])
        self.assertEqual(shape['internal_quarter_turns'], 0)

    def test_invalid_geometry_rejected(self):
        for path in ([2, 3], [0, 4], [0, 1]):
            with self.assertRaises(ValueError):
                self.audit.path_shape(path, 2, 3, blocked=[1])

    def test_boundary_triangle_bound_on_declared_heading_values(self):
        d = self.audit.quarter_distance
        for u in range(4):
            for v in range(4):
                for h in range(4):
                    self.assertLessEqual(abs(d(h, u)-d(h, v)), d(u, v))

    def test_existing_random32_equal_cost_reroute_decomposition(self):
        rows = self.audit.analyze(HERE.parents[1])['rows']
        row = next(r for r in rows if r['case'] == 'random-32-32-10__s01__n32')
        group = row['path_change_groups']
        self.assertEqual(group['equal_cost_reroute']['count'], 29)
        self.assertEqual(group['equal_cost_reroute']['delta']['internal_quarter_turns'], 113)
        self.assertEqual(group['unchanged']['agents'], [8])
        self.assertEqual(group['shorter']['agents'], [19])
        self.assertEqual(group['shorter']['soc_delta'], -2)
        self.assertEqual(group['longer']['agents'], [3])
        self.assertEqual(group['longer']['soc_delta'], 1)
        for r in rows:
            self.assertEqual(sum(g['count'] for g in r['path_change_groups'].values()), len(r['per_agent']))
            self.assertEqual(sum(g['soc_delta'] for g in r['path_change_groups'].values()),
                             r['final_soc']-r['initial_soc'])
            self.assertEqual(sum(g['delta']['internal_quarter_turns'] for g in r['path_change_groups'].values()),
                             r['delta']['internal_quarter_turns'])
            if r['case'].startswith('warehouse'):
                for screen in r['v2_one_edge_per_move_necessary_scale_interval'].values():
                    self.assertFalse(screen['necessary_interval_nonempty'])


class WholePlanSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('plan_selection', HERE/'plan_selection.py')
        cls.selection = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.selection)
        cls.Grid = cls.selection.load_grid_problem(HERE.parents[1])

    def test_equal_cost_retention_must_pass_full_multirobot_check(self):
        problem = self.Grid(3, 3, [], {0: (0, 4), 1: (2, 6)})
        old = {0: [0, 1, 4], 1: [2, 2, 5, 8, 7, 6]}
        new = {0: [0, 3, 4], 1: [2, 1, 0, 3, 6]}
        untouched = copy.deepcopy((old, new))
        result = self.selection.select_complete_plan(problem, old, new, rule='preserve_equal_cost')
        self.assertEqual(result['selected'], 'proposal')
        retained = next(c for c in result['candidates'] if c['name'] == 'retain_equal_cost_batch')
        self.assertFalse(retained['valid'])
        self.assertIn('vertex/goal-hold', retained['reason'])
        self.assertEqual((old, new), untouched)

    def test_turn_aware_control_has_explicit_secondary_objective(self):
        problem = self.Grid(3, 3, [], {0: (0, 8)})
        old, new = {0: [0, 1, 4, 5, 8]}, {0: [0, 1, 2, 5, 8]}
        preserved = self.selection.select_complete_plan(problem, old, new, rule='preserve_equal_cost')
        turns = self.selection.select_complete_plan(problem, old, new, rule='turn_aware')
        original = self.selection.select_complete_plan(problem, old, new, rule='soc_only')
        self.assertEqual(preserved['selected'], 'incumbent')
        self.assertEqual(original['selected'], 'incumbent')
        self.assertEqual(turns['selected'], 'proposal')
        self.assertEqual(turns['candidates'][0]['internal_quarter_turns'], 3)
        self.assertEqual(turns['candidates'][1]['internal_quarter_turns'], 1)

    def test_goal_hold_conflict_and_incomplete_proposal_fall_back(self):
        problem = self.Grid(3, 3, [], {0: (1, 1), 1: (0, 2)})
        old = {0: [1], 1: [0, 3, 4, 5, 2]}
        for proposal in ({0: [1], 1: [0, 0, 1, 2]}, {1: [0, 3, 4, 5, 2]}):
            with self.subTest(proposal=proposal):
                answer = self.selection.select_complete_plan(problem, old, proposal, rule='turn_aware')
                self.assertEqual(answer['selected'], 'incumbent')
                self.assertTrue(answer['final_validated'])
                self.assertFalse(answer['continuous_safety_checked'])
                self.assertEqual(answer['search_calls'], 0)

    def test_invalid_incumbent_cannot_be_repaired_silently(self):
        problem = self.Grid(1, 2, [], {0: (0, 1), 1: (1, 0)})
        with self.assertRaisesRegex(ValueError, 'opposite-edge'):
            self.selection.select_complete_plan(problem, {0: [0, 1], 1: [1, 0]},
                                                {0: [0, 1], 1: [1, 0]}, rule='soc_only')


if __name__ == '__main__':
    unittest.main(verbosity=2)
