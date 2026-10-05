# R18 online author adapter and event engine

This engine implements the approved research interface, not a new optimizer.
The original author SADG MILP, objective and hardcoded 60-second solve cap are
unchanged. The separately named R16 k0/all-head compiler adapter is shared by all
policies. The root owns dataset/protocol/model selection and the matrix runner.
This file and `engine_smoke.py` concern engine semantics and bounded pilots only.

```python
from engine import Simulator, EngineConfig, DensePositionPolicy
cfg = EngineConfig(solve_period=4, query_latency=.25, query_budget=16,
                   max_queries_per_gate=2, max_time=2000,
                   cache_dir="/tmp/r18-pilot-cache", output_dir="/tmp/pilot")
result = Simulator(case, disturbance, seed=10, config=cfg).run(policy,
                      probe_override={1: []})
```

Case accepts `solution.schedule` or top-level `schedule`; `dimensions` defaults
to resolution2/offset0, or accepts the original nested author dimensions object.
Agent names follow original ECBS `agent0`, `agent1`, ... . The author transform is
`(x,y) -> (resolution*y+x_offset, -resolution*x+y_offset)`.
Full policy JSON contract is [PUBLIC_SCHEMA.json](PUBLIC_SCHEMA.json).

The first gate is at `solve_period`, after dispatching the original valid graph.
At a gate the policy sees only delivered public history, START, previous POSITION
and current graph influence. Only selected currently executing agents are
captured. Every policy solves at gate time + common latency; motion and END
continue between capture and delivery. Stale occurrences cannot update the
successor. `probe_override` changes only explicitly listed gate queries;
unspecified gates use the same callback. An absent gate remains absent in a
short finished episode, not an exception. Empty active sets yield legal empty
query selection. DensePositionPolicy is explicitly unbudgeted; all other
policies share finite episode and per-gate caps. Root supplies the benchmark's
fixed/history/learned policies; engine's simple policies are smoke conveniences.

Public duration model is total delivered actual MOVE duration divided by total
original nominal duration; before any END its ratio is1 and history_count0.
Every future/current duration is ORIGINAL author `polyline_length/2 m/s` times
that ratio. Completed vertices use their delivered duration. Active normalized
progress comes from elapsed/history, or latest delivered capture plus its actual
age/history; prediction clamps at1 even when a MOVE is overdue. This is a cost
prediction limitation, not authority to complete, release or change a running
MOVE. Root's uncertainty rule can explicitly account for overdue execution.

Private disturbance is keyed by seed/agent/action, independently of policy and
execution order. `kind` is `stable`, `bounded_pause`, or `speed_shift`:

- `affected_fraction` defaults1; `stable_factor` (speed multiplier) defaults1,
  optionally `stable_factor_range=[lo,hi]` for deterministic per-agent variation.
- Pause: `pause_probability` default1 per affected action,
  `pause_fraction` default.35 along the action, `pause_duration` default1 second,
  optional bounded `pause_duration_range`. Motion resumes at its original rate.
- Shift: `shift_action_fraction` default.35 of that agent's action count;
  `shifted_factor` default.5 from that action onward.

Rates must be positive and pauses finite. This is action-relative process noise,
not exogenous absolute-time traffic. Gate selection never receives these values.
For auditing, truth profiles appear only in the final episode's `private_truth`.

Each agent has one cursor. Only that cursor can start through original
`Vertex.can_execute`; previous action must be COMPLETED. Running commitments
cannot be revoked. A solve changes only qualified staged dependency directions;
full graph/paired edges/type1/status preservation and DAG are checked. Exceptions,
infeasible solves and unsafe candidate changes are logged and restore the parent
directions. Solver feasible status does not by itself prove physical safety.

Compiler WAIT tuples are bundled into subsequent distance-based MOVE vertices;
planned time waits are replaced by dependency waits, as in the author action
model. Trailing WAIT leaves a resident at its goal. Pure stationary paths are an
explicit resident adapter: they are removed only from the optimizer's otherwise
empty per-agent vertex list, retained physically and in metrics/collision checks,
and never replaced by fictitious zero-time movements. Initial waits, dependency
waits, disturbance pauses, moves and goal residence are all logged as continuous
segments. A two-pointer sweep over every agent pair checks affine minimum distance
over full overlap intervals, including initial and terminal occupancy. This is
point-agent verification, not robot footprint/acceleration certification.

Episode schema `r18-sadg-episode-v1` includes:

- `initial_graph`: all vertices/statuses/polyline tuples/type1/dependency groups.
- `events`: public START/END/POSITION_DELIVER and explicitly private PAUSE events;
  time key is `time`; END contains start/duration/original nominal duration.
- `gates`: complete public_snapshot, selected agents, capture_time/solve_time.
- `queries`: captured agent/occurrence/progress/time, geometry binding, intended
  delivery, accepted/stale/pending status and canonical body hash.
- `solves`: exact input key, complete source hashes, objective/bound/status,
  constraint residual summary, before/after hashes, guard and timing receipts.
- `segments`: agent,vertex,t0,t1,p0,p1,kind; all WAIT/GOAL_HOLD included.
- `completion_times`, `sum_completion`, `makespan`, query/payload counts and costs.
  `production_cost` stays null. Failed/truncated episodes have null completed-path
  sum/makespan unless all agents actually finished, plus completed count and
  `restricted_sum_completion=sum(T_finished)+N_unfinished*common_max_time`.

Shared disk cache keys include every original graph vertex/status/normalized
progress/duration/path, active forward/reverse group direction and qualification,
horizon, author/adapter source hashes and Python-MIP version. Only feasible
guarded calls are cached. Exact cache reuse reports inherited reference duration
separately from new wall/solver work: do not charge later policy arms only their
cache misses or claim a speed benefit from execution order. Cached choices retain
the author's original tie decision. Optional `save_models` saves full constraints
for newly solved targeted audits; reused results point to their cache source and
model SHA. Every successful unique cached input also stores the complete compressed
model at `<cache_dir>/<semantic_key>.model.json.gz`; the atomic index JSON is
`<semantic_key>.json`, with `model_file`, `model_file_sha256`, `before_sha256`,
full after graph and model receipt. Each solve exposes `cache_source` and
`cached_model_file`. Independent auditors can therefore read all constraints
without repeating an optimization, even when per-episode save_models is false.

After the last END, pending POSITION transport is drained with all agents held
at their goals. `simulation_end` may exceed task makespan by transport latency;
task completion times do not change. Truncated episodes retain their pending
query count explicitly. Requested but never reached probe gates appear in
`unreached_probe_gates` and do not make a completed episode fail.

Smoke plan: official small ECBS fixture online rollout, matched exact cache reuse,
stationary/initial-goal occupancy and latency occurrence checks, then one available
standard TRAIN8 plan. At most12 new author calls for structural qualification;
no full matrix, CAL or TEST pilot. Every failed pilot is kept. No declaration of
engine qualification is made until the smoke receipts exist.
