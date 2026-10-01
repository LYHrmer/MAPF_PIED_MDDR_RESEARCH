"""Offline classification of terminal wait graphs from untouched joint-run logs.

Uses the final recorded owner/demand state. No simulator truth enters a policy.
Separates occupied final goals from cycles between unfinished static routes.
"""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path


def classify(path):
    frame = summary = None
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for line in f:
            digest.update(line)
            e = json.loads(line)
            if e["event"] == "world_frame_offline_only":
                frame = e
            elif e["event"] == "joint_summary":
                summary = e
    assert frame is not None and summary is not None
    result = {"raw": str(path), "sha256": digest.hexdigest(), "deadlock": summary["deadlock"],
              "served": summary["served"], "tasks": summary["task_count"]}
    if not summary["deadlock"]:
        result["terminal_graph_classification"] = "not a deadlock terminal"
        return result
    assert not frame["actions"] and all(not r["active"] for r in frame["robots"])
    owner = {cell: int(agent.split("-")[-1]) for cell, agent, _ in frame["owners"]}
    robots = {r["agent"]: r for r in frame["robots"]}
    finished = {a for a, r in robots.items() if r["served"] and r["head_index"] == 2}
    blockers = {}
    for d in frame["demands"]:
        a = int(d["agent"].split("-")[-1])
        blocked_by = {owner[c] for c in d["resources"] if c in owner and owner[c] != a}
        assert len(blocked_by) == 1, (a, blocked_by)
        blockers[a] = blocked_by.pop()
        assert not robots[a]["served"]
    diagnostics = []
    unique_cycles = set()
    for a in sorted(blockers):
        chain, current = [], a
        while current in blockers and current not in chain:
            chain.append(current)
            current = blockers[current]
        if current in chain:
            cycle = chain[chain.index(current):]
            # Canonicalize directed cycle by rotation, preserving orientation.
            smallest = min(range(len(cycle)), key=lambda i: cycle[i])
            cycle = tuple(cycle[smallest:] + cycle[:smallest])
            unique_cycles.add(cycle)
            reason = "unfinished_static_route_cycle"
        else:
            assert current in finished, (a, chain, current, "unexplained terminal sink")
            cycle = None
            reason = "completed_third_head_standing_owner"
        diagnostics.append({"agent": a, "blocker_chain": chain + [current], "reason": reason,
                            "cycle": cycle, "unfinished_fixed_heads": 3 - robots[a]["head_index"]})
    result.update({"finished_stationary_agents": sorted(finished), "direct_wait_edges": sorted(blockers.items()),
                   "unique_cycles": sorted(unique_cycles), "agents_by_root_cause": dict(Counter(d["reason"] for d in diagnostics)),
                   "unfinished_heads_by_root_cause": dict(sum((Counter({d["reason"]: d["unfinished_fixed_heads"]}) for d in diagnostics), Counter())),
                   "blocked_agents": diagnostics,
                   "scope": "Static post-run causal classification; not proof that a query or replanner can or cannot prevent earlier deadlock formation."})
    assert sum(d["unfinished_fixed_heads"] for d in diagnostics) == summary["uncompleted_heads"]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = {"runs": [classify(p) for p in sorted(args.directory.glob("*.jsonl"))]}
    assert result["runs"]
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"runs": [{k: v for k, v in r.items() if k in
        ("raw", "served", "tasks", "unique_cycles", "agents_by_root_cause", "unfinished_heads_by_root_cause")}
        for r in result["runs"]]}, indent=2))
