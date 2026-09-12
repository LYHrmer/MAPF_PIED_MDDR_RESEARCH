# C26：确定性计算模型建设咨询完整回执

2026-09-12；根实际调用，CONSTRUCTIVE / NONBALLOT。仅发送同号PROMPT的自包含设计问题；无工具/技能/MCP，不冒称Claude全读主稿。

唯一正常升级调用exec41716，终态chunk9a20b1/exit0。实际is_error=false、terminal_reason=completed、stop_reason=end_turn；客户端modelUsage为claude-opus-5/firstParty；session_id=7623d557-ec16-44b2-8c4a-1ff6914f69cb、duration_ms=101975、费用0.20266050000000002 USD。完整原stdout另存同号RAW_RESPONSE.json。正文1706空白分词，真实END-C26-20260912，不因成功返回计设计通过。

## 完整原文

<!-- BEGIN_C26_RESULT -->
# C26 — P_model: a declared deterministic simulated compute law

## 0. Route decision

I accept the successor law. I **reject the source-only nonpreemptive real-elapsed alternative**, for one precise reason: its seal row is a *measured host quantity*, so virtual Q becomes a function of temperature, caches and prior arms. That destroys the claim that the block trajectory is a deterministic `F_a(X_b,Z_b)`, and with it the independence derivation in §4 — randomized arm order cannot repair a broken determinism, only average over it. It also leaves guard/release charging unattributable, since a mid-guard cost belongs to no row supply.

**Smallest coherent alternative:** keep that proposal's *sealing and revocation discipline* verbatim — results and new private state invisible until an originally permitted strict successor row; cancellation revokes output but never undoes consumed supply or private source history — and replace only the *seal-row determination*, from measured elapsed to exhausted simulated ticks.

## 1. The semantics (M1)

**Normative model.** M1 is a deterministic finite-word RAM: fixed word width, finite addressable store, explicit instruction set over the declared representation domain (finite algebraic expressions, finite containers, variable-length semantic IDs/epochs, immutable state roots). M1 is *normative*; a portable VM may later only *instantiate* it, by refinement (§2).

**Unit.** One **tick** = one M1 primitive step. All deployment algorithm, source, control, querying, planning, geometry, scoring, failed attempts, communication, index maintenance and first/reused preparation are charged in ticks. Each writer (central server, per-agent server, planner source server, task-snapshot server, each declared comm server) has its own finite per-row tick supply and its own meter instance.

**Charge-before-step.** Before an op's effect, supply `s` is decremented by `c(op, paid size arguments)`. If `s < c`, the op does not occur, state is unchanged, `s→0`, and the outcome is EXHAUST (§2).

**Pause/continuation.** Every deployment computation is a resumable continuation reified at instruction boundaries only. Pausing is never observable to the paused program except through the chrono import (§2). Resumption occurs on the next originally permitted strict successor row with fresh supply. FIFO and the one-slot-per-writer publication rule are unchanged.

**Size-dependent work.** No macro. An op is admissible as a primitive only if its cost is a function of quantities **already decoded and paid for** in charged state — a container length, a limb-count header, a segment arity are each *paid field reads*. Anything whose cost depends on an undecoded value must be expressed as a charged loop over a paid iterator, one charge per iteration: variable-length ID/epoch comparison charges per atom (early exit allowed, each compared position charged); copying charges per word; scans charge per element; big-integer arithmetic charges per limb; certified numeric refinement charges per interval step; hashing/crypto charges per block; geometry charges per predicate evaluation. A **bounded reference with constant abstract access cost** is legitimate only inside a declared representation domain whose encoding size has a declared constant bound, and that membership must be *checked by a charged validation at CAPTURE*, never asserted.

**CAPTURE / publication.** `CAPTURE` is one charged op yielding an opaque token pinning a root/time reference; pinning levies a charged per-row retention fee, and query-induced retention/GC is charged to the querying writer. Public row arrival yields an opaque token only; decoding it is charged. Publication is a charged op that completes on its row or fails (§3).

**Why the meter neither recurses nor hides work.** The meter is an explicitly **ideal administrative facility**, not an M1 program, so it is not itself metered — no recursion. Its declared domain is exactly (op label, size arguments already present in charged registers, current supply). Invariant: the meter may not read heap or business state, may not rank or select among pending candidates or agents, and may not branch on world truth. Hence no free business information can flow through it. Its actual host cost is measured and reported separately, alongside wall/CPU/memory.

Host imports are not exempt: each import is a declared subroutine with a per-call **and** per-size tick schedule. An unpriced import is a design defect.

