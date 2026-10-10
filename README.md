## 当前入口：P2 历史学习来源与复用（2026-10-10）

本树停止独立扩展，保留R19条件时长估计器及历史正负证据。P2核定原来源与执行树冻结副本一致；统一新学习／更新合同由query-value-feasibility负责。没有机械合并代码或新增模型、训练、科学运行。 状态CONDITIONAL。[统一P2进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md#portfolio-p2)。本机交付目录：`/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY/exploration/learned_query/portfolio_p2_20261010/`。以下P1及更早记录保留，最新优先级以P1/P2为准。

# 学习型进度查询探索工作区

> **P1 路线调整（2026-10-10）**
> P1：停止作为独立查询学习研究线扩展，合并职责到 QUERY_VALUE_FEASIBILITY。历史训练、模型和正负结果保留；不机械合并代码，不继续旧 overlay 的测试集调参。学习现服务于误差相关 MAPF 决策，具体动作与数据资格另核，尚未开始新训练。
> [统一研究问题、各线职责与停止条件](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/RESEARCH_PORTFOLIO_20261010.md)。本轮仅调整研究计划，未改冻结证据或授权科学运行。以下旧轮次按历史范围阅读。

2026-10-05 R17：**C/LD/STOP 三臂价值模型、family 分组验证与查询预算前沿已完成。** [本轮报告](exploration/learned_query/budget_frontier_20261004_r17/REPORT.md)。分组 OOF 模型为 **1077 任务 / 受限 ΣT 135942.023389 / 223 查询**；节省查询伴随时间取舍，尚未超过固定 LD 的任务数。本轮只复用既有 TRAIN，CAL 为已使用的开发重放，**不是新 TEST，也没有新增 native episode**。[独立根复核](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/r17_root_review/QUERY_INDEPENDENT.json)通过；以下历史全部保留。

2026-10-04 R16：**完整 STOP 后缀、冻结条件模型与去重 CAL 评估已完成。** [本轮报告](exploration/learned_query/stop_value_20261004_r16/REPORT.md)。新增29次native，复用30个旧C后果；3个CAL B16 STOP由严格语义别名复用C8，保留真实来源，不伪造STOP日志。TRAIN C/STOP均1077任务，查询285→144，受限时间多约102.388；固定STOP并非逐条件无损。

CAL冻结树为238任务/52查询，固定STOP同238任务、仅36查询且受限时间少约90.775。模型确实训练并在冻结门决策上评估，当前未超强固定策略；不是新盲测或新增模型native部署。下一聚焦已有C/LD/STOP空间内的信息预算价值，保留完整历史与固定STOP对照。[三线科研导师复判与后继合同](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261004_R16.md)。以下旧轮次为历史。


2026-10-03 R9：[同续策预算价值实验](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/matched_tail_20261003_r9/REPORT.md)已完成91次成功原生运行，包括40个冻结留出。24个query标签和21个WAIT分支明确比较“当前选择后均继续同一π₀”，三模型实际训练部署。WAIT366任务；condition与history/nohistory/nobudget均367任务、123query，逐world固定FIFO时间也完全一致。没有新增学习收益，+1来自原condition策略。

本轮修正了估计目标，但16个训练query标签的主任务差全部0；下一优先增加真实决策分歧与可用训练信号，再检验历史/预算作用。生产COST尚未接入。[三线判断与后续设计](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261003_R9.md)。下方R8及更早为保留历史。

R8（2026-10-01）已完成123个训练/校准WAIT及探针运行、48个N16冻结留出和12个N32兼容后继，115标签用于同架构有/无历史ridge。N16任务WAIT346、RR/条件350、分时条件344、有/无历史均345；N32依次171/170/169/166/168。模型确实训练并部署，但尚无学习优势。原12个N32启动guard失败另存，后继仅修复输入上限，全部195attempt可追溯。

[R8完整报告](exploration/learned_query/stratified_value_20261001_r8/REPORT.md) · [全部留出配对图](exploration/learned_query/stratified_value_20261001_r8/ROOT_FIGURE_CAPTION.md) · [三线判断及下一方法](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261001_R8.md)。下一步将单次查询标签改为相同后续策略、剩余预算下的价值；不以少量查询或局部预测改善代替任务收益。下方R7及更早内容为历史记录。

R7（2026-10-01）已完成作者在线planner、公开承诺frontier与持续FIFO，允许在途执行。60次有效运行全部达到H128，24配对标签训练模型、20完整留出；任务总数WAIT/无历史180、RR/条件179、历史178，尚无学习任务收益。历史实际14次查询，无历史全部WAIT。所有失败、原始数据与独立审计保留。

详见[当前探索入口](exploration/learned_query/README.md)；[本轮Astra/科研导师判断与三线后续设计](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261001_R7.md)。下方旧轮次文字按历史记录阅读。

2026-10-01 R6：[16机器人共同执行与历史价值训练](exploration/learned_query/public_joint_20261001_r6/REPORT.md)完成6机械臂、24训练/校准反事实臂、40留出臂，实际训练并运行同架构有/无历史ridge。IID/SHIFT中模型与RR的任务和物理执行相同，尚无学习独立收益。全固定组中的静态循环、末任务驻留及两个旧超时均保留；下一步接合法依赖保持执行或作者在线任务接口。[根独立复核](exploration/learned_query/public_joint_root_review_20261001_r6/README.md)重拟合权重并复算320选择/324分数，不能把来源公开的静态轨迹机制称完整PIE-D或正式LMAPF对比。下列R5及更早内容为阶段历史。

2026-10-01 最新（20260930_R5批次）：[历史模型实验](exploration/learned_query/public_history_20260930_r5/RESULTS.md)完成156原生臂及同架构有/无历史真实训练，但14留出world全无合法查询机会，不能评价模型收益。[事件查询后继](exploration/learned_query/public_history_events_20260930_r5b/REPORT.md)完成24机械臂，RR/条件规则各19次真实查询，最多同时1候选；已验证多次查询时机，尚无多agent竞争或新学习优势。

[更新后三线实绩与两份独立复判](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20260930_R5.md)明确下一步：以共同执行误差平台和完整公开任务流承载查询价值检验，主线继续必要的消费/费用闭环。所有模型、失败、原生raw归档与核验保留；下面R2及更早说明属于历史快照，旧“尚未训练/待运行”不代表当前状态。

本轮另归档[原作者实际轨迹与输入/日志](exploration/learned_query/public_trace_author_archive_20260930_r2/README.md)，可直接复核355关系的来源。[root独立重放](exploration/learned_query/public_trace_root_review_20260930_r2.json)核对2000源动作、10746公开END、560选择、92260历史因果检查和四个新增decoder负例；原24份实验工件、81份旧查询文件及9组件头保持。[更新后的三线判断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20260930_R2.md)明确下一项为完整共同执行、多候选任务竞争与真实费用，而非继续堆方向模型。

2026-09-30 R2 最新：[公共轨迹→真实查询接口](exploration/learned_query/public_trace_20260930_r2/RESULTS_20260930_r2.md)已完整运行六个独立生成run：10,746条原MOVE反馈、4,260个局部真实执行episode，96个匹配公开任务的端点服务；END-only因果重放560项选择与native结果相同。公共PIE-D原100×20 trace、355真实跟随依赖及任务出处均独立核验。方向预测在IID下改善、反转时失效；强简单方向bin、监督categorical、解析与内部RR任务结果同效，没有学习独立收益。它是公共map的局部R1机制，尚非100机器人联合在线运行或正式外部benchmark比较。完整失败、严格几何审计和信息合同纠正见报告。

2026-09-30 最新：[同容量、公共任务结构与active任务实验](exploration/learned_query/BUDGET_TASK_RESULTS_20260930.md)完成384次运行、3456任务。任务导向规则已在一个预声明结构下以1次查询、流时36优于内部admission/RR的2次查询、流时37；AR仍与lag2同效，未证明学习独立增益。完整原始回执、CSV和root独立复核均链接于该报告。主要基线仍须使用已发表作者方法，内部规则仅用于机制消融。下一步接真实费用与公开场景；[2026近作核查](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/LITERATURE_DELTA_20260930.md)进一步限定贡献。以下旧“最新”说明按其日期阅读。

2026-09-24 最新：[查询决策到立即执行的比较](exploration/learned_query/DECISION_EXECUTION.md)已通过321项断言。原 SRDC（无报价回退）/RR 与两步准入前瞻均选 AB；单步选 CA。截止6时后者完成1个 MOVE、前者0个，截止7时前者完成2个、后者1个。后继改进改为围绕完成时刻选择查询，并把学习增益与决策目标改进分开检验。

同一仓库保留三条清楚分工的分支：[main 主线](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/main)验证空间误差下的安全执行和付费查询；本分支 `explore/learned-query` 研究查询预测与组合决策；新建的 [explore/error-aware-guidance](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/error-aware-guidance) 研究固定误差安全层上的路径占用/等待代价。新分支已有条件性的路径排序反转见证，尚未训练模型，不替换本分支或主线。

本工作区对应 `explore/learned-query`，探索范围与下一步见[学习型查询探索说明](exploration/learned_query/README.md)。已实现小型监督概率模型、[估计／决策分离诊断](exploration/learned_query/DECISION_ABLATION.md)及[真实 C++ 组件状态到模型入口的导出验证](exploration/learned_query/COMPONENT_VALIDATION.md)：57 项 Python 检查和29项人工输入的 C++ 组件断言通过，并修复浮点累计导致的并列错排。尚未接生产查询链、用研究数据训练或证明吞吐收益；[实现说明](exploration/learned_query/IMPLEMENTATION.md)区分组件接口与科研性能证据。

2026-09-24 接续：[合法组合阻塞预检](exploration/learned_query/legal_and_precheck.md)通过530项真实组件断言，支持给定空间/运动前提下的查询互补性。后继先隔离有限前瞻决策的价值，再固定决策器验证学习的独立收益；这不是生产 AUTH、完整费用或任务完成结果。

以下为继承的主线资料入口；当前实现含未纳入 Git 的本地工件，本工作区尚不具备完整可运行实现。

## 主线资料

当前目标、设计、权限和下一步统一见 [.github/README.md](.github/README.md)。

DARI 已淘汰，不属于当前研究目标或待办。旧编号计划中的 WORKING/pending 仅为历史记录；当前可修改的73草稿与冻结证据按上述入口区分。
