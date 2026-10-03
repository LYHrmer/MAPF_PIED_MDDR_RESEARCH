# R12: learned conditional macro selection under paired budgets

Completed 152 native episodes: 96 complete TRAIN/CAL macro branches and 56 frozen TEST deployments, with 0 execution failures. The full learned selector serves 340 tasks across the eight TEST family/budget contexts: task differences are +0 versus condition, +0 versus whole WAIT, and +0 versus the TRAIN budget lookup. These eight contexts come from four independent TEST families with paired B8/B16 settings; they are not eight independent replications.

| TEST policy | Tasks across both budgets | Queries | Δtasks vs condition | Δtasks vs WAIT | Δtasks vs TRAIN lookup | Chosen macro counts |
|---|---:|---:|---:|---:|---:|---|
| WAIT | 340 | 0 | +0 | +0 | +0 | {"W": 8} |
| condition | 340 | 88 | +0 | +0 | +0 | {"C": 8} |
| budget_lookup | 340 | 52 | +0 | +0 | +0 | {"LD": 4, "W": 4} |
| full | 340 | 88 | +0 | +0 | +0 | {"C": 8} |
| nohistory | 340 | 88 | +0 | +0 | +0 | {"C": 8} |
| nobudget | 340 | 88 | +0 | +0 | +0 | {"C": 8} |
| tasks_only | 340 | 88 | +0 | +0 | +0 | {"C": 8} |

All task counts cover the whole FIFO through H=128. Primary differences are reported per family and budget in RESULTS and aggregated within family in FAMILY_RESULTS. The secondary completion-time measure T is the restricted sum over each agent’s fixed first four FIFO tasks, with uncompleted tasks assigned 128; it is not the whole-FIFO task count. J=tasks−T/16385. Time and J comparisons retain rational lower/upper bounds; a robust improvement requires the lower difference bound to exceed zero.

## What was learned and actually deployed

Six TRAIN families provide twelve paired budget contexts. For each of five alternatives to condition, the code fits a task-advantage head and a normalized time-advantage head. Full, selector-history-masked and selector-budget-masked variants yield 30 ridge heads in total (25 public features plus intercept, lambda 1, TRAIN-only scaling, per-budget weight 1/2, nine-decimal rational deployment coefficients). The tasks_only policy reuses the full task heads. CAL contains two independent families/four budget contexts and chooses a single shared activation margin: infinity. The TRAIN-only budget lookup selects W at B8 and LD at B16.

The selector runs once at the first legal public opportunity. Its inputs are the slotwise means of the original 24 public candidate features plus candidate_count/N; it receives no agent/task/map ID, seed, split or future state. It chooses one complete macro C, W, E, L, ED or LD. C is condition throughout; W is whole WAIT; E skips the early top public occurrence, L skips at the first opportunity after at least half the supplied query budget has been spent; ED/LD add a SKIP at the earliest later legal different complete occurrence. Both target ranks and trigger rules are fixed public functions. Between/after skips the original condition policy continues. The fixed macro interpreter used for TRAIN labels is the same one used after learned TEST selection. A single-intervention label is never redeployed repeatedly as though its tail were unchanged.

Total budget B is externally supplied, not learned. B8 and B16 use the same starts, task streams and ordinal execution errors within a family. The model is fitted to value the finite macros under the supplied budget. The selector-budget ablation masks slots 20/22/23 while retaining the actual hard budget and macro thresholds. Selector-history masks 10..17 while retaining public eligibility and the original history-aware condition tail. These are selector-feature ablations, not systems with no budget or no END history. tasks_only removes the time head at inference but shares full’s time-aware CAL threshold; it is not an independently time-blind calibrated algorithm.

| Ablation vs full | Macro-choice disagreements / 8 | Full service-sequence changes / 8 | Task difference |
|---|---:|---:|---:|
| nohistory | 0 | 0 | +0 |
| nobudget | 0 | 0 | +0 |
| tasks_only | 0 | 0 | +0 |

Among the 60 non-condition TRAIN macro labels with a legal gate, 0 have nonzero task advantages; time labels are separately retained with their interval bounds.

| TRAIN macro vs condition | Task-positive / zero / negative labels | Robust T gain / unresolved / loss |
|---|---:|---:|
| W | 0 / 12 / 0 | 2 / 4 / 6 |
| E | 0 / 12 / 0 | 2 / 10 / 0 |
| L | 0 / 12 / 0 | 2 / 8 / 2 |
| ED | 0 / 12 / 0 | 3 / 9 / 0 |
| LD | 0 / 12 / 0 | 4 / 6 / 2 |

The frozen CAL margin is infinity. All learned variants therefore execute condition even when their fitted scores differ. Their equal deployed choices and trajectories cannot identify the effect of history, budget features or the time head. The experiment has implemented and exercised fitting and exact inference, but it has not demonstrated learned conditional budget allocation on TEST.

