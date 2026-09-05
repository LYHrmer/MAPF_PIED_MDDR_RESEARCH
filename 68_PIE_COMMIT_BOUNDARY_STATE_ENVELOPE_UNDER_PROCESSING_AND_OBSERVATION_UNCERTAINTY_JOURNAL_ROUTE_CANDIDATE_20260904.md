# 68 PIE Commit-Boundary State Envelope under Processing and Observation Uncertainty

Date: 2026-09-04

Artifact class: JOURNAL-ROUTE CANDIDATE / FORMAL PRE-EXPERIMENT SPECIFICATION / NONBALLOT

Status: OPEN / REVISION-REQUIRED UNTIL REVIEWED

Global state: HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT

No algorithm implementation, build, test, simulator run, parameter tuning, experimental payload, result writing, or release update is authorized by this document.

## 1. Lineage and reason for new bytes

Candidate 68 is a substantive successor to frozen Candidate 67:

- Candidate 67 SHA-256: 592825952065b2bee7386a1f91086e5778aa74fb689f7c22c318339da100860d
- Root audit: 67A1_PIE_UNCERTAIN_FEEDBACK_SCOPE_COLLISION_AND_SUCCESSOR_DECISION_ROOT_AUDIT_20260904.md

Candidate 67 was too broad: generic uncertain feedback overlaps belief-space MAPF, fixed-plan robust execution, and protocol-observation discrepancy calibration. Candidate 68 narrows the scientific object to the uncertain configuration at the boundary between a PIE planning interval and its next commit window.

This document does not amend, rename, sidecar, or revive Candidate 67.

## 2. Plain-language problem contract

PIE plans future actions while robots execute already committed actions. PIE-D handles failed movement attempts as delays and uses a dummy simulation that assumes no further delay to predict one next-window starting configuration.

That single prediction can be wrong when:

- planning itself takes time while physical execution continues;
- completion or current-state messages are delayed, missing, duplicated, or reordered;
- different admissible information sources disagree;
- an agent may be at its origin, traversing its authorized edge, or at its destination when the next plan becomes available.

The proposed research question is:

> Can a compact, sound set of possible PIE commit-boundary states replace the single optimistic boundary prediction, so that the system can preserve an exact PIE action whenever universally safe and otherwise convert only that action to safe WAIT or physical containment, without performing full belief-space replanning?

The primary contribution is not a new probability of failure. It is an information-and-execution contract at PIE's concurrent planning boundary.

## 3. Non-contribution and semantic exclusions

### 3.1 Delay is not renamed as error

An intended MOVE that does not start and leaves the agent at its origin is the MAPF-DP/PIE-D delay event. It is baseline behavior, not a new error class.

### 3.2 Same-tick slowdown remains a semantic null operation

Standard discrete MAPF observes only the state at tick boundaries. Multiple speed reductions inside one tick do not define a different MAPF action. They are permanently separated from coordinated WAIT.

### 3.3 Wrong-edge motion is outside this candidate

Candidate 68 assumes that any newly started physical traversal follows the exact edge authorized by the PIE proposal and committed transaction. Random wrong-edge motion, overshoot, or unconstrained drift would require a new model and a new candidate with continuous geometry and low-level fault control.

### 3.4 No alternative path action

The refinement layer never chooses a neighboring vertex, detour, priority-inheritance move, or repaired path. PIE is the only default source of proposed MAPF actions.

## 4. Verified motivating gap

### 4.1 PIE

PIE commits a symbolic number of actions and plans the uncommitted suffix concurrently under perfect execution.

- Yue Zhang et al., Planning and Execution in Multi-Agent Path Finding: Models and Algorithms, ICAPS 2024.
- DOI: https://doi.org/10.1609/icaps.v34i1.31534
- Author full text: https://people.eng.unimelb.edu.au/pstuckey/papers/ICAPS24.pdf

### 4.2 PIE-D

PIE-D retrieves one current state and committed-but-unexecuted actions. Its Dummy Simulation assumes no delays and predicts one next commit-window start configuration.

