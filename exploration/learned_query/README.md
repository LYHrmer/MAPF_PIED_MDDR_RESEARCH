# 学习辅助进度查询：探索说明

2026-10-03 R10：[持续SKIP实现与156次原生运行](skip_occurrence_20261003_r10/REPORT.md)已完成。SKIP绑定当前agent/action，到accepted正常END才清除；42次安装、118次重现屏蔽与后继资格均核验。48留出WAIT348任务，condition、once WAIT/SKIP及有/无历史模型均344，非WAIT均128query；模型没有新增任务或服务序列收益。

根的[机会改进空间诊断](skip_occurrence_20261003_r10/ROOT_OPPORTUNITY_HEADROOM.json)发现：30个已登记TRAIN/CAL机会的全部98分支，最佳单次动作相对原condition主任务提升空间为0；唯一QUERY+1标签只是胜过当前WAIT。下一应先识别有真实任务后果的合法决策集合，不靠加大模型解释当前零增益。代码、冻结模型、9个互斥raw包与6份root核验工件完整发布；[三线判断及下一合同](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261003_R10.md)。以下R9及更早为历史。

2026-10-03 R9：[同续策预算价值实验](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/matched_tail_20261003_r9/REPORT.md)已完成91次成功原生运行，包括40个冻结留出。24个query标签和21个WAIT分支明确比较“当前选择后均继续同一π₀”，三模型实际训练部署。WAIT366任务；condition与history/nohistory/nobudget均367任务、123query，逐world固定FIFO时间也完全一致。没有新增学习收益，+1来自原condition策略。

本轮修正了估计目标，但16个训练query标签的主任务差全部0；下一优先增加真实决策分歧与可用训练信号，再检验历史/预算作用。生产COST尚未接入。[三线判断与后续设计](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261003_R9.md)。下方R8及更早为保留历史。

2026-10-01 R8：[分层价值学习报告](stratified_value_20261001_r8/REPORT.md)已完成115标签、同架构有/无历史ridge及真实部署。123个WAIT/探针全部完成，48个N16留出任务WAIT346、普通RR/条件350、分时条件344、有/无历史345；12个N32兼容后继依次171/170/169/166/168。183个成功物理运行和原12个启动上限失败全部归档，后继只改N≤16为N≤32，没有更换场景或模型。

[完整任务/查询配对图](stratified_value_20261001_r8/ROOT_FIGURE_CAPTION.md)包含全部10个留出world，IID/SHIFT按同family处理。有历史模型未胜普通规则、WAIT或无历史模型；下一步使用同冻结续策的预算优势数据，先一次学习替换再扩多次干预。[Astra/导师判断与三线实绩](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261001_R8.md)、[具体方法合同](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/NEXT_METHOD_CONTRACT_20261001_R8.md)。以下均为此前轮次记录。

2026-10-01 R7：[持续在线 FIFO 与查询学习](online_fifo_20261001_r7/REPORT.md)已完成持久作者planner、公开承诺frontier、原资源依赖和异步执行，60有效native全部达到H128、当前窗口0死锁。24同前缀反事实训练同架构有/无历史ridge；20留出合计WAIT180、RR179、条件179、历史178、无历史180任务，查询分别0/64/64/14/0。历史模型没有任务优势，无历史实际选择全部WAIT。多候选训练已覆盖，但历史模型测试时的12个有预算多候选机会均等待，不能声称已学会排序。

[原始证据、失败与核验](online_fifo_20261001_r7/PUBLICATION_MEMBERS.json)完整冻结：60臂独立物理/资源/FIFO/特征/选择重放、8负控及root独立label/拟合复算通过。公开作者代码和地图不等于原作者完整benchmark，内部规则只作消融。[本轮Astra/科研导师判断与三线下一设计](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261001_R7.md)。以下R6及更早记录为历史状态。

