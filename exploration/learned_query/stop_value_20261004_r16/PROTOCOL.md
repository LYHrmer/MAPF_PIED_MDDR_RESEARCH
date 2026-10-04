# R16 preregistered C versus STOP mechanism experiment

This is exploration on old R13 TRAIN/CAL scenarios with a new complete action tail. It is not an independent final test. No old TEST raw traces, labels or model artifacts are used. No changes to R13/R14, README, Git commits or production code.

## Native contract and reuse

Copy R13 joint_history_native.cpp and change only the actor policy options/selection and allow-list: macro_STOP follows condition until the earliest public eligible gate with spent >= floor(B/2), capacity > 0. At that same pre-action gate it chooses STOP. Thereafter all QUERY/SKIP scores are zero (WAIT). Normal END, physical motion, public history, candidate visibility, planner, FIFO reveal, safety and H=128 continue unchanged. STOP never means stop the robot, end an episode, remove a commitment, or withhold normal END. No gate means condition throughout and the observation remains in the denominator.

Use all 12 R13 TRAIN families (six per map), B8/B16: 24 new STOP episodes. Existing C is reused only after exact world/rendered-input/source/bridge/config/hash verification. For each map's lowest-offset TRAIN B8, run one new macro_C under the R16 binary and require full canonical event/planner equality to the old C (only policy and native check count ignored). This is two necessary semantic compatibility checks, not new scientific replications. Full physical/public prefixes before the actual gate and the gate identity/features must match for every pair. No outcome-based filtering or replacement.

The old C and new STOP do not share a cache key: reuse manifest records their distinct source/binary provenance and complete input/bridge/config hashes. Private per-agent, per-occurrence disturbance rows are identical between arms (not merely equal seeds). Public planning actions after the gate can legitimately change. Original source before the actor choose method and between its end and main must be byte identical; the allow-list change in main is explicit.

## Costs and outcomes

Primary consequence is total FIFO task services through H. Restricted T is the sum of completion times for each agent's fixed first four FIFO tasks, with unfinished tasks assigned H=128. Report rigorous exported rational intervals, all-task service time sum, released-head restricted flow time, QUERY count, residual budget, zero/negative outcomes, host runtime, normal END count and moves. No conversion to production COST or invented monetary fee. QUERY count is a unit-query cost proxy, with unit monetary charge unspecified.

Report an explicit waiting decomposition over 16*128 agent-seconds: physical MOVE occupancy (including censored active MOVEs), physical-end-to-normal-END feedback hold, and residual not-moving time. This residual includes readiness/resource/planner waits and is not falsely labeled pure resource waiting. All are derived from raw lifecycle intervals; interval uncertainty retained. Physical safety uses the original independent Decimal audit at all event frames, ownership and collision checks, and FIFO/normal-END replay.

Material preference is task-first: STOP if delta tasks > 0, C if < 0; when tasks equal, STOP if T_C - T_STOP >= 1 second by interval lower bound, C if <= -1 by upper bound, otherwise neutral. Threshold is a prespecified material scale, not a significance level. Report all finer changes too. Families, not the two budgets, are independent sampling units.

## Conditional simple model (registered before TRAIN)

Activate only if at least one TRAIN context materially prefers STOP and at least one materially prefers C, and at least eight eligible gated TRAIN contexts exist. Otherwise no fitting or CAL simulations. This diagnoses opportunity, not guaranteed learnability.

Use the ten R13 late_target10_v1 public gate features, no IDs/map/seed/hidden truth. A depth-one regression tree has two leaf outputs: mean delta tasks and mean (T_C - T_STOP). Every budget row weighs 1/2. Enumerate feature indices 0..9 and midpoints of adjacent distinct TRAIN feature values in increasing order, requiring at least four rows in each leaf. Minimize weighted squared error of the scalar label delta tasks + time gain/16385; strict comparison retains the first tied split. Split only if its loss is strictly lower than the constant root. Leaf predictions are exact rational means, with exact rational inference. Select STOP if predicted task delta > 0, or if predicted task delta = 0 and predicted time gain >= 1; otherwise C. No CAL threshold or hyperparameter selection, no refit after CAL.

CAL is fixed before TRAIN: take families alternately by map (empty first), increasing offset, first three: empty offset192/seed131201; random offset224/seed132201; empty offset208/seed131202, each B8/B16. The fourth existing CAL family is not used this round. This three-family cap is a compute compromise, not a representative validation set. Six new STOP tails plus cached C, only if activation passes and the model is frozen first. Single-gate fixed-tail inference selects an already verified complete C or STOP trajectory; no duplicate native simulation is needed. Compare learned selector, fixed C, fixed STOP and the finite option oracle, reporting selected-arm hashes. This is exploratory held-out-family validation on old CAL environments; it is not a fresh TEST.

## Execution bounds and integrity

At most 32 new native episodes: 24 TRAIN STOP + 2 C compatibility + conditional 6 CAL STOP. Four native workers maximum, at most two independent audit workers. Register sources, worlds, old-C hashes, physical pins, binary and protocol before the first new native. Preserve errors, do not overwrite completed receipts, do not rerun failed science without explicit amendment. Compile/pure checks do not count as episodes. Model and activation source frozen before TRAIN; frozen model receipt before CAL. Every result carries input/raw/planner/receipt hash and whether it is reused.
