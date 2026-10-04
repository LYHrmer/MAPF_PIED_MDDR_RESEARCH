# R14：补齐证据正文与搜索接口，按内容复用既有实验

本轮优先完成 R13 留下的接口工作，并将“避免重复实验”落实到运行器。没有重跑主线十二臂、查询160臂或第三线36条轨迹。新增工作为一次主线证据观测和一次真正不同输入的原作者 GSES；查询只分析冻结结果，第三线没有新增物理续跑。

|线路|本轮新增实现|实际新增运行|复用与结论|
|---|---|---|---|
|主线|真实付费 SOURCE 返回值导出、POSITION wire/JSON、身份/时效/来源/费用绑定消费接口|1次 host 编译、1次原 guest 执行，用于补此前未归档的正文|原3个 guest 不变，429原事件与291费用段逐项相同；不是新性能样本|
|查询|完整尾策略价值数据接口、逐family任务风险/时间空间、内容缓存|0原生、0训练|复用160臂，导出48个C/LD配对；TEST两尾选择的任务上界仍等于固定LD|
|第三线|public_base→独立测量核验→search_view→原作者GSES→原guard/lift；输入和续跑两层去重|1次GSES，0物理续跑|23次solver请求复用；36结果记录复用24条唯一旧审计轨迹；位置证据未改变实际采用图|

## 主线：正文及实际费用可以核对，统一执行域仍需接入

本机实现：`implementation_binding_evidence/position_search_bridge_20261004_r14/`。新增host观察器只记录实际已返回给guest的付费SOURCE字，没有额外读取受保护正文，也没有导出禁止读取的private serial。一次 length12 paid / Natural 的358字节POSITION body由64个合法可读word还原，完整请求身份、精确数值与捕获/送达时点可以独立核对。原guest、输入和收费过程保持。

根独立从原始返回流解码，核85项事前producer绑定、429条原事件、291段费用：总实际工作344,352,218，与原R13逐项一致。选择、查询、结账账户0/1/3合计34,040,033；共享业务账户2单列，不能把前一数字包装成POSITION的因果边际成本。新增host记录是未计入guest收费的审计元数据。

JSON是可溯源的归档证据表示，不会重新创造受保护guest capability。消费合同仅允许估计用途，POSITION不能充当ARRIVE或改变current。主线真实证书与第三线模拟测量属于不同world/几何/occurrence域，目前没有把它们冒接成同一生产收费实验。公共main继续只更新四份进度文档，原始实现留本机，用户稿件保持。

## 查询：现有动作集合的剩余学习空间已经量化

[价值分析](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/evidence_value_diagnostics_20261004_r14/VALUE_INTERPRETATION.md)与[完整配对表](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/evidence_value_diagnostics_20261004_r14/VALUE_PAIRS.csv)复用全部原160臂，不重读原轨迹、不重新训练。

TRAIN的C/LD/逐条件任务优先oracle任务数为1077/1078/1080；CAL为321/322/323；TEST为712/713/713。TEST相对固定LD没有额外任务空间，同任务子集内可再减少的固定FIFO受限完成时间和仅[3.148719, 3.149149]，约为全TEST固定LD时间和的0.00351%。这是两种注册尾策略的事后诊断包络，不是可部署基线，更不是整个MAPF问题的性能上限。数值区间不是统计置信区间。

8个TEST family各配对两个预算，来自两份scenario文件；不能把16个预算条件当16个独立场景。所有48个实际gate都只有一条claim、一个owner；TRAIN只有2个双candidate、TEST只有1个。TRAIN里也有同family两个预算任务标签翻转，支持研究状态/预算交互，但两个预算的prefix和gate同时改变，不能称预算单独的因果效果。任务损失与时间变快的冲突标签完整保留。

新导出采用内容hash核对输入和输出，相同键直接复用。根审建议将oracle的差值按配对相减，避免相同策略自减产生伪小区间；离线v2修正已完成，v1代码/结果/收据按原字节留档。该表格修正没有重跑原实验，第二次v2读取提取0行。

## 第三线：证据影响搜索输入，但这组条件尚未改变执行

