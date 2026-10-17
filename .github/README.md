# 执行底座交接入口

2026-10-18 两线决定生效。本分支保留为底座与冻结证据交接入口，不是第三条研究选题。当前决定仅见 [总体研究计划](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/docs/RESEARCH_PLAN.md)，两线分别为 SCI MAPF 与硕士论文集成；旧“四分支只服务一个误差问题”不再约束选题。

职责：连续占用、鲁棒时窗、预执行日程和完整控制—反馈—END原型。代码按提交及 blob 清单复用，不能跨工作树读取任意最新版本；旧路径和冻结 SHA 原位保留。旧分支尚未完成运行依赖脱钩，因此本轮不删除工作树。

四次闭式功能 DEV 已实际完成，全部 SUCCESS、零重试；二/三车均只有1个组、两个方向，枚举保留原安排，实际完成时间之和分别54.315625/70.315625秒，收益为零。全部合法公共 END 已入账，完整子进程费用在收据外层，不能将旧内层 pending 模板解释为未运行。

- [已核 DEV 结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/PREEXECUTION_DEV_RESULT.md)
- [原始收据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/preexecution_dev_once_20261018/RUN_RECEIPT.json)
- [公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md) · [导航](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md) · [共享依赖](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/shared/README.md)

结果限于同一R16来源的闭式功能DEV；不是独立性能、训练、作者系统复现或实物证据。原v2仅描述整任务初始位姿不确定性、同步实际输入/时钟和零漂移等待，不是一般持续跟踪误差。未测碰撞/覆盖观测率不能填0。旧C1、L20/L21及其他失败保留；不在这批单组材料上训练，不复用任何已消费许可。本轮两线整理只做实现与静态核验。
