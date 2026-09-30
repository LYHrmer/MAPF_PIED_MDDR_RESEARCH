# 学习型进度查询探索工作区

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
