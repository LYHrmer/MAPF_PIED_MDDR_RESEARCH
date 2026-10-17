# MAPF 连续占用与执行约束

当前统一对象：**初始位姿不确定性下的连续占用与协调**。四个活动分支只服务一个论文问题，当前资格CONDITIONAL。

本分支 `explore/gaussian-mapf-feasibility`：误差来源、跨动作传播和覆盖条件；分支名不要求采用高斯。首版整任务共用初始位置/朝向参数，实际输入与参考完全相同、时钟同步，零输入无漂移；不涵盖滑移、轮速实现误差或闭环纠偏。

**最新决定：CTC同模型消元得到相同联合相位界，关闭独有收紧候选。** 执行分支新增精确半平面消元对照，使用冻结v2支持和同一逆映射条件；两个有效动作对的界与候选精确相等，另九对共享回退，十一最终约束不变。PSIPP/CTC原始源码和MIT许可匹配既有Git blob；这是本项目的CTC式适配，非作者全系统复现。全任务成本和独立任务仍未测，无额外保证，不准备新运行清单。旧C1平移投影和同信息放行负结果保持。

- [唯一当前方案与继续/停止判断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)
- [模型、联合逆映射证明、反馈可辨识性及精确收据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/DEPARTURE_NOTICE.md)
- [公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md)
- [分支、归档和恢复](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md)

停止项：联合仿射投影独有收紧、C1平移历史投影、同证书接线、同几何直接投影贡献，以及当前小问题网络和旧查询学习。RL、换序、LMAPF与实物后置。来源/工具按需求支持同一主线，本轮复用既有组件，不强求每个分支新增代码。

本轮只做一次固定代数和必要边界核验，作者代码、world、训练、任务会话和科学运行调用均0。旧T1及G2c清单不构成当前运行建议或授权，已消费许可不得复用。主稿未提交修改、旧失败、来源代码及冻结证据不改。

此前结果保留在[本轮前固定进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/34b9e83/GITHUB_PROGRESS.md)，详细技术历史见上方模块说明。日常只从本页进入，避免按旧根README或旧“下一步”恢复停止路线。

既有来源实现：[initial_pose_history.py](../exploration/spatial_source/initial_pose_history.py)只作固定C1的保守b_x投影；由公开z_x、旧合法参考进度范围及sin/cos界推出，不调用真值或采样。相同b_x加到全部未来车身点，保持b_y、δ及定位界，覆盖TURN/WAIT/HOLD而不在路点重置。唯一辨识仍不成立；完整后缀决定无变化，停止扩为通用估计器。原COMPOSITION.md和来源代码不改。

当前对照：[CTC适配与等价核验](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/ctc_adaptation.py) · [固定收据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/CTC_ADAPTATION_CHECK.json)。下一投入先指出具体算法差异或有证据的新工程缺口；不重复已完成核验。
