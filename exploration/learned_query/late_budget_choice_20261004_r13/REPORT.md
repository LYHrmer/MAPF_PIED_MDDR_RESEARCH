# R13: one learned C/LD decision at the actual late budget opportunity

Completed 160 native episodes: 64 TRAIN/CAL complete C/LD branches and 96 TEST deployments, with 0 execution failures. Full serves 713 whole-FIFO tasks in 16 TEST family/budget contexts. Its task differences are +1 versus condition, +0 versus alwaysLD, +1 versus the TRAIN per-budget lookup and +5 versus whole WAIT. These are eight registered heldout families, each repeated at B8/B16, not 16 independent replications or 96 independent samples.

| TEST policy | Tasks | QUERY | Actual C/LD/W choices | T gain vs C | T gain vs fixed LD |
|---|---:|---:|---|---:|---:|
| condition | 712 | 192 | {"C": 16} | [-0.000700, 0.000700] | [-4.965087, -4.963686] |
| alwaysLD | 713 | 192 | {"LD": 16} | [4.963686, 4.965087] | [-0.000701, 0.000701] |
| budget_lookup | 712 | 192 | {"C": 8, "LD": 8} | [-1.399309, -1.397909] | [-6.363696, -6.362295] |
| full | 713 | 192 | {"C": 6, "LD": 10} | [4.963687, 4.965088] | [-0.000700, 0.000702] |
| no_history_prob | 713 | 192 | {"C": 7, "LD": 9} | [5.677463, 5.678864] | [0.713076, 0.714478] |
| WAIT | 708 | 0 | {"W": 16} | [-81.433858, -81.432462] | [-86.398245, -86.396848] |

Tasks count the whole FIFO through H=128. The secondary T is the restricted sum for each agent’s fixed first four FIFO tasks, unfinished tasks assigned 128; QUERY count is separately reported. Positive T gain means faster. J=N−T/16385 retains rational lower/upper bounds; robust gain requires a strictly positive lower bound. Identical service records establish zero actual difference even when interval subtraction displays a small enclosure around zero.

## What changed and what the model can decide

Every non-WAIT policy executes original condition until the first public eligible candidate event after at least floor(B/2) queries have been spent, with remaining budget. Only then does the learned selector construct its ten public target features and call its model once. It chooses C for the full remaining condition tail, or LD for an immediate persistent SKIP followed by the earliest legal different complete occurrence SKIP and then condition. Both target ranks use exact original condition scores, including zero-score ties ordered by agent then occurrence. No second learned decision or repeated use of a one-intervention label occurs. Whole WAIT executes WAIT throughout.

The target features are history-conditioned release probability, history-free analytic prior, public age, inverse route/owner claim sum, minimum blocked remaining route, claim count, other visible candidate count, remaining budget, time to H and the probability–structure product. Full identity, seed, map, split, private progress, future END and unrevealed task information are excluded. Exact formulas and schemas are in CONTRACT.md. The existing24 candidate features and all before/after visibility records remain available to audit.

Total B is externally supplied. Selecting C or LD can change its allocation, but the model does not choose total budget. no_history_prob masks only the history probability and its structural product (slots0/9), fits its own two heads and uses the same CAL threshold. Eligibility, target ranking and condition tails still use public history, so this is not an entirely history-free system. B8/B16 gates are at different physical states; no cross-budget equal-gate or equal-score claim is made. All comparators are internal policy controls, not published external query-learning baselines.

## Training signal, calibration and actual activation

Twelve TRAIN families provide 24 budget contexts; 24 LD rows have a legal late gate and enter fitting, while 0 no-gate rows remain in outcomes with zero advantage and no fabricated features. Four TRAIN-only weighted ridge heads (full/no_history_prob x tasks/time) use ten features plus unpenalized intercept, lambda 1, each family/budget weight 1/2 and 9-decimal rational coefficients. Full alone chooses the shared CAL margin 1/10; the TRAIN lookup chooses LD for B8 and C for B16.

| Split: LD−C labels | Rows / gate rows | Task positive / zero / negative | Robust T gain / unresolved / loss |
|---|---:|---:|---:|
| train | 24 / 24 | 3 / 19 / 2 | 4 / 11 / 9 |
| calibration | 8 / 8 | 1 / 6 / 1 | 3 / 1 / 4 |

