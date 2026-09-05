# 69 PIE-DTRS-KC: Knowledge-Certified Proposal-Preserving Transactional Refinement

Date: 2026-09-05 (Asia/Shanghai)

Artifact class: `NEW-BYTE PRE-EXPERIMENT SUCCESSOR CANDIDATE / NONBALLOT`

Candidate state: `OPEN / REVIEWS REQUIRED`

Control state: `HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`

## 1. Succession and immutable boundary

Candidate 69 succeeds, but does not edit or approve, Candidate 68.

Parent Candidate 68 identity:

- SHA-256: `105ae41743f13a0add69751e0be322fbdd2ee99a81adfbdd9707ae7e3e8e0c5c`
- Bytes: `37575`
- Lines: `793`

Root rejection basis: `68R4_PIE_COMMIT_BOUNDARY_THREE_REVIEW_ROOT_SYNTHESIS_AND_SUCCESSOR_RULING_20260905.md`.

Candidate 69 is not an implementation plan masquerading as a result. It supplies a formal pre-experiment object, algorithms at specification level, proof obligations with derivations, counterexamples, fixed source evidence, and a preregistration contract. No build, test, simulator run, parameter choice, tuning, scientific payload, or result is authorized.

## 2. Plain-language problem contract

PIE may compute a valid joint action from a state that is no longer known to be current when the action is committed. Processing continues while reports can be stale, missing, duplicated, reordered, mutually inconsistent, or falsely claim completion. Choosing one optimistic location can release a resource too early. Stopping one robot independently can also make a following robot collide with the newly retained origin.

PIE-DTRS-KC therefore asks one narrow question:

> Given one exact batch of actions whose MOVE choices ultimately originate only from PIE, which of those exact MOVEs can still be committed from the knowledge available at the commit boundary, and what is the least mandatory cascade of MOVE-to-WAIT refinements needed to make the final batch certifiable?

The method does not invent a detour. It either preserves the exact authorized MOVE, emits WAIT at a certified holding occurrence, or issues no new discrete authorization and keeps the physical transaction contained.

## 3. Permanent semantic exclusions

- A PIE-D MOVE that fails to start and leaves the agent at its origin is `delay`, not a new error model.
- Consecutive “slowdowns” inside one standard discrete tick are a semantic no-op and are excluded.
- Multi-tick slow motion is out of the core model unless an explicit edge-in-progress state, interval occupancy, and speed-dependent risk model are added in a later separately reviewed artifact.
- Wrong-edge motion, arbitrary off-graph displacement, unmodeled localization geometry, braking-controller correctness, and physical sensor calibration are excluded from the core claim.
- PIE is the only source of a new MOVE destination.
- The refinement layer never changes a MOVE into a different MOVE.
- Generic ADG, commit-cut, discrepancy-channel, shield, transaction, fencing, abstract-interpretation, and query mechanisms are prior tools, not claimed inventions.
- No claim is made that pure simulation validates real hardware.

## 4. Research contribution candidate

The candidate contribution is the conjunction of five objects:

1. a finite knowledge abstraction over issued action occurrences and typed physical-resource phases;
2. a necessary evidence boundary for safely shrinking that abstraction when completion reports may be false;
3. a proposal-preserving batch certifier with a least mandatory reverse WAIT closure;
4. a composition contract with a fenced, fail-closed resource transaction substrate;
5. a targeted evidence-repair policy that can recover concurrency without creating an alternative MOVE.

No object alone is presented as novel. The conjunction remains novelty-OPEN until formal reviews and the primary-source exclusion audit close.

## 5. Primary-source claim chart

| Work | Primary source | What it already establishes | Difference candidate, not settled novelty |
|---|---|---|---|
| MAPF-DP | `https://doi.org/10.1609/aaai.v31i1.11035` | MOVE failure leaves an agent at its current vertex; FSP/MCP execution policies | Feedback truth is not the studied uncertainty; action failure remains delay here |
| PIE-D | `https://doi.org/10.1609/aaai.v39i22.34506`; `https://github.com/YueZhang-studyuse/LMAPF-delay` | Concurrent planning/execution using a predicted next commit-window state and delay-aware execution | Candidate certifies a fixed proposal against a non-singleton commit-time knowledge state |
| Hönig et al. 2019 | `https://doi.org/10.1109/LRA.2019.2894217`; author full text `https://whoenig.github.io/publications/2019_RA-L_Hoenig.pdf` | ADG robust execution, planning/execution overlap, deterministic commit cut; assumes robots report completion in a timely manner | Candidate studies unreliable completion/current-state evidence and does not claim ADG or commit cut |
| Liu et al. 2024 | `https://doi.org/10.1609/socs.v17i1.31543` | Fixed-path MOVE/WAIT online coordination under uncertain action duration; following conflicts; feasibility hardness; many agents moving | Candidate takes one fixed PIE-derived batch and uncertain knowledge rather than known evolving locations |
| Liu et al. 2026 | `https://doi.org/10.1016/j.artint.2026.104586` | LDG, evolving locations, maximal moving set, feasibility algorithms, conflict/deadlock freedom under timing delays | Candidate does not claim maximal moving-set coordination and must compare against this full method when an executable artifact is available |
| POD 2026 | `https://doi.org/10.1016/j.robot.2026.105701` | Typed protocol-observation discrepancy for occupancy, reservation, queue, and progress; age routing and recovery under noise/delay/faults | Candidate treats typed discrepancy as prior input machinery and asks for a proof-carrying fixed-proposal commit decision; full-text exclusion remains OPEN |
| Yang and Yoshida 2026 | `https://arxiv.org/abs/2604.06873` | Belief-style local Mealy shields and safe action sets under partial observation | Candidate does not claim generic belief shielding; it admits only exact fixed-proposal MOVE or WAIT and includes batch/transaction coupling |
| Shahar et al. 2021 | `https://doi.org/10.1613/JAIR.1.12397` | Safe MAPF under bounded action-duration uncertainty and online replanning variants | Candidate does not plan duration-robust paths or synthesize new paths |
| UM* | `https://doi.org/10.1609/icaps.v27i1.13866` | Belief-space multi-agent planning under uncertainty | Candidate is a bounded execution refinement, not whole-trajectory belief-space planning |

