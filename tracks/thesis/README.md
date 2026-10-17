# 硕士论文集成支线

工作树 `/home/lyh/MAPF_THESIS_RESEARCH`，分支 `research/thesis-integration`。[总体决定](../../docs/RESEARCH_PLAN.md)是唯一总体计划；[本线最新实现](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/research/thesis-integration/tracks/thesis)。main本页只作入口。

围绕与SCI一致的MAPF核心问题，条件式组织传统改进、学习辅助、执行误差扩展与系统验证。SCI成熟算法按固定提交引用，不能复制为第二套算法。原v2只用于已声明的初始位姿不确定性，LIMO不能提供独立真实误差上界。

下一项实质交付为冻结日志的离线轨迹对齐导出器，关联同刻参考、真值、定位、控制及公共反馈；它服务误差分解与验证图表，不重新仿真，也不自动证明连续安全。之后再衔接SCI路径与连续原语适用条件。
