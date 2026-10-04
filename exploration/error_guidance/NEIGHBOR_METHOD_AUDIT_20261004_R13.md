# R13 近邻全文与作者接口核查

2026-10-04。实际 Astra-ultra 只读核查；未增加实验，未改冻结实现。目的为下一方法合同排除已有贡献，并核实三 option 的最小接入能否成立。以下“下一步”均是设计，不能计入 R13 完成结果。

## 全文结论与未知项

本次读取两篇 arXiv 全文的建模、方法、算法与实验章节，另核对作者主页、STPG 官方说明及本地固定提交的原作者源归档。没有用摘要代替方法核查。

| 核查项 | Should I Replan? | REMAP / ESADG |
|---|---|---|
| 可见输入 | 实际/估计动作时间、完成和分配进度、等待与依赖等 ADG 特征 | 候选 ADG、动作与图特征、机器人运动学参数 |
| 有价位置证据 | 所述方法没有 POSITION 购买合同 | QueryOracle / QueryPredictor 是模型计算调用，没有所述物理证书购买合同 |
| 完整后果监督 | 同扰动下，不重规划与一次重规划的真实完整 SOC 差 | ExecTimeNet 学习执行结果；候选按预测执行目标比较 |
| 已承诺动作 | 跟踪执行状态；本次未从方法说明确认与 R13 同等的活动后缀提交 guard | ADG 完成确认及入队规则明确；ESADG 给出可逆群和无环修复，未确认活动后缀提交 guard |
| 求解耗时 | 额外报告求解时间乘未完成机器人数量；不进入训练目标 | 搜索有 wall-clock 预算，另测模型/优化开销；未确认把求解等待插入连续运动 |

