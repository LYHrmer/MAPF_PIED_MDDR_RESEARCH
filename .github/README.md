# MAPF 连续占用与执行约束

当前统一对象：**初始位姿不确定性下的连续占用与协调**。四个活动分支只服务一个论文问题，当前资格CONDITIONAL。

本分支 `explore/gaussian-mapf-feasibility`：误差来源、跨动作传播和覆盖条件；分支名不要求采用高斯。首版整任务共用初始位置/朝向参数，实际输入与参考完全相同、时钟同步，零输入无漂移；不涵盖滑移、轮速实现误差或闭环纠偏。

**最新决定：五轮反馈机制预检完成，关闭当前C1初始平移投影贡献候选。** 原两包公开消息按冻结哈希恢复，每臂726字节；b_x范围从±.02 m收缩到约[−.010680,.010684] m，但9.45 s的A₂—B₃/A₂—B₄阻塞仍在，9.95 s先验/单包/历史三组均分离。强简单区间交集与候选更新相同，没有约束、决定或全成本优势。保留复核工具，不扩场景或网络找正结果。T1全流、外部充分适配和独立任务证据仍缺；C1与T1合同不混报。

- [唯一当前方案与继续/停止判断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)
- [模型、联合逆映射证明、反馈可辨识性及精确收据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/DEPARTURE_NOTICE.md)
- [公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md)
- [分支、归档和恢复](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md)

停止项：C1平移历史投影贡献、同证书接线贡献、同几何直接投影候选、当前小问题网络训练、旧查询学习。RL、换序、LMAPF与实物后置。WinkTPG仍只读且有许可缺口；SADG执行核心复用，冲突构造以充分适配的PSIPP/CTC为比较对象。

本轮只做必要静态核验，没有world、训练、任务会话或科学运行。旧T1及G2c清单是历史证据，不构成当前运行建议或授权，已消费许可不得复用。主稿未提交修改、旧失败、来源代码及冻结证据不改。

此前结果保留在[本轮前固定进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/e670598/GITHUB_PROGRESS.md)，详细技术历史见上方模块说明。日常只从本页进入，避免按旧根README或旧“下一步”恢复停止路线。

本轮来源实现：[initial_pose_history.py](../exploration/spatial_source/initial_pose_history.py)只作固定C1的保守b_x投影；由公开z_x、旧合法参考进度范围及sin/cos界推出，不调用真值或采样。相同b_x加到全部未来车身点，保持b_y、δ及定位界，覆盖TURN/WAIT/HOLD而不在路点重置。唯一辨识仍不成立；完整后缀决定无变化，停止扩为通用估计器。原COMPOSITION.md和来源代码不改。
