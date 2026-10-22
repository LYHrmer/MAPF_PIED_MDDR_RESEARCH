"""Small software fixtures only; no scientific cases, solver, world or training."""
import copy
from fractions import Fraction
import importlib.util
import math
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
selection = local('plan_selection', 'plan_selection.py')


class NominalMotionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.Grid = selection.load_grid_problem(HERE.parents[1])

    def model(self, **changes):
        values = dict(cell_m='1', body_length_m='0.2', body_width_m='0.2',
                      speed_m_s='0.5', accel_m_s2='1', decel_m_s2='0.8',
                      turn_speed_rad_s='0.5', turn_accel_rad_s2='1', turn_decel_rad_s2='0.8')
        values.update(changes)
        return motion.MotionModel(**values)

    def compile(self, paths, *, rows=5, cols=5, blocked=(), model=None, headings=None,
                turn_quarter_slot_s=None, radius_increments=None, body_radius_m=None):
        endpoints = {a: (p[0], p[-1]) for a, p in paths.items()}
        problem = self.Grid(rows, cols, blocked, endpoints)
        if headings is None:
            headings = {a: 0 for a in paths}
        return motion.compile_motion(problem, paths, model or self.model(), headings,
                                     turn_quarter_slot_s=turn_quarter_slot_s,
                                     radius_increments=radius_increments,
                                     body_radius_m=body_radius_m)

    def test_exact_relative_minimum_detects_between_vertex_proximity(self):
        distance2, q = motion.relative_minimum_squared((0, 0), (1, 0), (1, 0), (1, 1))
        self.assertEqual((distance2, q), (Fraction(1, 2), Fraction(1, 2)))
        self.assertIsInstance(q, Fraction)
        # The discrete plan is legal; its large circular enclosures are not
        # proved separated at q=1/2. This is not a rectangular collision label.
        answer = self.compile({0: [6, 7], 1: [7, 12]},
                              model=self.model(body_length_m='.6', body_width_m='.6'))
        self.assertEqual(answer['status'], 'REJECTED')
        self.assertFalse(answer['certified_nominal_reference'])
        self.assertIsNone(answer['schedule'])
        self.assertEqual(answer['reason']['kind'], 'CIRCLE_PAIR_SEPARATION_NOT_ESTABLISHED')
        self.assertEqual(answer['reason']['common_progress_at_minimum'], '1/2')

    def test_shared_phase_preserves_following_distance(self):
        paths = {0: [11, 12], 1: [12, 13]}
        original = copy.deepcopy(paths)
        answer = self.compile(paths)
        self.assertTrue(answer['certified_nominal_reference'])
        moves = [row for rows in answer['schedule']['agents'].values() for row in rows if row['kind'] == 'MOVE']
        self.assertEqual(len({row['phase_id'] for row in moves}), 1)
        self.assertEqual(len({(row['start_s'], row['end_s']) for row in moves}), 1)
        distance2, _ = motion.relative_minimum_squared((0, 0), (1, 0), (1, 0), (2, 0))
        self.assertEqual(distance2, 1)
        # With independent progress q_A=1,q_B=0 these centres coincide. The
        # certified schedule explicitly forbids that altered execution model.
        self.assertIn('share one physical progress', answer['certificate']['conditions'][1])
        self.assertEqual(paths, original)

    def test_unequal_turns_wait_for_one_barrier_before_translation(self):
        answer = self.compile({0: [11, 12], 1: [16, 17]}, headings={0: 2, 1: 3})
        self.assertTrue(answer['certified_nominal_reference'])
        rows = answer['schedule']['agents']
        self.assertEqual(rows[0][0]['kind'], 'TURN')
        self.assertEqual(rows[0][0]['signed_quarters'], 2)
        self.assertEqual([r['kind'] for r in rows[1]], ['TURN', 'WAIT', 'MOVE', 'GOAL_HOLD'])
        a = next(r for r in rows[0] if r['kind'] == 'MOVE')
        b = next(r for r in rows[1] if r['kind'] == 'MOVE')
        self.assertEqual((a['start_s'], a['end_s'], a['phase_id']),
                         (b['start_s'], b['end_s'], b['phase_id']))
        for path in rows.values():
            self.assertEqual(path[0]['start_s'], 0)
            for before, after in zip(path, path[1:]):
                self.assertEqual(before['end_s'], after['start_s'])
            self.assertIsNone(path[-1]['end_s'])

    def test_obstacle_and_map_boundary_enclosures_fail_closed(self):
        obstacle = self.compile({0: [12, 13]}, blocked=[7],
                                model=self.model(body_length_m='.8', body_width_m='.8'))
        self.assertEqual(obstacle['reason']['kind'], 'CIRCLE_OBSTACLE_SEPARATION_NOT_ESTABLISHED')
        self.assertIsNone(obstacle['schedule'])
        edge = self.compile({0: [0, 1]}, model=self.model(body_length_m='1', body_width_m='1'))
        self.assertEqual(edge['reason']['kind'], 'CIRCLE_MAP_CONTAINMENT_NOT_ESTABLISHED')
        self.assertFalse(edge['certified_nominal_reference'])
        distance = motion.segment_box_distance_squared((Fraction(0), Fraction(0)),
            (Fraction(2), Fraction(0)), (Fraction(1), Fraction(3), Fraction(1), Fraction(2)))
        self.assertEqual(distance, 1)

    def test_terminal_hold_participates_in_later_pair_checks(self):
        answer = self.compile({0: [11, 12], 1: [16, 17, 18]})
        self.assertTrue(answer['certified_nominal_reference'])
        duration = answer['profiles']['linear_one_cell']['duration_s']
        self.assertEqual(answer['schedule']['completion_s'], {0: duration, 1: 2*duration})
        self.assertEqual([r['kind'] for r in answer['schedule']['agents'][0]], ['MOVE', 'GOAL_HOLD'])
        self.assertEqual(answer['certificate']['checks']['pair_segments'], 2)
        rejected = self.compile({0: [12], 1: [7, 8]},
                                model=self.model(body_length_m='.8', body_width_m='.8'))
        self.assertEqual(rejected['reason']['kind'], 'CIRCLE_PAIR_SEPARATION_NOT_ESTABLISHED')

    def test_all_wait_slots_and_zero_step_completion_are_explicit(self):
        answer = self.compile({0: [12, 12, 13]})
        self.assertTrue(answer['certified_nominal_reference'])
        path = answer['schedule']['agents'][0]
        self.assertEqual([r['kind'] for r in path], ['WAIT', 'MOVE', 'GOAL_HOLD'])
        self.assertEqual(path[0]['end_s'], answer['profiles']['linear_one_cell']['duration_s'])
        idle = self.compile({0: [12], 1: [18]}, headings={0: 1, 1: 2})
        self.assertTrue(idle['certified_nominal_reference'])
        self.assertEqual(idle['schedule']['completion_s'], {0: 0.0, 1: 0.0})
        self.assertEqual(idle['schedule']['makespan_s'], 0.0)
        self.assertEqual(idle['certificate']['checks']['pair_segments'], 1)

    def test_bad_discrete_path_or_missing_heading_never_gets_certificate(self):
        for answer in (self.compile({0: [0, 6]}), self.compile({0: [12, 13]}, headings={})):
            self.assertEqual(answer['status'], 'REJECTED')
            self.assertFalse(answer['certified_nominal_reference'])
            self.assertIsNone(answer['schedule'])
        with self.assertRaises(ValueError):
            self.model(speed_m_s='0')

    def test_obstacle_broadphase_keeps_every_circle_intersection(self):
        # Exhaustive synthetic tiny grids; not a scientific task or optimizer.
        problem = self.Grid(7, 7, set(range(49))-{24, 25}, {0: (24, 25)})
        for values in ({}, {'body_length_m': '.8', 'body_width_m': '1.6'},
                       {'cell_m': '.3', 'body_length_m': '2', 'body_width_m': '.1'}):
            model = self.model(**values)
            for start, end in ((24, 25), (24, 24), (24, 17), (24, 23)):
                a = motion._point(start, problem.cols, model.cell_m)
                b = motion._point(end, problem.cols, model.cell_m)
                candidates = set(motion.obstacle_candidates(problem, a, b, model))
                for vertex in problem.blocked:
                    x, y = motion._point(vertex, problem.cols, model.cell_m)
                    half = model.cell_m/2
                    distance2 = motion.segment_box_distance_squared(a, b,
                        (x-half, x+half, y-half, y+half))
                    if distance2 <= model.body_circle_radius_squared:
                        self.assertIn(vertex, candidates)

    def test_fixed_quarter_slots_split_180_and_pad_with_zero_input_wait(self):
        path = {0: [11, 12]}
        legacy = self.compile(path, headings={0: 2})
        self.assertEqual([r['kind'] for r in legacy['schedule']['agents'][0]],
                         ['TURN', 'MOVE', 'GOAL_HOLD'])
        self.assertEqual(legacy['schedule']['agents'][0][0]['signed_quarters'], 2)
        fixed = self.compile(path, headings={0: 2}, turn_quarter_slot_s=4)
        self.assertTrue(fixed['certified_nominal_reference'])
        rows = fixed['schedule']['agents'][0]
        self.assertEqual([r['kind'] for r in rows],
                         ['TURN', 'WAIT', 'TURN', 'WAIT', 'MOVE', 'GOAL_HOLD'])
        self.assertEqual([rows[0]['signed_quarters'], rows[2]['signed_quarters']], [1, 1])
        self.assertEqual([rows[0]['heading_from_quarters'], rows[2]['heading_from_quarters']], [2, 3])
        self.assertEqual([rows[0]['heading_to_quarters'], rows[2]['heading_to_quarters']], [3, 0])
        for turn, padding in ((rows[0], rows[1]), (rows[2], rows[3])):
            self.assertAlmostEqual(turn['end_s']-turn['start_s'],
                                   fixed['profiles']['turn_1']['duration_s'])
            self.assertEqual(padding['reason'], 'TURN_SLOT_PADDING')
            self.assertTrue(padding['zero_input'])
            self.assertAlmostEqual(padding['end_s']-padding['start_s'],
                                   4-(turn['end_s']-turn['start_s']))
            self.assertEqual(padding['heading_quarters'], turn['heading_to_quarters'])
        self.assertAlmostEqual(rows[4]['start_s'], 8.0)
        self.assertEqual(fixed['construction']['turn_quarter_slot_s'], '4')
        self.assertTrue(fixed['construction']['split_180_into_two_90'])
        # A 90 degree robot fills its own slot, then waits for the 180 degree
        # robot's second slot; both still share one barrier before translation.
        pair = self.compile({0: [11, 12], 1: [16, 17]}, headings={0: 2, 1: 3},
                            turn_quarter_slot_s=4)
        other = pair['schedule']['agents'][1]
        self.assertEqual([r['kind'] for r in other],
                         ['TURN', 'WAIT', 'WAIT', 'MOVE', 'GOAL_HOLD'])
        self.assertEqual(other[1]['reason'], 'TURN_SLOT_PADDING')
        self.assertEqual(other[2]['reason'], 'TURN_BARRIER')
        self.assertAlmostEqual(other[2]['end_s'], 8.0)

    def test_radius_increment_horizon_coverage_and_nonnegative_validation(self):
        paths = {0: [11, 12], 1: [16, 17]}
        accepted = self.compile(paths, radius_increments=[{0: 0, 1: Fraction(1, 100)}])
        self.assertTrue(accepted['certified_nominal_reference'])
        self.assertTrue(accepted['construction']['radius_increments_applied'])
        self.assertEqual(accepted['construction']['maximum_radius_increment_m'], '1/100')
        # A zero-step task still has one global stationary/goal segment.
        idle = self.compile({0: [12], 1: [18]}, headings={0: 0, 1: 0},
                            radius_increments=[{0: 0, 1: 0}])
        self.assertTrue(idle['certified_nominal_reference'])
        for bad in ([], [{}], [{0: -1, 1: 0}], [{0: True, 1: 0}], [[0, 0]]):
            answer = self.compile(paths, radius_increments=bad)
            self.assertEqual(answer['status'], 'REJECTED')
            self.assertEqual(answer['reason']['kind'], 'INVALID_INPUT_OR_UNREPRESENTABLE_SCHEDULE')
            self.assertIsNone(answer['schedule'])

    def test_inflation_changes_obstacle_boundary_and_pair_sufficiency(self):
        model = self.model(body_length_m='.6', body_width_m='.2')
        obstacle = self.compile({0: [12, 13]}, blocked=[7], model=model)
        self.assertTrue(obstacle['certified_nominal_reference'])
        inflated_obstacle = self.compile({0: [12, 13]}, blocked=[7], model=model,
                                         radius_increments=[{0: Fraction(1, 5)}])
        self.assertEqual(inflated_obstacle['reason']['kind'],
                         'CIRCLE_OBSTACLE_SEPARATION_NOT_ESTABLISHED')
        boundary = self.compile({0: [0, 1]}, model=model)
        self.assertTrue(boundary['certified_nominal_reference'])
        inflated_boundary = self.compile({0: [0, 1]}, model=model,
                                         radius_increments=[{0: Fraction(1, 5)}])
        self.assertEqual(inflated_boundary['reason']['kind'],
                         'CIRCLE_MAP_CONTAINMENT_NOT_ESTABLISHED')
        # Same discrete crossing fixture: the nominal circle enclosures are
        # separated, while adding 0.05 m to each radius is not.
        pair_model = self.model(body_length_m='.45', body_width_m='.45')
        pair = self.compile({0: [6, 7], 1: [7, 12]}, model=pair_model)
        self.assertTrue(pair['certified_nominal_reference'])
        inflated_pair = self.compile({0: [6, 7], 1: [7, 12]}, model=pair_model,
                                     radius_increments=[{0: Fraction(1, 20),
                                                        1: Fraction(1, 20)}])
        self.assertEqual(inflated_pair['reason']['kind'],
                         'CIRCLE_PAIR_SEPARATION_NOT_ESTABLISHED')
        self.assertFalse(inflated_pair['certified_nominal_reference'])
        self.assertIsNone(inflated_pair['schedule'])

    def test_fixed_slot_and_body_radius_bound_are_validated(self):
        slow = self.model(turn_speed_rad_s='.2', turn_accel_rad_s2='.1',
                          turn_decel_rad_s2='.1')
        answer = self.compile({0: [11, 12]}, headings={0: 2}, model=slow,
                              turn_quarter_slot_s=4)
        self.assertEqual(answer['status'], 'REJECTED')
        self.assertIsNone(answer['schedule'])
        under = self.compile({0: [11, 12]}, body_radius_m='.1')
        self.assertEqual(under['status'], 'REJECTED')
        self.assertIsNone(under['schedule'])

    def test_analytic_profiles_are_rest_to_rest_and_share_monotone_progress(self):
        for distance in (.05, 2):
            p = motion.rest_to_rest_profile(distance, .5, 1, .8)
            self.assertLessEqual(p['peak_speed'], .5)
            self.assertAlmostEqual(p['accel_s']+p['cruise_s']+p['decel_s'], p['duration_s'])
            self.assertAlmostEqual(p['peak_speed']*p['accel_s']/2
                + p['peak_speed']*p['cruise_s']+p['peak_speed']*p['decel_s']/2, distance)
            samples = [motion.progress(p, t*p['duration_s']/20) for t in range(21)]
            self.assertEqual(samples, sorted(samples))
            self.assertEqual((samples[0], samples[-1]), (0, 1))
            for time in (p['accel_s'], p['accel_s']+p['cruise_s']):
                self.assertAlmostEqual(motion.progress(p, time-1e-8), motion.progress(p, time+1e-8), places=6)
        with self.assertRaises(ValueError):
            motion.progress(p, math.nan)


if __name__ == '__main__':
    unittest.main(verbosity=2)
