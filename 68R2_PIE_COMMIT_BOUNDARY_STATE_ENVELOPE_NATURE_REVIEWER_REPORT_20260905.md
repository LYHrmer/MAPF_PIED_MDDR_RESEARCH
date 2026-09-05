# 68R2 PIE Commit-Boundary State Envelope: Nature Reviewer Report

## Review setup

### Start-of-report candidate identity registration

- Candidate: `/home/lyh/MAPF_PIED_MDDR_RESEARCH/68_PIE_COMMIT_BOUNDARY_STATE_ENVELOPE_UNDER_PROCESSING_AND_OBSERVATION_UNCERTAINTY_JOURNAL_ROUTE_CANDIDATE_20260904.md`
- Registered candidate SHA-256: `105ae41743f13a0add69751e0be322fbdd2ee99a81adfbdd9707ae7e3e8e0c5c`
- Registered candidate bytes: `37575`
- Registered candidate lines: `793`
- Registration hash: the registered candidate byte-stream SHA-256 above; no surrogate document was registered.
- Review-start identity check: `MATCH` on SHA-256, bytes, and lines before content access.
- Complete-read proof: after the start identity check, the candidate was read once as one complete stream, beginning with `# 68 PIE Commit-Boundary State Envelope under Processing and Observation Uncertainty` and ending with `HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`; no excerpt, range selection, or summary substituted for the candidate.
- Review-end identity check: `MATCH` on the same SHA-256, bytes, and lines after the complete read and before report creation.
- Independence boundary: this review used only the registered candidate and the local `nature-reviewer` source basis, workflow, axes, role-boundary, report-structure, and QA materials. It did not read any prior reviewer report, Candidate 68R1, old 35-38 material, Q-CAL/Q-CONFIRM outcome, or scientific payload.
- Review mode: `FORMAL / INDEPENDENT / BOUNDED / BALLOT` at referee level. `BALLOT` records a reviewer recommendation, not an editor's decision and not a settled judgment of Nature fit.
- Review transport state: `CLOSED`, meaning only that this nonempty review was completed against the registered bytes.
- Candidate artifact posture on entry: `JOURNAL-ROUTE CANDIDATE / FORMAL PRE-EXPERIMENT SPECIFICATION / NONBALLOT`.
- Candidate control state on entry: `HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`.

### Input scope

The input is a complete formal pre-experiment route candidate, not a completed research article. It defines a PIE-boundary uncertainty object, an event-envelope abstraction, an exact-PIE-or-WAIT refinement rule, a fenced resource transaction substrate, proof targets, counterexamples, fault cases, and future reproducibility gates.

### Assessment boundary

This review can assess internal novelty positioning, formal coherence, theorem readiness, computability claims, fault semantics, evaluation design, and Nature-style significance/readability as presented. It cannot establish external novelty, theorem truth, empirical effect, implementation feasibility, or baseline reproducibility because no primary prior-work packet, completed proofs, algorithms, code, experiment manifests, or results are present in the registered candidate. Those limits are findings, not invitations to infer missing evidence.

### Shared manuscript claim summary

The candidate proposes replacing PIE-D's single optimistic next-window boundary prediction with a sound set of physically possible commit-boundary cuts represented by an event DAG and compact resource projections. The wrapper would preserve each exact PIE action when universally safe and otherwise change only a PIE MOVE to certified WAIT or contain an already-started transaction. It claims a possible exact inactive reduction to PIE-D, accountability for every triggered refinement, safety under asynchronous observation and communication degradation, and conditional progress without full-horizon belief-space replanning.

### Visible evidence base

- A precise seam between concurrent planning and physical commitment is identified.
- Delay, processing latency, observation faults, and wrong-edge motion are explicitly separated.
- The candidate supplies formal objects, proposed theorem statements, a state machine, physical holding conditions, a route-killing overlap matrix, symbolic counterexamples, degradation cases, and preregistration requirements.
- The candidate repeatedly and correctly labels its theorems as proof targets and its novelty as unresolved.
- There are no completed proofs, complexity derivations, executable algorithms, empirical observations, or reproduced baselines in scope.

### Missing materials affecting confidence

- Primary-source, element-by-element overlap findings for the strongest adjacent work, especially Hönig 2019, Liu 2024/2026, and POD Robotics 2026.
- A formal event alphabet, cut semantics, update semantics, and a finite algorithm for constructing and maintaining the envelope.
- A definition and recognition procedure for the claimed resource-separable event-DAG class.
- Completed safety, identity, accountability, fault, and liveness proofs.
- A linearizable batch decision protocol or a proof that every permitted partial start is safe.
- Frozen baseline artifacts, information-parity rules, compute-accounting rules, public scenario/trace procedures, and a replayable pure-simulation specification.

