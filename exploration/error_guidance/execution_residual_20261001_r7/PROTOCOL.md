# R7 execution residual mechanism, frozen before new native runs

This is an isolated exploratory method, not a qualified publication claim. R6c
24 complete logs are used only for action-state diagnosis. R4 priority bias is
not reused. R6c S1 controller, parser, normal ACK, FIFO and joint-settled gate
are unchanged. The gate's limitation is retained and measured, not silently
called asynchronous execution.

## New runs and information

All maps use public MovingAI empty-32-32 and random-32-32-10. N=8, H=4000 ticks
at 10 Hz. Whole-run task/initial-priority seeds: train 931701/931702, calibration
931711, test 931721. Conditions for each map/seed: nominal, slow065, axis for
train/cal; nominal, axis, unknown_shift for test. Each agent's entire FIFO is
generated independently before any run, including the first target; starts
remain the official random-1 first eight starts. No test outcome selects a
model, scene, parameter, horizon or arm. Deterministic physical error laws use
the unchanged native R4_CONDITION actuator wrapper; they have no stochastic
error seed. All methods in a world share the exact law and FIFO.

Training and calibration use unchanged author OBJ3 hm+GPIBT only (12+6 runs).
Test has original OBJ3, original OBJ4 with the same old 560-parameter flow
checkpoint, OBJ3+history cost and OBJ3+learned residual cost (6 worlds×4=24).
Original baselines retain all object hashes. Candidate search.cpp is explicitly
a modified method: one nonnegative edge-cost addition, all other original
objects and actor priorities unchanged. Failed/zero/negative runs stay.

The actor receives only current planner starts/orientations/goals, parsed
public proposals, admitted action IDs/geometries, and normally accepted END
identities/timestamps. Public projection drops every observation and control
field before history extraction. It receives no condition label, private pose,
front/first-wheel timing, speed, future target or future ACK.

For each one-cell action, duration is final normal MOVE ACK tick minus proposal
tick, including dispatch wait, any ADG wait, turns and both half-MOVEs. It
excludes subsequent STATION dwell. Censored moves have no supervised target
and are retained separately. A label cannot become history before its own END.

## Fixed predictor and cost

Nominal prior is 45+10×quarter_turns ticks. Inputs are candidate direction,
quarter_turns, prior completed whole-step durations, direction-conditioned
duration estimates, and history count. No robot-ID feature. Ridge lambda=1,
unpenalized intercept, train-only mean/scale; target is duration minus nominal
prior. Same-history nonlearning control uses the mean of the last eight
completed same-direction residuals, shrunk with two zero-residual pseudo rows.
Both predictions clip to [5,200] ticks. Calibration fixes each method's 90th
percentile absolute error using rank ceil(.9×(n+1)), capped at n. The cost uses
predicted duration plus this calibration error; it is a pilot uncertainty
margin, not a distribution-free guarantee under temporal dependence/shift.

For each other agent, distribute unit mass uniformly across goal-decreasing
neighbors for two public shortest-path hops; each destination receives mass
times (clipped predicted duration+margin)/(45+10×initial candidate turns),
discounted by 1 and 1/2 for the two hops. Sum these nonnegative dimensionless
costs over other agents. Add once to the original unit-length+SUM_OVC edge
cost. Scale=1, depth=2 and discount=1/2 are fixed before data. The source agent's
own projected occupancy is excluded. Guidance is recomputed at the original
author update occasions; no forced all-agent refresh is introduced.

Train/cal native executions finish before fitting/checkpoint freeze; test is
blocked until freeze. Primary endpoints: normal STATION END, all task censoring,
legality/ACK/FIFO audit, prediction error and coverage, actual candidate edge
cost calls, action differences and task-service differences. Costs and planner
wall time are recorded. At one test seed per map/condition there is no claim
of general statistical superiority. This cost is a planning heuristic and does
not alter author collision/ADG/ACK admission rules or certify continuous safety.

R6 diagnosis classifies exactly one final wheel-command state per agent/tick.
It separates MOVE/TURN/STATION control, active pause, reconstructed unresolved
type-2 dependency, dispatch wait, queue-empty joint barrier, physical settling,
and all-empty planner-boundary idle. Sampled center distance is auxiliary;
controller speed_cm_s is not treated as measured body velocity.