2026-10-01 R6：[16机器人共同执行与历史价值训练](public_joint_20261001_r6/REPORT.md)完成6机械臂、24训练/校准反事实臂、40留出臂，实际训练并运行同架构有/无历史ridge。IID/SHIFT中模型与RR的任务和物理执行相同，尚无学习独立收益。全固定组中的静态循环、末任务驻留及两个旧超时均保留；下一步接合法依赖保持执行或作者在线任务接口。[根独立复核](public_joint_root_review_20261001_r6/README.md)重拟合权重并复算320选择/324分数，不能把来源公开的静态轨迹机制称完整PIE-D或正式LMAPF对比。下列R5及更早内容为阶段历史。

2026-10-01 最新（20260930_R5批次）：[历史模型实验](public_history_20260930_r5/RESULTS.md)完成156原生臂及同架构有/无历史真实训练，但14留出world全无合法查询机会，不能评价模型收益。[事件查询后继](public_history_events_20260930_r5b/REPORT.md)完成24机械臂，RR/条件规则各19次真实查询，最多同时1候选；已验证多次查询时机，尚无多agent竞争或新学习优势。

[更新后三线实绩与两份独立复判](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20260930_R5.md)明确下一步：以共同执行误差平台和完整公开任务流承载查询价值检验，主线继续必要的消费/费用闭环。所有模型、失败、原生raw归档与核验保留；下面R2及更早说明属于历史快照，旧“尚未训练/待运行”不代表当前状态。

2026-09-29 接续：[当前任务流时目标结果](OBJECTIVE_TASK_RESULTS.md)与[独立导师审查](OBJECTIVE_TASK_MENTOR_REVIEW_20260929.md)已完成。六组98次完整episode、882任务；同一AR/lag2预测下慢例C→AB，全程flow40→39，同时多查询一次。快例冗余查询及隐藏突变损失保留，AR仍与lag2同效。最终六组native成功，原wrapper分析失败保留，独立offline恢复重算72次选择/596候选及旧62项结果通过；没有追加native重跑。active/不可行输入分支没有本表运行覆盖。这是目标消融，不是外部baseline或净收费收益。[复核入口](objective_task_recover.py)与[98行完整结果](objective_task_results_20260929.csv)已归档。

下一步接主线真实查询费用、在新公开任务中覆盖active状态并验证泛化；外部论文基线遵循[三线共同设计](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/RESEARCH_DESIGN_AND_BASELINES_20260929.md)，内部规则不替代PIE-D/GPIBT/OnlineGGO作者方法。以下为此前时序预测与机制结果。

最新[时序历史—任务后继](TEMPORAL_TASK_MODEL.md)已通过六个固定实例、62个完整评价episode（558任务、744条requester MOVE，30,900项native检查）。实际训练AR(1)，与last/mean3/median3/lag2同信息比较，并接入明确人工native报价的原SRDC PositiveScore诊断。AR与lag2完全同效；准确预测在短窗口规则下也未必改善全程流时，隐藏突变负结果保留。新增[事前方法合同](TEMPORAL_TASK_CONTRACT.md)、[完整CSV](temporal_task_results_20260929.csv)及[原始回执](temporal_task_run_20260929_03.json)。当前没有独立学习优势或生产完整费用收益证据。

最新[历史时长拟合闭环](CALIBRATED_TASK_MODEL.md)已实际训练并运行，4376项检查通过：模型从此前独立MOVE的已交付END记录拟合时长，再参与查询/WAIT选择。合法较快条件下，拟合模型比固定先验少查询一次、任务曲线相同；较慢条件仍查C。单END解析校准与拟合相同，因此有历史适配收益，尚无学习优于解析或完整净费用证据。下面连续任务报告是此前阶段记录。

最新[连续任务后继](TASK_CONTINUATION.md)已通过3488项检查：每个机器人真实执行多段首任务并续接后两任务，共9个任务、12个requester原MOVE。完成导向只查C即可取得贪心查CA的同一任务完成曲线；AB与C在不同服务时刻互有领先，最终都完成9个任务。未查询blocker正常END，避免人为永久阻塞。当前模型是声明的解析先验，尚未运行学习器或完整付费服务。

