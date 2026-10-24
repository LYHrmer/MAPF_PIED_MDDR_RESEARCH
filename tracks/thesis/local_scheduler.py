"""Fixed-path scheduling controls, not the SADG implementation or a controller.

The global and local controls share exact rational primitive timing. Local
dependencies serialize overlapping complete action-block sweeps in the fixed
discrete visitation order. Initial/inter-block waiting and permanent goal holds
remain occupancy, so a dependency graph alone is NOT a geometric certificate.
"""
from fractions import Fraction as F
import heapq
import math

import nominal_motion as motion


PI_UPPER = F('3.141592653589793238462643383279503')
SQRT_DENOMINATOR = 10**12
SCHEDULERS = ('global_barrier', 'local_dependency')
PAIR_MAX_DEPTH = 16
PAIR_MAX_BOXES = 2048


def _poll(checkpoint):
    if checkpoint is not None:
        checkpoint()


def exact_profile(distance, speed, accel, decel):
    """Same rest-to-rest equations as nominal_motion, with a safe rational peak.

    If triangular, floor(sqrt(peak_squared)*10^12)/10^12 replaces the
    irrational peak. The resulting nonnegative cruise closes exactly the full
    displacement. Its speed and acceleration never exceed the supplied limits.
    """
    distance, speed, accel, decel = (motion.positive(v, name) for name, v in
        (('distance', distance), ('speed', speed), ('accel', accel), ('decel', decel)))
    peak2 = min(speed*speed, 2*distance/(1/accel+1/decel))
    if peak2 == speed*speed:
        peak = speed
    else:
        scaled = peak2.numerator*SQRT_DENOMINATOR**2//peak2.denominator
        peak = F(math.isqrt(scaled), SQRT_DENOMINATOR)
    if peak <= 0:
        raise ValueError('positive primitive peak is not representable')
    ta, td = peak/accel, peak/decel
    cruise_distance = distance-peak*(ta+td)/2
    tc = cruise_distance/peak
    if tc < 0:
        raise ValueError('negative primitive cruise')
    return dict(distance=distance, peak_speed=peak, accel=accel, decel=decel,
                accel_s=ta, cruise_s=tc, decel_s=td, duration_s=ta+tc+td)


def profile_position(profile, elapsed):
    """Exact monotone distance; not a time-sampled safety assertion."""
    t = max(F(0), min(F(elapsed), profile['duration_s']))
    if t <= profile['accel_s']:
        return profile['accel']*t*t/2
    if t <= profile['accel_s']+profile['cruise_s']:
        return (profile['peak_speed']*profile['accel_s']/2
                + profile['peak_speed']*(t-profile['accel_s']))
    return profile['distance']-profile['decel']*(profile['duration_s']-t)**2/2


def _profiles(model):
    # Only normalized angular progress is used: the REAL angle is k*pi/2,
    # never k*PI_UPPER/2. Scaling by real_angle/upper_angle <= 1 preserves all
    # angular limits and exact cardinal endpoints; circle occupancy is invariant.
    return dict(linear_one_cell=exact_profile(model.cell_m, model.speed_m_s,
                   model.accel_m_s2, model.decel_m_s2),
        **{'turn_'+str(k): exact_profile(k*PI_UPPER/2, model.turn_speed_rad_s,
                    model.turn_accel_rad_s2, model.turn_decel_rad_s2) for k in (1, 2)})


def _box(start, end):
    return (min(start[0], end[0]), max(start[0], end[0]),
            min(start[1], end[1]), max(start[1], end[1]))


def _box_distance2(a, b):
    return sum(motion.interval_gap(a[2*i], a[2*i+1], b[2*i], b[2*i+1])**2
               for i in (0, 1))