## 2. Chrono, RNG, persistence, scheduling, failure taxonomy

**Chrono.** `now()` is a charged import returning the *current virtual row time from O*, inclusive of queue and pause intervals. Real elapsed never enters any charged computation, any Q, or any source branch choice. Every native clock read in R0 and in the H19 ECBS source must be explicitly mapped to this import; an unmapped clock, RNG, environment, address or locale read is a **qualification failure**, not a tolerated detail.

**RNG.** R0's source-local MT initialization performed by original code stays source-local; the C PRNG state is part of the persistent private session, seeded from a declared deployment seed word (value unassigned), advanced only by original code. H19's ECBS keeps its own job state and callbacks and inherits no R0 rule by name.

**Persistence and barriers.** Every complete normal call advances the private session even if its result is later stale or rejected: the session is a monotone deterministic transducer. Revocation suppresses output only. Source→centre visibility requires a publication op on a strict successor row; the centre's disposition is a separate charged event and never rewinds the source.

**Scheduling.** Preemption at instruction boundaries within simulated supply. This alone removes real elapsed from Q.

**Qualification route, and what stays unproved.** Strongest plausible path: compile R0 and the H19 source to a portable VM; require (i) instrumentation whose count is a proved refinement of M1 ticks, (ii) every native callback replaced by a metered import, (iii) stop/resume at instruction granularity with a token-bound outer loop. **Unproved today:** that Wasmtime fuel (or any counter) equals or refines M1 ticks, that it charges expensive native callbacks, that the full C++ dependency set is supported, that a closed token-bound stop/clock interface exists, and that the sources are free of UB and of non-strict-weak-ordering comparators. Those last must be discharged by source evidence — sanitizers, comparator audits, index-domain and empty-target repairs — because writing "deterministic" cures nothing. No VM port is claimed to have passed.

**Four distinct outcomes.** (a) **EXHAUST**: supply reached zero; continuation live; no fault draw; no new public row; resumes later. (b) **SOURCE_EXCEPTION**: contract violation or raise; continuation destroyed; agent to declared safe HOLD; spent ticks retained; scored as algorithm failure. (c) **EVIDENCE_HOST_FAILURE**: simulator/harness OOM, crash or deadline; block score is **MISSING, never zero**, and never reclassified as (a) or (b). (d) **ADMIN_SHUTDOWN**: cutoff row; predeclared partial-block rule applies.

## 3. Current-row acceptance

At acceptance row *r*: charged read of the current physical reference mode and the exact local reference segment; charged variable-length guard computation; charged admission decision. Command-version equality is never sufficient, because continuous progress and autonomous END advance at their fixed virtual times — the segment must be revalidated at *r*.

**PARTIAL_GUARD.** If supply exhausts after an affordable CAPTURE but before the guard completes: no motion is authorized; no new public row; no retry-fault draw; the pinned token and *all* spent work are retained in the private continuation; the attempt watermark advances so the same guard cannot later be decided on stale data. Retry on a permitted later row must recompute every dynamic component from a fresh mode/segment read. A stale dynamic guard is never reusable. Not every guard decomposes into prior work plus one pointer comparison; where it does not, the recomputation is charged in full.

**Invariants.** No motion without a guard completed on the admission row; single-writer ownership; irreversible END; release only of resources proved behind the same MOVE; no invented detour or goal; finishing the MOVE, informing the centre, consuming READY and advancing the cursor remain four distinct events.

**Nonvacuous symbolic admissibility.** Obligation: exhibit supported input classes and capacity assignments (values unbound) for which every required guard provably completes within one row's supply — e.g. guards whose length is bounded by the declared representation domain's constant bound. A model in which all requests are permanently pending is admissible but is *not* a useful study and does not discharge this obligation. Finite global O bounds repeated failed checks, so no infinite execution arises.

## 4. Independence, scalability, scope

If the completed block trajectory is `F_a(X_b,Z_b)` with `F_a` deterministic and `Z_b` independent across blocks, then arms within a block share `Z_b` and may be dependent, while block innovations are independent — so Δ's summands are independent given X and θ = E_P[Δ|X] is well posed under predeclared weights and bounded Q.

**Leakage that would invalidate this:** measured elapsed; host clock/RNG/environment; allocator addresses or address-keyed iteration order; uninitialized reads; floating-point mode or FMA differences; memory-pressure-dependent branching; state carried across blocks or across harness restarts; and host OOM silently reclassified as simulated algorithm failure.

**Throughput vs scalability.** Ticks per row is an abstract model capacity; wall time and memory are host scalability. Both are reported; only the former can touch Q.

