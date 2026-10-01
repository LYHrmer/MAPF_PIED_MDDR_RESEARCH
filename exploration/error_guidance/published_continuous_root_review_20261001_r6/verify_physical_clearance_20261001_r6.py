"""Independent geometry audit of actual ARGoS observations, never a safety proof.

Uses synchronized observed poses and the boxes in the exact per-run ARGoS input.
The supplied circular footprint is a stated geometric approximation. In particular,
wheel commands are NOT treated as bounds on the simulated body's actual velocity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def audit(run, radius):
    run = Path(run)
    root = ET.parse(run / "experiment.argos").getroot()
    arena = root.find("arena")
    robots = sorted((r.attrib["id"] for r in arena.findall("foot-bot")), key=int)
    assert len(robots) >= 2 and len(set(robots)) == len(robots)
    box_ids, boxes = [], []
    for box in arena.findall("box"):
        assert box.attrib.get("movable", "false") == "false"
        body = box.find("body")
        assert all(float(v) == 0 for v in body.attrib["orientation"].split(","))
        x, y, _ = map(float, body.attrib["position"].split(","))
        sx, sy, _ = map(float, box.attrib["size"].split(","))
        assert sx > 0 and sy > 0
        boxes.append([x, y, sx / 2, sy / 2])
        box_ids.append(box.attrib["id"])
    positions = {}
    for line in (run / "events.jsonl").open():
        e = json.loads(line)
        if e["kind"] != "observation":
            continue
        o, robot = e["observation"], e["robot"]
        tick = o["tick"]
        assert tick == e["tick"] and robot in robots
        frame = positions.setdefault(tick, {})
        assert robot not in frame, (tick, robot, "duplicate observation")
        frame[robot] = [o["x"], o["y"]]
    ticks = sorted(positions)
    assert ticks and ticks == list(range(ticks[-1] + 1)), "missing physical tick"
    assert all(set(f) == set(robots) for f in positions.values()), "partial snapshot"
    xy = np.asarray([[positions[t][r] for r in robots] for t in ticks], dtype=float)
    assert np.isfinite(xy).all()
    pair_best = {"center_distance_m": float("inf")}
    a, b = np.triu_indices(len(robots), 1)
    for start in range(0, len(ticks), 256):
        ps = xy[start:start + 256]
        distance = np.linalg.norm(ps[:, a] - ps[:, b], axis=-1)
        t, pair = np.unravel_index(distance.argmin(), distance.shape)
        if distance[t, pair] < pair_best["center_distance_m"]:
            pair_best = {"center_distance_m": float(distance[t, pair]),
                         "tick": ticks[start + t], "robots": [robots[a[pair]], robots[b[pair]]],
                         "positions_m": [ps[t, a[pair]].tolist(), ps[t, b[pair]].tolist()]}
    pair_best["circular_footprint_gap_m"] = pair_best["center_distance_m"] - 2 * radius
    box_best = None
    if boxes:
        bx = np.asarray(boxes, dtype=float)
        best = float("inf")
        for start in range(0, len(ticks), 256):
            ps = xy[start:start + 256]
            q = np.abs(ps[:, :, None, :] - bx[None, None, :, :2]) - bx[None, None, :, 2:]
            distance = np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(np.max(q, axis=-1), 0)
            t, robot, box = np.unravel_index(distance.argmin(), distance.shape)
            if distance[t, robot, box] < best:
                best = float(distance[t, robot, box])
                box_best = {"center_to_box_signed_distance_m": best,
                            "circular_footprint_gap_m": best - radius,
                            "tick": ticks[start + t], "robot": robots[robot],
                            "box": box_ids[box], "position_m": ps[t, robot].tolist(),
                            "box_center_halfextents_m": bx[box].tolist()}
    return {"run": str(run), "robots": len(robots), "ticks": len(ticks),
            "observations": len(ticks) * len(robots), "boxes": len(boxes),
            "assumed_circular_footprint_radius_m": radius, "closest_pair": pair_best,
            "closest_obstacle": box_best,
            "all_sampled_circular_envelopes_separated": pair_best["circular_footprint_gap_m"] > 0 and
                (box_best is None or box_best["circular_footprint_gap_m"] > 0),
            "continuous_safety_verified": False,
            "scope": "Sampled circle/box geometry only; not collision contacts, substep trajectory, or online certificate.",
            "input_sha256": {n: sha(run / n) for n in ("experiment.argos", "events.jsonl")}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--radius", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert 0 < args.radius < 1
    result = audit(args.run, args.radius)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))
