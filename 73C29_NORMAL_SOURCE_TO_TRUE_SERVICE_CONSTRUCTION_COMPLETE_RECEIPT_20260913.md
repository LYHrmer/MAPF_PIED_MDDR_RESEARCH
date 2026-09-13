# 73C29：正常源到真实服务建设完整回执

2026-09-13；CONSTRUCTIVE / NONBALLOT。用户的一小时等待期已过，根实核 04:00:25 UTC 后启动本次唯一调用。输入为同名前缀 PROMPT 文件；归档文件含文本末尾换行，实际 CLI 提示为该正文去掉最后一个文件换行，未使用工具/文件读取或 MCP。请求 Opus/high；实际模型与终态见下。

实际 exec session 87486，启动 chunk 2c8606，最终 chunk e7dc72 / exit0；CLI session 03b25942-db6c-4be2-843e-aebf5e7b58f2；modelUsage 为 claude-opus-5 / firstParty；terminal_reason=completed、stop_reason=end_turn、is_error=false；duration_ms=136290，客户端费用 0.2778725 USD。正文末尾 END_C29_CONSTRUCTION 完整。此前待回不算完成，实际完整建议也不是正式审查通过票。

根已经完整读取并作第一轮独立取舍：
- 采用“原终点服务区包含 v+F+Z”的充分条件和真实非零空间误差应保留的要求；这是当前 §3/8 条件的直接应用，不声称新论文贡献或公开地图已合格。
- 采用把付费知识、源正常返回、合法授权/启动、有限 END、原 TASK_SERVICE 分开证明的建设方向；C29 给出的依赖图本身尚不能入稿为完成证明。
- 明确拒绝“拓扑排序使每行容量需求为1”：一个作业可能有变长几何/认证/复制及完整当前 guard，必须逐基本步给有限界，并单独满足同原行完整 guard 和发布容量。一个图节点不是一个基本步。
- C29 把中心 append MOVE 与 b=ell 授权合并，又把 PRECHECK 放进 ACTUATOR 当前检查；两者都不符合现合同。append 后必须经过本地 PRECHECK 证据与中心准入、grant/控制消息接入；ACTUATOR 只核现有命令的当前接纳条件。CURSOR/任务快照的请求、通道和回程也不能省。
- 拒绝外部 H19 “without any PLAN_CHECK/PRE_COMMIT/CAS”的笼统删除：§10 有自己的 PLAN_CHECK、规划返回验证、cut/合图/提交规则。它不支付 R0 专属函数，不等于无需付费规划接纳。
- G3 要求补定义的虚拟 clock 原始起点/转换与同 t 后继行，当前 §9 已明定；不能作为新缺口反复开题。G1 可以是条件引理的外生尝试位前提，不需要额外未来 bit 读取接口或新 roster 筛选规则。
- “闭包含单调所以非空”不足以证明栅格、所有起点/整段瓦片占有、时钟/队列/同原 O 和源分支联合可满足；A1 非相邻起点也不足以保证完整扫掠包络分离。有限源工作仍须根直接源码证明，原输入对象及实际参数未实例化。C29 自述 incomplete 是实际结论，不能截取末段当已闭合见证。

根将结合固定源码和已有合同继续建设同一主稿，尚未由本件放行设计、实现或实验；完整目标保持未完成。不修改顾问正文以隐藏错误。

## 原始完整正文

## 0. What this is

A conditional witness construction: a symbolic subfamily 𝔽 plus an explicitly incomplete satisfiability argument. All symbolic conditions below are **non-experimental feasibility predicates**, not assignments to H, T_delay, B_CAL, B_max, B*, P_active or density N. The R0 planner branch is used only as a **candidate still pending root-independent source-code verification**. No completeness, no positive effect, no roster claim.

## 1. Subfamily predicates (all finitely representable)

𝔽 = inputs satisfying, simultaneously:

- **(A1)** finite connected 4-grid, obstacle outer boundary; finitely many pairwise non-adjacent starts; each agent one unique adjacent first goal; goals distinct and on no start.
- **(A2)** initial world in legal BOOTSTRAP HOLD with true assigned tasks; for each agent the assigned head is legal and no committed path exists, hence PROJECT ≠ ∅ at the first PLAN_CHECK; head goal ≠ start, so no initial-Q shortcut exists and a genuine MOVE is required.
- **(A3)** for the distinguished agent i₀ with reference edge u→v, ell>0: the **clearance predicate** of §2 holds for the swept envelope and for the endpoint tile.
- **(A4)** install/grant choose C = b = ell (full ordinary initial authorization, GROUP_PREFIX-permitted, not a different algorithm), so an endpoint END is reachable at all.
- **(A5)** the ledger head j of i₀ in the true ledger A has vertex = v and ServiceRegion(j) satisfying §2.

