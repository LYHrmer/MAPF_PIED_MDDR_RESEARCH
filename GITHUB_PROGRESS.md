# 当前公共进度

2026-10-16。当前状态以[统一方案开头](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)为准；本页只保留当前决定，按时间堆叠的旧报告见[上一版本完整进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/6d09dce/GITHUB_PROGRESS.md)。

| 项目 | 当前证据与决定 |
|---|---|
| 研究对象 | 固定MAPF路径和通行次序，初始位姿不确定性下的连续占用与协调。同步实际输入、共享任务参数，不声称一般持续跟踪误差 |
| 本轮解析差异 | 同一支持多边形直接最大化联合相位差，严格检查加速/制动逆映射条件；全局禁行上界1.738392026978→1.737460840749 s |
| 完整决策 | 冻结9.45 s放行不变；旧两/三车固定消息例结果保留。新函数未接入控制会话，没有新任务收益测量 |
| 完整费用 | 裁剪外新增10次逆映射域比较和8次联合目标求值；来源、旧回退及全部反馈/控制/日志仍计入，总wall/CPU/内存优势UNKNOWN |
| 反馈探索 | 初始平移与固定定位偏置不能唯一分开；可定义保守历史集合交集，但现有T1摘要缺可重放包流，关键约束改变UNKNOWN。未实现缩域器或改协议 |
| 外部对照 | SADG已核执行核心复用；PSIPP/CTC冲突构造须充分适配；WinkTPG许可缺口未解决，仍只读；MAPF-X约束学习新颖性表述 |
| 已停止 | 同证书接线独立贡献、同几何直接投影、当前小问题网络训练、旧查询学习；本轮起停止继续打磨C1毫秒差额 |
| 后置 | RL、换序、LMAPF、实物；不扩大场景或扰动寻找正结果 |
| 运行状态 | 本轮只做固定代数/必要静态核验，world/控制会话/训练/科学运行均0；不重跑旧核验，不准备新科学运行清单 |
| G2c历史 | 两次新采集失败，有效新数据0，两次许可均消费；短IPC旧计划未授权未执行，不阻塞当前解析主线 |

本短周期只交模型范围、强解析差异、决策与全成本连接证据。[实现、证明与固定收据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/DEPARTURE_NOTICE.md)。联合目标是更强非学习对照，不作为已成立创新；反馈候选只有合法历史能排除具体状态且改变关键时窗时继续，并给强基线相同信息。关键证据不足时停止或保留UNKNOWN，不恢复旧训练。

四活动分支仍各司其职：[当前职责与停止投入](REPOSITORY_NAVIGATION.md)。公共协议仅在具体算法确需新字段时修改。旧查询学习由归档标签保留，不另开课题或复制框架。

保留主稿未提交修改、冻结来源/实现/清单、旧失败及本机原路径。旧T1有限清单和历史建议不是当前授权；不复用任何已消费许可。此前整理与各轮结果均可从[固定历史进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/6d09dce/GITHUB_PROGRESS.md)及[归档导航](REPOSITORY_NAVIGATION.md)恢复。
