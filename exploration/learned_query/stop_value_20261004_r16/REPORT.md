# R16 C/STOP complete-tail exploration report

Completed 29 new native runs, including 2 necessary C binary-compatibility checks. Reused 30 exact old C outcomes plus 3 explicitly registered STOP semantic aliases (pointing to existing C8, not additional raw runs). TRAIN is 12 old families × 2 budgets; no old TEST opened. CAL is 3 preregistered old families with a new STOP action. This is developmental evidence, not a new final test.

| Split/arm | FIFO tasks | Restricted T interval | Queries |
|---|---:|---:|---:|
| TRAIN C | 1077 | [135887.292922, 135887.293987] | 285 |
| TRAIN STOP | 1077 | [135989.681042, 135989.682106] | 144 |
| CAL C | 237 | [35255.730273, 35255.730508] | 72 |
| CAL STOP | 238 | [35161.445650, 35161.445886] | 36 |
| CAL learned | 238 | [35252.220910, 35252.221146] | 52 |

TRAIN material preferences (task first; ≥1 second for equal-task time): {'STOP': 2, 'C': 9, 'neutral': 13}. Tree activation: True. All labels and neutral or harmful contexts remain in TRAIN_PAIRS.json. Budget settings are paired within family, not independent replicates.

## Mechanism and validation

All 27 native C/STOP contexts have identical complete pre-gate physical/public prefixes and exact gate features. The 3 CAL B16 aliases instead have source-proved equality after projecting budget-only actor metadata; they keep the real C16 gate and real C8 source logs. No fictitious native STOP16 log is generated. Every STOP tail retains the ordinary controller and FIFO through H=128; it sends zero post-gate POSITION or SKIP. Normal END, MOVE launch and FIFO task service continue after the gate. Query counts are B/2, leaving half the registered budget unused. All new runs pass the original independent Decimal controller, ownership/collision, END/history and FIFO audit. Old C audit evidence is linked in ARM_HASHES.json.

Both new C compatibility raw logs are byte-for-byte identical to old C. Planner results match after excluding only host `planner_us`; the initial overstrict hash assertion and analysis-only amendment are preserved. No native run was repeated to resolve this analysis failure. All frozen scientific sources still match REGISTRATION.json.

Restricted T uses each agent’s fixed first four FIFO tasks and assigns H to unfinished tasks. Raw all-service ΣT and released-head restricted flow sums are retained separately. Query count is the only unit-cost proxy; no monetary tariff or production COST was supplied. Host runtime is separate from simulated time.

## Waiting decomposition

| TRAIN arm | Physical MOVE occupancy | END feedback hold | Residual not-moving time |
|---|---:|---:|---:|
| C | [36449.069876, 36449.121086] | [6406.091235, 6406.142520] | [6296.736394, 6296.838889] |
| STOP | [36411.329331, 36411.380464] | [6398.870346, 6398.921574] | [6341.697962, 6341.800323] |

The decomposition is over 24×16×128 agent-seconds. It includes censored active MOVEs. Residual not-moving time includes readiness/resource/planner waits and is not presented as pure resource waiting. Export intervals are numeric bounds, not statistical confidence intervals.

## Frozen simple selector

One depth-one tree predicts complete-tail task difference and timing gain from the ten public gate features. Exact split and leaf values are in MODEL_FROZEN.json; no CAL threshold selection or refit occurred. Single-gate decisions choose already verified complete tails, with selected raw SHA recorded in CAL_SELECTIONS.json.

```json
{
  "feature": 8,
  "threshold": "4992909/6400000",
  "left": {
    "tasks": "1/8",
    "time_gain": "-150785119/32000000",
    "n": 16,
    "weight": "8"
  },
  "right": {
    "tasks": "-1/4",
    "time_gain": "-674889/200000",
    "n": 8,
    "weight": "4"
  }
}
```

## Every development context

