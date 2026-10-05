# R18 TEST 查询机制只读诊断

本诊断读取同一批冻结实验的 270 个 TEST episode（54 个 world，嵌套于 6 个地图×场景家族），核对全部 `RUN_RECEIPT.json` 与输出哈希。没有新增求解、反事实、参数选择或测试集再训练。可复算脚本和逐项输入哈希见 [mechanism_diagnose.py](parallel/maze-32-32-2/mechanism_diagnose.py) 与 [MECHANISM_DIAGNOSTICS.json](parallel/maze-32-32-2/MECHANISM_DIAGNOSTICS.json)。以下秒数属于固定路径、连续点事件模型；不是 ROS 物理运行、LMAPF 吞吐或生产收费结果。

学习策略相对完整公开 END 历史基线为 **53 平、1 优**，相对历史规则为 **52 平、1 优、1 劣**。非零差异集中于下列 3 个 world；这些配对不能当作 54 个独立统计样本。

| TEST world | 比较基线 | 基线→学习 ΣT | makespan 基线→学习 | 查询数 基线→学习 | 首次图差异 |
|---|---|---:|---:|---:|---|
| random s05 N32 bounded_pause | history_only | 1121.5→1112.5 | 68→68 | 0→32 | gate 2，t=12.25 |
| random s05 N32 speed_shift | history_rule | 1064→1067.5 | 61→62.25 | 32→32 | gate 3，t=16.25 |
| maze s04 N32 speed_shift | history_rule | 3325.5→3298.5 | 243→243 | 32→32 | gate 1，t=24.4167 |

三项的 START/END 物理前缀在首次图差异时均一致，采用图均通过共同 guard。首个公开选择差异更早，均在 gate 0；不能把 gate 0 的不同选择直接当作后续收益的单查询因果归因。

**random pause：过期的进度饱和值掩盖当前暂停。** gate 2 学习选择 agent14、31、4、1；agent14 的完整历史尚未包含这次暂停，history_only 将 `v_14_9` 进度估计为 1。POSITION 在 t=12 捕获 0.35，经 0.25 秒公共速率推进后输入作者优化器为 0.60。两臂在该 gate 的全部顶点状态、时长和进度输入中，仅此进度不同。学习图合法翻转 `dg_agent14_10` 和 `dg_agent26_4`，agent3 的 `v_3_13` 从 t=22 提前到 13 开始，最终 agent3 早 9 秒到达；其他最终完成时间不变。history_rule 也获得同一 ΣT=1112.5，因此该项不是学习模型胜过强规则的证据。

**random shift：相同预算下晚一个周期翻转。** gate 3 规则查询 agent28、22、11、19，学习查询 agent25、4、31、29，导致 5 个正在执行顶点的估计进度不同。规则在 t=16.25 翻转 `dg_agent16_5`；学习直到下一 gate 的 t=20.25 才翻转。agent17 的 `v_17_17` 因而从 t=18 延后到 20.25 开始，最终 agent16、17 分别晚 1.25、2.25 秒。两臂均在 gate 7（t=32）用尽 32 次查询；首次差异发生时预算尚足，不能解释成预算已耗尽。学习与 history_only 的 ΣT=1067.5 相同。日志定位了选择与翻转时机差异，没有分离每次查询的独立价值。

**maze shift：学习避开了规则的一次不利排序，但与无查询打平。** gate 1 规则查询 agent7、1、19、0，学习只查询 agent31；双方 4 个当前顶点的估计进度不同。学习在 t=24.4167 翻转 `dg_agent15_6`、`dg_agent4_9`，规则保持原方向。例如 agent18 的 `v_18_22` 从 t=29 提前到 25 开始，agent16 的 `v_16_25` 从 t=42 提前到 34。完整后缀中 agent16、18、2、25、8 分别早 5、6、6、5、5 秒到达，总计 27 秒。history_only 也为 3298.5；不可把这 27 秒解释为相对无查询的新价值。规则到 gate 7（t≈96.667）耗尽预算，学习到 gate 13（t≈169.167）才耗尽；该首次图差异仍早于两者预算耗尽。

## 查询时的公开机会覆盖

以下使用每次**已选查询在 capture 前的 public snapshot**，没有用私有扰动或真实未来打标签。`outgoing` 对应 `outgoing_blocked_agents`，`upcoming` 对应 `upcoming_switchable_influence`；占比分母为实际查询条数，不是 gate 或 episode。

| 策略 | 查询数 | outgoing=0 | upcoming=0 | 二者均为 0 |
|---|---:|---:|---:|---:|
| fixed_update | 1008 | 595 / 59.03% | 909 / 90.18% | 571 / 56.65% |
| history_rule | 794 | 0 / 0% | 691 / 87.03% | 0 / 0% |
| learned_query | 1000 | 817 / 81.70% | 999 / 99.90% | 817 / 81.70% |
| dense_position（不受预算限制） | 6009 | 3633 / 60.46% | 5486 / 91.30% | 3462 / 57.61% |

学习策略当前大量查询落在没有这两项即时公开影响的候选上。但“当前没有 outgoing/upcoming”**不等于**查询永远没有价值：全图时长目标、后续依赖、同一 occurrence 的未来预测和到达时机都可能受影响。不能凭这张表删除候选或宣称 81.7% 查询无效。

## 预算和翻转的时间关系

gate 从 0 编号。首次翻转指该臂第一次通过 guard 并实际改变作者组方向的 solve，可能完全由公开历史驱动，不能自动归功于查询。

| 策略 | 耗尽预算的 episode | 耗尽 gate 范围／中位 | 耗尽前已有翻转 | 耗尽但全程无翻转 | 耗尽后仍翻转的 episode／gate |
|---|---:|---|---:|---:|---:|
| fixed_update | 54/54 | 7–7 / 7 | 28 | 26 | 5 / 7 |
| history_rule | 21/54 | 7–10 / 7 | 14 | 7 | 4 / 6 |
| learned_query | 53/54 | 7–14 / 7 | 27 | 26 | 4 / 4 |

没有预算耗尽早于或处于自身首次翻转同一 gate 的记录。学习和固定策略更常用完预算，规则有 33/54 episode 未用完；这只能说明预算使用模式不同。耗尽后的翻转同样不能证明多买一次查询就会获益。

导师判断：下一轮应先检验**公开可切换决策窗口、排序对残余时长的敏感性、查询时机和不查询选项**，再判断是否需要更大回归器。当前证据更直接指向学习目标与实际可改变排序机会的覆盖不足；三个非零后缀也说明“测得更准确”不会稳定转化为更好 ΣT。该判断属于事后研究设计建议，须另行预登记和使用独立数据验证，不在本轮追加扫参或重训。

## 并行执行收据

maze 专用 worker 使用原 `run_benchmark.episode` 完成 90/90 个新 episode，全部 `completed`，session 11875 退出码 0。没有重跑完成结果或未完成 STARTED；主顺序进程在碰到 live STARTED 时的退出由 root 单独记录。见 [COMPLETION.json](parallel/maze-32-32-2/COMPLETION.json)、[PROCESS_EXIT.json](parallel/maze-32-32-2/PROCESS_EXIT.json)。helper SHA256 为 `1aee80ec48dfb044a269e8c052fec88d0a742846105b67d2e0d11197a6a4e7db`；所有科学源码 pin 和模型哈希保持不变。并行 host 耗时仅供诊断，不作策略运行时间优劣结论。
