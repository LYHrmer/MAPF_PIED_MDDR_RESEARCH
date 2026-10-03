# R9三线实绩、两类判断与下一步（2026-10-03）

本轮完成了三条线的实际代码与实验，并新增作者Improved GSES可执行预检。结果支持继续研究学习辅助决策，但不支持“加一个模型即形成创新”。当前最有价值的发现是：查询等待会被后续规则很快补查，而误差模型的微小任务收益尚不能归因于更准的预测或在线历史。

实际分工：GPT-6-Astra/ultra子智能体完成主线及非盲技术后评；另一子智能体应用[research-mentor技能](/home/lyh/.codex/skills/research-mentor/SKILL.md)完成误差线及导师判断；查询子智能体完成同续策模型。根独立构建作者基线、复算主线费用/ELF、两支线模型和真实服务，再整合Git。模型与技能判断分开归档，没有把二者包装成盲审或两次独立统计实验。

## 三条线实际完成什么

|线路|本轮实现与运行|可确认结果|下一最重要的问题|
|---|---|---|---|
|main|同一个付费Center/root内，前后两机器人各两次原MOVE；四次正常服务及下一任务头；4最终臂|四服务16/17/19/20，462费用段闭合；六ELF隔离重编相同；Natural WAIT189,292,737、paid282,683,143|去掉预定t16之后的服务安排，事件驱动正常服务与查询结账并发，检验真实时间/费用取舍|
|explore/learned-query|6收集运行＋45完整反事实探针＋40新留出；同π₀尾策略、显式预算、三冻结模型|91成功；WAIT366任务，condition与三模型均367任务、123query；三模型逐world固定FIFO时间也同condition|把“暂缓一次”与“本次MOVE不再查询”定义成不同动作，获得有持续影响的价值信号|
|explore/error-aware-guidance|primitive监督修正、真实ridge拟合、6机械＋24新留出，原native/局部ADG不改|hm/history/learned184/186/188任务，学习仅一个条件+2；同轨迹12组运动MAE全部更差|分离离线几何先验与在线历史贡献；用作者强基线统一问题验证|

主线完整本地报告：[continuous_lifecycle R9](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/continuous_lifecycle_20261003_r9/REPORT.md)，公共摘要见[main Q2 §79](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/73Q2_MAIN_EXECUTION_IMPLEMENTATION_BINDINGS_20260914.md)。源码和运行仍保留本机ignored目录，公共main仅四份授权进度文档；原稿未改。有限预置FIFO未来描述符可见，服务日程固定，不能称为完整在线LMAPF吞吐结果或作者STATION。

查询完整证据：[R9报告](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/matched_tail_20261003_r9/REPORT.md)。只有16train/8cal query标签，另21个WAIT分支；训练主任务差全0，scalar3正8零5负，校准含query少1任务。history/nohistory各4/8、nobudget6/8实际将查询改为WAIT，不是模型没有参与；但24模型臂逐任务服务字典均同condition。history/nohistory在两个family推迟约0.101391或0.648609时间后，原尾策略又查同一MOVE，干预最终没有改变服务。24次替换全部单候选、全部在ordinal64切换前；不声称留出多对象排序或漂移后适应。固定前4项时间和WAIT43,915.333671，condition及模型44,331.3311765，因此相对WAIT的净+1任务与更差次级时间并列保留。

补充物理机制核查：14个真正改为WAIT的臂全部改变了RUN/物理END记录，但任务服务和planner请求仍逐事件同condition。被跳过的原查询有8次没有释放资源、6次确实释放了资源。因此模型有真实物理影响，只是没有传到最终服务，不能将零任务收益解释为模型或执行接口未接通。

误差完整证据：[R9报告](primitive_duration_20261003_r9/REPORT.md)。新标签D=E−max(A,Eprev)排除自身前序排队；半MOVE机械例17ticks不再错误标43ticks。使用原R7训练/校准数据拟合14,542运动行，R9测试前冻结。24测试的固定前10FIFO时间和hm/history/learned为2,233,212 / 2,237,230 / 2,232,200ticks，学习相对history有4个条件时间改善、4个相同，任务增量仅1/8。两个首次动作分歧发生于tick1、零在线history，支持“可能有离线先验作用”的假设，尚未证明历史自适应。4次socket启动失败、完整原始记录和删失均保留。

