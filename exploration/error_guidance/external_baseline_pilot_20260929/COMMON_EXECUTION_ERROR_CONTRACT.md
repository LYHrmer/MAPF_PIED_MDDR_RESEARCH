# Common execution error adapter: proposed interface v0

2026-09-29. **Specification only. No continuous execution, disturbance, learning model, or external-method comparison has been run by this artifact.** The accompanying GPIBT pilot runs the author's discrete nonrotation model. This contract is the next implementation boundary, not evidence that GPIBT already supports these signals or safety guarantees.

## Identity and comparison scope

Maintain two separate result tables: (R0) official method in its native environment with disclosed observation/seed patches; (R1) official method plus the same execution adapter. Pin each upstream commit, method configuration/checkpoint, patch hashes, dependency versions, controller/physics configuration, map/task files and units. Never compare PIE-D native time or B1 costs directly with the discrete GPIBT pilot.

The initial external pair should be official GPIBT and official OnlineGGO with the released learned policy actually loaded and invoked. A static OnlineGGO build flag or a GPIBT copy vendored in OnlineGGO is not the published learned method. Reject a claimed R1 comparison if one method gets a different safety controller, feedback schedule, robot footprint, error envelope, task visibility, planning time cap or execution clock.

Published baselines remain published algorithms; the shared adapter is a disclosed extension to their execution domain. Motion-only, same-information analytic waiting, last-END, lag-2 and learned residual variants are internal ablations. They must not substitute for external published baselines.

## Four separated records

All records carry `schema_version`, `trial_id`, `agent_id` where applicable, monotone `sequence`, explicit `clock_domain` and units, and immutable source/config hashes. JSON timestamps and quantities use canonical decimal strings plus units, or exact rational strings if the engine has exact values; do not silently convert an exact engine value to binary64. Absence is explicit `null` with a reason. Do not turn an unreceived event into a zero measurement.

| Record | Mandatory content | Who may read it |
| --- | --- | --- |
| `WorldConfig` | map coordinate transform/cell width; static obstacles; robot shape; public velocity/acceleration limits; declared spatial error set; controller and braking rule; initial public state; task release/visibility rule; planner/update/observation budgets; physical horizon | All methods, byte-identical within each paired trial |
| `PlannerView` | decision time; currently released task IDs and goals; latest delivered pose/progress observations with sample and delivery timestamps; public caps/pauses and acknowledgements; pending command IDs; admitted motion/occupancy commitments; traffic features derivable from the same delivered history | All methods through one immutable serializer |
| `PlanProposal` | view hash; monotonically increasing proposal ID; ordered candidate grid waypoints or joint next actions; action IDs; proposed departure order; optional predicted residual and uncertainty with training/model hashes; measured computation time | Shared adapter; prediction never grants motion authority |
| `ExecutionEvent` | command accepted/rejected/started; timestamped delivered observation; command finished; stopped/resumed; task assigned/completed; safety/timeout/contract failure; reason and authority/evidence IDs | Methods only once delivery time is reached; evaluator also retains raw event stream |

Hidden `WorldTruth` is a separate evaluator-only stream containing actual pose/velocity, disturbance realizations, unreceived sensor samples, future task releases and future completion times. A planner receives no simulator object, private controller, condition label encoding disturbance, future random state, or offline route rollout. Learning samples become available only after the corresponding event has actually been delivered. Split training and evaluation by whole trajectory/scenario/seed, with no shared-episode labels crossing the split.

## Delay and spatial error are separate interventions

Use distinct, versioned parameters for (a) velocity/acceleration or pause disturbances, (b) sensing/communication delay, and (c) spatial tracking deviation. A delayed grid move is not a spatial error experiment. A nonzero promised error box with a nominal center trajectory tests conservative occupancy; it does not demonstrate realized tracking deviation. If the third claim is made, execute and log actual two-dimensional deviations under the declared controller and verify their bounds.

Freeze a method-independent exogenous disturbance field before paired trials. Its indexing uses scenario/agent/physical time or documented spatial region, rather than a mutable random generator consumed whenever a policy requests a prediction. Different chosen paths may encounter different portions of the same field; do not force equal realized outcomes after choices diverge. Disclose which signals make the residual predictable. Do not manufacture otherwise unobservable noise and claim it demonstrates a need for learning.

