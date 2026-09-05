# 68R3 No-Skill Independent Logic Review

Date: 2026-09-05

Review class: FORMAL / INDEPENDENT LOGIC / NO-SKILL / BALLOT

Review completion status: CLOSED

Meaning of CLOSED: the assigned review was completed. CLOSED does not resolve, waive, or override any objection below.

Disposition: HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT

## 1. Scope and independence declaration

This review used basic logic applied only to the registered Candidate 68.

NO-SKILL: no SKILL.md or skill was read, invoked, or used. Claude and network search were not used. No other reviewer or consultant report, Candidate 68R1, 68R2, 68C0, 68C1, old 35-38 material, Q-CAL/Q-CONFIRM outcome, or scientific payload was read or used.

No implementation, build, test, simulator execution, parameter tuning, experiment, or scientific-payload generation was performed.

## 2. Candidate registration and identity checks

Candidate:
`/home/lyh/MAPF_PIED_MDDR_RESEARCH/68_PIE_COMMIT_BOUNDARY_STATE_ENVELOPE_UNDER_PROCESSING_AND_OBSERVATION_UNCERTAINTY_JOURNAL_ROUTE_CANDIDATE_20260904.md`

Review-start registration:

- SHA-256: `105ae41743f13a0add69751e0be322fbdd2ee99a81adfbdd9707ae7e3e8e0c5c`
- Bytes: `37575`
- Lines: `793`
- Registration hash: the candidate SHA-256 above

Review-end identity check, performed after analysis and before report writing:

- SHA-256: `105ae41743f13a0add69751e0be322fbdd2ee99a81adfbdd9707ae7e3e8e0c5c`
- Bytes: `37575`
- Lines: `793`
- Start/end result: `MATCH`

## 3. Auditable complete-reading proof

- Candidate body reads: exactly one.
- Read command: `rtk read /home/lyh/MAPF_PIED_MDDR_RESEARCH/68_PIE_COMMIT_BOUNDARY_STATE_ENVELOPE_UNDER_PROCESSING_AND_OBSERVATION_UNCERTAINTY_JOURNAL_ROUTE_CANDIDATE_20260904.md`
- Read exit status: `0`.
- Returned content had no truncation marker and remained below the configured output budget.
- First observed anchor: `# 68 PIE Commit-Boundary State Envelope under Processing and Observation Uncertainty`.
- Last observed anchor: `HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`.
- Ordered coverage observed: Sections 1 through 32, T68-COMP, T68-0 through T68-9, CEX68-01 through CEX68-12, all displayed matrices/tables, protected symbols, and final decision.
- Identity-only SHA/byte/line commands did not read or expose the candidate body.
- The candidate body was not reread.

## 4. Ballot result

The route is not logically closed. There are 20 BEARING objections and 3 NON-BEARING objections. Every BEARING objection is independently sufficient to retain the current disposition until a new-number successor supplies the stated closure evidence. The candidate's description of an item as a proof target does not count as that proof.

## 5. Stable objections

### O68R3-01 - BEARING - Physical phase and resource semantics are not closed

Objection: Sections 7-10 mix physical presence, protocol reservation, ownership, destination acquisition, and release without a state-to-resource mapping. Event 6 acquires the destination before event 7 releases the origin, while `unique physical location/phase` is required. It is therefore undecidable from the text whether an agent may simultaneously occupy origin, swept edge, and destination resources, and what exactly constitutes a collision.

Minimal failure witness: a robot's front enters the protected edge while its rear remains in the origin region. Treating it as only `AT(i,u)` leaves the edge unprotected; treating it as only `ON(i,u,v,tid)` releases the origin too early.

Revision obligation: define a transition system whose every physical phase maps to a set of simultaneously occupied resources; separately define prepared, reserved, owned, physically occupied, acquired, and released; define collision as incompatible simultaneous resource occupancy; prove each event transition preserves that invariant.

### O68R3-02 - BEARING - The commit boundary and TOCTOU linearization point are undefined

Objection: the envelope is inferred from evidence while execution continues, but no instant binds observation, envelope version, proposal digest, grants, epoch state, commit, and physical start. Safety of a state checked before COMMIT does not imply safety at COMMIT.

Minimal failure witness: the envelope records destination `v` free; before `i` commits, an earlier transaction for `j` becomes entitled to enter `v`; `i` then commits using the stale envelope and both transactions can claim `v`.

Revision obligation: define the decision linearization point and an atomic validation rule. Bind the proposal and envelope to resource versions and current epochs, require owners to reject changed versions, and either fence relevant transitions during commit or include every admissible intervening transition in the checked envelope.