def make_blocks(problem, paths, model, headings, *, checkpoint=None):
    """One complete TURN+MOVE or discrete WAIT block per original grid step."""
    _poll(checkpoint)
    if not isinstance(model, motion.MotionModel):
        raise ValueError('explicit MotionModel required')
    paths = {a: tuple(p) for a, p in paths.items()}
    if problem.validate(paths, complete=True) is not True:
        raise ValueError('complete discrete validation must return True')
    if set(paths) != set(problem.ids) or set(headings) != set(paths) or any(
            type(h) is not int or h not in range(4) for h in headings.values()):
        raise ValueError('exact agent set and explicit cardinal initial headings required')
    profiles = _profiles(model)
    blocks = {}
    for a in problem.ids:
        _poll(checkpoint)
        heading = headings[a]
        for step, (u, v) in enumerate(zip(paths[a], paths[a][1:])):
            _poll(checkpoint)
            start = motion._point(u, problem.cols, model.cell_m)
            end = motion._point(v, problem.cols, model.cell_m)
            target = motion._heading(start, end) if u != v else heading
            turn = motion._turn(heading, target)
            rotation = profiles['turn_'+str(abs(turn))]['duration_s'] if turn else F(0)
            blocks[a, step] = dict(agent=a, step=step, u=u, v=v, start=start, end=end,
                heading_from=heading, heading_to=target, turn=turn, turn_s=rotation,
                duration_s=rotation+profiles['linear_one_cell']['duration_s'])
            heading = target
    return paths, profiles, blocks



def primitive_completion_lower_bound(problem, paths, model, headings, *, checkpoint=None):
    """Exact sum of solo action durations, including initial turns/discrete waits.

    For either existing scheduler each robot finishes no earlier than the sum
    of its own complete blocks. Dependency/barrier waiting is nonnegative, so
    this is a lower bound on sum of completion times, not a safety certificate.
    """
    _, _, blocks = make_blocks(problem, paths, model, headings, checkpoint=checkpoint)
    value = F(0)
    for block in blocks.values():
        _poll(checkpoint)
        value += block['duration_s']
    _poll(checkpoint)
    return value


def dependency_edges(blocks, radius2, *, checkpoint=None):
    """Conservative swept-circle order; no switching or order optimization.

    Each axis-aligned swept centre segment equals its box exactly. Overlapping
    swept circles trigger a dependency based on the original visit times at
    shared vertices. Geometry without an unambiguous discrete order is rejected.
    This serializes the whole block, not merely its waypoint or TURN completion.
    """
    _poll(checkpoint)
    edges = set()
    for key, block in blocks.items():
        _poll(checkpoint)
        if block['step']:
            edges.add(((block['agent'], block['step']-1), key))
    keys = list(blocks)
    for i, left in enumerate(keys):
        _poll(checkpoint)
        a = blocks[left]
        for right in keys[i+1:]:
            _poll(checkpoint)
            b = blocks[right]
            if a['agent'] == b['agent'] or _box_distance2(
                    _box(a['start'], a['end']), _box(b['start'], b['end'])) > 4*radius2:
                continue
            shared = {a['u'], a['v']} & {b['u'], b['v']}
            orders = set()
            for vertex in shared:
                _poll(checkpoint)
                at = [a['step']+j for j, v in enumerate((a['u'], a['v'])) if v == vertex]
                bt = [b['step']+j for j, v in enumerate((b['u'], b['v'])) if v == vertex]
                if max(at) < min(bt):
                    orders.add((left, right))
                elif max(bt) < min(at):
                    orders.add((right, left))
                else:
                    return None, dict(kind='DEPENDENCY_ORDER_NOT_ESTABLISHED', blocks=[left, right])
            if len(orders) == 1:
                edges.update(orders)
            else:
                return None, dict(kind='DEPENDENCY_ORDER_NOT_ESTABLISHED', blocks=[left, right],
                                  detail='Overlapping sweeps lack a unique original visit order.')
    return edges, None


