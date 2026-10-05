#!/usr/bin/env python3
"""R0 mechanical qualification, at most two real author solver calls."""
import copy
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from engine import Simulator, EngineConfig, HistoryPredictor, NoQueryPolicy, StructuralStopPolicy, file_sha, write_json, base
from evidence import EvidenceStore, digest, expand_episode
from solver_adapter import capture_model

HERE = Path(__file__).resolve().parent
OUT = HERE/"r0"
MODEL = Path("/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/conditional_duration_20261005_r19")
CASE = dict(case_id="r19_r0_one_move", solution={"schedule": {"agent0": [dict(x=0,y=0,t=0), dict(x=1,y=0,t=1)]}})


def main():
    assert not (OUT/"REGISTRATION.json").exists(), "R0 is single attempt; preserve failures before changing protocol"
    write_json(OUT/"REGISTRATION.json", dict(scope="mechanical qualification, not science", native_call_cap=2,
        sources={name: file_sha(HERE/name) for name in ("engine.py", "evidence.py", "structural.py", "solver_adapter.py", "r0_checks.py", "PUBLIC_SCHEMA.json")},
        model_sha256=file_sha(MODEL/"MODEL.json"), predictor_sha256=file_sha(MODEL/"predictor.py")))
    config = EngineConfig(solve_period=.6, query_latency=.1, max_time=10,
        evidence_dir=str(OUT/"evidence"), cache_dir=str(OUT/"cache"))
    seen = []
    def spy(context):
        seen.append(context)
        return dict(remaining_time=2., future_duration_ratio=1., metadata=dict(method="R0_mock_prediction"))
    staged = Simulator(CASE, predictor=spy, config=config)
    staged.now = 10
    staged._estimate("agent0")
    assert seen[-1]["elapsed"] == 0 and seen[-1]["status"] == "STAGED"
    assert set(seen[-1]) == {"status", "nominal_duration", "elapsed", "completed_history"}
    current = Simulator(CASE, predictor=spy, config=config)
    current._dispatch(); current.now = .2
    current._update_predictor()
    v = current.agents["agent0"]["vertex"]
    assert 0 <= v.get_progress() <= 1 and abs(v.get_expected_completion_time()*(1-v.get_progress())-2) < 1e-12
    current.latest["agent0"] = dict(vertex=v.get_shorthand(), captured=.1, delivered_at=.2, progress=.25, query_id=0)
    e = current._estimate("agent0")
    assert abs(e["remaining"]-.65) < 1e-12 and e["provider"] == "position_linear_all_history"
    current.latest["agent0"]["vertex"] = "stale_other_occurrence"
    assert current._estimate("agent0")["remaining"] == 2.
    # Real author invocation 1, then exact same input reused under STOP.
    first = Simulator(CASE, config=replace(config, output_dir=str(OUT/"history"))).run(NoQueryPolicy())
    assert first["success"] and first["new_author_calls"] == 1 and first["makespan"] == 1
    second = Simulator(CASE, config=replace(config, output_dir=str(OUT/"cache_stop"))).run(StructuralStopPolicy())
    assert second["success"] and second["new_author_calls"] == 0 and second["query_count"] == 0
    store = EvidenceStore(config.evidence_dir)
    expanded = expand_episode(first, store)
    assert digest(expanded["initial_graph"]) == store.get(first["initial_graph_ref"])["full_sha256"]
    before = store.get_graph(first["solves"][0]["before_ref"])
    assert digest(before) == first["solves"][0]["before_sha256"]
    topology1 = store.get(first["solves"][0]["before_ref"])["topology"]
    topology2 = store.get(first["solves"][0]["after_ref"])["topology"]
    assert topology1 == topology2
    # Real frozen learned predictor, invocation 2. EWMA interface checked without solver.
    spec = importlib.util.spec_from_file_location("r19_r0_predictor", MODEL/"predictor.py")
    predictor_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(predictor_module)
    learned = predictor_module.DurationPredictor(MODEL/"MODEL.json", mode="learned")
    third = Simulator(CASE, predictor=learned, config=replace(config, output_dir=str(OUT/"learned"))).run(NoQueryPolicy())
    assert third["success"] and third["new_author_calls"] == 1
    ewma = predictor_module.DurationPredictor(MODEL/"MODEL.json", mode="ewma03_survival")
    ewma_result = ewma(dict(status="IN_PROGRESS", nominal_duration=1., elapsed=4., completed_history=[]))
    assert ewma_result["remaining_time"] > 0
    # Synthetic rejected-incumbent fixture: this is NOT an author solver result.
    variable = SimpleNamespace(name="x", x=2., lb=0., ub=10., var_type="C")
    class HashableVariable:
        name="x"
    symbolic = HashableVariable()
    row = SimpleNamespace(name="x_le_one", expr=SimpleNamespace(expr={symbolic:1.}, const=-1., sense="<"))
    fake = SimpleNamespace(vars=[variable], constrs=[row], num_solutions=1, status=SimpleNamespace(name="R0_SYNTHETIC_REJECTED"),
        objective=SimpleNamespace(const=0., expr={symbolic:1.}), objective_value=2., objective_bound=2., num_cols=1, num_rows=1)
    model, payload = capture_model(fake)
    assert not model["feasible"] and model["max_violation"] == 1.
    model.update(error=None, reference_solver_seconds=0., reference_author_seconds=0., actual_author_calls=0, author_max_seconds=60)
    failure_config = replace(config, cache_dir=str(OUT/"synthetic_failure_cache"), output_dir=str(OUT/"synthetic_failure"))
    with patch("solver_adapter.invoke", return_value=(model,payload,dict(scope="R0 synthetic negative-cache fixture, no native solver"),0.)):
        rejected = Simulator(CASE, config=failure_config).run(NoQueryPolicy())
    with patch("solver_adapter.invoke", side_effect=AssertionError("negative cache must not invoke solver")):
        repeated = Simulator(CASE, config=replace(failure_config, output_dir=str(OUT/"synthetic_failure_reuse"))).run(NoQueryPolicy())
    assert rejected["success"] and repeated["success"] and repeated["solves"][0]["cache_reused"]
    assert rejected["solves"][0]["before_sha256"] == rejected["solves"][0]["after_sha256"]
    assert store.get(rejected["solves"][0]["model_ref"])["constraints"][0]["violation"] == 1.
    report = dict(passed=True, real_author_calls=2, synthetic_negative_cache_calls=0, science_episodes=0,
        checks=["STAGED_wait_excluded", "public_predictor_whitelist", "normalized_residual_encoding", "common_POSITION_projection",
            "stale_occurrence_ignored", "original_author_history_optimal", "exact_cache_STOP_reuse", "CAS_lossless_graph",
            "CAS_topology_dedup", "frozen_learned_model_runs", "conditional_EWMA_overdue_positive", "full_failed_payload",
            "constraint_residual_rejects", "failed_cache_reuses_without_solver", "parent_graph_retained"],
        statuses=[first["status"],second["status"],third["status"]], source_hashes={name:file_sha(HERE/name) for name in ("engine.py","solver_adapter.py","evidence.py","structural.py")})
    write_json(OUT/"VALIDATION.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