## Reviewer 1

Emphasis: technical soundness and technical failings.

### Overall assessment

The candidate isolates a scientifically plausible systems problem and shows unusual discipline in separating logical MAPF actions from physical occupancy. However, the central safety argument is not yet closed. The current compact state is partly denotational rather than computational, the decision has no explicit linearization point, and the batch rule is not closed under changing one MOVE to WAIT. These are not presentation defects: each can invalidate T68-3, T68-4, T68-5, or T68-8.

### Who would be interested in the results, and why

Researchers in MAPF execution, asynchronous distributed coordination, multi-robot safety, and runtime assurance would care if the candidate proves that uncertainty local to a concurrent planner's commit boundary can be handled without replacing PIE or performing full belief-space search. The interest depends on a real reduction in online reasoning and on preserving useful concurrency, not merely on restating conservative reservation rules.

### Major strengths

- The proposal-source restriction is sharp: PIE remains the sole source of MOVE, and the wrapper cannot synthesize a detour.
- The use of occurrence indices avoids conflating repeated visits to the same vertex.
- The event-DAG construction recognizes that independent per-agent location sets lose decisive joint correlation.
- Positive physical occupancy outranks timeout, missing ACK, or negative reports, which is the correct safety direction under the stated fault model.
- The three-part safe-holding contract exposes why symbolic WAIT is not automatically a physically safe action.
- The candidate acknowledges impossibility when absence cannot be trusted and no physical interlock exists.

### Major concerns

- `MAY_OCCUPY` and `MUST_OCCUPY` are defined by quantification over all consistent cuts. Without an algorithm and complexity result, the proposed compact state can conceal the very joint-state reasoning it claims to avoid.
- The envelope is tied loosely to a "boundary," but OBSERVE, PREPARE, COMMIT, execution progress, evidence arrival, and reconfiguration occur over different physical intervals. No event is identified as the decision linearization point.
- A per-agent MOVE-to-WAIT substitution can make another preserved MOVE unsafe. The text does not define the required reverse dependency closure or a final fixed-point batch certificate.
- Atomic batch commitment is asserted while each MOVE has its own destination commit authority. No mechanism gives the distributed set of authorities one atomic outcome, and no theorem permits safe partial starts.
- Authority, reservation, physical occupancy, transaction ownership, and authorization are described but not represented as disjoint typed state with transition invariants.
- Fencing is asserted to prevent stale authority, but safe reconfiguration under partition requires an explicit uniqueness mechanism or an enforcement point that rejects losing epochs.

### Technical failings that need to be addressed before the case is established

The case is blocked by `B68R2-03` through `B68R2-11`. In particular, the authors must provide a computable envelope algorithm, an explicit decision linearization contract, a terminating MOVE-to-WAIT reverse closure, coherent batch-commit semantics, typed physical/protocol invariants, durable idempotence and split-brain assumptions, an inactive noninterference proof, a total triggered-refinement rule, and a non-vacuous liveness theorem. Failure witnesses `FW68R2-01` through `FW68R2-09` show concrete traces not discharged by the present text.

### Assessment against Nature-style criteria

- Originality: potentially original at the exact PIE commit-boundary seam, but not established from this packet.
- Scientific importance: a successful compression and safety theorem could matter, but the current document contains targets rather than results.
- Interdisciplinary readership: there is plausible reach into distributed systems and robotics safety, conditional on making the general principle explicit.
- Technical soundness: not yet established because the central online decision and fault invariants are incomplete.
- Readability for nonspecialists: the plain-language problem contract is strong; the transition from that contract to event ideals and fenced transactions is too compressed for a broad reader.

### Recommendation posture

Currently not established from the provided evidence. Substantive formal revision is required before implementation or experimentation, and the candidate's own successor rule applies because the objections are bearing.

## Reviewer 2

Emphasis: originality and scientific importance.

### Overall assessment

The strongest potentially publishable idea is not "transactions for robots" or "uncertainty causes waiting." It is the narrower claim that uncertainty created specifically at a PIE concurrent planning/commit seam admits a compact, sound, and useful boundary abstraction that preserves exact PIE behavior whenever the abstraction is inactive. That claim is intellectually coherent, but the candidate has not yet shown that it is new, nontrivial, or stronger than a careful composition of known execution dependencies, online MOVE/WAIT coordination, and protocol-discrepancy recovery.

### Who would be interested in the results, and why

MAPF and lifelong-MAPF researchers would care about preserving concurrent planning gains under uncertain observations. Distributed-systems readers may care about the relation between consistent cuts, fencing, idempotence, and physical resource ownership. Runtime-assurance readers may care about exact pass-through plus witnessed conservative intervention. This audience exists only if the paper extracts a transferable scientific principle beyond one PIE integration.

