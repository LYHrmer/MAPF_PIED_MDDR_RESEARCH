# 73C30：付费首次移动依赖与公共日历嵌入——完整建设回执

2026-09-13；实际 Claude 建设交付，非正式审稿、非通过票。提示中的固定源有限正常输出是待根证明的前提，不是本回执验证过的事实。

## 实际终态

- 唯一 exec session：32405；启动 chunk 96d129；终态 chunk 0ee1b3，exit 0。
- CLI session：08be843e-5512-4bf8-8bee-a22eda23ec05。
- 实际模型：claude-opus-5 / firstParty；terminal_reason=completed，stop_reason=end_turn，is_error=false。
- duration_ms=93028；客户端 total_cost_usd=0.21176625000000002；正文末尾 END_C30_CONSTRUCTION 完整。
- 同名前缀 PROMPT 保存实际输入；RAW_RESPONSE.json 保存实际工具返回的完整 stdout。未重新调用或从摘要重造原文。

## 根独立取舍

采用方向：把单作业展开为多个站点处理阶段，逐一保留通信、接收、计算、未来发布和当前原子 guard 的费用；append、GRANT、RUN、ACTUATOR START 是不同因果环节；真实 TASK_SERVICE 不依赖软件 READY 已交付；非空见证只能对事先定义的符号日历类提出，不能依实际完成轨迹生成实验 O。

必须纠正，以下建议未采用：

1. N13/N14 倒序。P 先发布源输出，经 P→C 通信到中心验证/CAS；中心决定再经 C→P 返回保留的作业内收件槽，P 才能接收/核验/retire。源站此时仍被原作业占用，不能让收件排在自己之后。源请求与结果两向通信也不能省略。
2. CURSOR、TASK_REQ、POLICY 和 PLAN_CHECK 是原公共机会；回复接收/核验使用已有接收 token 与 PROCESS_SLICE，不能把它们重新标成这些公共机会，从而暗加请求、轮转或策略次数。
3. phase 1 的 RESEND_CAP 只有事先排在 grant 接纳前才可构成付费 NO_GRANT；若已收到 grant 就可能重发，不能无条件称 NOOP。一次 START 后由已定义控制律自主推进，正文 N27 重复 ACTUATOR 不是完成该 MOVE 的必要前提。
4. DAG 同层不保证站点互异；须先加入 FIFO/单写者和跨发布占用的串行边，再排拓扑次序。所有不可跨行的 CAPTURE、guard、账本原子段及同一行其它实际费用均须有界，不能只列 grant/ACTUATOR/publication。
5. 把每段费用命名为 W 不是已经证明其有限上界。须由固定源分支、库实体、表示条件和收费操作给出上界；不采纳新增 SRC_WORK_CERT 接口，也不要求一个仅依输入字节长度而上界任意正常返回运行的未证全局函数。已证具体输入族与固定私有初态的预先界才可用于本次存在性证明。
6. 当前主稿已区分 CUM_CAP 的 cap lineage 和独立 control epoch/attempt；本意见未提供新反例，不能凭“secondary seam”新增 ACK、重置 epoch 或宣称原绑定缺失。

根尚未将完整联合见证判为闭合，也未修改全来源、后端资格或正式门状态。该回执只能支持经纠正的设计构造。

## Claude 完整原文

## 1. Paid dependency DAG (nodes = station-visits, not jobs)

Notation `⟨public type @ station⟩`; `⇒` = strict-later-row edge (new job/message/result); `→` = same-row internal stage sequence. Every node is a *stage*, and a job is a path of stages: no node is "one unit".

**Bootstrap.** N0 `⟨INIT @ Srv_C⟩`: transfer bootstrap responsibility, build resident indices, initial cursor evidence. ⇒

**Cursor evidence (Kc).** N1 `⟨CURSOR @ Srv_C⟩` request under the generic stable rotation ⇒ N2 `⟨NETWORK(C,E(i))⟩` ⇒ N3 `⟨PROCESS_SLICE(Srv_E(i))⟩` capture → certify ⇒ N4 `⟨NETWORK(E(i),C)⟩` ⇒ N5 `⟨CURSOR @ Srv_C⟩` validate/install `c=k, Kc`. A second needed capture re-enters at N1 only after the rotation returns to `i`: that gap is paid, not free.