| Full CAL margin | Tasks | Restricted T interval | QUERY | Selected tails |
|---|---:|---:|---:|---|
| 0 | 322 | [46534.867924, 46534.868242] | 96 | {"C": 4, "LD": 4} |
| 1/10000 | 322 | [46534.867924, 46534.868242] | 96 | {"C": 4, "LD": 4} |
| 1/1000 | 322 | [46534.867924, 46534.868242] | 96 | {"C": 4, "LD": 4} |
| 1/100 | 322 | [46534.867924, 46534.868242] | 96 | {"C": 4, "LD": 4} |
| 1/10 | 323 | [46524.280953, 46524.281272] | 96 | {"C": 5, "LD": 3} |
| infinity | 321 | [46603.301008, 46603.301325] | 96 | {"C": 8} |

The frozen rule maximizes CAL tasks, then retains interval-undominated T, then minimizes QUERY, then takes the larger margin. The same threshold applies to both learned variants. It is not changed to force activation. CAL and TRAIN diagnostics are not heldout evidence.

Full makes 16 native model calls, selects 10 LD tails and executes 20 SKIPs. no_history_prob differs from full in 3 macro choices and 1 full service records, with task difference +0. An ablation only supports a measured contribution where decisions and consequences actually differ.

## Heldout outcomes by budget and family

| B | Policy | Tasks | QUERY | Δtasks vs C / LD | T gain vs C | T gain vs LD |
|---|---|---:|---:|---:|---:|---:|
| 8 | condition | 356 | 64 | +0 / +0 | [-0.000350, 0.000350] | [1.398259, 1.398959] |
| 8 | alwaysLD | 356 | 64 | +0 / +0 | [-1.398959, -1.398259] | [-0.000350, 0.000350] |
| 8 | budget_lookup | 356 | 64 | +0 / +0 | [-1.398959, -1.398259] | [-0.000350, 0.000350] |
| 8 | full | 356 | 64 | +0 / +0 | [-0.815517, -0.814817] | [0.583092, 0.583792] |
| 8 | no_history_prob | 356 | 64 | +0 / +0 | [-0.101741, -0.101041] | [1.296868, 1.297568] |
| 8 | WAIT | 354 | 0 | -2 / -2 | [-36.532975, -36.532277] | [-35.134366, -35.133668] |
| 16 | condition | 356 | 128 | +0 / -1 | [-0.000350, 0.000350] | [-6.363346, -6.362645] |
| 16 | alwaysLD | 357 | 128 | +1 / +0 | [6.362645, 6.363346] | [-0.000351, 0.000351] |
| 16 | budget_lookup | 356 | 128 | +0 / -1 | [-0.000350, 0.000350] | [-6.363346, -6.362645] |
| 16 | full | 357 | 128 | +1 / +0 | [5.779204, 5.779905] | [-0.583792, -0.583090] |
| 16 | no_history_prob | 357 | 128 | +1 / +0 | [5.779204, 5.779905] | [-0.583792, -0.583090] |
| 16 | WAIT | 354 | 0 | -2 / -3 | [-44.900883, -44.900185] | [-51.263879, -51.263180] |