Route-killing rule: if primary text shows another method already combines the same fixed-proposal knowledge certificate, reverse closure, exact inactive identity, and message-fault transaction semantics, Candidate 69 is rejected rather than cosmetically renamed.

## 6. Formal objects

### 6.1 Environment and proposals

Let the discrete workspace be a graph `G = (V,E)` and let `A` be the finite agent set. Each agent has a current action occurrence, not merely a vertex label; revisits therefore remain distinct.

PIE emits a canonical proposal byte string `P` and decoded action vector `pi`. An action is either `WAIT(i,u)` or `MOVE(i,u,v)` with `{u,v}` in `E`.

An existing delay-execution policy such as the PIE-D MCP layer may first transform `pi` to `mu`, subject to:

`mu_i = pi_i` or `mu_i = WAIT at the same certified origin`.

PIE-DTRS-KC transforms `mu` to `rho`, subject to:

`rho_i = mu_i`, `rho_i = WAIT at the same certified occurrence`, or `rho_i = NO-NEW-AUTHORIZATION` when an ordinary WAIT cannot be proved safe.

Thus every MOVE in `rho` is byte-identical to a MOVE in `mu` and ultimately in `pi`. No alternative MOVE exists in the refinement codomain.

### 6.2 Disturbance classes

- `D-start`: an authorized MOVE does not start and the agent remains at origin. This is delay.
- `D-process`: proposal computation and commit processing consume time while prior physical transactions may advance.
- `F-stale`: an authentic report describes an older occurrence or epoch.
- `F-missing`: an expected report is not delivered.
- `F-duplicate`: an already processed report is delivered again.
- `F-reorder`: authentic reports arrive outside causal or sender order.
- `F-conflict`: reports cannot all describe one physical history.
- `F-false-complete`: an authentic source claims terminal progress that did not occur.
- `F-state`: a current-state report has an incorrect payload.
- `F-partition`, `F-crash`, `F-restart`: protocol participants become unreachable or lose volatile state.

Safety is distribution-free over the admitted fault class. Probabilities are evaluation inputs only and do not enter the safety theorem.

### 6.3 Resource types

The resource universe is typed:

- `VERTEX(v)`: protected vertex region;
- `D_EDGE(u,v)`: directed swept-volume region;
- `OPP_EDGE({u,v})`: mutex for opposite-direction traversal;
- `ORIGIN_RELEASE(i,u,k)`: obligation proving occurrence `k` has cleared origin `u`;
- `DEST_ACQUIRE(i,v,k)`: obligation governing destination entry;
- `HOLD_RIGHT(i,u,k)`: versioned permission to remain at occurrence `k`;
- `TXN_CLAIM(tid,r)`: protocol claim from PREPARE until certified terminal release.

For each resource `r`, state is a typed tuple:

`RState(r) = (phys, swept, reservation, authority, epoch, enforce, prepared, committed, release_cert)`.

These fields never alias:

- `phys` is a physical occupant assertion;
- `swept` is an in-progress swept-volume assertion;
- `reservation` is a protocol holder;
- `authority` is the unique grant writer under the substrate assumption;
- `epoch` is the fencing generation;
- `enforce` is the physical admission point that rejects stale epochs;
- `prepared` and `committed` are transaction sets constrained by exclusivity;
- `release_cert` is a monotone physical clearance fact.

### 6.4 Physical phases and footprints

Each issued MOVE occurrence has ordered phases:

`AT_ORIGIN -> PREPARED -> COMMITTED -> STARTED -> CLEARED_ORIGIN -> ON_EDGE -> ACQUIRED_DEST -> CLEARED_EDGE -> AT_DEST -> COMPLETE`.

ABORT is allowed only before physical start. RECOVER may inspect any nonterminal phase but cannot erase physical occupancy.

The footprint function is conservative:

| Phase | Required protected resources |
|---|---|
| AT_ORIGIN/PREPARED/COMMITTED before start | origin vertex and holding right |
| STARTED before certified origin clearance | origin vertex, directed edge, opposite-edge mutex, destination claim |
| CLEARED_ORIGIN/ON_EDGE | directed edge, opposite-edge mutex, destination claim |
| ACQUIRED_DEST before edge clearance | directed edge, opposite-edge mutex, destination vertex |
| CLEARED_EDGE/AT_DEST/COMPLETE | destination vertex until a later certified release |

The footprint can over-approximate geometry. Pure simulation tests this declared resource model; it does not certify that a real robot's swept volume matches it.

## 7. Trust and impossibility boundary

### 7.1 Distinct evidence properties

Authentication proves sender identity. Integrity proves bytes were not changed in transit. Freshness proves occurrence/epoch order. None proves physical truth.

Ordinary COMPLETE and current-state reports may be wrong. Such a report may widen the knowledge set or trigger recovery, but cannot alone remove a physical phase or release a contested resource.

A shrinking fact must be one of:

- a trusted monotone physical-clearance certificate accepted by the resource enforcement point;
- corroborated independent evidence under an explicitly declared fault bound;
- a fact entailed by a durable transaction record plus an enforcing physical interlock.

The core safety proof uses the first or third form. The second form is an optional extension and requires a separately stated source-independence/fault assumption.

### 7.2 Indistinguishability theorem

**Theorem 69-I.** Suppose every source capable of asserting release may produce the same false terminal message in one history, and no independent physical interlock prevents entry. Then no algorithm receiving those messages can both authorize a contested MOVE in the apparently released history and guarantee collision freedom.