𝔽 is non-empty as a predicate set, not by exhibiting data: every constraint is a closed containment between finitely represented bounded sets, monotone in ServiceRegion and in tile clearance; since ell>0 and F, Z are bounded, containments are attainable by any representation whose clearance exceeds diam(F ⊕ B). I am not generating such a map.

## 2. Service sufficiency retaining non-zero spatial error

B := ∏ⱼ[−z̄ⱼ, z̄ⱼ] is forward-invariant for ż = −κz + w with |wⱼ| ≤ κz̄ⱼ, and z is never cleared at edge change; hence for all t, X(t) ⊆ (u + s(t)e) ⊕ F ⊕ B, and during endpoint residence X(t) ⊆ v ⊕ F ⊕ B, a non-degenerate set.

**Sufficient service condition (S):** ServiceRegion(j) ⊇ closure(v ⊕ F ⊕ B).
**Sufficient legality condition (L):** the swept envelope ⋃_{s∈[0,ell]}((u+se) ⊕ F ⊕ B) is obstacle-free and shares no closed tile boundary with any other agent's occupied envelope on that row.

(S) is what makes "reference zero speed ≠ entity zero speed" harmless: containment is asserted for the whole tube, not for a nominal point. (L) is why non-adjacent starts alone are insufficient — the clearance is on F ⊕ B, not on tiles.

## 3. Finite billing dependency DAG (over existing opportunity types only)

Nodes are (type, role instance, purpose); every edge is "strictly later row", by the new-work-visibility rule:

INIT → CURSOR (c evidence) → TASK_REQ → CAPTURE at Srv_A (opaque root+time first, field decode/derivation billed after) → NETWORK(channel) → Srv_C verification ⇒ K_task; {c, Kc, K_task} → PLAN_CHECK (all Kc ≥ S, no job, PROJECT ≠ ∅) → Srv_P slices via PROCESS_SLICE(Srv_P) → PRE_COMMIT_SHAPE → planner_commit → Srv_C re-check of latest PROJECT/version/anchor + CAS admission ⇒ MOVE(b=ell) → POLICY(role,i₀) → ENTRY(i₀,kind) → ACTUATOR(i₀) with full in-row re-capture PRECHECK ⇒ RUN admitted ⇒ START (delay-bit access) → control to C over finite T_ref → END at v → TASK_SERVICE(i₀) row: A's head j has vertex v, X(t) ⊆ ServiceRegion(j), not Stopped, one service on that agent row, then atomic replenishment (new task not served on the same row).

The graph is acyclic: every edge is forward in row order and no prerequisite is reachable from its consumer. QUERY, COORDINATE, MODE, FAULT, CUTOFF, STOP, END_LOCAL_RETRY, READY_CENTER_RETRY, GROUP_RETIRE appear only as *non-preemption* obligations, not as producers.

## 4. Where the finite compute bounds come from

Not from "everything is finite". Concretely: (i) import of the finitely represented instance is billed per word, so its cost is a function of the representation length, not a constant; (ii) each envelope/containment test is billed as (polygon vertex count) × (arithmetic steps of the interval test), never as one unit; (iii) CAPTURE decode is billed per decoded field, copies/containers/logs/GC per element; (iv) planner work is bounded **structurally**, not by wall clock: under (A1) the first PIBT step sends each agent to its own adjacent goal with no vertex/swap conflict, the second high-level iteration terminates because the configuration is the goal configuration, and LNS padding to commit_step is a finite terminal-residence extension.

(iv) is load-bearing because of the clock contract: chrono now is the virtual t via duration-period floor, the first plan overrides time_limit=1 and builds the LaCAM deadline as (time_limit−0.1)·1000, and Deadline fires on elapsed_ms > limit. If planner slices run at one virtual t, elapsed stays 0, the deadline never fires, and only the structural exit prevents illegal infinite same-t work. If virtual t advances across slices, the floor encoding can instead make the deadline fire and kill the plan. So 𝔽 must also carry the symbolic condition **(C-clock): the total billed planner steps are admissible at Srv_P capacity within the rows available before the floor-encoded elapsed exceeds limit.**

