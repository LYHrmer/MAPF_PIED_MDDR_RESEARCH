"""Minimal fixed-parameter v2 initial-pose-error reference pair.

The two arms share one declared motion model, one set of paths, one fixed
quarter-turn slot and one global barrier clock. The nominal arm uses zero pose
error; the error arm uses a fixed task-initial pose rectangle propagated by a
conservative L1 circle-radius increment that is never reset at waypoints. Only
sufficient circle-separation conditions are reported. Failure means those
conditions were not established, never that a collision occurred.

This is a conservative reference interface. It is not the SADG original method,
contains no rescheduling, and claims no algorithmic novelty or waiting benefit.
Static eligibility requires every path vertex to have absolute coordinate at
most 10 m and displacement at most 8 m from that robot's task-initial vertex on
each axis; each non-wait move is one grid edge with an independent stop.
"""
from fractions import Fraction

import nominal_motion as motion


CELL_M = Fraction(1)
TURN_QUARTER_SLOT_S = Fraction(4)
BODY_LENGTH_M = Fraction(3, 5)      # 0.6 m
BODY_WIDTH_M = Fraction(1, 5)       # 0.2 m
SPEED_M_S = Fraction(1, 2)          # 0.5 m/s
ACCEL_M_S2 = Fraction(1)
DECEL_M_S2 = Fraction(1)
TURN_SPEED_RAD_S = Fraction(1, 2)   # 0.5 rad/s
TURN_ACCEL_RAD_S2 = Fraction(1)
TURN_DECEL_RAD_S2 = Fraction(1)

INITIAL_POSE_BOUND_X_M = Fraction(1, 50)   # 0.02 m
INITIAL_POSE_BOUND_Y_M = Fraction(1, 100)  # 0.01 m
INITIAL_L1_RADIUS_M = INITIAL_POSE_BOUND_X_M+INITIAL_POSE_BOUND_Y_M
INITIAL_HEADING_BOUND_RAD = Fraction(1, 500)  # 0.002 radians; angle, not inverse metres
NUMERIC_MARGIN_M = Fraction(1, 10**6)      # 1e-6, added to both arms

ABSOLUTE_AXIS_LIMIT_M = Fraction(10)
INITIAL_DISPLACEMENT_LIMIT_M = Fraction(8)

V2_MODEL = motion.MotionModel(
    cell_m=CELL_M, body_length_m=BODY_LENGTH_M, body_width_m=BODY_WIDTH_M,
    speed_m_s=SPEED_M_S, accel_m_s2=ACCEL_M_S2, decel_m_s2=DECEL_M_S2,
    turn_speed_rad_s=TURN_SPEED_RAD_S, turn_accel_rad_s2=TURN_ACCEL_RAD_S2,
    turn_decel_rad_s2=TURN_DECEL_RAD_S2)
BODY_RADIUS_SQUARED_M2 = V2_MODEL.body_circle_radius_squared
# Exact rational ceiling at 1e-12, then the common numerical margin.
BODY_RADIUS_CEILING_M = motion.rational_sqrt_ceiling(BODY_RADIUS_SQUARED_M2)
SHARED_CIRCLE_RADIUS_M = BODY_RADIUS_CEILING_M+NUMERIC_MARGIN_M


def _horizon(paths):
    count = max(len(path)-1 for path in paths.values())
    return max(1, count)


def _point(vertex, cols, scale=CELL_M):
    return motion._point(vertex, cols, scale)