**Proof.** Construct histories `h_clear` and `h_occupied` with identical delivered bytes, epochs, and timing. In `h_clear`, the previous occupant has cleared the resource; in `h_occupied`, it has not, but its source emits the same terminal report. The decision procedure has identical observations and therefore returns the same authorization. If it authorizes entry, the execution in `h_occupied` conflicts. If it never authorizes entry, it preserves safety but gives up nontrivial progress in `h_clear`. No message-only procedure distinguishes the histories. QED.

Consequence: safety under arbitrary false completion is possible by conservative blocking; safety plus progress requires at least one declared sound clearance/interlock path. This is a conditional model statement, not a claim about real sensor reliability.

## 8. Finite knowledge abstraction

### 8.1 Occurrence-index domain

Each agent has a finite active occurrence list `Q_i` containing issued but not checkpoint-compacted event occurrences. An occurrence key is:

`(agent_id, boot_id, action_seq, event_seq)`.

For each agent, the monitor stores:

- `lo_i`: greatest phase occurrence proved by trusted monotone evidence;
- `hi_i`: greatest phase occurrence still physically possible from issued commands and unresolved outcomes;
- `holes_i`: received later events whose predecessors are not yet proved;
- `choice_i`: unresolved mutually exclusive reports;
- `txn_tags_i`: cross-agent transaction correlations that may not be joined away.

The abstract element `K_i` denotes every prefix-consistent phase between `lo_i` and `hi_i` that respects retained transaction tags. Revisited vertices are mapped through occurrence IDs, never collapsed by vertex name.

### 8.2 Evidence update algorithm

For one input message `m`:

1. reject if its candidate, agent, boot, transaction, or epoch namespace is invalid;
2. ignore as an idempotent duplicate if the exact message key and payload digest are already durable;
3. retain but do not apply a sender-later message whose causal predecessor is absent;
4. discard a losing epoch at the enforcement boundary without narrowing `K`;
5. join conflicting ordinary payloads, thereby widening or preserving `K`;
6. advance `lo_i` only on an accepted shrinking fact from Section 7.1;
7. reduce `hi_i` only when a durable terminal/interlock fact excludes later physical phases;
8. check prefix consistency and resource-claim consistency;
9. if concretization becomes empty, enter RECOVER/containment and authorize no new action.

No empty knowledge set is interpreted as universal safety.

### 8.3 Queries

`MAY_PHYS(K,r)` is computed by scanning the footprints of occurrences represented by each `K_i` plus unresolved transaction tags.

`MAY_CLAIM(K,r)` is computed from prepared/committed transaction records that have no accepted release certificate.

`MUST_AT(K,i,k,u)` holds only if every represented phase for agent `i` is the same endpoint occurrence `(k,u)`.

`MUST_CLEAR(K,r)` holds only through an accepted shrinking fact, never through absence of a report or elapsed wall time.

The abstraction is sound by construction but may be conservative. Candidate 69 does not claim globally complete correlation recovery. Transaction tags are retained specifically where joining them would make a coupled handoff unsound.

### 8.4 Soundness lemma

**Lemma 69-K.** If the concrete initial phase is in the concretization of `K`, every accepted update follows Section 8.2, and every shrinking fact satisfies Section 7.1, then the concrete phase remains in the concretization after any finite sequence of stale, missing, duplicate, reordered, conflicting, or false ordinary reports.

**Proof.** Duplicate and losing-epoch steps leave `K` unchanged. Missing and predecessor-absent messages cannot shrink it. Conflict joins add alternatives. A trusted shrinking fact removes only phases excluded by the declared sound certificate/interlock. Prefix and claim inconsistency transitions to containment rather than treating an empty concretization as safe. Induction over the delivered message sequence proves inclusion. QED.

## 9. Commit linearization and fenced substrate

### 9.1 Substrate assumption

Candidate 69 does not invent consensus. It assumes one durable single writer `owner(r)` per resource while an active transaction exists. Every physical admission point checks the resource epoch and rejects a losing epoch.

Owner failover during uncertainty is prohibited. Reconfiguration requires quiescence, durable transfer, and proof that old epochs can no longer be executed. If that proof is unavailable, the resource blocks. This sacrifices availability under partition but preserves the safety claim.

### 9.2 Transaction identity

`tid = (candidate_hash, coordinator_boot, monotone_local_seq, proposal_digest)`.

Every message also carries resource ID, owner epoch, phase, predecessor phase, payload digest, and idempotency key. The durable receiver table makes exact duplicate processing a no-op. An executor writes an intent record before actuation and a terminal/tombstone record before accepting a later conflicting transaction.

Exactly-once network delivery is not assumed. Exactly-once physical motion is not claimed merely from an idempotency key; it follows only if the executor's write-before-actuate and recovery interlock assumptions hold. Otherwise recovery contains the resource and does not replay.

### 9.3 Linearization event

The decision linearization point `LIN_COMMIT(tid)` is the atomic durable append of one final-batch decision record after every participating resource owner has issued a version-bound PREPARE token.

The record binds:

- candidate hash;
- proposal and preauthorization digests;
- knowledge-state digest;
- resource-version and owner-epoch vector;
- mandatory suppression seeds and reverse-closure witness;
- holding or containment certificates;
- final action-vector digest;
- participating resource set and prepare-token digests.

An executor may start only after validating the record and all current fences. A changed resource version or owner epoch before append aborts PREPARE. After append, participants retain claims until certified terminal release. A wall-clock timeout never releases a physical resource.

### 9.4 Partial delivery

Independent moves whose protected footprints are disjoint may start in any delivery order after `LIN_COMMIT`.

A coupled handoff may start only under a named linked-execution contract that proves every admitted partial start trace safe. If no such contract is present, the certifier suppresses the entire coupled component. Atomic commit alone is not a linked-execution proof.

