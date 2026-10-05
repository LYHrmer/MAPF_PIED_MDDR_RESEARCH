# R19 independent execution acceptance

This review reads the frozen R19 execution and original R18 TRAIN model package. It launches no solver or physical episode and imports neither the execution engine nor predictor. `audit_episode.py` implements the new R19 schema and lossless CAS decoding directly; it never rewrites a record's schema to make the older verifier accept it. `physical_math.py` contains only the verbatim R18 independent event/trajectory/disturbance checks named and hashed in `BASE_PROVENANCE.json`.

## Actual model consumption

The authoritative adapter is error-guidance R19 `engine.py`, methods `Simulator._estimate`, `_update_predictor`, `public_snapshot` and `run`. `_estimate` receives original nominal duration, status, elapsed since the current START and delivered END history. It excludes dependency waiting from elapsed, and only earlier END records enter model features. The independent checker recomputes the lognormal conditional mean with SciPy; the frozen runtime uses standard-library survival arithmetic.

For an active action, the adapter records `d=max(nominal*future_ratio, remaining, eps)` and `p=1-remaining/d`. Thus the original author's actual residual expression `d*(1-p)` equals the predicted conditional remaining time. The encoded duration is an optimizer parameter; it is not a claim that the full action actually lasts `d` seconds. Future staged actions use original nominal duration times the unconditional future ratio, and completed actions retain their actual delivered duration and progress one.

The author's `dependency_group.py:within_horizon` sums full predecessor durations without multiplying by progress. Consequently, this adapter can affect legal horizon qualification through its encoded duration as well as the optimization objective through its residual. The independent checker reconstructs the author's mutable first active head from whole-group switch history and evaluates this same horizon predicate. It does not silently replace that predicate with a residual-time interpretation.

When a POSITION from the current occurrence has actually been delivered, the common registered rule overrides only the active residual with `max(0,(1-captured_progress)*nominal*all_history_ratio-(now-capture))`. The END-only model's unconditional future ratio remains intact. This is a common linear-history override, not a learned joint posterior or a remaining-segment rescaling. Every prediction record binds public input, model output, chosen provider and optimizer encoding; capture and solve receipts identify the actual records used.

## Acceptance evidence

| Requirement | Independent evidence |
| --- | --- |
| Scientific identity | Registered code/model/case hashes, source pins, raw receipt hash and registration/model-before-run chronology |
| R19 CAS | Reference schema, canonical hash, expected path, uncompressed byte count, complete static/dynamic graph reconstruction and full graph hash |
| Public model input | Exact allowlist, original nominal geometry, START-relative elapsed, all and only earlier delivered END records |
| Conditional inference | Independently reconstructed history features, fitted parameters and SciPy survival expression; no predictor import |
| Actual adoption input | Per-capture and per-solve prediction keys bound to graph durations/progress; completed and staged actions accounted for |
| POSITION handling | Actual captured geometry, delivery event/time, occurrence identity, stale discard and exact common override |
| Structure and STOP | Actual adopted parent directions at capture, all-head qualification, author horizon, DAG path relaxation and exact public structural score/ranking/cap |
| Legal execution | Whole-group conservation, changed heads STAGED, rejected candidate retains exact parent, actual START dependencies already END |
| Full finite episode | START/END conservation, complete continuous affine paths including initial wait/pause/terminal hold, shared disturbance regeneration and full outcome/query/solver accounting |
| All solver attempts | Before/candidate/after/log/model CAS hashes, including failures, plus exact cache provenance; numerical residual proof is a separate execution-team audit |

The final `COMPLETED_AUDIT.json` passes all **324 completed scientific episodes** and **221,381,042 logical assertions**, with 324 recorded successful completions. The last incremental pass added 52 proofs and reused 272 unchanged proofs. It launched zero scientific, physical or solver episodes. The 18 registered matrix rows blocked by initial ECBS failure remain outside this execution count. These results do not imply that every solver incumbent was feasible; rejected candidates and exact parent fallback are retained and covered by the separate numerical model audit.

`COMPLETED_AUDIT.json` lists the completed scientific receipts actually audited. Initial ECBS failures have no execution episode; they remain in the root registered denominator and are not manufactured into successful physical records. A verifier PASS means the available record agrees with reconstruction, separately from the recorded execution success.

## Mechanical verification and portability

`VERIFIER_SELFCHECK.json` rejects eight in-memory corruptions: dependency wait substituted for elapsed, future END as a feature, zero substituted for the conditional mean, a corrupt future ratio, a private feature, ignored delivered POSITION, a wrong byte count for an already cached CAS object, and path traversal. These changes never touch raw records.

`RELOCATION_CHECK.json` moves an existing R0 pilot's repository files and evidence store into separate temporary directories and verifies them without changing the receipt. The pilot's `query_budget=None` is independently interpreted as the inherited 2N default by its explicit test adapter; formal R19 records register N directly. Author checkout paths remain external read-only references in that mechanical test.

`SCIENCE_RELOCATION_CHECK.json` additionally executes the real CLI on a relocated formal learned-no-query episode. Its 155 copied dependencies include the review code, scientific root, separate CAS store, model bundle, R18/R16 sources and the author checkout files. All 67,294 assertions pass with unchanged receipt bytes. The minimum model bundle for that audit is `MODEL.json`, `predictor.py`, `MODEL_FREEZE.json`; the model public schema and full manifest remain useful documentation. This is another verification of existing evidence, not another scientific sample.

The general command is `python3 audit_episode.py --episode EPISODE --root R19_ROOT --store CAS_ROOT --bundle MODEL_BUNDLE --path-map OLD_PREFIX=NEW_PREFIX --output AUDIT.json`. `--path-map` may be repeated for externally retained author files. Historical absolute paths remain in the receipt; only the verifier resolves them to a supplied location.

`audit_completed.py` reads only finished RUN_RECEIPT files. It reuses a PASS only when the episode hash, verifier hash and every source/case/receipt/CAS/model dependency hash still agree. Such reuse is evidence reuse, not another experimental sample. The logical assertion count likewise is not a sample size.

## Interpretation boundary

The model package's nested TRAIN prediction metrics are in `../REPORT.md`; the learned residual predictor did not outperform the EWMA survival reference on active-gate MSE or MAE. The separately frozen `../heldout_r19/REPORT.md` evaluates all nine frozen predictors on 42 common history-no-query TEST trajectories without retraining: learned START MSE is lowest, but active-gate MSE and MAE do not beat the EWMA survival reference in either the core or N64 cohort. Full finite SADG execution outcomes determine the scheduling effect separately. This audit does not establish publication novelty, calibrated probabilities, full LMAPF, finite-body safety, robot dynamics or deadline compliance. Concurrent wall times are diagnostic. Numerical feasibility of all candidate models, including rejected incumbents, is established only by the separate full-payload verifier, whose report must accompany this one.