Should I Replan 的依据是 [§III–IV](https://arxiv.org/html/2604.25567v1#S3)、[标签与开销式 (3)/(4)](https://arxiv.org/html/2604.25567v1#S4.SS2) 和 [§VI-C](https://arxiv.org/html/2604.25567v1#S6.SS3)。不能把完整后果标签、调用门控或考虑求解耗时单独宣称新颖。REMAP / ESADG 的依据是 [ADG 执行规则](https://arxiv.org/html/2511.21886v2#S2.SS2)、[REMAP 门控](https://arxiv.org/html/2511.21886v2#S4.SS3)、[ESADG 算法 2](https://arxiv.org/html/2511.21886v2#S5.SS3) 和 [实际执行评估](https://arxiv.org/html/2511.21886v2#S6.SS3)。不能把固定路径图重排加预测时长单独宣称新颖。

本次未定位并验证这两项学习方法的完整作者实现与训练权重。已查论文外链、[ExecTimeNet 作者页](https://jingtianyan.github.io/publication/2026-06-21-exectimenet)、[作者 GitHub 主页](https://github.com/JingtianYan) 及 CVUT 作者检索；部分目录/主页请求失败。这里的结论是代码资格未知，绝不是断言作者未公开代码。也不能从没有描述推出作者必然缺少某安全机制。

## 最直接可复现的外部对照

我选择原作者 **Improved GSES** 作为下一阶段直接运行的固定路径外部对照，同时保留 GSES 配对。其 [AAAI 2025 论文](https://ojs.aaai.org/index.php/AAAI/article/view/34487) 与 [固定提交官方 README](https://raw.githubusercontent.com/DiligentPanda/STPG/25fb931eff03f1cce23a22a68ab42b7533f85ab3/README.md) 可核，R13 已实接作者求解器并采用异图；不是自行实现的弱启发式。固定源提交为 `25fb931eff03f1cce23a22a68ab42b7533f85ab3`。

公平接口应固定同一合法 checkpoint、相同可见输入、作者搜索上限、同一个 adoption guard、相同完整后续物理执行，并保留超时/拒绝/无变化结果。公开状态的“调用或继续”学习对照还应采用 Should-I-Replan-style 完整尾部价值门控；这是论文定义的适配实现，未取得作者代码资格前不能标成该作者软件复现。Improved GSES 解决真实求解基线问题，却不能单独证明学习门控超过最近学习方法。

## 作者权重到 R13 采用的实际缝隙

这里同时读了本地 `gses_online_adoption_20261004_r13/AUTHOR_SOURCES.tar.gz` 中的原源与新适配器。原源 SHA 列于 [AUTHOR_SOURCE.json](gses_online_adoption_20261004_r13/AUTHOR_SOURCE.json)；在线源文件请求有 cache miss，以下固定提交链接提供精确定位，不暗示失败请求取得了内容。

1. **作者不是整数类型，但不能因此宣称任意小数正确。** [inc/define.h:5](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/inc/define.h#L5) 定义 `COST_TYPE float`；[EdgeManager:20](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/inc/graph/edge_manager.h#L20) 存储权重；[Graph::delay:207](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/inc/graph/graph.h#L207) 能修改当前边；[longest paths:209](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/src/Algorithm/graph_algo.cpp#L209) 确实使用这些权重。故当前边估计能进入真实候选评分，不只是写入日志。
2. **搜索仍含单位间隔假设。** [Astar:203/217](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/src/Algorithm/Astar.cpp#L203) 与 [最终定向:458](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/src/Algorithm/Astar.cpp#L458) 用 `diff >= 0` 检查冲突；[heuristic:142/153](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/src/Algorithm/heuristic.cpp#L142) 含 `+1`。例如两端时间差不足 1 的小数情况，不再能从严格先后直接推出单位 type2 间隔。此处是失去适用依据的源码诊断，并未运行新反例证明算法整体失败。把全图乘尺度也会碰到这些写死常数，不能作为无改动捷径。
3. **本轮适配另有限制。** [executor.py:19](gses_online_adoption_20261004_r13/executor.py#L19) 只接受当前边整数且至少 1，未来边固定 1；[author_online.cpp:29](gses_online_adoption_20261004_r13/author_online.cpp#L29) 才转入作者权重。最小新合同可先事前固定 `max(1, ceil(残余时间估计))`，未来/type2 仍单位。代价是所有小于 1 的残余都折成 1，可能完全抹掉付费进度差。这是需要先测的敏感性瓶颈，不应通过事后放宽量化解决。
4. **当前入口会拒绝证书修改后的包。** [online.py:78](gses_online_adoption_20261004_r13/online.py#L78) 要求 `public == public_input(engine)`。下一版必须明确区分不变的 `public_base`、身份/时点验证后的 `paid_evidence` 和由两者生成的 `search_view`。不能直接篡改 public 包后删除相等校验。候选 type1 应与该 search_view 匹配；[merge_candidate:65–74](gses_online_adoption_20261004_r13/online.py#L65) 已有只取候选 type2、恢复原执行图的缝隙，可在新合同中保留这一原则。
5. **剩余时间只作预测，不能成为完成证明。** [executor.py:83](gses_online_adoption_20261004_r13/executor.py#L83) 要求依赖源实际到达；只有 [ARRIVE:111–113](gses_online_adoption_20261004_r13/executor.py#L111) 推进 `state`。[adoption_guard:28](gses_online_adoption_20261004_r13/executor.py#L28) 保持路径、current、执行 type1 和活动边入依赖；[online.py:85](gses_online_adoption_20261004_r13/online.py#L85) 另保留已经满足的方向。POSITION 不能冒充 ARRIVE，不能提前推进 current。证书本身也不自动证明未来速度、暂停或精确剩余时间；估计只能使用证书允许字段、合法公开知识与事前训练模型。

因此第一版仅改变搜索估计/候选排序，采用后所有 active guard、原执行 type1、队列和资源状态仍保持。若改用细粒度 fractional 估计，需显式适配并验证搜索假设；若改为认证早释放，更需要独立执行语义、正确性论证和连续验证，两者都不是 R13 已获得的性质。搜索输入也应独立构建；作者 `deep_copy` 明确复制 EdgeManager（[graph.h:350](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/inc/graph/graph.h#L350)），不能让可变权重通过别名污染原执行图。

## 公开粗进度与付费增量：先资格，再学习

[public_input:36–44](gses_online_adoption_20261004_r13/online.py#L36) 已公开 phase、实际到达状态、占用格、资源和当前承诺；`CELL_ENTER`/`CELL_EXIT` 会改变占用（[executor.py:95–108](gses_online_adoption_20261004_r13/executor.py#L95)）。所以无 POSITION 的对照也知道一部分开放动作进度。统一合同应保留调度器合法拥有的发车时刻与公开事件历史，不能故意只给弱化快照以制造购买收益。当前 C++ 作者适配只读取 `solver_graph`；额外公开占用并未直接转为剩余权重，这说明存在建模缝隙，不证明必须付费。

下一步先做小规模、事前登记的完整三 option 配对：继续原图；用完整合法公开信息估计后调用作者方法；购买一次证书后更新同一估计并调用同一作者方法。先逐层检查证书是否带来公开条件下不能获得的精度/认证增量、量化权重是否改变、真实候选是否改变、guard 后后续执行是否改变。证书费用与来源必须真实入账。若 option 2/3 相同，应报告实际信息或量化瓶颈，不能加网络后宣称解决；若只是认证资格不同，应称认证价值，不称新信息价值。

当配对确有正负完整后果，再学 `ΔΣT/n` 并单列 makespan 约束与费用硬预算/Pareto。这保留了第三线真实采用和查询线完整尾策略学习的共同对象。相对于近邻，值得争取的区别是**有明确价格与可见性边界的物理证据，怎样改变既有执行承诺下的候选/采用价值**；目前尚未证明这一差异带来独立收益。重复“预测执行时间后决定是否重规划”不足以形成该贡献。
