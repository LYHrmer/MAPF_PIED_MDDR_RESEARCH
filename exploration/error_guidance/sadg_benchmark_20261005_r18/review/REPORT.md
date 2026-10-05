# R18 independent final review

All 641 completed scientific episodes (236 TRAIN, 135 CAL, 270 TEST) pass the independent artifact audit. The 405-row evaluation summary, 180 strata, paired family calculations and figure data also pass. This review launched zero scientific episodes or solver calls and imported neither the engine nor policy implementation. It verifies the recorded finite benchmark; it does not establish general learned information value.

## Evidence and reproduction entry points

| Evidence | Result | Independent entry point |
| --- | --- | --- |
| Complete episodes, source/input/receipt binding, query accounting, graph adoption, continuous point trajectories and available full models | 641 PASS | `audit_study.py`, `COMPLETED_ARTIFACTS_AUDIT.json`, `episodes/` |
| Paired interventions, public features, family isolation, weighting, fold moments and normal equations | 108 pairs; 19 fits PASS; maximum equation residual 1.654e-12 | `LEARNING_AUDIT.json` |
| Matrix, raw accounting, failures, family bootstrap and figure data | 405 rows and 180 strata PASS | `audit_summary.py`, `SUMMARY_AUDIT.json` |
| Corrupted in-memory evidence | All six negative cases rejected | `verifier_selfcheck.py`, `VERIFIER_SELFCHECK.json` |
| TRAIN label support and fixed-zero reference | Descriptive post-fit diagnostic | `training_diagnostics.py`, `LEARNING_SUPPORT.json` |
| All rejected solver candidates | 11 calls, five distinct inputs; exact parent retained | `failure_diagnostics.py`, `FAILURE_DIAGNOSTICS.json` |

The episode auditor checks task/occurrence conservation, graph dependencies and actual starts; continuous point separation includes waits, pauses, initial occupancy and terminal residence. It reconstructs shared action-keyed disturbances, public histories, policy choices, query capture/delivery/staleness and budgets. Every available accepted full-model payload is checked for constraints, bounds, integrality and objective. Immutable audit reuse binds the verifier and all external dependencies; the logical check count is not a count of independent experiments. Requirements and source-line locations are recorded in `REQUIREMENTS.md` and `POLICY_SOURCE_REVIEW.md`.

## Learning and workload findings

The 108 TRAIN labels contain 106 zeros, one +7 and one −62.5 complete-episode value. Each of six map/scenario families contributes 18 labels. Registered family-grouped fitting selected ridge alpha 100. Its LOFO family-mean MSE is 44.250617, compared with 36.622685 for always predicting zero. The latter is a TRAIN-only post-fit reference, not an executed policy or a basis for changing the frozen model.

All five TEST arms finish 1,008 agent tasks across 54 worlds. Because every episode completes, the restricted completion sums below equal the actual completion-time sums.

| TEST arm | Completion-time sum | Purchased queries | Rejected solver calls |
| --- | ---: | ---: | ---: |
| History only | 67,636.833333 | 0 | 1 |
| Fixed update | 67,636.833333 | 1,008 | 1 |
| History rule | 67,651.333333 | 794 | 1 |
| Learned query | 67,627.833333 | 1,000 | 1 |
| Dense position | 67,645.333333 | 6,009 | 1 |

Learned query improves the aggregate over history only by 9 time units (about 0.0133%) while purchasing 1,000 queries; 53 worlds tie and one improves. Against the history rule it improves by 23.5 units with 206 additional queries: 52 ties, one improvement and one deterioration. These sparse effects do not support a robust general advantage or a query-efficiency claim. Query and completion costs remain separate; no post hoc exchange rate is introduced. Dense position is an uncapped reference.

The paired labels measure a singleton intervention followed by the fixed history continuation. Deployment uses learned decisions across gates and may select batches, so the fitted singleton values are not established additive causal batch values. LOFO selects the hyperparameter and is not a nested unbiased estimate. Held-out scenarios belong to three already known map families; six-family intervals are descriptive. Model freeze precedes every CAL/TEST episode even when their orchestration interleaves. Concurrent wall times are diagnostic, and solver wall time does not advance the simulator's physical clock.

## Rejected solver candidates and evidence limit

TRAIN has zero rejected calls across 236 episodes. CAL has six calls over four inputs, and TEST has five calls over one input. All 11 report OPTIMAL with finite values and zero logged bound/integrality violations, but fail the logged constraint-residual check; the maximum residual is 53.873333. All retain the exact parent graph, have zero adoption rejections and complete physically. These are not successful feasible solves and are not recorded timeouts.

| Split / world suffix | Gate | Arms sharing input | Calls | Logged maximum residual |
| --- | ---: | --- | ---: | ---: |
| CAL maze s03 n32 bounded_pause | 9 | Fixed update, history rule | 2 | 53.873333 |
| CAL maze s03 n32 speed_shift | 10 | History only, fixed update | 2 | 22.48 |
| CAL maze s03 n32 speed_shift | 10 | Learned query | 1 | 22.48 |
| CAL maze s03 n32 speed_shift | 10 | History rule | 1 | 37.34 |
| TEST maze s04 n32 stable | 5 | All five arms | 5 | 6.12 |

All 11 are actual author calls, not cache hits: rejected candidates are not cached, so repeated semantic inputs in distinct registered arms were solved again. `FAILURE_DIAGNOSTICS.json` contains the full semantic keys and receipt paths. Failed full-model payloads were not saved. Their reported residuals and numerical cause therefore remain source-linked/logged evidence; this review cannot independently recompute the failed rows or diagnose a solver numerical cause. Exact parent retention and subsequent physical trajectories are independently verified. No additional solve was run to fill this artifact gap.

## Mentor judgment

The registered benchmark and learning implementation are complete and mechanically auditable within the stated payload limit. The evidence supports a restrained exploratory result: the model is fitted correctly, but the label space is nearly all zero, its selected regression does not exceed the zero-prediction MSE reference, and held-out policy effects are small and sparse relative to query purchases. Subsequent work should retain failed candidate payloads and seek better supported decision-dependent value; this round must remain frozen without retuning on CAL/TEST.

`PUBLICATION_MANIFEST.json` binds this review's files and the final external scientific artifacts. Existing raw episodes and shared models are referenced, not duplicated here.
