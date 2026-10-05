"""R19 isolated adapters; original author optimizer and R18 execution unchanged."""
from dataclasses import dataclass, replace, asdict
from pathlib import Path
from collections import defaultdict
import copy
import importlib.util
import math
import statistics
import sys
import types

from evidence import EvidenceStore, digest, expand_episode
from structural import StructuralStopPolicy, structural_features

HERE = Path(__file__).resolve().parent
R18 = HERE.parent / "sadg_benchmark_20261005_r18"
BASE_SHA = "7a83912d7fbefa8122ed551cab2ce93a536e6efafc3ebaf0b1e0dbb99eff12f6"
import hashlib
if hashlib.sha256((R18 / "engine.py").read_bytes()).hexdigest() != BASE_SHA:
    raise RuntimeError("frozen R18 inheritance source changed")
spec = importlib.util.spec_from_file_location("r19_frozen_r18_engine", R18 / "engine.py")
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)

EPS = base.EPS
NoQueryPolicy = base.NoQueryPolicy
DensePositionPolicy = base.DensePositionPolicy
adoption_guard = base.adoption_guard
graph_snapshot = base.graph_snapshot
write_json = base.write_json
file_sha = base.file_sha


@dataclass(frozen=True)
class EngineConfig(base.EngineConfig):
    evidence_dir: str | None = None


class HistoryPredictor:
    """Exact strong R18 all-delivered-END duration ratio, without POSITION."""
    name = "all_history"

    def __call__(self, context):
        h = context["completed_history"]
        ratio = sum(x["duration"] for x in h)/sum(x["nominal_duration"] for x in h) if h else 1.
        mean = context["nominal_duration"]*ratio
        return dict(remaining_time=max(0., mean-context["elapsed"]), future_duration_ratio=ratio,
            metadata=dict(method=self.name, history_count=len(h)))