### Major strengths

- The candidate states route-killing overlap tests instead of assuming novelty from terminology.
- It distinguishes baseline no-start delay from uncertainty in what state is known at commitment.
- It makes inactive identity and triggered intervention falsifiable rather than relying on qualitative similarity.
- It identifies a meaningful exactness boundary: general sound conservatism versus completeness on a characterized event-DAG class.
- It does not claim empirical effects before evidence exists.

### Major concerns

- The candidate does not provide a primary-source claim chart against Hönig 2019's ADG/commit-cut/planning-execution overlap, Liu 2024/2026's known evolving-location coordination on original-path MOVE/WAIT with maximal moving sets and hard feasibility, or POD Robotics 2026's occupancy/reservation/queue/progress discrepancy, typed channels, age routing, and recovery.
- PIE and PIE-D are anchored, but the strongest exclusion claims against neighboring methods remain route-killing questions rather than answered comparisons.
- The compact projection theorem is the main scientific lever, yet its class, algorithm, completeness, and complexity are absent. If the projection only wraps a global cut-feasibility oracle, the claimed reduction is nominal.
- The transaction layer risks becoming the dominant contribution. If safety follows only from generic exclusive reservations and fencing, the PIE-boundary envelope may add little beyond a systems integration.
- No proof or result currently supports "outstanding scientific importance," immediate implications, or far-reaching implications. The status is necessarily a route hypothesis.

### Technical failings that need to be addressed before the case is established

`B68R2-01`, `B68R2-02`, `B68R2-03`, `B68R2-12`, and `B68R2-13` are decisive for this emphasis. The successor must isolate an element-level novelty delta, prove that boundary uncertainty changes the theorem rather than merely the protocol vocabulary, give computational results at theorem level, and define fair comparisons capable of showing both safety and retained concurrency without importing unstated advantages.

### Assessment against Nature-style criteria

- Originality: explicitly unresolved and therefore not assessable as established.
- Scientific importance: potentially meaningful within MAPF execution, but no outstanding or far-reaching result is yet demonstrated.
- Interdisciplinary readership: plausible, especially through consistent-cut and runtime-assurance ideas, but the generalizable conclusion is not yet extracted.
- Technical soundness: the proposed theorem ladder is sensible as a research agenda; it is not evidence that the claims hold.
- Readability for nonspecialists: the motivating gap is accessible, while the novelty boundary requires a simpler statement of what prior methods know, decide, and guarantee.

### Recommendation posture

Promising as a sharply bounded research route, but the originality and significance case is currently underdeveloped and cannot support a strong Nature-style case.

## Reviewer 3

Emphasis: interdisciplinary readership and readability for nonspecialists.

### Overall assessment

The opening question is clear: when a plan finishes computing, the robots may not be where one optimistic prediction says they are. The manuscript becomes harder to follow when four different concepts use similar ownership language: physical presence, reservation, permission authority, and transaction state. The paper can become broadly intelligible if one decision timeline and one typed resource-state diagram carry the argument from uncertain evidence to exact MOVE, WAIT, or containment.

### Who would be interested in the results, and why

Beyond MAPF, readers working on asynchronous cyber-physical systems, distributed transactions, safety envelopes, and auditable autonomy could recognize the pattern: preserve a nominal controller exactly when knowledge is sufficient, and intervene only with a recorded witness when it is not. The current candidate hints at that pattern but frames most implications in domain-specific terms.

### Major strengths

- The document explicitly separates logical boundary states from physical edge occupancy.
- The fault taxonomy is readable and avoids relabeling PIE-D delay as a new error.
- The degradation table distinguishes safety from progress.
- The candidate gives a defensible reason pure simulation could be sufficient for an algorithmic/formal contribution: safety is to rest on proofs and symbolic traces, while simulation measures conservatism and throughput. This remains defensible only if claims about real sensors, braking, interlocks, and deployment reliability stay outside the evidence claim.
- The failure denominator and independent-unit definitions anticipate common reproducibility errors.

### Major concerns

- There is no single linear sequence showing when evidence is sampled, when the envelope is valid, when resources become unavailable to competitors, when a decision takes effect, and what can still change before departure.
- "Owner" alternates between the physical occupant and the authority that grants access. "Acquire" alternates between reservation and physical phase. This blocks nonspecialist comprehension and formal audit alike.
- The MOVE-to-WAIT rule is described per agent even though safety is batch-coupled. A broad reader will reasonably infer that suppressing one departure can obstruct every move that depended on the vacated origin; the candidate does not close that loop.
- The inactive identity claim needs a visible bypass boundary. Equal final actions are not bitwise identity if wrapper latency changes planner inputs, proposal ordering, task disclosure, or random-source consumption.
- The pure-simulation plan remains incomplete: simulator semantics, independent safety oracle, deterministic replay, environment capture, trace provenance, baseline information parity, and compute accounting are not fixed.

