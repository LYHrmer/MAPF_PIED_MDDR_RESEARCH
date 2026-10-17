# MAPF 预执行局部重优化原型

explore/error-aware-guidance负责连续占用、鲁棒时窗及完整执行比较。现有实现均在exploration/spatial_constraints_s1_20261016内迭代，不复制框架。

四个活动分支只服务一个问题：固定路径和原v2原语，在执行前调整声明的局部通行组，保留完整鲁棒可行安排，在同一计算预算下比较组选取。当前为CANDIDATE_TOPIC，尚未建立独立创新或任务收益。

- [唯一当前方案](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)
- [公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md) · [导航及归档](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md)
- [文献与基线身份](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/LITERATURE_GUIDED_RESEARCH_PLAN_20261016.md)

2026-10-18已实现：原子组/固定边/锁组合同、双向鲁棒访问窗口、最早时间求解、WAIT日程、地图及全车连续占用核验。时间正环与动作图成环分开报告；当前适配器拒绝后者。声明组还不是作者SADG最大组复现，条件证书还不是执行许可。仅AST/compile与只读复核，未调用新求解或证书入口。

END-to-START加固定原语时长不能让误差进入优化价值，现只作内部消融。正式ESADG式规则与后继候选共享相同窗口、候选组、优化器、缓存、总预算和最终检查。当前冻结v2域只能支持同域时窗比较，尚不支持后验缩域实验。UNRESOLVED保留，不能把已认证候选中的最好值称全体最优。

仍缺任务级组生成/选择器、联合启动至合法END、外层总预算和完整成本、独立合格任务及新运行清单。R16可复用为DEV；45份R18仍超原v2必要位移域。来源仅为整任务共享初始位姿偏差、同步实际输入与时钟，非LIMO标定或一般持续跟踪扰动。

旧C1同信息放行相同及Q/P/T/W等停止结论在原范围保留，见历史进度和执行SOLVER_RULE_COMPARISON.md。旧查询学习、ins2/ins3扩展不重启；RL、运行中换序、变速和LMAPF后置。主稿未提交修改与冻结证据保护；科学运行待新授权，不复用T1/G2c许可。
