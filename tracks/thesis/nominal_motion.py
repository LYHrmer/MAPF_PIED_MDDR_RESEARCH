"""Sufficient continuous checks for an ideal, error-free barrier schedule.

All robots turn at fixed grid centres, then every moving robot shares ONE
normalised progress function. Bodies are the same declared rectangle, enclosed
by a circle. This is a conservative reference construction, not a controller,
an optimal scheduler, a v2 error certificate, or a scientific-run entry point.
"""
from dataclasses import dataclass, fields
from fractions import Fraction
import math


def positive(value, name):
    if isinstance(value, bool):
        raise ValueError(name+' must be a positive finite quantity')
    try:
        exact = Fraction(str(value))
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(name+' must be a positive finite quantity') from error
    if exact <= 0 or not math.isfinite(float(exact)):
        raise ValueError(name+' must be a positive finite quantity')
    return exact


@dataclass(frozen=True)
class MotionModel:
    """SI units; all parameters explicit, identical for every robot.

    The rectangle is centred at its reference point. Straight and rotational
    primitives start and finish at rest, with no translation during rotation.
    No uncertainty, tracking disturbance, localisation or feedback is assumed.
    """
    cell_m: Fraction
    body_length_m: Fraction
    body_width_m: Fraction
    speed_m_s: Fraction
    accel_m_s2: Fraction
    decel_m_s2: Fraction
    turn_speed_rad_s: Fraction
    turn_accel_rad_s2: Fraction
    turn_decel_rad_s2: Fraction

    def __post_init__(self):
        for field in fields(self):
            object.__setattr__(self, field.name, positive(getattr(self, field.name), field.name))

    def record(self):
        return {field.name: str(getattr(self, field.name)) for field in fields(self)}

    @property
    def body_circle_radius_squared(self):
        return (self.body_length_m**2+self.body_width_m**2)/4


def rest_to_rest_profile(distance, speed, accel, decel):
    """Asymmetric trapezoid (or triangle), with an analytic monotone position.

    Float times are numerical representations of this analytic construction.
    Safety checks below use exact spatial coefficients and do not sample them.
    """
    distance, speed, accel, decel = (float(positive(v, name)) for name, v in
        (('distance', distance), ('speed', speed), ('accel', accel), ('decel', decel)))
    peak = min(speed, math.sqrt(2*distance/(1/accel+1/decel)))
    ta, td = peak/accel, peak/decel
    da, dd = peak*ta/2, peak*td/2
    cruise = max(0.0, distance-da-dd)
    tc = cruise/peak
    total = ta+tc+td
    if not all(math.isfinite(v) and v >= 0 for v in (peak, ta, td, tc, total)) or total <= 0:
        raise ValueError('motion profile cannot be represented with finite positive duration')
    return {'distance': distance, 'speed_limit': speed, 'accel_limit': accel,
            'decel_limit': decel, 'peak_speed': peak, 'accel_s': ta, 'cruise_s': tc,
            'decel_s': td, 'duration_s': total, 'accel_distance': da,
            'kind': 'TRAPEZOID' if tc > 0 else 'TRIANGLE'}


def progress(profile, elapsed_s):
    """One common q in [0,1], also useful for reference visualisation.

    Do not evaluate independently shifted clocks for different moving robots.
    This floating-point helper is not the continuous safety check.
    """
    if not math.isfinite(elapsed_s):
        raise ValueError('finite reference time required')
    total = profile['duration_s']
    if elapsed_s <= 0:
        return 0.0
    if elapsed_s >= total:
        return 1.0
    if elapsed_s <= profile['accel_s']:
        distance = profile['accel_limit']*elapsed_s**2/2
    elif elapsed_s <= profile['accel_s']+profile['cruise_s']:
        distance = profile['accel_distance']+profile['peak_speed']*(elapsed_s-profile['accel_s'])
    else:
        distance = profile['distance']-profile['decel_limit']*(total-elapsed_s)**2/2
    return min(1.0, max(0.0, distance/profile['distance']))


