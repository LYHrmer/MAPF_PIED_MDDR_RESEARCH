# 68R4 Candidate 68 Three-Review Root Synthesis and Successor Ruling

Date: 2026-09-05 (Asia/Shanghai)

Status: `ROOT-ACCEPTED REVIEW SYNTHESIS / CANDIDATE 68 REJECTED / NEW BYTES REQUIRED`

Control state: `HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`

## 1. Registered object

The reviewed object is exactly:

`68_PIE_COMMIT_BOUNDARY_STATE_ENVELOPE_UNDER_PROCESSING_AND_OBSERVATION_UNCERTAINTY_JOURNAL_ROUTE_CANDIDATE_20260904.md`

- SHA-256: `105ae41743f13a0add69751e0be322fbdd2ee99a81adfbdd9707ae7e3e8e0c5c`
- Bytes: `37575`
- Lines: `793`
- Candidate state: `OPEN / NONBALLOT / HOLD`
- Candidate 68 was not edited, renamed, sidecar-approved, or cosmetically rehashed.

## 2. Formal review chain

### 2.1 Research-mentor review

File: `68R1_PIE_COMMIT_BOUNDARY_STATE_ENVELOPE_RESEARCH_MENTOR_REVIEW_20260904.md`

- SHA-256: `843f4c2cac7cb7e9602fe7589a65b73503ad7da6b0938ce1fb21b714aba70f7b`
- Bytes: `35528`
- Lines: `348`
- Candidate identity matched at review start and end.
- Complete-read proof was present.
- Review transport: `CLOSED = REVIEW COMPLETED ONLY`.
- Disposition: Candidate 68 rejected; route conditional; bearing objections present.

### 2.2 Nature reviewer review

File: `68R2_PIE_COMMIT_BOUNDARY_STATE_ENVELOPE_NATURE_REVIEWER_REPORT_20260905.md`

- SHA-256: `0c01d03980202e7df6b689e671cf538053716852b25a8563b498610161fa88ff`
- Bytes: `43745`
- Lines: `439`
- Candidate identity matched at registration, review start, and review end.
- One complete candidate read was proved.
- Three reviewer reports and a cross-review synthesis were present.
- Review transport: `CLOSED = REVIEW COMPLETED ONLY`.
- Disposition: `BEARING OBJECTIONS / REVISION REQUIRED`.
- Stable register: thirteen bearing objections and four non-bearing objections.

### 2.3 No-skill independent logic review

File: `68R3_PIE_COMMIT_BOUNDARY_STATE_ENVELOPE_NO_SKILL_INDEPENDENT_LOGIC_REVIEW_20260905.md`

- SHA-256: `1c47cf580fcb2674e5d0ec6458a1d07da25361590145a8641602fc8fbf4aba78`
- Bytes: `25408`
- Lines: `282`
- Candidate identity matched at review start and end.
- Exactly one complete candidate body read was proved.
- The reviewer declared and preserved `NO-SKILL` independence.
- Review transport: `CLOSED = REVIEW COMPLETED ONLY`.
- Stable register: twenty bearing objections and three non-bearing objections.
- Disposition: `HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`.

## 3. Invalid transports and nonballot advice

### 3.1 Nature transport failures

- Laplace handle `01a06ba5-5861-79a0-9e7d-cb4eb3abf591` later returned `not_found`; no target report existed. It is invalid and contributes no ballot.
- Kepler handle `01a06ccb-9bb4-7ff0-8cff-05ab9da6eb67` later returned `not_found`; no target report existed. It is invalid and contributes no ballot.
- Gauss handle `01a06fc8-ad4c-7fd0-b220-73f45f939224` produced the valid 68R2 report. Only this Nature transport counts.

### 3.2 Claude Opus

- Earlier failed or empty attempts remain invalid under the 68C0 ledger and later observed `FailedToOpenSocket`/empty-output attempts.
- Session `83871` ended with exit status zero and a complete nonempty response.
- The valid constructive receipt is `68C1_PIE_COMMIT_BOUNDARY_CLAUDE_OPUS_CONSTRUCTIVE_COMBINATION_ADVICE_RECEIPT_20260905.md`.
- Receipt SHA-256: `8c0e6744072f4606e7278a6d9732cf39d148bf26dc163b9b770db015b4d43dc5`.
- Receipt bytes: `27195`.
- Receipt lines: `277`.
- The receipt is `CONSTRUCTIVE / NONBALLOT / UNADJUDICATED`; it cannot offset a formal objection.