[完整报告](position_search_bridge_20261004_r14/REPORT.md)、[敏感性表](position_search_bridge_20261004_r14/SENSITIVITY.csv)和[协议](position_search_bridge_20261004_r14/PROTOCOL.md)已封存。12个旧checkpoint全部保留，每个最多查询一个由公开未满足依赖数事前选出的active MOVE。公共估计保留已发生的MOVE_START、CELL_ENTER/EXIT等信息；测量只替换同一估计器的当前位置，不免费透露未来暂停或ETA。

2个目标的测量进度与公开估计不同：random的一处差异被ceil抹平；warehouse的一处使当前搜索边1→2。24个公共/测量请求共9个不同solver输入，8个有旧成功结果，仅1个需新GSES。该调用成功，作者搜索耗时1.098750秒，但最终type2方向和恢复后的实际执行图与旧结果完全相同。因此12组位置测量相对公共方案的ΣT、makespan差全部为0，复用已有完整轨迹即可。

根未导入候选实现，独立重建12个目标/估计/当前点位并核36条调用和采用关系。24条唯一复用轨迹以完整checkpoint、完整采用图、executor/guard及原始SHA绑定旧资源/连续几何审计，不把再次读取证据算成新实验。见[视图核验](r14_root_review/ROOT_VIEW_AUDIT.json)、[采用及复用核验](r14_root_review/ROOT_RESULT_AUDIT.json)。模拟测量的`production_cost=null`；请求次数与主线真实费用不能互换。

## Astra-ultra 技术判断

本轮Astra子智能体同时负责主线实现，因此其判断不是盲评；根另做了独立正文、费用及第三线采用核验。完整本机评议为 `implementation_binding_evidence/position_search_bridge_20261004_r14/ASTRA_TECHNICAL_JUDGMENT.md`，SHA256 `46b38620941e64f1e993a0d25e7a68d70d151a796de6422d0debeb077f57b987`。

Astra将当前阻点定位为合法动作的实际响应空间：ceil抹掉了一部分差异，但唯一未被抹掉的差异也没有改变依赖方向，不能只归咎于取整或模型太小。采样时刻2的POSITION上界也不能直接当成交付时刻4的当前上界，未接入未来ETA。

其具体建议是：第三线先在公开图、承诺与事前物理可行整数残余范围内，检验至多两个合法查询目标能否改变可逆依赖选择；不从隐藏真值倒推范围、不任意增大权重。只有出现候选响应才登记新checkpoint的证据配对，所有同键作者调用继续复用；若敏感性筛查进入在线策略，其计算开销也要报告。查询线则建议在新的TRAIN/CAL比较同一晚点后的C与STOP：STOP停止后续POSITION购买，但正常END、合法任务执行继续。保留LD/整程WAIT，按任务、时间、查询数报告权衡，不虚设费用兑率。这两项是下一轮具体设计，本轮尚未运行。

## 科研导师判断与下一步

[导师本轮判断](position_search_bridge_20261004_r14/REPORT.md#科研导师的下一步判断)强调：当前更精确的位置没有产生更好的合法后缀，先统一真实证书与执行对象的合同，区分信息精度与认证权限。残余估计若需要更细权重，须先验证作者算法的单位步长假设，不能因为COST_TYPE是float就直接接入分数时长。旧12个条件封存，不在零标签上换网络再训练。

根采纳的下一执行顺序：

1. 主线保留现有证据/费用接口，明确同一执行对象的几何映射、occurrence、捕获与送达年龄以及消费权限；不再以初始化/复制微优化作为主要论文进展。
2. 查询线用已经导出的任务风险和时间标签定位动作集合与条件覆盖；将C/STOP的匹配晚点尾策略作为下一小规模机制候选，先有完整后果再拟合。当前TEST和两尾策略保持冻结。
3. 作者方法线把“最多释放依赖”与“信息能改变合法候选排序”分开。先以至多两个合法目标及事前可行范围做公开敏感性检查；证明新增输入能改变采用及完整后果，再收集购买价值训练集。搜索时长、测量费用和物理时间继续分别报告。

这轮完成了可运行、可审计、可恢复的接口，尚未产生新的学习性能优势。正式论文继续使用原作者GSES/Improved GSES等适用外部方法；C/LD、oracle及新测量规则仅作为内部策略、消融或机制诊断。