- Yue Zhang et al., Concurrent Planning and Execution in Lifelong Multi-Agent Path Finding with Delay Probabilities, AAAI 2025.
- DOI: https://doi.org/10.1609/aaai.v39i22.34506
- Official full text: https://ojs.aaai.org/index.php/AAAI/article/download/34506/36661

Candidate 68 targets the missing set-valued boundary semantics. This is a candidate gap, not yet a novelty verdict.

## 5. Formal scope

Let G = (V, E) be a graph. Each agent i receives from PIE one proposed discrete action for the next decision:

- WAIT(i, u), or
- MOVE(i, u, v), where (u, v) is in E.

Each action occurrence has an occurrence index. Vertices may repeat in a committed path; therefore an occurrence is identified by agent and path index, not only by a vertex name.

Candidate 68 has two linked layers:

- Logical MAPF layer: certified endpoint states at decision boundaries.
- Physical execution layer: origin occupancy, edge-in-progress occupancy, destination acquisition, completion, and fenced resource ownership.

The physical layer exists only to prevent discrete decisions from pretending that a robot has already released a resource while it remains physically present.

## 6. Error and latency taxonomy

### E68-D: baseline no-start delay

The authorized MOVE does not start and the agent remains at its origin. This is PIE-D delay.

### E68-P: processing latency

The planner consumes a nonzero and potentially variable physical interval. Execution facts can change after the planner's input snapshot and before its output is considered for commitment.

Safety must not depend on a known upper bound. Progress may require an eventual-timeliness assumption stated separately.

### E68-O1: stale observation

A syntactically valid observation describes an earlier event prefix or earlier epoch.

### E68-O2: missing observation

No completion, occupancy, or current-state evidence is available when a decision is requested.

### E68-O3: duplicated or reordered observation

An old idempotent message reappears or messages arrive in an order different from physical event order.

### E68-O4: conflicting observation

Two admissible channels assert incompatible endpoint, occupancy, ownership, or progress facts.

### E68-O5: false completion or false release assertion

An untrusted channel asserts that an edge or origin was released when positive trusted evidence does not support release.

### E68-O6: endpoint ambiguity

Available evidence permits more than one of origin, authorized edge-in-progress, or destination.

### Excluded error class

No observation may justify a new MOVE to an edge that was not proposed by PIE. Uncommanded physical motion is a low-level fault outside this candidate's safety theorem.

## 7. Trusted evidence boundary

The model distinguishes facts from reports.

### 7.1 Facts

Physical facts include:

- AT(i, v): agent i physically occupies endpoint v;
- ON(i, u, v, tid): agent i is traversing the directed edge occurrence from u to v under transaction tid;
- ARRIVED(i, v, tid): arrival at v has physically occurred;
- HOLDING(i, v): agent i can remain at v under the safe-holding contract.

### 7.2 Reports

Every protocol report carries:

- transaction identifier;
- resource epoch or epoch vector;
- per-sender sequence identifier;
- event type;
- payload digest;
- sender identity;
- integrity evidence required by the deployment model.

Reports may be stale, missing, duplicated, reordered, or mutually inconsistent. An untrusted negative observation does not prove that a physical occupant is absent.

### 7.3 Minimal trust assumption

At least one mechanism must provide unforgeable positive evidence for resource acquisition and eventual release, or a physical interlock must prevent conflicting entry.

Without either mechanism, an arbitrary false-release observation is indistinguishable from true release. No nontrivial collision-free MOVE policy can then be guaranteed. This is an impossibility boundary, not an engineering inconvenience.

## 8. Event structure

For every exact PIE MOVE occurrence, define ordered events:

1. proposed;
2. resources prepared;
3. transaction committed;
4. physical departure begins;
5. directed edge becomes physically occupied;
6. destination is acquired;
7. origin is released only after certified departure;
8. arrival completes;
9. directed edge is released only after certified arrival;
10. completion is acknowledged.

These labels describe an order, not measured timing values.

The point of no return is physical departure or edge occupancy, whichever is observed first. Before that point, a prepared transaction may abort. After that point, ABORT may not pretend that the agent remains safely at its origin; the transaction must complete or enter RECOVER/physical containment.

## 9. Commit-boundary event envelope

### 9.1 Event DAG

Let D be a directed acyclic graph of event occurrences. It contains:

- per-agent action order;
- prepare-before-commit;
- commit-before-departure;
- destination-acquire-before-conflicting-entry;
- departure-before-origin-release;
- arrival-before-edge-release;
- resource-owner serialization;
- predecessor relations inherited from the exact committed PIE prefix.

### 9.2 Lower and upper event ideals

Maintain:

- L: events proved complete by accepted positive evidence;
- U: events not ruled out as complete by accepted evidence and event order.

A physically possible boundary cut I must:

- be predecessor-closed in D;
- contain L;
- be contained in U;
- satisfy unique physical location/phase for every agent;
- satisfy resource-owner and fencing constraints;
- agree with positive physical occupancy evidence.

The commit-boundary envelope E is the set of all such cuts and their induced physical configurations.

The scientific invariant is:

> If the trust and physical-conformance assumptions hold, the true boundary cut is in E.

No probability distribution is required for this containment claim.

### 9.3 Why the full Cartesian product is rejected

Independent per-agent location sets can contain joint configurations that violate event dependencies and resource serialization. Candidate 68 therefore retains an event DAG and does not define E as an unconstrained Cartesian product.

## 10. Compact information state

Enumerating every cut in E is prohibited as the default method. The candidate compact state is:

- lower event ideal L;
- upper event ideal U;
- per-agent minimum and maximum reachable occurrence indices on its exact committed path;
- current in-progress edge occurrence, if positively observed;
- for every exclusive resource r, MAY_OCCUPY(r);
- for every exclusive resource r, MUST_OCCUPY(r);
- unique protocol owner and current fence epoch for r;
- prepared and committed transaction identifiers touching r;
- unresolved evidence conflicts;
- safe-holding certificate for each candidate holding vertex.

MAY_OCCUPY(r) is the set of agents for which at least one cut consistent with L, U, and D occupies r.

MUST_OCCUPY(r) is the set of agents that occupy r in every consistent cut.

Resource identities include:

- vertex resource V(v);
- directed-edge resource DE(u, v);
- opposite-edge exclusion resource OE({u, v});
- origin-release obligation OR(i, u, tid);
- destination-acquire obligation DA(i, v, tid).

The representation uses occurrence indices so a path that revisits a vertex does not collapse two physically different phases.

## 11. Proposed compression theorem

### T68-COMP candidate statement

Assume:

- agents physically conform to their exact committed path occurrences;
- all physical conflicts are expressible as exclusive vertex, directed-edge, or opposite-edge resource occupancy;
- accepted positive evidence is sound;
- event order and resource fences are enforced;
- a new decision authorizes only one exact PIE action per agent or WAIT.

Then universal one-decision collision safety over every joint cut in E is decidable from:

- the proposing agent's certified origin/phase;
- resource-local MAY_OCCUPY and MUST_OCCUPY sets;
- the event-DAG predecessor relation for resources touched by the proposed batch;
- pairwise resource conflicts among the exact proposed actions;
- current owner/fence and transaction state.

It is not necessary to enumerate every joint configuration in E.

### Intended proof structure

1. Show that every collision witness contains a conflicting exclusive resource atom.
2. Project any joint-cut collision witness to one resource-local MAY_OCCUPY witness or one pair of proposed actions.
3. Show that each rejected resource-local witness corresponds to an admissible joint cut under the stated separability conditions.
4. Separate the general case: if projection feasibility cannot be reconstructed because of cross-resource correlations, the check remains sound but may be conservative.

### Exactness boundary

Soundness is required generally under the assumptions. Sound-and-complete reduction is claimed only for an explicitly characterized resource-separable event-DAG class. That class must be formally defined and shown to include nontrivial corridors, trees, and intersections before the route can pass review.

If exactness requires enumerating all joint cuts, T68-COMP fails and the journal route must be reconsidered.

## 12. Exact PIE refinement rule

Let p_i be PIE's exact proposal for agent i.

### 12.1 Proposed WAIT

Preserve WAIT only if the current endpoint has a valid safe-holding certificate and no already committed incoming transaction makes continued occupancy unsafe.

### 12.2 Proposed MOVE

Preserve the exact MOVE(i, u, v) only if all conditions hold:

