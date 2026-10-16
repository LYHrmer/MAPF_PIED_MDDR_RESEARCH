"""Conservative relative-start hulls from paired phase intervals.

Exploratory CTC-style interval adapter, NOT an author implementation or a
release gate. Continuous enclosure callbacks must cover their entire interval.
No physical plant, feedback, simulation, training, I/O or timing on import.
"""
from fractions import Fraction as Q
import heapq
from interface import q


class ProjectionBudget(ValueError):
    def __init__(self, operations):
        self.operations = dict(operations)
        super().__init__('phase-pair budget exhausted; no partial certificate')


def relative_hull(domain_a, domain_b, box_a, box_b, *, resolution, max_cells):
    """Enclose {s_a-s_b: possible continuous body intersection}.

    Two best-first traversals use one deterministic rectangular bisection tree.
    First unresolved leaf supplies an outer extremum; all pending projections
    are no more extreme. A leaf is unresolved, never a collision witness.
    """
    root = tuple(q(x) for x in (*domain_a, *domain_b))
    resolution = q(resolution)
    if (len(root) != 4 or root[0] > root[1] or root[2] > root[3]
            or resolution <= 0 or type(max_cells) is not int or max_cells < 1):
        raise ValueError('ordered exact domains, positive resolution and budget required')
    boxes = ({}, {})
    separated = {}
    ops = dict(pair_cells=0, box_evaluations=0, box_cache_hits=0,
               pair_cache_hits=0, heap_pushes=0, heap_pops=0, max_heap=0)

    def clear(cell):
        if cell in separated:
            ops['pair_cache_hits'] += 1
            return separated[cell]
        if ops['pair_cells'] >= max_cells:
            raise ProjectionBudget(ops)
        pair = []
        for i, (callback, span) in enumerate(zip((box_a, box_b), (cell[:2], cell[2:]))):
            if span not in boxes[i]:
                boxes[i][span] = callback(*span)
                ops['box_evaluations'] += 1
            else:
                ops['box_cache_hits'] += 1
            pair.append(boxes[i][span])
        separated[cell] = pair[0].separated(pair[1])
        ops['pair_cells'] += 1
        return separated[cell]

    def search(upper):
        heap, serial = [], 0

        def push(cell):
            nonlocal serial
            bound = cell[1]-cell[2] if upper else cell[0]-cell[3]
            heapq.heappush(heap, (-bound if upper else bound, serial, cell))
            serial += 1
            ops['heap_pushes'] += 1
            ops['max_heap'] = max(ops['max_heap'], len(heap))

        push(root)
        while heap:
            key, _, cell = heapq.heappop(heap)
            ops['heap_pops'] += 1
            if clear(cell):
                continue
            a, b, c, d = cell
            if max(b-a, d-c) <= resolution:
                return (-key if upper else key), cell
            if b-a >= d-c:
                mid = (a+b)/2
                push((a, mid, c, d)); push((mid, b, c, d))
            else:
                mid = (c+d)/2
                push((a, b, c, mid)); push((a, b, mid, d))
        return None

    left = search(False)
    right = search(True) if left is not None else None
    return {'window': None if left is None else (left[0], right[0]),
            'extreme_cells': None if left is None else (left[1], right[1]),
            'operations': ops, 'overlap_is_collision': False}


def union_closed(intervals):
    """Keep gaps between action-pair hulls; touching stays forbidden."""
    result = []
    for lo, hi in sorted((q(a), q(b)) for a, b in intervals):
        if lo > hi:
            raise ValueError('inverted forbidden interval')
        if result and lo <= result[-1][1]:
            result[-1] = (result[-1][0], max(hi, result[-1][1]))
        else:
            result.append((lo, hi))
    return tuple(result)
