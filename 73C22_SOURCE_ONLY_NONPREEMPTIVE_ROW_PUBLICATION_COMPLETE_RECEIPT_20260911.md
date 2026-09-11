# 73C22：原行发布的源非抢占候选——完整调用终态与独立分析

2026-09-11；/root/source73_r0_remaining_contract。NO-SKILL / CONSTRUCTIVE / NONBALLOT。调用终态与科学正文完整，意见并非全部正确；保持HOLD。父任务后来要求转入新根交接，本调用在该消息之前已经提交，之后仅续原句柄取得终态并封存原获准四件，不扩任务。

## 1. 固定输入与完整实际调用

唯一提示73C22_SOURCE_ONLY_NONPREEMPTIVE_ROW_PUBLICATION_PROMPT_20260911.md先以apply_patch写入，SHA256 16835758832351e4fd74b279a7e906ca022850804c0968968fd21a855917b519。其依据为主稿9e06199cc6045ddd750b861b3091ec239c7c6ff2ae7eeaebbdd0e7fde61ec113 /216498 bytes/665 LF的具名源服务、时钟及故障窗口与完整C8SR；本代理先独立形成判断，再提交咨询。没有读取其它新的Opus意见或重试C14/C17/P7/L7；旧C21的95740→6348b3已真实exit0，与本调用无关。

实际命令只运行一遍，正常require_escalated审批，不绕过已证沙箱socket限制：

```text
rtk proxy timeout 480s claude -p --safe-mode --model opus --effort high --max-budget-usd 5 --permission-mode dontAsk --tools '' --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --no-session-persistence --output-format json < /home/lyh/MAPF_PIED_MDDR_RESEARCH/73C22_SOURCE_ONLY_NONPREEMPTIVE_ROW_PUBLICATION_PROMPT_20260911.md
```

functions cell323等待原工具返回后关闭，得到exec81862、初始chunk a149e5，初等1000ms且stdout空；续81862第一轮a3399c仍活/空，第二轮e6165e真实exit0并取得完整JSON。没有第二调用、失败重试或按同名PID猜终态；所有观察≤30s。父任务的暂停消息到达时已及时报告cell323，取得session后报告81862，终态后又报告exit0。

实际JSON：type=result、subtype=success、is_error=false、terminal_reason=completed、stop_reason=end_turn、num_turns=1，duration_ms=52346、duration_api_ms=52307；session_id=f991ec42-109e-4620-b92f-7d990fdcb089，uuid=ac36a6f0-a8f4-421a-ac01-b378b778b3d6。实际modelUsage为claude-opus-5/firstParty；inputTokens=2、cacheCreationInputTokens=4682、cacheReadInputTokens=0、outputTokens=3595、webSearchRequests=0；costUSD=0.11914749999999999，permission_denials=[]。工具空、slash禁、strict空MCP、无持久化。正文744空白分词，超过建议约700词；如实保留完整原文，不重新请求或截断。

完整stdout按原字符串保存RAW_RESPONSE，以下result原文将与磁盘JSON逐字比较；不是重新整理后的意见。成功终态不是G3/G6通过，不证明模型总定义或实际后端已具备。

## 2. 完整result，保留原措辞

<!-- BEGIN_C22_RESULT -->
## Verdict

At the paper level the candidate is **causal but not total**. Every phase edge respects the calendar (nothing becomes visible earlier than a strictly later row, no new dynamic completion event, no pre-read of cancellation, no pre-run of a later job), so external O is unchanged as an object. Totality fails: one reachable state has no legal successor, because the candidate removes the only charged vehicle for a phase it simultaneously keeps mandatory.

## Intended phase ordering (as I read it)

START at an original legal source-start row a with paid input/private-boundary capture → BODY over [a, a+d]: not-yet-paid installation, core, PRE_COMMIT_SHAPE, protected original commit, immutable sealing, frozen-input cleanup; nonpreemptive, occupying no intermediate row and granting no parallel core work → SEAL of output, costs, new private state, actual CPU and d against all strategies → WAIT while logically occupied → PUBLISH at the first *existing* strictly subsequent row whose t ≥ a+d and whose original paid publication capacity and single writer slot are available (Srv_C) → visibility strictly later → center validation/CAS (Srv_C, STALE permitted under ALWAYS_ADVANCE) → DISPOSITION over the existing channel into the preallocated control inbox → CONSUME + RELEASE by the same job in a later Srv_P slice → next legal START. Actual CPU, body elapsed d, and post-body wait remain three distinct measured quantities; only the first two are inside the sealed body.

## Strongest genuine composition counterexample

Compose the candidate with the unchanged inbox rule and with ALWAYS_ADVANCE. A body completes and seals; publication succeeds at a qualifying row; center validation returns STALE; by ALWAYS_ADVANCE the source state/RNG history is retained and the disposition is delivered through the existing channel into the preallocated control inbox at a strictly later row. The rules require that disposition be consumed *in a later Srv_P slice*, and the candidate keeps "disposition/release still required before another start" — but "its old instruction-slice quota is explicitly removed" and no other station's capacity was added. The occupied slot therefore has no charged execution carrier for CONSUME+RELEASE. No Stop, no center failure, no authority closure, no WORKER_FAIL has occurred, so no failure phase applies either; the arm sits in (occupied, disposition pending) with an empty successor set. The same gap recurs, independently, for post-cancellation session destruction, which is explicitly "separately charged" and hence also needs a Srv_P slice that no longer exists. This is a contract partiality result only; it asserts nothing about physics, backend, or termination behavior.

## The one necessary lifecycle revision

Scope the quota removal to the body alone: Srv_P loses its instruction-slice quota **only for the interval [a, a+d]**, and retains its original charged finite slice capacity for the strictly post-body lifecycle phases — disposition consumption and slot release, and post-cancellation session destruction/reaping. Nothing else changes; no new parameter, row, event, or capacity is introduced, and no other station is touched.

## The remaining points, separated by kind

**Conditional model.** C8SR gives conditional nonanticipation of sealed bodies only; the candidate inherits that and adds no isolation, ABI, continuation-domain or independence claim.

**Removed capability restriction.** Only the source's slice quota is lifted, and (with the revision) only inside the body. This is a relaxation of a restriction, not a grant of new capability, and not a qualification of anything.

**d = 0 and cross-job monotonicity.** d = 0 is admissible; no epsilon is added. Because publication still requires a strictly subsequent existing row, same-row visibility never arises, and because a next START is gated behind publication, validation and release, source chrono is nondecreasing across jobs — nondecreasing, possibly tied, with ties resolved only by the existing (t, row_id) order.

**Cancellation vs hard WORKER_FAIL.** Soft cancellation preserves the history and charges the whole executed body and tail without clipping at Stop and without adding to Q. Hard WORKER_FAIL / Stop / init-deadline revokes publication and demands actual termination and reaping evidence; whether such evidence can be obtained relative to a+d for a body the host cannot observe midway is **unknown here** and must stay unknown.

**Executed tails vs unavailable costs.** Where a tail demonstrably executed but metering is unverified, absent, or the call did not return, the cost must be recorded as unavailable/incomplete — never imputed, zeroed, or converted into timeout success.

**Source fidelity.** Changing chrono to a plus in-body elapsed diverges from "current public t"; source logic that compares chrono against calendar-derived quantities may read values matching no O row. Fidelity impact is a genuine open item, not resolved here.

END-C22
<!-- END_C22_RESULT -->

## 3. 不用skill的独立逐项分析

1. **采纳旧收件处置载体缺口，拒绝把停滞直接等同逻辑无定义。** 旧§9 L350明确要在同占槽job的后继Srv_P切片验证处置后释放；候选删除该站指令供给而未改这一句，确实不能凭“费用另记”宣布它已执行。但原合同本就允许无后继行/容量时保持pending至Stop；保持pending可以是完整状态语义。这里是预期恢复路径缺少可执行收费接缝，不是已证明世界没有任何后继或轨迹必然不total。没有运行该反例，它是给定条款下的符号组合。