- agent i is certified at origin occurrence u and is not already in another edge transaction;
- the proposal bytes identify the same occurrence and edge produced by PIE;
- destination V(v) has no conflicting possible occupant;
- DE(u, v) and OE({u, v}) have no conflicting possible occupant;
- origin V(u) remains owned by i until certified departure;
- destination and edge resources have valid prepares from their unique owners;
- the commit authority holds a current fence for every grant;
- the proposed batch has no vertex, directed-edge, or opposite-edge conflict;
- destination v satisfies the dynamic holding condition needed if subsequent progress stops;
- unresolved evidence conflict cannot hide a physical occupant.

If any condition fails:

- output WAIT only when u is a certified safe holding vertex; or
- if physical departure already crossed the point of no return, issue no new discrete action and contain or complete the already committed physical transaction.

No branch selects an alternative MOVE.

### 12.3 Batch semantics

A batch is committed atomically with respect to its exclusive resource grants. Partial grant receipt does not authorize a partial physical start. Independent nonconflicting transactions may proceed under distinct resource owners, but each transaction has one commit authority.

## 13. Resource ownership and commit authority

### 13.1 Unique resource owner

Each exclusive resource r has exactly one authority AUTH(r, epoch) in a valid epoch. Only that authority may issue a prepare grant for r.

The authority assignment may be distributed across vertices and edges. It is not a claim that one global coordinator owns all resources.

### 13.2 Transaction identifier

Every movement transaction uses a globally unique logical identifier formed from:

- agent identity;
- boot/incarnation identity;
- monotonic local sequence;
- proposal digest.

The representation is symbolic. No bit width or numerical allocation is selected here.

### 13.3 Commit authority

For MOVE(i, u, v), the authority of destination V(v) is the deterministic transaction commit authority. It may commit only after collecting current-epoch prepare grants for every required resource.

The commit authority cannot manufacture another resource owner's grant.

### 13.4 Epoch and fencing

Every ownership change advances a monotonic epoch. A grant from an older epoch is fenced and cannot authorize execution after reconfiguration or component merge.

Safety does not rely on synchronized wall clocks or lease expiry alone.

### 13.5 Idempotence

OBSERVE, PROPOSE, PREPARE, COMMIT, COMPLETE, ACK, ABORT, and RECOVER messages are idempotent by transaction identifier, epoch, sequence, and payload digest.

Two messages with the same idempotence key but different payload digests are evidence conflicts and force containment.

## 14. Required state machine

### OBSERVE

Collect physical and protocol evidence. Classify each report by identity, epoch, sequence, digest, age ordering, and trust class. Do not convert absence of evidence into release.

### PROPOSE

Record the exact PIE action digest and its assumed boundary input. A proposal creates no physical authority.

### PREPARE

Resource owners tentatively reserve required resources. Prepare is revocable before commit and does not permit departure.

### COMMIT

The one commit authority records the complete current-epoch grant set and issues the fenced decision. Duplicate identical COMMIT is harmless.

### EXECUTE

The physical layer begins only after a valid COMMIT. Departure establishes the point of no return and positive edge occupancy.

### COMPLETE

Positive arrival evidence closes the physical traversal. Origin and edge releases follow certified physical events, not planner prediction.

### ACK

ACK confirms receipt but is not itself physical completion. A lost ACK causes retransmission of the same idempotent state, not a second traversal.

### ABORT

ABORT is permitted before the point of no return. It releases prepares but cannot release physical occupancy that has already begun.

### RECOVER

RECOVER reconciles conflicting evidence, ownership epochs, interrupted transactions, and component merges. It authorizes no alternative MAPF MOVE.

## 15. Physical occupancy priority

Evidence is ordered conservatively:

1. positive physical occupancy or edge-in-progress evidence;
2. current-epoch committed transaction state;
3. current-epoch positive completion/release certificate;
4. current protocol bookkeeping;
5. stale, conflicting, or negative observation.

If a lower-priority source says free while a higher-priority source says occupied, the resource remains occupied.

A timeout, missing ACK, planner prediction, or elapsed wall-clock duration cannot by itself release a physically occupied resource.