def earliest_starts(blocks, edges, *, checkpoint=None):
    """Longest-path release times for this finite DAG; a cycle is local failure."""
    _poll(checkpoint)
    successors = {key: [] for key in blocks}
    degree = {key: 0 for key in blocks}
    starts = {key: F(0) for key in blocks}
    for source, target in edges:
        _poll(checkpoint)
        if source not in blocks or target not in blocks:
            raise ValueError('dependency refers to a missing complete action block')
        successors[source].append(target)
        degree[target] += 1
    ready = [key for key, count in degree.items() if not count]
    heapq.heapify(ready)
    completed = []
    while ready:
        _poll(checkpoint)
        key = heapq.heappop(ready)
        completed.append(key)
        finish = starts[key]+blocks[key]['duration_s']
        for other in successors[key]:
            _poll(checkpoint)
            starts[other] = max(starts[other], finish)
            degree[other] -= 1
            if degree[other] == 0:
                heapq.heappush(ready, other)
    if len(completed) != len(blocks):
        return None, dict(kind='DEPENDENCY_CYCLE', unresolved_blocks=[k for k, n in degree.items() if n],
                          meaning='This conservative local construction is infeasible; other schedules may exist.')
    return starts, None


def _action(kind, start, end, **values):
    if start < 0 or (end is not None and end <= start):
        raise ValueError('non-positive or negative action time')
    return dict(kind=kind, start_s=float(start), end_s=None if end is None else float(end),
                start_exact_s=str(start), end_exact_s=None if end is None else str(end), **values)


def build_schedule(problem, paths, model, headings, scheduler, *, checkpoint=None):
    """Construct a full candidate. Certification is a separate obligatory step."""
    _poll(checkpoint)
    if scheduler not in SCHEDULERS:
        raise ValueError('unknown scheduler')
    paths, profiles, blocks = make_blocks(problem, paths, model, headings, checkpoint=checkpoint)
    edges = set()
    if scheduler == 'local_dependency':
        edges, reason = dependency_edges(blocks, model.body_circle_radius_squared, checkpoint=checkpoint)
        if reason:
            return None, reason
        starts, reason = earliest_starts(blocks, edges, checkpoint=checkpoint)
        if reason:
            return None, reason
    else:
        starts, clock = {}, F(0)
        for step in range(max((len(p)-1 for p in paths.values()), default=0)):
            _poll(checkpoint)
            current = [key for key in blocks if key[1] == step]
            barrier = max((blocks[key]['turn_s'] for key in current), default=F(0))
            for key in current:
                _poll(checkpoint)
                starts[key] = clock
                blocks[key]['barrier_padding_s'] = barrier-blocks[key]['turn_s']
            clock += barrier+profiles['linear_one_cell']['duration_s']
    actions, completion = {}, {}
    for a in problem.ids:
        _poll(checkpoint)
        sequence, clock, heading = [], F(0), headings[a]
        for step in range(len(paths[a])-1):
            _poll(checkpoint)
            block, begin = blocks[a, step], starts[a, step]
            center = motion._point_record(block['start'])
            if begin < clock:
                raise ValueError('overlapping own action blocks')
            if begin > clock:
                sequence.append(_action('WAIT', clock, begin, center_m=center,
                                        reason='LOCAL_DEPENDENCY', heading_quarters=heading))
            clock = begin
            if block['turn']:
                finish = clock+block['turn_s']
                sequence.append(_action('TURN', clock, finish, center_m=center,
                    heading_from_quarters=heading, heading_to_quarters=block['heading_to'],
                    signed_quarters=block['turn'], profile='turn_'+str(abs(block['turn'])),
                    angle_semantics='signed_quarters*pi/2 exactly; normalized PI_UPPER profile'))
                clock = finish
            heading = block['heading_to']
            padding = block.get('barrier_padding_s', F(0))
            if padding:
                sequence.append(_action('WAIT', clock, clock+padding, center_m=center,
                                        reason='TURN_BARRIER', heading_quarters=heading))
                clock += padding
            finish = clock+profiles['linear_one_cell']['duration_s']
            if block['u'] == block['v']:
                sequence.append(_action('WAIT', clock, finish, center_m=center,
                                        reason='DISCRETE_WAIT_SLOT', heading_quarters=heading))
            else:
                sequence.append(_action('MOVE', clock, finish, from_m=center,
                    to_m=motion._point_record(block['end']), heading_quarters=heading,
                    profile='linear_one_cell'))
            clock = finish
        completion[a] = clock
        sequence.append(_action('GOAL_HOLD', clock, None,
            center_m=motion._point_record(motion._point(paths[a][-1], problem.cols, model.cell_m)),
            heading_quarters=heading, end_semantics='PERMANENT'))
        actions[a] = sequence
    return dict(scheduler=scheduler, agents=actions, completion_s={a: float(t) for a, t in completion.items()},
        completion_exact_s={a: str(t) for a, t in completion.items()},
        completion_sum_s=float(sum(completion.values(), F(0))),
        makespan_s=float(max(completion.values(), default=F(0))),
        dependency_edges=[[list(a), list(b)] for a, b in sorted(edges)],
        block_times=[dict(agent=a, step=step, start_exact_s=str(starts[a, step]),
                          end_exact_s=str(starts[a, step]+block['duration_s']
                                          +block.get('barrier_padding_s', F(0))))
                     for (a, step), block in sorted(blocks.items())],
        profiles={name: {k: str(v) for k, v in p.items()} for name, p in profiles.items()},
        timing='RATIONAL_REST_TO_REST_COMMON_TO_BOTH_SCHEDULERS',
        certified=False, common_end_received=False), None


