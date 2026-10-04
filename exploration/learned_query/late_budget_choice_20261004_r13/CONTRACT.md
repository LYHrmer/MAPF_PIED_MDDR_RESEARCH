# R13 frozen late-budget C/LD learning contract

This new experiment tests whether a public-state model, evaluated at the actual late budget opportunity, improves on fixed late double-SKIP (LD) and original condition (C). It does not reuse R12 TEST as new heldout data and does not change R12, physics, planner, eligibility or safety certification. Root authorization fixes 160 native episodes, maximum six native workers and two original audit workers. No result-dependent new seeds, arms, thresholds or reruns.

## Families and physical scope

N=16, H=128, FIFO reservoir=256 per agent, original unshifted ordinal persistent 9:1 errors, original continuous controller, ownership, enlarged geometry, author GPIBT planner/configuration and normal END latency. Original Move3/World3 and original public candidate/history feature methods stay byte-identical to frozen R12. Only actor macro selection/logging, policy allow-list and experiment runner/learning/auditing change.

Each map has six TRAIN, two CAL and four TEST independent families, each paired at B8 and B16. Same family has identical starts, FIFO tasks and ordinal error input at both budgets. Empty scenario2 offsets are 96,112,128,144,160,176 TRAIN;192,208 CAL;224,240,256,272 TEST. Random scenario2 offsets are 128,144,160,176,192,208 TRAIN;224,240 CAL;256,272,288,304 TEST. Empty seeds are 131101..131106 TRAIN,131201..131202 CAL,131301..131304 TEST; random seeds add 1000. Family keys include map, scenario identity, offset, split and seed. Both scenario files are copied from pinned R12 official inputs. Before science, check all old query registrations for seed/task/start-sequence/row overlap, map geometry and paired inputs; hash inputs and source. No world is filtered by an outcome.

TRAIN/CAL: 16 families x 2 budgets x {C,LD}=64 complete native trajectories. TEST:8 families x 2 budgets x {condition,alwaysLD,budget_lookup,full,no_history_prob,WAIT}=96 complete trajectories. TEST comparisons and family-level summaries include both budgets, not 16 independent replications. Report B8 and B16 separately as well as together.

## One actual late decision with a fixed complete tail

Every non-WAIT arm executes the original condition policy before the gate. The gate is the earliest public eligible candidate event with remaining budget>0 and spent>=floor(B/2). The actor records initial B at its first legal event, before any QUERY; it cannot infer B from later private state. There is one model call at this gate and no later model call. A missing gate is retained: the trajectory is C throughout, no feature vector is invented, no call is counted, and the selected effective tail is C. Whole WAIT executes WAIT from start and has no late-gate model call.

At a gate choose C or LD. C continues original condition. LD immediately installs SKIP on the original exact condition-rank top visible candidate, including zero-score candidates; ties use agent then complete occurrence ID. It then skips the earliest subsequent eligible candidate with remaining budget and a different complete (agent,occurrence) identity, using the same rank. Between and after interventions it executes original condition. There is no oracle selection of the second point, no repeated deployment of a single-intervention label and no same-event compensating query. Planned but unreachable second skips remain recorded in the denominator. SKIP uses the full identity, consumes no query budget and persists until the matching accepted public normal END; physical END cannot clear it, and successor occurrences are unaffected.

All C/LD TRAIN/CAL trajectories must have identical complete physical/public records up to the actual late gate, allowing only declared policy metadata differences. Same-world TEST non-WAIT policies must share that prefix. B8 and B16 gates occur at different states; cross-budget gate/feature equality is neither assumed nor tested as an invariance.

## Ten public gate features

The target is the exact condition-rank top visible candidate at the actual gate. Rank remains the same public function for every variant. The original 24 candidate slots remain fully logged; the model receives these ten explicit target/context scalars only, with exact rational values:

0. p: target history-conditioned analytic survival release probability.
1. p0: same target's analytic survival release probability with no history (the original prior).
2. floor_1e-6(public target age)/2, as original slot18.
3. sum over target public claims of 1/(remaining route items x owners).
4. minimum remaining route items over those claims /64.
5. number of target claims /15.
6. number of other visible candidates /15.
7. remaining query budget /16.
8. 1-floor_1e-6(at/8)/16, i.e. public remaining horizon proportion with the existing quantization.
9. p times feature3.

No ID, seed, map, split, future task/END/error, private position/progress or realized counterfactual consequence is an input. Claims refer only to currently revealed public head tasks/routes. no_history_prob masks slots0 and9 to zero in TRAIN preprocessing and native inference, with its own otherwise identical fitted heads. It retains prior/age, history-dependent eligibility, target rank and original condition tail; this is only a selector history-probability feature ablation, not a history-free system. No nobudget arm is included.

## Whole-tail labels and fixed fitting