The engine checks `actual_pose − reference_pose ∈ error_set` throughout admitted motion, with explicit monitoring/enclosure precision. Exceeding the envelope is a contract failure reported for that arm; never clip the recorded error or silently widen the promise. Finite sampled checks alone are reported as sampled checks, not continuous-time collision proofs.

## Admission, feedback and terminal ownership

The adapter validates every proposal against the same delivered-state snapshot and motion feasibility rule. A synchronous GPIBT action is a proposal; it cannot update a robot's grid location before physical completion. The implementation must choose and document either synchronized joint action boundaries or a replanning interface that uses actual delivered asynchronous state. It must not advance nominal discrete time while some agents are physically elsewhere and still treat the old graph collision guarantee as sufficient.

Only the shared executor may admit/reject motion. Admission must protect the entire swept robot footprint plus error envelope and reservations against obstacles and other agents. Its safety argument must state required geometry, braking, feedback and disturbance assumptions. Neither an unchanged grid validator nor an imported ADG guarantee automatically covers arbitrary footprint/error choices. If no proposal is admissible, use a jointly verified hold/braking action; independently commanding every agent to wait is not automatically safe when others are still moving.

Normal END comes from the completed commanded motion (actual endpoint plus declared velocity/settling condition) and becomes visible only at its delivery time. Retiring a moving reservation must atomically retain endpoint stationary occupancy. A predicted arrival, elapsed nominal duration, or evaluator-only position cannot retire a reservation. Task completion uses the same physical service criterion for every method; task ID, assignment/release time, service time and agent are recorded. Future tasks are visible only according to the author/application contract.

Each event stream includes proposal, admission and command IDs, so offline replay can distinguish planning, waiting for authority, physical motion, observation delay and terminal residence. At horizon, unfinished commands/tasks and all remaining occupancy are preserved. Timeouts, infeasibility and lost safety contracts remain outcomes rather than disappearing from successful-run averages.

## Metrics and cost

Predeclare either a constrained optimization objective (e.g. task throughput under one common compute/query budget) or a weighted task/cost objective with an externally justified fixed weight; otherwise retain the task/cost Pareto trade-off. Do not tune the objective after observing a preferred predictor's result.

Record the complete task-completion curve, completed and pending tasks, per-task release/assignment and service times, physical makespan where defined, energy only if the simulator supports it, and censored task ages. Completed-task mean flow is conditional on completion. In lifelong one-visible-task-per-agent roundrobin, all-assigned restricted flow over a fixed horizon is exactly `N × horizon`; it is a useful accounting identity and not a discriminating performance measure. If task availability is method-dependent, disclose the exposure difference instead of comparing identical-looking task IDs across arms as if they were the same job.

Record planner/inference/update/training/adapter/safety-check time, observations and transferred bytes separately. Historical data acquisition is counted under a common protocol. Host wall time, simulated physical time and production metered costs are distinct columns. The current pilot provides only native host planning/wall time and discrete steps; it supplies no query price or production COST.

## Smallest acceptance gate before a comparative experiment

1. **R0 conservation:** zero-error/no-delay mode reproduces the fixed seeded author discrete actions/tasks when the adapter promises a synchronous reduction. If this reduction is not possible, explicitly identify the changed execution semantics and establish a separate zero-error R1 reference.
2. **Causality:** replay views with altered evaluator-only future labels; all proposals before the altered information's delivery remain unchanged. Reject forged early END and mismatched command/view IDs. All baseline arms receive identical observable fields.
3. **Safety and termination:** offline replay checks actual footprints/swept paths under the declared numerical precision, including a narrow passage, delayed move, normal END with retained endpoint, and horizon-censored motion. Deliberate invalid traces must be rejected by the checker.
4. **Cost equality:** log actual predictor and adapter work for every arm; a learned predictor may only change ranking. It cannot bypass the common admission path.
5. **Scientific gate:** on a separately frozen small paired holdout, test whether legal context predicts residual wait beyond same-information analytic motion/traffic and simple seasonal/conditional baselines. Only then train a more complex learner. Stop the learning claim if residuals are zero or simple controls explain the decision improvement. Keep valid non-learning execution-aware results if they answer the declared task objective.

Passing these gates licenses a bounded comparative pilot, not a claim of general safety or publication-level performance. The next paper experiment must use multiple author-supported maps/workloads and independently seeded runs after this interface is working, with the workload list and paired statistical unit fixed in advance.