**Scope lost:** any claim that θ under P_model equals θ under real-host P, byte-for-byte nativeness, or native performance engineering conclusions. **Retained:** net task benefit of D-S vs R-S (primary) and D-S vs E0 (mandatory), and the H19 comparison, under limited computation and genuine bounded transverse error — with the compute limit now a declared law rather than a measured one. Fixed roster, pairs, weights, E and primary comparisons unchanged; no post-outcome filtering, weakened R, or retrospective weights.

**STRICT vs NATURAL** remains meaningful and becomes cleaner: STRICT charges the declared upper bound before the op; NATURAL charges ticks actually consumed. Both in the same unit; a preregistered model sensitivity analysis over tick rates may not use outcomes to select rates.

## 5. Adoption checklist

**Closed design clauses.** M1 as normative semantics; tick unit; charge-before-step; instruction-boundary preemption with private continuations; no unpriced import; size-dependent costs only from paid size arguments; ideal meter with no-business-read and no-selection invariants; charged CAPTURE/retention/GC; sealing-and-revocation discipline; four disjoint outcomes; PARTIAL_GUARD rule; acceptance revalidation; MISSING ≠ 0.

**Required source/adapter evidence.** Complete map of clock/RNG/env reads in R0 and H19; UB and comparator-ordering audit; ownership, empty-target and index-domain repairs; adapter proof that it only certifies starts, caps monotone within-MOVE progress, brakes/HOLDs, and releases behind the same MOVE; representation-domain bound proofs for every constant-cost reference.

**Later implementation qualification.** VM-to-M1 refinement proof; metered callbacks; token-bound stop/resume; dependency support; cross-platform bit-identical replay.

**Actual hypotheses to test.** θ(D-S vs R-S) > 0; D-S vs E0; H19 comparison; internal spatial-release vs cap-reservation ablations; tick-rate sensitivity.

Nothing here authorizes implementation, parameter binding, or an experiment GO.

END-C26-20260912
<!-- END_C26_RESULT -->

## 根独立分析与取舍

1. 采纳的方向仅为明确后继P_model：全部部署计算由确定性模型计费、宿主CPU/wall/memory另报。它是执行环境分布的实质变更；既不证明旧real-host theta等值，也不由顾问自行“accept”而生效。实际采纳由根整合稿决定。
2. 拒绝“只改seal-row、撤权照搬”口径：恢复可暂停源与删除非抢占体，源取消/异常/部分调用的继续权限也必须重新定义；不能保留P29 REVOKE_AND_DRAIN又声称逐指令立即暂停。
3. 不采纳费用不足时s→0。未执行容量不是NATURAL实际工作，保留未用供给/闲置账；STRICT按原公共供给预付，不是顾问写的每操作事前上界。计量设施为显式数学规则，宿主成本不为零。
4. 其M1仍缺完整primitive及导入覆盖，尤其“每geometry predicate/interval step收费”不能隐含任意位复杂度恒价。固定字运算、变长展开、内存分配/增长、导入/证明验证及最终发布的完整归属必须先写清，不将本件closed checklist视为已闭。
5. CAPTURE固定有界引用可采用，但表示域资格不能每次先免费判业务成员；有界引用编码应由合法已存在表示不变量保证，无法建立的不读。可变语义标签不降为固定指针相等。引用专用保留/GC照实际需要收费，不强制无工作每行付固定人工税。
6. 明确拒绝PARTIAL_GUARD推进attempt watermark。尚未完成实际处理的本行耗尽不消费水位、不抽新故障、不生控制效果；已付工作不退、动态根下次重捕获。过期防护来自后继行freshness/原身份，不能用消耗水位补。
7. 明确拒绝SOURCE_EXCEPTION让agent安全HOLD或将所有异常计算法失败。源会话停止不替已接纳物理段制动；模型内可定义源失败保实际物理服务，源UB/映射不闭是不可推断，宿主证据失败是未知，不能混为分数零。
8. 接受确定映射F_a(X_b,Z_b)加独立Z_b的数学独立性推论；需要实际无host泄漏和无跨block可变状态。当前未运行且没有对完整源/VM给资格通过，也不要求跨所有平台无条件bitwise相同。
9. 容量与输入的非空可用域仍须构造；大而固定表示域本身不证明当前行能完成guard。未实现不能单独当FAIL，但定价/权限缺定义不能都推给未来测试。

原调用已结束，无本题活句柄。仅科学建设材料；未实现/伪代码/测试/仿真/数据/保护参数赋值，不修改旧件或自动更新资格门。