For each TRAIN/CAL world, C and LD execute to H. Primary label is whole-FIFO task difference N_LD-N_C. T is the restricted sum of completion times for the fixed first four FIFO tasks of each agent; unfinished tasks receive128. Time label is (T_C-T_LD)/16385. Retain exact rational lower/upper time intervals; fitting uses their midpoint. QUERY count is an independently reported outcome, not production COST. Complete common-prefix audit is a prerequisite to reading labels into fitting.

Fit two ridge heads (task/time) for each of full and no_history_prob: four heads, ten features plus intercept. TRAIN only; each family's two budget rows has weight1/2 each. Weighted means/standard deviations; scales below1e-12 become1. Lambda=1 with an unpenalized intercept. Preserve row bindings, weights, raw coefficients, standardized coefficients, means/scales and labels. Round raw-coordinate coefficients to9 decimals using the preregistered Python round path, then deploy as exact rationals. Never use CAL/TEST in normalization or fitting. Missing gate rows remain in complete outcome tables but are excluded from fit. If all TRAIN gates are absent, predeclared zero heads, zero means/unit scales and C fallback apply; do not expand data.

C has score0. LD score is predicted task advantage plus predicted normalized time advantage. Choose LD exactly when score>shared_margin; tie chooses C. No repeated model use. No task-zero prediction is a guarantee against task loss.

Only full chooses one common CAL margin from [0,1/10000,1/1000,1/100,1/10,+infinity]; no_history_prob receives that exact margin. For each threshold select the matching already executed complete C/LD trajectory for every CAL context, using C when no gate. First maximize summed tasks; among ties retain the interval-undominated T set (no other candidate upper T strictly below its lower T); then minimize summed QUERY count; then take the larger threshold. No per-family no-harm veto or activation requirement. CAL may select infinity again, which must be reported as no active learned choice. No post-TEST changes.

TRAIN budget_lookup separately selects C or LD for each B by summed TRAIN tasks, then the same interval-undominated T rule, then QUERY count, then fixed option order C before LD. It is frozen with the models and CAL margin before any TEST. AlwaysLD is a mandatory strong comparator and can outperform both lookup and full. A useful learned choice needs evidence beyond merely matching a fixed macro; positive and negative per-family outcomes remain visible.

## Phase freezes, audit and publication

Freeze protocol, data/worlds, native/runner/fit/audit/prefix source hashes and executable/bridge/config before any scientific TC run. Preserve every compile or execution failure and its original receipt. Bind cached receipts to exact input including model/margin/lookup, all raw hashes, binary/source/bridge/config and world/B. Keep actual start/end nanosecond receipts, registration revision history if any, and stage scheduling receipts.

After64 TC, original continuous-physics/service/certificate audit and complete C/LD prefixes must pass. Then fit/calibrate and freeze model/labels/lookup hashes before96 TEST. Independent root/mentor verification rebuilds raw labels, exact ridge/calibration and runtime gate/choice/macros. Original audit checks public target rank, earliest gate and second trigger, budget and accepted-END skip lifetimes. Negative controls corrupt gates/features/heads/choices/prefix/persistence/certificates. Full/condition/alwaysLD/lookup trajectories sharing the selected macro must match after removing only declared policy, gate-scoring/timing and native-check-count metadata.

At finish publish REPORT/RESULTS/family and budget strata, full TRAIN/CAL signal counts, prediction/activation/selection/service distinctions, raw failure evidence, source delta audit, model/phase hashes, independent reports and hashes. Archive every raw member exactly once in SHA-verified compressed parts below45MB each, verify offline extraction/replay, then final whitelist/frozen manifest. No production COST, broad optimality, throughput improvement or effective feature ablation claim follows merely from implementation or equal outcomes. Root owns README, Git and final publication; this agent changes only the new isolated R13 directory.

## Native and model schema

TC policy strings are macro_C and macro_LD. TEST strings are condition,alwaysLD,budget_lookup,full,no_history_prob,WAIT. Before the late gate, non-WAIT actor_decision has macro="", initial_capacity=B and decision_mode=condition. At the gate macro_choice records at,policy,opportunity,initial_capacity,remaining_capacity,spent,target_agent,target_move,feature_schema="late_target10_v1", ten rational features, exact tasks/time/total scores for options[C,LD],shared margin/inf flag,selected_option,inference_calls and inference_ns. Later actor macro is C or LD. WAIT has macro W and no macro_choice. All original24 candidate features and visibility/skip state logs remain.

Model parameters: full_LD_tasks,full_LD_time,no_history_prob_LD_tasks,no_history_prob_LD_time each have11 rational coefficients; shared_margin=[infinity_flag,value]; budget_lookup_8/16 are0 forC or1 forLD. Native input M rows and receipts retain R12 hash/time bindings. Timing begins at gate target ranking and includes ten-feature construction plus scoring/threshold selection; it excludes World3 candidate construction and original24 features, and does not establish production COST.
