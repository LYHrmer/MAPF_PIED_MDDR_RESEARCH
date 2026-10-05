#!/usr/bin/env python3
"""Post hoc read-only diagnosis; never imports the engine or invokes a solver."""
import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph(path, gate, which):
    return load(path.parent / "solves" / f"{gate:05d}" / f"{which}.json")


def orientation(g):
    return {x["uid"]: [d["active"] for d in x["dependencies"]] for x in g["groups"]}


def mechanism(base_path, learned_path):
    base, learned = load(base_path), load(learned_path)
    first_selection = next((dict(gate_index=a["gate_index"], capture_time=a["capture_time"],
        baseline=a["selected"], learned=b["selected"])
        for a, b in zip(base["gates"], learned["gates"]) if a["selected"] != b["selected"]), None)
    first_graph = None
    for sa, sb in zip(base["solves"], learned["solves"]):
        assert sa["gate_index"] == sb["gate_index"]
        gi = sa["gate_index"]
        a, b = graph(base_path, gi, "after"), graph(learned_path, gi, "after")
        oa, ob = orientation(a), orientation(b)
        different = [key for key in oa if oa[key] != ob[key]]
        if not different:
            continue
        before_a, before_b = graph(base_path, gi, "before"), graph(learned_path, gi, "before")
        va, vb = ({v["uid"]: v for v in x["vertices"]} for x in (before_a, before_b))
        changed_input = []
        for uid, av in va.items():
            bv = vb[uid]
            if any(av[k] != bv[k] for k in ("status", "progress", "duration")):
                changed_input.append(dict(vertex=uid, agent=av["agent"],
                    baseline={k: av[k] for k in ("status", "progress", "duration")},
                    learned={k: bv[k] for k in ("status", "progress", "duration")}))
        first_graph = dict(gate_index=gi, time=sa["time"], groups=different,
            baseline_groups=[x for x in a["groups"] if x["uid"] in different],
            learned_groups=[x for x in b["groups"] if x["uid"] in different],
            baseline_guard=sa["guard"], learned_guard=sb["guard"],
            differing_optimizer_vertex_inputs=changed_input,
            baseline_queries=[q for q in base["queries"] if q["gate_index"] == gi],
            learned_queries=[q for q in learned["queries"] if q["gate_index"] == gi],
            baseline_public=next(g["public_snapshot"] for g in base["gates"] if g["gate_index"] == gi),
            learned_public=next(g["public_snapshot"] for g in learned["gates"] if g["gate_index"] == gi))
        affected = {uid for group in a["groups"] if group["uid"] in different
            for dependency in group["dependencies"] for key in ("forward", "reverse")
            for uid in (dependency[key] or [])}
        first_graph["same_start_end_prefix"] = (
            [e for e in base["events"] if e["kind"] in ("START", "END") and e["time"] <= sa["time"]] ==
            [e for e in learned["events"] if e["kind"] in ("START", "END") and e["time"] <= sb["time"]])
        for label, episode, path in (("baseline", base, base_path), ("learned", learned, learned_path)):
            first_graph[label + "_relevant_events"] = [e for e in episode["events"]
                if e["kind"] in ("START", "END") and e["vertex"] in affected]
            first_graph[label + "_group_timeline"] = [dict(gate_index=s["gate_index"], time=s["time"],
                groups=[x for x in graph(path, s["gate_index"], "after")["groups"] if x["uid"] in different])
                for s in episode["solves"] if s["gate_index"] >= gi]
        break
    return dict(baseline_episode=str(base_path.relative_to(HERE)), learned_episode=str(learned_path.relative_to(HERE)),
        sum_completion=[base["sum_completion"], learned["sum_completion"]],
        makespan=[base["makespan"], learned["makespan"]],
        queries=[base["query_count"], learned["query_count"]],
        completion_changes={k: learned["completion_times"][k]-v for k, v in base["completion_times"].items()
            if abs(learned["completion_times"][k]-v) > 1e-8},
        first_selection_difference=first_selection, first_graph_difference=first_graph)