### Technical failings that need to be addressed before the case is established

The presentation issue is inseparable from `B68R2-04` through `B68R2-10`: the missing diagram is a symptom of missing semantics. The successor should define a typed state model, an explicit linearization point, closure over the complete output batch, and auditable certificates. It must also fulfill `B68R2-12` before any throughput or reproducibility claim can be interpreted.

### Assessment against Nature-style criteria

- Originality: the exact nominal-pass-through/witnessed-intervention pattern may be distinctive, but prior-work separation is not demonstrated.
- Scientific importance: broad importance is possible if the paper proves a reusable boundary-assurance principle; it is not demonstrated by a PIE-specific protocol proposal alone.
- Interdisciplinary readership: potential is real but currently latent.
- Technical soundness: key semantics remain incomplete, so readability changes alone would not establish the case.
- Readability for nonspecialists: strong initial motivation, followed by excessive compression and overloaded terminology.

### Recommendation posture

Major conceptual revision is required. A clearer manuscript would still need the same formal closures; this is not a copyediting-only recommendation.

## Cross-review synthesis

### Consensus strengths

- The candidate identifies a precise and consequential boundary between concurrent planning and physical commitment.
- It preserves PIE as the only MOVE source and treats intervention as exact MOVE preservation, certified WAIT, or containment.
- It distinguishes no-start delay, processing latency, uncertain observations, and excluded wrong-edge motion.
- It recognizes the need for event correlation, trusted positive evidence, physical holding conditions, fencing, idempotence, and explicit safety-versus-liveness separation.
- It is appropriately cautious: novelty, proof, utility, reproducibility, and implementation readiness are all left open.

### Consensus technical risks

- The proposed compact representation has no demonstrated computation that avoids global cut reasoning.
- The decision lacks a formal linearization point and validity interval.
- Per-agent refinement is not closed under batch dependencies, and asserted batch atomicity conflicts with per-MOVE commit authorities.
- Physical occupancy, reservation, authority, grant, and transaction phase are not yet cleanly separated.
- Partition/reconfiguration and crash/retry safety depend on unformalized enforcement and persistence assumptions.
- Inactive identity, triggered accountability, and conditional progress are specifications rather than established properties.
- Evaluation fairness and pure-simulation reproducibility remain open.

### Where emphasis differs across reviewers

- Reviewer 1 gives greatest weight to safety proof obligations and concrete protocol counterexamples.
- Reviewer 2 gives greatest weight to route-killing overlap, computational novelty, and the absence of a demonstrated high-significance result.
- Reviewer 3 gives greatest weight to the transferability and intelligibility of the core idea, and to whether a pure-simulation study can support only the claims it actually models.

These differences are weighting differences over the same registered facts; they do not rely on different evidence or invented reviewer identities.

### Broad-interest / significance readout

The work is potentially interesting beyond MAPF because it connects consistent-cut reasoning, runtime assurance, distributed fencing, and exact nominal-controller pass-through. The supplied candidate does not yet establish outstanding scientific importance or immediate and far-reaching implications. At present the contribution is a disciplined research specification, not a demonstrated scientific result.

### Most important issues to resolve before a strong Nature-style case is established

1. Establish a defensible novelty delta against the named closest neighbors using primary-source claims and theorem-level comparison.
2. Make the envelope operational: define updates, algorithms, separability, complexity, and conservatism.
3. Linearize decision and resource acquisition, then prove a complete batch MOVE-to-WAIT closure.
4. Formalize typed occupancy/reservation/authority/transaction invariants and the fault assumptions that make fencing and idempotence effective.
5. Prove inactive noninterference, triggered certificates, and meaningful conditional liveness.
6. Freeze fair baselines and a replayable pure-simulation protocol before any main experiment.

### Knowledge-certification readout

The candidate correctly identifies a necessary boundary: if every apparent release can be an indistinguishable false release and no physical interlock prevents conflicting entry, no nontrivial contested MOVE can be certified safe. The sufficient side is not yet proved. A sufficient contract would have to connect sound accepted evidence or an enforcing interlock, event-order containment, current-epoch exclusivity, durable transaction identity, resource-grant validity at the decision linearization point, full output-batch closure, and safe physical holding. Listing these ingredients is not itself a sufficiency proof.