| Full CAL margin | Total tasks | Restricted T interval | Queries | Chosen macros |
|---|---:|---:|---:|---|
| 0 | 166 | [23065.211790, 23065.211950] | 0 | {"W": 4} |
| 1/10000 | 166 | [23065.211790, 23065.211950] | 0 | {"W": 4} |
| 1/1000 | 166 | [23064.221136, 23064.221296] | 48 | {"C": 4} |
| 1/100 | 166 | [23064.221136, 23064.221296] | 48 | {"C": 4} |
| 1/10 | 166 | [23064.221136, 23064.221296] | 48 | {"C": 4} |
| infinity | 166 | [23064.221136, 23064.221296] | 48 | {"C": 4} |

CAL selects maximum total tasks first, then the interval-undominated restricted-time set, then fewer queries, then the larger margin. Thus the largest tied threshold may select infinity; this is a recorded calibration outcome, not a threshold changed after seeing TEST.

All TRAIN task-advantage targets are zero, so the fitted task heads are zero. Any learned preferences in this round come from completion-time heads; this is not evidence of learning a throughput-improvement relation. The tasks_only default to condition under the nonnegative shared margin is part of the measured ablation, not an independently discovered policy.

The counts distinguish running inference, choosing a different macro, and changing actual service. Identical ablation outcomes show no measured contribution in these contexts; they do not establish that the omitted information can never matter.

## Per-context learned outcomes and completion-time value

| TEST family | B | Full option | Full tasks | Δtasks vs condition / WAIT / lookup | T gain vs condition interval | Queries | Actual / planned SKIPs |
|---|---:|---|---:|---:|---:|---:|---:|
| empty-32-32_scen2_offset64_test_121301 | 8 | C | 42 | +0 / +0 / +0 | [-0.000042, 0.000042] | 8 | 0 / 0 |
| empty-32-32_scen2_offset64_test_121301 | 16 | C | 42 | +0 / +0 / +0 | [-0.000042, 0.000042] | 12 | 0 / 0 |
| empty-32-32_scen2_offset80_test_121302 | 8 | C | 43 | +0 / +0 / +0 | [-0.000043, 0.000043] | 8 | 0 / 0 |
| empty-32-32_scen2_offset80_test_121302 | 16 | C | 43 | +0 / +0 / +0 | [-0.000043, 0.000043] | 12 | 0 / 0 |
| random-32-32-10_scen2_offset112_test_122302 | 8 | C | 40 | +0 / +0 / +0 | [-0.000039, 0.000039] | 8 | 0 / 0 |
| random-32-32-10_scen2_offset112_test_122302 | 16 | C | 40 | +0 / +0 / +0 | [-0.000039, 0.000039] | 16 | 0 / 0 |
| random-32-32-10_scen2_offset96_test_122301 | 8 | C | 45 | +0 / +0 / +0 | [-0.000044, 0.000044] | 8 | 0 / 0 |
| random-32-32-10_scen2_offset96_test_122301 | 16 | C | 45 | +0 / +0 / +0 | [-0.000044, 0.000044] | 16 | 0 / 0 |

| Policy | T gain interval vs condition (sum over paired contexts) | Robust aggregate J gain vs condition | Actual SKIPs | Unreached planned SKIPs |
|---|---:|---:|---:|---:|
| WAIT | [-45.138801, -45.138129] | False | 0 | 0 |
| condition | [-0.000336, 0.000336] | False | 0 | 0 |
| budget_lookup | [-12.936475, -12.935803] | False | 8 | 0 |
| full | [-0.000336, 0.000336] | False | 0 | 0 |
| nohistory | [-0.000336, 0.000336] | False | 0 | 0 |
| nobudget | [-0.000336, 0.000336] | False | 0 | 0 |
| tasks_only | [-0.000336, 0.000336] | False | 0 | 0 |

| Supplied budget | TRAIN lookup macro | Tasks lookup / condition | Queries lookup / condition | Lookup T gain vs condition |
|---|---|---:|---:|---:|
| 8 | W | 170 / 170 | 0 / 32 | [-17.009079, -17.008743] |
| 16 | LD | 170 / 170 | 52 / 56 | [4.072604, 4.072940] |

At B16 the TRAIN-frozen LD lookup keeps 170 tasks, uses 52 queries versus condition’s 56, and reduces restricted T by [4.072604, 4.072940]. Its timing gain comes from random family 122302; the other three families have identical service records. Each empty family saves two queries. At B8 the TRAIN-frozen W lookup increases T by about 17.0089, so the aggregate lookup loses time despite its B16 gain. These are outcomes of the preregistered per-budget lookup, not gains attributable to the learned selector.

