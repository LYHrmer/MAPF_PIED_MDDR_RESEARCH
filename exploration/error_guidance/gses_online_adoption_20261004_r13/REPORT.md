# R13: actual author suffix-graph adoption during primitive execution

All 24 real author calls returned within the registered budget and supplied a different graph that passed the adoption guard. All 24 changed full execution traces; the 12 original continuations and 24 adopted continuations passed local event/resource checks. This closes the specific R11 gap between same-graph checkpoint restore and actual different-graph adoption. It does not establish general planner superiority, original-feedback-controller equivalence or lifelong MAPF.

Two existing author instances, random60 and warehouse110, each use public checkpoints1/2 and5/2 and three unchanged primitive profiles. The 12 contexts are mechanism conditions, not12 independent heldout tasks. Their paths and original type2 relations come from the frozen R10 author exports. There was no case substitution, model training, outcome tuning, additional solver search or changed physical profile. Source registration precedes all24 calls; all43 compiled author source/header files remain unchanged.

## Actual data and execution boundary

At the checkpoint, the simulator serializes a full private continuation state and a separate allowlisted public author input. Only the latter is passed to the author executable. It contains actual ARRIVE states, current action identities/occupancy, known paths and unsatisfied dependencies. Active MOVE remains at its from-state. Public initial hold minus elapsed time gives a rounded nominal residual hold; all future search edges have unit weight. Private queued finish times, future segments/profile and pauses are excluded. Search weights never override physical primitive durations.

The unmodified author make_switchable fixes outgoing edges at current+1. Already satisfied incoming constraints of active movements are removed from the suffix optimizer and restored with their original directions when lifting back to the full graph. The guard preserves every canonical dependency family, full paths/type1 ordering, completed transitions, active incoming constraints and satisfied orientations, and checks the complete DAG. It then replaces the real executor graph/dependency map while every other state field, event queue, reservation and committed segment remains unchanged. Downstream MOVE_START records use the new dependency map.

These checkpoints declare present controller/reservation state public. That assumption is distinct from implementing the main line's paid-information contract. The solver transaction freezes virtual time; actual host grouping/search/subprocess durations are preserved, not inserted as robot motion delay. The experiments therefore do not establish a real-time asynchronous planning benefit.

## Full registered results

Each cell is sum completion time / makespan. Values are exact quarters or halves in these profiles; raw fractions remain in RESULTS.json. The primary descriptive outcome is completion sum; makespan is reported without omission.

|Author case|Checkpoint|Profile|Original continuation|GSES adoption|Improved GSES adoption|
|---|---|---|---:|---:|---:|
|random-32-32-10|1/2|primitive_nominal|2085.75 / 77.25|2042.75 / 79.5|2043.75 / 79.5|
|random-32-32-10|1/2|axis_slow|2362 / 87.5|2341 / 90.5|2345 / 90.5|
|random-32-32-10|1/2|midpoint_pause|2172 / 79.5|2133.5 / 83.25|2133 / 83.25|
|random-32-32-10|5/2|primitive_nominal|2085.75 / 77.25|2032.75 / 79.5|2032.75 / 79.5|
|random-32-32-10|5/2|axis_slow|2362 / 87.5|2327 / 90.5|2326 / 90.5|
|random-32-32-10|5/2|midpoint_pause|2172 / 79.5|2122.75 / 83.25|2121.25 / 83.25|
|warehouse-10-20-10-2-1|1/2|primitive_nominal|16489.25 / 310.25|16493.75 / 310.25|16504 / 310.25|
|warehouse-10-20-10-2-1|1/2|axis_slow|20832 / 387.5|20827.75 / 387.5|20831.25 / 387.5|
|warehouse-10-20-10-2-1|1/2|midpoint_pause|17218.75 / 323.75|17225.5 / 323.75|17235.75 / 323.75|
|warehouse-10-20-10-2-1|5/2|primitive_nominal|16489.25 / 310.25|16485.25 / 310.25|16485.25 / 310.25|
|warehouse-10-20-10-2-1|5/2|axis_slow|20832 / 387.5|20819.5 / 387.5|20819.5 / 387.5|
|warehouse-10-20-10-2-1|5/2|midpoint_pause|17218.75 / 323.75|17235.75 / 323.75|17226.5 / 323.75|

Across the24 adopted continuations, completion sum improves18 times and worsens6 times. All12 random60 continuations lower the sum but increase makespan; all12 warehouse110 continuations keep makespan, with six sum gains and six losses. Therefore changed and legal adoption does not imply a better primitive objective. Examples of retained regressions: warehouse at1/2 nominal costs +4.5 for GSES and +14.75 for Improved; midpoint costs +6.75/+17. At5/2 midpoint the sum increases +17/+7.75. These are signed consequences of the same real author methods under the registered execution adaptation, not solver failures to be discarded.

The existence of both better and worse legal outcomes supplies a concrete future value-selection question. No model chose these results in R13, no full candidate-set optimality is claimed, and primitive truth did not enter the author inputs. A subsequent model must compare complete legal continuations using only the declared decision-time information and fresh TRAIN/TEST data.

## Safety, fallback and reproduction

All36 local audits independently reconstruct event/resource state and dependency versions. They retain destination geometric entry at2/5 and source geometric exit at3/5, midpoint state nonadvancement, TURN/STATION residence and goal holding. The independent root dynamic-dependency/resource/continuous audit passed; ROOT_AUDIT_BINDING.json pins its exact source and output.

MECHANICS.json retains seven rejected corruptions, exact same-graph checkpoint continuation, exact rejected-candidate fallback and exact fallback under injected Timeout/HostTimeout/AuthorError statuses. The altered-current control can fail earlier structural validation, and the commitment control uses a genuine author reversal against an explicitly protected target transition; these are not independent physical samples. The explicit-cycle control directly exercises the DAG checker. There were zero natural timeouts, rejections or author errors in the24 scientific calls. Injected timeout handling must not be reported as a naturally observed timed-out solver run.

Changing only private queued future times, future geometric segments and the private profile leaves the serialized author input identical. This tests the implemented message boundary; it is not a proof of arbitrary external noninterference.

The48 raw gzip members contain36 complete execution traces and12 serialized checkpoints, totaling44,495,082 bytes. AUTHOR_SOURCES.tar.gz contains43 pinned original compilation files and the MIT notice is preserved. `reproduce.py --build` reconstructs the author adapter offline from the archive and checks byte-identical ELF output. `reproduce.py --replay ID` resumes a stored checkpoint and compares the entire emitted trace, not only summary metrics; it does not launch a new author optimization or count as another scientific instance. REPRODUCTION.json records checks actually performed. Absolute historical paths in registration record provenance; replay inputs are included locally.

This is a finite fixed-path dependency-ordering interface with piecewise affine geometry, instantaneous velocity changes and synthetic per-vertex station stress. It does not independently certify map-obstacle clearance, acceleration/tracking dynamics or hardware. It does not issue new tasks, learn a policy, alter paths, implement LMAPF or use the original ARGoS continuous controller.
