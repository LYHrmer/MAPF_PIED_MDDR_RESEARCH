# Frozen R19 TEST prediction: secondary result

On the common history-no-query states, the learned model has the lowest action-start MSE among the nine fixed modes, but does not beat the EWMA survival reference for active residual MSE or MAE. This distinction must remain separate from the original experiment’s actual scheduling outcomes.

This analysis was registered after the main experiment began. It makes no parameter changes, refits, solver calls or new physical runs. Each executable world contributes exactly one common history_no_query trajectory. All nine modes use the same inputs and the same frozen TRAIN-only model parameters. Future END is a label only.

## Coverage and aggregation

Core: 36 worlds in six map/scenario families, N16/32 and scenarios6/7; 45,060 action START labels and 5,462 active-gate labels. Scale extension: six executable worlds in two families, N64; 21,741 action START labels and 2,417 active-gate labels. Three additional planned N64 worlds in the maze family lack a valid initial plan and remain explicit coverage failures. All available canonical trajectories complete; both targets have zero terminal right-censored rows.

MAE is in simulation seconds and MSE in squared seconds. Each family has equal weight, each world within a family has equal weight, and rows within a world have equal weight. Repeated landmarks and actions do not create additional independent families. Core and scale are reported separately.

## Core: six families

| Frozen internal mode | START MAE | START MSE | Active MAE | Active MSE |
| --- | ---: | ---: | ---: | ---: |
| nominal | 0.253095 | 0.521947 | 0.422025 | 0.787434 |
| all_history | 0.269156 | 0.372618 | 0.392571 | 0.558949 |
| recent4 | 0.208566 | 0.391859 | 0.302213 | 0.546747 |
| ewma03 | 0.208268 | 0.362021 | 0.306119 | 0.524697 |
| constant_survival | 0.428278 | 0.457941 | 0.500030 | 0.577512 |
| all_history_survival | 0.269156 | 0.372618 | 0.350553 | 0.456829 |
| recent4_survival | 0.208566 | 0.391859 | 0.290968 | 0.465208 |
| ewma03_survival | 0.208268 | 0.362021 | 0.291829 | 0.445077 |
| learned | 0.293862 | 0.346998 | 0.372231 | 0.457975 |

## N64 extension: two executable families

| Frozen internal mode | START MAE | START MSE | Active MAE | Active MSE |
| --- | ---: | ---: | ---: | ---: |
| nominal | 0.232054 | 0.476643 | 0.368605 | 0.657699 |
| all_history | 0.243334 | 0.339204 | 0.356015 | 0.500667 |
| recent4 | 0.187862 | 0.351175 | 0.269755 | 0.474362 |
| ewma03 | 0.188651 | 0.326487 | 0.273529 | 0.452430 |
| constant_survival | 0.413980 | 0.423591 | 0.465844 | 0.487926 |
| all_history_survival | 0.243334 | 0.339204 | 0.323108 | 0.404295 |
| recent4_survival | 0.187862 | 0.351175 | 0.273565 | 0.404696 |
| ewma03_survival | 0.188651 | 0.326487 | 0.269142 | 0.381322 |
| learned | 0.275066 | 0.314209 | 0.340936 | 0.388652 |

## What this result supports

The learned model’s core START MSE is 0.346998 against 0.362021 for EWMA; the N64 values are 0.314209 and 0.326487. Its START MAE is worse than recent-history/EWMA. For active residuals, learned MSE is 0.457975 core and 0.388652 N64, against EWMA survival’s 0.445077 and 0.381322; learned MAE is also worse. Core whole-history survival MSE, 0.456829, is marginally below learned as well. No model or arm is substituted on this basis.

These labels concern action execution time including in-action pauses. They exclude dependency waiting before START. Complete agent completion-time sums include such waiting and scheduling interactions, so a lower action prediction MSE cannot establish a scheduling gain. This evaluation uses common baseline-policy states; it is not a pooled comparison of each deployed policy’s different visited states. The two-family scale result is especially limited, and no significance or calibrated-probability claim is made.

## Reproducibility

`REGISTRATION.json` timestamps the secondary protocol and binds the original scientific registration, frozen model, predictor and scoring code. `SOURCES.json` binds the 42 canonical raw episodes and receipts. `ACTION_PREDICTIONS.jsonl.gz` and `ACTIVE_PREDICTIONS.jsonl.gz` retain every row, public-history summary, offline label and all nine predictions. `RESULTS.json` includes per-world and per-family metrics in addition to aggregates. `COVERAGE.json` retains the planned initial failures.

`check_scores.py` independently reconstructs public history from original logs, evaluates the fixed distribution using SciPy without importing the scorer or predictor, and recomputes family/world weights and metrics. Its result is `VERIFICATION.json`. `PUBLICATION_MANIFEST.json` binds this secondary package. Runtime data remain referenced rather than repackaged.