### O68R3-03 - BEARING - L, U, and empty-envelope behavior are undefined

Objection: no update algorithm requires `L` to be predecessor-closed, makes `U` compatible with `L`, or resolves temporally incomparable evidence. If constraints make `E` empty, universal safety is vacuous, `MAY_OCCUPY` is empty, and `MUST_OCCUPY` becomes vacuous.

Minimal failure witness: accepted reports place one occurrence both before departure and after arrival at the same asserted boundary, yielding no consistent cut. A rule testing only empty MAY sets can falsely treat every resource as free.

Revision obligation: give monotone closure rules for L and U, an explicit evidence-time model, a consistency/nonemptiness check, and a mandatory `E = empty` transition to RECOVER or containment with no new discrete MOVE or WAIT.

### O68R3-04 - BEARING - Trust and fault quantifiers are not closed

Objection: `unforgeable` authenticates origin but does not establish physical truth. The text assumes accepted positive evidence is sound without defining its acceptance predicate or stating whether sensors, resource owners, commit authorities, actuators, and durable stores are crash-faulty, equivocating, or trusted.

Minimal failure witness: an authenticated but faulty sensor signs ARRIVED before arrival; the edge is released and an opposing traversal is admitted. Message integrity and epochs do not prevent this collision.

Revision obligation: state the fault model component by component; separate authenticity, integrity, freshness, and physical soundness; define the accepted-evidence predicate; and restate every theorem under those explicit trust assumptions or under a named physical interlock.

### O68R3-05 - BEARING - MOVE-to-WAIT refinement lacks final-batch closure

Objection: actions are described per agent, but changing one MOVE to WAIT changes origin occupancy and can invalidate another action in the same coordinated batch. Atomic resource grants do not prove the final transformed vector safe, and atomic COMMIT does not imply atomic physical execution.

Minimal failure witness: PIE proposes `a: u->v` and `b: w->u` under a release-before-acquire dependency. If `a` is changed to WAIT while `b` remains authorized, `b` enters occupied `u`.

Revision obligation: construct the final output vector before authorization, recompute occupancy and dependencies to a fixed point, cascade suppressions through dependent actions, and certify the final batch. If dependency components require all-or-none execution, specify and prove that protocol rather than relying on grant atomicity.

### O68R3-06 - BEARING - Following and rotation semantics conflict with the singleton claim

Objection: the literal rule forbids a MOVE whenever its destination has a possible occupant. That rejects ordinary following and cycle rotations even in a perfect singleton state. If such handoffs are instead intended to be accepted through event dependencies, no-start and partial-start semantics are missing. T68-6's added condition `no protocol guard is active` makes singleton identity weaker than the Section 21 claim of exact reversion whenever the envelope is singleton.

Minimal failure witness: three agents at `u`, `v`, and `w` receive the legal simultaneous cycle `u->v`, `v->w`, `w->u`. Literal destination checks suppress the cycle despite singleton certainty; accepting it without coupled execution allows one no-start to collide with its follower.

Revision obligation: declare whether baseline following and rotations are legal; define their release/acquire ordering and failure semantics; then either support them with dependency-closed certification or narrow all identity and usefulness claims to the explicitly conservative subset.

### O68R3-07 - BEARING - WAIT is not bound to a universally known endpoint and validity interval

Objection: a proposed WAIT refers to `the current endpoint`, while an envelope may contain multiple endpoint or edge phases. MOVE fallback permits WAIT when `u` has a holding certificate, but does not explicitly require the agent to be at that same occurrence in every cut. SH-DYNAMIC and SH-BRAKE also lack a version/epoch binding through command acceptance.

Minimal failure witness: the envelope permits the agent at `u` or already on `u->v`; `u` is statically holdable, so a nominal `WAIT(i,u)` is emitted even though the robot may be past the braking boundary.

Revision obligation: issue endpoint-bound WAIT only when the same occurrence is certified across all cuts and a resource-versioned holding grant remains valid for the decision; otherwise emit no new discrete action and reconcile/contain. Make final-batch incoming claims part of SH-DYNAMIC.

### O68R3-08 - BEARING - Future claims are not represented by current MAY occupancy

Objection: MAY/MUST describe occupancy in boundary cuts, but a committed transaction can be currently unoccupied and still entitled to enter later. Prepared and committed identifiers are listed, yet no formal resource lifecycle prevents a new grant from overlapping an unresolved prior commitment.

