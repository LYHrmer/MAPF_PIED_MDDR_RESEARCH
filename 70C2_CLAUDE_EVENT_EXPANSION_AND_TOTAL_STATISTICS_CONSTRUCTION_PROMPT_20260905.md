# 70C2：后继事件语法与缺失臂统计的建设性协作任务

任务日期：2026-09-05。你是 Claude Opus 的建设性协作者，NONBALLOT；不是任何正式科研导师、Nature 或独立逻辑审查。只根据本提示给纸面规格建议，不读文件、不用 skill、不调用任何工具/网络、不生成代码、测试、仿真、载荷、参数值或结果。最后必须以 ADVICE-COMPLETE 结束。若不知道，明确写不知道。

背景：多机器人保留 PIE 唯一原 MOVE；共同连续物理底座、持久独占资源事务和可信查询是各公平对照共有。控制外层只能保留原 MOVE、合法驻留 HOLD、推进/保有旧事务。候选 70 已固定，三路正式审查正在按序进行；你的建议只为收齐三路后另立新编号准备，不能改 70。保护符号 H、T_delay、B_CAL、B_max、B*、P_active、density N 原义不变且不得赋值、给范围/默认/先验/调参建议，也不得借同名定义新含义。

请构造两项最小而完整的补充（中文正文不超过约 4000 字，不复述背景）：

一、把机会表变为闭合且确定的事件流。
现有字段：(event_id, block_id, stream_domain, semantic_key, parent_event_ids, type, actor_id, recipient_id, occurrence, tid, resource_id, generation, logical_emit_time, delivery_time_or_missing, innovation_ref, ordinary_payload_or_certificate_ref)。
原闭合 type：PROPOSAL_READY、PREPARE_REQ/ACK/REJECT、DECIDE_REQ/RESULT、START、PROGRESS_SAMPLE/RESULT、TERMINAL_LATCH、ORDINARY_REPORT、DUPLICATE、DROP、PARTITION_ON/OFF、CRASH、RESTART、QUERY_OPPORTUNITY、PROCESS_SLICE、MODEL_BREACH、RUN_STOP。
但文字又依赖未编码的公共执行器机会、公共普通报告机会。起步失败发生在已有 COMMIT 未 START 的 tid，失败须消费 attempt ordinal；不能因无 START 而压缩后续键。普通报告机会先由各方法自身物理状态产生普通 payload，随后施加同类错误操作（STALE、FALSE_COMPLETE、WRONG_POSITION、DUPLICATE、DROP/REORDER），某方法没有对应发送/请求则 NO_EVENT，不能借别的方法真值。真实状态只给仿真 oracle/物理模拟器和已声明可信样本服务，不能泄漏给候选调度。
还有 R0 式任务服务机会：每 agent 每次服务至多完成队首一个已分配任务，判断实际驻留是否位于其任务顶点；在途不完成任务。任务真值计分与算法获知该完成必须区分，后者依已计费的合法证据/通知。
请给最小扩展枚举、所有机会的 ordinal 定义/无动作分支/父事件/费用/同时刻总序以及一个确定的 Expand(manifest, state, key)-> finite event list 数学描述。处理零时长事件递归、失败请求、重复/重排、多 agent 同时刻、launch 前尚不存在 tid，必须有总返回，不可用“未来实现决定”。具体时间表、分布表和费用未授权绑定时只能 UNINSTANTIATED；不给任何具体值。

二、把主配对统计函数定义完整。
每合法公共 roster block 的 full 和固定 control 必须留在分母账本；正 declared exposure 提前固定。已 launch 后 crash、timeout、主动方法停止、数值不确定都是科学结果，不重试；实际已完成数 Q 在终止后评分扩展为零新增任务至 declared cutoff，Y=Q/declared exposure。这不是补模拟剩余物理过程。基础设施可在 launch 前按预声明规则重试，但若到截止有必需臂从未 launch，目前 Y 未定义，不能静默删该 block/重归一化/假装 Y=0。最小可接受方案可直接：任意必需臂缺失则主估计量/置信区间为 UNESTIMABLE，同时完整报告观察臂和缺失原因；不用为了填数而引入新插补理论。
条件总体为固定公开类别/地图/源记录/预声明因素 profile 集合，随机性仅为独立重复根创新；地图不是从更大地图总体随机抽样。固定层级权重对 paired differences 加权；agent/tick 不是独立样本。请说明如何不把 cluster bootstrap 误称固定条件总体的有保证区间（可给明示假设/不可估分支），且 STRICT 统一总计算预算轨道是主比较，NATURAL 计算开销轨道为次要解释。不给样本量、阈值或保护参数任何值。

要求：每项给一个简短纸面反例说明为什么缺该分支会改变公平比较，再给精确补充。不要声称已有提升或通过资格门。任何证书、普通 payload、oracle 信息通道必须严格分开。