最新完成[决策—立即执行比较](DECISION_EXECUTION.md)：321项断言通过，原 SRDC 无报价时确实回退 RR，与两步前瞻同选 AB，尚无超越原选择器的证据；单步 CA 在较早截止反而先完成一个 MOVE。这一结果支持将后继目标改为预计完成量，而不只统计准入数量。具体新接口、公平对照和已运行范围见该报告；本轮没有运行学习器。

创建及更新：2026-09-24。状态：轻量概率模型、影子评分器及[估计／决策分离诊断](DECISION_ABLATION.md)已建立；后续已完成[组件已提交状态到模型入口的验证](COMPONENT_VALIDATION.md)，57 项 Python 检查及29项人工输入的真实 C++ 组件断言通过。[数据接口契约](DATA_INTERFACE.md)中的生产外层接线仍未完成。训练仅发生在明确标注的人工软件样例上，没有研究数据、原系统实验或吞吐收益结论。[独立评审](REVIEW_20260924.md)支持继续验证实际组合查询价值，保留原评分作对照。运行命令和限制见[实现说明](IMPLEMENTATION.md)。

新增[组合阻塞合法几何预检](legal_and_precheck.md)：真实 Geometry/Index/PositionCommit 与同原 MOVE ReferenceController 上 530 项断言通过，两个需求确需 A/B 两责任都退休；两次固定查询机会下 A→B/B→A 可准入 2 个需求，其余四种顺序为 1。它是人工 native 机制与可达性见证，未接生产 AUTH、完整费用或任务完成链，不是学习收益。

## 工作区与基线

- 分支：`explore/learned-query`。
- 工作区：`/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE`。
- 起点提交：`b7ce69ff52b1edc8d4494fbc694218de036da255`。
- 主线目录：`/home/lyh/MAPF_PIED_MDDR_RESEARCH`，继续位于 `main`。
- 主线已有的 `MANUSCRIPT_PREEXPERIMENT.md` 未提交修改未带入本工作区，也未暂存、提交或覆盖。

Git 起点只固定已跟踪文件。主线的 `implementation/` 及本次参考的查询算法合同尚未纳入 Git，本工作区不会自动包含它们。后续需要实现时，应明确最小源码依赖和来源版本，在本工作区建立独立副本；不通过可写软链接修改主线，不把当前目录称为完整可运行副本。

本地只读参考：

- [当前研究说明](/home/lyh/MAPF_PIED_MDDR_RESEARCH/RESEARCH_BRIEF_FOR_ADVISOR.md)
- [当前进度](/home/lyh/MAPF_PIED_MDDR_RESEARCH/GITHUB_PROGRESS.md)
- [查询算法合同](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/query_scheduler_contract_20260919.md)
- [查询实现入口](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation/pie_query/README.md)

以上路径指向本机参考材料，不是本分支已固定的源码快照。当前进度记录只支持最小原生释放机制与独立费用反馈分别通过，尚无完整费用链运行、净吞吐或规模性能结论。

## 首个研究问题

在相同合法信息、执行安全规则与在线资源约束下，小型监督模型能否比现有割线预测和利用已知控制约束的简单预测，更有效地选择进度查询，并提高真实任务完成量？

第一候选只预测：此刻查询指定机器人，返回的合法进度证书能否严格越过指定空间释放阈值。暂不加入完整世界模型、端到端运动控制或强化学习。低预测误差、较多释放与较高吞吐分别评价，不互相替代。

## 特征与标签

特征只使用选择时已经合法获得的信息：历史证书下界及捕获时刻、信息年龄、观测精度、当前认证进度、中心授权上界、阈值距离、合法可见的授权反馈、依赖关系和已交付费用/延迟记录。中心授权上界不能冒充本地已安装权限；缺失的信息应显式表示，不能用模拟器真值补齐。

每条样本绑定运行、查询、原 MOVE、选择视图及当时冻结的关系阈值。对返回且身份有效的证书，以其实际下界是否严格大于该阈值作为跨阈值标签；不使用交付时刻的真实位置，不把证书中点当真值。证书是否有效、动作是否仍匹配、资源是否实际释放、需求是否获准执行、任务是否完成分别记录。

