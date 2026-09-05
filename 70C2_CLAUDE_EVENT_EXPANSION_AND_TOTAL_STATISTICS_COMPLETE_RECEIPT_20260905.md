# 70C2 Claude 事件展开与统计总函数：第二次实际完整回执

日期：2026-09-05。状态：COMPLETE-RECEIPT / NONBALLOT；不修改候选 70，不是正式审查、不授予资格门通过。
固定提示：70C2_CLAUDE_EVENT_EXPANSION_AND_TOTAL_STATISTICS_CONSTRUCTION_PROMPT_20260905.md。
第一次 shell 58610 实际退出 0，但 tool 输出截断，不接受其为完整建议；详见 70A1。确认其终止后才同提示重试。
第二次实际 shell 47256，exit=0；客户端 session_id=674ea165-260c-44b3-83c5-dfde1d881f81，terminal_reason=completed，is_error=false，duration_ms=106307。客户端报告 canonicalModel=claude-opus-5 / provider=firstParty；没有独立证明其后端模型。无工具/skill/网页/文件读取。根代理把完整 stdout 存入会话缓存，成功解析 JSON，连续读完 result 至 ADVICE-COMPLETE；本文件保留实际 stdout 文本和完整 result，不声称对原远程网络字节作取证归档。

## 根代理采纳边界

可用原则：机会本身与成功动作分开；起步失败仍消耗相应尝试序号；普通载荷从各方法自己的物理历史产生；计分和算法获知隔离；缺必需臂时主统计整体 UNESTIMABLE；STRICT 主轨道、NATURAL 次要。它们仍须写进后继的具体总函数并接受全部顺序审查。

未采纳/需重构：
- 用 (resource_id,generation) 代替 agent/occurrence 作为执行尝试主体不适合一个 MOVE 涉及多个 owner 的协议，也会把资源分配差异混进物理起步键。公共机会索引和 agent/tid 尝试序号须分别定义。
- “COMPLETION_NOTICE 不得以真完成为父事件”和“三通道互不可推”过强。合法证据本来必须蕴含相应物理事实；需要限制算法可见投影和原始 oracle 指针，不能禁止后台保存真实因果谱系。
- g_category 由未来 manifest 给纯函数、有限良基格等仍只是函数插槽/证明骨架，尚未定义本项目全部事件展开；不能直接用来宣布 B03 关闭。物理模拟器/可信服务可按合同读物理状态，候选决策不可读，不能把两类生成器都强行限制为 View_arm。
- NO_EVENT 一律按机会收费不足以定义执行前崩溃、无主体、预算拒绝与已实际支付服务等分支；后继须给一致的具体类别函数，费用值仍不绑定。
- 独立创新、标签可交换、固定权重不能推出配对差的符号置换检验有效；还需要相应随机化零假设或对称性。对此建议不采纳。按固定地图内根创新重采样也不必然等价于抽样地图超总体，不能沿用笼统否定。
- 区间的“cell 充分性判据不知道”不算完成统计合同。后继应采用有明确假设与总返回的区间规则，或者明确不可估，不能留给实现者临时决定。
- 本回执不是已见任何效用结果。所有给出的规则还未写入正式后继或获审查通过。

## 完整实际 stdout 文本

