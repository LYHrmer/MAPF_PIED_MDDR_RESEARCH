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


if __name__ == '__main__':
    unittest.main(verbosity=2)