def _position(action, when, profiles):
    if action['kind'] != 'MOVE':
        return tuple(F(v) for v in action['center_m'])
    start, end = (tuple(F(v) for v in action[name]) for name in ('from_m', 'to_m'))
    p = profiles[action['profile']]
    q = profile_position(p, when-F(action['start_exact_s']))/p['distance']
    return tuple(x+q*(y-x) for x, y in zip(start, end))


def pair_interval_check(a, b, left, right, profiles, required2, *, checkpoint=None):
    """Prove a whole time interval by exact monotone position enclosures.

    Each action has its OWN start clock and progress. On [l,r], monotonicity
    encloses its complete centre trajectory in the box of its endpoint positions.
    Positive box separation certifies every instant. Otherwise bisect the closed
    interval. An exact midpoint circle overlap is an inconclusive body-collision
    result, not a safety sample. Acceptance NEVER relies on point samples.
    """
    _poll(checkpoint)
    stack, tested = [(left, right, 0)], 0
    while stack:
        _poll(checkpoint)
        if tested >= PAIR_MAX_BOXES:
            lo, hi, _ = stack[-1]
            return False, tested, dict(kind='CIRCLE_INTERVAL_SEPARATION_NOT_ESTABLISHED',
                unresolved_closed_interval_s=[str(lo), str(hi)],
                reason='Fixed interval box budget exhausted before processing this interval.')
        lo, hi, depth = stack.pop()
        tested += 1
        ap, aq = _position(a, lo, profiles), _position(a, hi, profiles)
        bp, bq = _position(b, lo, profiles), _position(b, hi, profiles)
        lower = _box_distance2(_box(ap, aq), _box(bp, bq))
        if lower > required2:
            continue
        middle = (lo+hi)/2
        ma, mb = _position(a, middle, profiles), _position(b, middle, profiles)
        distance2 = sum((x-y)**2 for x, y in zip(ma, mb))
        if distance2 <= required2:
            return False, tested, dict(kind='CIRCLE_PAIR_SEPARATION_NOT_ESTABLISHED',
                exact_circle_overlap_time_s=str(middle), distance_squared_m2=str(distance2),
                rectangular_collision_claim=False)
        if depth >= PAIR_MAX_DEPTH or lo == hi:
            return False, tested, dict(kind='CIRCLE_INTERVAL_SEPARATION_NOT_ESTABLISHED',
                unresolved_closed_interval_s=[str(lo), str(hi)],
                interval_lower_squared_m2=str(lower),
                reason='Fixed interval proof budget exhausted; no safety inference from samples.')
        stack.extend(((middle, hi, depth+1), (lo, middle, depth+1)))
    return True, tested, None