| TEST family | B | Full tail / gate | Tasks | Δtasks vs C / LD / lookup | T gain vs C | T gain vs LD | QUERY | SKIPs actual / planned |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| empty-32-32_scen2_offset224_test_131301 | 8 | LD / True | 46 | +0 / +0 / +0 | [-0.684878, -0.684788] | [-0.000045, 0.000045] | 8 | 2 / 2 |
| empty-32-32_scen2_offset224_test_131301 | 16 | LD / True | 46 | +0 / +0 / +0 | [-0.000045, 0.000045] | [-0.000045, 0.000045] | 16 | 2 / 2 |
| empty-32-32_scen2_offset240_test_131302 | 8 | LD / True | 42 | +0 / +0 / +0 | [-0.000042, 0.000042] | [-0.000042, 0.000042] | 8 | 2 / 2 |
| empty-32-32_scen2_offset240_test_131302 | 16 | C / True | 42 | +0 / +0 / +0 | [-0.000042, 0.000042] | [-0.000042, 0.000042] | 16 | 0 / 0 |
| empty-32-32_scen2_offset256_test_131303 | 8 | LD / True | 42 | +0 / +0 / +0 | [-0.713818, -0.713734] | [-0.000042, 0.000042] | 8 | 2 / 2 |
| empty-32-32_scen2_offset256_test_131303 | 16 | LD / True | 42 | +0 / +0 / +0 | [-0.583483, -0.583399] | [-0.000042, 0.000042] | 16 | 2 / 2 |
| empty-32-32_scen2_offset272_test_131304 | 8 | LD / True | 53 | +0 / +0 / +0 | [0.583393, 0.583491] | [-0.000049, 0.000049] | 8 | 2 / 2 |
| empty-32-32_scen2_offset272_test_131304 | 16 | LD / True | 53 | +0 / +0 / +0 | [-0.583491, -0.583393] | [-0.000049, 0.000049] | 16 | 2 / 2 |
| random-32-32-10_scen2_offset256_test_132301 | 8 | C / True | 45 | +0 / +0 / +0 | [-0.000045, 0.000045] | [-0.000045, 0.000045] | 8 | 0 / 0 |
| random-32-32-10_scen2_offset256_test_132301 | 16 | LD / True | 46 | +1 / +0 / +1 | [6.946392, 6.946483] | [-0.000046, 0.000046] | 16 | 2 / 2 |
| random-32-32-10_scen2_offset272_test_132302 | 8 | C / True | 38 | +0 / +0 / +0 | [-0.000037, 0.000037] | [0.583405, 0.583479] | 8 | 0 / 0 |
| random-32-32-10_scen2_offset272_test_132302 | 16 | C / True | 38 | +0 / +0 / +0 | [-0.000037, 0.000037] | [-0.000037, 0.000037] | 16 | 0 / 0 |
| random-32-32-10_scen2_offset288_test_132303 | 8 | LD / True | 45 | +0 / +0 / +0 | [-0.000045, 0.000045] | [-0.000045, 0.000045] | 8 | 2 / 2 |
| random-32-32-10_scen2_offset288_test_132303 | 16 | C / True | 45 | +0 / +0 / +0 | [-0.000045, 0.000045] | [-0.000045, 0.000045] | 16 | 0 / 0 |
| random-32-32-10_scen2_offset304_test_132304 | 8 | LD / True | 45 | +0 / +0 / +0 | [-0.000045, 0.000045] | [-0.000045, 0.000045] | 8 | 2 / 2 |
| random-32-32-10_scen2_offset304_test_132304 | 16 | C / True | 45 | +0 / +0 / +0 | [-0.000045, 0.000045] | [-0.583486, -0.583396] | 16 | 0 / 0 |

FAMILY_RESULTS retains the within-family paired-budget effects. All positive, zero and negative outcomes remain; neither budget stratum nor family is selected for publication by gain. Missing gates and unavailable second triggers remain in the fixed 160-run denominator. No gate means effective C; fixed-LD intentions and their unexecuted SKIPs are separately recorded, not silently relabeled as successful intervention.

## Verification, timing and evidence scope

Independent original continuous-physics/exact-policy audit: PASS. Deployment/source/model/time/common-prefix audit: PASS. Deliberate corruptions: PASS. Root independent raw gate/tail audit: PASS. Mentor independent raw labels/ridge/CAL/deployment: PASS.

There are 150 SKIP installations, 150 cleared directly after the matching accepted public normal END, 348 masked raw-identity reappearances and 108 installations with later same-agent successor visibility. Maximum simultaneous skip bindings is 2. Full identity, remaining budget at installation/clear, first later query and per-episode new query identities are retained in SKIP_LIFETIMES. Physical END cannot clear a skip.

TEST performs 32 learned selector calls. Recorded host durations span 1013258–2439909 ns and include gate target ranking, ten-feature construction and scoring/thresholding, but exclude World3 candidate construction and the original 24 feature computation. They are not physical completion time or production COST.

Move3/World3, original public history and candidate feature construction are byte-identical to R12. SOURCE_DELTA scopes the chooser and main policy allow-list. All predecessor frozen files and original dependency hashes were verified. The actor gains no private input. Normal service/FIFO, geometry, ownership and certified POSITION semantics are retained.

Source, inputs and fitting rules were frozen before 64 TC; complete C/LD prefixes and original physics audits precede fit. Model coefficients, common CAL margin and TRAIN lookup were frozen before 96 TEST. Native start/end nanoseconds and exact input/model/binary/bridge/config/raw hashes bind those phases. Local timestamp consistency is not an external trusted timestamp. All compile/execution failures and no-gate cases are retained; no outcome-based sample or rule change occurred.

Every raw file is archived once: 960 members in 9 SHA-verified compressed parts, each under 45 MB. External original planner/configuration and numerical dependencies remain pinned requirements; this is not a standalone production release.

