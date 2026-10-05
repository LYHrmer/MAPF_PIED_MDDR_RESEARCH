# R19 conditional duration model: measured TRAIN result

The model and runtime predictor are frozen in `MODEL_FREEZE.json`. Training reads exactly 54 R18 TRAIN history_rule episodes, one per world; CAL/TEST and counterfactual trajectories are excluded. The 51,942 completed actions and 6,477 active-gate landmarks belong to six map/scenario families. No new scientific episode or solver call was launched.

| Internal reference / model | Action-start MAE | Action-start MSE | Active-gate MAE | Active-gate MSE |
| --- | ---: | ---: | ---: | ---: |
| learned | 0.321941 | 0.398685 | 0.384644 | 0.469827 |
| nominal | 0.287345 | 0.599447 | 0.435299 | 0.796250 |
| all_history | 0.298113 | 0.424772 | 0.407821 | 0.581430 |
| recent4 | 0.238940 | 0.447821 | 0.319455 | 0.566473 |
| ewma03 | 0.238942 | 0.416627 | 0.323475 | 0.538024 |
| constant_survival | 0.452947 | 0.518940 | 0.506331 | 0.584596 |
| all_history_survival | 0.298113 | 0.424772 | 0.367314 | 0.476433 |
| recent4_survival | 0.238940 | 0.447821 | 0.314046 | 0.485349 |
| ewma03_survival | 0.238942 | 0.416627 | 0.313360 | 0.459525 |

These are nested grouped OOF predictions on existing TRAIN worlds, not independent R19 TEST or scheduling results. Each outer family is excluded from all fitting and hyperparameter selection for its predictions. Inner family validation selects alpha; every outer fold and final TRAIN selection chose 0.1. Metrics give equal weight to families, then worlds, then rows within worlds. Multiple landmarks are not independent experiments.

The learned active MSE improves over the raw whole-history reference but does not beat ewma03_survival; its MAE is also worse. The latter is therefore retained as a strong internal execution comparator by the R19 team. No policy was replaced after inspecting holdout results. A lower prediction MSE need not improve legal scheduling; new R19 complete episodes are required for that claim.

## Target, censoring and wait separation

A completed label is END minus its own START, including pauses during that action. Dependency waiting before START is separately recorded and never added to the target. Features use only earlier delivered ENDs. Every chosen source episode completes, so terminal right-censored labels number zero. At an active gate, elapsed is survival evidence D > elapsed; the lognormal model supplies E[D−elapsed | D>elapsed]. The future END is used only to score that prediction. The model does not fit partial elapsed as if it were a completed duration.

The fitted distribution is a simple lognormal approximation, not a calibrated uncertainty certificate. The observed disturbances form a mixture, and future change points cannot be identified before public evidence appears. Empty or short histories, new geometries/nominal scales, persistent pauses beyond training support, and using the model under a different scheduling continuation can degrade predictions. The distribution allows durations below the physical nominal value; its expectation is a scheduling estimate, not a reachability or safety claim.

## Validation and artifacts

`VALIDATION.json` passes: all 64 fitted parameter sets satisfy independently reconstructed weighted normal equations (maximum residual 9.612e-15), all earlier-history features match raw END reconstruction, and runtime inference on all 6,477 landmarks matches a separate SciPy conditional-mean calculation within 2.110e-14. The 150 tail/boundary cases have maximum relative error 6.608e-7. Private metadata changes leave predictions unchanged; nonzero STAGED elapsed is rejected.

`TRAIN_SOURCES.json` binds the 54 raw receipts; compressed TRAIN action/landmark tables retain public-feature provenance and separate offline labels. `CV.json` stores every fit, nested split and selection curve. `OOF_ACTIONS.jsonl.gz`, `OOF_LANDMARKS.jsonl.gz` and `RESULTS.json` retain all scored predictions. Runtime needs only `predictor.py`, `MODEL.json` and Python standard library. `PUBLIC_SCHEMA.json` defines the adapter contract; `MODEL_BUNDLE_MANIFEST.json` binds the frozen package.

The original model and predictor files must remain unchanged. In R19, a delivered current-occurrence POSITION may override the END-only residual using the separately registered original linear_history rule; this is not a learned joint posterior. The no-query factor isolates conditional duration prediction. Actual R19 scheduling results are maintained by the execution team and are not fabricated here.

Reproduce this internal validation with `python3 verify.py`. Training code is `study.py`; rerunning is unnecessary to consume the frozen model. This exploratory prototype is not publication qualification; see `DESIGN_CARD.md`.