## 外部基线已从名单变为实际运行

新增[作者GSES预检与适配报告](gses_author_preflight_20261003_r9/REPORT.md)：[AAAI 2025论文](https://ojs.aaai.org/index.php/AAAI/article/view/34487)对应[作者STPG仓库](https://github.com/DiligentPanda/STPG)，提交、子模块、MIT许可和实际输入均可核。作者源码零修改，私有补齐SFML依赖后编译，原示例及四图两方法共9次运行完成。四个预先选定实例下Improved GSES4/4成功，基础GSES2成功2超时；作者超时回退和进程wall时间原样保留。

这是R0可运行证据。作者离散固定路径调度与当前连续FIFO重路由的目标/执行语义不同；单situation程序也没有输出新路径，故尚未独立全轨迹重放。不能把这些成本与本分支任务数混排来宣称优越。若改通行次序，先做共同固定路径与primitive依赖映射；若主张LMAPF重路由吞吐，继续保留同任务的hm+GPIBT/OnlineGGO作者实现。内部history/WAIT等只作消融，不冒充发表基线。

## Astra与科研导师分别怎么判断

[Astra技术后评](ASTRA_POSTEXEC_20261003_R9.md)强调：主线的任务/资源事务已经打通，但需要事件驱动才有及时性问题；查询零收益的具体原因之一是尾策略补查同一动作，先改行动语义而非放大模型；第三线预测MAE反证与几何先验混杂必须拆开。其只读查询原始流诊断另存 `ASTRA_QUERY_POSTEXEC_DIAGNOSTIC_20261003_R9.json`。

[科研导师后评](MENTOR_POSTUPDATE_20261003_R9.md)强调：面向SCI方法论文，应从清晰问题、作者基线和任务结果组织工作。当前优先正常服务/费用的共同口径、固定路径作者算法适配与几何先验消融，再按决策价值扩查询数据；不要用检查数量、网络复杂度或单个+2条件充当创新强度。导师的[实施前判断](MENTOR_PREEXEC_20261003_R9.md)保留，后评没有回填或修改本轮模型。

根的执行选择：保留学习路线，继续把模型限制在可由数据检验的决策环节。主线负责真实合法服务与费用；查询线研究有限信息的取得价值；第三线用正确primitive标签和作者算法检验误差引导。当前不合并三条线的任务收益，不以视频世界模型增加工作量，也不因一次小正例立刻更换整篇论文基线。

下一接口、消融、64臂建议矩阵和作者适配步骤见[具体方法合同](NEXT_METHOD_CONTRACT_20261003_R9.md)。正式扩量前先用新训练world确认动作能形成持续差异；之后冻结模型，在公开图、多任务family、统一误差/信息/资源条件下对比。R9冻结数据继续保留，不能用于挑选下一轮最好参数。

## 独立复核与仓库边界

- 根直接重算四个主线费用流，核实际六ELF、20,480bytes kernel与空目录重编，192父文件及用户原稿不变：本地主线 `ROOT_VERIFY.json`。
- 查询根用增广加权最小二乘重拟合三模型，最大系数差2.1e−17；读取40原始留出复核服务、固定FIFO、每个模型候选分数与选择：查询 `ROOT_REFIT.json`、`ROOT_HELDOUT.json`。完整91物理/π₀前缀/预算/尾策略/WAIT推进审计也通过。
- 第三线独立33,076个新primitive标签复核，根另从24原始事件流复算当前任务头、正常END及20tick服务和总指标：[ROOT_REPLAY.json](primitive_duration_20261003_r9/ROOT_REPLAY.json)。1634执行冻结项不变。
- 作者基线75个核心源码归档成员和八个实际输入逐SHA核对，日志保留缺依赖失败、成功构建、超时及全部结果。新查询raw分为五包，最大13.89MB；第三线34包，最大3.37MB。文件数和运行臂数不当作独立统计样本。

三条分支继续分开；各自入口更新R9，旧证据原样保留。主线原稿原有未提交修改不进入本轮提交。具体新提交与远端一致性在本机R9最终Git回执记录。