```json
{"is_error":false,"duration_api_ms":106287,"num_turns":1,"stop_reason":"end_turn","session_id":"674ea165-260c-44b3-83c5-dfde1d881f81","total_cost_usd":0.18499749999999998,"usage":{"input_tokens":2652,"cache_creation_input_tokens":1338,"cache_read_input_tokens":0,"output_tokens":6535,"output_tokens_details":{"thinking_tokens":0},"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":1338},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{"claude-opus-5":{"inputTokens":2652,"outputTokens":6535,"cacheReadInputTokens":0,"cacheCreationInputTokens":1338,"webSearchRequests":0,"costUSD":0.18499749999999998,"contextWindow":200000,"maxOutputTokens":64000,"canonicalModel":"claude-opus-5","provider":"firstParty"}},"permission_denials":[],"terminal_reason":"completed","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subtype":"success","api_error_status":null,"result":"以下建议仅作为三路审查收齐后**另立新编号**的纸面素材，不触碰候选 70；受保护符号一律沿用原义，本文不引用、不赋值、不给范围。所有时间表、分布表、费用表均标 UNINSTANTIATED。\n\n## 一、机会表 → 闭合确定事件流\n\n**反例（为何缺分支会改变公平比较）**：某 tid 已 COMMIT 但从未 START。若无起步失败事件、attempt ordinal 不被消费，则该 lineage 的后续 semantic_key 被\"压缩\"上移一位；于是甲方法在 key=k 处遇到的注入故障，乙方法在 k 处遇到的是原本属于 k+1 的故障——两臂面对的世界不同，配对差失去意义。第二反例：若\"请求服务但实际不在任务顶点/在途\"只记 NO_EVENT 且不计费，则方法可零成本反复试探，而按规矩先自查的方法付费，费用账本不对称。\n\n**最小扩展枚举**（仅加 6 个 type + 1 个哨兵）：\n`EXECUTOR_OPPORTUNITY`、`ORDINARY_REPORT_OPPORTUNITY`、`TASK_SERVICE_OPPORTUNITY`、`START_FAILURE`、`COMPLETION_TRUTH`（oracle 通道）、`COMPLETION_NOTICE`（算法获知通道）、`NO_EVENT`。\n\n**最小新增字段**：`opportunity_ordinal`、`subject_key`、`attempt_ordinal`、`copy_index`、`channel_class ∈ {CERT, ORDINARY, ORACLE}`、`no_event_reason`、`cost_class_ref`（UNINSTANTIATED）、`expand_depth`。\n\n**subject_key 与 launch 前无 tid**：attempt ordinal 不挂在 tid 上，而挂在 lineage `(resource_id, generation)` 上；tid 未生成时 `tid = ⊥`（保留哨兵，永不复用），tid 落地时发一条绑定关系而非改键。`START_FAILURE` 消费本次 attempt_ordinal 并使 lineage 序号前进，后继键不回填。\n\n**ordinal 定义**：每类机会的 ordinal 是 `(block_id, stream_domain, category, subject_key)` 上从声明起点单调递增的计数；**只要机会被提供就自增**，与结果无关。`copy_index` 区分重复副本，使 DUPLICATE 不与原件撞键；重排只置换 `delivery_time_or_missing`，绝不置换 `logical_emit_time`；丢失即 delivery = ⊥。\n\n**无动作分支**：`NO_EVENT` 必带 reason ∈ {NO_SUBJECT, NO_PENDING_SEND, NOT_AT_TASK_VERTEX, IN_TRANSIT, QUEUE_EMPTY, ARM_NOT_APPLICABLE}。某方法无对应发送/请求 → ARM_NOT_APPLICABLE，**禁止借他法真值构造 payload**。\n\n**父事件**：机会类事件的 parent 为其触发上下文（block 时钟槽或前一同 subject_key 事件）；`START_FAILURE` 的 parent 为对应 DECIDE_RESULT/COMMIT；`COMPLETION_TRUTH` 的 parent 为 `TASK_SERVICE_OPPORTUNITY`；`COMPLETION_NOTICE` 的 parent 必须是一条已计费的合法证据/通知事件，**不得以 COMPLETION_TRUTH 为 parent**。\n\n**费用**：入账时点 = 机会被提供的时刻，按 cost_class_ref 记账，NO_EVENT 同样入账（消除试探不对称）；类别→数值的绑定 UNINSTANTIATED。\n\n**同时刻总序**（字典序，全序且确定）：`(logical_emit_time, phase_rank, expand_depth, block_id, stream_domain, category_rank, subject_key, ordinal, copy_index, actor_id, event_id)`。多 agent 同时刻由 block_id/actor_id 尾键决然打破，不引入随机。\n\n**Expand 的数学描述**：\n`Expand(manifest, state, key) -> L`，L 为有穷序列，且**恒非空**：\n1. 若 `enabled(manifest, key) = false` → 返回 `[NO_EVENT(reason)]`（总返回保证）。\n2. 否则按 key.category 取该类的确定生成规则 g_category（manifest 给出，纯函数于 `View_arm(state)` 与 manifest，不读真值），生成本层事件；每个被生成的零时长后继必须满足 `(phase_rank, expand_depth)` 在声明的有穷良基格上**严格递增**，且每 (key, category) 的 ordinal 槽数由 manifest 声明为有穷（数值 UNINSTANTIATED）。二者合起来给出递归终止与 |L| < ∞ 的证明骨架。\n3. 失败请求（PREPARE_REJECT、起步失败、服务未完成）仍产出事件并消费 ordinal，不改变后续键。\n4. 任务服务：每 agent 每次服务至多结算队首一个已分配任务；判据为\"实际驻留是否位于任务顶点\"，在途 → `NO_EVENT(IN_TRANSIT)`。\n5. 真值分流：`COMPLETION_TRUTH.channel_class = ORACLE`，recipient 只能是计分账本与已声明可信样本服务；不变式：`View_arm` 对 ORACLE 事件与真值字段取空，候选可见信息只能来自 CERT/ORDINARY 通道；三通道字段互不共享、互不可推。\n\n## 二、主配对统计函数\n\n**反例**：若某 block 因基础设施原因某必需臂始终未 launch，而做法是悄悄删除该 block 并重归一化，则两臂在不同 roster 子集上被比较；在困难地图上更容易起不来的方法反而获益（幸存者偏差）。另一反例：若分母用\"实际运行时长\"而非 declared exposure，早崩溃反而抬高比率。\n\n**精确补充**：\n1. 分母账本：每个合法公共 roster block 的 full 与固定 control 两项**永久留在账本**；declared exposure 于 launch 前固定、正、不可变，并冻结登记。\n2. launch 后的 crash / timeout / 主动停止 / 数值不确定一律不重试，均为科学结果；`Q` 为终止前真值计分的实际完成数；终止到 declared cutoff 之间按**零新增任务**外推；`Y = Q / declared exposure`。该外推不是补模拟剩余物理过程。\n3. launch 前可按预声明规则做基础设施重试；重试不改 declared exposure、不新建 block。\n4. 若到截止有必需臂从未 launch：该 block 记为 MISSING_ARM，其 Y 未定义；**主估计量与置信区间取 UNESTIMABLE**，同时完整报告已观察臂的原始 Y、每臂 launch 状态、终止原因分类与缺失原因。不删块、不重归一化、不设 Y=0、不引入插补理论。\n5. 估计量：块内配对差 `D_b = Y_b^full − Y_b^control`；固定层级权重 w（由公开类别/地图/源记录/预声明 profile 决定，launch 前固定、非数据自适应）；`Δ̂ = Σ w_b D_b / Σ w_b`。\n6. 条件总体 = 固定公开类别/地图/源记录/profile 集合；随机性**仅**为独立重复根创新。地图非从更大地图总体随机抽样，故推断是\"给定该固定地图集合的有限总体条件推断\"，不得声称对地图总体外推。\n7. 区间：主区间只在每个 profile cell 内对**根创新重复标签**做配对随机化/符号置换（地图集合与权重保持固定），其有效性依赖明示假设：(A1) 跨根创新独立；(A2) cell 内配对差在创新标签置换下可交换；(A3) 权重 launch 前固定；(A4) 方差单位只取 block（=创新重复），agent/tick 不是独立样本、禁止伪重复。若某必需 cell 的独立创新重复不足以支撑有限样本随机化分布（判据为声明性要求，本文不给任何数值），该 cell → UNESTIMABLE；任一必需 cell 不可估 → 总体 UNESTIMABLE。\n8. cluster bootstrap 若重抽地图/块，隐含把地图当作更大总体的可交换抽样，与固定条件总体矛盾；因此它只能作为附注，标注为\"地图超总体启发式，非固定条件总体的有保证区间\"，不得充当主区间，也不得在主区间 UNESTIMABLE 时替补。\n9. STRICT 统一总计算预算轨道为主比较；NATURAL 计算开销轨道为次要解释，单独报告、不与主轨道合池、不参与主结论。\n\n不主张任何提升或已通过资格门；上述仅为分支完整性与可判定性的纸面补齐。未知项（如各机会的具体费用类别取值、cell 充分性判据的具体形式）此处明确写作：不知道，需另行授权绑定。\n\nADVICE-COMPLETE","ttft_ms":53282,"ttft_stream_ms":3104,"time_to_request_ms":21,"type":"result","duration_ms":106307,"uuid":"6f54e98f-af2f-487f-b2bd-78877cc3b569"}
```

