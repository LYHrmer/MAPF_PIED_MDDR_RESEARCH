# R9 result ledger

Exploratory 6 mechanical + 24 held-out runs, all normal native exits, full4000 held-out ticks. Model frozen before tests; no retuning.

|Held-out policy|Normal task END|First10 FIFO restricted tick sum|Completed primitive rows|Censored nodes|
|---|---:|---:|---:|---:|
|Author hm|184|2233212|10847|116|
|History|186|2237230|10895|163|
|Learned|188|2232200|10979|163|

Learned−history task signs: one positive(+2), seven zero, zero negative. Positive is random951922 nominal only. Restricted time: four better, four identical. Five first-action divergences all share exact initial snapshot/frontier; two occur at tick1 with zero online history. Four map/task families only; paired conditions are correlated.

CAL motion MAE(history/learned)=1.38516/1.40756. Same held-out hm traces: step0=1.29392/1.48518, step1=1.22478/1.38349. All12 primitive×direction motion groups have worse learned MAE. Positive task result cannot be attributed to better absolute prediction accuracy or proven online adaptation.

Mechanical nominal:5/5/5 tasks; pause:5/4/4. These negative mechanism results remain separate from test totals.

Reconstructed old TRAIN/CAL22,153 complete primitive labels, 161 censored; independent refit coefficient max difference9.23e−11. New runs33,076 labels independently verified, feature difference0. 30 full execution/geometry checks PASS; 11 malformed-input controls rejected. 34 raw archives include four pre-execution socket failures. See REPORT.md for scope and all links; summary.csv/json, prediction_same_hm_traces.json, bias_and_divergence.json contain exact per-condition values.