## 5. Row / publish / queue / guard constraints

Each row: physics and autonomous events, then publication of prior-row completion units under finite publish capacity by job key, then the row's own type. Consequences: (a) every cross-station handoff in §3 costs at least one row of latency, and Srv_C serializes CAPTURE verification, CAS admission and publication on one FIFO slot each; (b) same virtual t may host strictly-later rows with no epsilon, so the chain may compress in time but not in rows; (c) the ACTUATOR opportunity rank counts **all** opportunities including empty ones, so chain length selects which delay-table position START reads; (d) the PRECHECK re-capture must fit inside that ACTUATOR row's capacity with no virtual-time advance and no interleaved writer — on failure fees are kept, no effect, no watermark consumption, retry at the next eligible row; (e) T_ref must contain no HOLD/BRAKE/MODE/FAULT/CUTOFF/STOP for i₀ and the ACTUATOR guard must admit within the agent's control capacity.

## 6. Joint satisfiability — what is proved and what is assumed

Proved: the constraint system is *structurally* consistent. The dependency graph is a finite DAG; any topological order with one job per station per row meets per-row capacity demand 1; the geometric conditions (S),(L) are monotone closed containments compatible with (A1); (A4) makes END reachable; (A2) makes the first PLAN_CHECK legal and forbids the initial-Q bypass; §4(iv) gives termination without relying on the deadline.

Not proved, and I am not claiming it: three premises are assumptions on given objects I may not construct.

## 7. Minimal necessary design revisions

- **(G1) delay position.** The construction needs the bit actually read at i₀'s realized ACTUATOR rank to permit start. There is no second no-start draw and no future-bit API. Minimal revision: define a named predicate "start-permitting position at rank r" and license conditional lemmas indexed by it, with an explicit prohibition on using it to filter the main roster.
- **(G2) row-type adequacy.** Need a named assumption that the public non-decreasing-time O contains the needed occurrences of each type in the DAG's topological order. This cannot be produced here.
- **(G3) clock semantics.** Define whether elapsed_ms is measured from plan-start virtual t and whether multi-slice continuation at one t is permitted with structural exit only; otherwise (C-clock) is undefined.
- **(G4) source repair.** The Instance.h lower-left adjacency guard / goal-read inconsistency must be repaired on paper before (A1)'s adjacency is read consistently; until root verification, R0 is a candidate only.
- **(G5)** confirm ServiceRegion is a constrainable map-level datum and that ACTUATOR row capacity may bound full re-capture cost.

## 8. ECBS-ADG conditional argument

Conditional on (G1)–(G3) and on H19 ECBS-FA's low-level first-goal search returning normally on this one-sided adjacency family: Type-2 ADG edges are empty, so its dependency graph is Type-1 only, and its execution consumes the *same public facility* — POLICY, ENTRY, ACTUATOR with in-row re-capture, END, TASK_SERVICE under the same (S),(L) — while paying its own graph construction, enqueue, APPEND and guard fees on its own rows, and without any PLAN_CHECK/PRE_COMMIT/CAS. R0's proposal is never its output.

## 9. Paragraph for the manuscript

*Conditional witness (statement only).* Under predicates (A1)–(A5), (S), (L), (C-clock), the start-permitting-position hypothesis (G1) and the row-type adequacy hypothesis (G2), the billing dependency DAG of §3 admits a schedule on the fixed stations under which one agent's genuinely non-zero MOVE is admitted, started, driven to a finite END at its authorized endpoint, and served on a subsequent TASK_SERVICE row with the full spatial-error tube inside the service region; the same facility conditionally admits a fixed external ECBS-ADG path with empty Type-2 edges. This establishes non-vacuity of the service pipeline only. It is not a positive effect, not roster-wide eligibility, not solver completeness; the main comparison (NATURAL D-S− strong-stability polling R-S inside GROUP_PREFIX, mandatory D-S−E0, external H19E0 and H19R-S) and the Q/E main effect on the full fixed E with original weights are unchanged, and no public input's legality or statistical weight is filtered by this construction.

END_C29_CONSTRUCTION