非法返回、超时和未完成查询单独保留状态；未查询对象没有标签，不能标为失败。未完成记录也不能直接混入条件于有效返回的二分类标签。若后续目标扩为“按时取得有效证据的概率”，需先定义时间窗与删失处理。

记录候选集合与行为策略，检查选择性观测造成的覆盖不足。训练、验证、测试按完整运行和场景分组；同次查询产生的多个关系样本放在同一组。跨地图与执行条件的泛化单独检验。线上输入不得包含未交付证书、未来扰动、未来任务或私有世界状态。

## 方法与对照

先从逻辑回归或小型树模型等低成本方法开始，模型选择由数据覆盖和验证表现决定。对同一证书的多个阈值，概率应随阈值增大而不增，避免互相矛盾的预测。

保留三类机制对照：原割线预测、利用已知授权/等待约束的简单预测、小型学习预测。候选集合、可用信息及安全规则保持可比。如果将 SRDC 的二值预计消障改为概率期望评分，应作为新候选策略，另设相同评分接口下的简单预测对照，区分评分变化与学习本身的作用。

终点保留责任、权限不足等已知不可释放条件继续由规则判定。预测只辅助查询选择；实际释放与执行授权必须经过原有可信证据及几何检查。安全结论仍依赖原模型与实现条件，不能由预测准确率推出，也不自动得到公平性或吞吐保证。

主要比较固定时间内真实任务完成量；同时解释无效查询、错失释放、等待、失败、概率校准与排序错误。新增推理和维护工作必须进入在线资源比较，离线训练成本单独报告。现有 B1 工作量与宿主/GPU 耗时不是可直接互换的单位，实现时需明确计费对应关系，不把推理作为免费服务。

这些简单策略是机制对照，不包装成已发表外部方法。正式研究仍需适用的外部参照。

## 后续推进与取舍

1. 核对已有合法日志是否足以形成上述样本，以及最小实现依赖；当前先做源码和接口工作，不读取受限实验载荷。
2. 在可比较的非学习闭环和数据形成后，验证小模型能否改善决策；不要求先做完全部规模实验才探索。
3. 若主要损失来自多步查询互补性，先比较简单短时域搜索。只有搜索有效但昂贵时，再考虑模仿学习或图排序模型；不把前瞻收益全部归于学习。

继续或收缩的判断：

- 学习模型应在按运行/场景留出的评估中改善与决策相关的预测或排序；若不能优于简单模型，停止增加模型复杂度。
- 计入推理、维护及查询成本后，需有可重复的任务收益才能主张方法有效；释放更多本身不算成功。
- 若改进主要来自多步搜索，转向查询组合调度；若主要受限于计算、查询服务或固定占用包络，优先研究对应瓶颈。

可以使用未来真值作明确隔离的诊断，但固定启发式使用真值后的表现不自动构成最优性能上界。

## 本轮范围

用户随后要求先推送主线与探索分支、再继续探索，并明确允许 Claude Opus 协作。两分支已先行推送，主线未提交稿件仍留在原工作区。本轮新增独立 Python 原型及纯合成软件检查，未运行原有 guest、world、仿真或研究实验，未读取受限载荷、赋原研究保护参数或改写主线实现。候选模型没有接入真实执行；相关实现和费用边界见 [实现说明](IMPLEMENTATION.md)。

方法依据：[Learning to Resolve Conflicts for Multi-Agent Path Finding with Conflict-Based Search，AAAI 2021](https://ojs.aaai.org/index.php/AAAI/article/view/17341)展示以监督排序近似昂贵冲突选择；它是设计参照，不是可直接使用的查询调度外部基线。[Planned synchronization for multi-robot systems with active observations，Autonomous Robots 2026](https://link.springer.com/article/10.1007/s10514-025-10225-4)说明有成本观测与后续动作联合规划已有研究，新增学习模块本身不构成新颖性。