## 16. Safe holding vertex contract

A vertex is a safe holding location for agent i only when all three conditions hold.

### SH-STATIC

The vertex is physically stoppable and is not designated as a no-stop edge interior, swept-volume conflict area, or non-holdable bottleneck interior.

### SH-DYNAMIC

The agent owns or is granted continued occupancy, and no committed incoming transaction can acquire the same physical region while it waits.

### SH-BRAKE

Given the current physical phase, the agent can stop before crossing the protected resource boundary. If this is not true because the point of no return has passed, WAIT is not a valid abstraction; the existing transaction must complete or enter physical containment.

All three are required. A graph vertex label alone is not a safe-holding certificate.

## 17. Theorem ladder

All items below are proof targets, not completed theorems.

### T68-0 Semantic non-equivalence

Prove that E68-O and E68-P alter the agent's information state while a PIE-D no-start delay alters only physical progress under correctly known state. Also prove that E68-D alone reduces to PIE-D.

### T68-1 Impossibility under arbitrary false release

If all occupancy/release channels may produce indistinguishable arbitrary false negatives and no physical interlock exists, no policy that ever authorizes a contested MOVE can guarantee collision freedom.

### T68-2 Envelope containment

Under accepted-positive-evidence soundness, path conformance, and fencing, the true physical boundary cut is always contained in E.

### T68-3 Compact resource projection

Prove T68-COMP, including the exact resource-separable class and a conservative general-case statement.

### T68-4 Safety refinement

Every action emitted by the wrapper is either the exact PIE action or a certified safe WAIT/containment, and every emitted batch is collision-free for every physical state in E.

### T68-5 Transaction safety

The resource protocol prevents dual current-epoch ownership, vertex conflict, same-directed-edge conflict, opposite-edge conflict, premature origin release, premature destination acquisition, and duplicate physical execution.

### T68-6 Inactive identity

When the boundary envelope is a certified singleton equal to PIE-D's boundary state, observations are consistent, and no protocol guard is active, the wrapper preserves the baseline planner input and exact action-vector bytes.

### T68-7 Triggered refinement accountability

Whenever output differs from PIE-D, the log contains an uncertainty or resource witness and the only discrete difference is PIE MOVE to WAIT. No alternative MOVE is permitted.

### T68-8 Safety under asynchronous degradation

Lost messages, duplication, reordering, clock skew, network partition, and unbounded delay can prevent progress but cannot create a conflicting current-epoch grant or false physical release.

### T68-9 Conditional progress

Under eventual communication, eventual terminal physical outcomes, fair resource service, valid safe holding, and a repeatedly feasible exact PIE proposal, every continuously requesting transaction eventually commits or receives a newer explicit reason for rejection.

Safety is unconditional with respect to message-delay duration under the model. Liveness is not.

## 18. Minimal counterexample suite

Each witness must later become a symbolic trace checked independently of experimental results.

### CEX68-01 False completion and following conflict

Agent a is still at origin u after a no-start delay. A stale or false completion says u was released. Agent b is authorized into u. A vertex collision follows unless positive release is required.

### CEX68-02 Optimistic commit-boundary prediction

The planner predicts agent a at v after the commit window while a may still be at u. A future PIE suffix valid from v is not necessarily executable from u.

### CEX68-03 Lost ACK and duplicate execution

COMMIT is executed, COMPLETE is recorded, but ACK is lost. Treating retry as a new command repeats the MOVE. Transaction idempotence must instead return the existing terminal state.

### CEX68-04 Clock-skew lease expiry

One resource owner considers a lease expired while another clock considers the old owner active. Wall-clock expiry can create dual ownership; epoch fencing must dominate.

### CEX68-05 Network partition

Two components each believe they may grant the same intersection. New commits must stop without the current authority; already committed motion may only complete or contain.

### CEX68-06 Mid-edge failure

An agent begins u to v and stops on the edge. Releasing u, v, or the opposite-edge exclusion solely from expected duration permits a conflicting traversal.

### CEX68-07 Unsafe WAIT

An executor suppresses MOVE and waits at a nominal vertex that is inside a non-stoppable intersection or has an already committed incoming agent. WAIT is unsafe without all three holding conditions.

