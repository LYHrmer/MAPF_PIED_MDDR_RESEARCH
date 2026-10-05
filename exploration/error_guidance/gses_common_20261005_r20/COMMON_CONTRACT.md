# Runnable common executor, limited ordering model

`common_engine.GSESCommonSimulator(case, disturbance=None, seed=0, *, predictor=None, config=EngineConfig(...)).run(policy=None, probe_override=None)` accepts the same public callback, case schedule, disturbance and predictor interface as the frozen R19 engine. It inherits R19's whole delivered END history, occurrence-bound POSITION delivery, active commitments, cursor execution, MOVE/WAIT/GOAL_HOLD trajectory output and continuous point collision check. An explicit `output_dir`, `cache_dir` and shared `evidence_dir` are required. `gses_quantum=1.0` and `gses_max_new_calls=4` are mechanical defaults, not a registered large-matrix configuration.

The optimizer is the existing R13 JSON wrapper around the unchanged Improved GSES author source, commit `25fb931eff03f1cce23a22a68ab42b7533f85ab3`, MIT licensed. Execution graph compilation remains the separately identified frozen R16/R19 SADG compiler and all-heads/k0 adaptation; it is not relabelled as STPG code. No SADG MILP is called by this subclass.

## Mapping

1. Native arrival state zero is the original start. State `i+1` is SADG action `i`'s END location. Original nominal path timestamps are retained for the author Graph constructor. The current state is the number of completed actions. Stationary agents remain in the common executor and require no optimizer path.
2. The current in-progress type1 edge uses only its public predicted remaining duration. Future type1 edges use the public predicted duration. Durations become `max(1, ceil(duration / quantum))` integer ticks. An active action with zero predicted residual still occupies at least one native tick until END arrives.
3. Each live SADG tail-END → head-START relation becomes a native tail-arrival → head-arrival edge of **one tick**. The adjacent reverse relation must exactly match native `(head+1, tail-1)`; otherwise the adapter rejects the mapping. Already satisfied dependencies are omitted from the live native suffix and restored unchanged in the execution graph.
4. The returned native graph must preserve all paths, current states and type1 edges, contain exactly one orientation of every translated family, and choose uniform bits within each original SADG group. A partial native grouping result is rejected. Original R19 qualification, horizon, active-head commitment and whole-DAG checks then decide adoption; rejection restores the complete parent graph including cached group-head handles.

The type2 mapping is exact for the elementary one-tick arrival separation interpretation. For heterogeneous action durations, a continuous tail-END → head-START constraint would require a head-action-dependent arrival gap. Reverse direction may require a different gap. The original R13 author wrapper stores the same weight for both directions, and the unchanged author search uses a unit test/heuristic. Consequently this implementation is an **integer arrival ordering surrogate with common execution**, not an exact optimizer for continuous SADG predictions. The `.01` SADG model margin is not silently substituted into STPG. Time scaling does not solve this structural mismatch.

## Evidence and failures

Every solve stores the public encoded input, source-bound exact-input cache key, original command/receipt/stdout/stderr/reply, native graph objective, full before/candidate/after graphs and original guard. Graphs and predictions use unchanged R19 lossless CAS references under `common_evidence/`; decode with R19 `evidence.EvidenceStore.get` or `.get_graph`. Native replies are cached only for an identical complete native graph plus original binary hash and method. Reference search/author durations are retained on reuse; only actual new wall time and invocation counts become zero. Cache timing is diagnostic, not a production cost or a speed comparison.

Author errors, timeouts, mapping errors and guard rejection retain the parent graph and are visible as `GSES_SURROGATE_FALLBACK`. The author limit is 16 seconds in the existing ELF, outer limit 20 seconds. Those limits differ from SADG's original 60 seconds, so this mechanical work does not establish a fair time-budget performance comparison. The tiny Fraction oracle supports independently enumerating one reversible dependency; it is deliberately not reused as an independent-group proof for arbitrary large SADG groupings.

The cache writer is atomic, but no cross-process key lock is provided. Future parallel callers must serialize identical keys or add a separately reviewed lock to prevent duplicate computation. This qualification used a single worker. The runtime call cap is explicit; reaching it records fallback, and must not be mistaken for episode completion or a scientifically valid large benchmark configuration.

## Run and inspect

The registered calls have already run and the scripts intentionally refuse repeats. To inspect the existing evidence without new native calls:

```bash
rtk proxy /home/lyh/.cache/mapf_research/sadg-r16-venv/bin/python exploration/error_guidance/gses_common_20261005_r20/final_audit.py
```

The audit command refuses to overwrite its frozen final output after publication. `phase1.py`, `schedule_fix.py`, `phase2.py` and `phase3_switch.py` record their source/input hashes and start markers before each new call. Reproduction elsewhere should use a new isolated output directory and a new registration; never delete the completed markers to make a script run again.