Minimal failure witness: `v` is physically free, but `j` holds an undelivered current-epoch COMMIT to enter it. MAY says no one occupies `v`; `i` receives a new grant; both commands later execute.

Revision obligation: define resource claim intervals from prepare through certified release, distinguish `may occupy now` from `may acquire under an outstanding transaction`, and prohibit conflicting grants across both sets until an explicit legal terminal transition.

### O68R3-09 - BEARING - Unique authority and atomic commit are assumed, not derived

Objection: a monotonic epoch does not by itself prevent two partitioned components from appointing authorities or make a distributed multi-resource commit atomic. Fencing works only if every physical acceptance point knows and enforces the winning epoch. The protocol has no reconfiguration, quorum, durable decision, or blocking rule sufficient for T68-5 and T68-8.

Minimal failure witness: old authority A is partitioned; component B advances the epoch and grants `v`; A remains able to deliver an older committed grant to an actuator that has not learned the new epoch. Two entrants are authorized.

Revision obligation: provide a linearizable ownership/reconfiguration model with quorum intersection or prohibit failover during uncertainty; identify the physical fencing enforcement point; specify durable commit records, partial-delivery behavior, and allowed blocking; prove no split-brain grant is executable.

### O68R3-10 - BEARING - Crash recovery and exactly-once physical execution are unspecified

Objection: message idempotence does not imply exactly-once actuation after executor, owner, or commit-authority crash. Boot/incarnation identifiers prevent identifier reuse but do not preserve knowledge of old physical occupancy or completed commands.

Minimal failure witness: an executor performs `tid`, crashes before durably recording COMPLETE, reboots, and receives the valid COMMIT again. It repeats the traversal or accepts a new transaction while the old resource remains occupied.

Revision obligation: specify crash points, stable records, write-before-actuate ordering, replay and tombstone rules, reconciliation of old incarnations, and physical occupancy recovery. Prove duplicate delivery across reboot cannot duplicate motion or release resources early.

### O68R3-11 - BEARING - A single finite event DAG cannot yet represent the admitted histories

Objection: unknown owner serialization is a choice between orders, while a DAG contains one fixed partial order. ABORT, RECOVER, reconfiguration, retry, and crash transitions are not integrated into D. No finite event universe or update rule is defined under unbounded processing and message delay.

Minimal failure witness: two unseen pending transactions can legally be serialized `x` before `y` or `y` before `x`. Fixing either edge can exclude the true history; leaving them unordered permits cuts that violate serialization.

Revision obligation: define the finite decision horizon and construct D from exact occurrences; represent unresolved alternatives with an explicit conflict/choice structure or symbolic disjunction; include recovery and authority transitions; prove the true history remains represented after every update.

### O68R3-12 - BEARING - T68-COMP hides the global feasibility problem

Objection: MAY/MUST are defined by existential/universal quantification over globally consistent cuts. Supplying them as inputs does not prove compression if computing or maintaining them already requires joint-cut reasoning. The resource-separable class and the claimed projection equivalence are explicitly absent.

Minimal failure witness: two envelopes have identical resource-local sets and touched-resource predecessor projections, but a remote unresolved serialization makes two required release events jointly feasible in one envelope and mutually exclusive in the other. A local decision cannot distinguish them.

Revision obligation: formally define the resource-separable class, the retained projection, and its update algorithm; prove indistinguishability witnesses cannot occur inside the class; prove soundness outside it; and exhibit a nontrivial included family without assuming precomputed global MAY/MUST oracles.

### O68R3-13 - BEARING - Computability and complexity claims are absent

Objection: `decidable` and `compact` are not accompanied by an input encoding, termination argument, storage bound, update cost, decision cost, or certificate-checking cost. Precedence plus exclusive-resource choices can represent many cuts despite small L/U descriptions.

Minimal failure witness: each of a growing family of unresolved owner-order choices doubles the set of legal cuts while the visible lower/upper ideals remain compact; a MAY query can still depend on a globally compatible choice assignment.

Revision obligation: define encoded input size; give algorithms for consistency, MAY, MUST, batch certification, and updates; state worst-case upper and lower complexity; and identify any tractable structural restriction without confusing representation size with query complexity.

### O68R3-14 - BEARING - Safety is quantified over start states, not admissible executions

Objection: T68-4 says a batch is safe for every physical state in E, but collision freedom is a trace property after emission. Action durations, no-start outcomes, partial delivery, physical overlap, and interleavings are not quantified. The listed graph resources also need an explicit mapping for every swept-volume conflict.