### CEX68-08 Corridor or tree retreat impossibility

Two agents enter a single-width branch from opposite directions with no internal safe hold. Once both cross their points of no return, MOVE-to-WAIT refinement cannot repair the state. Entry serialization is required before commitment.

### CEX68-09 Intersection starvation

A locally safe repeated WAIT can indefinitely deny one approach while other approaches repeatedly receive grants. Safety does not imply progress; fair service is an explicit liveness assumption.

### CEX68-10 Component merge with stale epoch

Two previously partitioned components merge. Replaying an older valid-looking grant without fencing can resurrect a second owner.

### CEX68-11 Cartesian-product over-conservatism

Independent local state sets combine mutually exclusive progress states into an impossible joint state and force all agents to wait. The event DAG must preserve enough correlation to beat slowest-agent synchronization.

### CEX68-12 No trustworthy absence information

All sensors can falsely report an occupied destination as free, and no interlock exists. Any nontrivial entry policy has indistinguishable safe and colliding worlds, proving T68-1's impossibility boundary.

## 19. Explicit degradation table

| Disturbance | Safety response | Progress status |
|---|---|---|
| Lost ACK | resend/query same transaction; do not re-execute | may pause until terminal state is learned |
| Duplicate or reordered message | idempotence and sequence/epoch rejection | preserved if eventual fresh message arrives |
| Clock skew | no safety release based only on wall-clock expiry | may retain resources conservatively |
| Network partition | deny new contested commits; finish or contain already committed motion | no liveness claim during partition |
| Unbounded message delay | retain MAY occupancy and resource ownership | safety only; liveness suspended |
| Corridor/tree without internal safe hold | serialize entry before point of no return | throughput may fall; no reactive retreat claim |
| Intersection | one current authority per exclusive resource | depends on fair queue service |
| Starvation | preserve safety and expose wait witness | liveness requires fairness assumption |
| Component merge | reconcile epochs; fence all losing histories | resume only after ownership convergence |
| Conflicting physical/protocol evidence | physical occupancy wins; enter RECOVER | no progress until conflict is resolved |

## 20. Novelty and difference matrix

| Neighbor | Its scientific object | Relation to Candidate 68 | Route-killing overlap test |
|---|---|---|---|
| PIE, ICAPS 2024 | concurrent plan improvement and fixed commit windows under perfect execution | supplies the proposal source and boundary seam | kills route if PIE already propagates uncertain physical boundary sets |
| PIE-D, AAAI 2025 | delay-aware concurrent execution; one current state and no-delay dummy prediction | primary baseline | kills route if Dummy Simulation is proved a sound representative for all uncertain boundary states |
| MAPF-DP/MCP | safe execution of a fixed feasible plan under no-start delays and action dependencies | execution baseline; E68-D must reduce to it | kills route if Candidate 68 is only another dependency graph executor |
| ADG-style execution | precedence scheduling and robust execution of a fixed plan | nearest protocol-level comparator | kills route if no theorem depends on concurrent planner boundary uncertainty |
| UM*, ICAPS 2017 | belief-space planning under pose uncertainty and chance constraints | handles uncertainty throughout planning and may replace the planner | kills route if Candidate 68 requires full-horizon belief search or changes PIE's path choice |
| Stochastic travel-time replanning, AAMAS 2023 | continuous random travel times, Bayesian parameter updating, online path replanning | probability-learning comparator | kills route if Candidate 68's only content is learning another delay distribution |
| Safe MAPF with time uncertainty, JAIR 2021 | plans safe temporal trajectories under uncertain durations | temporal-uncertainty comparator | kills route if the envelope is merely a known temporal interval converted to reservations |
| Robust and effective MAPE with timing uncertainty, AI 2026 | dynamic robust execution under unexpected timing delay | current robust-execution comparator | kills route if it already combines the same boundary envelope, exact PIE refinement, and compression theorem |
| POD, RAS 2026 | typed protocol-observation discrepancy and recovery for resource coordination | strongest observation/protocol neighbor | kills route if full text contains the same PIE commit-boundary reachable-set object and theorem |

Candidate 68 may claim no novelty until every route-killing test is resolved against primary full text.