## 4. Root synthesis of bearing objections

### 4.1 Decision-time semantics are missing

All three formal routes converge on a time-of-check/time-of-use defect. Candidate 68 does not bind the evidence cut, proposal digest, resource versions, authority epochs, prepare grants, commit decision, and physical departure to one linearization event. A safe successor must name that event and prove that no admitted intervening transition invalidates the authorization.

### 4.2 The compact envelope is denotational, not yet computational

`MAY_OCCUPY` and `MUST_OCCUPY` are defined through quantification over globally consistent cuts. Candidate 68 gives no finite input encoding, incremental update algorithm, nonemptiness test, resource-separable recognition procedure, query complexity, certificate-checking complexity, or hardness boundary. Compact storage is not a computational result if constructing the projection requires the hidden global oracle.

### 4.3 MOVE-to-WAIT is a batch transformation

Suppressing one departure retains its origin and can invalidate an incoming MOVE. Suppression may propagate through a following chain or a rotation component. Candidate 68 certifies agents individually and never computes or certifies the final transformed vector. A successor needs a monotone reverse-dependency closure, a worklist algorithm, termination, final-batch soundness, and a defined outcome when induced WAIT is not physically safe.

### 4.4 Following and rotations cannot be handled by a literal destination-MAY test

A literal rule that rejects every destination with a possible current occupant rejects legal singleton following and rotation batches, contradicting unqualified inactive identity. Conversely, accepting those batches under independent no-start outcomes can collide. The successor must distinguish an independent move from a coupled handoff and either require a proved linked-execution contract or suppress the entire affected component.

### 4.5 WAIT is not automatically safe

WAIT requires the same occurrence to be the physical endpoint in every admissible state, a static holdable vertex, a current dynamic holding right with no incoming committed claim, and braking reachability before the point of no return. If any condition is absent, the system may issue no new discrete command and must retain/contain the existing physical transaction. “All WAIT” is therefore not an unconditional safe base case.

### 4.6 Resource concepts are overloaded

Candidate 68 does not type-separate physical occupant, swept-volume occupancy, reservation holder, grant authority, fence-enforcement point, transaction phase, holding right, and release certificate. It also does not bind origin release, directed edge, opposite edge, and destination acquire to exact physical phases.

### 4.7 Generic fencing and two-phase vocabulary are insufficient

Epoch fields do not select a unique authority under partition. Message idempotence does not imply exactly-once actuation after restart. Atomic grant decisions do not imply atomic physical execution. The route must either assume a named linearizable substrate with an enforcement point or accept blocking and quiescent reconfiguration. It must not claim consensus, availability, or exactly-once motion without the corresponding mechanism.

### 4.8 Evidence authenticity is not physical truth

An authenticated false completion can still release an occupied resource. Ordinary completion/current-state messages may widen knowledge but cannot by themselves justify irreversible release if their payload may be wrong. A trusted monotone clearance certificate or physical interlock is required for nontrivial progress. If every release source can be arbitrarily false and there is no interlock, contested safe MOVE is information-theoretically impossible.

### 4.9 Identity and accountability are not yet mechanical

Equal action labels are weaker than bitwise noninterference. The exact byte domains, random-state coupling, task-disclosure stream, ordering, logical scheduler, proposal bytes, final action bytes, and audit side channel must be declared. A triggered certificate must bind evidence, versions, proposal, closure, holding proof, decision class, and transaction lineage to the final output.

### 4.10 Liveness is vacuous under repeated rejection

“Commit or receive a newer reason” permits infinite non-progress. Safety can hold under arbitrary partition and unbounded delay, but progress cannot. A valid theorem needs eventual evidence soundness, stable authority, terminal physical outcomes, deadlock prevention, persistent feasibility, bounded contender assumptions where used, and an explicit fairness relation. Outside those assumptions the declared result is safe blocking, not progress.

### 4.11 Evaluation protocol remains non-operational