class Simulator(base.Simulator):
    def __init__(self, case, disturbance=None, seed=0, *, predictor=None, config=None, **kwargs):
        cfg = config or EngineConfig(**kwargs)
        if config is not None and kwargs:
            raise ValueError("config or keyword config, not both")
        if not cfg.evidence_dir:
            raise ValueError("R19 requires a shared evidence_dir")
        self.requested_config = cfg
        self.output_dir = Path(cfg.output_dir) if cfg.output_dir else None
        self.store = EvidenceStore(cfg.evidence_dir)
        self.predictor = predictor or HistoryPredictor()
        self.prediction_records = {}
        self._last_predictions = {}
        # Suppress only R18's redundant episode/file writer. Physical execution,
        # event cadence, transport, commitments and collision audit are inherited.
        super().__init__(case, disturbance, seed, config=replace(cfg, output_dir=None))

    def _estimate(self, aid):
        agent = self.agents[aid]
        vertex = agent["vertex"]
        ratio, variance, cv = self._history(aid)
        if vertex is None:
            self._last_predictions.pop(aid, None)
            return dict(progress=1., remaining=0., ratio=ratio, future_ratio=ratio,
                variance=variance, cv=cv, age=None, residual=None, provider="completed")
        nominal = self.nominal[vertex.get_shorthand()]
        elapsed = 0. if agent["start"] is None else self.now-agent["start"]
        context = dict(status=vertex.get_status().name, nominal_duration=nominal, elapsed=elapsed,
            completed_history=[{k: h[k] for k in ("nominal_duration", "duration", "start", "end", "delivered")}
                for h in self.history[aid]])
        if any(h["delivered"] > self.now+EPS for h in context["completed_history"]):
            raise RuntimeError("undelivered END in public predictor input")
        function = self.predictor if callable(self.predictor) else self.predictor.predict
        prediction = function(copy.deepcopy(context))
        remaining, future_ratio = float(prediction["remaining_time"]), float(prediction["future_duration_ratio"])
        if not (math.isfinite(remaining) and remaining >= 0 and math.isfinite(future_ratio) and future_ratio > 0):
            raise ValueError("predictor must produce finite nonnegative residual and positive future ratio")
        provider = "end_history_predictor"
        latest = self.latest.get(aid)
        age = residual = None
        observed = None
        if latest is not None and latest["vertex"] == vertex.get_shorthand():
            if latest["delivered_at"] > self.now+EPS or latest["captured"] > self.now+EPS:
                raise RuntimeError("undelivered POSITION in prediction")
            age = self.now-latest["captured"]
            residual = nominal*(1-latest["progress"])
            # Root-registered common fusion: the original R18 linear-history
            # projection, independent of the learned predictor's future ratio.
            remaining = max(0., residual*ratio-age)
            provider = "position_linear_all_history"
            observed = {k: latest[k] for k in ("vertex", "captured", "delivered_at", "progress", "query_id")}
        duration = max(nominal*future_ratio, remaining, EPS)
        progress = 1-remaining/duration if vertex.get_status() == self.Status.IN_PROGRESS else 0.
        evidence = dict(agent=aid, vertex=vertex.get_shorthand(), time=self.now,
            context=context, predictor_output=prediction, delivered_position=observed,
            provider=provider, remaining_time=remaining, future_duration_ratio=future_ratio,
            encoded_duration=duration, encoded_progress=progress)
        key = digest(evidence)
        self.prediction_records[key] = evidence
        self._last_predictions[aid] = key
        return dict(progress=progress, remaining=remaining, ratio=ratio, future_ratio=future_ratio,
            variance=variance, cv=cv, age=age, residual=residual, provider=provider, encoded_duration=duration)

    def _update_predictor(self):
        estimates = {aid: self._estimate(aid) for aid in self.agent_ids}
        for aid, vertices in self.graph.vertices_by_agent.items():
            delivered = {h["vertex"]: h for h in self.history[aid]}
            estimate = estimates[aid]
            for vertex in vertices:
                uid = vertex.get_shorthand()
                if vertex.get_status() == self.Status.COMPLETED:
                    duration, progress = delivered[uid]["duration"], 1.
                elif vertex.get_status() == self.Status.IN_PROGRESS:
                    duration, progress = estimate["encoded_duration"], estimate["progress"]
                else:
                    duration, progress = self.nominal[uid]*estimate["future_ratio"], 0.
                vertex.expected_completion_time = duration
                vertex.get_progress = types.MethodType(lambda self, value=progress: value, vertex)
        return estimates

    def public_snapshot(self, dense=False):
        snapshot = super().public_snapshot(dense)
        graph = graph_snapshot(self.graph, self.config.horizon)
        structure = structural_features(graph, snapshot["agents"])
        for agent in snapshot["agents"]:
            agent.update(structure[agent["agent_id"]])
            key = self._last_predictions.get(agent["agent_id"])
            prediction = self.prediction_records.get(key)
            agent["prediction_provider"] = prediction["provider"] if prediction and agent["status"] != "COMPLETED" else "completed"
        snapshot["solve_period"] = self.config.solve_period
        snapshot["public_schema"] = "r19-history-structure-v1"
        self._capture_graph_ref = self.store.put_graph(graph)
        self._capture_prediction_keys = dict(self._last_predictions)
        return snapshot

    def _capture_gate(self, policy, override):
        super()._capture_gate(policy, override)
        self.gates[-1]["capture_graph_ref"] = self._capture_graph_ref
        self.gates[-1]["prediction_keys"] = self._capture_prediction_keys

    def _solve(self, gate):
        # Imported separately to keep the mechanical public-interface adapter
        # short. This wrapper calls graph.optimize unmodified exactly once on
        # a cache miss and stores every unsuccessful model as well.
        from solver_adapter import solve
        solve(self, gate)

    def run(self, policy=None, probe_override=None):
        result = super().run(policy, probe_override)
        result["schema"] = "r19-sadg-episode-v1"
        result["config"] = asdict(self.requested_config)
        result["r18_engine_sha256"] = BASE_SHA
        result["engine_sha256"] = file_sha(__file__)
        result["adapter_source_hashes"] = {p: file_sha(HERE/p) for p in (
            "engine.py", "solver_adapter.py", "evidence.py", "structural.py", "PUBLIC_SCHEMA.json")}
        result["public_schema_sha256"] = result["adapter_source_hashes"]["PUBLIC_SCHEMA.json"]
        result["predictor_name"] = getattr(self.predictor, "name", type(self.predictor).__name__)
        result["predictor_mode"] = getattr(self.predictor, "mode", getattr(self.predictor, "name", None))
        if hasattr(self.predictor, "model"):
            result["predictor_model_ref"] = self.store.put(self.predictor.model)
        result["initial_graph_ref"] = self.store.put_graph(result.pop("initial_graph"))
        for gate in result["gates"]:
            gate["public_snapshot_ref"] = self.store.put(gate.pop("public_snapshot"))
        result["prediction_evidence_ref"] = self.store.put(self.prediction_records)
        result["evidence_store"] = str(self.store.root)
        result["fusion_contract"] = "current delivered POSITION overrides active residual with original R18 linear all-history projection; no joint posterior claim"
        if self.output_dir:
            write_json(self.output_dir/"episode.json", result)
        return result
