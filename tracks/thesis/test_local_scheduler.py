"""Handwritten synthetic software fixtures only; no frozen task is constructed."""
from fractions import Fraction as F
from pathlib import Path
from copy import deepcopy
import unittest
from unittest.mock import patch

import local_scheduler as local
import nominal_motion as motion
import plan_selection as selection


class LocalContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.Grid = selection.load_grid_problem(Path(__file__).resolve().parents[2])

    def model(self, **changes):
        values = dict(cell_m='1/2', body_length_m='11/50', body_width_m='4/25',
            speed_m_s='1/2', accel_m_s2='1/2', decel_m_s2='1/2',
            turn_speed_rad_s='1', turn_accel_rad_s2='1', turn_decel_rad_s2='1')
        values.update(changes)
        return motion.MotionModel(**values)

    def problem(self, paths, cols=5):
        return self.Grid(5, cols, [], {a: (p[0], p[-1]) for a, p in paths.items()})

    def test_primitive_physics_exact_endpoints_and_bounds(self):
        for distance, speed, accel, decel in [(F(1, 2), F(1, 2), F(1, 2), F(1, 2)),
                                               (F(1, 7), F(3), F(2), F(3))]:
            p = local.exact_profile(distance, speed, accel, decel)
            self.assertLessEqual(p['peak_speed'], speed)
            self.assertEqual(p['accel'], accel)
            self.assertEqual(p['decel'], decel)
            self.assertEqual(p['peak_speed']/p['accel_s'], accel)
            self.assertEqual(p['peak_speed']/p['decel_s'], decel)
            self.assertEqual(local.profile_position(p, 0), 0)
            self.assertEqual(local.profile_position(p, p['duration_s']), distance)
            self.assertEqual(p['peak_speed']*(p['accel_s']/2+p['cruise_s']+p['decel_s']/2), distance)
            self.assertEqual(p['peak_speed']-p['decel']*p['decel_s'], 0)
        paths = {0: [6, 7], 1: [16, 17]}
        schedule, reason = local.build_schedule(self.problem(paths), paths, self.model(),
                                                {0: 1, 1: 2}, 'local_dependency')
        self.assertIsNone(reason)
        turns = [a[0] for a in schedule['agents'].values()]
        self.assertEqual([a['signed_quarters'] for a in turns], [-1, 2])
        self.assertTrue(all(a['heading_to_quarters'] == 0 for a in turns))
        self.assertTrue(all('exactly' in a['angle_semantics'] for a in turns))

    def test_independent_turn_has_no_global_barrier_in_local_schedule(self):
        paths, headings = {0: [6, 11], 1: [16, 17]}, {0: 0, 1: 0}
        problem, model = self.problem(paths), self.model()
        global_plan, _ = local.build_schedule(problem, paths, model, headings, 'global_barrier')
        local_plan, reason = local.build_schedule(problem, paths, model, headings, 'local_dependency')
        self.assertIsNone(reason)
        self.assertEqual(local_plan['dependency_edges'], [])
        turn = F(global_plan['profiles']['turn_1']['duration_s'])
        self.assertEqual(F(local_plan['completion_exact_s'][1]), 2)
        self.assertEqual(F(global_plan['completion_exact_s'][1]), 2+turn)
        self.assertEqual(global_plan['agents'][1][0]['reason'], 'TURN_BARRIER')
        self.assertEqual(local_plan['agents'][1][0]['kind'], 'MOVE')
        self.assertFalse(local_plan['certified'])

    def test_following_must_wait_until_complete_predecessor_block(self):
        paths = {0: [6, 7], 1: [7, 8]}
        schedule, reason = local.build_schedule(self.problem(paths), paths, self.model(),
                                                {0: 0, 1: 0}, 'local_dependency')
        self.assertIsNone(reason)
        self.assertIn([[1, 0], [0, 0]], schedule['dependency_edges'])
        self.assertEqual(schedule['agents'][0][0]['reason'], 'LOCAL_DEPENDENCY')
        self.assertEqual(schedule['agents'][0][0]['start_exact_s'], '0')
        self.assertEqual(schedule['agents'][0][0]['end_exact_s'], '2')
        self.assertEqual(schedule['completion_exact_s'], {0: '4', 1: '2'})

    def test_discrete_wait_and_zero_step_permanent_goal_are_explicit(self):
        paths = {0: [6, 6, 7], 1: [18]}
        schedule, reason = local.build_schedule(self.problem(paths), paths, self.model(),
                                                {0: 0, 1: 0}, 'local_dependency')
        self.assertIsNone(reason)
        self.assertEqual(schedule['agents'][0][0]['reason'], 'DISCRETE_WAIT_SLOT')
        self.assertEqual(schedule['agents'][1][0]['kind'], 'GOAL_HOLD')
        self.assertIsNone(schedule['agents'][1][0]['end_exact_s'])
        self.assertEqual(schedule['completion_exact_s'][1], '0')

    def test_directed_grid_cycle_is_local_construction_failure(self):
        paths = {0: [6, 7], 1: [7, 12], 2: [12, 11], 3: [11, 6]}
        problem, model = self.problem(paths), self.model()
        headings = {0: 0, 1: 3, 2: 2, 3: 1}
        self.assertTrue(problem.validate(paths, complete=True))
        schedule, reason = local.build_schedule(problem, paths, model, headings, 'local_dependency')
        self.assertIsNone(schedule)
        self.assertEqual(reason['kind'], 'DEPENDENCY_CYCLE')
        global_plan, reason = local.build_schedule(problem, paths, model, headings, 'global_barrier')
        self.assertIsNone(reason)
        self.assertEqual(global_plan['completion_sum_s'], 8)

    def test_all_positive_fixtures_have_full_independent_continuous_certificate(self):
        fixtures = [{0: [6, 11], 1: [16, 17]}, {0: [6, 7], 1: [7, 8]},
                    {0: [6, 6, 7], 1: [18]},
                    {0: [6, 7], 1: [7, 12], 2: [12, 11], 3: [11, 6]}]
        for paths in fixtures:
            headings = {a: 0 for a in paths}
            for scheduler in local.SCHEDULERS:
                with self.subTest(paths=paths, scheduler=scheduler):
                    answer = local.compile_schedule(self.problem(paths), paths, self.model(), headings, scheduler)
                    if len(paths) == 4 and scheduler == 'local_dependency':
                        self.assertEqual(answer['reason']['kind'], 'DEPENDENCY_CYCLE')
                    else:
                        self.assertTrue(answer['certified_nominal_reference'], answer)
                        self.assertFalse(answer['certificate']['shared_q_proof_used'])
                        self.assertTrue(answer['certificate']['terminal_holds_permanent'])

    def test_shifted_clock_crossing_caught_between_clear_endpoints(self):
        p = local.exact_profile(F(1, 2), F(1, 2), F(1, 2), F(1, 2))
        profiles = {'linear_one_cell': p}
        a = local._action('MOVE', F(0), F(2), from_m=['-1/4', '0'], to_m=['1/4', '0'],
                          profile='linear_one_cell')
        b = local._action('MOVE', F(1, 4), F(9, 4), from_m=['0', '-1/4'], to_m=['0', '1/4'],
                          profile='linear_one_cell')
        for t in (F(1, 4), F(2)):
            pa, pb = local._position(a, t, profiles), local._position(b, t, profiles)
            self.assertGreater(sum((x-y)**2 for x, y in zip(pa, pb)), F(1, 100))
        passed, _, reason = local.pair_interval_check(a, b, F(1, 4), F(2), profiles, F(1, 100))
        self.assertFalse(passed)
        self.assertEqual(reason['kind'], 'CIRCLE_PAIR_SEPARATION_NOT_ESTABLISHED')
        self.assertFalse(reason['rectangular_collision_claim'])

    def test_wait_turn_and_goal_hold_are_not_released_at_motion_end(self):
        paths, headings = {0: [6, 6, 7], 1: [8, 7, 12]}, {0: 0, 1: 2}
        problem, model = self.problem(paths), self.model()
        safe, reason = local.build_schedule(problem, paths, model, headings, 'local_dependency')
        self.assertIsNone(reason)
        self.assertTrue(local.check_continuous(problem, paths, model, headings, safe)[0])
        # Deliberately remove one robot's dependency wait, keeping complete paths
        # and explicit occupancy. Its early arrival conflicts with the other's
        # TURN and then its infinite GOAL_HOLD conflicts with that robot's MOVE.
        broken = deepcopy(safe)
        first = broken['agents'][0]
        move = next(a for a in first if a['kind'] == 'MOVE')
        hold = first[-1]
        move.update(start_s=2.0, end_s=4.0, start_exact_s='2', end_exact_s='4')
        hold.update(start_s=4.0, start_exact_s='4')
        broken['agents'][0] = [first[0], move, hold]
        broken['completion_exact_s'][0] = '4'
        with self.assertRaisesRegex(ValueError, 'block times'):
            local.check_continuous(problem, paths, model, headings, broken)
        # Even a consistently rewritten block-time index cannot bypass order.
        next(r for r in broken['block_times'] if r['agent'] == 0 and r['step'] == 1).update(
            start_exact_s='2', end_exact_s='4')
        with self.assertRaisesRegex(ValueError, 'predecessor release'):
            local.check_continuous(problem, paths, model, headings, broken)
        profiles = {n: {k: F(v) for k, v in p.items()} for n, p in broken['profiles'].items()}
        other_turn = next(a for a in broken['agents'][1] if a['kind'] == 'TURN')
        self.assertFalse(local.pair_interval_check(move, other_turn, F(2), F(4), profiles,
                                                  4*model.body_circle_radius_squared)[0])
        other_move = [a for a in broken['agents'][1] if a['kind'] == 'MOVE'][-1]
        lo = F(other_move['start_exact_s'])
        hi = F(other_move['end_exact_s'])
        self.assertFalse(local.pair_interval_check(hold, other_move, lo, hi, profiles,
                                                  4*model.body_circle_radius_squared)[0])

    def test_missing_initial_wait_is_invalid_and_interval_budget_is_inconclusive(self):
        paths = {0: [6, 7], 1: [7, 8]}
        model, headings = self.model(), {0: 0, 1: 0}
        schedule, _ = local.build_schedule(self.problem(paths), paths, model, headings, 'local_dependency')
        del schedule['agents'][0][0]
        with self.assertRaisesRegex(ValueError, 'missing initial'):
            local.check_continuous(self.problem(paths), paths, model, headings, schedule)
        p = local.exact_profile(F(1, 2), F(1, 2), F(1, 2), F(1, 2))
        a = local._action('MOVE', F(0), F(2), from_m=['0', '0'], to_m=['1/2', '0'],
                          profile='linear_one_cell')
        b = local._action('MOVE', F(0), F(2), from_m=['1/2', '0'], to_m=['1', '0'],
                          profile='linear_one_cell')
        with patch.object(local, 'PAIR_MAX_DEPTH', 0):
            passed, _, reason = local.pair_interval_check(a, b, F(0), F(2),
                                                        {'linear_one_cell': p}, F(1, 100))
        self.assertFalse(passed)
        self.assertEqual(reason['kind'], 'CIRCLE_INTERVAL_SEPARATION_NOT_ESTABLISHED')
        with patch.object(local, 'PAIR_MAX_BOXES', 1):
            passed, boxes, _ = local.pair_interval_check(a, b, F(0), F(2),
                                                        {'linear_one_cell': p}, F(1, 100))
        self.assertFalse(passed)
        self.assertEqual(boxes, 1)

    def test_profile_order_and_display_corruption_are_not_certified(self):
        paths, headings = {0: [6, 7], 1: [7, 8]}, {0: 0, 1: 0}
        problem, model = self.problem(paths), self.model()
        schedule, _ = local.build_schedule(problem, paths, model, headings, 'local_dependency')
        for mutation, pattern in [
            (lambda p: next(a for a in p['agents'][1] if a['kind'] == 'MOVE').update(profile='turn_1'), 'primitive duration'),
            (lambda p: p.update(dependency_edges=[]), 'dependency order'),
            (lambda p: (p['completion_exact_s'].update({999: '-100'}),
                        p['completion_s'].update({999: -100.0}),
                        p.update(completion_sum_s=-94.0)), 'completion map agent coverage'),
            (lambda p: p.update(completion_sum_s=1.0), 'summary completion'),
            (lambda p: p['agents'][0][0].update(end_s=999.0), 'display action')]:
            broken = deepcopy(schedule)
            mutation(broken)
            with self.assertRaisesRegex(ValueError, pattern):
                local.check_continuous(problem, paths, model, headings, broken)


if __name__ == '__main__':
    unittest.main(verbosity=2)