## Risk / unsupported claims

- Unsupported novelty claim: no final novelty claim is made, correctly; any stronger claim would be unsupported until `B68R2-01` is closed.
- Unsupported compression claim: decidability from compact projections is not established without a construction and complexity analysis.
- Unsupported safety claim: T68-4 and T68-5 remain proof targets and are exposed by batch and fault witnesses below.
- Unsupported identity claim: equality of selected action bytes does not yet prove end-to-end baseline noninterference.
- Unsupported liveness claim: the current formulation allows repeated explicit rejection without task progress.
- Unsupported significance claim: no evidence in scope establishes outstanding scientific importance or broad impact.
- Not assessable from provided material: external-artifact availability, licenses, builds, original-method reproduction, empirical throughput, conservatism, tail waiting, starvation frequency, and simulator fidelity.
- Pure-simulation boundary: a formal-plus-simulation paper can be reproducible and scientifically adequate for algorithmic claims, but it cannot use those results alone to validate unmodeled sensor trust, braking physics, interlock reliability, or deployment robustness.

## Stable objection register

### BEARING objections

#### B68R2-01 [BEARING] Novelty exclusion is unresolved against the strongest adjacent work

The candidate's own route-killing tests remain open. It does not yet supply an element-level comparison against Hönig 2019 for ADG, commit cut, and planning/execution overlap; Liu 2024/2026 for known evolving locations, original-path MOVE/WAIT coordination, maximal moving sets, and hard feasibility; or POD Robotics 2026 for occupancy/reservation/queue/progress discrepancy, typed channels, age routing, and recovery. The successor must distinguish assumptions, information state, decision variable, theorem, complexity, and failure domain. Similar vocabulary is not enough, and title-level absence is not evidence of novelty.

#### B68R2-02 [BEARING] The scientific contribution is still a conditional route, not a result

Every item in the theorem ladder is a proof target. No theorem, lower bound, exact class, or empirical observation is complete. This is appropriate for a pre-experiment candidate but insufficient for a claim of correctness, usefulness, or high scientific importance.

#### B68R2-03 [BEARING] The compact state is denotationally defined but not shown computable

`MAY_OCCUPY` and `MUST_OCCUPY` quantify over E, while E quantifies over consistent predecessor-closed cuts with physical and ownership constraints. The candidate gives neither an incremental construction nor a decision procedure, complexity bound, hardness boundary, approximation order, or certificate checker. If computing one resource-local set invokes global cut feasibility, T68-COMP has not reduced the online problem.

#### B68R2-04 [BEARING] The commitment decision has no linearization point

The candidate does not identify the unique event at which the envelope, proposal digest, grant set, fence epochs, and physical phase jointly determine the decision. It also does not state what locks, version checks, or conservative envelope advancement keep that decision valid between OBSERVE, PREPARE, COMMIT, and departure. This leaves a time-of-check/time-of-use gap under the very processing and observation uncertainty being studied.

#### B68R2-05 [BEARING] MOVE-to-WAIT refinement lacks full-batch reverse closure and totality

Changing one agent from MOVE to WAIT retains its origin occupancy. Any other proposed MOVE whose safety depends on that origin being vacated must then also be suppressed, and this dependency can propagate. The candidate has no monotone closure operator, termination proof, final-batch safety check, or treatment of a proposed WAIT/induced WAIT that lacks a safe-holding certificate. Per-agent guards are insufficient.

#### B68R2-06 [BEARING] Atomic batch semantics conflict with per-MOVE commit authorities

Section 12.3 requires atomic batch commitment, while section 13.3 assigns a separate destination authority to each MOVE and permits independent transactions. No coordinator, linked conditional grant, common commit record, or safe-partial-start theorem connects those statements. Physical following moves are especially sensitive because a destination may be another agent's currently occupied origin.

#### B68R2-07 [BEARING] Physical occupancy, reservation, permission, authority, and transaction state are not type-separated

The word `owner` refers both to an authority and, implicitly, to an occupant or holder; `acquire` can mean a reservation or a physical phase. The model needs disjoint state variables and invariants for physical occupant, reservation holder, grant authority, fence-enforcement point, transaction phase, and release certificate. OR and DA obligations also need a precise relationship to exclusive resources rather than being listed as if all resource kinds had identical semantics.

#### B68R2-08 [BEARING] Partition, reconfiguration, lost ACK, crash, and mid-edge failure are not yet covered by enforceable invariants

Monotonic epochs do not alone prevent two partitioned components from acting. The model must state how one history wins, where stale fences are rejected, and what assumptions support reconfiguration. Exactly-once physical execution after lost ACK requires durable deduplication or an equivalent interlock across executor crash and incarnation change. Mid-edge containment must retain every conflicting swept-volume resource until a trusted terminal transition; expected duration cannot release it.

