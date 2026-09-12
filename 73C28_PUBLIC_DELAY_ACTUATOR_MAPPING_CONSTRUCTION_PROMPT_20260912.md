你是本项目的Claude Opus建设合作者，不是审稿投票员。请构造一个可直接写入研究设计的“固定公开延迟表→共同ACTUATOR”的有限语义合同，并建议首选路线。只输出中文方案，不实现、不写伪代码、不联网、不调用工具、不生成任何实验输入或实例，不赋参数值或范围。文末必须输出 END_C28_CONSTRUCTION。

当前固定官方源YueZhang-studyuse/LMAPF-delay@0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。用户刚允许只读四类别路径字节序首个JSON和其引用文件，根已实际读取并对13引用对象重算Git blob全部相等。
事实：
1. 四配置city/game/warehouse-s teamSize1000，random100；均taskAssignmentStrategy=roundrobin、numTasksReveal=1。这些数字只是原文件事实，绝不是研究参数赋值。原driver不读取numTasksReveal，而set_num_tasks_reveal(commit_window+1)，commit_window来自CLI commitStep。本研究保护H、T_delay、B_CAL、B_max、B*、P_active、density N保持原义UNASSIGNED。
2. 四份共用delay-0.001-1.txt，blob ff0df58b4fb3223f247888afaec0b40208621407，20,000,011 bytes。实际首行5000,53983；其后5000行，每行2000个逗号token，只有0/1；总1的数量53983。原read_int_delay只把首行第一个token作max_team_size，第二个token不使用，再取前team_size行，非零转bool。不从文件名或经验1比例推生成概率或独立性。
3. 原BaseSystem::execution_simulate取current_time=curr_states[0].timestep，再对每agent和完整commit_window取D[agent][current_time+offset]（零基）。它不保证末次窗口会缩短，因此静态原生支持需每次整个读取窗口在实际列宽内。MCP/PIBT/PIBTD将直接delay和依赖等待施于原离散移动，它们不是本研究连续控制器。
4. 四图/起点/任务实际静态检查通过：记录足数、每行单位置、起点互异、位置皆可通行且所属同一四邻接分量；这不证明连续包络/世界初态、源动态继续、任务服务或效果。纯来源核验，未运行研究算法。

当前主稿工作法P_model：
- 固定有限公共机会O、全序及所有原服务容量，处理按有限确定性基本步计费；宿主CPU/elapsed/内存另报，不进入虚拟Q/时钟/故障。不生成O，不加服务行/新旋钮，不改E或保护参数。
- ACTUATOR(i)公共行处理已认证发布候选；本行当前guard全费完成才作用。部分guard耗尽，无外部改变、不推进attempt watermark、不抽新no-start。已合法处理的RUN即使no-start、C=s、运行中无作用、BRAKE未停，也消费该尝试；重放不能复活。BRAKE不被no-start取消，已有运动不会因no-start瞬停。
- 原同block各臂共享创新函数，key=(角色,公开行或请求/作业语义id,有限copy/attempt序号)，块内允许相关，块间创新根Z_b独立。完整Q_a,b=F_a,b(X,Z_b)，X含固定来源与设计。主theta=sum w_b E[(Q_D-S,b-Q_R-S,b)/E_b|X]。保主D/R和必报D/E0及外部H19E0/H19R-S；原生PIE-D另轨，不能宣称新物理与native逐迹等价。
- source_id目前=(category,map_blob,agent_blob,task_blob,delay_blob,assignment_strategy,parsed_semantic_options)，同语义alias合并保全部出处。固定权重四类等权/每类不同map等权/每map不同合法source等权/每source预定profile等权/固定repeat等权。不按运行结果删改。尚无实际roster。

请你交付：
A. 明确选择最小合同。可以考虑“每agent公共ACTUATOR机会零基秩对应原列”（只依X/O，不依实际请求/被处理次数/成本/臂），或“显式源时间到公共时刻映射”。比较两者后选一种，不新增任意源时间缩放旋钮，不假装保留native时间物理。给数学定义、空机会/guard不足/无作用/重复/越界/无行的语义及成本边界。固定矩阵可以作为X的确定性no-start分量；若这样做必须明说不是每次重新Bernoulli抽样，其它Z_b如何仍有意义，不能隐含双重no-start叠加。
B. 给静态支持谓词，使用全部潜在公共机会而非实际成功尝试，避免运行后删困难来源。不要将未知尾部补零、循环、按结果缩短E或补供给。解释矩阵列是否应在空机会推进以及no-start是否要对非RUN分支读值。值不可免费透露给应用策略或规划器。
C. 解决原delay_blob只作为出处却重复加权的风险：当不同blob只有未使用行/列不同，如何定义有效语义与alias、何时必须明确改变原source_id/权重目标；如何避免用已实现轨迹合并来源。不要把“保权重公式”当作数值总体不变证明。
D. 最多给5个应当检查的纸面边界（不是测试代码或新实例），并给可直接入稿的4–7条中文合同。区分可现在定的语义与未来未实例化/实现资格；不做泛泛风险清单、不要求无关的新文献/审稿轮数。总答复约1800–2500中文字。