## 10. Safe holding and total outcome classes

`SAFE_HOLD(i,k,u,ver)` requires all three predicates:

- `SH_STATIC`: the declared resource model permits indefinite stopping at `u`;
- `SH_DYNAMIC`: a current versioned holding right exists and no committed incoming claim can execute against it;
- `SH_BRAKE`: the executor certifies the agent remains before the point of no return for occurrence `k`.

It also requires `MUST_AT(K,i,k,u)`.

The refinement result for each agent is exactly one class:

- `UNCHANGED_MOVE`;
- `UNCHANGED_WAIT`;
- `MOVE_TO_WAIT` with `SAFE_HOLD`;
- `CONTINUE_EXISTING_TXN` for an already-started physical transition;
- `NO_NEW_AUTH_CONTAIN` when WAIT or a new MOVE cannot be certified.

Containment is not a new planner action. It preserves existing resource claims and delegates only braking/hold behavior already certified by the executor interface.

## 11. Proposal-preserving batch closure

### 11.1 Initial authorized set

Let `M` be indices whose preauthorized action `mu_i` is MOVE. Candidate 69 never adds an index to `M`.

For a tentative kept set `S` contained in `M`, `CERT(i,S,K)` checks:

- the exact origin occurrence is known or protected by an existing transaction;
- every vertex, directed-edge, opposite-edge, origin-release, and destination-acquire obligation is exclusive against `MAY_PHYS` and `MAY_CLAIM`;
- any same-batch vacate/acquire dependency is represented by an explicit edge in the linked component;
- the resource versions and fences are valid for `LIN_COMMIT`;
- if `i` is removed, its WAIT is safe or its outcome is containment rather than symbolic WAIT.

### 11.2 Mandatory seed set

`Seed(K,M)` contains every MOVE that fails `CERT` for reasons independent of another tentative same-batch release, every MOVE lacking required prepare/fence tokens, and every MOVE whose only fallback requires an unavailable safe hold.

An unsafe fallback is marked `CONTAIN`; it is not silently converted to WAIT.

### 11.3 Reverse dependency relation

For `i,j` in `M`, write `i -> j` when preserving `j` requires a resource that `i` releases only if `i` preserves and executes its MOVE. If `i` is suppressed, `j` must be reconsidered. The relation includes destination-to-origin following, coupled rotation, directed-edge release, opposite-edge exclusion, and dynamic holding claims.

### 11.4 Worklist algorithm

1. initialize suppressed set `X := Seed(K,M)`;
2. place every seed on a worklist;
3. remove one suppressed index `i`;
4. for every edge `i -> j`, recompute `CERT(j,M\X,K)` against the transformed batch;
5. if `j` fails, add it to `X` and the worklist;
6. recompute `SAFE_HOLD` for each induced WAIT against all final incoming claims;
7. if an induced WAIT is unsafe, mark its component `NO_NEW_AUTH_CONTAIN` and propagate all dependent releases;
8. stop when the worklist is empty;
9. independently certify the final vector `rho`, not the original `mu`.

### 11.5 Closure theorem

**Theorem 69-C.** For a finite batch and fixed knowledge/resource versions, the worklist terminates. Its suppressed set is the least set containing `Seed` and closed under every mandatory reverse dependency discovered by `CERT`. The resulting vector contains no alternative MOVE.

**Proof.** An index is inserted into `X` at most once and never removed. Since `M` is finite, the loop terminates. Every insertion is either mandatory by `Seed` or forced by an edge from an already suppressed index whose retained release is no longer available. Any closed suppression set containing `Seed` must therefore contain each index reached inductively by the worklist, proving leastness relative to the declared certificate/dependency relation. Output construction either copies `mu_i`, emits WAIT at the same certified occurrence, continues an already committed transaction, or emits no new authorization; none creates a MOVE. QED.

This theorem does not claim a globally maximum-cardinality moving set. It proves only the least mandatory suppression under the fixed proposal, abstraction, and certificate relation.

## 12. Following and rotation contract

Following or a rotation cycle may be retained only if one of these contracts holds:

- the baseline execution layer already provides a proved delay-robust linked handoff and Candidate 69 preserves the whole linked component;
- a common transaction plus executor interlock proves all physically possible partial starts safe;
- the declared pure-discrete environment provides an atomic joint transition and the experiment is explicitly limited to that semantics.

If none holds, every MOVE whose destination depends on same-batch vacating is placed in one coupled component. Any uncertified member suppresses the entire dependency-reachable component. This is conservative but does not falsely call a singleton destination empty.

Inactive identity is asserted only relative to the declared baseline execution semantics. Candidate 69 does not simultaneously assume independent no-start failure and unguarded atomic rotation.

## 13. Safety composition theorem

**Theorem 69-S.** Assume:

- Lemma 69-K's knowledge soundness;
- the conservative footprint map of Section 6.4;
- unique enforced resource epochs and retained transaction claims;
- `LIN_COMMIT` validation;
- final-batch closure and safe-holding checks;
- a linked-execution proof for every retained coupled component;
- containment rather than new authorization when these conditions fail.

Then every admissible execution trace of the committed final batch is free of incompatible vertex, directed-edge, opposite-edge, origin-release, and destination-acquire occupancy in the declared resource model.

**Proof.** Consider the first alleged incompatible physical occupancy. Both participants must have passed an enforcement point or one must be an unresolved prior occupant. A prior occupant/claim remains in `MAY_PHYS` or `MAY_CLAIM` by Lemma 69-K and retained-release rules, so `CERT` would reject a conflicting new claim. Two new independent moves cannot conflict because their final footprints were checked together and resource owners prepared exclusive current-epoch claims. A suppression-created conflict cannot be first because Theorem 69-C propagates every lost release and the final vector is recertified. A coupled component is safe by its explicit linked-execution premise. A stale epoch is rejected at enforcement. These cases exhaust admitted starts, contradicting the first conflict. QED.

