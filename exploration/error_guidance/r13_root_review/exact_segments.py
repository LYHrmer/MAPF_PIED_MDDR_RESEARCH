"""Independent exact collision audit of piecewise affine disc trajectories.

No simulator imports. Spatial indexing is only a conservative broad phase: each
segment's entire axis-aligned spatial box is enlarged by the robot radius.
Every possible overlapping pair of discs must share a bucket. Candidate pairs
are then checked over their complete closed time overlap with exact fractions.
"""
from collections import defaultdict
from fractions import Fraction as F
from math import floor


def q(value):
    if isinstance(value, float):
        raise ValueError('Use recorded exact fractions, not binary float times')
    return F(value)


def point(segment, t):
    alpha = (t - segment['a']) / (segment['b'] - segment['a'])
    return tuple(x + alpha * (y - x) for x, y in zip(segment['p'], segment['z']))


def minimum_squared(left, right):
    """Exact minimum squared centre distance on a closed overlapping interval."""
    a, b = max(left['a'], right['a']), min(left['b'], right['b'])
    if a > b:
        return None
    lp, rp = point(left, a), point(right, a)
    d = tuple(x - y for x, y in zip(lp, rp))
    lv = tuple((z - p) / (left['b'] - left['a']) for p, z in zip(left['p'], left['z']))
    rv = tuple((z - p) / (right['b'] - right['a']) for p, z in zip(right['p'], right['z']))
    v = tuple(x - y for x, y in zip(lv, rv))
    vv = sum(x * x for x in v)
    dt = max(F(0), min(b - a, -sum(x * y for x, y in zip(d, v)) / vv)) if vv else F(0)
    return sum((x + dt * y) ** 2 for x, y in zip(d, v)), a + dt


def audit(segments, makespan, agents, radius='1/10'):
    horizon, rad = q(makespan), q(radius)
    assert horizon > 0 and rad > 0
    paths = defaultdict(list)
    records = []
    buckets = defaultdict(list)
    for sid, item in enumerate(segments):
        record = {'id': sid, 'agent': item['agent'], 'a': q(item['t0']), 'b': q(item['t1']),
                  'p': tuple(map(q, item['p0'])), 'z': tuple(map(q, item['p1']))}
        assert len(record['p']) == len(record['z']) == 2
        assert 0 <= record['a'] < record['b'] <= horizon, item
        paths[record['agent']].append(record)
        records.append(record)
        lower = [floor(min(x, y) - rad) for x, y in zip(record['p'], record['z'])]
        upper = [floor(max(x, y) + rad) for x, y in zip(record['p'], record['z'])]
        for x in range(lower[0], upper[0] + 1):
            for y in range(lower[1], upper[1] + 1):
                buckets[x, y].append(record)
    assert set(paths) == set(range(agents)), 'Missing agent trajectory'
    for agent, row in paths.items():
        row.sort(key=lambda s: (s['a'], s['b']))
        assert row[0]['a'] == 0 and row[-1]['b'] == horizon, ('coverage', agent)
        for before, after in zip(row, row[1:]):
            assert before['b'] == after['a'], ('gap or overlap', agent)
            assert before['z'] == after['p'], ('position discontinuity', agent)
    seen = set()
    threshold = (2 * rad) ** 2
    nearest = None
    for row in buckets.values():
        row.sort(key=lambda s: (s['a'], s['b'], s['id']))
        active = []
        for current in row:
            active = [s for s in active if s['b'] >= current['a']]
            for prior in active:
                if prior['agent'] == current['agent']:
                    continue
                pair = tuple(sorted((prior['id'], current['id'])))
                if pair in seen:
                    continue
                seen.add(pair)
                result = minimum_squared(prior, current)
                assert result is not None
                distance2, at = result
                assert distance2 >= threshold, ('continuous collision', prior['agent'], current['agent'], str(at), str(distance2))
                if nearest is None or distance2 < nearest[0]:
                    nearest = (distance2, at, prior['agent'], current['agent'])
            active.append(current)
    return {'passed': True, 'agents': agents, 'segments': len(records), 'radius': str(rad),
            'exact_pairs_checked': len(seen), 'spatial_buckets': len(buckets),
            'minimum_checked_distance_squared': str(nearest[0]) if nearest else None,
            'minimum_checked_at': str(nearest[1]) if nearest else None,
            'minimum_scope': 'Candidate pairs only; all excluded spatial boxes are separated beyond disc overlap.',
            'coverage': 'All agents continuously through makespan, including completed robots.'}


def self_check():
    def seg(agent, p0, p1, t0='0', t1='1'):
        return {'agent': agent, 'p0': p0, 'p1': p1, 't0': t0, 't1': t1}
    safe = [seg(0, [0, 0], [1, 0]), seg(1, [0, 1], [1, 1])]
    assert audit(safe, '1', 2)['passed']
    # Exact tangency is allowed; the next rational amount of overlap is rejected.
    assert audit([seg(0, [0, 0], [0, 0]), seg(1, ['1/5', 0], ['1/5', 0])], '1', 2)['passed']
    negatives = {
        'interior_crossing_endpoint_checks_miss': [seg(0, [-1, 0], [1, 0]), seg(1, [0, -1], [0, 1])],
        'head_on_swap': [seg(0, [0, 0], [1, 0]), seg(1, [1, 0], [0, 0])],
        'tiny_exact_overlap': [seg(0, [0, 0], [0, 0]), seg(1, ['199999/1000000', 0], ['199999/1000000', 0])],
        'missing_goal_dwell': [safe[0], seg(1, [0, 1], [0, 1], t1='1/2')],
    }
    rejected = []
    for name, rows in negatives.items():
        try:
            audit(rows, '1', 2)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('Accepted broken trace: ' + name)
    return {'passed': True, 'negative_controls': rejected}


if __name__ == '__main__':
    import json
    print(json.dumps(self_check()))