## 21. Strongest defensible journal claim

The candidate claim, if the theorem ladder succeeds, is:

> For PIE-style concurrent MAPF execution with uncertain processing completion and unreliable endpoint feedback, collision-safe acceptance of exact PIE actions can be reduced from universal reasoning over joint commit-boundary configurations to a compact event-and-resource envelope on a characterized nontrivial class, while reverting exactly to PIE-D when the envelope is a certified singleton.

This claim is falsified if:

- a prior primary source already proves the same result;
- the true boundary state cannot be contained under implementable evidence assumptions;
- exact checking requires joint-state enumeration on all useful instances;
- the resource projection rejects essentially every contested MOVE;
- safety requires an alternative MOVE or planner replacement;
- singleton inactive behavior cannot preserve baseline bytes;
- nontrivial progress cannot be shown even under explicit eventual-synchrony and fairness assumptions.

## 22. PIE inactive bitwise-identity contract

The future mechanical check must compare baseline PIE-D and wrapper-inactive executions using identical:

- planner input bytes;
- committed path bytes;
- proposal order;
- action-vector bytes;
- task disclosure sequence;
- random source state, if the baseline consumes randomness.

The wrapper is inactive only when:

- the boundary envelope is singleton;
- that singleton equals the baseline boundary state;
- observations and epochs are consistent;
- there is no unresolved physical occupancy;
- every resource guard is already satisfied.

Inactive mode may add audit metadata outside the compared action/planner-input channel, but may not modify baseline decision bytes.

## 23. Triggered-refinement mechanical contract

For every activated decision, a future verifier must establish:

- baseline proposal digest;
- envelope digest;
- triggering MAY/MUST occupancy or evidence-conflict witness;
- exact output digest;
- proof that each unchanged MOVE equals the corresponding PIE MOVE;
- proof that each changed discrete action is MOVE to WAIT;
- proof that WAIT has SH-STATIC, SH-DYNAMIC, and SH-BRAKE evidence;
- proof that no alternative MOVE appears;
- transaction and epoch lineage;
- whether progress assumptions currently hold.

Containment of an already in-progress edge transaction is logged separately and is not presented as a newly selected MAPF MOVE.

## 24. External baseline and reproducibility contract

No baseline is accepted merely by paper title.

At least one published external comparator must have:

- official paper or author manuscript;
- official source artifact or a documented absence;
- fixed repository commit or immutable release;
- license compatible with the planned use;
- build entry;
- minimal original-method test;
- read-only audit of the actual extension seam;
- a preregistered mapping from its outputs to common metrics.

Candidate baseline families are MAPF-DP/MCP, ADG-style robust execution, UM*, and stochastic-travel-time online replanning. Selection remains OPEN.

## 25. PIE official R0 read-only audit contract

Before implementation, the PIE/PIE-D baseline gate requires:

- official paper URL and DOI;
- official repository URL;
- fixed commit or immutable version;
- repository license;
- build entry;
- original minimum test invocation;
- expected untouched output contract;
- exact planner/executor/dummy-simulation extension points;
- proof that the frozen upstream artifact is not modified;
- record of any missing build or license evidence.

The currently discovered repository page is not sufficient to close this gate. No fixed commit has been selected in this candidate.

## 26. Pre-registration contract

No numerical parameter is selected here.

### 26.1 Comparator regimes

Results must separate:

- strict same-compute comparison;
- natural-runtime comparison;
- inactive identity comparison;
- triggered refinement comparison;
- safety-only degradation cases;
- conditional-liveness cases.

### 26.2 Independent sample unit

The independent unit must include an independently generated or selected map/task instance and an independently selected execution/observation trace. Repeated time points, agents, or resource events inside one run are not independent replicates.

### 26.3 Failure denominator

Every launched unit remains in the denominator, including:

- planner failure;
- timeout;
- deadlock;
- protocol nontermination;
- safety containment;
- unresolved partition;
- invalid output;
- infrastructure failure, reported separately but not silently deleted.

### 26.4 Stopping and censoring

Stopping, right-censoring, infrastructure exclusion, retry, and corrupted-artifact rules must be fixed before any main run. No condition may be removed because its outcome is unfavorable.