## 完整 result 文本

以下建议仅作为三路审查收齐后**另立新编号**的纸面素材，不触碰候选 70；受保护符号一律沿用原义，本文不引用、不赋值、不给范围。所有时间表、分布表、费用表均标 UNINSTANTIATED。

## 一、机会表 → 闭合确定事件流

**反例（为何缺分支会改变公平比较）**：某 tid 已 COMMIT 但从未 START。若无起步失败事件、attempt ordinal 不被消费，则该 lineage 的后续 semantic_key 被"压缩"上移一位；于是甲方法在 key=k 处遇到的注入故障，乙方法在 k 处遇到的是原本属于 k+1 的故障——两臂面对的世界不同，配对差失去意义。第二反例：若"请求服务但实际不在任务顶点/在途"只记 NO_EVENT 且不计费，则方法可零成本反复试探，而按规矩先自查的方法付费，费用账本不对称。

**最小扩展枚举**（仅加 6 个 type + 1 个哨兵）：
`EXECUTOR_OPPORTUNITY`、`ORDINARY_REPORT_OPPORTUNITY`、`TASK_SERVICE_OPPORTUNITY`、`START_FAILURE`、`COMPLETION_TRUTH`（oracle 通道）、`COMPLETION_NOTICE`（算法获知通道）、`NO_EVENT`。