Candidate 68 names same-compute and natural-runtime regimes but does not freeze information parity, complete compute accounting, external adapters, independent collision oracle, public trace provenance, environment capture, deterministic replay, stopping/censoring, or the launched-unit failure denominator. Pure simulation can establish only modeled algorithmic claims; it cannot validate real sensors, braking, interlocks, or warehouse deployment.

## 5. Root literature ruling

### 5.1 Claims permanently removed from novelty

- ADG/event dependency representation is not new.
- Deterministic commit cuts and planning/execution overlap are not new; Hönig et al. 2019 already provide them under timely completion feedback.
- Coordinating MOVE/WAIT on fixed paths under timing uncertainty is not new; Liu et al. 2024 and its 2026 journal extension cover known evolving locations, a maximal moving set, and hard feasibility.
- Typed discrepancy over occupancy, reservation ownership, queue, and progress plus age routing and recovery is not new; POD 2026 directly occupies this space.
- Belief-style safe action filtering under partial observation is not new; Yang and Yoshida 2026 compile belief-state local shields.
- Generic fencing, transactions, CEGAR, abstract interpretation, active querying, and runtime shielding are not novelty claims.

### 5.2 Candidate novelty kernel allowed for a successor

The only defensible kernel currently left open is the conjunction below, not any component alone:

1. one externally generated PIE/PIE-D proposal batch;
2. a commit-time knowledge certificate under unreliable completion/current-state feedback;
3. no alternative MOVE, only exact proposal preservation or WAIT/containment;
4. a least mandatory reverse WAIT closure over the final batch;
5. a mechanically checkable inactive byte-identity contract;
6. a composition theorem with an explicitly assumed fenced resource substrate;
7. targeted evidence repair used only to shrink uncertainty and recover retained concurrency.

This conjunction remains a hypothesis until primary-source overlap, definitions, algorithms, proofs, and reviews close. Similar terminology is not evidence of novelty.

## 6. Root adjudication of Opus advice

### Accepted as constructive direction

- proposal-preserving keep-or-WAIT positioning;
- delay/channel-fault/unsafe-admission separation;
- progress-index abstraction as a computable candidate;
- uncorroborated false completion as an impossibility witness;
- reverse WAIT closure;
- fencing as substrate rather than contribution;
- locality/noninterference and targeted evidence acquisition as effect mechanisms;
- same-compute/natural-runtime dual tracks and complete failure denominators;
- pure simulation for abstract algorithmic claims only.

### Rejected unless reformulated and proved

- blanket prohibition of same-tick vacating, because it can destroy legal singleton following/rotation and inactive identity;
- unconditional “all WAIT is safe,” because holding and point-of-no-return conditions may fail;
- claims of exact interval abstraction under revisiting routes without a proof;
- claims of confluence, optimality, hardness, submodularity, or bounded liveness before formal derivation;
- any statement that Hönig, Liu, POD, or local shielding lacks a feature not established from primary text.

## 7. Required successor structure

The successor must be new-number, new-byte Candidate 69 and must:

- replace event-ideal quantifier oracles with an explicit finite progress abstraction and algorithms;
- define a commit linearization record and version/fence validation;
- type every physical and protocol resource state;
- compute and verify final-batch reverse suppression closure;
- support coupled handoff only under an explicit contract and otherwise suppress it;
- make unsafe WAIT lead to no-new-authorization plus containment;
- give safety and impossibility proofs under named trust assumptions;
- give honest conditional liveness and safe-blocking results;
- include claim-level literature differences;
- freeze official R0, external baseline, scenario source, and preregistration contracts;
- remain non-implementing and non-experimental pending its own three formal reviews and root acceptance.

## 8. Final ruling

- Candidate 68: `REJECTED / BEARING OBJECTIONS / REVISION REQUIRED`.
- Candidate 68 review chain: `CLOSED = ALL THREE REVIEWS RECEIVED`, not candidate approval.
- Sidecar approval: prohibited.
- Modification of Candidate 68: prohibited.
- Successor authorization: only a new Candidate 69 with new bytes and a new hash.
- Current qualification: two inherited gates are PASS; four gates remain not formally PASS.
- Current activity state: `HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`.