**Task evidence (K_task).** N6 `⟨TASK_REQ @ Srv_C⟩` ⇒ N7 `⟨NETWORK(C,A)⟩` ⇒ N8 `⟨PROCESS_SLICE(Srv_A)⟩` TASK CAPTURE against the *global atomic ledger* → copy → encode → sign (each expanded to word steps) ⇒ N9 `⟨NETWORK(A,C)⟩` ⇒ N10 `⟨TASK_REQ @ Srv_C⟩` paid validation + install.

**Plan.** N11 `⟨PLAN_CHECK @ Srv_C⟩`: test `Kc≥S` ∀, PROJECT nonempty, no pending source job → freeze anchored input → reserve in-job control-receipt slot → request Srv_P. ⇒ N12ᵏ `⟨PROCESS_SLICE(Srv_P)⟩`, k=1..m: import-authority check, PRE_COMMIT_SHAPE, `planner_commit`, output/cleanup — a *chain* of slices, each ⇒ the next. ⇒ N13 `⟨PROCESS_SLICE(Srv_P)⟩` receipt receive/validate/retire on the reserved slot (never behind itself) ⇒ N14 `⟨PLAN_CHECK @ Srv_C⟩` validate latest PROJECT/versions/anchor → CAS-append Π. **N14 creates original MOVE slots and nothing else**: no grant, no RUN, no motion. (C29's conflation of append with grant is cut here.)

**Grant.** N15 `⟨POLICY(SOURCE_REQUEST,i) @ Srv_C⟩` with `n_i mod 3 = SOURCE_OR_EXTEND`: from paid Kc and the committed original MOVE, allocate `tid/slot/parent`, emit the PRECHECK job. ⇒ N16 `⟨NETWORK(C,E(i))⟩` ⇒ N17 `⟨ENTRY(i,PRECHECK) @ Srv_E(i)⟩`: PRECHECK CAPTURE proving RESIDENT_OPEN, `c=k`, resident at original `u`, active/pending NONE, HOLD, slot unconsumed/unended, exact binding → certify reply. **This is not an ACTUATOR test** (C29's second error); it neither reads a delay bit nor authorizes motion. ⇒ N18 `⟨NETWORK(E(i),C)⟩` ⇒ N19 `⟨POLICY(SOURCE_REQUEST,i) @ Srv_C⟩` **atomic grant row**: receive/validate certificate, test full-edge M0 FREE-or-own-parent and no foreign fence, then `b=ℓ`, retag owner, record GRANTED + initial `control_epoch`/RUN_ALLOWED *intent*, build CUM_CAP. Captures CURRENT root in its original row; if the row's supply is exhausted mid-guard, fees are retained, no effect/watermark, recapture later — never amortized. No RUN is emitted.

**Arming.** N20 `⟨NETWORK(C,E(i))⟩` ⇒ N21 `⟨PROCESS_SLICE(Srv_E(i))⟩` verify binding, reserve END-record/handshake/event-descriptor slots ⇒ N22 `⟨PROCESS_SLICE(Srv_E(i))⟩` *publication* installing `C=ℓ`, phase GRANT_ARMED, `active_tid`; no s/v/z/c change, no START.

**RUN and actuation.** N23 `⟨POLICY(SOURCE_REQUEST,i) @ Srv_C⟩` with `n_i mod 3 = CONTROL_RETRY`: fresh RUN tied to *that* opportunity. Because every opportunity counts even when empty, N23 is at least two counted opportunities after N15 (the intervening RESEND_CAP opportunity is paid no-op work, not a skip). ⇒ N24 `⟨NETWORK(C,E(i))⟩` ⇒ N25 `⟨PROCESS_SLICE(Srv_E(i))⟩` authentication only (no control effect) ⇒ N26 `⟨PROCESS_SLICE(Srv_E(i))⟩` publication of the immutable ACTUATOR candidate ⇒ N27 `⟨ACTUATOR(i)⟩`: consume one candidate in published FIFO order, fully pay identity/phase/epoch/attempt/motion guard and the *current* delay-bit read/commit; START iff installed positive `C` and reference HOLD. N27ʳ repeats over the reference horizon; Srv_E and ACTUATOR never overwrite each other's state.

**END and service.** N28 real END: durable EndRecord/pending/TERMINAL_UNCONSUMED, `c` unchanged, only an opaque local END offer. N29 `⟨TASK_SERVICE⟩` at its fixed row may count agent `i` when the original still-effective head is `v` and `X(t)⊆ServiceRegion(j)` (symbolic sufficient condition `v+F+Z⊆ServiceRegion(j)`), before STOP, with **no** dependency on N28's proof or on `⟨READY_CENTER_RETRY⟩`/`⟨END_LOCAL_RETRY⟩`/`⟨GROUP_RETIRE⟩`, which hang off N28 as separate later chains. Intermediate cap HOLD never counts.

**Required delays.** (i) one strict row per ⇒ edge; (ii) completion-then-publication splits N21/N22 and N25/N26; (iii) mod-3 rotation gap N15→N23; (iv) CURSOR rotation gap for repeat captures; (v) FIFO occupancy: at each single-writer station the resident job holds its slot through its one future atomic publication, so co-resident chains serialize into distinct rows; (vi) recapture rows for any atomic guard that did not close.

## 2. Bound scheme and same-t embedding

Per-stage word-work symbols (**non-experimental, abstract**): `W_hop, W_cap, W_val, W_sig, W_pub, W_grant, W_guard, W_noop`, each a definable function of encoded index/key/geometry widths — these are *known definitions*, expandable to basic steps. `W_src` (total billed steps of one source invocation: import, PRE_COMMIT_SHAPE, `planner_commit`, output, cleanup) is **not proved here**: the source's finite normal two-state output is an explicit premise under proof by root+source; I do not claim the C++ chain.

Layer the DAG by longest ⇒-path; nodes in one layer touch disjoint stations and may occupy the same `t` with distinct `row_id`, executed physics → publication → type. Two conditions: (a) **row supply** ≥ the largest *indivisible* unit placed in it — max(`W_grant`, `W_guard`+bit read, one publication unit), plus co-located paid no-ops (QUERY/COORDINATE/MODE); (b) **layer count** ≥ number of ⇒-layers, including rotation and recapture rows.

Can finitely many bounds be met jointly? Yes — precisely because no macro-job is primitive. The only indivisible units are the grant commit, an ACTUATOR guard, and one publication; `W_src` is split across N12¹⁻ᵐ, each slice bounded by slice supply. Treating the source call as one primitive would make `W_src` an atomic unit, forcing (a) to dominate an unproved quantity, so feasibility would inherit the premise instead of resting on definitions.

## 3. Statement and the seam

**Lemma (non-vacuity, existence over a symbolic calendar class).** Under A–H, assuming (P1) the source's finite normal two-state output with a pre-declarable step bound, there exists a legal public calendar in the class admitting the above DAG embedding, in which one agent's first original MOVE receives a genuine grant, a genuine ACTUATOR START, and is counted by a fixed TASK_SERVICE row. Claims nothing about D superiority, deadlock freedom, source full-history qualification, legality of all instances, or WinkTPG-class comparison.

**Genuine seam.** Row supply must be fixed non-adaptively, so `m` cannot be chosen from realized completion; termination alone is insufficient. Smallest shared definition needed: **SRC\_WORK\_CERT** — a function of the *frozen anchored input's* encoded size alone, upper-bounding total billed source word-steps on any normal-return run, independent of delay bits and private progress. Minor secondary seam: the token binding `control_epoch` carried by CUM_CAP vs. the published candidate, needed to make N27's epoch test decidable from published state.

END_C30_CONSTRUCTION