### 26.5 Public sources

Map, task, processing-latency trace, no-start-delay trace, and observation-error trace sources must be public or generated by a frozen public procedure. Source selection remains OPEN.

### 26.6 Metrics

Metric definitions must distinguish:

- physical collision;
- logical resource conflict;
- unsafe entry prevented;
- false-positive suppression;
- total and per-cause WAIT;
- unresolved containment;
- throughput or completion performance;
- planner runtime;
- protocol runtime;
- active-decision fraction;
- starvation and tail waiting;
- envelope size and compressed-state size;
- conservative rejection caused by lost correlation.

No expected direction or numerical effect size is recorded.

## 27. Qualification card

| Gate | Required closure evidence | Current state |
|---|---|---|
| Q68-1 Plain-language problem contract | independent reviewers agree the question is precise and not delay relabeling | OPEN |
| Q68-2 Published anchors | at least two primary published anchors verified and difference claims accepted | EVIDENCE-AVAILABLE / REVIEW-PENDING |
| Q68-3 PIE official R0 | URL, fixed commit/version, license, build entry, minimum original test, extension seam | UNKNOWN |
| Q68-4 External baseline | official artifact/version/license and minimum reproduction plan | UNKNOWN |
| Q68-5 Data and scenarios | public map/task/trace sources and independent-unit construction | UNKNOWN |
| Q68-6 Simulation evidence chain | preregistration, immutable manifests, denominators, stopping/censoring, provenance | UNKNOWN |

No row marked EVIDENCE-AVAILABLE is a PASS. All six gates must be explicitly accepted before implementation or a main experiment.

## 28. Ordered pre-experiment closure sequence

1. Resolve the POD and 2026 robust-execution full-text overlap risk.
2. Define the resource-separable event-DAG class and either prove or reject T68-COMP.
3. Complete all counterexample traces and impossibility proofs.
4. Complete the PIE official R0 read-only audit.
5. Complete one external baseline artifact/version/license/minimum-reproduction audit.
6. Freeze data, task, processing-latency, no-start-delay, and observation-error trace provenance.
7. Freeze strict same-compute and natural-runtime protocols.
8. Freeze failure denominators, stopping, censoring, retry, and exclusion rules.
9. Specify the inactive and triggered mechanical verifiers without implementing them.
10. Submit the exact Candidate 68 identity sequentially to research-mentor, Nature reviewer, and no-skill independent logic review.
11. Root-integrate every bearing objection. Any substantive correction requires a new number and new bytes.
12. Perform a requirement-by-requirement completion audit.

The sequence is dependency ordered. Later evidence cannot retroactively excuse an earlier open gate.

## 29. Review protocol

Each formal review must record:

- exact candidate filename;
- candidate SHA-256, byte count, and line count at registration;
- registration hash;
- review-start identity check;
- proof of complete candidate reading;
- review-end identity check;
- nonempty report;
- explicit bearing-objection list;
- OPEN/CLOSED and BALLOT/NONBALLOT status.

A report with empty output, API failure, incomplete reading, changed candidate identity, or missing end check is invalid.

The research-mentor review must occur first, followed by Nature reviewer, followed by a reviewer explicitly using no skill. Root acceptance occurs only after all valid reports exist.

No reviewer can override a bearing objection from another reviewer. A bearing objection forces a new-number successor.

## 30. Claude Opus boundary

Claude Opus may provide constructive architecture ideas only as NONBALLOT consultation. A complete, nonempty, identity-matched actual receipt is required before any such advice can be cited.

Transport failure, timeout, empty output, or a still-running session is not scientific evidence and is not a review.

## 31. Protected symbols

The following remain unassigned:

- H
- T_delay
- B_CAL
- B_max
- B*
- P_active
- density N

No value, range, default, prior, hint, or tuning direction is implied.

The PIE commit length and every timing quantity also remain symbolic in this candidate.

## 32. Current decision

Candidate 68 is a technically plausible journal route because it targets a verified single-state assumption in PIE-D and separates itself from action-failure relabeling.

It is not yet established as novel, sound, complete, useful, reproducible, or implementable.

Final state:

HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT

