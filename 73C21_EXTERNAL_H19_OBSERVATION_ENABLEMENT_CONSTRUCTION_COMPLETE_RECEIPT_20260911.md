# 73C21：H19途中证据建设咨询完整终态与独立分析

2026-09-11；执行代理 `/root/source73_r0_remaining_contract`。CONSTRUCTIVE / NONBALLOT / NO-SKILL。调用终态和科学正文均实际完整取得；本回执不授资格，正文有下列需纠正项。保持HOLD，不重启任何旧题。

## 1. 固定输入与真实调用

唯一提示：73C21_EXTERNAL_H19_OBSERVATION_ENABLEMENT_CONSTRUCTION_PROMPT_20260911.md，SHA256 `248465810c8feba071b50b33d399f05483cafa8b84c2d89ef28ae40b96ef044e`，5249 bytes / 19 LF。其主稿输入是 `7928cfd0ffa630e73d1cdc7ab912a47d4ead2d53854bbfa43e3b85d5e9f2b9fc` / 214119 bytes / 659 LF；包含实际已读条款、两阶段域和待核命题。调用前根另提醒已请求动作的未finished-Type2可能空域，已纳入固定提示；不是收到意见后才改提示。

C21只有一次实际调用。此前同类CLI已真实发生沙箱socket错误，本次直接经正常require_escalated审批，不绕过网络边界。实际functions cell310先等待工具，随后返回exec session95740，初始chunk4bd125、1.001s且stdout为空；原句柄第一次轮询e128b6仍活且为空，第二次6348b3真实exit0。没有依据同名进程/PID推断完成，没有失败或超时重试，没有第二个C21会话；旧C20/C14/C17及失落P7/L7均未调用。

实际命令如下，仅为已执行咨询调用的留证，不是研究程序或实验配置：

```text
rtk proxy timeout 480s claude -p --safe-mode --model opus --effort high --max-budget-usd 5 --permission-mode dontAsk --tools '' --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --no-session-persistence --output-format json < /home/lyh/MAPF_PIED_MDDR_RESEARCH/73C21_EXTERNAL_H19_OBSERVATION_ENABLEMENT_CONSTRUCTION_PROMPT_20260911.md
```

首个exec等待参数1000ms，观察原句柄各次均不超过30s。实际JSON：is_error=false，terminal_reason=completed，stop_reason=end_turn，subtype=success，num_turns=1，duration_ms=67644，duration_api_ms=67604；result完整并以END-C21结尾。CLI会话身份为 `a26563b6-9676-47c9-bd86-679a1acea865`，返回uuid为 `d5463a99-8223-4e3b-ac25-02f5a0a3d16e`；这是回执字段，不把它当另一个可续exec。

modelUsage实际键/规范模型为claude-opus-5，provider=firstParty；inputTokens=2、cacheCreationInputTokens=4571、cacheReadInputTokens=0、outputTokens=4871、webSearchRequests=0，costUSD=0.15035375。permission_denials为空。提示约束无skill/工具/MCP，CLI工具空、slash禁、严格空MCP且不持久化；没有代理自行替它打开工具。

完整stdout JSON按返回原字符串以apply_patch保存到73C21_EXTERNAL_H19_OBSERVATION_ENABLEMENT_CONSTRUCTION_RAW_RESPONSE_20260911.json，未改意见措辞。按空白分词的正文为824词，超出提示“约700词”的目标；如实保留，不截断以假装满足。实际完成是完整咨询回执，不是全文意见全部正确。不存在失败原回执需要另造文件。

## 2. 完整result原文

下列BEGIN/END标记之间内容与JSON result逐字核验；标记自身不属于原文。

<!-- BEGIN_C21_RESULT -->
## 1. The exact boundary of a q-only gain

Retirement acts on one quantity only: it monotonically raises `q_t` for one active tid `t`, replacing `Mask(U_t(q_t,ℓ_t))` by a certified suffix mask. By the last-exit characterization (valid here because `b=ℓ`), `r` leaves that mask iff `q_t > λ(t,r)`. Hence the *entire* reachable effect of q is confined to foreign resources with `λ(t,r) < ℓ_t`. Endpoint resources have `λ=ℓ` and are permanently owned; `q` also never marks ADG-finished, never consumes a slot, never alters the original action, and supplies no task truth. Therefore a q-only admission gain for `p` exists only in states where the *unique* failing conjunct of `p` is resource occupancy in `D_p`, every blocking owner is a foreign non-endpoint pair, and every other conjunct (source domain, ADG, mode, binding, geometry, PRECHECK/END/READY/consumption, paid known cursor, per-agent ≤1 open request, per-gate ≤1 active tid) already holds.

## 2. The proposed no-gain statement

It is **valid but structurally inert**. If some mandatory-finished predecessor of `p` is unfinished, `p` fails the ADG conjunct; since `q` cannot mark finished, `p` stays inadmissible. The conclusion is carried entirely by the ADG conjunct, and the resource-blocker/tid-identity clause does no work. So it licenses no claim about resource geometry, and in particular no converse.

**Empty-blocker case.** The hypothesis is vacuously satisfied and the conclusion still holds, but again for an unrelated reason: with no foreign blocker, the failing conjunct is non-resource, and q touches no non-resource conjunct. If instead `p` is otherwise admissible, `p` is already admissible and there is no "gain" to explain. The empty case must not be presented as content.

**Type-1 vs mandatory-finished.** The Type-1 requirement is disjunctive (enqueued *or* finished *or* the preceding selected item in the same-agent chain). An unfinished-but-enqueued Type-1 predecessor is not a blocker, so "unfinished predecessor" must be narrowed to predecessors whose *finished* status is necessary: Type-2 predecessors, plus a Type-1 predecessor that is neither enqueued nor the immediately preceding selected chain item.

**The Type-2 domain for actual requests is empty.** Selectability required all Type-2 predecessors in the paid `F0`; finished is monotone historical knowledge; L394 forbids later splice from adding predecessors to old enqueued actions; and new enqueued items never count as Type-2 finished. Hence for an already-enqueued/requested `p` the set of unfinished Type-2 predecessors is empty. That state is not a legal configuration and yields no negative example. Consequently the statement has non-vacuous content only for **not-yet-enqueued candidates**; for **actual requests** its Type-2 branch is unsatisfiable and only the narrow Type-1 branch could ever apply.

## 3. Enqueued request benefiting from retirement of a non-dominated action

Necessary: (i) resource occupancy is the sole failing conjunct at that center state; (ii) each blocking `r` is owned only by foreign tids with `λ(t,r) < ℓ_t`; (iii) each blocker is bound to the *current* owning action instance — retiring `t` releases nothing if `agent(t)` now executes a later `t'`, and `q_{t'}` is the only relevant cursor; (iv) a correctly bound paid sample (`q ≤ s` at capture) plus paid central verification certifies `q_t > λ(t,r)` for *every* blocking `r`, and commits before `p`'s admission test under a paid known cursor; (v) the blocker class exists at all — the discrete ADG need not cover the expanded tube `K=Z+F` or coarse closed tiles, so tube-level conflicts may have no ADG edge, which is precisely the non-dominated class.

Conditionally sufficient: (i)–(v) together with serialization guarantees — the retirement publishes in the center's single slot before `p` is evaluated, no interleaved GRANT/APPEND installs a new owner of any `r`, and the single-open-request and single-active-tid invariants remain intact. Absence of an ADG edge alone never certifies legality of release.

## 4. No universal ordering

Local redundancy is a per-state predicate. Every sample, verification and retirement occupies the center slot through publication while physics and fixed TASK_SERVICE rows continue; extra querying reshapes queueing, control attempts, replanning/cut inputs and later task timing. Task service needs the full entity at a legal endpoint at a scheduled row, so earlier admission does not imply service. The loop is closed and non-monotone, so no total-cost or Q ordering follows.

## 5. Recommended sentences

"Under H19-PR-COMMON-SYSTEM with b=ℓ, raising q can release only foreign non-endpoint resources (λ<ℓ) and never establishes ADG-finished status, so a q-only admission change is possible only when resource occupancy is the sole failing conjunct; for already-enqueued requests the unfinished-Type-2 case is not a legal state." "Whether such releases alter whole-run Q or total cost is not decided here, since paid queries consume the same finite stations and both external arms and all prespecified failure/missing outcomes remain registered with no results obtained."

## 6. Unproved obligations

Reachability of the required certification by an admissible paid sample/verification sequence within station capacity; tile-level FREE derivability from `q` alone under coarse tiles and expanded `K` (no other resident occupant); membership of `p` in the allowed source domain with a paid known cursor at that row; legitimacy of ADG coverage gaps versus omitted dependencies.

END-C21
<!-- END_C21_RESULT -->

## 3. 执行代理不用skill的逐项复核