def static_qualification(problem, paths):
    """Check the complete paths before any continuous motion construction.

    Every path vertex must satisfy |x|<=10 m and |y|<=10 m, and every vertex
    must be within 8 m of that robot's own task-initial vertex on each axis.
    Repeated vertices are waits; every other consecutive pair must be one grid
    edge. The v2 model gives each such MOVE an independent rest-to-rest profile
    and gives waits no translation. No continuous claim is made here.
    """
    normalized = {agent: tuple(path) for agent, path in paths.items()}
    if problem.validate(normalized, complete=True) is not True:
        raise ValueError('complete discrete validation must return True')
    if set(normalized) != set(problem.ids):
        raise ValueError('paths must cover exactly the problem agents')
    violations, violation_count = [], 0

    def add(kind, agent, index, vertex, **extra):
        nonlocal violation_count
        violation_count += 1
        if len(violations) < 12:
            violations.append({'kind': kind, 'agent': agent, 'vertex_index': index,
                               'vertex': vertex, **extra})

    for agent in problem.ids:
        path = normalized[agent]
        x0, y0 = _point(path[0], problem.cols)
        for index, vertex in enumerate(path):
            x, y = _point(vertex, problem.cols)
            if abs(x) > ABSOLUTE_AXIS_LIMIT_M:
                add('ABSOLUTE_X_LIMIT', agent, index, vertex, axis='x', value_m=str(x),
                    inclusive_limit_m=str(ABSOLUTE_AXIS_LIMIT_M))
            if abs(y) > ABSOLUTE_AXIS_LIMIT_M:
                add('ABSOLUTE_Y_LIMIT', agent, index, vertex, axis='y', value_m=str(y),
                    inclusive_limit_m=str(ABSOLUTE_AXIS_LIMIT_M))
            if abs(x-x0) > INITIAL_DISPLACEMENT_LIMIT_M:
                add('INITIAL_X_DISPLACEMENT_LIMIT', agent, index, vertex, axis='x',
                    displacement_m=str(x-x0),
                    inclusive_limit_m=str(INITIAL_DISPLACEMENT_LIMIT_M))
            if abs(y-y0) > INITIAL_DISPLACEMENT_LIMIT_M:
                add('INITIAL_Y_DISPLACEMENT_LIMIT', agent, index, vertex, axis='y',
                    displacement_m=str(y-y0),
                    inclusive_limit_m=str(INITIAL_DISPLACEMENT_LIMIT_M))
        for index, (before, after) in enumerate(zip(path, path[1:])):
            if before == after:
                continue
            p, q = _point(before, problem.cols), _point(after, problem.cols)
            if abs(p[0]-q[0])+abs(p[1]-q[1]) != CELL_M:
                add('NON_SINGLE_CELL_MOVE', agent, index, before, next_vertex=after)
    return {'status': 'QUALIFIED' if violation_count == 0 else 'NOT_QUALIFIED',
            'qualified': violation_count == 0,
            'limits_m': {'absolute_each_axis_inclusive': str(ABSOLUTE_AXIS_LIMIT_M),
                         'initial_displacement_each_axis_inclusive':
                             str(INITIAL_DISPLACEMENT_LIMIT_M)},
            'violation_count': violation_count,
            'violations_truncated': violation_count > len(violations),
            'violations': violations,
            'static_properties': {
                'per_cell_move_rest_to_rest': True,
                'stationary_wait_has_no_translation': True,
                'turn_occurs_at_fixed_centre': True},
            'scope': 'STATIC_PATH_AND_MODEL_ELIGIBILITY_ONLY'}


def zero_radius_increments(problem, paths):
    """One zero increment per agent over the complete global horizon."""
    horizon = _horizon(paths)
    return [{agent: Fraction(0) for agent in problem.ids} for _ in range(horizon)]


def propagated_radius_increments(problem, paths):
    """Conservative fixed-initial-pose L1 radius increment per segment.

    For a whole-cell continuous segment,
        e = 0.03 + (Dx+Dy)*(h+h**2/2),
    where Dx and Dy are the largest absolute endpoint displacements from that
    robot's task-initial position on each axis. The 0.03 term is the L1 radius
    of the fixed initial rectangle (0.02, 0.01). Dx/Dy are relative to the task
    initial state, so no waypoint or action boundary resets the increment.
    """
    growth = INITIAL_HEADING_BOUND_RAD+INITIAL_HEADING_BOUND_RAD**2/2
    horizon = _horizon(paths)
    rows = []
    for step in range(horizon):
        row = {}
        for agent in problem.ids:
            path = paths[agent]
            first = _point(path[0], problem.cols)
            before = _point(path[min(step, len(path)-1)], problem.cols)
            after = _point(path[min(step+1, len(path)-1)], problem.cols)
            dx = max(abs(before[0]-first[0]), abs(after[0]-first[0]))
            dy = max(abs(before[1]-first[1]), abs(after[1]-first[1]))
            row[agent] = INITIAL_L1_RADIUS_M+(dx+dy)*growth
        rows.append(row)
    return rows