#### B68R2-09 [BEARING] PIE inactive bitwise identity is not established as noninterference

The proposed comparison fields are appropriate, but no bypass boundary prevents wrapper observation, bookkeeping, or latency from changing planner input timing, task disclosure order, proposal order, or random-source state. Equal semantic actions are weaker than bitwise identity. The inactive theorem needs canonical byte domains and an execution-coupling argument.

#### B68R2-10 [BEARING] Triggered refinement is not yet a total, independently checkable contract

The log fields are useful but require canonical serialization, an activation predicate, sound witness generation, and a verifier whose accepted certificate implies the final batch theorem. The candidate does not define what happens when PIE proposes WAIT at an uncertified holding state, when an induced WAIT is unsafe, or when the point of no return occurs during decision formation.

#### B68R2-11 [BEARING] Conditional progress is too weak to establish liveness

"Commits or receives a newer explicit reason for rejection" permits infinite rejection and therefore does not establish task progress. "Repeatedly feasible" does not ensure feasibility when service occurs. The theorem needs stable-authority and no-infinite-epoch-churn assumptions, a precise persistent-feasibility condition, the selected fairness notion, retry behavior, finite-contender conditions where needed, and a progress measure distinct from diagnostic responsiveness.

#### B68R2-12 [BEARING] Baseline fairness and pure-simulation reproducibility are not operational

The candidate lists the right regimes but leaves baseline versions, comparator inclusion, information parity, action authority, compute budget, runtime environment, timeout/censoring policy, trace generation, randomization records, independent safety oracle, and deterministic replay open. Strict same-compute must account for planner, envelope, and protocol work without advantaging the proposed method; natural-runtime must expose total wall-clock and implementation effects. All methods must see the same admissible evidence and face the same launched-unit denominator.

#### B68R2-13 [BEARING] A Nature-level broad-interest case is not demonstrated

The candidate may support a strong specialist contribution if its theorems hold, but the registered material does not establish outstanding scientific importance, an arresting result, or immediate and far-reaching implications. A future manuscript must derive a general principle and demonstrate retained concurrency or another nontrivial benefit without overstating what pure simulation can validate.

### NON-BEARING objections

#### NB68R2-01 [NON-BEARING] Preserve the semantic exclusions but make them visible earlier

The delay/error distinction, same-tick slowdown exclusion, wrong-edge exclusion, and no-alternative-MOVE rule are coherent. A compact front-page scope box would prevent readers from misclassifying the work.

#### NB68R2-02 [NON-BEARING] Use conjecture/proof-obligation labels consistently

The text already says theorems are targets. Repeating `candidate theorem` or `proof obligation` in headings would avoid accidental overreading before proofs exist.

#### NB68R2-03 [NON-BEARING] Add a compact glossary and one decision-timeline figure

Terms such as event ideal, boundary cut, authority, fence, holding certificate, physical containment, and proposal digest need one stable definition each. This is a readability obligation and does not close the bearing semantic gaps by itself.

#### NB68R2-04 [NON-BEARING] Retain the conservative pre-experiment status language

The explicit OPEN gates, failure denominator, and refusal to predict effect direction are strengths. They should survive revision unchanged in intent.

## Failure witnesses

#### FW68R2-01: Reverse-closure collision

PIE proposes `a: MOVE(u,v)` and `b: MOVE(w,u)`. The original batch is valid because `a` is expected to vacate `u`. Uncertainty rejects `a`'s MOVE, and `a` waits safely at `u`; if `b` is assessed only against the original proposal and remains a MOVE, `b` enters occupied `u`. This falsifies per-agent substitution without reverse closure.

#### FW68R2-02: Partial following-batch start

PIE proposes `a: MOVE(u,v)` and `b: MOVE(v,w)`. Separate destination authorities complete `a`'s commit while `b`'s commit is missing or aborted. If `a` starts on the assumption that `b` vacates `v`, physical conflict follows; if `a` is always denied because `b` MAY occupy `v`, useful following concurrency disappears. The candidate must choose and prove atomic linked handoff or safe conservative serialization.

#### FW68R2-03: Decision time-of-check/time-of-use gap

An envelope and grant set are accepted for one event prefix. Before the decision becomes effective, a relevant physical phase advances or an authority epoch changes. Without a linearization point plus lock/version/fence enforcement, the commit can be valid for the checked prefix but invalid for the state at departure.

#### FW68R2-04: Partitioned authority histories

