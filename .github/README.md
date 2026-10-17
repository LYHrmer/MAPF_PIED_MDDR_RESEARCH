# MAPF 连续占用与执行约束

本分支 `explore/error-aware-guidance`：连续占用、冲突时窗及构造算法。 四个活动分支服务同一论文问题，资格保持CANDIDATE_TOPIC。

2026-10-18后继：SOLVER_RULE_COMPARISON.md新增单位格点的统一分离/共同接触位置证明、单有限动作禁行时间连通证明及R16静态计数。没有额外求解算子通过准入，不实现删完整潜在对或区间内部孔洞的搜索器。全链、可变等待和反馈截短域仍须另查；[唯一当前方案](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)为准。以下保留前轮记录。

2026-10-18：SOLVER_RULE_COMPARISON.md新增Q的条件证明，并给出G_linear的同一残差、Jacobian及恢复步。一次Newton/线性消元严格匹配Q，不必另求固定姿态极值，原成本差提议不成立，停止独立实现。未测完整费用，不准备运行。下面保留前轮依据，当前决定见[统一方案开头](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)。

**当前没有放行新求解器投入。下一项须先提出共享基座之外的具体算子及合格请求。** 全链最右禁行边界是辅助目标，不能替代固定各处已有通行次序的完整协调。旧45份计划中31份存在同车对在不同位置先后相反，共599对；这些是输入结构，不是连续安全或性能结果。

SOLVER_RULE_COMPARISON.md已明确全链右端子问题范围；无新增求解器或执行接线。

本轮另给出重复停稳直行的周期增量规则P及原R16实体见证；其当前完整链请求已被共同粗界/后续见证覆盖，不进入实现。详细公式和适用范围见唯一当前方案。

重复动作偏移聚合和普通事件图阈值求解均未建立额外算法差异，不进入实现。T的原v2/全链右端停止证明、W在已核材料上的停止、E/H及C1放行相同的负结果均保留；不从尚未覆盖的范围推定正例。

- [唯一当前方案：具体规则、范围和准入条件](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)
- [定点近邻依据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/LITERATURE_GUIDED_RESEARCH_PLAN_20261016.md)
- [旧输入结构记录](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/gaussian-mapf-feasibility/exploration/spatial_source/INPUT_STRUCTURE_SCREEN.json)
- [全链辅助求解规则及范围补充](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/SOLVER_RULE_COMPARISON.md)
- [公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md) · [导航及历史恢复](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md)

来源仍是整任务共享初始位姿参数、同步实际输入与时钟、零输入无漂移；不声称一般持续跟踪误差。45份R18仍不满足原v2位移必要条件，结构记录不授予执行资格。放行须有有效反馈、动作承诺、制动及完整后缀无再进入依据。

本次仅静态核查与设计判断；没有新求根、B&B、任务会话、world、作者算法或训练，不准备新运行清单，不复用T1/G2c已消费许可。主稿未提交修改、旧失败及冻结证据保护不变。旧查询、RL、换序和LMAPF保持停止或后置。
