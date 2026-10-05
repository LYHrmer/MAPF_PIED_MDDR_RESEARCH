# Frozen R18 engine validation notes

The generalized author adapter is ready for the root's registered collection,
subject to the separate independent review. Engine ownership is limited to
`engine.py`, `PUBLIC_SCHEMA.json`, engine smoke/unit code, and these notes.
Dataset generation, benchmark protocol, policies/model selection and matrix
runner belong to other agents. No CAL/TEST policy pilot was run by this agent.

Structural pilots completed eight new author optimizations in total:

|Pilot|Agents|New calls|Result|Scope|
|---|---:|---:|---|---|
|Official original ECBS test, online stable speed0.8|4|3|All completed; Σ37.5, makespan15.625; min point distance2.5|Multi-epoch author invocation and dated dense capture|
|Same complete official input/cache replay|4|0|Exact completion/query results and inherited solver timing|No second scientific solver call|
|Stationary resident plus moving agent with bounded pauses|2|1|All completed; resident retained; no collision|Empty-author-vertex lifecycle handling|
|First standard TRAIN8 random-map path|8|4|All completed; Σ219, makespan54.75; 1937 overlapping segment checks, min point distance2|Arbitrary original ECBS schedule and dynamic disturbances|

These pilot metrics establish structural behavior and runtime plausibility only;
they are not comparisons used to tune query policies or claims of benchmark
performance. Standard pilot cadence was max(4, public plan makespan/4) to bound
qualification calls; the benchmark cadence is separately registered by root.

Nine additional boundary checks used zero author calls: transport after last END,
goal residence through transport, stale occurrence rejection, callback field
privacy, explicit absence of history, common-H restricted completion sum,
unreached probe retention, changed-vertex commitment rejection, and rejection
of a noncardinal polyline shortcut. Tests are ordinary simulator/geometry
qualification, not a production AUTH or robot footprint proof.

Two failed pilot invocations are retained under `engine_smoke/attempt*.json`:
an importlib local-scope error before Simulator construction, and an incorrectly
double-wrapped data plan in the smoke script. Both made zero author calls and
zero completed suffix executions. Neither is silently counted as a scientific
solver failure or discarded map family. The corrected standard-plan loader
accepts its actual `solution.schedule` wrapper.

The final source-pin check uses `git diff --exit-code HEAD`, covering both staged
and unstaged changes, in addition to verifying actual HEAD against the fixed
author commit. This final one-line strengthening followed the pilots; it does
not change graph, prediction, solver or execution semantics. Its read-only git
check was performed before freezing; no native pilot was repeated for it.

Runtime notes:

- Author MILP remains unchanged with max_seconds60 and an outer90s watchdog.
  Successful model adoption checks finite values, every linear row, bounds and
  integrality, followed by the common full-graph/commitment guard.
- Rejected solves restore both original directions and the author's cached
  first-head references used by its horizon predicate. A double switch alone
  would not reliably restore that derived metadata.
- Shared cache JSON/model files are atomically replaced. Full unique models
  are gzip-compressed once in the cache, not required as duplicate episode
  artifacts. This is read-integrity protection, not a multiprocess solve lock;
  simultaneous same-key misses can still duplicate actual work and must each
  be accounted. Root currently collects serially.
- Every cached result reports inherited reference timing separately from newly
  executed timing. Cross-policy timing must not reward later cache-hit arms.
- `simulation_end` includes draining pending POSITION after tasks finish;
  makespan and completion sums remain actual task END times. Canceled final
  all-completed solve opportunities do not trigger extra optimization work.
- Author compiler folds planned WAITs into distance-based MOVE actions.
  Actual dependency/initial waits, disturbances and terminal residence are
  recorded continuously. A cardinal single-displacement invariant is checked
  before using affine interpolation; unsupported grouped geometry is rejected.

Current evidence is continuous point-agent simulation under fixed paths. There
is no ROS, physical footprint, acceleration-control or production query-charge
claim. Public history estimates can be stale or misspecified, and their progress
predictions never complete an action or authorize changing an active commitment.
