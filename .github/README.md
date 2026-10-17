# MAPF 连续占用与执行约束

本分支 `explore/error-aware-guidance`：连续占用、冲突时窗及构造算法。四个活动分支只服务固定路径、固定次序下的一个论文问题，资格保持CANDIDATE_TOPIC。

**当前候选T：用全段接触变化率证书，将合格TURN–MOVE的禁行右端精确归约到TURN结束姿态。** 唯一拟新增能力是删除转弯时间搜索变量；两臂仍共享紧几何、来源、解析快路、导数/单调性、全局剪枝、缓存、精度与回退。条件证明及资格化原型完成，独立创新和完整加速均未证明。

原S1模块新增turn_endpoint.py资格化原型及TURN_ENDPOINT_CHECK.json；保留WEIGHTED_SCOPE_CHECK.json负结果，未修改冻结实现。

旧R16输入有5个合格动作对；共同边界下界剪去1个，余4个中3个在该顶点符合原次序。这不是全部G0剪枝后存活请求，也不是完整任务实验。原输入采用明确的1米共同问题适配，作者原2.5米尺度未复现；四车时序、起点等待/终点驻留及共同紧端点几何仍待核验。

W在45份R18原输入上的简单(2,4)/(4,2)权重请求已全部被共享分离/单调性结束，停止该材料范围的求根器投入；不为它扩大v2来源域。原E/H、四角点和C1放行相同的停止/负结果保持。

- [唯一当前方案、条件证明及投入门槛](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)
- [直接近邻与强适配对照](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/LITERATURE_GUIDED_RESEARCH_PLAN_20261016.md#转弯端点归约的直接对照)
- [T资格化原型](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/turn_endpoint.py) · [静态记录](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/TURN_ENDPOINT_CHECK.json)
- [W输入资格停止记录](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/WEIGHTED_SCOPE_CHECK.json)
- [公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md) · [导航与历史恢复](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md)

下一项只核查T剩余请求上的强通用接触变化率适配及完整共同剪枝。如果同等或更便宜的已有规则已闭合，或请求全被主导，停止T；否则先闭合共享几何和完整任务资格，再考虑有限运行。不能将“框架可加入T”当作已有等价算法，也不能把少一个变量当作完整加速。

来源仍是整任务共用初始位姿参数、同步实际输入/时钟、零输入无漂移；不声称一般持续跟踪误差。端点归约不是在线放行，合法反馈、动作承诺、制动和完整后缀无再进入条件保持。

本轮无求根、B&B、姿态/控制调用、任务会话、world、作者算法或训练；不准备新运行清单、不复用T1/G2c已消费许可。主稿未提交修改、旧失败及冻结证据保护不变。学习、旧查询、RL、换序和LMAPF继续停止或后置，实物不阻塞纯仿真主线。