1. **采纳局部集合边界，限制其作用域。** b=ell时，r退出原tid后缀当且仅当q_t严格大于最后退出lambda；q只改合法退休及owner/索引，不改原ADG、slot或任务真值。原文“entire reachable effect”只能解释为保持其它变量不变的直接语义影响，不能覆盖真实付费作业诱发的后继排队/规划/物理效果。多个资源阻塞可以同时存在；“sole failing conjunct”是把完整资源可用性作为一个合取项，不是声称只能有一个阻塞者。

2. **采纳Type-2空域，拒绝残留Type-1例外。** 已enqueued动作的原Type-2在批捕获F0中为finished，后继不加前驱且finished不回退。故对合法已请求p再假定其原Type-2未finished没有实例域。Type-1规则本来是enqueued/finished或批内此前已选项；即使当前均不满足，也不等于该前驱从此“必须finished”，后继合法enqueued本身可以满足它。q不改变这些队列事实，所以未入队时可证不能靠q补该门，但应称不满足Type-1入队条件，不应混称必须finished的前驱。已经enqueued的p也不能保留原文声称的“only the narrow Type-1 branch could ever apply”：它所用的既未enqueued又非批前项状态与合法入队链不相容。对真正物理当前请求，自身前MOVE的END/READY消费另由共同门负责，不能拿Type-1入队替代，也不是外国资源阻塞来源。

3. **限定空集论证。** 提示只说“外国非endpoint阻塞”集合。这个集合为空，不一定完全没有外国阻塞：可能仍有endpoint或resident资源。它们不由原tid的q单独清掉，故仍无q-only false→true，但不能像原文直接断言所有阻塞都不存在。若全部资源本来可用，q也没有资源门的准入增量；其它失败门保持或原本已可授均分别处理。支配条件是充分且较强，不是必要条件；已有任何一个独立未满足的必需finished门便足够否定该点q-only增益。

4. **采纳当前owner原动作绑定。** 资源r的实际owner必须绑定完整tid及其原动作，不能把同agent以前已经finished的ADG前驱与该agent后来执行的另一原动作混为一项。必须退完所有仍阻塞p的资源；无ADG边本身不是可退证明，还需合法证书、严格退出、身份及所有其它门。原文关于“unproved tile-level FREE”的表述，在已有唯一owner、固定Mask及合法原子退休合同下可由集合判据条件证明；未闭的是具体输入/轨迹/证书/费用执行是否满足，而非另凭空要求一个新FREE神谕。

5. **纠正APPEND权限。** 条件充分性中“GRANT/APPEND installs a new owner”错误。APPEND只安装不可变逻辑执行记录，不写物理owner；可重新占有释放资源的是后继合法资源准入等事务。正确条件是相关状态与其它准入守卫在付费复核/发布间保持，没有另一个合法资源提交先取走所需资源，而不是禁止APPEND或给H19新增屏障。

6. **纠正服务站混淆。** “Every sample ... occupies the center slot”不符合合同：SELECT/中心验证退休在Srv_C，authority采样/区间编码在Srv_E，网络在Srv_N，另有各自后继发布和接收。额外查询可在这些原有限站竞争服务，不能把所有步骤合成中心同步等待，也不能以此夸大或漏记费用。条件充分的数学资源门翻转不承诺这些工作已经在有限O内完成。

7. **纠正endpoint永久性。** 对本原动作的q≤ell，endpoint资源不能仅凭q退休；END还保留endpoint并改同agent resident tag。以后合法下一MOVE可以接续并按其自己的责任/证据改变资源状态，所以“permanently owned”若指永远世界则过强。只保留本次q-only干预不删除该endpoint责任的结论。

8. **采纳全轨迹无通用排序与完整比较，但不借其断言两种收益都已构造。** 在固定状态移除资源阻塞是单调的集合事实；额外作业的服务竞争、控制机会、规划h/cut/任务知识及真实TASK_SERVICE时刻不是固定。当地无新增准入不证明Q相同或总费用必更大，新增实际查询工作本身仍正计费；全量规划/重试/内存及失败消耗可随后继轨迹变化。本题没有合法地图/原源输出/完整付费轨迹，因此不写H19R-S必强、必弱或已经实证两向反例。已有两外部臂继续预登记，未取得或失败的比较不删去。

## 4. 交付状态

本回执与P27用于细化既有H19两臂解释，不声称此前未登记它们。原result不因上述纠错改写，P27和根仍需各自独立判断；无正式审查票。没有新地图、场景、任务、参数、配置或实验结果；未读35–38/Q或受限载荷，未改主稿、旧件、行政、Git或桌面。全部文字以apply_patch保存研究目录；最终原文一致性和四件身份在完整交付时只读核验。原95740已exit0，functions cell310已闭，无活句柄。
