# R17 retrospective three-tail learning and query-budget frontier

This is an offline development analysis of already observed R13/R16 outcomes. The method is frozen before this analysis runs; it is not a prospective registration before the original labels existed. R16 aggregate findings and a first-row schema inspection were already known. No existing result, model, input or TEST file may be changed, and no new native episode may run.

Qualification: CONDITIONAL for exploratory learning; the real C/LD/STOP tails and complete physical/FIFO consequences exist, and this study must reverify matching before fitting. Twelve TRAIN families, each with budgets 8 and 16, form 24 contexts. There are only 12 independent family groups. All 72 arm consequences are reused. CAL is already development data and its six R16 contexts may receive descriptive replay only after the final model is frozen; it is not an independent test. R13 TEST remains unopened. No deployment or generalization gain is promised.

## Frozen input and target semantics

Use R13 `TRAIN_CAL_LABELS.json` filtered to TRAIN C/LD, and R16 `TRAIN_PAIRS.json` C/STOP. Recompute raw hashes, policy-normalized complete pre-gate prefixes, exact gate identities/features, shared input hashes, whole-tail task counts, query counts and restricted completion-time intervals. Read matching R13 raw/receipt/input and R16 raw/receipt/input paths only. All training data bindings and preprocessing source hashes go in `REGISTRATION.json` and `DATASET_AUDIT.json`.

The existing late gate and action semantics are unchanged. C continues condition; LD performs the two registered legal SKIPs then condition; STOP buys no further POSITION while ordinary END/FIFO work proceeds to H=128. Missing gates use C; no synthetic gate features. Policy/summary native-check metadata are the only allowed prefix normalizations. Every matched context must share its entire physical/public prefix and its gate identity, not only a feature vector.

Targets remain distinct:

- `tasks`: total genuine FIFO services by horizon, including all served tasks.
- `T`: restricted sum for the predetermined first four tasks of each of 16 agents (64 fixed tasks), unfinished tasks assigned H=128; exact lower/upper intervals retained.
- `queries`: actual successful POSITION purchases, with one query as one unit; this is neither currency nor production COST.

For C and LD separately, fit their three full-tail differences relative to STOP: task count, T midpoint, and query count. Shared prefix contributions cancel. STOP has zero relative predictions and does not require knowing its realized outcome at inference. Absolute realized STOP outcomes are used only to construct TRAIN labels or evaluate a selected completed arm.

## Model and nested grouped validation

Six linear ridge heads share the original ten public gate features and an unpenalized intercept. No map name, family/seed identity, private position/speed, future gate, oracle outcome or other budget's gate is a feature. Each family's two rows has weight 1/2. Each fitted model estimates feature mean/standard deviation from its own training fold only; scales below 1e-12 become 1.

Outer leave-one-family-out has 12 folds and always holds both budgets together. For each outer fold, inner leave-one-family-out on its remaining 11 families selects one common lambda from `[1,10,100]` using only inner out-of-fold selected consequences. Choose maximal task sum; retain candidates with no other candidate's upper T strictly below their lower T; then minimize queries; then larger lambda. After outer evaluation, select final lambda by the same grouped inner validation on all 12 TRAIN families, fit all six heads on TRAIN, and freeze the complete model before CAL replay.

The action rule is fixed: maximize predicted task gain allowing a tolerance of 1e-6 task; among that set minimize predicted T difference allowing 1e-3 time unit; then minimize predicted query difference allowing 1e-6 query; exact remaining ties use STOP, C, LD in that order. These tolerances are numerical guards, not outcome-tuned margins. Query cost has no task/time conversion coefficient. Report raw predictions, chosen actions, observed consequences and three-target prediction errors.

## Required comparators

Fixed C, LD and STOP appear in every report. Two learned strong rules use only each outer training set: a separate initial-budget action lookup; and a threshold decision stump. The stump may split public history probability (feature 0) or remaining-horizon fraction (feature 8) at fixed thresholds `[1/4,1/2,3/4]`, or remaining-capacity/16 (feature 7) at `3/8`. Each leaf action is selected from C/LD/STOP using the exact TRAIN task/T/query ordering above; no label-selected threshold beyond this fixed grid. Also include a constant TRAIN-selected action. Require at least two distinct training families on each side; tie between rules favors the constant, then earlier listed feature/threshold. Evaluate each rule on the untouched outer family; do not choose the most flattering comparator after outcomes.

Report OOF and fixed-policy tasks/T/query totals overall and for B8/B16, family-level differences and empirical nondominated policies. Neither 24 contexts nor 72 arms are independent replicates. A policy's totals must never mix in-sample choices with OOF choices. Final frozen model replay on TRAIN is labelled resubstitution, and CAL replay is labelled already-used development.

## Query-cost frontier without monetary conversion

Use exact dynamic programming over observed discrete actions. For each `(query total, task total)`, retain the minimal midpoint restricted T and the complete choices, with intervals; prune final task/T/query domination. Export all surviving states, exact per-query task-first envelope and deterministic action reconstruction. Run this over 24 contexts with three same-gate tails and separately over each budget's 12 contexts.

Additionally, form a six-action `{B8,B16}×{C,LD,STOP}` oracle per family and its frontier. This is a noncausal episode-start information upper bound, not a late-gate policy: the late gate cannot change the initial budget or inspect the other budget's realized trajectory. Oracle selection sees outcomes and is never training or test performance. No fee exchange rate, hand-picked scalarization or post-hoc budget is selected.

## Deliverables and stopping rule

Deliver independent input/prefix audit, frozen analysis code/model, all outer and inner folds and predictions, OOF/final choices for every family and budget, fixed/strong-rule comparisons, exact frontier data, model diagnostics, limitations and a root-recomputable manifest. Finish even if learned OOF loses to fixed policies. No new scientific episode, extra seed, TEST access, CAL retuning or rerun based on a disappointing learning outcome is allowed. This finite retrospective analysis can identify next-study hypotheses; it cannot establish fresh unseen-family success.
