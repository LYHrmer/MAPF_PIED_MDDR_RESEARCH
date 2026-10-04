# R14 interpretation and next target

The finite C/LD TEST oracle completes 713 tasks, exactly the fixed LD total 713. It has no additional task-count space over LD in these 16 registered contexts. Among the 15 equal-task contexts, its time improvement over LD is [3.148719, 3.149149], about 0.003507% of LD’s restricted-time total. This is a small finite-option opportunity envelope, not evidence that the broader problem is unlearnable.

TIGHT_HEADROOM independently recomputes the v2 pairwise bounds in SPLIT_DIAGNOSTICS. Unchanged selected branches contribute exactly zero, avoiding interval self-subtraction. The original more conservative v1 export remains in V1_EXPORT_EVIDENCE; all versions use the same data and policy set. Neither bound is a statistical confidence interval.

| TEST family | Equal-task finite oracle T gain vs LD |
|---|---:|
| empty-32-32_scen2_offset224_test_131301 | [0.684788, 0.684878] |
| empty-32-32_scen2_offset240_test_131302 | [0.000000, 0.000000] |
| empty-32-32_scen2_offset256_test_131303 | [1.297133, 1.297301] |
| empty-32-32_scen2_offset272_test_131304 | [0.583393, 0.583491] |
| random-32-32-10_scen2_offset256_test_132301 | [0.000000, 0.000000] |
| random-32-32-10_scen2_offset272_test_132302 | [0.583405, 0.583479] |
| random-32-32-10_scen2_offset288_test_132303 | [0.000000, 0.000000] |
| random-32-32-10_scen2_offset304_test_132304 | [0.000000, 0.000000] |

The TRAIN task-first envelope is 1080 versus C 1077 and LD 1078. TRAIN contains two LD task losses as well as three gains. In random132103, LD loses one task at B8 and gains one at B16; the gate state also changes, so this is not an isolated causal estimate of budget alone.

All 48 target gates have exactly one public claim: True; exact reconstruction from the public inverse-route/owner feature gives one owner on each claim. PUBLIC_COVERAGE records the calculation without private inputs. TRAIN has 22 single-candidate gates and two two-candidate gates; TEST has 15 and one. Multiple visible candidates therefore do not constitute multi-head or multi-owner coupled blocking. The current narrow C/LD tails offer little remaining TEST headroom over a strong fixed rule.

The next TRAIN question should be which publicly distinguishable states offer larger legal continuation effects while preserving task count, and where task-count risk changes with remaining budget and state. Keep a task-risk target separate from a same-task timing target; register full-tail labels and a material effect scale before fitting. Public claim/owner multiplicity and alternative eligible actions need actual coverage if the next design aims at coupled dependence. Do not merely enlarge the model, or use these TEST contributors to pick future evaluation cases.

These are hypotheses for new preregistered TRAIN/CAL collection, not a new threshold, policy or permission to retune R13 TEST. A separate file-level holdout should test any design change. The common schema preserves shared context, legal complete continuation, whole-task reward, restricted-time cost, actual queries and reachability across research lines; numerical transfer requires a common simulator/action contract.