def reference_schedule_properties(answer):
    """Audit the constructed closed-form actions, not simulated execution."""
    schedule = answer.get('schedule')
    if schedule is None:
        return None
    properties = {'per_cell_move_rest_to_rest': True,
                  'wait_has_no_translation': True,
                  'turn_has_fixed_centre': True,
                  'terminal_hold_permanent': True}
    for actions in schedule['agents'].values():
        for action in actions:
            kind = action['kind']
            if kind == 'MOVE':
                before = [Fraction(v) for v in action['from_m']]
                after = [Fraction(v) for v in action['to_m']]
                if (action.get('profile') != 'linear_one_cell'
                        or abs(before[0]-after[0])+abs(before[1]-after[1]) != CELL_M):
                    properties['per_cell_move_rest_to_rest'] = False
            elif kind in ('WAIT', 'TURN'):
                if 'center_m' not in action:
                    key = ('wait_has_no_translation' if kind == 'WAIT'
                           else 'turn_has_fixed_centre')
                    properties[key] = False
                if kind == 'WAIT' and ('from_m' in action or 'to_m' in action):
                    properties['wait_has_no_translation'] = False
            elif kind == 'GOAL_HOLD' and action.get('end_s') is not None:
                properties['terminal_hold_permanent'] = False
    return properties


