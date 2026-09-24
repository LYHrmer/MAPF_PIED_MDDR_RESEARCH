# 学习型进度查询探索工作区

同一仓库保留三条清楚分工的分支：[main 主线](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/main)验证空间误差下的安全执行和付费查询；本分支 `explore/learned-query` 研究查询预测与组合决策；新建的 [explore/error-aware-guidance](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/error-aware-guidance) 研究固定误差安全层上的路径占用/等待代价。新分支已有条件性的路径排序反转见证，尚未训练模型，不替换本分支或主线。

本工作区对应 `explore/learned-query`，探索范围与下一步见[学习型查询探索说明](exploration/learned_query/README.md)。已实现小型监督概率模型、[估计／决策分离诊断](exploration/learned_query/DECISION_ABLATION.md)及[真实 C++ 组件状态到模型入口的导出验证](exploration/learned_query/COMPONENT_VALIDATION.md)：57 项 Python 检查和29项人工输入的 C++ 组件断言通过，并修复浮点累计导致的并列错排。尚未接生产查询链、用研究数据训练或证明吞吐收益；[实现说明](exploration/learned_query/IMPLEMENTATION.md)区分组件接口与科研性能证据。

2026-09-24 接续：[合法组合阻塞预检](exploration/learned_query/legal_and_precheck.md)通过530项真实组件断言，支持给定空间/运动前提下的查询互补性。后继先隔离有限前瞻决策的价值，再固定决策器验证学习的独立收益；这不是生产 AUTH、完整费用或任务完成结果。

以下为继承的主线资料入口；当前实现含未纳入 Git 的本地工件，本工作区尚不具备完整可运行实现。

## 主线资料

当前目标、设计、权限和下一步统一见 [.github/README.md](.github/README.md)。

DARI 已淘汰，不属于当前研究目标或待办。旧编号计划中的 WORKING/pending 仅为历史记录；当前可修改的73草稿与冻结证据按上述入口区分。