Root offline archive replay: PASS. Independent root/mentor source and result artifacts, descriptive diagnostics, figures and separately authored scientific reviews are part of the final publication whitelist.

## Interpretation

The measured full task differences versus C / fixed LD / TRAIN lookup are +1 / +0 / +1; T gain intervals are [4.963687, 4.965088] / [-0.000700, 0.000702] / [6.362296, 6.363697]. These signed comparisons and actual macro/service differences determine the claim, not the number of trained heads or audit checks.

This registered eight-family test evaluates one limited late C/LD choice. It does not establish a general budget allocator, broad map generalization, coupled blocking benefit, production economic superiority or publication qualification. A fixed LD or TRAIN lookup benefit is not automatically a conditional-model contribution. If the learner merely reproduces one fixed tail, that result remains visible and does not justify enlarging the model or tuning this TEST afterward.

## What the eight-family comparison supports

Full does not exceed fixed LD on whole-FIFO task count, and its total restricted-time difference is not numerically resolved. The displayed bounds are deterministic numerical enclosures, not confidence intervals or significance tests. Fourteen of the sixteen full service records equal fixed LD; the two differences oppose each other: random132302 at B8 chooses C and improves T by [0.583405, 0.583479], while random132304 at B16 chooses C and worsens T by [0.583396, 0.583486]. Equal aggregate outcomes therefore do not imply identical policies or identical trajectories.

The single extra task versus condition occurs at random132301/B16 and is also obtained by fixed LD. Full does make conditional choices, but this test does not establish an independent gain over that stronger control. All five active policies spend the complete supplied budgets: 192 queries over the sixteen contexts. SKIP reallocates opportunities rather than reducing the total query count in this test.

Removing selector history probability changes three choices. Only empty131303/B8 changes service: the masked selector chooses C instead of LD and improves T by [0.713734, 0.713818], with unchanged tasks. The other two choice changes preserve service. This is a measured advantage for the registered masked selector, not support for a beneficial contribution from the two removed features and not a general claim against public history.

Each family combines a disjoint row block with an independent error seed, from the scenario-2 file for each of two maps. The eight heldout families are not eight independent official scenario files. TRAIN/CAL/TEST do not share their registered row blocks or seeds, but this is neither file-level nor unseen-map generalization. Pairing two budgets does not increase the independent family count.

| Registered heldout family (B8+B16 paired) | Full tasks | Δtasks vs C / LD | Full T gain vs C | Full T gain vs LD |
|---|---:|---:|---:|---:|
| empty-32-32_scen2_offset224_test_131301 | 92 | +0 / +0 | [-0.684923, -0.684743] | [-0.000090, 0.000090] |
| empty-32-32_scen2_offset240_test_131302 | 84 | +0 / +0 | [-0.000084, 0.000084] | [-0.000084, 0.000084] |
| empty-32-32_scen2_offset256_test_131303 | 84 | +0 / +0 | [-1.297301, -1.297133] | [-0.000084, 0.000084] |
| empty-32-32_scen2_offset272_test_131304 | 106 | +0 / +0 | [-0.000098, 0.000098] | [-0.000098, 0.000098] |
| random-32-32-10_scen2_offset256_test_132301 | 91 | +1 / +0 | [6.946347, 6.946528] | [-0.000091, 0.000091] |
| random-32-32-10_scen2_offset272_test_132302 | 76 | +0 / +0 | [-0.000074, 0.000074] | [0.583368, 0.583516] |
| random-32-32-10_scen2_offset288_test_132303 | 90 | +0 / +0 | [-0.000090, 0.000090] | [-0.000090, 0.000090] |
| random-32-32-10_scen2_offset304_test_132304 | 90 | +0 / +0 | [-0.000090, 0.000090] | [-0.583531, -0.583351] |

Root's post-hoc frozen-score diagnostic removes only the time-head term, without refitting or recalibrating: 0/32 learned TEST choices change. Thus this run does not demonstrate a decision-level contribution from its fitted time head. This is not an additional trained ablation, and it does not show that completion time is generally unlearnable or useless.

Separately authored three-line assessments are copied verbatim in [Astra postexecution review](ASTRA_POSTEXEC_20261004_R13.md) and [research-mentor postexecution review](MENTOR_POSTEXEC_20261004_R13.md). REVIEW_PROVENANCE binds their original paths and hashes. Both preserve the narrow masked-selector time signal and reject treating full as superior to fixed LD. The root synthesis is [ROOT_CONCLUSION.md](ROOT_CONCLUSION.md).