Scope: this proves safety only for the declared resource abstraction and trusted enforcement assumptions. It does not prove geometric or hardware collision avoidance outside that abstraction.

## 14. Message and recovery lemmas

### 14.1 Idempotence

Processing an identical `(key,digest)` twice leaves knowledge and transaction state unchanged after the first durable application.

### 14.2 Reorder convergence

Messages from one sender apply only after causal predecessors. Independent ordinary reports combine by conservative join. Therefore any finite delivery permutation with the same accepted shrinking certificates converges to the same knowledge over represented occurrences.

### 14.3 Lost ACK

A missing ACK retains the committed claim. Recovery queries the durable decision/tombstone record; it never infers release from timeout. Throughput may stop, but no conflicting claim is granted.

### 14.4 Clock skew

No safety transition depends on comparing unsynchronized wall clocks. Time can trigger a recovery request but cannot expire physical occupancy, a fence, or a committed claim.

### 14.5 Partition and component merge

No owner failover occurs while old execution authority might remain enforceable. Components without all required current owners cannot commit. On merge, stale epochs are rejected. If quiescent transfer cannot be proved, the resource remains blocked.

### 14.6 Mid-edge failure

The edge, opposite-edge mutex, destination claim, and every not-yet-cleared origin footprint remain protected until a trusted terminal reconciliation. Expected duration, negative sensing, missing bookkeeping, or stale completion cannot release them.

## 15. Inactive byte-identity contract

Candidate 69 defines the compared byte domains rather than claiming identity of wall-clock time:

- canonical planner-input bytes;
- task-disclosure bytes and order;
- PIE proposal bytes;
- preauthorization action bytes;
- final authorized action bytes;
- planner random-source state before and after each call;
- logical environment-state bytes at each boundary.

The inactive fast path is taken when the external activation predicate is false and no Candidate 69 state is allowed to feed the planner. It returns the preauthorization byte buffer without decoding/re-encoding, consumes no random draw, changes no ordering, and writes audit metadata only to an out-of-band stream after the logical decision.

**Theorem 69-B.** Under equal initial byte states, equal exogenous logical trace, and the same deterministic logical scheduler, inactive Candidate 69 produces byte-identical compared domains to the frozen baseline.

**Proof.** The branch is taken before any candidate monitor update visible to the planner. It returns the same immutable action bytes and performs no write to any compared state or random source. Induction over logical boundaries preserves equality. QED.

Wall-clock runtime cannot be bitwise identical merely because an optional wrapper exists. Runtime overhead is measured separately in the natural-runtime track and is not hidden inside Theorem 69-B.

Mechanical contract: hash every compared canonical stream for paired baseline/inactive replays; any mismatch is an automatic gate failure, not a statistical metric.

## 16. Triggered refinement certificate

Every non-inactive decision emits a canonical certificate containing:

- candidate and source-artifact hashes;
- proposal and preauthorization digests;
- activation class;
- evidence keys, trust classes, and knowledge digest;
- resource versions, owners, epochs, and enforcement points;
- mandatory seed witnesses;
- reverse-dependency edges and closure order;
- safe-hold certificates or containment reasons;
- final action and transaction digests;
- decision class for every agent;
- `LIN_COMMIT` record digest or precommit abort reason.

An independent verifier accepts only if it can reconstruct the same seed set, closure, outcome classes, proposal-preservation relation, holding decisions, and final resource-exclusion certificate. Digest equality alone is insufficient.

## 17. Locality and effect mechanism

Let `Affected` be the reverse-reachable set from mandatory seeds in the dependency graph plus any resource component entering containment.

**Lemma 69-L.** Every index outside `Affected` that was preauthorized MOVE remains byte-identical in the final vector, provided its resource version remains unchanged through `LIN_COMMIT`.

**Proof.** Such an index is neither a seed nor reachable from a lost release and therefore is never inserted into the monotone suppressed set. Final recertification sees the same independent claims and copies its original bytes. QED.

This gives the empirical effect mechanism: compared with global stop, faults confined to a small dependency component need not suppress unrelated PIE MOVEs. It is a falsifiable hypothesis that this retained locality improves completed-task throughput under matched safety obligations; no improvement is claimed before experiment.

## 18. Targeted evidence repair

When `CERT` fails because a represented alternative lacks a shrinking fact, the verifier returns a witness set of missing resource/phase facts. The repair policy may request current state or clearance only from the owners/sources appearing in those witnesses.

Rules:

- a query never authorizes a MOVE;
- no reply leaves the conservative decision unchanged;
- an ordinary contradictory reply widens knowledge;
- only an accepted shrinking fact can remove a witness;
- resource/query allocation parameters remain protected and unassigned;
- exact optimal query selection, submodularity, approximation, and hardness are not claimed in Candidate 69.

Candidate comparison includes passive knowledge certification versus witness-directed repair. The intended effect is fewer unnecessary WAIT decisions at equal safety, but direction and magnitude remain empirical questions.

## 19. Computability and complexity

Let encoded input size include active event occurrences, delivered messages, resources touched by the proposal, unresolved transaction tags, and dependency edges.

- message ingestion is linear in delivered encoded messages plus predecessor activations;
- `MAY_PHYS` and `MAY_CLAIM` construction is linear in represented occurrence footprints and active claims;
- consistency/nonemptiness is checked during prefix and transaction-tag propagation;
- seed generation is linear in proposal-resource incidences plus conflict lookups;
- reverse closure is linear in proposal indices plus dependency edges after indexes are built;
- certificate verification has the same asymptotic bound as recomputing the affected subproblem;
- storage is linear in the active occurrence window, durable transaction/tombstone entries, and touched-resource index.