def relative_minimum_squared(a0, a1, b0, b1):
    """Exact minimum ||a+q b||² for the SAME q in [0,1]."""
    a0, a1, b0, b1 = (tuple(Fraction(v) for v in point) for point in (a0, a1, b0, b1))
    a = tuple(x-y for x, y in zip(a0, b0))
    b = tuple((x1-x0)-(y1-y0) for x0, x1, y0, y1 in zip(a0, a1, b0, b1))
    norm = sum(x*x for x in b)
    q = max(Fraction(0), min(Fraction(1), -sum(x*y for x, y in zip(a, b))/norm)) if norm else Fraction(0)
    return sum((x+q*y)**2 for x, y in zip(a, b)), q


def interval_gap(a0, a1, b0, b1):
    return max(Fraction(0), b0-a1, a0-b1)


def segment_box_distance_squared(start, end, box):
    """Exact distance for an axis-aligned segment (including a point)."""
    if start[0] != end[0] and start[1] != end[1]:
        raise ValueError('axis-aligned segment required')
    return sum(interval_gap(min(start[i], end[i]), max(start[i], end[i]),
                            box[2*i], box[2*i+1])**2 for i in (0, 1))


def _point(vertex, cols, scale):
    # Explicit world coordinates: x right, y up; input grid rows increase down.
    return (vertex % cols*scale, -(vertex // cols)*scale)


def _point_record(point):
    return [str(v) for v in point]


def _heading(start, end):
    return {(1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}[
        tuple(0 if y == x else 1 if y > x else -1 for x, y in zip(start, end))]


def _turn(old, new):
    difference = (new-old) % 4
    return -1 if difference == 3 else difference  # pi tie is +pi (CCW).


def compile_motion(problem, paths, model, initial_headings):
    """Build a full nominal schedule or reject; never return a partial safe plan.

    `problem` is the shared SCI GridProblem, obtained through the existing fixed
    plan_selection.load_grid_problem reader. Each heading is an explicit cardinal
    quarter-turn: E=0,N=1,W=2,S=3. Every integer MAPF step receives one straight-slot
    duration, even if all active robots wait. A preceding turn barrier lasts as
    long as that step's slowest required rotation; others wait at fixed centres.

    Geometric certificate assumptions: exact ideal reference tracking, shared
    phase and barrier clocks, centre-aligned equal rectangular bodies, closed
    occupied grid squares, and the declared closed outer map. Rejected circle
    overlap is inconclusive about actual rectangular-body collision.
    """
    output = {'status': 'REJECTED', 'certified_nominal_reference': False,
              'scope': 'ERROR_FREE_SHARED_PHASE_BARRIER_REFERENCE',
              'schedule': None, 'contains_method_comparison': False,
              'error_model_applied': False, 'v2_qualification_claimed': False}
    try:
        if not isinstance(model, MotionModel):
            raise ValueError('explicit MotionModel required')
        normalized = {agent: tuple(path) for agent, path in paths.items()}
        if problem.validate(normalized, complete=True) is not True:
            raise ValueError('complete discrete validation must return True')
        if set(initial_headings) != set(normalized) or any(type(h) is not int or not 0 <= h < 4
                                                         for h in initial_headings.values()):
            raise ValueError('every robot requires an explicit cardinal initial heading')
        linear = rest_to_rest_profile(model.cell_m, model.speed_m_s, model.accel_m_s2, model.decel_m_s2)
        turns = {quarters: rest_to_rest_profile(quarters*math.pi/2, model.turn_speed_rad_s,
                  model.turn_accel_rad_s2, model.turn_decel_rad_s2) for quarters in (1, 2)}
        agents = tuple(problem.ids)
        count = max(len(p)-1 for p in normalized.values())
        scale, radius2 = model.cell_m, model.body_circle_radius_squared
        boundary = (-scale/2, (problem.cols-Fraction(1, 2))*scale,
                    -(problem.rows-Fraction(1, 2))*scale, scale/2)
        obstacles = {}
        for vertex in sorted(problem.blocked):
            x, y = _point(vertex, problem.cols, scale)
            obstacles[vertex] = (x-scale/2, x+scale/2, y-scale/2, y+scale/2)
        checks = {'pair_segments': 0, 'obstacle_segments': 0, 'map_boundary_segments': 0}
        # q=0 and q=1 are included, so this also checks every rotation/wait
        # barrier and final permanent hold. The zero-step case is checked once.
        for step in range(max(1, count)):
            segments = {a: (_point(normalized[a][min(step, len(normalized[a])-1)], problem.cols, scale),
                            _point(normalized[a][min(step+1, len(normalized[a])-1)], problem.cols, scale))
                        for a in agents}
            for a, (start, end) in segments.items():
                clearances = (min(start[0], end[0])-boundary[0], boundary[1]-max(start[0], end[0]),
                              min(start[1], end[1])-boundary[2], boundary[3]-max(start[1], end[1]))
                checks['map_boundary_segments'] += 1
                if any(gap <= 0 or gap*gap <= radius2 for gap in clearances):
                    output['reason'] = {'kind': 'CIRCLE_MAP_CONTAINMENT_NOT_ESTABLISHED', 'step': step,
                                        'agent': a, 'clearances_m': [str(v) for v in clearances]}
                    output['checks_attempted'] = checks
                    return output
                for obstacle, box in obstacles.items():
                    distance2 = segment_box_distance_squared(start, end, box)
                    checks['obstacle_segments'] += 1
                    if distance2 <= radius2:
                        output['reason'] = {'kind': 'CIRCLE_OBSTACLE_SEPARATION_NOT_ESTABLISHED', 'step': step,
                            'agent': a, 'obstacle': obstacle, 'distance_squared_m2': str(distance2),
                            'required_strictly_greater_than_m2': str(radius2)}
                        output['checks_attempted'] = checks
                        return output
            for index, a in enumerate(agents):
                for b in agents[index+1:]:
                    distance2, q = relative_minimum_squared(*segments[a], *segments[b])
                    checks['pair_segments'] += 1
                    if distance2 <= 4*radius2:
                        output['reason'] = {'kind': 'CIRCLE_PAIR_SEPARATION_NOT_ESTABLISHED', 'step': step,
                            'agents': [a, b], 'common_progress_at_minimum': str(q),
                            'distance_squared_m2': str(distance2),
                            'required_strictly_greater_than_m2': str(4*radius2)}
                        output['checks_attempted'] = checks
                        return output
        heading = dict(initial_headings)
        actions, completion = {a: [] for a in agents}, {}
        stages, clock = [], 0.0

        def append(a, kind, start, end, **extra):
            if not math.isfinite(start) or (end is not None and (not math.isfinite(end) or end <= start)):
                raise ValueError('action times cannot represent positive finite duration')
            actions[a].append(dict(kind=kind, start_s=start, end_s=end, **extra))

        def hold(a, when):
            completion[a] = when
            append(a, 'GOAL_HOLD', when, None, end_semantics='PERMANENT',
                   center_m=_point_record(_point(normalized[a][-1], problem.cols, scale)),
                   heading_quarters=heading[a])

        for a in agents:
            if len(normalized[a]) == 1:
                hold(a, 0.0)
        for step in range(count):
            old = {a: _point(normalized[a][min(step, len(normalized[a])-1)], problem.cols, scale) for a in agents}
            new = {a: _point(normalized[a][min(step+1, len(normalized[a])-1)], problem.cols, scale) for a in agents}
            moving = {a for a in agents if old[a] != new[a]}
            target = {a: _heading(old[a], new[a]) if a in moving else heading[a] for a in agents}
            rotations = {a: _turn(heading[a], target[a]) for a in agents}
            barrier = max((turns[abs(q)]['duration_s'] for q in rotations.values() if q), default=0.0)
            if barrier:
                stages.append({'step': step, 'kind': 'TURN_BARRIER', 'start_s': clock,
                               'end_s': clock+barrier, 'centres_fixed': True})
                for a in agents:
                    if a in completion:
                        continue
                    delta = rotations[a]
                    duration = turns[abs(delta)]['duration_s'] if delta else 0.0
                    if delta:
                        append(a, 'TURN', clock, clock+duration, center_m=_point_record(old[a]),
                               heading_from_quarters=heading[a], heading_to_quarters=target[a],
                               signed_quarters=delta, profile='turn_'+str(abs(delta)))
                    if duration < barrier:
                        append(a, 'WAIT', clock+duration, clock+barrier, center_m=_point_record(old[a]),
                               heading_quarters=target[a], reason='TURN_BARRIER')
                clock += barrier
            heading = target
            phase = 'step_'+str(step)+'_shared_move'
            finish = clock+linear['duration_s']
            if not math.isfinite(finish) or finish <= clock:
                raise ValueError('schedule times cannot represent a positive straight slot')
            stages.append({'step': step, 'kind': 'SHARED_MOVE_SLOT', 'start_s': clock, 'end_s': finish,
                           'profile': 'linear_one_cell', 'phase_id': phase,
                           'moving_agents': sorted(moving)})
            for a in agents:
                if a in completion:
                    continue
                if a in moving:
                    append(a, 'MOVE', clock, finish, from_m=_point_record(old[a]), to_m=_point_record(new[a]),
                           heading_quarters=heading[a], profile='linear_one_cell', phase_id=phase)
                else:
                    append(a, 'WAIT', clock, finish, center_m=_point_record(old[a]),
                           heading_quarters=heading[a], reason='DISCRETE_WAIT_SLOT')
                if step+1 == len(normalized[a])-1:
                    hold(a, finish)
            clock = finish
        if set(completion) != set(agents):
            raise ValueError('incomplete task completion/terminal hold')
        if not math.isfinite(sum(completion.values())):
            raise ValueError('completion sum cannot be represented finitely')
        output.update({'status': 'CERTIFIED_NOMINAL_REFERENCE', 'certified_nominal_reference': True,
            'model': model.record(), 'initial_headings_quarters': dict(initial_headings),
            'grid_problem_key': problem.model_key,
            'world_coordinates': 'x=column*cell_m; y=-row*cell_m; E/N/W/S=0/1/2/3 counterclockwise',
            'schedule': {'stages': stages, 'agents': actions, 'completion_s': completion,
                         'completion_sum_s': sum(completion.values()), 'makespan_s': clock},
            'profiles': dict(linear_one_cell=linear, **{'turn_'+str(k): v for k, v in turns.items()}),
            'certificate': {'arithmetic': 'EXACT_RATIONAL_GEOMETRY_NO_TIME_SAMPLING',
                'body_circle_radius_squared_m2': str(radius2), 'strict_separation': True,
                'checks': checks, 'every_step_and_all_robot_pairs_checked': True,
                'obstacles_are_closed_grid_squares': True, 'terminal_holds_permanent': True,
                'argument': 'The rectangle is inside its orientation-invariant circle. During turn/wait centres are fixed. During translation relative centres equal a+q*b for one shared q in [0,1]; the convex quadratic minimum and every axis-aligned segment/closed-obstacle distance are checked exactly. Endpoints cover all barriers and permanent terminal holds.',
                'conditions': ['Exact ideal tracking of these reference primitives; zero error only.',
                    'Moving robots share one physical progress value and every barrier start; no independent time shifts.',
                    'No continuous safety claim for different speed/turn/clock conditions or an actual feedback controller.',
                    'Printed float times/progress samples represent analytic profiles; they are not a verified floating-point controller.']}})
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as error:
        output.update({'reason': {'kind': 'INVALID_INPUT_OR_UNREPRESENTABLE_SCHEDULE',
                                  'detail': type(error).__name__+': '+str(error)}})
    return output
