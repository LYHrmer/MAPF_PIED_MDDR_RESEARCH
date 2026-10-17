# 当前公共进度

2026-10-17。当前状态以[统一方案开头](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)为准；[本轮前进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/59d356b/GITHUB_PROGRESS.md)保留上一轮缺口筛选及旧否证。

| 项目 | 当前证据与决定 |
|---|---|
| 研究对象 | 固定MAPF路径和通行次序，初始位姿不确定性下的连续占用与协调。同步实际输入、共享任务参数，不声称一般持续跟踪误差 |
| 本轮交付 | 分相位进度边界枚举的公式、伪代码与强B&B比较；固定系数/顶点代数核对，无新求解器实现或运行 |
| 实现缺口 | TURN全旋转外包不随相位细分收缩。原C1 A₁起点旧y上界.334001 m，同δ安全解析界.114601 m，局部至少松弛.2194 m；不代表碰撞或任务收益 |
| 不利证据 | 六个含TURN动作对最大右界1.4995703125 s，低于MOVE全局界1.737460840749 s；只修TURN不能改变该例全局约束 |
| 具体规则 | MOVE距离按双方三速度相位裁片，枚举边界端点和一次方程驻点；可覆盖旧仿射逆式必须回退的情况。几何外包顶点仍非实体见证 |
| 同条件比较 | R只分朝向；G共享几何/完整边界快路/缓存/回退并允许自适应分支。相同P下额外进度分割不收紧已精确求尽的上界；G的显式朝向策略可复现R，但不是所有B&B等价 |
| 固定C1 | 两个瓶颈在旧多边形匀速段顶点取等，完整分段逆式最大值不变；其余九界仍低于瓶颈，全局U及约9.465086 ms夹逼保持。不报新放行或净计算收益 |
| 强对照 | 同模型通用区间分支定界，允许相同紧几何、解析快路、缓存和回退。IPC非线性CCD/Tight-Inclusion核须先适配验证，不能把给定轨迹TOI当鲁棒出发右端 |
| 近邻核验 | 沿用Täubig2012、TOG2021 TI、TR-CCBS2024和TIME2026依据，以及前轮两个作者库固定版本与MIT许可。本轮核对IBEX官方目标界/可行性/未决状态和收缩器接口，未构建或运行作者程序 |
| 旧反馈结果 | C1平移投影缩小范围但不改变阻塞与放行；9.45 s仍阻塞、9.95 s三组分离。不混用T1的9.45 s结果；T1全流仍缺 |
| 旧外部身份 | PSIPP/CTC同模型消元适配与联合相位界相同，非作者全系统复现；SADG核心、WinkTPG只读限制、MAPF-X近邻依据均复用 |
| 已停止 | 联合仿射投影独有收紧、C1平移历史投影、同证书接线、同几何直接投影贡献；当前小问题网络、旧查询学习及C1毫秒调优 |
| 后置 | RL、换序、LMAPF、实物；不扩大场景或扰动寻找正结果 |
| 运行状态 | 只做来源读取及精确算术，不导入/执行研究模块；world/控制会话/训练/科学运行/作者代码调用均0。不准备新运行清单 |
| G2c历史 | 两次新采集失败，有效新数据0，两次许可均消费；短IPC旧计划未授权未执行，不阻塞当前解析主线 |

本轮依据见执行分支[具体求解规则与比较](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/SOLVER_RULE_COMPARISON.md)和[固定代数收据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/SOLVER_RULE_CHECK.json)。上一轮[筛选记录](implementation_binding_evidence/space_time_composition_20261016/ALGORITHM_GAP_SCREEN_20261017.json)保持。当前仍CANDIDATE_TOPIC，完整几何/求解器未实现、总成本未测。

四活动分支仍各司其职：[当前职责与停止投入](REPOSITORY_NAVIGATION.md)。本轮在执行模块原目录交付规则和解析核对，各入口同步，源码不改。保留共同解析设计，暂不把“进度消元后只分朝向”作为独立贡献推进。若继续，须先给出共享快路后仍不同的规则和完整工作量依据；本轮不准备有限运行，不因负结果扩场景、改噪声或训练。

保留主稿未提交修改、冻结来源/实现/清单、旧失败及本机原路径。旧T1有限清单和历史建议不是当前授权；不复用已消费许可。归档及历轮依据从[导航](REPOSITORY_NAVIGATION.md)恢复。
