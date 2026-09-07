# 72C5：Opus 费用、权限与服务队列合同构造

你是建设性非投票顾问，不是正式审稿。固定72正在顺序审查，不能读取、修改或审查它，也不产生后继候选；仅根据下面自给的抽象问题提出可供根后续综合的符号合同。禁任何skill、工具、网络、子代理、文件读取。禁实现/构建/测试/仿真/种子/载荷/实验结果。H、T_delay、B_CAL、B_max、B*、P_active、density N一律不赋值、范围、默认，不重新定义。数个角色、逻辑枚举和符号不等式不是规模/参数绑定。请给完整约2500中文字，以ADVICE-COMPLETE结束，不臆造文献。

问题：比较有界空间跟踪偏差下的多机器人长期执行，所有臂调用相同PIE-D新MOVE来源和控制器，主要区别是用付费阻塞计数选择途中POSITION查询对象D，或轮询R；E0无途中POSITION，但具有同样必要终点/CURSOR/TASK服务。实际executor游标c私有，算法只获付费Kc；POSITION只给同tid可信参考进度区间，ENTRY给PRECHECK/END，CURSOR只给c，TASK只给已真实转移的任务账本快照。真实任务计分不依赖算法是否询问。

抽象语义：公共有限机会O全序，每行先推进连续物理/既定END，再发布先前已完成的付费应用结果，再登记当前机会；新生工作不在同一行递归执行。PROCESS_SLICE(server)给有限工作容量，每server FIFO，首个付费CAPTURE才固定不可变版本快照，不足原子采样费不能读。应用完成后须严格后继行的付费验证/发布才可见。唯一中心authority写owner/P/关闭水位/查询last/模式；各executor写自己的c/离散命令；真实任务环境写A。每writer至多一个计算或待发布槽，pending不能让后继读取旧账本，但不锁连续物理/autonomous END。每项资源/复制/扫描/几何/字节/日志/失败/发布费用必须计，标量也非零。控制发布容量不得免费完成业务重算。元评价器推进物理/维护固定不透明token另计宿主费用，不替算法偷读真值。NATURAL共享相同服务供给但实际工作可不同；STRICT额外报告公共预付闲置供给，不能为费用对齐冻结物理。

任务一：给一个最小但完整、可有限描述的job→读取能力→authority/writer→入队server→发布容量→费用向量矩阵，包括INIT、POLICY请求生成/消费、SELECT、PRECHECK、END、POSITION、CURSOR、TASK_REQ/snapshot、NETWORK发送/接收验证、资源grant/retire、planner、MODE/fault、日志GC及共同物理控制/真实TASK_SERVICE。允许拆job以避免一个job占两个writer死锁，但拆分必须付费且不赠数据。不得假定一切job都中心串行，也不得用任意未声明server拓扑制造对比。

任务二：给明确的符号公平等式/固定前约束，哪些规则在各臂完全相同，哪些由自己的history自然不同；如何将角色/agent/channel映射为有限server集合、绑定时机、模式切换及失败时pending槽清理写成无隐藏业务工作的合同。考虑entry与position共享authority资源、网络发送与接收端成本、planner暂停耗时、初始化费用和查询饿死终点服务。

任务三：给两条纸面因果轨迹（不要实例化实验O）：一条合法的QUERY→CAPTURE→延迟投送→退役→新grant；一条看似公平实际偷送真实c/当前q或免费发布的失败轨迹。指出哪个谓词阻止后者。明确不能从费用记账完整推出吞吐正/无饥饿，也不要为保证所有情况活性假设用户尚未提供的服务下界。

只作office式合同组织和数学分析，若队列拓扑选择还需研究取舍，列其具体后果/UNKNOWN，不自动选有利于D的拓扑，不宣称现有协议已通过。
