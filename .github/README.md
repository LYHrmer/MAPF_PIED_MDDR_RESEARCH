# MAPF 连续占用与执行约束

当前统一对象：**初始位姿不确定性下的连续占用与协调**。四个活动分支只服务一个论文问题，当前资格CONDITIONAL。

本分支 `explore/gaussian-mapf-feasibility`：误差来源、跨动作传播和覆盖条件；分支名不要求采用高斯。首版整任务共用初始位置/朝向参数，实际输入与参考完全相同、时钟同步，零输入无漂移；不涵盖滑移、轮速实现误差或闭环纠偏。

**最新决定：** 联合相位差已作为更强的非学习对照实现，冻结例全局上界1.738392026978→1.737460840749 s，但既有9.45 s放行不变。没有新任务收益或全成本加速证据；停止继续打磨C1毫秒差额。历史观测缩域只完成可辨识性和合同判断，尚无可重放T1公共包与关键决策差异，不新增估计器或采集。

- [唯一当前方案与继续/停止判断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)
- [模型、联合逆映射证明、反馈可辨识性及精确收据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/DEPARTURE_NOTICE.md)
- [公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md)
- [分支、归档和恢复](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md)

停止项：同证书接线贡献、同几何直接投影候选、当前小问题网络训练、旧查询学习。RL、换序、LMAPF与实物后置。WinkTPG仍只读且有许可缺口；SADG执行核心复用，冲突构造以充分适配的PSIPP/CTC为比较对象。

本轮只做必要静态核验，没有world、训练、任务会话或科学运行。旧T1及G2c清单是历史证据，不构成当前运行建议或授权，已消费许可不得复用。主稿未提交修改、旧失败、来源代码及冻结证据不改。

此前入口和结果保留在[本轮前固定版本](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/6d09dce/GITHUB_PROGRESS.md)，详细技术历史见上方模块说明。日常只从本页进入，避免按旧根README或旧“下一步”恢复停止路线。

来源复核：[COMPOSITION.md](../exploration/spatial_source/COMPOSITION.md)及现行代码保持冻结。初始平移b与固定定位偏置ℓ存在观测不变性；重复帧不能唯一分开二者，但仍可能缩小允许集合。源内固定偏置不自动等于公开接收合同已证明可跨帧抵消，条件说明见当前证据入口。
