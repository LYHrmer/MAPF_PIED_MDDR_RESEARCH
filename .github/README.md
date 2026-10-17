# MAPF 连续占用与执行约束

本分支 `explore/query-value-feasibility`：合法反馈、配对日志、完整成本与失败账目；不恢复查询对象选择。 四个活动分支服务同一论文问题，资格保持CANDIDATE_TOPIC。

2026-10-18当前：执行前局部换序原型已接入共同的`Costs`，本分支继续复用合法反馈、配对费用和最终END账本，不新增协议或独立框架。代码中的**单个候选费用边界**已纳入：组schema核验、固定边及两方向冲突窗口构造与缓存、最早时差求解、组/完整时间表校验、静态矩形地图检查、全车连续占用证书，以及失败收据的复制和账本追加。这是已实现的计费入口，**没有运行费用测量或加速结果**。入口见执行模块[预执行调度原型](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/preexecution_schedule.py)与[组及时差合同](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/preexecution_order.py)。

联合启动和反馈至END的事件接口已在执行模块`preexecution_session.py`实现，复用原Plant/TaskPacket/Inbox/Costs，不修改冻结协议。全部程序本地准备并获得合法STOPPED回执后，才在同一独占回调的共同epoch安装clock；计划时钟不填写完成时间，完成只由本地产生且合法送达的END入账。逐车PREPARE/LAUNCH命令、反馈生成/到达尝试/接受、失败分别计数、计字节与SHA。参考/真值/观测/控制只存控制端评估通道，账本关闭后才导出。仅静态核验，未运行联合会话；不是网络原子启动保证。

会话构造已纳入其Costs入口，但目录构造、导入、构造失败外层账本、最后计时metadata、外层序列化和进程费用仍未完整覆盖；全优化总预算、硬时限及自主事件驱动也未接通。逐候选预算可受调用方绝对截止限制，不代表整个优化过程有总预算。已有接口不等于完整任务运行或完整成本测量。

后续两臂须使用相同的窗口来源、构造核、缓存规则、精度和预算，构造失败及缓存开销均保留。`END_TO_START`与空间窗口约束是内部消融，不能用较弱END对照单独证明新的选择策略优越；外部强对照仍按统一方案适配。UNRESOLVED、超时、无改善和没有初始可行计划的尝试不得从账本删除。只有通过声明组/时间表、静态地图及全车完整连续检查的有效schedule，才可形成候选改进标签；其计划完成时间之和不是收到END后的实际完成指标。旧L20/L21逻辑边权差也不能充作当前物理收益标签。

完整动作/驻留覆盖证书若成立，可由双方复用以免逐候选重复pair细分；相同几何的地图检查也可共享缓存。该快路尚缺可核验覆盖记录与证书类型，未实现或计时，现保留最终pair检查；不得把要求基线重复认证造成的费用差归为学习收益。

以[统一方案开头](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)为准；下面保留前轮范围和负结果，不作为恢复旧计划的入口。

2026-10-18：Q恢复步被G_linear逐式匹配，原成本差提议不成立，停止独立实现。不以对照多做一次固定姿态极值制造收益，也不强迫原G0支付不用的Q外包/分解成本。没有新费用测量，原协议和费用代码不改、不准备运行。[统一方案开头](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)为准，下面保留前轮依据。

**前轮的独立贡献门槛仍用于科研判断；当前已按用户授权实现上述小原型，不代表增量成立。** 全链最右禁行边界是辅助目标，不能替代各处通行关系的完整协调。旧45份计划中31份存在同车对在不同位置先后相反，共599对；这些是输入结构，不是连续安全或性能结果。

原协议和费用组件不改。局部阈值停止属于共同求解能力；没有测得新的构造、更新或完整任务费用。

本轮另给出重复停稳直行的周期增量规则P及原R16实体见证；其当前完整链请求已被共同粗界/后续见证覆盖，不进入实现。详细公式和适用范围见唯一当前方案。

重复动作偏移聚合和普通事件图阈值求解均未建立额外算法差异，不进入实现。T的原v2/全链右端停止证明、W在已核材料上的停止、E/H及C1放行相同的负结果均保留；不从尚未覆盖的范围推定正例。

- [唯一当前方案：具体规则、范围和准入条件](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)
- [定点近邻依据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/LITERATURE_GUIDED_RESEARCH_PLAN_20261016.md)
- [旧输入结构记录](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/gaussian-mapf-feasibility/exploration/spatial_source/INPUT_STRUCTURE_SCREEN.json)
- [全链辅助求解规则及范围补充](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/SOLVER_RULE_COMPARISON.md)
- [公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md) · [导航及历史恢复](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md)

来源仍是整任务共享初始位姿参数、同步实际输入与时钟、零输入无漂移；不声称一般持续跟踪误差。45份R18仍不满足原v2位移必要条件，结构记录不授予执行资格。放行须有有效反馈、动作承诺、制动及完整后缀无再进入依据。

本次为接口实现及AST/编译静态核验；没有执行新图求解、证书细分、任务会话、world、作者算法或训练，不复用T1/G2c已消费许可。主稿未提交修改、旧失败及冻结证据保护不变。只有执行前局部组与完整计划候选进入原型阶段；运行中换序、旧查询学习、RL和LMAPF仍不推进。
