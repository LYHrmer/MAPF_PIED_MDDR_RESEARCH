# 当前公共进度

2026-10-17。当前状态以[统一方案开头](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)为准；[本轮前进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/34b9e83/GITHUB_PROGRESS.md)保留五轮反馈预检结果。

| 项目 | 当前证据与决定 |
|---|---|
| 研究对象 | 固定MAPF路径和通行次序，初始位姿不确定性下的连续占用与协调。同步实际输入、共享任务参数，不声称一般持续跟踪误差 |
| 本轮实现 | 原执行模块新增CTC式精确半平面消元，同冻结支持、逆映射条件与回退；未调用候选顶点求解或作者求解器 |
| 约束结果 | 两个有效动作对分别为1.731201361042 s、1.737460840749 s，与联合相位候选精确相等；其余九对共享回退，十一最终右界均相等 |
| 停止决定 | 关闭“共同支持多边形上的联合仿射投影具有独有收紧能力”候选。标准相对时间投影适配能获得同样界，不宣称所有鲁棒算法等价 |
| 费用与保证 | 消元12次投影、112次界配对，另计端点验证；旧裁剪算子记录复用。总构造/更新/控制/日志费用未测，无额外保证，不作性能胜负结论 |
| 旧反馈结果 | C1平移投影缩小范围但不改变阻塞与放行；9.45 s仍阻塞、9.95 s三组分离。不混用T1的9.45 s结果；T1全流仍缺 |
| 外部身份 | PSIPP/CTC两个作者源码及MIT许可匹配既有Git blob；本轮是项目共同模型适配，非原版全系统复现。SADG核心复用，WinkTPG仍只读，MAPF-X近邻依据保留 |
| 已停止 | 联合仿射投影独有收紧、C1平移历史投影、同证书接线、同几何直接投影贡献；当前小问题网络、旧查询学习及C1毫秒调优 |
| 后置 | RL、换序、LMAPF、实物；不扩大场景或扰动寻找正结果 |
| 运行状态 | 一次固定代数及必要边界核验通过；world/控制会话/训练/科学运行均0，作者代码调用0。不重跑旧套件，不准备新科学运行清单 |
| G2c历史 | 两次新采集失败，有效新数据0，两次许可均消费；短IPC旧计划未授权未执行，不阻塞当前解析主线 |

本轮结果见[CTC适配公式、边界与判定](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/DEPARTURE_NOTICE.md#ctc同模型消元适配联合相位收紧不是独有能力)及[公开收据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/CTC_ADAPTATION_CHECK.json)。静态代数结果不等于独立科学验证；完整作者系统比较、独立任务、公共全流和纯仿真性能仍未闭合，研究资格CONDITIONAL。

四活动分支仍各司其职：[当前职责与停止投入](REPOSITORY_NAVIGATION.md)。本轮执行分支实现对照，来源及工具复用既有组件并更新入口；不以每分支改代码作为推进要求。下一项投入先给出新的具体算法差异或有合法证据的工程缺口，不因当前负结果扩场景、改噪声或训练。

保留主稿未提交修改、冻结来源/实现/清单、旧失败及本机原路径。旧T1有限清单和历史建议不是当前授权；不复用已消费许可。归档及历轮依据从[导航](REPOSITORY_NAVIGATION.md)恢复。