def check_continuous(problem, paths, model, headings, schedule, *, checkpoint=None):
    """Full nominal occupancy, including every turn/wait and infinite goal tail."""
    _poll(checkpoint)
    profiles = {name: {k: F(v) for k, v in p.items()} for name, p in schedule['profiles'].items()}
    if profiles != _profiles(model):
        raise ValueError('schedule profiles differ from the declared common primitive model')
    if set(schedule['agents']) != set(problem.ids):
        raise ValueError('schedule agent coverage differs from the complete problem')
    if (set(schedule['completion_exact_s']) != set(problem.ids)
            or set(schedule['completion_s']) != set(problem.ids)
            or any(F(t) < 0 for t in schedule['completion_exact_s'].values())):
        raise ValueError('completion map agent coverage or nonnegative times invalid')
    radius2 = model.body_circle_radius_squared
    scale = model.cell_m
    boundary = (-scale/2, (problem.cols-F(1, 2))*scale,
                -(problem.rows-F(1, 2))*scale, scale/2)
    checks = dict(actions=0, obstacle_segments=0, map_boundary_segments=0,
                  pair_action_intersections=0, rational_interval_boxes=0)
    actual_blocks = {}
    # Validate completeness before any geometric early return. This is also what
    # makes advancing both cursors at a shared endpoint valid below: positions
    # are continuous, so both incident actions have the same endpoint occupancy.
    for a in problem.ids:
        _poll(checkpoint)
        sequence = schedule['agents'][a]
        clock, position, heading = F(0), motion._point(paths[a][0], problem.cols, scale), headings[a]
        executed_path, turn_pending, block_begin, step = [position], False, None, 0
        for index, action in enumerate(sequence):
            _poll(checkpoint)
            checks['actions'] += 1
            begin = F(action['start_exact_s'])
            end = None if action['end_exact_s'] is None else F(action['end_exact_s'])
            if (action['start_s'] != float(begin)
                    or action['end_s'] != (None if end is None else float(end))):
                raise ValueError('display action times differ from exact schedule')
            if begin != clock or _position(action, begin, profiles) != position:
                raise ValueError('missing initial/inter-action occupancy or discontinuous action')
            if end is not None and end <= begin:
                raise ValueError('non-positive action duration')
            kind = action['kind']
            if kind in ('TURN', 'MOVE') or (kind == 'WAIT' and action['reason'] != 'LOCAL_DEPENDENCY'):
                if block_begin is None:
                    block_begin = begin
            if kind == 'GOAL_HOLD':
                if (index != len(sequence)-1 or end is not None
                        or position != motion._point(paths[a][-1], problem.cols, scale)
                        or str(clock) != schedule['completion_exact_s'][a]
                        or action['heading_quarters'] != heading):
                    raise ValueError('missing permanent terminal hold or incorrect completion')
            elif end is None or index == len(sequence)-1:
                raise ValueError('nonterminal action must finish before permanent goal hold')
            elif kind == 'TURN':
                if (action['heading_from_quarters'] != heading
                        or (heading+action['signed_quarters']) % 4 != action['heading_to_quarters']
                        or action['signed_quarters'] not in (-1, 1, 2)
                        or action['profile'] != 'turn_'+str(abs(action['signed_quarters']))
                        or end-begin != profiles['turn_'+str(abs(action['signed_quarters']))]['duration_s']):
                    raise ValueError('turn heading or primitive duration mismatch')
                heading = action['heading_to_quarters']
                turn_pending = True
            elif kind == 'MOVE':
                target = tuple(F(v) for v in action['to_m'])
                if (sum(abs(x-y) for x, y in zip(position, target)) != scale
                        or (position[0] != target[0] and position[1] != target[1])
                        or action['profile'] != 'linear_one_cell'
                        or motion._heading(position, target) != heading
                        or action['heading_quarters'] != heading
                        or end-begin != profiles['linear_one_cell']['duration_s']
                        or _position(action, end, profiles) != target):
                    raise ValueError('move displacement, heading or primitive duration mismatch')
                executed_path.append(target)
                position, turn_pending = target, False
            elif kind == 'WAIT':
                if action['reason'] not in ('DISCRETE_WAIT_SLOT', 'TURN_BARRIER', 'LOCAL_DEPENDENCY'):
                    raise ValueError('unknown wait semantics')
                if action['heading_quarters'] != heading:
                    raise ValueError('wait changes heading')
                if action['reason'] == 'LOCAL_DEPENDENCY' and block_begin is not None:
                    raise ValueError('dependency WAIT inserted inside an action block')
                if action['reason'] == 'DISCRETE_WAIT_SLOT':
                    if end-begin != profiles['linear_one_cell']['duration_s']:
                        raise ValueError('discrete WAIT lost its complete movement slot')
                    executed_path.append(position)
            else:
                raise ValueError('unknown motion action')
            if kind == 'MOVE' or (kind == 'WAIT' and action['reason'] == 'DISCRETE_WAIT_SLOT'):
                actual_blocks[a, step] = (block_begin, end)
                block_begin, step = None, step+1
            if end is not None:
                clock = end
        if (executed_path != [motion._point(v, problem.cols, scale) for v in paths[a]]
                or turn_pending or not sequence or sequence[-1]['kind'] != 'GOAL_HOLD'):
            raise ValueError('schedule does not cover the full supplied discrete path')
    _, _, expected_blocks = make_blocks(problem, paths, model, headings, checkpoint=checkpoint)
    if set(actual_blocks) != set(expected_blocks):
        raise ValueError('complete action block coverage mismatch')
    recorded_blocks = {(r['agent'], r['step']): (F(r['start_exact_s']), F(r['end_exact_s']))
                       for r in schedule['block_times']}
    if len(recorded_blocks) != len(schedule['block_times']) or recorded_blocks != actual_blocks:
        raise ValueError('recorded action block times differ from complete actions')
    scheduler = schedule['scheduler']
    if scheduler == 'local_dependency':
        expected_edges, failure = dependency_edges(expected_blocks, radius2, checkpoint=checkpoint)
        if failure is not None:
            raise ValueError('local dependency order could not be established')
        actual_edges = {(tuple(a), tuple(b)) for a, b in schedule['dependency_edges']}
        if expected_edges != actual_edges:
            raise ValueError('fixed discrete dependency order changed')
        if any(actual_blocks[a][1] > actual_blocks[b][0] for a, b in expected_edges):
            raise ValueError('action starts before complete predecessor release')
        if any(end-begin != expected_blocks[key]['duration_s'] for key, (begin, end) in actual_blocks.items()):
            raise ValueError('local complete block timing mismatch')
    elif scheduler == 'global_barrier':
        clock = F(0)
        if schedule['dependency_edges']:
            raise ValueError('unexpected dependencies in global control')
        for step in range(max((len(p)-1 for p in paths.values()), default=0)):
            _poll(checkpoint)
            current = [key for key in expected_blocks if key[1] == step]
            duration = max((expected_blocks[k]['turn_s'] for k in current), default=F(0))
            duration += profiles['linear_one_cell']['duration_s']
            if any(actual_blocks[k] != (clock, clock+duration) for k in current):
                raise ValueError('global barrier block timing mismatch')
            clock += duration
    else:
        raise ValueError('unknown schedule mode')
    exact_completions = {a: F(t) for a, t in schedule['completion_exact_s'].items()}
    if (schedule['completion_s'] != {a: float(t) for a, t in exact_completions.items()}
            or schedule['completion_sum_s'] != float(sum(exact_completions.values(), F(0)))
            or schedule['makespan_s'] != float(max(exact_completions.values(), default=F(0)))):
        raise ValueError('summary completion costs differ from exact schedule')
    for a, sequence in schedule['agents'].items():
        _poll(checkpoint)
        for index, action in enumerate(sequence):
            _poll(checkpoint)
            start = _position(action, F(action['start_exact_s']), profiles)
            end = (tuple(F(v) for v in action['to_m']) if action['kind'] == 'MOVE' else start)
            clearances = (min(start[0], end[0])-boundary[0], boundary[1]-max(start[0], end[0]),
                          min(start[1], end[1])-boundary[2], boundary[3]-max(start[1], end[1]))
            checks['map_boundary_segments'] += 1
            if any(g <= 0 or g*g <= radius2 for g in clearances):
                return False, dict(kind='CIRCLE_MAP_CONTAINMENT_NOT_ESTABLISHED', agent=a, action=index), checks
            for obstacle in motion.obstacle_candidates(problem, start, end, model):
                _poll(checkpoint)
                x, y = motion._point(obstacle, problem.cols, scale)
                box = (x-scale/2, x+scale/2, y-scale/2, y+scale/2)
                checks['obstacle_segments'] += 1
                if motion.segment_box_distance_squared(start, end, box) <= radius2:
                    return False, dict(kind='CIRCLE_OBSTACLE_SEPARATION_NOT_ESTABLISHED',
                                       agent=a, action=index, obstacle=obstacle), checks
    horizon = max((F(t) for t in schedule['completion_exact_s'].values()), default=F(0))
    agents = tuple(problem.ids)
    for offset, a in enumerate(agents):
        _poll(checkpoint)
        for b in agents[offset+1:]:
            _poll(checkpoint)
            aa, bb, i, j = schedule['agents'][a], schedule['agents'][b], 0, 0
            while i < len(aa) and j < len(bb):
                _poll(checkpoint)
                one, two = aa[i], bb[j]
                end_a = horizon if one['end_exact_s'] is None else F(one['end_exact_s'])
                end_b = horizon if two['end_exact_s'] is None else F(two['end_exact_s'])
                lo = max(F(one['start_exact_s']), F(two['start_exact_s']))
                hi = min(end_a, end_b)
                if lo <= hi:
                    checks['pair_action_intersections'] += 1
                    passed, count, reason = pair_interval_check(one, two, lo, hi, profiles, 4*radius2, checkpoint=checkpoint)
                    checks['rational_interval_boxes'] += count
                    if not passed:
                        reason.update(agents=[a, b], action_indices=[i, j],
                                      action_kinds=[one['kind'], two['kind']])
                        return False, reason, checks
                if end_a <= end_b:
                    i += 1
                if end_b <= end_a:
                    j += 1
            # Both centres remain at these points forever after the horizon.
            final_a, final_b = (_position(seq[-1], horizon, profiles) for seq in (aa, bb))
            if sum((x-y)**2 for x, y in zip(final_a, final_b)) <= 4*radius2:
                return False, dict(kind='CIRCLE_PERMANENT_GOAL_SEPARATION_NOT_ESTABLISHED', agents=[a, b]), checks
    return True, None, checks