**最小新增字段**：`opportunity_ordinal`、`subject_key`、`attempt_ordinal`、`copy_index`、`channel_class ∈ {CERT, ORDINARY, ORACLE}`、`no_event_reason`、`cost_class_ref`（UNINSTANTIATED）、`expand_depth`。

**subject_key 与 launch 前无 tid**：attempt ordinal 不挂在 tid 上，而挂在 lineage `(resource_id, generation)` 上；tid 未生成时 `tid = ⊥`（保留哨兵，永不复用），tid 落地时发一条绑定关系而非改键。`START_FAILURE` 消费本次 attempt_ordinal 并使 lineage 序号前进，后继键不回填。

**ordinal 定义**：每类机会的 ordinal 是 `(block_id, stream_domain, category, subject_key)` 上从声明起点单调递增的计数；**只要机会被提供就自增**，与结果无关。`copy_index` 区分重复副本，使 DUPLICATE 不与原件撞键；重排只置换 `delivery_time_or_missing`，绝不置换 `logical_emit_time`；丢失即 delivery = ⊥。

**无动作分支**：`NO_EVENT` 必带 reason ∈ {NO_SUBJECT, NO_PENDING_SEND, NOT_AT_TASK_VERTEX, IN_TRANSIT, QUEUE_EMPTY, ARM_NOT_APPLICABLE}。某方法无对应发送/请求 → ARM_NOT_APPLICABLE，**禁止借他法真值构造 payload**。

**父事件**：机会类事件的 parent 为其触发上下文（block 时钟槽或前一同 subject_key 事件）；`START_FAILURE` 的 parent 为对应 DECIDE_RESULT/COMMIT；`COMPLETION_TRUTH` 的 parent 为 `TASK_SERVICE_OPPORTUNITY`；`COMPLETION_NOTICE` 的 parent 必须是一条已计费的合法证据/通知事件，**不得以 COMPLETION_TRUTH 为 parent**。

**费用**：入账时点 = 机会被提供的时刻，按 cost_class_ref 记账，NO_EVENT 同样入账（消除试探不对称）；类别→数值的绑定 UNINSTANTIATED。

**同时刻总序**（字典序，全序且确定）：`(logical_emit_time, phase_rank, expand_depth, block_id, stream_domain, category_rank, subject_key, ordinal, copy_index, actor_id, event_id)`。多 agent 同时刻由 block_id/actor_id 尾键决然打破，不引入随机。

