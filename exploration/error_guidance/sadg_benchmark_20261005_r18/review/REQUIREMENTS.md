# Independent R18 acceptance requirements

The verifier's `passed` means the available record agrees with the independently reconstructed evidence. It is separate from an episode's `success`: a correctly recorded collision, truncation or constructor failure is a retained negative experiment result. Verification never upgrades a failed episode into a safe completion.

| Requirement | Acceptance evidence | Failure treatment |
| --- | --- | --- |
| Author identity | Original author pin and each source file hash; Python-MIP/CBC version metadata retained | Discrepancy prevents acceptance; no silent alternative optimizer |
| Scientific freeze | Registration source pins equal receipt specification; source/case/model hashes match; registration/model UTC precedes execution | A changed input or implementation is a new registered attempt |
| Original path identity | Case schedule/dimensions bind geometry; complete compiled route equals input route after declared WAIT collapse | Missing case is an explicit pilot limitation, not full path validation |
| Per-agent task conservation | One current cursor, one START/END per occurrence, type-1 predecessor ended before successor starts; completion from final actual END | Include unfinished tasks in common-H restricted completion |
| Dependency conservation | Every complete before/after graph has same vertices/type-1 and paired dependency families; whole-group switches only | Partial/deleted relation is a verification failure |
| Commitment safety | Every changed candidate head was STAGED, group qualified, both graphs DAG, each actual START's active tails already ended | An engine `guard.passed` flag alone is insufficient |
| Solver incumbent | For saved feasible candidates, actual compressed model hash and independently recomputed each row, bound, integrality and objective; rejected candidates audited separately | Feasible flag alone is insufficient; failed candidate retains exact parent directions; missing failed-model payload prevents independent residual reconstruction |
| Full physical path | Entire time interval from initial state through final residence, contiguous affine segments, original movement edge | No omission of initial waits, stationary resident, pauses or terminal hold |
| Continuous point safety | Analytic closest distance over every overlapping interval, including interior extrema | Sparse time samples do not establish safety; body/dynamics claims excluded |
| Shared disturbances | Hash-keyed per-agent/action profile independently regenerated and bound to each raw MOVE speed/pause/END duration | Never redraw by policy execution order or expose private profile to callback |
| Query evidence | Selected eligible occurrence, actual capture position, canonical body and byte count, fixed delivery latency | Stale captures charged and discarded; cannot update successor |
| Public information | Exact whitelist; delivered END history/ratio/CV, measurement history/age/projection, public graph influence reconstructed | Any private metadata field or inconsistency is rejected |
| Equal-budget behavior | Same N/cap/latency and total purchased query accounting; chosen action reconstructed from registered public policy/model | Dense arm explicitly uncapped; do not present it as equal-budget superiority |
| Matched value labels | Same case/graph/world/config, full clipped physical/public prefix, true empty versus registered singleton query, history continuation | A post hoc best gate or different prefix is not a valid label |
| Grouped learning | TRAIN-only rows; whole map/scenario family retained across N/disturbance/probes; fold-only weighting/moments/normal equation; registered alpha and threshold | CAL/TEST cannot repair fitted coefficients or hyperparameters |
| Evaluation denominator | Every planned world/arm has a result or explicit failure; raw outcome/query/solver accounting matches aggregate report | Never drop failures because they do not yield useful learning labels |

`audit_episode.py` checks raw execution without importing engine or policy code. `audit_study.py` reads completed `RUN_RECEIPT.json` only, avoiding partially written live runs. It accepts CAL/TEST access only after the saved model-freeze receipt verifies. Its default scope is TRAIN.

Incremental audit reuse binds the episode and verifier hash plus every case, scientific source, RUN/solve receipt, before/after graph, cache index and compressed model dependency. A missing or changed dependency invalidates that audit cache. File content hashes are freshly computed once per file per invocation and reused in that invocation only while file size/mtime are unchanged. An episode JSON hash alone is not a sufficient cache key.

The separately registered warehouse TEST scheduler calls the original frozen episode function after model freeze. CAL and TEST may interleave; acceptance requires the same frozen model and specifications before either, not all CAL completion before any TEST. Sandbox process IDs are not treated as globally unique. Concurrent wall times are diagnostic and cannot support a controlled runtime ranking.

`VERIFIER_SELFCHECK.json` records six in-memory negative cases: wrong total query count, forbidden future-speed field, wrong history ratio, forged captured progress, missing trajectory prefix, and a colliding path with the original successful engine flag. Original data remain immutable and no new native or solver episode is launched.

Some guarantees necessarily remain source-linked: the callback is passed a fresh whitelist snapshot, optimizer code is the registered author implementation, and simulator time does not include measured solver wall time. Raw artifacts can establish the supplied input, returned incumbent and executed trace; they cannot establish real-robot footprint or deployment deadline guarantees. UTC receipts are local execution chronology, not an external timestamp attestation.

The original ECBS map-obstacle, discrete swap and scenario-row validation belongs to `../data/`; the episode verifier independently binds that exact route to the continuous trace. The stationary adapter retains physical occupancy and reports completion at time 0; it does not pretend that the author optimizer originally handled empty routes.

The full scientific result is exploratory even when every mechanical check passes. A useful information-value or policy-improvement claim still depends on the frozen learned policy's actual held-out effect against the strong public-history rule, with query cost and finite benchmark uncertainty shown separately.

Final rejected-incumbent evidence boundary: 11 calls over five unique inputs report OPTIMAL but fail the logged constraint-residual check. Failed full-model payloads were not saved or cached, so their residuals and numerical cause cannot be independently reconstructed. The audit independently verifies exact before/after parent-graph retention and the resulting complete physical traces. This is a disclosed payload limitation, not a solver-success claim; see `FAILURE_DIAGNOSTICS.json`.