Candidate 69 claims polynomial sound certification for this explicit abstraction. It does not claim exact solution of the general consistent-cut problem, exact maximum concurrency, or completeness outside the declared representation.

## 20. Conditional liveness and explicit degradation

### 20.1 Safety without progress

Under unbounded communication delay, permanent partition, unavailable owner, missing sound clearance, unresolved mid-edge failure, or unsafe holding, the protocol may block forever. The safety theorem remains conditional on enforcement; no liveness claim applies.

### 20.2 Progress assumptions

Conditional progress requires:

- authority and fence enforcement eventually stabilize;
- every started physical action eventually reaches a sound terminal/containment certificate;
- required messages and selected evidence requests are eventually delivered;
- transaction resource acquisition follows one global deterministic order, preventing prepare deadlock;
- persistent feasibility holds at service times, not merely intermittently;
- a continuously enabled oldest transaction is eventually served;
- the baseline execution policy itself offers progress from the resulting state.

### 20.3 Progress result

**Theorem 69-P.** Under all Section 20.2 assumptions, a continuously retried transaction that remains feasible is eventually committed or becomes terminally infeasible; once all uncertainty witnesses for an unaffected baseline MOVE receive sound terminal evidence, Candidate 69 ceases suppressing that MOVE.

**Proof sketch.** Global resource order prevents cyclic prepare wait. Stable epochs prevent infinite reconfiguration invalidation. Eventual delivery resolves every finite predecessor gap, and terminal-action evidence removes persistent physical ambiguity. Fair service prevents an oldest continuously enabled request from being bypassed forever. The closure then loses the corresponding mandatory seed; if no remaining dependency reaches it, Lemma 69-L preserves the MOVE. Terminal infeasibility is a distinct final outcome, not an endless stream of fresh diagnostic reasons. QED.

No bound on slowdown, waiting time, or throughput is asserted.

## 21. Complete transaction state machine

| State | Entry evidence | Permitted next states | Safety action |
|---|---|---|---|
| OBSERVE | versioned messages and durable prior state | PROPOSE, RECOVER | widen on conflict; never release on absence |
| PROPOSE | canonical PIE proposal | PREPARE, ABORT | compute knowledge and final-batch candidate |
| PREPARE | exact proposal/knowledge digest | COMMIT, ABORT, RECOVER | acquire ordered version-bound claims |
| COMMIT | all prepare tokens valid | EXECUTE, RECOVER | append `LIN_COMMIT`; no postcommit abort |
| EXECUTE | validated commit and fences | COMPLETE, RECOVER | protect phase footprints |
| COMPLETE | trusted terminal/interlock evidence | ACK, RECOVER | install monotone release certificate |
| ACK | durable terminal receipt | terminal | release only certified claims |
| ABORT | pre-start transaction only | terminal, PROPOSE | release prepares; no physical rollback claim |
| RECOVER | ambiguity, crash, loss, inconsistency | EXECUTE, COMPLETE, ACK, ABORT, contained terminal | query durable decision/physical interlock; fail closed |

Messages are phase-idempotent. A message whose predecessor phase is absent cannot advance the state. A postcommit transaction never transitions to ABORT merely because an ACK is missing.

## 22. Counterexample and degradation suite

| ID | Minimal witness | Unsafe shortcut | Required Candidate 69 outcome |
|---|---|---|---|
| C69-01 | stale origin report | MOVE from wrong occurrence | reject/shrink only with trusted fact |
| C69-02 | false COMPLETE while occupant remains | release destination | keep claim; WAIT/contain |
| C69-03 | duplicate terminal after new boot | replay release or motion | idempotent tombstone/fence |
| C69-04 | reordered START/COMPLETE | impossible prefix | hold later event; no shrink |
| C69-05 | mutually conflicting state reports | choose optimistic point | conservative join/recover |
| C69-06 | one MOVE suppressed, follower enters origin | per-agent filtering | reverse closure suppresses follower |
| C69-07 | rotation member does not start | unlinked cycle execution | suppress component or require linked proof |
| C69-08 | destination physically free but old COMMIT exists | inspect occupancy only | `MAY_CLAIM` blocks new grant |
| C69-09 | decision checked before resource version changes | TOCTOU commit | abort PREPARE/version mismatch |
| C69-10 | old and new authorities after partition | epoch field without enforcement | stale epoch rejected or full blocking |
| C69-11 | physical completion, lost ACK, restart | replay COMMIT | durable intent/tombstone or containment |
| C69-12 | agent may be at origin or already mid-edge | emit symbolic WAIT | no new action; contain transaction |
| C69-13 | vertex statically stoppable but incoming grant committed | static hold only | SH_DYNAMIC fails; propagate/contain |
| C69-14 | braking point already passed | late WAIT | CONTINUE_EXISTING_TXN/contain |
| C69-15 | edge failure before clearance | timeout release | retain swept-volume claims |
| C69-16 | clock skew expires lease early | wall-time safety | clocks trigger recovery only |
| C69-17 | unbounded communication delay | promise progress | safe blocking; liveness suspended |
| C69-18 | corridor/tree following chain | one-pass suppression | worklist reaches full required chain |
| C69-19 | intersection partial delivery | atomic grant assumed physical | independent footprints or linked proof |
| C69-20 | repeated fresh rejection | diagnostic response called progress | terminal infeasible or fair eventual service |
| C69-21 | component merge with old epoch command | accept both histories | enforcement rejects losing epoch |
| C69-22 | empty concretization from inconsistent evidence | vacuous universal safety | RECOVER/contain; no authorization |

Each future mechanical witness must freeze initial state, exact event order, expected decision class, invariant, and theorem mapping before main experiments.

## 23. PIE-D official R0 read-only audit

Official paper:

- DOI: `10.1609/aaai.v39i22.34506`
- Official PDF: `https://ojs.aaai.org/index.php/AAAI/article/download/34506/36661`
- The paper links the implementation and benchmarks to `https://github.com/YueZhang-studyuse/LMAPF-delay`.

Frozen repository object:

- Commit: `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`
- Commit URL: `https://github.com/YueZhang-studyuse/LMAPF-delay/commit/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`
- Repository version file: `1.1.0`
- License: MIT
- License blob: `1f4b6eadac278447824a47d409bb4de04ea7f3ee`
- Build system: CMake; C++14; Boost program_options/system/filesystem/log/log_setup; target `lifelong`.
- Official run shape: `lifelong` consumes one declared input JSON and an output destination as documented by the repository.

Read-only extension seam:

- `inc/CompetitionSystem.h`: `BaseSystem::plan`, `execution_with_delay`, `execution_simulate`, `curr_commits`, `curr_states`, and `env`.
- `src/CompetitionSystem.cpp`: `sync_shared_env` predicts the next state from committed actions; planner invocation and `planner_commit` follow; `execution_simulate` instantiates the delay policy; unexecuted paths are updated afterward.
- `src/DelaySimulation.cpp`: `SimulateMCP::simulate`, `moveAgent`, and `build`.
- `inc/MAPFPlanner.h` and `src/MAPFPlanner.cpp`: planner, committed path, future path, and commit interfaces.
- `src/driver.cpp`: command-line and system wiring.

Real extension rule: Candidate 69 belongs between synchronized evidence abstraction and action commitment. It does not modify `MAPFPlanner` path selection.

Minimal original-method audit plan, not executed:

1. check out the fixed commit;
2. build only by the official CMake entry;
3. run one repository-supplied input without Candidate 69;
4. retain exact command, environment, input hash, output, and exit status;
5. compare to the repository's own validity contract before any extension is enabled.

No checkout, build, or run is authorized until all gates and reviews close.

## 24. Published external baseline audit

Primary paper:

- Title: `Time-Independent Planning for Multiple Moving Agents`.
- Publication: AAAI 2021.
- Preprint: `https://arxiv.org/abs/2005.13187`.

Official artifact:

- Repository: `https://github.com/Kei18/time-independent-planning`.
- Publication experiment tag: `v1.0`.
- Immutable commit: `755a7ce740d49543b1165403371752c08e342ca4`.
- Commit URL: `https://github.com/Kei18/time-independent-planning/commit/755a7ce740d49543b1165403371752c08e342ca4`.
- License: MIT.
- License blob: `cdc9e1cb51b24b72f079baf9af9e31f53c967fbd`.
- Build: CMake, C++17, `app` and `lib-time-ind` targets.
- Official sample: `instances/sample.txt`, blob `842958a104943a6d7cad2474547ee5665c427b37`.
- Implemented comparators include FSP, MCP, Causal-PIBT, and Causal-PIBT-MAPF.
- MCP interface blobs: header `3afcec...`; source `51459f...`.
- MAPF-DP interface blobs: header `1323af...`; source `7537e7...`.

Minimal reproduction plan, not executed:

1. check out the immutable publication commit;
2. build with the official CMake instructions;
3. run the official sample through the documented MCP solver path;
4. retain environment, command, input/output hashes, exit status, and validator result;
5. adapt only through a separately specified information/action interface; never silently give the comparator less evidence or charge it more runtime.

## 25. Public maps, tasks, and disturbance traces

The fixed PIE-D commit contains `lifelong_benchmark` subtrees with maps, agent starts, task streams, and original delay-scenario JSON files. Representative source classes include city and warehouse layouts; exact files will be selected by a deterministic manifest rule without assigning any protected parameter.

The preregistration manifest must bind:

- repository commit and tree/blob hashes;
- map blob;
- agent/start blob;
- task-stream blob;
- original delay-scenario blob where used;
- generated feedback-fault trace schema and generator version;
- planner and disturbance random-state streams kept separate;
- complete replay ledger.

No new trace realization is generated in Candidate 69. Trace generation before authorization would be scientific payload.

## 26. Comparator contract

Executable comparators planned after authorization:

- frozen PIE nominal path;
- frozen PIE-D R0;
- official external FSP/MCP artifact;
- global fail-closed stop as a safety/conservatism control;
- passive PIE-DTRS-KC without targeted evidence repair;
- full PIE-DTRS-KC.

POD, Liu 2026, Hönig ADG, and local shields are claim-level comparators unless a lawful official executable artifact and faithful adapter are independently frozen. Reimplementing them from prose and calling the result official is prohibited.

Information parity:

- all methods receive the same admissible physical truth channel or none;
- all methods receive the same delayed/faulted report trace;
- any extra evidence query resource is made available under the same accounting rule;
- the same nominal PIE proposal and task stream are used when the method's interface permits;
- comparator domain mismatches are reported rather than forced into a misleading table.

## 27. Pure-simulation preregistration

### 27.1 Independent sample unit

One independent unit is one complete tuple of map, task stream, initial state, nominal planner stream, physical delay trace, feedback-fault trace, and method. Agents and ticks within that run are repeated observations, not independent samples.

### 27.2 Failure denominator

Every launched unit remains in the denominator. Build failure, crash, timeout, invalid output, collision/resource violation, deadlock, recovery nontermination, and censored completion are separately labeled but never silently deleted.

### 27.3 Stopping and censoring

- freeze the complete run roster before observing comparative outcomes;
- no effect-dependent early stopping;
- use a method-independent symbolic stopping contract;
- preserve all partial logs on censoring;
- retry only transport/infrastructure failures under a predeclared rule, never scientific failures;
- report both launched and validly completed denominators.

### 27.4 Independent safety oracle