Minimal failure witness: two actions start from a conflict-free cut and use graph-distinct edges whose swept regions intersect; asynchronous execution produces a physical collision not represented by endpoint checks.

Revision obligation: define admissible execution traces and the collision predicate; quantify safety over every trace from every cut under the stated fault model; provide the physical-conflict-to-exclusive-resource abstraction and prove it is conservative.

### O68R3-15 - BEARING - Inactive bitwise identity is under-specified and potentially vacuous

Objection: singleton equality does not ensure the wrapper is inactive because its own resource guards, processing, task disclosure, ordering, or random-state consumption may differ. Conditioning T68-6 on every guard already being satisfied allows the theorem to avoid precisely the legal singleton batches most likely to activate guards.

Minimal failure witness: a perfect singleton contains the legal rotation in O68R3-06. The destination guards activate, so the wrapper changes bytes while T68-6 is simply inapplicable.

Revision obligation: define an operational inactive mode and exact compared byte channels; show how observation and audit metadata cannot perturb planner inputs, order, timing-dependent disclosure, or random state; reconcile T68-6 with the unqualified singleton-reversion claim or narrow that claim.

### O68R3-16 - BEARING - Triggered accountability is not yet a verifiable certificate

Objection: digests alone do not prove envelope validity, universal safety, or WAIT safety. Canonical serialization, evidence provenance, snapshot binding, final-batch binding, proof objects, and an independent checker are absent. T68-7 also says every output difference is MOVE-to-WAIT, while Section 12 permits no new action/containment after the point of no return.

Minimal failure witness: baseline emits MOVE, but the robot is already in progress and the wrapper emits no discrete action. The output differs and is not MOVE-to-WAIT, contradicting the literal T68-7 scope.

Revision obligation: define outcome classes for unchanged, MOVE-to-WAIT, continue-existing-transaction, no-action, and containment; bind a canonical certificate to candidate/proposal/envelope/evidence/resource versions and the final batch; specify checker acceptance rules; revise T68-7 to cover every class without contradiction.

### O68R3-17 - BEARING - Conditional liveness is too weak and its assumptions are insufficient

Objection: `commits or receives a newer explicit reason for rejection` permits infinite rejection and proves no movement. Fair service is undefined, and fair individual resource owners do not prevent multi-resource prepare deadlock or perpetual invalidation.

Minimal failure witness: transaction x holds a prepare for r while waiting for s, and y holds s while waiting for r. Each owner serves requests fairly, yet neither transaction commits; alternatively, a requester receives endlessly newer rejection reasons.

Revision obligation: define continuous enablement, stable feasibility, request identity, and fairness in temporal terms; add a deadlock-prevention or cancellation discipline; distinguish diagnostic responsiveness from physical progress; then prove the selected progress property under explicit eventual-communication and terminal-physical-outcome assumptions.

### O68R3-18 - BEARING - The counterexample suite is not closure-complete

Objection: the twelve traces cover important single faults but omit failures exposed by the candidate's own coupled semantics and do not map each trace to theorem premises and expected outcomes.

Minimal failure witness: O68R3-05's transformed-batch following collision is not represented by CEX68-01 through CEX68-12.

Revision obligation: add minimal traces for TOCTOU, partial batch transformation/execution, following, rotation, empty E, crash windows, stale replay across incarnation, split-brain reconfiguration, dynamic WAIT invalidation, and lost cross-resource correlation. Give each trace an initial state, event order, expected decision, invariant, and theorem mapping.

### O68R3-19 - BEARING - Baseline fairness is not operationally specified

Objection: `strict same-compute` and `natural-runtime` are labels, not protocols. The candidate does not yet equalize information, preprocessing, safety obligations, protocol overhead, adaptation effort, or failure handling across PIE-D and external methods.

Minimal failure witness: candidate runtime excludes envelope construction and transaction waiting while a comparator runtime includes all coordination; throughput then favors the candidate by accounting rather than method.

Revision obligation: preregister common inputs, information availability, safety contract, preprocessing, compute accounting, protocol costs, adaptation rules, timeout/censoring treatment, and comparator-domain mismatches. Keep every launched unit in the declared denominator as already required.

### O68R3-20 - BEARING - Pure simulation cannot validate the physical trust assumptions as written

Objection: a simulator can falsify an algorithm with a counterexample, but cannot establish sensor soundness, braking, fencing enforcement, or physical conformance when those properties are simply encoded by the same state machine under test.

