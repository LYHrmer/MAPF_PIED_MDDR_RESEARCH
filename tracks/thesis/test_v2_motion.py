"""Small software fixtures only; no scientific case, solver or world is loaded."""
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent


def local(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE/filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # Required by dataclass annotation processing.
    spec.loader.exec_module(module)
    return module


motion = local('nominal_motion', 'nominal_motion.py')
v2 = local('v2_motion', 'v2_motion.py')
selection = local('plan_selection', 'plan_selection.py')


class V2MotionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.Grid = selection.load_grid_problem(HERE.parents[1])

    def problem(self, paths, *, rows=5, cols=5, blocked=()):
        endpoints = {a: (p[0], p[-1]) for a, p in paths.items()}
        return self.Grid(rows, cols, blocked, endpoints)

    def test_fixed_si_parameters_and_rational_body_bound(self):
        self.assertEqual(v2.V2_MODEL.cell_m, Fraction(1))
        self.assertEqual((v2.V2_MODEL.body_length_m, v2.V2_MODEL.body_width_m),
                         (Fraction(3, 5), Fraction(1, 5)))
        self.assertEqual((v2.V2_MODEL.speed_m_s, v2.V2_MODEL.accel_m_s2,
                          v2.V2_MODEL.decel_m_s2),
                         (Fraction(1, 2), Fraction(1), Fraction(1)))
        self.assertEqual((v2.V2_MODEL.turn_speed_rad_s, v2.V2_MODEL.turn_accel_rad_s2,
                          v2.V2_MODEL.turn_decel_rad_s2),
                         (Fraction(1, 2), Fraction(1), Fraction(1)))
        self.assertEqual(v2.TURN_QUARTER_SLOT_S, Fraction(4))
        self.assertEqual(v2.BODY_RADIUS_SQUARED_M2, Fraction(1, 10))
        self.assertGreaterEqual(v2.BODY_RADIUS_CEILING_M**2, v2.BODY_RADIUS_SQUARED_M2)
        self.assertLess(v2.BODY_RADIUS_CEILING_M**2,
                        v2.BODY_RADIUS_SQUARED_M2+Fraction(1, 10**11))
        self.assertEqual(v2.SHARED_CIRCLE_RADIUS_M,
                         v2.BODY_RADIUS_CEILING_M+v2.NUMERIC_MARGIN_M)

    def test_static_qualification_limits_are_inclusive_and_exact(self):
        inside = {0: (0, 1, 2)}
        self.assertTrue(v2.static_qualification(self.problem(inside), inside)['qualified'])
        # 9 m single-axis displacement exceeds 8 m, while |x| stays at most 9 m.
        displaced = {0: tuple(range(10))}
        answer = v2.static_qualification(self.problem(displaced, rows=2, cols=12), displaced)
        self.assertFalse(answer['qualified'])
        self.assertIn('INITIAL_X_DISPLACEMENT_LIMIT',
                      {row['kind'] for row in answer['violations']})
        # |x|=11 m exceeds 10 m with only 5 m displacement from this task start.
        absolute = {0: tuple(range(6, 12))}
        answer = v2.static_qualification(self.problem(absolute, rows=2, cols=12), absolute)
        self.assertFalse(answer['qualified'])
        kinds = {row['kind'] for row in answer['violations']}
        self.assertIn('ABSOLUTE_X_LIMIT', kinds)
        self.assertNotIn('INITIAL_X_DISPLACEMENT_LIMIT', kinds)
        self.assertEqual(answer['static_properties'],
                         {'per_cell_move_rest_to_rest': True,
                          'stationary_wait_has_no_translation': True,
                          'turn_occurs_at_fixed_centre': True})

    def test_propagated_increment_is_never_reset_at_waypoints(self):
        paths = {0: (11, 12, 7)}  # East then North, one cell each.
        rows = v2.propagated_radius_increments(self.problem(paths), paths)
        base = v2.INITIAL_L1_RADIUS_M
        growth = v2.INITIAL_HEADING_BOUND_RAD+v2.INITIAL_HEADING_BOUND_RAD**2/2
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], base+growth)
        self.assertEqual(rows[1][0], base+2*growth)
        self.assertGreater(rows[1][0], rows[0][0])
        # The shorter robot is stationary at its goal during global step 1;
        # its increment still refers to the task initial state, not a reset.
        mixed = {0: (11, 12), 1: (16, 17, 18)}
        rows = v2.propagated_radius_increments(self.problem(mixed), mixed)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][0], base+growth)
        self.assertEqual(rows[0][1], base+growth)
        self.assertEqual(rows[1][1], base+2*growth)

    def test_nominal_and_error_arms_share_one_closed_form_schedule(self):
        paths = {0: [11, 12], 1: [16, 17]}
        answer = v2.compile_v2_pair(self.problem(paths), paths, {0: 2, 1: 3})
        self.assertEqual(answer['status'], 'CERTIFIED_V2_PAIR')
        self.assertTrue(answer['certified_sufficient_conditions'])
        self.assertTrue(answer['both_arms_same_reference_schedule'])
        self.assertTrue(answer['both_arms_same_reference_time'])
        self.assertFalse(answer['common_end_received'])
        self.assertFalse(answer['waiting_benefit_claimed'])
        self.assertFalse(answer['rescheduling_performed'])
        self.assertFalse(answer['collision_claim'])
        self.assertEqual(answer['schedule_semantics'], 'CLOSED_FORM_REFERENCE_SCHEDULE')
        nominal = answer['arms']['zero_initial_pose_error']
        error = answer['arms']['propagated_initial_pose_error']
        self.assertTrue(nominal['certified_nominal_reference'])
        self.assertTrue(error['certified_nominal_reference'])
        self.assertFalse(nominal['v2_initial_pose_error_applied'])
        self.assertTrue(error['v2_initial_pose_error_applied'])
        self.assertTrue(error['error_model_applied'])
        self.assertEqual(nominal['schedule'], error['schedule'])
        self.assertEqual(nominal['schedule']['completion_s'], error['schedule']['completion_s'])
        self.assertEqual(answer['reference_completion_s'], nominal['schedule']['completion_s'])
        self.assertEqual(nominal['construction']['maximum_radius_increment_m'], '0')
        self.assertGreater(
            Fraction(error['construction']['maximum_radius_increment_m']), 0)
        self.assertEqual(nominal['construction']['turn_quarter_slot_s'], '4')
        self.assertEqual(error['construction']['turn_quarter_slot_s'], '4')
        split = ['TURN', 'WAIT', 'TURN', 'WAIT', 'MOVE', 'GOAL_HOLD']
        self.assertEqual([r['kind'] for r in nominal['schedule']['agents'][0]], split)
        self.assertEqual([r['kind'] for r in error['schedule']['agents'][0]], split)
        self.assertTrue(all(answer['schedule_properties'].values()))

    def test_propagated_increment_can_flip_pair_sufficiency_without_collision_claim(self):
        # On a 12x12 fixture, robot 0 traverses 4 cells east and 4 north before
        # a followed-vertex crossing; robot 1 waits at that vertex and leaves
        # south. The nominal arm's circles separate at the crossing, while the
        # accumulated increments make the sufficient condition fail there.
        first = [49, 50, 51, 52, 53, 41, 29, 17, 5, 6]
        second = [6]*9+[18]
        paths = {0: first, 1: second}
        answer = v2.compile_v2_pair(self.problem(paths, rows=12, cols=12),
                                    paths, {0: 0, 1: 0})
        self.assertEqual(answer['status'], 'SUFFICIENT_SEPARATION_NOT_ESTABLISHED')
        self.assertFalse(answer['certified_sufficient_conditions'])
        self.assertFalse(answer['both_arms_same_reference_schedule'])
        self.assertFalse(answer['collision_claim'])
        nominal = answer['arms']['zero_initial_pose_error']
        error = answer['arms']['propagated_initial_pose_error']
        self.assertTrue(nominal['certified_nominal_reference'])
        self.assertFalse(error['certified_nominal_reference'])
        self.assertIsNone(error['schedule'])
        self.assertEqual(error['reason']['kind'],
                         'CIRCLE_PAIR_SEPARATION_NOT_ESTABLISHED')
        self.assertEqual(error['reason']['step'], 8)
        self.assertEqual(error['reason']['common_progress_at_minimum'], '1/2')

    def test_not_qualified_returns_no_arms_and_no_collision_claim(self):
        paths = {0: tuple(range(10))}
        answer = v2.compile_v2_pair(self.problem(paths, rows=2, cols=12), paths, {0: 0})
        self.assertEqual(answer['status'], 'NOT_QUALIFIED')
        self.assertFalse(answer['certified_sufficient_conditions'])
        self.assertIsNone(answer['arms'])
        self.assertFalse(answer['collision_claim'])
        self.assertEqual(answer['reason']['kind'], 'V2_STATIC_QUALIFICATION_FAILED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
