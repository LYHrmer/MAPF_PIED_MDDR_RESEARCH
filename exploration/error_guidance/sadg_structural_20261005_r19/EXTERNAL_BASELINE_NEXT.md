# 外部对照与创新边界（2026-10-05）

本次只查论文、作者页面和作者仓库，没有下载、构建或运行新算法。结论是：**当前固定路径执行问题最该先补 Improved GSES；期刊执行误差路线优先做 WinkTPG 的接口资格审查。** 不能把“已能编译作者 SADG + 接入学习预测”本身写成新的调度方法。

| 方法与正式来源 | 作者代码／许可 | 与当前问题的关系及接入判断 |
|---|---|---|
| SADG，*Receding Horizon Re-Ordering of Multi-Agent Execution Schedules*，IEEE T-RO 40，2024，DOI 10.1109/TRO.2023.3344051 | [作者仓库](https://github.com/alexberndt/sadg-controller)，AGPL-3.0；本项目已固定作者 SHA 并保留原优化器 | 已有执行进度反馈、滚动重排、累计完成时间目标与递归可行性。R19 的变化是估计器、观测选择和记录接口，不是这些机制的首创。[作者论文](https://arxiv.org/abs/2312.04190) |
| Improved GSES，*Speedup Techniques for Switchable Temporal Plan Graph Optimization*，AAAI 2025（会议，非 T-RO） | [作者 STPG 仓库](https://github.com/DiligentPanda/STPG)，MIT；C++/Python、CMake，PBS/pybind11 子模块 | 同样在延迟下选择无环 TPG、优化执行代价，直接对照 MILP/GSES；更强启发式、组边、分支与增量实现已发表。最适合隔离“收益来自预测/查询”还是“更换求解器”。[正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/34487) |
| WinkTPG，*An Execution Framework for Multi-Agent Path Finding Using Temporal Reasoning*，IEEE **T-ASE** 23，2026，DOI 10.1109/TASE.2026.3688563 | [作者仓库](https://github.com/JingtianYan/WinkTPG-IEEE-TASE)有官方实现和小例，C++20/CMake/Boost；本次顶层目录未见 LICENSE，许可尚未核清 | 最接近期刊层面的执行时间不确定性／动力学处理，但输出为速度轨迹，观测与物理假设更强。不是当前 SADG API 的直接替换。[作者正式发表页](https://jingtianyan.github.io/publication/2026-06-07-winktpg) |
| OTIMAPP，*Offline Time-Independent Multi-Agent Path Planning*，IEEE T-RO，2023，DOI 10.1109/TRO.2023.3258690 | [作者项目](https://kei18.github.io/otimapp/)、[作者代码](https://github.com/Kei18/otimapp)，MIT；C++17/CMake，含计划与执行程序 | 是满足异步执行条件的路径规划方案。直接换入任意 ECBS 路径不能继承其结论；对照会同时改变路径和执行机制，适合作为另一问题设置，不能假装为同一路径上的查询消融。 |

WinkTPG 的论文明确在到达位置时接收实际到达时刻和当前运动学状态，并据此更新滚动窗口；还承诺一段已入队的动作。它处理的分布式延迟假设与本轮按 agent/action 固定的速度变化及暂停并不相同。因此“利用执行反馈改善执行”“考虑时间不确定性”“保持已承诺动作”均不是本轮独有机制。要公平接入，需先固定共同的速度／加速度限制、到达反馈与付费 POSITION 的可用性、终点驻留和冲突语义；其原生全状态反馈结果只能作为另标的参考，不能冒充同信息预算对照。[论文全文，尤其 uncertainty model 与 windowed planning](https://arxiv.org/html/2508.01495v2)

学习执行时间反馈也不是可以不查先例的宽泛创新点：官方 IROS 2026 MAPF 教程已有 learning-enhanced execution feedback 主题。这是方向已有公开讨论的证据，不等同于已核实某篇论文完成了本轮的 END 条件残余、带年龄 POSITION、结构 STOP 和预算组合。[官方教程日程](https://sites.google.com/view/iros-26-mapf-tutorial/schedule)

本地并非从零接 GSES。已有 R9 缓存固定作者 `25fb931eff03f1cce23a22a68ab42b7533f85ab3`，本次只读 `git rev-parse` 再次核到同一 SHA；PBS 与 pybind11 分别固定 `f1e08e1...`、`19a6b9f...`。R10 已导出作者完整图并独立重放；R13 已有 24 次中途 suffix 搜索、全图采用与活动承诺保护。旧输入属于已消费的机制实例，**无需重复原例，也不能计作下一轮留出测试**。[R10 报告](../gses_fixed_path_20261003_r10/REPORT.md)、[R13 报告](../gses_online_adoption_20261004_r13/REPORT.md)

这次沿固定作者源码进一步核清三个具体接口：

- 数值类型并不是整数：`COST_TYPE=float`，`Graph::delay(agent,state,delay)` 可以改变指定 type1 边；`EdgeManager` 可输入加权边。可是 Astar 的分支/终止条件用 `iTime-jTime>=0`，启发式含硬编码 `+1`，默认边权是 1。因此“存得下 float”不等于任意连续权重下保留搜索条件/启发式性质；尤其 type2 间隔改成实数后必须另核。[define.h](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/inc/define.h)、[Astar.cpp](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/src/Algorithm/Astar.cpp)、[heuristic.cpp](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/src/Algorithm/heuristic.cpp)
- 原 `NewSimulator` 明确只模拟整数步，`delay_steps` 是 int；reset 读取当前 type1 权重后减 1。R10 已实际验证默认／当前加权／未来加权图 cost 为 2/4/4，而原执行 cost 为 2/4/2；不能再把未来预测写入边权就声称原模拟器按它执行。下一接口应继续用共同事件执行器，作者搜索只返回顺序。[原模拟器](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/inc/simulation/new_simulator.h)、[已完成机械证据](../gses_fixed_path_20261003_r10/REPORT.md)
- `make_switchable` 固定 current+1 的出边；原状态是离散已到达索引，不能把 active MOVE 的目的地提前当作 current。R13 包装已将 active 保持在源状态，把其已满足入依赖暂时移出搜索，再按原方向恢复，核全图 DAG 与所有承诺。可复用这个设计，但 R19 的 grouped action／位置采样边界和公共信息合同仍须逐项重映射。[graph.h](https://github.com/DiligentPanda/STPG/blob/25fb931eff03f1cce23a22a68ab42b7533f85ab3/inc/graph/graph.h)、[本地 R13 包装](../gses_online_adoption_20261004_r13/author_online.cpp)

**明确优先级：先做 Improved GSES 共同 wrapper 的小规模资格验证，先于继续增大学习模型容量。** 原因是本轮已留存若干作者 MILP 返回 OPTIMAL 却违反线性行的候选，执行器正确拒绝后，最终差异会混入不同回退路径；这首先是求解接口可靠性和对照解释的问题。该判断不等于已经证明 Improved GSES 数值更稳、更快或更优。它应保留原作者 Astar，沿既有 R13 适配复用固定路径和活动承诺，预登记少量零误差、当前残余、未来加权、延迟观测及拒绝回退条件，并由独立 DAG/完成目标枚举核其结果。只有资格通过后，才扩展到同公共历史、同预算、同执行器的新留出矩阵。

整数尺度 60 可以精确表示门时刻的 1/12 网格、1/4 传输年龄和 0.35 等有理量，但不能精确表示学习模型任意实数输出，也不能精确表示作者 SADG 的 `EPSILON=0.01`。这些已知有理量共同可用尺度300；`1e-5` 是本项目候选残差容差，**不是作者模型间隔**。并且把 STPG 原 type2 单位间隔缩成 1/60 或1/300秒本身就是新语义；这需要共同 wrapper 和量化误差登记，不能用“乘 60”一笔带过，更不能称已经完成对齐。[作者 SADG 间隔常量及原约束](https://github.com/alexberndt/sadg-controller/blob/c2626d996121a9d6c128844a167b917db24418ac/sadg_controller/sadg_controller/sadg/sadg.py) WinkTPG 则作为随后期刊级跨框架路线，先核清许可与运动学／观测合同，再决定是否进入新矩阵。

当前可保留的窄主张是：在冻结的作者 SADG 求解与执行接口下，检验条件剩余时长、非学习强生存基线和结构查询／STOP 对有限预算执行的作用。它仍需完整外测、失败输入审计及上述真实发表对照；本轮观测到收益或零收益都不构成算法优越性或文献首创的证明。
