# 73L23A：固定输入解析与消费条件核对

2026-09-12；/root/source_service_audit；CONSTRUCTIVE / NONBALLOT。依据全文L20/L21/L22及本轮定点原源码，不审主稿、不判数据通过。根负责获准四类首个配置和引用载荷；本代理没有读取或下载任何数据。

固定来源为YueZhang-studyuse/LMAPF-delay@0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。本轮直接读[driver](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp)、[common.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/common.h)、[Grid.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/Grid.cpp)、[Tasks.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/Tasks.h)及[CompetitionSystem.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/CompetitionSystem.h)全文；[CompetitionSystem.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/CompetitionSystem.cpp)读L1–220、615–885，包括Inf同步、delay取列及三类补给。未新读三个delay策略内部，相关语义承接L21。

1. **读取条件。** JSON必须具备原入口所读类型和字段，引用按配置父目录解释且落在获准固定树。agent/delay头计数不小于请求team_size仍不足：后面须实际具有所需非注释记录。位置记录只取逗号首token；空token或缺行不能让原迭代器被直接解引用，atoi不能替严格整数/表示核验。task计数须匹配实际取用记录；额外字段不会自动成为多阶段任务。

2. **地图条件。** 维度及乘积可表示，header所需token存在，正文每行至少cols个合法地图字符；位置须在[0,rows×cols)且非障碍。原parser仅把@/T视为障碍。Inf构造直接先读grid.map[start_locs[i]]再判断障碍，非法位置会在“障碍检查”前越界；exit(0)也不能作合法证明。

3. **Fixed/Inf。** Fixed按全局任务下标模agent数分派；循环执行时agent数须非零。各agent队列有限、不循环，任务少于agent只触发warning，空队列/最终耗尽不应自动排除。Inf补给使用(counter_i×agent数+i) mod tasks_size；循环进入时任务数须非零，乘加、计数、task_id须可表示。重复目标仍形成新实例。

4. **字段有效仍可能越界。** Inf同步遍历curr_commits时无保护读取copy_tasks.front()。若一个提交前缀已弹尽全部已分配副本而仍有下一项，下一次读取即无定义；初始副本为空而提交非空亦然。随后while补给不能保护之前的front。这里给出源码条件，不声称获准配置已触发；共同PROJECT的空队列守卫属于显式适配，不能倒称native安全。

5. **delay支持。** set_delay只复制矩阵。每次execution_simulate先读curr_states[0]，再对所有agent及整个commit_window读D[i][current_time+u]。必要谓词为状态/矩阵行存在、索引算术可表示，且每个实际u满足列索引在该行范围内。只核“列数覆盖评价末端”不足以覆盖末次完整窗口读取；各行足宽不要求无关尾部长度完全相等。整数转bool将所有非零值合并，不默认允许任意整数，也不把未知尾部填零。

共同WORLD还须另证agent实体/误差包络不交且避障、bootstrap责任覆盖、任务ServiceRegion及静态可解释性、任务实例/队列规则，以及旧delay列到新公共ACTUATOR尝试的共同映射和支持域。基础网格/位置合法不替这些证明；合法搜索无解、等待或任务耗尽不能回填为静态非法。参数仅以符号讨论，未赋保护参数、运行原入口或形成source_id。

唯一新工件由apply_patch建立；无源码实现、伪代码、构建、测试、仿真、Claude或Git写入，未触及其它配置及旧Q结果。本件可支持根的静态核验清单，不授执行或主实验GO。