def compile_v2_pair(problem, paths, initial_headings):
    """Return the nominal and propagated-initial-pose full-task reference pair.

    Static eligibility is checked first. Both arms then receive the same fixed
    SI model, paths, headings, quarter-turn slot and rational body-radius upper
    bound plus 1e-6 m. Only the per-step radius increments differ: all zero for
    the nominal arm, the propagated L1 enclosure for the error arm. There is no
    rescheduling and no received common END: these are offline closed-form
    reference schedules. Under this identical input and barrier model the two
    arms therefore have identical reference times, so no waiting benefit is
    claimed.
    """
    output = {
        'scope': 'V2_FIXED_PARAMETER_INITIAL_POSE_ERROR_SUFFICIENT_CONDITIONS_ONLY',
        'model': V2_MODEL.record(),
        'fixed_parameters': {
            'cell_m': str(CELL_M), 'body_length_m': str(BODY_LENGTH_M),
            'body_width_m': str(BODY_WIDTH_M), 'speed_m_s': str(SPEED_M_S),
            'accel_m_s2': str(ACCEL_M_S2), 'decel_m_s2': str(DECEL_M_S2),
            'turn_speed_rad_s': str(TURN_SPEED_RAD_S),
            'turn_accel_rad_s2': str(TURN_ACCEL_RAD_S2),
            'turn_decel_rad_s2': str(TURN_DECEL_RAD_S2),
            'turn_quarter_slot_s': str(TURN_QUARTER_SLOT_S),
            'initial_pose_bound_m': {'x': str(INITIAL_POSE_BOUND_X_M),
                                     'y': str(INITIAL_POSE_BOUND_Y_M)},
            'initial_heading_bound_rad': str(INITIAL_HEADING_BOUND_RAD),
            'body_circle_radius_squared_m2': str(BODY_RADIUS_SQUARED_M2),
            'body_circle_radius_rational_ceiling_m': str(BODY_RADIUS_CEILING_M),
            'numeric_margin_m': str(NUMERIC_MARGIN_M),
            'shared_circle_radius_m': str(SHARED_CIRCLE_RADIUS_M),
            'orientation_error_handling':
                'ORIENTATION_INVARIANT_CIRCUMSCRIBED_BODY_CIRCLE',
            'initial_pose_state_persists_through_all_actions': True,
            'increment_reset_at_waypoints': False},
        'schedule_semantics': 'CLOSED_FORM_REFERENCE_SCHEDULE',
        'common_end_received': False,
        'both_arms_same_reference_time': None,
        'collision_claim': False,
        'rescheduling_performed': False,
        'waiting_benefit_claimed': False,
        'conditional_source_assumptions': [
            'For each robot one fixed b and delta satisfy p_true=p0+b+R(delta)(p_ref-p0) and theta_true=theta_ref+delta for the whole task.',
            'Actual/reference v and omega are identical; pause, resume and action switches share one clock.',
            'Every MOVE and quarter TURN starts/ends at rest; WAIT and permanent HOLD have zero drift.',
            'No persistent input error, slip, closed-loop correction or measured LIMO error bound is represented.'],
        'waiting_benefit_basis': 'Both arms use the same input, barrier model and '
            'closed-form reference schedule; only conservative separation radii differ.',
        'qualification': None, 'arms': None}
    try:
        qualification = static_qualification(problem, paths)
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as error:
        output.update({'status': 'REJECTED', 'certified_sufficient_conditions': False,
                       'reason': {'kind': 'INVALID_V2_INPUT',
                                  'detail': type(error).__name__+': '+str(error)}})
        return output
    output['qualification'] = qualification
    if not qualification['qualified']:
        output.update({'status': 'NOT_QUALIFIED', 'certified_sufficient_conditions': False,
                       'reason': {'kind': 'V2_STATIC_QUALIFICATION_FAILED',
                                  'violation_count': qualification['violation_count']}})
        return output
    try:
        nominal_increments = zero_radius_increments(problem, paths)
        error_increments = propagated_radius_increments(problem, paths)
        common = dict(turn_quarter_slot_s=TURN_QUARTER_SLOT_S,
                      body_radius_m=SHARED_CIRCLE_RADIUS_M)
        nominal = motion.compile_motion(problem, paths, V2_MODEL, initial_headings,
                                        radius_increments=nominal_increments, **common)
        propagated = motion.compile_motion(problem, paths, V2_MODEL, initial_headings,
                                           radius_increments=error_increments, **common)
        nominal.update({'v2_arm': 'ZERO_INITIAL_POSE_ERROR',
                        'v2_initial_pose_error_applied': False})
        propagated.update({'v2_arm': 'PROPAGATED_INITIAL_POSE_ERROR',
                           'v2_initial_pose_error_applied': True,
                           'error_model_applied': True})
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as error:
        output.update({'status': 'REJECTED', 'certified_sufficient_conditions': False,
                       'reason': {'kind': 'INVALID_V2_INPUT_OR_UNREPRESENTABLE_SCHEDULE',
                                  'detail': type(error).__name__+': '+str(error)}})
        return output
    output['arms'] = {'zero_initial_pose_error': nominal,
                      'propagated_initial_pose_error': propagated}
    nominal_ok = nominal['certified_nominal_reference'] is True
    propagated_ok = propagated['certified_nominal_reference'] is True
    same_schedule = (nominal['schedule'] is not None
                     and propagated['schedule'] is not None
                     and nominal['schedule'] == propagated['schedule'])
    output['both_arms_same_reference_schedule'] = same_schedule
    if nominal_ok and propagated_ok and same_schedule:
        schedule = nominal['schedule']
        output.update({'status': 'CERTIFIED_V2_PAIR',
                       'certified_sufficient_conditions': True,
                       'both_arms_same_reference_time': True,
                       'reference_completion_s': dict(schedule['completion_s']),
                       'reference_completion_sum_s': schedule['completion_sum_s'],
                       'reference_makespan_s': schedule['makespan_s'],
                       'schedule_properties': reference_schedule_properties(nominal)})
    elif nominal_ok and propagated_ok:
        output.update({'status': 'REJECTED', 'certified_sufficient_conditions': False,
                       'reason': {'kind': 'ARMS_DO_NOT_SHARE_REFERENCE_SCHEDULE'}})
    elif any((answer.get('reason') or {}).get('kind', '').startswith('CIRCLE_')
             for answer in (nominal, propagated)):
        output.update({'status': 'SUFFICIENT_SEPARATION_NOT_ESTABLISHED',
                       'certified_sufficient_conditions': False,
                       'reason': {'kind': 'AT_LEAST_ONE_ARM_SEPARATION_NOT_ESTABLISHED',
                                  'arm_reasons': {
                                      'zero_initial_pose_error': nominal.get('reason'),
                                      'propagated_initial_pose_error': propagated.get('reason')},
                                  'collision_claim': False}})
    else:
        output.update({'status': 'REJECTED', 'certified_sufficient_conditions': False,
                       'reason': {'kind': 'AT_LEAST_ONE_ARM_INVALID_OR_UNREPRESENTABLE',
                                  'arm_reasons': {
                                      'zero_initial_pose_error': nominal.get('reason'),
                                      'propagated_initial_pose_error': propagated.get('reason')}}})
    return output