An old authority retains a prepared grant while another component installs a newer authority and grants the same resource. If the physical admission point does not reject the losing epoch, both histories can authorize entry. A monotonic epoch field in messages does not itself choose or enforce the winning history.

#### FW68R2-05: Lost ACK followed by executor restart

A transaction physically completes, its ACK is lost, and the executor restarts without durable terminal transaction state. A replayed COMMIT can be interpreted as new work despite an idempotence key. Boot identity prevents confusion only if old commits are fenced and terminal knowledge or physical state survives in an enforceable form.

#### FW68R2-06: Unsafe induced WAIT

A MOVE is suppressed after its point-of-no-return status becomes ambiguous, or its origin lacks SH-DYNAMIC because an incoming transaction is already committed. Returning symbolic WAIT does not stop the physical traversal or cancel the incoming acquisition. The refinement function therefore has no safe ordinary action unless the precondition excludes this state or containment semantics are total.

#### FW68R2-07: Vacuous progress by repeated rejection

A continuously requesting transaction is repeatedly feasible, but never at the instants when the authority serves it; every request receives a fresh reason for rejection. The stated T68-9 conclusion holds while no transaction commits and no task progresses.

#### FW68R2-08: Hidden global oracle in local occupancy sets

To decide whether an agent belongs to `MAY_OCCUPY(r)`, the procedure must decide whether any globally consistent event cut places that agent on `r`. If the only construction searches the full correlated cut space, storing the resulting set is compact but computing it is not the claimed reduction.

#### FW68R2-09: Semantic equality without bitwise identity

The wrapper emits the same action labels as PIE-D but delays task disclosure or consumes a random draw before the planner call. The next planner-input bytes, proposal order, or random-source state differ. Action equality at one boundary therefore does not establish inactive bitwise identity.

#### FW68R2-10: Mid-edge failure with premature resource release

An agent departs `u`, occupies the protected edge region, and fails before certified arrival at `v`. If any owner releases `u`, the edge exclusion, or destination protection from an expected duration, timeout, stale completion, or lost bookkeeping, a conflicting transaction can enter the swept volume. Safety requires the physical occupancy/interlock state to dominate until trusted terminal reconciliation.

## Constructive revision obligations

#### RO68R2-01 closes B68R2-01

Produce a primary-source claim chart for PIE/PIE-D, Hönig 2019, Liu 2024/2026, POD Robotics 2026, and any closer discovered work. For each, record the known state, uncertainty source, allowed action changes, planning horizon, commit seam, safety/liveness theorem, computational burden, physical-resource semantics, and exact exclusion from Candidate 68. Any unresolved route-killing overlap remains OPEN.

#### RO68R2-02 closes B68R2-02

Convert the theorem ladder into dependency-ordered definitions, lemmas, theorems, and explicit nonclaims. Mark which statements are general soundness, which are class-restricted completeness, and which are protocol assumptions. Do not advance the route on theorem names alone.

#### RO68R2-03 closes B68R2-03

Define a finite input encoding and an incremental algorithm for L, U, cut consistency, `MAY_OCCUPY`, `MUST_OCCUPY`, and batch certification. Define the resource-separable class structurally, give a recognition procedure, prove soundness and the stated completeness boundary, and state computational complexity or hardness. If a conservative approximation is used, define its order and expose correlation-loss rejections.

#### RO68R2-04 closes B68R2-04

Select one decision linearization event and specify the state version it covers. State which prepares reserve resources, which events may advance concurrently, how stale versions fail closed, when grants expire by logical state rather than wall clock, and how a current physical phase is coupled to the commit. Prove that authorization remains safe through departure.

#### RO68R2-05 closes B68R2-05

Define a monotone reverse-dependency closure over the whole proposed batch. Seed it with every rejected MOVE and every unsafe proposed WAIT; propagate suppression to any MOVE requiring a retained origin or other unreleased resource; recompute holding validity; terminate at a fixed point; and certify the final output batch, not the original PIE batch. If no certified WAIT exists, return no new discrete authorization and enter precisely defined containment. Prove termination, soundness, and no-alternative-MOVE.

#### RO68R2-06 closes B68R2-06

Choose one coherent batch model: a common atomic commit record for coupled actions, linked conditional grants with a proof of all permitted partial orders, or conservative serialization. Define coordinator/authority failure behavior and show that every physically possible partial delivery/start trace remains collision-free. Quantify future throughput consequences only after this semantic choice is frozen.

#### RO68R2-07 closes B68R2-07

Introduce disjoint typed variables for physical occupant, swept-volume occupancy, reservation holder, grant authority, fence-enforcement point, transaction phase, release certificate, and holding right. Give state invariants and allowed transitions. State exactly when origin, edge, opposite-edge exclusion, and destination protections are acquired and released.

