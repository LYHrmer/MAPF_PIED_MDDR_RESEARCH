# R18 public-information policy and benchmark source review

Decision: qualified for the registered exploratory benchmark after the structural pilots; no claim that the learned policy improves performance is made by this review. The research-mentor qualification remains conditional for a publishable information-value contribution. Author R0 and the registered adapter exist, data and the finite-task execution contract are concrete, and the new multi-map claim still requires actual held-out results.

This reviewer edits only `review/`, imports no engine/policy module, and launches no ECBS, SADG or scientific episode. The frozen source hashes belong to `../EXPERIMENT_REGISTRATION.json`; original and failed attempts remain outside this review untouched.

## Authoritative implementation locations

| Contract | Source location | Independent evidence |
| --- | --- | --- |
| Public duration/history and measured-age projection | `engine.py:410` / `419` / `431` | END records and accepted capture bodies reconstruct ratios, CV, count, progress and remaining duration |
| Public callback whitelist and graph influence | `engine.py:444` / `479`; `PUBLIC_SCHEMA.json` | Every snapshot key checked; outgoing heads and switchable influence reconstructed from raw graphs and completed events |
| Captured active occurrence, stale discard | `engine.py:479` / `500` | Query body hash, physical capture point, delivery time, ended occurrence and subsequent snapshot |
| Same original author solve, transactional adoption | `engine.py:525` | Full before/after graph, exact source/input key, cached model, all candidate heads STAGED, DAG, START dependencies |
| Unchanged physical cursor, completion and residence | `engine.py:332` / `368` / `384` / `612` | Serial START/END, full MOVE/WAIT/GOAL_HOLD coverage and analytic continuous point distance |
| Complete history rule and fixed mismatch floor | `policies.py:73` / `113` | Formula below; no private condition classifier |
| 22 public features and learned threshold | `policies.py:43` / `121` | Independent feature construction, saved prediction and action reconstruction |
| Family-weighted preprocessing/ridge | `policies.py:142` / `163` | Each fold's weights, moments, normal equation, held predictions and MSE independently reconstructed |
| All scientific pins and shared budgets/clocks | `run_benchmark.py:92` / `131` / `152` | Frozen registration, STARTED/RUN receipts, original case hash and input equality |
| One probe, same continuation, no future-based candidate | `run_benchmark.py:206` / `226` | Raw paired physical/public prefixes, actual empty versus singleton selection and complete outcomes |
| Final freeze before CAL/TEST | `run_benchmark.py:297` / `318` | Model/row hash and UTC receipt ordering, each evaluation's model hash |

Line locations refer to the scientific freeze of 2026-10-05. The source files, rather than these line numbers, are the authority.

## Strong public-history comparator

Let `d` be the original nominal duration, `r=max(1,history_ratio)`, `u=d*max(0.25,history_cv)*r`, `late=max(0,elapsed-d*r)`, `remaining=max(remaining_estimate,late,0.25*d)`, `b=outgoing_blocked_agents` and `m=measurement_count`.

The rule score is `b * min(remaining,u+late) * (1+min(2,downstream_nominal/d)) / (1+m)`. A current-occurrence observation younger than `0.5*d` gives score zero. This cooldown is policy behavior; the common eligible action space remains all IN_PROGRESS occurrences. Candidates with positive score are ordered by descending score then agent ID, subject to the same N total and ceil(N/8) gate budgets as the learned and fixed policies. The explicit uncertainty and overdue floors prevent clamped public progress=1 from incorrectly eliminating a still-running blocker.

This rule is an internal comparator on the published SADG optimizer, not an independently published algorithm. It receives exactly the same public history and graph fields as learning. The unbudgeted dense arm is an information-cost reference, not an equal-budget competitor.

## Learning estimand and split

The label is `restricted_sum(noquery)-restricted_sum(query one selected agent)` at preselected gates 1 and 3, with the same deterministic history policy before the probe and after it. Query consumption naturally changes later remaining budget. Full raw trajectories, original inputs and action-keyed private disturbances must match before intervention. Two solver objective values are not labels. An unmodified history episode can be reused only when its actual probe action equals the intervention.

Candidate selection is strongest public history score at gate 1 and greatest downstream nominal duration at gate 3, then agent ID. Missing gate, absent eligible candidate, exhausted budget and invalid execution remain in the registered denominator. TRAIN collection may require up to 54 baseline episodes plus 216 paired arms before exact reuse. The registered fixed update period is `max(4, public ECBS makespan/12)` throughout each full episode; there is no three-gate execution cutoff.

Each map/scenario family includes every nested N=8/16/32 view, disturbance and probe. TRAIN scenarios 1/2 yield six families; CAL 3 is diagnostic only; TEST 4/5 yields six new scenario families on the same three map types. Family-weighted ridge chooses alpha in {1,10,100} by TRAIN leave-one-family-out MSE. Feature moments are fit on each training fold only; the intercept is unpenalized, alpha ties choose the smaller value and query threshold is fixed at 1e-8. The final all-TRAIN model freezes before every CAL/TEST learned execution.

LOFO also selects alpha, so the selected TRAIN CV score is a model-selection diagnostic, not a nested unbiased policy estimate. Deterministically selected probe candidates provide limited state/action support. The single-query label identifies value under the history-rule continuation; deployment changes subsequent continuation and may select batches of 2 or 4 queries. Their values need not add. The benchmark therefore tests a concrete value-learning heuristic by actual complete held-out episodes; it does not claim to have learned the optimal policy or a globally correct causal Q-function.

## Statistical and physical boundaries

The restricted completion objective counts unfinished agents at the same registered H; safely completed count and episode status are reported alongside it. Collided completions cannot be silently counted as safe success. Queries, bytes, solver calls, reference work and newly incurred work remain separate quantities. A cache hit is not evidence that its later policy is intrinsically faster.

Physical simulation advances through the fixed 0.25 observation latency. Measured author/MILP wall time is reported separately and does not advance the simulated physical clock. Thus the experiment supports a synchronous event-simulation comparison, not a claim that a deployed real-time optimizer can meet those decision deadlines.

The analysis source preserves all 54 TEST-world denominators per arm, shows legal-pair coverage, and bootstraps map/scenario family means without separating nested team sizes or disturbance variants. Six families on three shared map types provide descriptive uncertainty for this benchmark; they do not justify broad map-family generalization. Simulation is continuous point-agent fixed-path execution, not a footprint/dynamics guarantee or an open lifelong task stream.

## Audit entry points

`audit_episode.py --episode <path> --case <case-path> --policy <arm> --output <review-output>` reconstructs one immutable episode. Add `--model ../MODEL_FROZEN.json` for the learned arm.

`audit_study.py` audits finished TRAIN RUN_RECEIPTs and available pair/model evidence. It reuses only audit outputs whose raw episode hash and verifier source hash match. `--splits TRAIN CAL TEST` additionally audits evaluation once the frozen-model receipt exists and matches the model. `--learning-only` reconstructs labels and all model equations without touching execution. No command calls an author optimizer or simulator.