def main():
    paths = sorted((HERE / "episodes/TEST").glob("*/*/episode.json"))
    assert len(paths) == 270, f"Expected full TEST: {len(paths)}/270"
    coverage = collections.defaultdict(collections.Counter)
    relations = collections.defaultdict(collections.Counter)
    budgets = []
    inputs = []
    worlds = collections.defaultdict(dict)
    for path in paths:
        d = load(path)
        receipt = load(path.parent / "RUN_RECEIPT.json")
        assert sha(path) == receipt["episode_sha256"]
        assert d["status"] == "completed"
        arm = d["benchmark"]["arm"]
        worlds[path.parent.parent.name][arm] = path
        inputs.append(dict(path=str(path.relative_to(HERE)), sha256=sha(path)))
        selected_count = 0
        exhaustion = None
        for gate in d["gates"]:
            public = {a["agent_id"]: a for a in gate["public_snapshot"]["agents"]}
            for aid in gate["selected"]:
                a = public[aid]
                outgoing = a["outgoing_blocked_agents"] == 0
                switchable = a["upcoming_switchable_influence"] == 0
                coverage[arm]["queries"] += 1
                coverage[arm]["outgoing_zero"] += outgoing
                coverage[arm]["switchable_zero"] += switchable
                coverage[arm]["both_zero"] += outgoing and switchable
            selected_count += len(gate["selected"])
            if not d["dense_unbudgeted_reference"] and exhaustion is None and selected_count >= d["query_budget"]:
                exhaustion = dict(gate_index=gate["gate_index"], capture_time=gate["capture_time"])
        assert selected_count == d["query_count"]
        flips = [s for s in d["solves"] if s["guard"]["passed"] and s["guard"]["changed_groups"]]
        first = dict(gate_index=flips[0]["gate_index"], time=flips[0]["time"]) if flips else None
        relation = "not_exhausted" if exhaustion is None else ("no_flip" if first is None else
            ("exhaustion_before_first_flip" if exhaustion["gate_index"] < first["gate_index"] else
             "exhaustion_same_gate_as_first_flip" if exhaustion["gate_index"] == first["gate_index"] else
             "exhaustion_after_first_flip"))
        relations[arm][relation] += 1
        budgets.append(dict(episode=str(path.relative_to(HERE)), arm=arm, queries=d["query_count"],
            budget=d["query_budget"], exhaustion=exhaustion, first_adopted_flip=first,
            adopted_flip_gate_count=len(flips), relation=relation,
            flip_gates_after_exhaustion=sum(s["gate_index"] > exhaustion["gate_index"] for s in flips) if exhaustion else None))
    pairs, details = collections.defaultdict(collections.Counter), []
    for world, arms in worlds.items():
        learned = load(arms["learned_query"])
        for baseline in ("history_only", "history_rule"):
            base = load(arms[baseline])
            delta = learned["sum_completion"] - base["sum_completion"]
            pairs[baseline]["better" if delta < -1e-8 else "worse" if delta > 1e-8 else "same"] += 1
            if abs(delta) > 1e-8:
                details.append(dict(world=world, baseline=baseline, learned_minus_baseline=delta,
                    **mechanism(arms[baseline], arms["learned_query"])))
    result = dict(scope="post hoc descriptive diagnosis of the same frozen TEST episodes; zero new runs or counterfactuals",
        test_episodes=len(paths), test_worlds=len(worlds), input_manifest=inputs,
        helper_sha256=sha(Path(__file__)), query_public_coverage=dict(coverage),
        budget_first_flip_relations=dict(relations), budget_details=budgets,
        learned_comparisons=dict(pairs), nonzero_mechanisms=details,
        limitations=["No current public outgoing/switchable influence does not imply zero future query value.",
            "First adopted flip may be driven by public history without any queried observation; these are descriptive timings.",
            "Post hoc input/graph differences alone do not identify a single query's causal value."])
    output = Path(__file__).with_name("MECHANISM_DIAGNOSTICS.json")
    assert not output.exists(), "diagnostics immutable; do not overwrite"
    output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({k: result[k] for k in ("test_episodes", "test_worlds", "query_public_coverage", "budget_first_flip_relations", "learned_comparisons")}, indent=2))


if __name__ == "__main__":
    main()
