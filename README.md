# LMAPF 空间误差与执行占用引导探索

2026-10-04 R16：**SADG作者连续时间核心已跑通，三条线路均有新增实作。** [三线科研导师复判](exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261004_R16.md) · [下一方法合同](exploration/error_guidance/NEXT_METHOD_CONTRACT_20261004_R16.md) · [SADG实现和完整结果](exploration/error_guidance/sadg_preflight_20261004_r16/REPORT.md)。

12次作者MILP均OPTIMAL，官方ECBS→SADG回归通过。两车小例连续进度改变合法顺序，实际后缀ΣT13.5→13.0；但完整公共历史速率也得到13.0，因此POSITION独立增益为0。warehouse映射10743动作及15789关系，隔离k0/承诺修补后两臂均通过原guard、采用图相同，未重复物理续跑。根独立核全部12组约束和两条完整后缀；原源码、适配版、失败和数据分开保存。下一检验同历史模型下、有时效与成本的信息是否仍有决策价值。以下旧轮次为历史。


2026-10-03 R9：[primitive时长模型](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/primitive_duration_20261003_r9/REPORT.md)修正队列等待混入标签的问题，6机械＋24新留出完成。hm/history/learned任务184/186/188；学习相对历史只在一个条件多2，其余7相同。12个primitive×方向组的预测MAE全部更差，两个条件零历史时已分叉。下一先分离离线几何先验与在线历史，再扩大验证。

[作者Improved GSES预检](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/gses_author_preflight_20261003_r9/REPORT.md)已跑通原始代码，四组成功；尚未与连续FIFO任务统一对照。保留作者原版结果，并另做固定路径依赖映射。[本轮Astra与科研导师分别判断、三线实绩](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261003_R9.md)。下方R8及更早为保留历史。

[R8三线结果与两类判断](exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261001_R8.md) · [下一方法合同](exploration/error_guidance/NEXT_METHOD_CONTRACT_20261001_R8.md)。

R8（2026-10-01）已完成合法两步缓冲内的局部依赖执行，6个机械验证及48个新留出全部结束。相同作者hm规划器的global/local总任务为174/200；同历史规则与学习模型在local均201任务，学习没有独立任务优势。根审重建全部ADG前驱ACK、正常服务与固定FIFO时间，另修正了转弯编码并重训冻结模型。新诊断定位到累计第二步标签与单步训练的单位不一致，下一步先统一监督目标。[完整结果与图](exploration/error_guidance/local_dependency_20261001_r8/REPORT.md)、[近邻及已发表基线](exploration/error_guidance/NEIGHBOR_COMPARISON_20261001_R8.md)。下方R7及以前保留为历史记录。

R7（2026-10-01）已训练新执行残差模型并完成42次真实运行。留出预测MAE由同历史规则9.386降至6.897 ticks，4/6场景实际动作改变，一个场景累计完成时刻少14.2秒；总任务模型/规则119、原作者hm120，尚无整体任务优势。原始失败、完整数据及root独立模型/服务核验均保留。

详见[当前探索入口](exploration/error_guidance/README.md)；[本轮Astra/科研导师判断与三线后续设计](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261001_R7.md)。下方旧轮次文字按历史记录阅读。

2026-10-01 R6 当前结果：[共同物理执行的 24 组作者方法实验](exploration/error_guidance/published_continuous_execution_20261001_r6c/REPORT.md)全部实际完成 800 秒并通过 FIFO、真实服务、动作及严格点 ACK 审计。两个地图、8/16 机器人、三个执行条件下，hm+GPIBT 共完成 780 任务，旧冻结 OnlineGGO 迁移模型 648；12 个配对全部旧模型较低。模型真实调用 154,434 次，但这不是新执行误差模型，也不是充分训练的作者学习方法结论。原错误配置的 24 组及 R6b 预检完整保留。

[三线结果与两份独立后评审](exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261001_R6.md)：主线完整收费查询已闭合，精确收据优化后统一 8m 合同成功、总实际费用净降 9.61%；查询线 70 次成功原生运行与 40 次留出已完成，主要条件下模型未胜 RR。[下一方法设计](exploration/error_guidance/NEXT_METHOD_DESIGN_20261001_R6.md)优先把真实进度证书接入在线任务/资源阻塞释放，再评价学习选择查询的边际任务收益。以下 R5 及更早文字是历史记录。