Minimal failure witness: the simulator generates ARRIVED and release from one shared truth variable, so false release is impossible by construction and zero collisions merely restates the simulator assumption.

Revision obligation: separate conditional formal claims from performance evidence; use an independent ground-truth collision oracle and independently injected protocol/observation faults; predeclare falsifying traces and bounded formal checks; limit simulation conclusions to the modeled assumptions and do not present them as validation of physical trust or hardware interlocks.

### O68R3-21 - NON-BEARING - Aggregate notation E68-O is undefined

Objection: T68-0 uses `E68-O`, while the taxonomy defines E68-O1 through E68-O6 but no aggregate symbol.

Minimal failure witness: a proof reader cannot tell whether E68-O includes every observation class or only endpoint ambiguity.

Revision obligation: define E68-O explicitly as the intended set or replace it with the exact subclasses in every theorem.

### O68R3-22 - NON-BEARING - Cross-sender age ordering is ambiguous

Objection: OBSERVE classifies reports by `age ordering`, although sequence identifiers are sender-local and synchronized wall clocks are rejected.

Minimal failure witness: two current-epoch reports from different senders have unrelated sequence counters; imposing a total age order can discard the wrong report.

Revision obligation: use sender-local sequence and explicit causal/epoch relations; treat reports from unrelated channels as incomparable unless a trusted ordering relation exists.

### O68R3-23 - NON-BEARING - Edge capacity policy is implicit

Objection: exclusive DE and OE resources appear to impose unit capacity for both same-direction and opposite-direction use, but this scope choice is not stated.

Minimal failure witness: two physically separated robots on a long directed edge are rejected as a conflict under unit-capacity DE even if the physical model could safely permit spacing.

Revision obligation: state unit-capacity edge semantics as a conservative scope restriction, or define segmented/capacity resources and their physical conflict mapping. Do not mix the two policies in baseline comparisons.

## 6. Mandatory-topic coverage map

| Required audit topic | Primary objection(s) | Result |
|---|---|---|
| Definition closure | O68R3-01, O68R3-03, O68R3-04 | BEARING gaps |
| Quantifiers | O68R3-03, O68R3-04, O68R3-14 | BEARING gaps |
| State/action semantics | O68R3-01, O68R3-07, O68R3-14 | BEARING gaps |
| TOCTOU | O68R3-02, O68R3-08 | BEARING gaps |
| Batch MOVE-to-WAIT coupling | O68R3-05 | BEARING gap |
| Following/rotation | O68R3-06 | BEARING gap |
| WAIT safety | O68R3-07 | BEARING gap |
| Resource occupancy/transaction authority | O68R3-01, O68R3-08, O68R3-09 | BEARING gaps |
| Crash/replay/partition | O68R3-09, O68R3-10 | BEARING gaps |
| Computability | O68R3-11, O68R3-12, O68R3-13 | BEARING gaps |
| Complexity | O68R3-13 | BEARING gap |
| Inactive bitwise identity | O68R3-06, O68R3-15 | BEARING gaps |
| Triggered certificate | O68R3-16 | BEARING gap |
| Liveness | O68R3-17 | BEARING gap |
| Counterexample coverage | O68R3-18 | BEARING gap |
| Baseline fairness | O68R3-19 | BEARING gap |
| Pure-simulation falsifiability | O68R3-20 | BEARING gap |

## 7. Protected-symbol audit

The review assigns no value, interval, bound, default, prior, hint, or tuning direction to any protected symbol. `H`, `T_delay`, `B_CAL`, `B_max`, `B*`, `P_active`, and `density N` remain unassigned. Commit length and timing quantities remain symbolic.

## 8. Required closure disposition

Candidate 68 remains a plausible question, not a closed formal route. The most immediate dependency order is: close physical/event semantics and fault quantifiers; close TOCTOU and transaction authority; define batch/following/rotation/WAIT semantics; then establish the envelope algorithm, compression class, complexity, verifiers, and liveness statement. Baseline and simulation protocols cannot cure a failed semantic or safety theorem.

All O68R3-01 through O68R3-20 objections are BEARING and require root integration in a new-number successor. O68R3-21 through O68R3-23 are NON-BEARING but should be corrected with that successor.

Final review state:

`CLOSED / BALLOT COMPLETE / BEARING OBJECTIONS PRESENT`

Final project disposition:

`HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`

Report self-identity is measured only after this final write, because embedding a file's resulting SHA-256 inside that same file would change the identity. The exact report SHA-256, byte count, and line count are supplied in the final audit handoff without rereading the report body.