| Family / B | Δ tasks STOP−C | T gain C−STOP interval | Queries saved | Material preference |
|---|---:|---:|---:|---|
| empty-32-32_scen2_offset96_train_131101 / 8 | 0 | [-0.000047, 0.000047] | 4 | neutral |
| empty-32-32_scen2_offset96_train_131101 / 16 | 0 | [-1.779315, -1.779221] | 5 | C |
| empty-32-32_scen2_offset112_train_131102 / 8 | 0 | [-0.000041, 0.000041] | 4 | neutral |
| empty-32-32_scen2_offset112_train_131102 / 16 | 0 | [-4.620033, -4.619951] | 8 | C |
| empty-32-32_scen2_offset128_train_131103 / 8 | 0 | [-0.648653, -0.648565] | 4 | neutral |
| empty-32-32_scen2_offset128_train_131103 / 16 | 0 | [-0.000044, 0.000044] | 8 | neutral |
| empty-32-32_scen2_offset144_train_131104 / 8 | -1 | [5.268420, 5.268507] | 4 | C |
| empty-32-32_scen2_offset144_train_131104 / 16 | 0 | [-0.619710, -0.619622] | 8 | neutral |
| empty-32-32_scen2_offset160_train_131105 / 8 | 0 | [-0.583489, -0.583395] | 4 | neutral |
| empty-32-32_scen2_offset160_train_131105 / 16 | 0 | [-0.583489, -0.583395] | 8 | neutral |
| empty-32-32_scen2_offset176_train_131106 / 8 | 1 | [-40.671671, -40.671579] | 4 | STOP |
| empty-32-32_scen2_offset176_train_131106 / 16 | 0 | [-0.583488, -0.583396] | 8 | neutral |
| random-32-32-10_scen2_offset128_train_132101 / 8 | 0 | [-5.297590, -5.297498] | 4 | C |
| random-32-32-10_scen2_offset128_train_132101 / 16 | 0 | [-0.036270, -0.036178] | 8 | neutral |
| random-32-32-10_scen2_offset144_train_132102 / 8 | 0 | [-10.522689, -10.522591] | 4 | C |
| random-32-32-10_scen2_offset144_train_132102 / 16 | 0 | [-8.682291, -8.682193] | 8 | C |
| random-32-32-10_scen2_offset160_train_132103 / 8 | -1 | [-7.098657, -7.098566] | 4 | C |
| random-32-32-10_scen2_offset160_train_132103 / 16 | 1 | [-6.033070, -6.032979] | 8 | STOP |
| random-32-32-10_scen2_offset176_train_132104 / 8 | 0 | [0.470874, 0.470960] | 4 | neutral |
| random-32-32-10_scen2_offset176_train_132104 / 16 | 0 | [-0.000043, 0.000043] | 8 | neutral |
| random-32-32-10_scen2_offset192_train_132105 / 8 | 0 | [-3.098192, -3.098108] | 4 | C |
| random-32-32-10_scen2_offset192_train_132105 / 16 | 0 | [-16.621011, -16.620927] | 8 | C |
| random-32-32-10_scen2_offset208_train_132106 / 8 | 0 | [-0.000038, 0.000038] | 4 | neutral |
| random-32-32-10_scen2_offset208_train_132106 / 16 | 0 | [-0.648647, -0.648571] | 8 | neutral |
| empty-32-32_scen2_offset192_calibration_131201 / 8 | 0 | [-0.000040, 0.000040] | 4 | neutral |
| empty-32-32_scen2_offset192_calibration_131201 / 16 | 0 | [-7.077648, -7.077568] | 8 | C |
| empty-32-32_scen2_offset208_calibration_131202 / 8 | 0 | [92.050779, 92.050853] | 4 | STOP |
| empty-32-32_scen2_offset208_calibration_131202 / 16 | 0 | [-1.275593, -1.275519] | 8 | C |
| random-32-32-10_scen2_offset224_calibration_132201 / 8 | 0 | [-0.000041, 0.000041] | 4 | neutral |
| random-32-32-10_scen2_offset224_calibration_132201 / 16 | 1 | [10.586930, 10.587011] | 8 | STOP |

## Reproduction and boundaries

Run `rtk proxy python3 pipeline.py register`, `rtk proxy python3 pipeline.py TRAIN`, then the documented `finish_train.py` analysis recovery. For the registered CAL alias amendment run `rtk proxy python3 cal_alias.py register`, `rtk proxy python3 cal_alias.py run`, and `rtk proxy python3 close.py`. Existing output paths intentionally refuse overwrite; reproduce in a new sibling experiment directory with a fresh receipt contract. Do not rerun in this completed directory.

C/STOP are internal diagnostic strategies, not new external paper baselines. This result does not establish innovation, generalization to new map files, or production controller deployment. Mentor judgment and concrete next action are recorded in MENTOR_POSTEXEC.md.
