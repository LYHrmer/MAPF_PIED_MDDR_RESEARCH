"""Zero-native follow-up for capture evidence logging and structural boundary."""
from pathlib import Path
import copy
import json

from engine import Simulator, EngineConfig, NoQueryPolicy, file_sha, write_json
from evidence import EvidenceStore, expand_episode, digest
from structural import structural_features, StructuralStopPolicy
from r0_checks import CASE

HERE = Path(__file__).resolve().parent
OUT = HERE/"r0"
config = EngineConfig(solve_period=.6, query_latency=.1, max_time=10,
    evidence_dir=str(OUT/"evidence"), cache_dir=str(OUT/"cache"), output_dir=str(OUT/"capture_binding"))
result = Simulator(CASE, config=config).run(NoQueryPolicy())
assert result["success"] and result["new_author_calls"] == 0
store = EvidenceStore(config.evidence_dir)
expanded = expand_episode(result, store)
gate = result["gates"][0]
graph = store.get_graph(gate["capture_graph_ref"])
assert abs(graph["vertices"][0]["progress"]-.6) < 1e-12
predictions = store.get(result["prediction_evidence_ref"])
prediction = predictions[gate["prediction_keys"]["agent0"]]
assert prediction["time"] == gate["capture_time"]
assert "capture_graph_ref" not in expanded["gates"][0]["public_snapshot"]

vertices = [dict(uid=uid, status="IN_PROGRESS" if uid in ("a0", "b0") else "STAGED", duration=1., progress=.2)
    for uid in ("a0", "a1", "a2", "b0", "b1", "b2", "c0")]
fixture = dict(vertices=vertices, type1=[["a0","a1"],["a1","a2"],["b0","b1"],["b1","b2"]],
    groups=[dict(uid="legal", switchable=True, within_horizon=True,
        dependencies=[dict(forward=["a2","b2"],reverse=["b1","a1"],active=["a2","b2"],b=False)]),
        dict(uid="blocking",switchable=False,within_horizon=True,
            dependencies=[dict(forward=["a0","c0"],reverse=None,active=["a0","c0"],b=False)])])
agents = [dict(agent_id=aid,current_vertex=uid,query_eligible=active,blocked=blocked,nominal_duration=1.,history_ratio=1.,
    elapsed=.2,history_cv=0.,last_measurement_age=None) for aid,uid,active,blocked in
    [("a","a0",True,False),("b","b0",True,False),("c","c0",False,True)]]
features = structural_features(fixture, agents)
assert features["a"]["legal_boundary_group_count"] == 1 and features["a"]["blocked_frontier_count"] == 1
assert features["a"]["direct_blocked_frontier_count"] == 1
assert features["b"]["legal_boundary_group_count"] == 1 and features["b"]["blocked_frontier_count"] == 0
for agent in agents:agent.update(features[agent["agent_id"]])
assert StructuralStopPolicy()(dict(agents=agents,solve_period=4.,max_queries=1)) == ["a"]
empty = copy.deepcopy(fixture);empty["groups"]=[]
for agent in agents:agent["blocked"]=False
features = structural_features(empty, agents)
for agent in agents:agent.update(features[agent["agent_id"]])
assert StructuralStopPolicy()(dict(agents=agents,solve_period=4.,max_queries=2)) == []
bad = copy.deepcopy(fixture);bad["vertices"][1]["status"]="IN_PROGRESS"
rejected=False
try:structural_features(bad,agents)
except ValueError:rejected=True
assert rejected
report=dict(passed=True,new_author_calls=0,science_episodes=0,
    checks=["capture_graph_at_capture_not_solve", "capture_prediction_keys_match_time", "extra_receipts_not_policy_inputs",
        "reachable_legal_boundary", "blocked_frontier", "direct_frontier", "structural_priority", "STOP_no_structure", "committed_head_rejected"],
    source_hashes={name:file_sha(HERE/name) for name in ("engine.py","solver_adapter.py","evidence.py","structural.py")})
write_json(OUT/"CAPTURE_VALIDATION.json",report)
print(json.dumps(report,indent=2))