#### RO68R2-08 closes B68R2-08

Define the fault model for crash-stop, restart, partition, reconfiguration, corrupted report, and physical failure. State the authority-selection or interlock assumption, durable deduplication boundary, old-incarnation rejection rule, merge rule, and resource retention during mid-edge containment. Show the relevant symbolic traces preserve safety; suspend liveness explicitly where assumptions fail.

#### RO68R2-09 closes B68R2-09

Define the exact byte domains and a coupled baseline/wrapper execution. In inactive mode, bypass every operation that can alter planner inputs, proposal/action ordering, task disclosure, scheduling-visible timing, or random-source consumption; keep audit metadata outside those channels. Prove equality from identical initial bytes and environmental trace, not only equality of one action label.

#### RO68R2-10 closes B68R2-10

Define a total refinement function and canonical certificate schema. Every activation must carry a checkable envelope/version digest, trigger witness, final-batch closure witness, safe-holding evidence or containment reason, exact proposal/output mapping, and transaction/fence lineage. The verifier's acceptance condition must imply the relevant safety theorem.

#### RO68R2-11 closes B68R2-11

Separate response accountability from progress. State persistent feasibility, eventual authority stability, communication and physical terminal assumptions, contention scope, retry semantics, and the precise fairness condition. Use a well-founded or temporal progress property that cannot be satisfied by infinite fresh rejections.

#### RO68R2-12 closes B68R2-12

Freeze comparator artifacts and give all methods the same admissible observations, proposal trace, physical fault trace, and launched-unit denominator. Define strict same-compute accounting and natural-runtime accounting separately, including all wrapper/protocol work. Freeze public generation procedures, provenance manifests, stopping/censoring/retry rules, deterministic replay, environment capture, and an independent collision/resource oracle. Preserve failures in the denominator by declared cause.

#### RO68R2-13 closes B68R2-13

Frame the transferable result as a boundary-assurance theorem only after it exists, identify who outside MAPF benefits and why, and show a nontrivial usefulness result under fair baselines. Pure simulation is sufficient only for formal/algorithmic and modeled-system claims backed by proofs, symbolic witnesses, and replayable experiments; explicitly disclaim validation of unmodeled hardware, sensing, braking, interlock, and deployment properties. No physical experiment is required unless those real-world properties become part of the claim.

## Protected-symbol and activity audit

- `H`: `UNASSIGNED`.
- `T_delay`: `UNASSIGNED`.
- `B_CAL`: `UNASSIGNED`.
- `B_max`: `UNASSIGNED`.
- `B*`: `UNASSIGNED`.
- `P_active`: `UNASSIGNED`.
- density `N`: `UNASSIGNED`.
- This report introduces no numerical value, interval, range, default, prior, tuning direction, or empirical estimate for any protected symbol.
- No implementation, build, test, simulator execution, parameter tuning, main experiment, or scientific payload was performed or authorized.

## Candidate disposition

- Referee-level ballot: `BEARING OBJECTIONS / REVISION REQUIRED`.
- Nature-style case: `CURRENTLY NOT ESTABLISHED FROM THE PROVIDED EVIDENCE`.
- Editorial boundary: this is not an acceptance/rejection decision by a Nature editor and does not claim certainty about journal fit.
- Successor consequence: because the report contains substantive BEARING objections, Candidate 68 cannot be accepted as the route root without resolving them in a new-number successor under its own review protocol.
- Candidate control state after review: `HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`.
- Review transport state: `CLOSED`; this means only that the registered candidate was fully reviewed and a nonempty report was written. It does not mean the candidate, objections, gates, novelty, proofs, or route are closed.

## End-of-report candidate identity registration

- Candidate: `/home/lyh/MAPF_PIED_MDDR_RESEARCH/68_PIE_COMMIT_BOUNDARY_STATE_ENVELOPE_UNDER_PROCESSING_AND_OBSERVATION_UNCERTAINTY_JOURNAL_ROUTE_CANDIDATE_20260904.md`
- Candidate SHA-256 at registration, review start, and review end: `105ae41743f13a0add69751e0be322fbdd2ee99a81adfbdd9707ae7e3e8e0c5c`
- Candidate bytes at registration, review start, and review end: `37575`
- Candidate lines at registration, review start, and review end: `793`
- Complete-read proof: one complete candidate-content read occurred between matching start and end identity gates, from the registered first heading through the terminal `HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT` state. No forbidden review, old-candidate material, outcome file, or scientific payload entered the assessment basis.
- Terminal review status: `CLOSED = REVIEW COMPLETED ONLY`.
- Terminal candidate disposition: `BEARING OBJECTIONS / HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT`.
