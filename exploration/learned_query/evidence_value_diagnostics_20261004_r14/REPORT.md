# R14: reusable complete-tail evidence value diagnostics

This analysis reuses all 160 frozen R13 arms and exports 48 matched C/LD complete-tail pairs. It performs no new native run, fit, threshold selection or raw trajectory audit. All exported raw references retain their archive/member content hashes.

The 16 TEST contexts are eight registered row-block/error-seed families, each run with B8 and B16. They come from two scenario-2 files on two maps. Budget repetitions are paired, not independent observations; no file-level or unseen-map generalization is established.

| Split | C tasks | LD tasks | Task-first finite oracle | Oracle gain vs C / LD | LD more / equal / fewer task contexts |
|---|---:|---:|---:|---:|---:|
| train | 1077 | 1078 | 1080 | 3 / 2 | 3 / 19 / 2 |
| calibration | 321 | 322 | 323 | 2 / 1 | 1 / 6 / 1 |
| test | 712 | 713 | 713 | 1 / 0 | 1 / 15 / 0 |

The oracle knows both completed outcomes. It only bounds choices within the two registered tails at the registered gate; it is not a deployable baseline or the globally best MAPF policy. Its label must never become an input feature or tune this TEST.

| Split: equal-task subset only | Contexts | LD faster / C faster / identical / unresolved | Finite oracle time gain vs C | Finite oracle time gain vs LD |
|---|---:|---:|---:|---:|
| train | 19 | 2 / 6 / 11 / 0 | [5.119768, 5.119936] | [39.097567, 39.098109] |
| calibration | 6 | 2 / 3 / 1 / 0 | [11.731972, 11.732134] | [7.899938, 7.900174] |
| test | 15 | 2 / 5 / 8 / 0 | [1.166789, 1.166977] | [3.148719, 3.149149] |

Time is the fixed first-four-tasks-per-agent restricted sum through H128, with unfinished tasks assigned128; task count covers the whole FIFO. Rational bounds are numerical enclosures, not statistical confidence intervals. Identical service hashes tighten a pair difference to exactly zero. Equal-task time-space excludes every context whose task counts differ, so faster timing cannot hide a lost task.

| Registered TEST family (both budgets) | C / LD tasks | Task-first oracle tasks | Equal-task oracle T gain vs LD | B8 / B16 LD task labels |
|---|---:|---:|---:|---|
| empty-32-32_scen2_offset224_test_131301 | 92 / 92 | 92 | [0.684788, 0.684878] | 0 / 0 |
| empty-32-32_scen2_offset240_test_131302 | 84 / 84 | 84 | [0.000000, 0.000000] | 0 / 0 |
| empty-32-32_scen2_offset256_test_131303 | 84 / 84 | 84 | [1.297133, 1.297301] | 0 / 0 |
| empty-32-32_scen2_offset272_test_131304 | 106 / 106 | 106 | [0.583393, 0.583491] | 0 / 0 |
| random-32-32-10_scen2_offset256_test_132301 | 90 / 91 | 91 | [0.000000, 0.000000] | 0 / 1 |
| random-32-32-10_scen2_offset272_test_132302 | 76 / 76 | 76 | [0.583405, 0.583479] | 0 / 0 |
| random-32-32-10_scen2_offset288_test_132303 | 90 / 90 | 90 | [0.000000, 0.000000] | 0 / 0 |
| random-32-32-10_scen2_offset304_test_132304 | 90 / 90 | 90 | [0.000000, 0.000000] | 0 / 0 |

Task/time conflicts are retained: empty-32-32_scen2_offset160_train_131105_B16 (LD ΔN=-1, ΔT=[6.336967, 6.337060]); empty-32-32_scen2_offset176_train_131106_B8 (LD ΔN=+1, ΔT=[-25.502182, -25.502090]); random-32-32-10_scen2_offset160_train_132103_B16 (LD ΔN=+1, ΔT=[-6.033070, -6.032979]).

The reusable learning target is the value of a complete continuation from a common public prefix. Keep whole-task risk and equal-task time value as distinct targets/evaluation strata. Public budget, candidate multiplicity, claim structure and time remaining are available conditioning variables; their descriptive tables are not a fitted threshold rule. A future TRAIN design should collect both task-safe timing reversals and task-risk examples at matched budget/state conditions, retain ties and negative cases, and evaluate against fixed LD and C. More parameters alone do not create missing causal action-space coverage.

The shared interface in COMMON_VALUE_SCHEMA.json is context → complete option → task/time/query outcome plus paired value. It can align query and graph/search experiments only after their legal action, budget and full-tail contracts are separately specified. It does not equate the third line’s actions with C/LD or transfer these numerical labels to another simulator.

This round fits no model and uses no TEST result to select a new policy. Future research remains within the user’s continuing authorization; proposed training changes require new preregistered TRAIN/CAL and separate file-level TEST. Cache receipts record extraction and a second content-verified reuse. The original v1 evidence and receipts are preserved; v2 sums nonnegative pairwise oracle gains so unchanged branches contribute exactly zero. Source and export hashes are in VALUE_CACHE.json.