def compile_schedule(problem, paths, model, headings, scheduler, *, checkpoint=None):
    """Return a complete certified reference or an explicit retained rejection."""
    _poll(checkpoint)
    output = dict(status='REJECTED', certified_nominal_reference=False, schedule=None,
        scope='ERROR_FREE_FIXED_PATH_'+scheduler.upper(), error_model_applied=False,
        v2_qualification_claimed=False, common_end_received=False,
        author_sadg_reproduction=False, collision_claim=False)
    try:
        schedule, reason = build_schedule(problem, paths, model, headings, scheduler, checkpoint=checkpoint)
        if reason is None:
            passed, reason, checks = check_continuous(problem, paths, model, headings, schedule, checkpoint=checkpoint)
            output['checks_attempted'] = checks
            if passed:
                schedule['certified'] = True
                output.update(status='CERTIFIED_NOMINAL_REFERENCE', certified_nominal_reference=True,
                    schedule=schedule, model=model.record(), initial_headings_quarters=dict(headings),
                    certificate=dict(arithmetic='EXACT_RATIONAL_MONOTONE_INTERVAL_ENCLOSURES',
                        pair_max_depth=PAIR_MAX_DEPTH, pair_max_boxes=PAIR_MAX_BOXES,
                        every_time_interval_and_robot_pair_covered=True,
                        initial_and_inter_block_waits_checked=True, terminal_holds_permanent=True,
                        body_circle_radius_squared_m2=str(model.body_circle_radius_squared),
                        independent_progress=True, shared_q_proof_used=False,
                        conditions=['Exact nominal reference with its own declared action clocks.',
                                    'No tracking disturbance, feedback delay or v2 uncertainty.',
                                    'Circle overlap or proof-budget exhaustion establishes no body collision.',
                                    'Rational strings define timing; floats are display/metrics only.']))
                return output
        output['reason'] = reason
        if schedule is not None:
            output['uncertified_candidate'] = schedule
    except (ValueError, TypeError, KeyError, OverflowError, ZeroDivisionError) as error:
        output['reason'] = dict(kind='INVALID_INPUT_OR_UNREPRESENTABLE_SCHEDULE', detail=str(error))
    return output