The collision/resource oracle consumes simulator ground truth, not Candidate 69's knowledge state. It checks vertex, directed-edge, opposite-edge, origin-release, destination-acquire, and swept-volume invariants independently. Candidate certificates are checked by a second deterministic verifier.

### 27.5 Two compute tracks

`Strict same-compute`:

- one common symbolic compute allowance;
- planner, knowledge updates, queries, transaction work, recovery, and certificate generation are all charged;
- unused compute is not converted into extra information;
- baseline and candidate receive equal evidence-query accounting;
- operation counts and wall time are both retained.

`Natural-runtime`:

- each frozen method uses its documented natural execution path;
- total end-to-end wall time includes adapters, monitoring, transactions, and recovery;
- throughput and tail decision latency are reported with runtime, not instead of runtime.

The protected compute symbols remain unassigned.

### 27.6 Primary outcomes and falsification

Safety outcomes:

- any incompatible physical-resource overlap;
- unsafe admission count per admitted MOVE;
- collision/deadlock/containment terminal class;
- certificate-verifier disagreement.

Utility outcomes:

- completed tasks per declared run exposure;
- retained baseline MOVE fraction;
- induced WAIT and containment exposure;
- affected-component size;
- recovery duration and stale-claim duration;
- total and per-decision compute.

Falsifying observations include:

- any inactive canonical-byte mismatch;
- any admitted alternative MOVE;
- any safety-oracle violation under theorem assumptions;
- any certificate accepted when independent recomputation rejects;
- any action outside `Affected` changed without a resource-version change;
- any result that reverses the preregistered locality or evidence-repair hypothesis.

No effect size or direction is reported as a result in this artifact.

## 28. Ablation matrix

| Ablation | Question | Required interpretation |
|---|---|---|
| point estimate instead of `K` | Is set-valued knowledge necessary? | expose optimistic-release failures, not hide them |
| trust single COMPLETE | Is the shrinking boundary necessary? | test indistinguishable false completion |
| one-pass filtering | Is reverse closure necessary? | test following/cascade witness |
| remove final recertification | Can closure introduce a new hazard? | any violation rejects shortcut |
| occupancy only, no outstanding claims | Are future entitlements relevant? | test undelivered COMMIT |
| no fence enforcement | Are epochs merely metadata? | test split histories |
| unsafe WAIT allowed | Does symbolic WAIT equal physical hold? | test point-of-no-return/dynamic hold |
| global stop | Does locality retain useful concurrency? | safety-matched conservatism control |
| passive certification | Does targeted evidence repair help? | equal query accounting |
| perfect-knowledge oracle | What is the remaining knowledge gap? | upper bound, not deployable comparator |

An ablation that violates a proved safety premise is run only as a labeled counterexample/negative control, never presented as a safe deployable method.

## 29. Why physical experiments are not required for the core paper

The core claims concern a discrete action interface, message/event uncertainty, resource-state invariants, and proposal-preserving certification. They can be established by proofs, symbolic counterexamples, small-state exhaustive checking after authorization, and replayable pure simulation.

Physical experiments become required only if the paper claims that a real sensor supplies sound clearance, a real brake satisfies `SH_BRAKE`, a physical fence rejects stale epochs, the swept-volume abstraction matches a robot, or a warehouse deployment is safe. Candidate 69 makes none of those claims.

The manuscript must state that trusted clearance, braking reachability, and enforcement are assumptions/interfaces. Simulation can test behavior when those predicates are true or false; it cannot validate the hardware implementing them.

## 30. Qualification card

| Gate | Evidence | Candidate 69 status |
|---|---|---|
| Plain-language problem contract | Section 2 and inherited reviewed contract | `PASS-INHERITED` |
| Published anchors | primary-source chart and fixed DOIs | `PASS-INHERITED` |
| PIE official R0 | URL, immutable commit/version, license, build entry, minimal audit plan, real seam | `EVIDENCE-COMPLETE / REVIEW-PENDING` |
| External published baseline | official tag/commit, license, sample, minimal plan | `EVIDENCE-COMPLETE / REVIEW-PENDING` |
| Public data/scenarios | fixed benchmark tree classes and manifest contract | `EVIDENCE-COMPLETE / REVIEW-PENDING` |
| Pure-simulation evidence chain | oracle, units, denominator, stopping, replay, compute tracks, falsifiers | `PROTOCOL-COMPLETE / REVIEW-PENDING` |

No `REVIEW-PENDING` gate is counted as PASS. Effective gate state remains two PASS and four open until Candidate 69 receives research-mentor, Nature reviewer, no-skill logic, and root acceptance without unresolved bearing objection.

## 31. Protected-symbol lock

- `H`: unassigned.
- `T_delay`: unassigned.
- `B_CAL`: unassigned.
- `B_max`: unassigned.
- `B*`: unassigned.
- `P_active`: unassigned.
- density `N`: unassigned.

Candidate 69 assigns no value, interval, range, default, prior, empirical estimate, or tuning direction to any protected symbol. Complexity notation uses set cardinalities and encoded input size, not density `N`.

## 32. Review and authorization sequence

Candidate 69 must receive, in order:

1. a complete research-mentor skill review against its exact frozen hash;
2. a complete Nature reviewer skill review against the same hash, independent of the mentor report;
3. a complete no-skill logic review against the same hash, independent of both prior reports;
4. root synthesis and requirement-by-requirement acceptance.

Any bearing objection requires new-number, new-byte succession. CLOSED review transport never means candidate approval. A valid Claude Opus consultation remains nonballot.

## 33. Final state

- Candidate 69 scientific route: `OPEN`.
- Novelty: `OPEN`.
- Formal review: `NOT STARTED`.
- Implementation: prohibited.
- Build and original-method test execution: prohibited pending gates.
- Simulator and trace generation: prohibited pending gates.
- Main experiment and scientific payload: prohibited.
- Global release update: prohibited.

`HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`