**Expand 的数学描述**：
`Expand(manifest, state, key) -> L`，L 为有穷序列，且**恒非空**：
1. 若 `enabled(manifest, key) = false` → 返回 `[NO_EVENT(reason)]`（总返回保证）。
2. 否则按 key.category 取该类的确定生成规则 g_category（manifest 给出，纯函数于 `View_arm(state)` 与 manifest，不读真值），生成本层事件；每个被生成的零时长后继必须满足 `(phase_rank, expand_depth)` 在声明的有穷良基格上**严格递增**，且每 (key, category) 的 ordinal 槽数由 manifest 声明为有穷（数值 UNINSTANTIATED）。二者合起来给出递归终止与 |L| < ∞ 的证明骨架。
3. 失败请求（PREPARE_REJECT、起步失败、服务未完成）仍产出事件并消费 ordinal，不改变后续键。
4. 任务服务：每 agent 每次服务至多结算队首一个已分配任务；判据为"实际驻留是否位于任务顶点"，在途 → `NO_EVENT(IN_TRANSIT)`。
5. 真值分流：`COMPLETION_TRUTH.channel_class = ORACLE`，recipient 只能是计分账本与已声明可信样本服务；不变式：`View_arm` 对 ORACLE 事件与真值字段取空，候选可见信息只能来自 CERT/ORDINARY 通道；三通道字段互不共享、互不可推。

## 二、主配对统计函数

**反例**：若某 block 因基础设施原因某必需臂始终未 launch，而做法是悄悄删除该 block 并重归一化，则两臂在不同 roster 子集上被比较；在困难地图上更容易起不来的方法反而获益（幸存者偏差）。另一反例：若分母用"实际运行时长"而非 declared exposure，早崩溃反而抬高比率。

**精确补充**：
1. 分母账本：每个合法公共 roster block 的 full 与固定 control 两项**永久留在账本**；declared exposure 于 launch 前固定、正、不可变，并冻结登记。
2. launch 后的 crash / timeout / 主动停止 / 数值不确定一律不重试，均为科学结果；`Q` 为终止前真值计分的实际完成数；终止到 declared cutoff 之间按**零新增任务**外推；`Y = Q / declared exposure`。该外推不是补模拟剩余物理过程。
3. launch 前可按预声明规则做基础设施重试；重试不改 declared exposure、不新建 block。
4. 若到截止有必需臂从未 launch：该 block 记为 MISSING_ARM，其 Y 未定义；**主估计量与置信区间取 UNESTIMABLE**，同时完整报告已观察臂的原始 Y、每臂 launch 状态、终止原因分类与缺失原因。不删块、不重归一化、不设 Y=0、不引入插补理论。
5. 估计量：块内配对差 `D_b = Y_b^full − Y_b^control`；固定层级权重 w（由公开类别/地图/源记录/预声明 profile 决定，launch 前固定、非数据自适应）；`Δ̂ = Σ w_b D_b / Σ w_b`。
6. 条件总体 = 固定公开类别/地图/源记录/profile 集合；随机性**仅**为独立重复根创新。地图非从更大地图总体随机抽样，故推断是"给定该固定地图集合的有限总体条件推断"，不得声称对地图总体外推。
7. 区间：主区间只在每个 profile cell 内对**根创新重复标签**做配对随机化/符号置换（地图集合与权重保持固定），其有效性依赖明示假设：(A1) 跨根创新独立；(A2) cell 内配对差在创新标签置换下可交换；(A3) 权重 launch 前固定；(A4) 方差单位只取 block（=创新重复），agent/tick 不是独立样本、禁止伪重复。若某必需 cell 的独立创新重复不足以支撑有限样本随机化分布（判据为声明性要求，本文不给任何数值），该 cell → UNESTIMABLE；任一必需 cell 不可估 → 总体 UNESTIMABLE。
8. cluster bootstrap 若重抽地图/块，隐含把地图当作更大总体的可交换抽样，与固定条件总体矛盾；因此它只能作为附注，标注为"地图超总体启发式，非固定条件总体的有保证区间"，不得充当主区间，也不得在主区间 UNESTIMABLE 时替补。
9. STRICT 统一总计算预算轨道为主比较；NATURAL 计算开销轨道为次要解释，单独报告、不与主轨道合池、不参与主结论。

不主张任何提升或已通过资格门；上述仅为分支完整性与可判定性的纸面补齐。未知项（如各机会的具体费用类别取值、cell 充分性判据的具体形式）此处明确写作：不知道，需另行授权绑定。

ADVICE-COMPLETE

## 回执结束

RECEIPT-COMPLETE；NONBALLOT；保持 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

