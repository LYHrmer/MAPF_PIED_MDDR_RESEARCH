# R20 external source and mechanism review

Status: PASS within the stated read-only scope. No native call, physical replay or complete collision recheck was performed. All 22 registered source/model/data/inherited pins match. The 36 primary-pair episode files match their run receipts. Frozen scientific files were not changed.

The new POSITION head is connected to the real optimizer. `engine.py` requires a delivered observation for the same active occurrence, checks the capture-time END prefix, passes capture progress and START-relative elapsed/age to the frozen predictor, and replaces only current residual. Future duration ratio remains the END-only predictor output. `_update_predictor` writes the resulting duration/progress to the actual author vertices; `solver_adapter.solve` captures those values before calling unchanged `graph.optimize`. Completed and staged vertices retain their respective END/future treatment. The original feasibility/whole-graph adoption checks and parent rollback remain in effect.

A direct saved-model witness at maze gate1, t=19.4166666667, agent21/v_21_5 has residual0.773194581874, encoded duration2.336894932463 and progress0.669135924285. Their product d(1-p) equals the residual. The saved author row `boundary_v_21_5_g` has RHS0.773194581874. Its future ratio2.336894932463 is exactly the unchanged END predictor output. This checks actual model consumption, not just a prediction log.

`run_study.py` freezes the END and POSITION models and their code, source/data/config registrations, uses policy-independent world seeds and refuses completed/unfinished duplicate attempts. The primary arms differ only by presence of the POSITION head; both use the same structural policy and budget. Reading all18 primary pairs confirms identical private physical profiles, final per-agent completions, makespan and query counts. Full query payloads are identical in17 pairs. The maze pause pair has different later payloads after its execution diverges, so “same query count/policy” must not be reported as “identical query stream” for that pair.

The exceptional pair has two legal orientation changes at19.4166666667, groups dg_agent24_23 and dg_agent30_50, and eight changed START/END timestamps. Raw events identify the exact downstream absorption:

| Agent | Linear last early-segment END | POSITION END | Common next START | Binding dependency END | Extra waiting absorbs |
|---|---:|---:|---:|---|---:|
|23, after v_23_8|59.7500000000|21.4166666667|138.7449703690|v_11_62 at138.7449703690|38.3333333333|
|6, after v_6_12|36.3880171561|23.0715050614|44.8164284741|v_26_18 at44.8164284741|13.3165120947|

For agent23 the next action v_23_9 also depends on v_24_44, which ends at123.6869396981 in both arms; v_11_62 is the latest release. Its waits are78.9949703690 (linear) and117.3283037024 (POSITION), and both complete at139.7449703690. For agent6 the next action v_6_13 has the same four dependency tails in both arms; v_26_18 is the last, later than v_30_14 at34.3880171561. Its waits are8.4284113180 and21.7449234127, after which both trajectories rejoin and finish at86.7856599690. Thus earlier local actions are real, but the later dependency releases determine the same downstream starts and final completion. This is post-hoc explanation of saved events, not another heldout test or a counterfactual experiment. The first local difference precedes the recorded late solver rejection; it is not explained by that later fallback.

The existing13 verifier negatives cover wrong elapsed, future END, capture age, occurrence, undelivered/private information, zero/wrong residual, future-ratio and encoded-progress corruption, ignored POSITION and CAS corruption/path traversal. I inspected their scope/receipts, without rerunning them. They are useful targeted controls, not exhaustive adversarial or floating-point certification; no missing item blocks the present source binding finding.

Finally, 122 versus298 newly executed author calls for the joint and linear arms is affected by shared exact-input cache reuse and arm order. It cannot support a solver speed claim. Remaining limits are the registered fixed-path, continuous-point/event setting and the absence of final completion improvement in this18-pair primary contrast; neither should be broadened into a claim of physical-robot validation or universal lack of information value.
