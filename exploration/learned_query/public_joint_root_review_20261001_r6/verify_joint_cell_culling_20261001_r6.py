"""Exact integer cross-check for the fixed unit-grid R6 geometry's broad phase.

An axis-aligned square with half-width 1/10 plus error half-width 1/20
has a swept rectangular envelope with half-width 3/20. Resource cells have
half-width 1/2. A disjoint full-sweep box cannot intersect any suffix sweep.
This checks ALL fixed source edges, irrespective of policy or outcome.
It does not replace differential checks against the actual Geometry engine.
"""
import argparse
import hashlib
import json
from pathlib import Path


SCALE = 20_000_000
BODY = 3 * SCALE // 20
CELL = SCALE // 2
SAMPLES = (0, SCALE // 2, 13 * SCALE // 20,
           13 * SCALE // 20 + 1, SCALE - 1, SCALE)


def mask(start, end, q, cells):
    dx, dy = end[0] - start[0], end[1] - start[1]
    sx, sy = start[0] * SCALE + dx * q, start[1] * SCALE + dy * q
    ex, ey = end[0] * SCALE, end[1] * SCALE
    lo_x, hi_x = min(sx, ex) - BODY, max(sx, ex) + BODY
    lo_y, hi_y = min(sy, ey) - BODY, max(sy, ey) + BODY
    return {(x, y) for x, y in cells if
            x * SCALE + CELL >= lo_x and x * SCALE - CELL <= hi_x and
            y * SCALE + CELL >= lo_y and y * SCALE - CELL <= hi_y}


def main(source):
    d = json.loads(source.read_text())
    edges, layouts = {}, {}
    for c in d["cohorts"]:
        cells = frozenset(map(tuple, c["resource_cells"]))
        layout = hashlib.sha256(json.dumps(sorted(cells)).encode()).hexdigest()
        layouts[layout] = cells
        for r in c["robots"]:
            ps = list(map(tuple, r["route_points"]))
            assert ps[0] == tuple(r["start"]) and len(ps) == len(r["route"]) + 1
            for s, e in zip(ps, ps[1:]):
                assert s in cells and e in cells
                distance = abs(s[0] - e[0]) + abs(s[1] - e[1])
                assert distance in (0, 1)
                if distance:
                    edges[(layout, s, e)] = cells
    checked = 0
    for (_, s, e), cells in edges.items():
        candidates = mask(s, e, 0, cells)
        assert candidates == {s, e}, (s, e, candidates)
        for q in SAMPLES:
            full = mask(s, e, q, cells)
            reduced = mask(s, e, q, candidates)
            assert full == reduced, (s, e, q)
            assert (s in full) == (q <= 13 * SCALE // 20), (s, e, q)
            checked += 1
    return {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "cohorts": len(d["cohorts"]), "distinct_cell_layouts": len(layouts),
            "distinct_cardinal_edges": len(edges), "suffix_mask_checks": checked,
            "all_full_sweep_candidate_sets_equal_exact_two_end_cells": True,
            "closed_contact_at_13_over_20_preserved": True,
            "exact_integer_scale": SCALE, "q_samples_scaled": SAMPLES,
            "claim": "Exact rectangular geometry check plus the disjoint-full-sweep inclusion argument; actual engine differential validation remains separate."}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    result = main(args.source)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