2. **拒绝将源结果发表归Srv_C。** 源自己的封存envelope/结束节点首先用Srv_P这一writer原有发布容量交给原规划通道；后继网络及中心检验/CAS另用原Srv_N/Srv_C。如果中心槽被占，不能把所有源发布检查移给中心或声称源自行写中心Π。严格后继约束分别绑定源开始/完成、发送、接收与中心提交，不重复引入免费跨站可见性。

3. **不采用其唯一建议作为本候选答案。** 保留后体精确PROCESS_SLICE会重新要求当前尚未实现的源代码/析构步骤级闸门；这可以是另一个混合模型，但不是本题取消Srv_P指令预算后的具体收束。原控制收件槽的有限字段核验可明确归本源writer既有有限发布检查容量，后体依未来撤销的任意会话析构则不能藏进它。后者只在实际撤销后执行行政回收并全量计尾费，确认退出前不复用来源；没有实际后端证据就保留未知。

4. **“只是限制放松，不增加能力”误导。** 同一有限O内源体可能执行超过旧源切片总额的工作，服务能力及时间映射已实质改变。逻辑串行与完整elapsed占用限制这种新能力，但不使它与原配额等价。必须各引用来源的内部臂及外部ECBS共用新服务规则，并保留来源自身工作和失败差异；其他站不免配额，STRICT不再虚收已取消的源指令供给。

5. **d=0和跨job非降只有在具体时钟条件下成立。** 严格后继row阻止同一行递归，有限O也限制启动次数，但不会凭此自动证明所有源clock读值合法。需同一单调测量域/epoch、源各读值不晚于完整d端点、统一非降的ABI转换且无表示溢出；下一job开始不早于前完整体、源发布和中心处置/释放。该条件下a_next≥a+d≥任一前job原时钟读值（转换前），可能等时但不倒退。不补epsilon，也不从零elapsed推CPU/工作免费。

6. **硬失败不是只缺reap证据。** 原WORKER_FAIL/INIT截止与新的不可抢占完整体在语义上先冲突：如果硬故障必须中断原体，而宿主已把故障后的指令算过，不能只说等待退出证据便保持原前缀。P29提出一个明确但尚未采用的源级REVOKE_AND_DRAIN修订：公开撤权立即关闭输出/新调用，完整体可继续但未来状态隔离，真实回收另外确认。真正宿主崩溃/无法结束仍是失败或未知，不冒作该模型的已完成正常体。此改变不得隐在旧WORKER_FAIL名称下。

7. **源原样保真与合法映射分开。** 新chrono可返回非O时刻是已声明的非抢占源时钟语义，不因它非日历行就自动非法；但其读域、ABI别名/单位、计时末端及原预算分支必须实际绑定。不能宣称新规则与原同row钟逐结果等价，亦不能根据咨询证明R0/ECBS全部继续域。

8. **尾费未知分类采纳，但不一概推Q未知。** 已执行工作不得被Stop截掉；未获完整测量就只保留可信成本前缀，不填零/上界。Q是否可辨仍由已认证世界/源依赖和固定评分规则判定，不能仅凭源未返回自动写Q=0，也不能在缺完整可信轨迹时补全Q。本题不证明尾部有限、实际全费用、配对独立或效果排序。

## 4. 最终实际边界

完整咨询及独立判断已保存；P29是主稿外的有界备选构造与未闭义务，不是正式资格票。交接请求到达后没有启动新调用/检索或新增任务，只完成原81862与本获准工件封存。未实现、写伪代码、构建、测试、仿真、调参或读取/生成受限载荷，保护参数未赋值。主稿/旧件/行政/Git/桌面未改。原exec81862 exit0，cell323已关闭，无活句柄；HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT保持。