2026-10-01 最新（20260930_R5批次）：[真实误差模型36次执行](exploration/error_guidance/gpibt_lsmart_error_model_20260930_r4c/REPORT.md)已让预测改变官方动作和服务时刻，但学习/解析/历史全动作相同、完成任务数无增益；严格半MOVE点误差失败保留。[800机器人同未来任务流正式比较](exploration/error_guidance/paired_published_guidance_20260930_r5/REPORT.md)及[四官方地图64机器人试跑](exploration/error_guidance/standard_map_pilot_20260930_r5/REPORT.md)均已真实完成。训练模型、实际运行及原始归档已有完整结果，下面旧“尚未训练/待权限”只是历史阶段。

[三线更新与两份独立复判](exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20260930_R5.md)保留技术与导师的不同优先级；当前采纳共同执行误差平台优先，在其中验证查询价值，主线收敛证据消费/费用。[下一模型设计](exploration/error_guidance/LEARNING_DECISION_DESIGN_20260930_R5.md)与[MAPF／LMAPF实验规范](exploration/error_guidance/mapf_evaluation_20260930_r5/README.md)区分已运行的先导与尚待完成的正式规模实验。

2026-09-30 R2 当前分支更新：官方GPIBT/LSMART固定两臂均完整200tick并有真实任务服务，OnlineGGO官方OBJ4评估入口已运行但尚未取得合格训练策略。当前完整报告、独立核验及三线下一实验见[探索入口](exploration/error_guidance/README.md)。活动MOVE扰动与连续空间安全是下一项验证，原时窗只造成派发延迟；下方旧状态按其日期阅读。

2026-09-30 最新：官方GPIBT已接到LSMART的实际连续执行链，首步运动与END有真实记录；后续默认LNS邻域大于两机器人数量导致崩溃，已用作者公开group_size=2修复构建。最终两次200tick验证尚待本机RPC沙箱权限，未计为完成。当前交付见[同步执行适配协议](exploration/error_guidance/gpibt_lsmart_integration_20260930/PROTOCOL.md)及[2026近作核查](exploration/error_guidance/LITERATURE_DELTA_20260930.md)。它是公开适配R1，LSMART是试验台；旧机制结果及作者原生GPIBT先导保留，尚未证明学习残差或连续空间误差安全。以下原预检说明按其阶段阅读。

本次源码、补丁、构建记录及首步原始轨迹详见[适配报告](exploration/error_guidance/gpibt_lsmart_integration_20260930/REPORT.md)，另有[root独立工件/提案—执行映射复核](exploration/error_guidance/gpibt_lsmart_root_review_20260930.json)。

当前分支：`explore/error-aware-guidance`。从 `main@af17410` 建立，使用同一远端
仓库 `LYHrmer/MAPF_PIED_MDDR_RESEARCH`。本目录是独立 Git worktree。

| 分支 | 负责的问题 | 当前工作入口 |
| --- | --- | --- |
| [`main`](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/main) | PIE-D 误差执行、完整查询与实际费用闭环 | 主线当前进度 |
| [`explore/learned-query`](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/learned-query) | 在既有路径上选择查询对象，分离预测与组合决策 | 查询学习及合法 AND 预检 |
| **`explore/error-aware-guidance`（本分支）** | 固定空间误差安全层上，以执行占用/等待代价引导路径 | [误差引导探索](exploration/error_guidance/README.md) |

共同观察时机预检已通过 **3042 项断言**。非零误差下，t=2 的证书不足释放，
精确等号也不释放；t=5/2 观察使上绕恢复更快，t=4 则下绕更快。这说明本例的
路径排序取决于误差包络与证据时机，尚未证明学习有效。

结果与范围见 [时机预检](exploration/error_guidance/TIMING_PRECHECK.md)；
[夹具](exploration/error_guidance/timing_precheck.cpp)、
[运行器](exploration/error_guidance/run_timing_precheck.py)及
[完整证据](exploration/error_guidance/timing_run_20260924_01.json)可逐项复核。

下一步做“原 prefix / full-MOVE 授权 × 基础运动代价 / 加入解析等待代价”的
2×2 对照，先分离授权方式与等待估计的作用，再判断学习是否有独立收益。

本分支新增工作只放在 `exploration/error_guidance/`。继承的论文和历史文档是
分支起点快照；主线最新事实请看 `main`。主线未提交的主稿修改不属于这个分支。