Full’s aggregate T gains are [45.138129, 45.138801] versus WAIT and [12.935803, 12.936475] versus lookup. Full executes condition in all eight contexts, so those gains belong to the original condition policy. Identical full/condition trajectories establish no actual service or timing difference; the displayed self-comparison interval width is numerical enclosure, not a measured effect.

The protocol retains any unreached late/second trigger in the denominator, using its realized full-tail outcome. In these 152 runs all 104 planned SKIPs were reached; no unavailable trigger was relabeled as a successful intervention. All task differences and negative timing outcomes are retained. The four-family pilot does not support broad advantage or combination-blocking claims.

## Original execution and verification

The complete Move3/World3 block and the public history/feature construction are byte-identical to frozen R11. Changes are confined to actor macro selection/state/logging, the policy allow-list, a clock header for host timing, and runner budget/provenance binding. The original author planner, continuous controller, geometry, ownership, certified POSITION release, FIFO service and candidate eligibility remain pinned. Independent physics and exact macro replay: PASS 152 episodes. Deployment/hash/time/prefix controls: PASS 152 episodes, 36 same-macro full-trajectory comparisons. Negative controls: 24 rejected.

There were 104 persistent SKIP installations; 104 cleared directly after their matching accepted normal END, with any horizon-censored lifetime retained. Masked identities reappeared in raw candidates 271 times without becoming visible. 76 installations have a later distinct occurrence of the same agent visible. Maximum simultaneous bindings: 1. Per-installation remaining budget and subsequent QUERY identities are preserved in SKIP_LIFETIMES.

TEST recorded 32 learned-selector calls. Host scoring/threshold-selection durations span 28955–97072 ns. The timer excludes candidate-feature and mean-feature construction, and is host metadata rather than physical completion time or production COST.

Root raw macro/prefix/deployment audit artifact: PASS. Mentor independent label/refit/CAL/lookup audit artifact: PASS. These audit files own their exact PASS criteria and limitations; their source and result hashes are part of the final publication whitelist.

Source, inputs and learning/calibration algorithms were frozen before TRAIN. Complete common public/physical prefixes were independently checked before fitting; identical mean features alone were not treated as equal states. TRAIN standardization, all raw/rounded coefficients, row bindings, labels and CAL grid outcomes are retained. Model/margin/lookup hashes and nanosecond start/end receipts link source freeze→96 TC outcomes→fit→model freeze→TEST. Every TEST input contains the exact frozen coefficients and control parameters; cached receipts are reusable only with matching input/model, executable, bridge/config, world/budget and raw hashes.

Pre-execution reviews identified a permissive cache binding and a missing complete-prefix fit prerequisite. Both were fixed before any scientific outcome. The initial registration is retained as ATTEMPT01; the explicit zero-run registration revision adds the prefix prerequisite and a predeclared zero-head/C fallback for the all-no-gate case. All 24 declared world/budget inputs remain fixed. The official empty scenario2 archive was newly pinned; random scenario2 was copied from frozen R11. Prior seeds/task identities and scenario row groups, free-space geometry and paired inputs were checked. No seed, option, budget or horizon was added after seeing outcomes.

Every raw record is archived once: 912 members in 8 SHA-verified compressed files, each under 45 MB. Reproduction requires the pinned external author bridge, configuration and numerical dependencies; this is not a self-contained production release.

Independent offline archive replay: PASS. The root audit reconstructed all 152 episodes from eight compressed archives in a fresh temporary directory and reproduced its complete result JSON exactly, without invoking the native simulator. See OFFLINE_REPLAY_RECEIPT.json, ROOT_TEST_RESULTS.json and ROOT_MODEL_DIAGNOSTICS.json; the diagnostic analysis did not refit or retune the frozen policy.

The independent implementation and scientific assessments are retained in [ASTRA_POSTEXEC.md](ASTRA_POSTEXEC.md) and [MENTOR_POSTEXEC.md](MENTOR_POSTEXEC.md). [ROOT_CONCLUSION.md](ROOT_CONCLUSION.md) records the root review and the [figure caption](figures/CAPTION.md) defines the plotted quantities.

## Interpretation

R12 completes matched-macro training, exact native inference and frozen deployment, but shows no learned throughput or allocation gain on TEST. All 60 non-condition TRAIN task labels are zero, and CAL selects infinity; every learned variant then executes condition. The finite macro set contains some completion-time signal and the TRAIN-frozen B16 LD lookup improves time and saves queries on TEST, while its B8 W lookup loses time. These limited findings do not identify a useful learned conditional choice rule. A follow-up needs newly registered public opportunities with informative task or timing labels, while preserving complete-macro tails, real budget variation and zero-space outcomes.
