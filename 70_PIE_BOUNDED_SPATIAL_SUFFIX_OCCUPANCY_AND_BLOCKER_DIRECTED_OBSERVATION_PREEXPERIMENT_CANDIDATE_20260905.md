# 70 PIE 原 MOVE 的有界空间占用与按阻塞原因取证：实验前新候选

日期：2026-09-05（Asia/Shanghai）
工件性质：NEW-NUMBER / NEW-BYTE / PRE-EXPERIMENT CANDIDATE / NONBALLOT
状态：OPEN，等待依序科研导师、Nature、无 skill 逻辑审查与根代理验收。
控制状态：HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 继承边界与要回答的问题

69 的身份为 SHA256 e07cc5c7dd3e87d4e03d6e7cd544dedad5f05b686585494630c497f4ae1eb80d，50975 bytes，787 个换行。69R4（SHA256 624e669f5bdb397ef30b028e35455ac42d51a72591ebbf6ad238cf0b445448d6）有效综合三份审查，要求新编号修复；69 不修改、不封存、不继承通过。

本候选回应的实际问题是：机器人实际占用位置偏离标称路径、边上运动持续多个决策时刻，而规划和通信仍需耗时；如果把“已经完成”的错误消息当成清空，后车可能进入仍被占用的位置。如果始终等到所有机器人都完成，又会无谓地阻塞其他位置。能否在保留 PIE 原 MOVE 的条件下，用明确的几何包络和有限进度证据安全地提早释放已不可能再占用的后方区域，并把有限查询机会用在真正阻塞动作的位置？

待验证的效果是减少“已经物理通过、但尚未被证明通过”导致的等待，且计入测量、通信、事务和计算代价。不是宣称无条件提升吞吐。只组合已有机制也可构成有用研究；这里不把组合、主动查询、互斥、CAS、belief shield、ADG 或缓冲区本身主张为首创。若完整同类方法已经完成同一机制和证据，则改为复现/增量研究并重新审查，不能只换名字。

70 主动撤回 69 的最小 WAIT 闭包、全局最大可动集合、任意队列次序等价和线性总复杂度等未证明强主张。采用逐个申请、完整未来占用掩码与持久事务；拒绝依赖“同一批其他机器人一定会离开”的投机放行。它可能更保守，必须由明确负例和公平实验检验其用途。

只有 PIE 产生新的离散 MOVE。外层可复制那个 MOVE，保有真实安全的驻留，或继续/制动已发行的同一 MOVE；不得改目标、换边、插入绕行动作。本文是规格、推导和未执行检查合同，没有代码、测试、仿真、载荷或结果。

## 2. 一手来源、阅读深度与路线比较

以下是根代理亲见的来源审计，不冒充旧 69L1/69E1 任务的回执。两任务原 UUID 已查询、当前会话不可观测；截至候选起草仍无约定文件，不以超时计通过。文献陈述限于实际读到的部分；预览不当全文，源码链接不当运行证明。

| 一手来源 | 已核实内容与限制 | 对路线选择的作用 |
|---|---|---|
| Hönig 等，RA-L 2019，Persistent and Robust Execution of MAPF Schedules in Warehouses，DOI 10.1109/LRA.2019.2894217；[作者全文](https://whoenig.github.io/publications/2019_RA-L_Hoenig.pdf) | 7 页文本完整读；ADG、执行通知、commit cut 已有。其模型假定定位/控制较准确、不发生显著空间偏离、动作最终完成且及时报告。 | 执行依赖和规划执行重叠不能当新意；新增空间包络与错误消息不能直接继承其前提。 |
| Zhong、Rossi、Shell，Autonomous Robots 50, 5 (2026)，Planned synchronization for multi-robot systems with active observations，DOI 10.1007/s10514-025-10225-4；[出版社全文](https://link.springer.com/article/10.1007/s10514-025-10225-4) | 全文文本完整读。收费观测、观测持续时间、运动和测量误差、同步宏动作已研究；部分模型依赖一致观测和简化动态。 | 主动观测不是首创；必须比较查询代价，并明确反馈真假与共享观测的区别。 |
| Zhu、Brito、Alonso-Mora，Autonomous Robots 46, 401–420 (2022)，Decentralized probabilistic multi-robot collision avoidance using buffered uncertainty-aware Voronoi cells，DOI 10.1007/s10514-021-10029-2；[作者全文](https://autonomousrobots.nl/assets/files/publications/22_zhu_auro.pdf) | 20 页提取文本完整读；高斯误差、机会约束、连续控制修正。双积分制动扩张在文中明确为 heuristic；死锁处理可改变局部目标。 | 物理误差路线有直接期刊锚点，但不能把概率安全转成硬安全，也不能把其新控制目标无声塞入 PIE MOVE 保持层。 |
| Shahar 等，JAIR 70, 923–954 (2021)，Safe Multi-Agent Pathfinding with Time Uncertainty，DOI 10.1613/jair.1.12397；[官方公共全文](https://par.nsf.gov/servlets/purl/10297272) | 32 页可提取文本完整读；未审图像，抽取中一页近空。边持续时间区间、潜在占用、在线 SENSE / SENSE+COM 已有；通信/位置证据有专门前提。 | 跨 tick 占用不能退化成离散起步失败；计划代价界改善不等于实际吞吐必然改善。 |
| Atzmon 等，JAIR 67, 549–579 (2020)，Robust Multi-Agent Path Finding and Executing，DOI 10.1613/jair.1.11734；[期刊页](https://jair.org/index.php/jair/article/view/11734) | 出版信息和摘要，未全文读；k-robust 延迟处理及执行策略。 | 延迟鲁棒性是已发表锚点，不能据摘要断言其没有某项完整机制。 |
| Liu、Tang、Cai、Li，Artificial Intelligence 358, 104586 (2026)，Robust and effective multi-agent path execution with timing uncertainty，DOI 10.1016/j.artint.2026.104586；[出版社](https://www.sciencedirect.com/science/article/abs/pii/S0004370226001128) | 出版社摘要片段和作者出版列表核实；全文未读。 | 时序执行路线的重要近邻；不沿用 69 对其完整算法能力的未经全文核对断言。 |
| Wang、Zhang、Shi，Robotics and Autonomous Systems 206, 105701 (2026)，Protocol-observation discrepancy calibration for robust multi-AGV coordination under noise, delay, and faults，DOI 10.1016/j.robot.2026.105701；[出版社](https://www.sciencedirect.com/science/article/pii/S0921889026003726) | 官方摘要、highlights 和搜索可见片段；全文未得。涉及 occupancy / reservation / queue / progress 的差异及恢复。 | 最近同题期刊；全文排除与强新颖性结论 OPEN，不从不可访问推出其缺少证明或机制。 |
| Serra-Gómez 等，Autonomous Robots 47, 1275–1297 (2023)，Learning scalable and efficient communication policies for multi-robot collision avoidance，DOI 10.1007/s10514-023-10127-3；[出版社全文入口](https://link.springer.com/article/10.1007/s10514-023-10127-3) | 摘要、引言、相关工作已读，余文未读；通信策略与连续避碰联合。 | 查询对象选择已有学习路线；本文确定规则须与相同信息机会的普通轮询比较。 |
| Zhou 等，RA-L 2, 1047–1054 (2017)，Fast, On-line Collision Avoidance for Dynamic Vehicles Using Buffered Voronoi Cells，DOI 10.1109/LRA.2017.2656241；[作者论文页](https://msl.stanford.edu/bibliography/zhou_fast_2017) | 作者摘要/书目信息，未全文读。 | BVC 是几何控制基础，不能据后续论文引用就声称本根代理审过其完整证明。 |
| Luo、Sun、Kapoor，PrSBC，NeurIPS 2020；[官方论文页](https://papers.nips.cc/paper_files/paper/2020/hash/03793ef7d06ffd63d34ade9d091f1ced-Abstract.html) | 官方摘要，未全文读；有限支持运动/测量不确定性与概率安全屏障。会议，不计期刊数。 | 控制修正/概率屏障为已有路线；不转称为本文的无替代离散 MOVE 定理。 |
| Carr 等，Safe Reinforcement Learning via Shielding under Partial Observability，AAAI 2023，DOI 10.1609/aaai.v37i12.26723；[官方页](https://ojs.aaai.org/index.php/AAAI/article/view/26723) | 摘要及首页片段，未全文读；部分观测和可能转移的 shielding。会议。 | 集合式知识安全层不是新颖性本身。 |
| Zhang 等，Concurrent Planning and Execution in Lifelong Multi-Agent Path Finding with Delay Probabilities，AAAI 2025，DOI 10.1609/aaai.v39i22.34506；[官方论文](https://ojs.aaai.org/index.php/AAAI/article/view/34506/36661) | 论文核心算法、执行政策、源码脚注和有关讨论已读，未声称逐页全文审读。脚注明确关联官方仓库。 | PIE-D 必须保留；根代理逐对象审计源码见 §3。 |
| Okumura、Tamura、Défago，Time-Independent Planning for Multiple Moving Agents，AAAI 2021，DOI 10.1609/aaai.v35i13.17347；[官方全文](https://cdn.aaai.org/ojs/17347/17347-13-20841-1-2-20210518.pdf) | 9 页文本完整读，未审图。contracted / requesting / extended；交互为黑盒，结论明确通信延迟尚未建模；脚注关联官方仓库。 | 已发表外部 MCP 执行基线；Causal-PIBT 会改路径，不能借其可达性证明本文。 |

四份完整文本中，Zhong 响应 SHA256 6d1bd846552a9c29bd6fb1f4d40b78c434eaffc7f8ed5f2d64930af4f512e741（474572 bytes）；B-UAVC 作者 PDF SHA256 6de59654091de1bdf388f1544c00e7ce4be1236f2b1aad89dfd682c7897e2e83（7788136 bytes）；JAIR 时间不确定性 PDF SHA256 def08325da0ee2d4d12e01fd5ed864acaa224b87b0421f402803b9e4a68023bd（1097341 bytes）。Hönig 经官方作者 PDF 的网页提取全文读取，本轮未做 PDF 字节散列。三份散列不等于图像/公式排版逐项核验。均仅内存读取，未下载新研究载荷。

路线的实际选择如下：

| 路线 | 改变的量、可信前提 | 可证伪作用与代价 | 本候选处置 |
|---|---|---|---|
| 起步失败/随机延迟 | 仍在原顶点；原时序执行前提 | 延迟调度收益；不测试几何误差 | 保留 PIE-D 原域基线，绝不改名为“误差” |
| 空间定位/运动执行偏差 | 实际身体中心和占用相对路径偏移；有限空间包络和制动约束 | 膨胀后能否避免真实包络内冲突；代价是狭窄地图不可行与并发下降 | 70 的物理主域；需要同底座比较 |
| 反馈错误 | 实体状态与所报状态不同；普通报告可错，另有有界误差的可信测量能力 | 防止假 COMPLETE 释放；可信查询耗时、缺失时阻塞 | 作为独立因素和组合因素，不能充当物理误差替身 |
| 几何 + 反馈 + 处理耗时 | 连续运动、空间偏移和观测滞后同时存在 | 是否能以有限查询收回保守等待；也可能计算/测量成本抵消收益 | 本轮条件性推荐，仍可被后续审查或实验否定 |

没有把“更复杂”作为更优证据。几何硬包络若不可信，本定理域不成立；可转向机会约束路线，但那是另一个概率主张和新候选，不能以本稿偷偷替换。

## 3. 官方 R0 与外部基线的不可变源码证据

R0：YueZhang-studyuse/LMAPF-delay，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357，version.txt 内容 1.1.0，MIT。AAAI 2025 正文源码脚注直接指向此仓库。
外部：Kei18/time-independent-planning，commit 755a7ce740d49543b1165403371752c08e342ca4。GitHub ref/tags/v1.0 实际返回该 commit，MIT；AAAI 2021 源码脚注直接指向该仓库。两个不同 commit 不混用。

下表均通过 GitHub 固定 commit API 取得对象；根代理完整读取注明代码/文档，并在内存独立计算 Git blob SHA1（带 blob 长度头）与 SHA256，核对 API size / sha。只列承重对象；没有 clone、build、test 或运行原法。

| 仓库、路径 | Git blob | SHA256 | bytes；用途 |
|---|---|---|---|
| R0 inc/CompetitionSystem.h | 6daf0b9e3fa1015e49893b09be87940577427189 | e4e0b26e30412503e496d56af1b1fd841fe9ff01b99ca425316027538bcc0f55 | 6753；状态/执行接口 |
| R0 src/CompetitionSystem.cpp | 4e9a86921fda3fd15bd616c3c0dff461688254ed | fe7532c9fe4e4dfe19d8e5e7c2192635c99a5fbd8c4d95db728ae02336839604 | 27752；调用顺序 |
| R0 inc/MAPFPlanner.h | 68fbfd7a13d2a1513c6634d41d0dca5133740aeb | d25fbcb08b6d80b4f03234b4f7c3c08c553d7074a7e12c47fee86d336409633e | 971；规划接口 |
| R0 src/MAPFPlanner.cpp | 94afb42df1a70f5e312a382e61cf83576fd7360e | c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1 | 6125；commit 接口 |
| R0 src/DelaySimulation.cpp | 1e1953d9fa9ccb1eb96ae5d7b8829f425679d113 | 432e704bcef191b82261a4106cf9ebfad9a7cf0932d5017fe51e4a0dc1202f6f | 14733；MCP 原时序语义 |
| R0 src/driver.cpp | b75764cc26c2374ce51dabb94e13a138e50f166f | 3198636d1114e4901c9aae48d549787c9fb3bc3a0bdfd49b6445d81bb5fc4f44 | 6664；实际参数与输入 |
| R0 inc/ActionModel.h | fb3aa01448d3f9369ca7a423d975d4a148cbe1e8 | 8f3ed2ebaac0c014874892b81e4273ac69fb9a914c528d8a71e2bac43d3c1666 | 3757；实际离散动作 |
| R0 src/ActionModel.cpp | 3292164aa861521beda270f18b8d3892e35fbd21 | 13ee35e8536ebc8fe0f897bf6b16bdb5b6d70c67169379b6a3cd0fce534f239a | 8164；顶点/对向边校验 |
| R0 LICENSE | 1f4b6eadac278447824a47d409bb4de04ea7f3ee | f7f63f9810a4de1d4db59c034bcbbb5f33aa8ec3a1c07b21e774033f6bac2a94 | 1084；MIT |
| R0 CMakeLists.txt | 148459bb9542731723e8125bb8d54da6a3ce954b | ecdf7e3c889ab8290eb9cc839543c0f281419db957982a03b79ae79da25dc899 | 2790；构建入口 |
| R0 README.md | a4578f87f918dab4b67b50cd404e3ec901a8f636 | 335709410787bf335fadedcfc514b8f722d66ab6d9c0785c52992ca24d90738b | 2730；与源码有差异 |
| R0 Input_Output_Format.md | a16e1a41630d0a6229118ef5f4096e6717bb6c36 | 70a57193f57ad3aab9d134972877bcd9fb3873910de2406adca2ce08d6d84e2b | 12724；格式说明有旧内容 |
| 外部 time_independent/src/mapf_dp.cpp | 7537e71885496ff9b0a75bf8d49b0f2138044625 | f0f3d23be2ccd8f004b850b29cb336a6fabf5f2e77c9407df01fd305e284c5e0 | 3758；异步执行语义 |
| 外部 time_independent/src/mcp.cpp | 51459fc9ea27b3c8831b0a72d2455bca360b2223 | d2c53110803ef784a28419298c24d86477ff93e18bdbb957459dcd697fe90ad7 | 1135；MCP |
| 外部 time_independent/src/agent.cpp | a5a8f1ba47d295cd93f728cb8ad2cf85caca3b3a | 1e1700c650424f0ea7bcb9951dea697f799d15a64872fbbb2318234ff0c6bb15 | 4569；真实 tail/head |
| 外部 app.cpp | 78f3c6944789f10999791e8f360d849ebbc1350e | ec61c055cc79a3c4746e59f472d784fd2e697280d733ac5e0f0c9441389069e3 | 9615；MCP 分支与输入 |
| 外部 LICENCE.txt | cdc9e1cb51b24b72f079baf9af9e31f53c967fbd | 1a29e915c0d12f49bde2dfca5ef905f4a4e3575f18c7d8e121c3e7d25c908fa5 | 1055；MIT |
| 外部 CMakeLists.txt | 746d1cb3608fdb05017fc12437b2ce3303f278ec | 7ca030f3ba57ebc52532d079dcae0b6105dab2b48fddd48c3226e9637b81377a | 295；app |
| 外部 time_independent/CMakeLists.txt | ac67e5b8f9932e9305408b2ce1e07a40e343d3e3 | deed3f4a966117cb51a1719a28570fe39a7c18d4fdbb36bf9beb5aef8125136a | 577；lib-time-ind |
| 外部 instances/sample.txt | 842958a104943a6d7cad2474547ee5665c427b37 | 293eabfcce21e5198fbb7cf6359ffb25e80be12873a4bf1106b697920dcdc61a | 620；原样例，已全文读 |
| 外部 map/6x6.map | 1b27a7e3384ab9dbe984d452e6b481b6d11d8469 | 9524a48abca00d838b210306d5ba4375273dda9ecafcbb273a65812b07590361 | 62；样例引用闭合，身份核验 |
| 外部 mapf_plan/sample.txt | b7ad38d85756c6b26d57dd0169fb29533660e416 | 688a52a29a767c5ed6bfd8cf4a51d6b125c0a252636f920dd1c6b89888b9e17d | 490；样例引用闭合，身份核验 |

源码定位由如下固定链接和表中路径组合，禁止用 default branch 顶替：[R0 固定树](https://github.com/YueZhang-studyuse/LMAPF-delay/tree/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357)，[外部固定树](https://github.com/Kei18/time-independent-planning/tree/755a7ce740d49543b1165403371752c08e342ca4)。

承重接口核对：

- R0 CompetitionSystem.cpp L14–41 直接从真实 curr_states 计算下一离散状态/任务完成；L52–98 同步预测提交窗口末端；L384–402 先 sync/load/plan/commit，再推进其逻辑执行；L404–414 另记额外规划耗时。它不是已经实现连续机器人与错误消息通道的代码。
- MAPFPlanner.cpp L141–166 是 planner_commit，调用 commitPath / validateCommitSolution。此审计没有完整展开 LNS 验证器；不把函数名算成独立几何校验。
- DelaySimulation.cpp L145–153 的 no-start 延迟不移动，L256–308 跟随递归及回滚使用真实 delay/progress。ActionModel.h L16–17 的 rotation 枚举被注释，活动动作是 N/E/S/WE/WA；cpp L31–82 校验下一顶点、障碍、对向边，不校验连续扫掠体。文档中的旋转格式不能覆盖实际源码。
- driver.cpp L40–55 注册的实际选项优先于 README；evaluationMode 注册被注释。L101–158 实际读取 mapFile、agentFile、taskFile、teamSize、delayFile 和任务策略，不是旧文档 robotFile。源码内部覆盖部分任务揭示设置。不能把旧 README 的不存在样例/compile.sh 直接当可运行复现入口。
- R0 输出 AllValid 关联 fast_mover_feasible；不把这个字段独立当所有碰撞类型的通过证据。
- 外部 MCP 直接读取其他 agent 的真实进度 getT；agent.cpp 的占用由真实 head/tail 判断。app.cpp L141–143 选 MCP，L176 运行，读取公开固定 MAPF plan。不存在已经处理假 COMPLETE 的通道。app 缺少输入也可能返回 0，故 exit=0 单独不是原法检查通过。

最小原法检查合同（全部未执行）：取得对应 commit 和完整依赖对象，保留 MIT 声明；R0 使用 CMake 3.16 及以上、原 C++14 非 Python 分支、Boost program_options/system/filesystem/log/log_setup，目标 lifelong；外部原目标 app / lib-time-ind，C++17，文档建议 CMake 3.16 而构建最低写 3.1，采用文档要求并记录差异；openFrameworks 是可视化子模块，不是 headless 构建依赖。实际工具链版本、CPU 架构、编译命令、flags、依赖版本和完整 stdout/stderr 以后单独绑定。

外部固定 sample、map、plan 已形成可定位原输入闭合，未来原样选 MCP 分支验证解析、任务定义、状态序列、终止和独立离散冲突校验。样例中的原论文数字不成为本项目保护参数赋值。R0 由 §12 的确定选择器提供原样公开 JSON 及引用闭合，显式指定原 MCP 政策和规划分支，不能借默认值偷偷设项目参数。原法检查必须同时检查输入消费记录、非空结构输出、exit、任务完成语义和独立校验；任何不符记 AUDIT-FAIL，不调参救样例，不把帮助文本/中断处理成功当复现成功。

本候选只承诺一个官方外部 MCP 执行比较；不声称已审计 FSP 或 Causal-PIBT 全实现。官方原版运行与加适配器的运行永远分列。

## 4. 有界物理模型：实际空间误差，而非延迟换名

图 G=(V,E) 嵌入有限平面工作区，顶点坐标有理，每条可执行边是固定直线段。一个 MOVE 的原始字节指定 i,u,v 及动作 occurrence；几何嵌入不改 u,v。转向只可在顶点驻留、速度为零时完成，机器人任意允许姿态的身体由已声明有理凸多面体 P_i 外包。模型不含选错边、任意横越车道或控制器完全失效。

以边长度 ℓ 和单位方向 e 表示身体中心 x=u+s e+z。连续状态为 s、v 和二维偏移 z：

ds/dt=v，dv/dt=u_ctl+d，dz/dt=−κ z+w。

物理合同为 0≤s≤ℓ、v≥0、|z_j|≤ε_track,j、|w_j|≤κ ε_track,j、|d|≤δ_acc；另有执行器速度限 v_cap 与保证减速度 a_brake。所有这些是未赋数值的物理模型量，不是保护符号的重命名。轴对齐原格边使 e 为有理向量；斜边仅在所有几何系数有理的声明子域使用。物理安全域还要求：

v²≤2 a_brake(ℓ−s)。

控制器必须在 v=0 时实施单向约束，在 v=v_cap 时不继续加速，在上述制动边界且 s<ℓ、v>0 时选择 u_ctl≤−a_brake−δ_acc；执行器制动力范围须可实现它，且无额外未建模响应滞后。达到 s=ℓ 时立即进入终点吸收驻留模式，v=0；该模式禁止继续纵向加速直到新 tid 正式接管。驻留状态速度为零、中心在顶点偏移盒内。若执行器响应有滞后，要把响应期间距离计入另行证明的可行域，不能沿用本稿公式。

保持推导：偏移盒正边界的导数≤0、负边界的导数≥0；g=v²−2 a_brake(ℓ−s) 的边界导数是 2v(u_ctl+d+a_brake)≤0。因此从可行初态，连续流保持横向/纵向偏移盒与终点前制动可行域；s 单调不减；s=ℓ 时 v=0。控制器可以提前制动并停在边上，仍属于同一个 MOVE；制动不要求瞬时把位置冻结。用于纯仿真的公共执行器是受约束的平面跟踪模型，不声称等同任意差速车、轮滑或负载变化模型。没有声称该合同已经在真实硬件上得到验证。

实际误差包括非零 z、受 d 影响的速度/加减速偏差，以及观测位置与 s 的差；真实占用为 x+P_i。即使同一时刻两台机器人的标称点没有冲突，偏移后的身体仍可能相交。外生起步失败另外保留为 D-start；它只是没有开始移动。处理耗时期间 s 和 z 仍演化，边上状态不会被塞成某个离散端点。“tick 内慢一点但终点相同”的标准离散 no-op 不作为因素。

## 5. 有限空间资源与有限知识的具体编码

工作区用有限有理闭矩形瓦片集 R 覆盖；边界同时计入所有接触瓦片。瓦片只是保守互斥资源，不声称瓦片数是 density N。障碍也为有理多边形。所有合法图边、驻留区和物理包络必须在工作区中；触及障碍的完整 MOVE 掩码直接几何拒绝，不改变路线。

每个 MOVE 固定有限有理切点表 Q_e=(0=q_0<…<q_m=ℓ)。切点作为几何模型输入在未来实例化前冻结，不自适应依实验结果增加。本文不赋切点数/间距。令 Z_i 为偏移盒；未来占用集合

U_i(q)= {u+s e+z+p : q≤s≤ℓ, z∈Z_i, p∈P_i}，
M_i(q)= {r∈R : r∩U_i(q)≠∅}。

驻留集合 U_hold(i,u)=u+Z_i+P_i，驻留掩码同样按相交定义。有理多面体相交由线性可行性系统表达，需检验变量 s,z,p 及瓦片约束；枚举有限瓦片给出实际可计算的掩码，边界接触算冲突。这里不是用未知 Reach/CERT 预言机定义算法。掩码包含任意以后停车位置、制动路径及终点驻留。q 增大时 M_i(q) 只能缩小。

每个 agent 的有限活动记录为：
(agent_id, boot_fence, occurrence, resident_generation, tid_or_none, stage, cut_index, proposal_bytes_hash, geometry_hash)。
stage∈{HOLD, ISSUED, TERMINAL_LATCHED, QUARANTINE}，且至多一个未终结 tid。有限性指固定有限输入与单次事件的活动状态；不声称无限执行的 occurrence 整数总域有限。已终结 tid 由持久单调 action 序号/fence 排除，不能丢掉所有防重放记录以声称常数总历史。

HOLD 的 concretization 是顶点偏移盒、v=0、门关闭且有当前 resident claim。ISSUED、cut_index=j 的 concretization 包含 q_j≤s≤ℓ 的全部模型合法状态，及 COMMIT 后尚未启动的状态（其 q_j 必为 0）；不是一个乐观“当前相位”。每个可能状态及其全部静默未来都在 M_i(q_j) 内。TERMINAL_LATCHED 是 s=ℓ、v=0、旧 MOVE 门已关闭、终点驻留。联合 concretization 采用各 agent 集合的保守笛卡尔积；账本独立记录精确 claim，不从物理有无占用反推有没有未送达的授权。活动表示尺寸为各记录和各掩码位集总长度，不枚举全局状态积。

普通报告可迟到、丢失、重复、重排、矛盾或假报完成，均不能增加 cut_index、转 TERMINAL 或释放 claim。它们只影响诊断和查询候选，不影响这个硬安全知识域。真实性来自单独的有界测量服务：证据含真实的采样时刻、agent/occurrence/tid、几何版本、传感服务身份、进度读数 ŝ 和误差界 ε_obs，满足 |ŝ−s_sample|≤ε_obs。它不是免费精确真值；可耗时、缺失和分区，但在定理域内不能提供违背该界的有效证据。算法不读取模拟器真值。

进度证据更新是 j←max(j, max{k:q_k≤max(0,ŝ−ε_obs)})；若下界大于 ℓ、签名/身份/几何不合法或与已锁定 terminal 的 occurrence 不一致，拒绝并记录异常，不令 K=∅。旧测量仍是此 tid 当前进度的下界，因为 s 不回退；因此不以时钟新鲜性冒充物理真值，也不把下界扩展到下一个 tid。

INIT：只有全体相关 agent 的合法驻留/门关闭证据和互不冲突初始 resident 掩码建账成功才进入安全域；否则 REJECT_INITIAL，不凭空初始化占用真值。
ISSUE-BEFORE-ACT：执行门仍关闭时，将 HOLD 转为 ISSUED(0)，完整未来掩码转入持久 tid；完成后才允许开门。
ADVANCE-SILENT：无需消息更新 j；s 单调与模型包含保证知识仍包含真实状态。
OBSERVE：仅上面的有界真证据增加 j；乱序/重复取 max，结果与消息顺序无关（固定 tid、均有效的进度事实集合）。
RETIRE：仅释放 M_i(old q) \ M_i(new q) 中仍绑定当前 tid、resource generation、owner fence 的 claim；该资源从当前及全部未来可能占用中消失。释放可以分批延迟，延迟不破坏安全。
TERMINAL：必须另有终点驻留和旧门关闭的可信 latch 证据，原子地把终点掩码的 tid claim 转成下一 resident_generation，释放剩余非终点 claim，才可接收下一 MOVE。
REBOOT/COMPACT：重建持久 D、entry gate、claim 与最大有效 j；丢失 j 则取更保守下界且不得重新申请已转给别人的后方资源。此情形保持已持久退休记录，使用旧 j 的持久证明重建；若证明也不可得，门维持关闭/旧事务继续保有，进入 QUARANTINE，不能倒退 j 后假称仍拥有旧全掩码。

对于内部错误导致的空/不一致知识，禁止空集上的真空全称 CERT。保有现有物理责任、不给新 MOVE，必要的制动沿旧事务包络进行；没有有效初始责任的空知识事件属于域外/模型违反，不能声称算法使其安全。

## 6. 资源 owner、每个 tid 的协调者与执行门

基础接口是持久、线性化的单资源 owner 和每 tid 单决策寄存器，不是依靠普通消息就凭空解决了共识。可用复制状态机实现，但复制协议实现不在本稿内。分区中无法取得线性化决定即阻塞；不承诺可用性。故障可以丢易失内存，不能丢已承诺的持久记录；永久损毁属于域外。各 owner 只管理自己的瓦片，协调者只管理该 tid 的参与者，不设置全局停止管理者。

D_tid∈{UNDECIDED,COMMIT,ABORT}，从 UNDECIDED 只能一次 CAS 到一个终值，终值不可改。tid 绑定完整 proposal 字节、agent、occurrence、geometry_hash、mask_hash 和冻结参与者列表。物理运行状态和 D 分开：COMMIT 既可能尚未启动，也可能在边上或已到终点。

PREPARE 票为 (tid,resource_id,resource_generation,owner_epoch,proposal_hash,mask_hash,decision_key,parent_resident_or_none)。owner 发票前持久锁住该资源的未来排他使用权，直到可验证 D=ABORT 或提交后的合法退休/终结，不设本地超时失效。更换 owner epoch 必须继承旧锁；不能当作旧锁全空。

同一个 agent 不是通用豁免：只有 entry gate 已关闭、无未终结旧 tid、occurrence 匹配且票中明确指定的当前 resident claim 可以准备转移给新 tid；同 epoch 的旧 tid、旧 resident_generation 和另一机器人全部不豁免。resident 权利在准备阶段仍保护原驻留；COMMIT 后无缝转为该 tid 对同一资源的权利；ABORT 只删除新准备义务而保留 parent resident。hold 与未来 intent 不是两台实体，不错误计成自碰撞。

角色守卫表：

| 角色/事件 | 必须满足的守卫 | 持久动作及失败分支 |
|---|---|---|
| 协调者建立 tid | 原 MOVE、entry HOLD、无旧 tid；完整掩码无障碍；冻结列表 | D=UNDECIDED；不先要求尚未申请的 PREPARE 票 |
| owner PREPARE | 身份/版本正确；无别的 agent/不兼容 tid claim；本 tid 未已知 ABORT | 保有锁再签票；拒绝给出阻塞 claim 身份。若与 ABORT 竞态，所得锁随后依已决 ABORT 清理，不可被当新 COMMIT 票 |
| entry PREPARE | 仍驻留且门关闭，parent resident 正是本 occurrence，未给其他 tid | 持久锁定 agent 的新授权入口；它也是冻结参与者之一 |
| 协调者 COMMIT | 所有冻结参与者的有效不可撤销票齐备；完整证书独立复核通过 | CAS UNDECIDED→COMMIT；任何缺票/不一致→尝试 CAS ABORT，未知时保有，不开门 |
| 协调者 ABORT | 仅 D 仍 UNDECIDED | CAS→ABORT；若实际 COMMIT 已胜出，则遵守 COMMIT，不能发送可释放的 ABORT 指令 |
| owner RECOVER | 读取持久决策和自身票/claim | ABORT 清新票但保留 parent；COMMIT 保有并转移；UNDECIDED/不可达保有。UNKNOWN 不等于没有 COMMIT |
| 执行器 START | 完整 COMMIT 证书、entry token、当前 fence、精确 tid/occurrence/action；ISSUED(0) 和全部权利已持久 | 对此 tid 一次开门，调用原 MOVE 的公共控制器；重复 START 只回已有状态 |
| owner RETIRE | 当前持有 tuple 完全匹配；可信进度证明使该瓦片不属于未来掩码 | 先持久记录新下界、证据及本 generation 退休事实，再开放该 generation 的后继申请；旧证据不能释放后来 holder |
| 执行器/owner TERMINAL | 有界物理证据加旧门 latch；终点 resident 转移持久完成 | 下一 occurrence 可提出新申请；失 ACK 按旧决定恢复，不重复运行原 MOVE |

执行器可以根据同一 COMMIT 决策开始而某些 owner 尚未收到 COMMIT 通知，因为它们的不可撤销准备锁已经持久保有；不是依赖所有机器人在同一瞬间启动。尚未启动或晚启动者的完整掩码从头保留，其他获准 MOVE 与它不冲突。COMMIT 后不提供“超时取消即释放”的捷径。停止尝试新动作、继续旧 MOVE、沿旧 MOVE 制动，是不同命令，不把它们都打印成 WAIT。

## 7. 总算法与独立证书校验

每次处理一个有限已到达事件集和一个冻结 PIE 提案 P。先应用有效证据及已决恢复，随后按 (proposal occurrence,agent_id) 的固定字典序处理其待决动作；时间相同事件按 §13 总序规范化。候选本身不控制 PIE 选择哪个相邻顶点。

对于每个动作：

1. 尚有已发行旧 tid：输出 CONTINUE_OLD / CONTAIN_OLD，保有责任，不接受此 agent 的新 proposal；COMMIT 未启动也算旧 tid。
2. QUARANTINE、无有效初始驻留或不可恢复知识：NO_NEW_AUTHORIZATION；不伪造物理 WAIT。
3. 原动作 WAIT：entry 门关闭且驻留 claim/证据有效则 HOLD；否则按前两项，不调用新 MOVE。
4. 原 MOVE 的 origin/occurrence 不匹配，或完整几何掩码触障碍：HOLD（有驻留前提时），记 STALE_PROPOSAL / GEOMETRY_REJECT；不生成替代 MOVE。
5. 其余建立 tid、按 resource_id 总序申请所有 PREPARE（含 entry）。首个拒绝或当前事件回合尚缺票则本回合不给新 MOVE，已取得的票保有或由成功 ABORT 释放；不可达并不无限占住根算法的计算调用。
6. 票齐且独立最终 verifier 接受则原子决定 COMMIT，再执行 ISSUE-BEFORE-ACT/START；若最终复核拒绝，只尝试 ABORT，无新 MOVE，留存失败原因；若别处 COMMIT 已决定，进入旧事务分支处理，不能把已提交实体当 WAIT。
7. 本回合后根据明确阻塞表选择 §9 的查询；查询结果作为之后的事件处理，不在同一次认证中假定它已经返回。

准备中的 tid 不重复创建。后续回合由它自己的消息状态推进；有限算法调用不等于网络请求有限时完成。一个 MOVE 的返回结果是 pending、rejected、committed 三者之一；pending 时物理仍由 resident/旧 tid 负责。为避免用无限等待掩盖总性，所有网络步骤都发消息并返回，接收与恢复是后继事件。

最终 verifier 的输入不是几个 hash：它接收规范提案字节、完整几何多面体/切点/瓦片描述、agent 的 entry 证据和 predecessor resident tuple、冻结参与者清单、所有 PREPARE 票原文、各 owner/entry 的可信验证公钥与持久承诺合同、当前 tid 决策键以及演算掩码。逐项检查字节/身份一致、无多余或遗漏参与者、正确原边、有限合法几何、掩码重新计算、无障碍、每个票的签名/版本、parent 例外仅针对正确同一个驻留、entry 的单次入口承诺。票签发者的排他记录语义是基础接口前提，不把签名等同真实物理。并行第二 verifier 可用独立多面体表示重算掩码；后验独立 oracle 另读完整物理/账本日志，不能让 verifier 偷读真值。

不再建立 WAIT 传播图：所有预先驻留、在途、已承诺未启动和本轮新 PREPARE 都是阻塞资源。某机器人被抑制而仍占原点时，那些资源从未被投机移除，所以不需要一个事后修补跟随链的闭包。代价是放弃原子旋转和部分本可共同移动的组合。

## 8. 定理、证明范围与可检验的成本界

定理 70-A（知识与未来掩码包含）：合法 INIT 后，任意发行、静默推进、有效证据、持久恢复与终结事件交错中，真实身体及未终结 MOVE 的全部模型内未来位于它仍持有的掩码中，除已证不可能再进入的退休瓦片。

证明：HOLD 由初始驻留证据；发行在开门前加入 M(0)；§4 保持式给出空间盒、单调 s 与制动路径包含；有效测量有 ŝ−ε_obs≤s_sample≤s_now，向下取切点仍是下界，取 max 保持它；M(q) 的集合单调性证明退休瓦片以后不可达；退休前把所用证据和新的 cut_index 持久化，恢复从持久事实重建而不凭超时释放；terminal 只有门关闭后转 resident，驻留掩码仍保有。普通假报告不做缩减。逐事件归纳得证。这不是所有可能硬件故障的证明。

定理 70-B（不相交资源权利推出物理无碰撞）：在 70-A、owner 排他持久性、entry 强制执行和唯一决定成立时，合法初态的任意两不同机器人真实身体不相交。

证明：若时刻 t 身体相交于点 x，则有限闭瓦片覆盖使至少一个含 x 的资源 r 同时属于两者所需掩码；70-A 与开门前保有规则使两者在 t 都必须有 r 的有效物理使用权。不同 agent 的 resident/prepare/committed 权利不能并存，矛盾。owner 排他不是“动作已经安全”的循环前提，而是可单独检查的单资源状态机不变量；几何包含与真实执行另外证明。瓦片保守性只造成假冲突，不会漏掉交点。

定理 70-C（提交/恢复竞态）：若协调者 COMMIT 与恢复者 ABORT 并发，则仅一个 CAS 从 UNDECIDED 成功。ABORT 赢时任何执行门无法取得 COMMIT；COMMIT 赢时恢复者不得释放准备资源。未知决定只保有。故局部超时或失 ACK 不能形成“已经物理开动但所有者当作没提交”的合法历史。部分 START 由完整掩码保有覆盖，不需要全批动作原子启动。

定理 70-D（无替代 MOVE 与提案域局部性）：每个新 START 的规范字节等于其 PIE proposal 的对应 MOVE；这是 verifier 的直接必要检查和门绑定结果。对两个掩码/entry 资源完全不相交且无共享处理/查询配额的独立事件分量，改变一方资源/报告不会改变另一方几何和票据的布尔有效性。它不保证有共享计算预算时延迟不变，也不保证闭环提案字节相同。

定理 70-E（信息改善仅在冻结比较中单调）：固定同一原 MOVE、其他资源权利、几何及预算；有效较大 q 使旧事务剩余阻塞掩码缩小，所以仅由该掩码造成的阻塞不会增加。全闭环吞吐不在定理中；额外查询代价、不同后继提案与资源争用均可使效用更差。

终止/复杂度：单个本地调用处理有限事件和有限提案后返回。设 a 为本轮提案数、r 为瓦片数、b 为几何和票据输入比特长度、L(b) 为有理线性可行性判定的比特成本。预计算/最终重算每条直边掩码各至多 r 次判定；一次几何判断 O(r L(b))；本轮总成本 O(a r L(b)+V+S)，V 是本轮实际签名/票据验证成本，S 是排序及消息/掩码操作总成本，全部计费。每条真正到达的消息和每次最终复核分别计入，不把网络等待、重复消息、恢复或 a 次 CERT 隐藏为 O(r)。活动掩码 O(a r) 位，加实际票据/事件队列和持久防重放存储；后两者不宣称常数界。

没有无条件活性/最大并发定理。条件性单 MOVE 完成需要：阻塞者在有限时间释放；消息/决定/查询最终成功；该 agent 最终获得公平服务；执行器最终启动且沿边有足够累计正进度。永久分区、硬件永久停住、满占旋转、几何走廊过窄都可永久阻塞。它们保留在效果评估中，不用定理前提删去所有困难场景。

## 9. 按阻塞原因取证的确定策略

阻塞表的每行是 (waiting_proposal_id,blocking_tid,res_id,holder_generation,reason,first_seen_round)。reason 只能为 GEOMETRY、RESIDENT、UNDECIDED、COMMITTED_SUFFIX、ENTRY_BUSY、INVALID_EVIDENCE、SERVICE_UNAVAILABLE。GEOMETRY 不查询，查询不可能改变空间包络；RESIDENT 若没有已发行 MOVE，物理上仍要保有，不要求它凭空让路；UNDECIDED 发决策恢复读取，不假装传感测量能代替 COMMIT 真相。

COMMITTED_SUFFIX 行在该 tid 当前掩码中确实含阻塞瓦片，且存在较后切点使该瓦片消失时，才产生一次进度查询候选。ENTRY_BUSY 的当前 tid 可请求 terminal latch 检查；若已发未回，不重复发。候选按“被其阻塞的不同当前原提案数”降序、first_seen_round 升序、tid/res_id 字典序排列。一次可用查询机会取第一项；同一次查询可覆盖同 tid 多个瓦片。查询请求对 tid 和 occurrence 绑定，返回 §5 测量或不可用状态；不得让查询服务读待比较方法的评分结果选择返回内容。

一次 query opportunity 是公共计算/通信调度器的显式事件。所有方法获得同样的调用能力与收费接口；策略不能自己制造免费机会。当前预算不能支付则记 BUDGET_DENIED，不调用，不修改权利；服务不可用则记 SERVICE_UNAVAILABLE。本次请求完成且收到后来新的机会后可重试，但每次都计费，按上述排序重新取候选。只对同一尚未返回请求去重，不把暂时不可用者永久封死。

安全对照采用 2×2 全矩阵：查询选择为 BLOCKER 或 ROUND-ROBIN，退休时机为 SUFFIX 或 TERMINAL-ONLY。四格使用同一查询服务；返回有界进度样本，若实体已经终点吸收驻留并完成旧门 latch，则还返回同规格 terminal 证据，所有费用共同计入。TERMINAL-ONLY 收到中途样本不退休，只有 terminal 才释放非终点掩码。BLOCKER 的查询候选仍按相同几何上可退休的阻塞表排序，不能凭所属实验格改变服务响应。ROUND-ROBIN 按活动 tid 循环字典序、跳过未返回的已有请求。FULL-BLOCKER 就是 BLOCKER×SUFFIX，与 ROUND-ROBIN×SUFFIX 只差选择规则，构成主比较；其余格用于退休时机主效应及交互，不假定两收益可加。不可把全局完美观测/互锁只免费给 FULL。

待证伪机制链：查询落到真实阻塞的在途 tid → 获得能够推进切点的有界证据 → 退休确实不再可达瓦片 → 待决原 MOVE 通过现有 PREPARE → 减少等待。每一箭头都有独立日志字段；如果多数查询不能退休、退休后仍被另一资源阻塞或成本抵消完成数，则不支持该场景中的收益。

## 10. 启用、排空和停用

区分原生域与共同物理底座域。NATIVE-OFF 是全程未安装介入行为的原 R0 轨道，仅在原生离散假设下比较字节恒等；ACTIVE/SHARED-OFF/DRAIN 是已安装共同几何、entry 和事务底座的轨道。没有把额外安全底座的效果算给查询策略。

公共底座初始化成功后，SHARED-OFF 采用 TERMINAL-ONLY 的安全驻留/发行规则；ACTIVE 改用后缀证据与指定查询策略。SHARED-OFF→ACTIVE 只在本地入口事件边界改变策略标志，先接管已有 tid、claim、持久证明和待回查询；现有权利不清零。ACTIVE→DRAIN 停止新的非终结主动查询和新 MOVE 申请，推进/保有所有旧决定与终结；只有无旧 PREPARE/COMMIT 责任、全部 agent 驻留证据和 resident 转移完整、待回旧 query 已 tombstone 时，DRAIN→SHARED-OFF。暂时查不到某 tid 不算排空。可按独立资源分量接管，但任何共享资源必须有唯一 owner 和入口决定者。

NATIVE-OFF 不允许凭外部“现在可能有误差”通知直接跳入 ACTIVE 并主张全过程物理安全。若要同一次运行从原生轨道接管，先停发新授权并等待可验证的合法驻留、门关闭和全部旧责任清单，按 INIT 建账；这个接管前段只享有原生模型的原有保证。不能完成则保持未接管，记录 TAKEOVER_PENDING，不称安全域已经启动。本候选的主实验不混用这种跨模型接管；运行时开关实验只在共同底座内进行。外部触发不是完美故障探测器。

冷启动恒等的精确范围：同一 R0 commit、同初态、同外生流/随机流、同选项和同环境（包含规范回放中的时钟返回与线程调度输入），NATIVE-OFF 分支不调用候选模块，原 R0 规范输入输出逐步相同。归纳理由是每一步调用和状态转移均相同。这个性质不覆盖曾介入后重新停用的执行历史，不覆盖共同几何底座改变后的原版字节，也不把墙钟测量噪声计成算法字节承诺。

## 11. 未执行静态故障 witness 与机械检查合同

下列都是纸面符号构型和预期，不是已运行测试/轨迹。所有 r 表示声明几何所得瓦片；不同符号的初始驻留掩码互不相交，除明确指出的故障构型。q<q' 为同 tid 的合法切点，U/M 按 §5 计算；每个结构实例化时仍须核验其几何可实现性，不能随意手造与身体不一致的资源集合。

| ID、固定初态 | 有序事件 | 预期分类和要检查的不变量 |
|---|---|---|
| W01 假完成；A 的 ISSUED(0) 仍可占 r，B 原 MOVE 需要 r | 普通 A:COMPLETE 到达；B PREPARE | B 阻塞，A 不退休；70-A/B，假消息与延迟不同 |
| W02 同 tid 有效证据下界 q、q' | 先送 q' 再 q，再重复 q' | 最终下界 q'，资源不会重新扩大或重复释放；max 合并与防重放 |
| W03 旧 tid 已 terminal，r 已归新 holder | 迟到旧 q' / TERMINAL，epoch 字面值可相同 | tuple/generation 不符拒绝；不释放新 holder |
| W04 A COMMIT 未 START，全部 M(0) 已准备 | A 失联；B 请求 A 掩码内 r | B 阻塞，不能因没看到身体移动而回收 intent |
| W05 所有票已持久，D 未决 | 协调者 COMMIT CAS 与恢复者 ABORT CAS 交错 | 只能一个成功；两个可能次序各满足 70-C |
| W06 D 已 COMMIT，owner 未收到通知 | 协调者崩溃；owner 查不到 D；执行器持完整 COMMIT 启动 | owner 保有，实体仍被掩码覆盖；UNKNOWN 不释放 |
| W07 resident 属 A，A 新票含 parent | D=ABORT 后清理所有新票 | 原 resident 仍有效；安全 HOLD 可继续 |
| W08 A、B 新 MOVE 各完整掩码不相交 | 两个 COMMIT；A 先 START，B 任意晚 START | 部分启动无冲突，不借全批原子假设 |
| W09 A 在 u、B 想进入 u，A 提案将离开 | A 因另一瓦片阻塞，B 申请含 u 掩码 | B 从开始就见 resident 阻塞；没有单体 WAIT 引入新冲突 |
| W10 若干 agent 占满环路顶点，全部提案旋转 | 每个申请都要另一个 resident | 全阻塞/有效负例；不主张最大可动集合或无条件活性 |
| W11 A 已推进但未到终点；B 原 MOVE 只与 A 的已越过部分相交 | 有效 q' 使交集瓦片退出 M_A(q')，持久退休后 B 重试 | B 可通过；TERMINAL-ONLY 仍阻塞，展示条件性机制收益 |
| W12 相同 W11，但测量没有推进切点 | query 返回 q 或 SERVICE_UNAVAILABLE | 无退休、无放行，费用仍记；不伪造收益 |
| W13 两平行标称通道间距 d，身体半宽 ρ，允许偏移 ε，满足 2ρ<d<2(ρ+ε) | 两实体分别朝内偏移至模型允许位置 | 标称点/名义身体可不碰而真实身体碰；膨胀掩码预先互斥；几何因素不是起步失败 |
| W14 A 边上 s<ℓ、v>0，停止命令到达 | 沿原边按制动合同演化至 v=0 | 保有整段未来/制动责任；输出 CONTAIN_OLD，不打印顶点 WAIT |
| W15 同 W14，但实际制动力不足/响应越出已声明域 | 执行外生域外故障 | MODEL_BREACH，若碰撞同时保留 collision flag；不能作为定理内安全支持 |
| W16 合法驻留但原提案 WAIT；另一个 agent 无驻留证据 | 分别进入总决策函数 | 前者 HOLD，后者 NO_NEW_AUTHORIZATION；不使用空 K 全称真 |
| W17 所有票看似齐备，一票 mask_hash 或 entry occurrence 错误 | 最终 verifier 拒绝；协调者尝试 ABORT | 没有新 START；已决 COMMIT 只能走旧事务恢复，不能强制撤销 |
| W18 老执行命令 tid_old 与当前 tid_new 使用同 epoch | old START 重放 | entry 的 tid/occurrence/单次序号拒绝；只看 epoch 的删减版为负控 |
| W19 A 已凭 q' 退休 r，之后 r 被 B 获取 | A reboot，易失 j 丢失 | 从退休证据/持久下界重建 q'；不得用 j=0 重认已丢 r；证据永久损毁记域外/隔离 |
| W20 ACTIVE 有 COMMIT 未完成 | 请求停用，旧 ACK 丢失，随后恢复得到 COMMIT | 保持 DRAIN，保有旧责任；不能零清单旁路到 OFF |
| W21 普通反馈同字节，物理分别“已清空/未清空”，无有效真测量 | 决策输入除隐藏状态外完全相同 | 无法同时无条件放行且保证安全；有信息假设必要，阻塞不是活性证明 |
| W22 A 在两方法中被分别放行/驻留 | 同外生键触发 FALSE_COMPLETE，payload 分别从各自状态产生再施加同类变换；一方无发送事件则 NO_EVENT | 不能强制共享不可能的真实报告；比较块与计费同时分叉，§13/14 |
| W23 A 的完整扩张掩码触障碍，普通定位报告声称中心通畅 | 几何校验后到达若干好消息 | 永久 GEOMETRY_REJECT，不靠测量把固定空间模型缩小 |
| W24 同一 query opportunity，多个等待者被 A/B 不同瓦片阻塞 | FULL 选阻塞数多者；ROUND-ROBIN 按循环取另一者 | 信息能力/单次费用相同、选择不同；不预设 FULL 一定较优 |
| W25 NATIVE-OFF 同规范输入与随机流，另一路曾 ACTIVE | 逐步比较原生冷启动；再比较有干预历史者 | 冷恒等应成立；跨历史恒等没有承诺，不混在同一个通过统计 |
| W27 在途时间短于有效测量交付时间，普通消息不供可信缩减 | 中途发查询，实体先 terminal，之后才收到样本 | SUFFIX 可能没有中途退休收益，查询仍付费；延迟/收益尺度负例 |
| W28 本轮运行所有可信样本均不可得，普通 COMPLETE 可假 | 多次公共查询机会但都不可用 | 后缀和终点都不能凭假报告退休；永久阻塞负例，不声称无条件降级安全/活性 |
| W26 declared exposure 未结束，方法崩溃且未发新动作 | 保留最后日志，结束该次物理计算，评分扩展为零新增任务至 declared cutoff | 分母保留、科学失败不重试；“评分吸收”不伪称模拟了剩余物理过程 |

机械检查将来只在授权后实现，当前合同如下：

- 输入层：候选/几何/源代码/公开数据 manifest/预算登记的散列；配置合法性证明；所有事件原始字段与前后记录；不能只读候选生成的 PASS。
- 几何层：独立计算瓦片与 U 的相交；对每个物理积分区间用保守连续包络检验真实身体互碰与障碍接触。只看离散端点不合格；数值不确定区间记 UNKNOWN/NUMERICAL_INCONCLUSIVE，不能算无碰。
- 事务层：从原始持久事件重放每资源的 generation/owner/holder、D CAS、entry 状态和退休证据，检查不同 agent 排他、旧责任没有无证据消失、每个 START 先有完整权利。
- 动作层：检查原 MOVE 字节和 occurrence 对应，WAIT 必有驻留；CONTINUE/CONTAIN 单列；拒绝把 planner 自主改后继路径当本次外层替代 MOVE。
- 知识层：后验 oracle 可读取模拟器物理真值验证 q≤s 及包络前提；算法/查询调度不许读该 oracle。校验报告区分“证书不合法”“前提违反”“不变量反例”。
- 证伪输出：每个 W 的初态/事件/预期/实际证据链绑定散列，反例给最短已记录前缀及相应定理前提。未执行、UNKNOWN、超时和进程 exit=0 均不是 PASS。
- 程序级检查只为未来授权后的规格实现验证；本稿没有创建测试脚本、测试套件或实验 trace。原法检查、机械检查与主实验是三个不同许可动作。

## 12. 唯一公共数据选择器与 manifest 语法

R0 的 lifelong_benchmark 固定 tree 为 22ae3c8b3ad1f4791bd8c15b7d7b5521ed043c17。已核实浅层类别树：city 3e12a4483e615cd1a261d1e2476a29294fa4d0d1，game 8d8f8fbe8d16d80f5dab7a5cbf5ab6f3a341215a，random 2264326dfda14559e0db92e1649aaf512f9ff98f，warehouse-s 60b252f11972fed7d12f00960a7c6738b3f35a19；delay 树为 4e3fe329a547e682d1520047bf767a5397b3b43f，它只作为被 JSON 引用的数据来源，不再作为独立地图类别重复采样。warehouse-s 的 agents/maps/tasks 子树也已核实存在，分别 9d343cdafe66122ed15c3531be1af04fae5faa84、d1248ff1cf4af4163a64828e1398f7b02a98bef8、c27c62cb21a662a1891a480f348096a3c83b047c。未根据任何 Q-CAL/Q-CONFIRM 内容选择它们。

函数 SelectPublic(commit, density_binding) 的纸面函数体：

1. 若 commit 不是指定 R0 或 density_binding 尚未被授权登记，返回 UNINSTANTIATED，空输出不是“没有可用样本”；当前即此状态，不读取/生成新实验载荷。
2. 从上述四个类别的直接子项选普通 .json 文件，大小写敏感、按 UTF-8 路径字节升序；不递归扫描其他目录。按真实 driver 的键解析 mapFile、agentFile、taskFile、delayFile、teamSize、taskAssignmentStrategy。不得按文件名猜数量或概率。
3. teamSize 仅与未来合法 density_binding 的原含义比对；不在本稿设置 density N。各相对路径严格以 JSON 所在目录解析，规范化后须仍在固定仓库 lifelong_benchmark 内；只取普通文件，禁止符号链接/路径逸出。引用 tree/blob/byte size 全部绑定。
4. 数据合法性由无副作用解析检验：地图头/尺寸/字符合法，起点数量足够且使用 driver 规定前缀，起点在可行顶点且无重复，任务流非空且顶点合法，delay 数据 agent 维度/索引与实际原读取语义一致，任务策略属于实际三种分支。失败输出带路径/原因的公共排除记录，不能依据算法效果排除。
5. 去重键为 (map blob, consumed start prefix digest, task blob, delay blob, teamSize, task strategy)。重复保留排序最前路径，所有别名仍列在 manifest。不把共享地图的两个路径当独立地图。
6. 返回全部合格记录，不挑“代表性最好”的一部分。若某个预声明类别在合法 density_binding 下无记录，主四类总体不实例化，记 ROSTER_DOMAIN_EMPTY 并返回设计审查；不得事后改权重把空类悄悄删掉。某类地图几何膨胀后不可执行仍作为该物理条件中的结构失败保留，不据候选成功与否再过滤。

主 Roster 使用按上述源记录展开的闭环对照；外部原 MCP 样例只属最小原法检查，不混进 lifelong 完成率总体。外部 MCP 的共同底座版本对每次由同一 PIE 软件产生的固定路径提交段运行其执行政策；独立原版则使用其本来 MAPF-DP 样例域，指标与终止条件按原法，不拿一次到达任务的 SOC 直接除成 lifelong 吞吐。

manifest 每条记录必须含：
schema_version、record_id、repo_commit、category、json_path/blob/hash、所有解析后引用 path/blob/hash/size、消费前缀规则、task_strategy、geometry_schema/hash、body/误差/切点/瓦片模型绑定、factor_profile_id、planner_stream_id、exogenous_stream_id、公共停止/收费/查询机会合同身份、methods、block_id、cluster_id、alias_paths、preflight_status。
record_id 是这些规范字段的散列；canonical serialization 使用 UTF-8、对象键字节升序、有理数为最简分子/正分母、禁止 NaN/隐式浮点/重复键，数组保留合同顺序。源哈希不代替语义字段。

所有配置先作为符号参数的未实例化登记；未来填写具体合法物理/计算/实验值要成为独立可审查登记，不能在看过结果后挑值。本文确定选择和统计函数，不以新名字给 H、T_delay、B_CAL、B_max、B*、P_active 或 density N 提供隐含值。

## 13. 故障事件、处理耗时与公平外生耦合

事件规范字段：
(event_id, block_id, stream_domain, semantic_key, parent_event_ids, type, actor_id, recipient_id, occurrence, tid, resource_id, generation, logical_emit_time, delivery_time_or_missing, innovation_ref, ordinary_payload_or_certificate_ref)。
type 的闭合枚举为 PROPOSAL_READY、PREPARE_REQ/ACK/REJECT、DECIDE_REQ/RESULT、START、PROGRESS_SAMPLE/RESULT、TERMINAL_LATCH、ORDINARY_REPORT、DUPLICATE、DROP、PARTITION_ON/OFF、CRASH、RESTART、QUERY_OPPORTUNITY、PROCESS_SLICE、MODEL_BREACH、RUN_STOP。禁止把 GroundTruth 指针放入算法可见字段。物理区间积分记录属于 oracle 通道，不是候选事件。

外生域至少分开：规划随机性、起步失败、加速度扰动、空间偏移驱动 w、测量误差、普通报告错误、网络传输、查询服务、处理成本。根随机键彼此隔离；同一配对块各方法使用相同根外生创新机制。随机生成器版本、编码和子流规则在实例化前散列冻结，本稿不生成任何种子实现值或 tape。

实体扰动按 (block, agent, absolute physical interval index, disturbance type) 寻址，表示同一物理环境时间场；查询噪声按 (block, agent, occurrence, query ordinal, observation type) 寻址，表示相同语义请求序号的创新。普通报告故障按 (block, agent, occurrence, report type, emission ordinal) 寻址；依赖请求的网络传输按完整消息语义键寻址。不按算法内部“第几次调用随机数”对齐。存在共同地图/时间场的 agent 或 tick 不视为独立样本。

同样的外生错误操作用于各方法自身的有效原 payload：
STALE 选择同一 sender 已存在的上一 occurrence 报告；若没有，NO_EVENT 并记录，不编造前史。
FALSE_COMPLETE 把当前真实生成的普通报告的阶段字段替成 COMPLETE，保留其 occurrence/tid；不伪造可信测量证书。
WRONG_POSITION 对普通位置读数施加外生偏移/替换规则，变换参数是未实例化 profile 的字段。
DUPLICATE 重送同一已产生的 event_id，不能算新证据。
DROP 不交付；REORDER 用各消息的外生交付时刻决定，不逆转消息的因果生成前提。
同一键在某方法根本没有发送/查询事件时记 NO_EVENT；该方法不能得到另一方法才有的真报告或费用减免补贴。可信测量越界只属于显式域外负控，不混入定理内普通假消息。

绝对时间上，现有 MOVE 的连续状态在 planning、certification、query、网络、事务恢复期间继续演化。PROCESS_SLICE 含已消费计算量和对应耗时，完成后才生成下一可见结果。原始 R0 “先算再推进逻辑执行”的轨道保留原样；共同物理底座轨道通过这个计时适配器改变语义并明确标注。不能让候选查询期间世界冻结，却让基线计算期间机器人移动。

同时刻总序：先物理区间终点/本地强制制动与终点模式，再持久决策线性化结果，再到达证据/报告，再恢复和候选决策，再新 START。相同类别按 (actor_id,semantic_key,event_id) 字节序；不同部署可有不同真实线性化先后，但一次 simulation/replay 必须显式记录，不能让评估器择优排列。输入事件必须因果有向无环；非法时间前移输出 INVALID_TRACE，而不是自动修正成有利历史。

W22 展开：块内相同初态，M_full 获准 A:u→v，M_control 仍在 u。后来普通报告的真 payload 分别是各自进度，而 FALSE_COMPLETE 操作在两者都替换阶段；输出字节不必相同，且各自动作/查询费用进入各自账本。下一轮 PIE 读到的允许观测可能不同，故提案也可能不同。固定快照的 verifier 对照可以共享同一 P 和 K；闭环效用对照共享软件、任务生成规则和外生创新，不能同时强制相同闭环提案字节。


参数化执行/扰动函数补充：公共执行器在边内采用确定的名义加速 u_nom=a_drive(1−v/v_cap)，对 v>0 取 u_ctl 为 u_nom、γ_speed(v_cap−v)−δ_acc、γ_brake[2 a_brake(ℓ−s)−v²]/(2v)−a_brake−δ_acc 三者最小；可行输入要求制动力容许不低于 −a_brake−δ_acc。v=0 时不使用除 v 项，实施单向边界 dv/dt=max(0,u_ctl+d)；终点吸收模式另按 §4。由第三项可得制动裕量 h 的导数≥−γ_brake h，因此不仅检查边界瞬时导数。各 γ、a_drive 为未赋值物理模型参数，控制器对所有共同底座方法完全相同，不能由候选自行优化。控制器未来数值离散实现还须满足连续包含校验；离散误差不默认为安全。

每个外生 profile 的形式固定为有限离散分布表 (value, rational mass)，按规范 value 字节序累加分布后用 U∈[0,1) 的逆分布函数取第一个累计概率严格大于 U 的项；退化零因素是单一中性值。表只含 §4 已允许范围内的 d、w、测量误差及 §13 的故障枚举/时长/处理工作片段，不准加入新控制策略；质量非负且和为一。具体表项数值当前未实例化，不生成 tape。物理驱动在公共绝对时间分段上保持常值，分段端点表是公共 profile 的一部分，不依某方法是否完成某 MOVE 改变。起步尝试在公共执行器机会事件上，对已有已提交 tid 按 (agent,occurrence,attempt ordinal) 取失败/成功项；失败保持源驻留且不产生新 MOVE。

普通报告在公共报告机会事件上由各自物理状态形成普通 payload，再按该机会的故障枚举做 §13 变换；查询仅在实际请求后产生样本。组合因素允许由同一个 profile 中联合表保持明确相关性，不强行假设扰动之间独立；配对方法共享相同联合创新。谱系/条件表、机会时间表和每项成本全部是 manifest 的完整值字段，缺字段则 UNINSTANTIATED，不能由实现者临时补默认模型。随机实现按 canonical_key 与未实例化根 seed 生成 SHA256(domain || length-prefixed-key || counter || root_seed)，将 256 位无符号整数除以 2^256 得 U；根 seed 之间独立性的实验假设另登记，伪随机键不被当成数学独立性的证明。本文只规定算法，不计算一个随机输出。

## 14. 纯仿真公平预注册：函数、分母与证伪

### 14.1 对照与研究问题

| 轨道/方法 | 动作与信息接口 | 归因范围 |
|---|---|---|
| NATIVE PIE-D R0 | 原源码的规划和 MCP 执行、真实原生状态/延迟输入；原论文域 | 官方原法保持，必须保留；不声称原法能处理其未建模反馈错误 |
| NATIVE 外部 MCP | 冻结外部 app/MAPF-DP/MCP、原定路径与真实 head/tail/getT | 已发表外部执行基线；原适用域单列 |
| SHARED PIE-D / 外部 MCP 适配版 | 同公共几何/entry/事务/测量能力；在其实际执行接口上生成或抑制已有原 MOVE，原读真值接口替为共同证据适配器 | 明确名为 adapted；变化和成本列出，不能说是原版 |
| SHARED TERMINAL-ONLY×ROUND-ROBIN 与 ×BLOCKER | 同 PIE 软件、公共物理底座；完整掩码至 terminal；分别轮询/按阻塞查询同服务 | 补全 2×2；保守释放控制，不伪称独立已发表方法 |
| SHARED ROUND-ROBIN-SUFFIX | 同后缀与票据算法，轮询活动 tid | 主查询策略对照 |
| SHARED FULL-BLOCKER | §7/9 完整组合 | 主处理 |
| SHARED GLOBAL-BARRIER | 所有当前 tid terminal 前不给下一批；相同身体/观测/费用 | 保守控制，不能当唯一基线证明优越 |
| ORACLE 上界/违前提删减 | 精确信息或故意删膨胀/信假报告/无门检查 | 分列上界与不安全负控，不作公平 deployable 安全竞赛 |

适配版不能凭空使用原实现的真实 getT：entry/terminal 的离散 occurrence 由共同证据适配器提供；在途记录不得乐观映射成下一个顶点。共同版本需完整记录每个真值读取替换位置，若无法忠实定义则该 adapted arm 不可运行，返回协议修订。外部 MCP 对固定提交路径的排序逻辑保留；不能偷偷换成 Causal-PIBT 的新路线，或声称它与 PIE-D 整个 lifelong planner 等价。

主效用假设为：在“非零空间偏移包络 + 普通反馈不可靠 + 正处理耗时”的预声明模型内组合条件中，FULL-BLOCKER 相对 ROUND-ROBIN-SUFFIX 的全部发起配对运行，按下述固定权重的任务完成率差为正，且机制链确有中途退休和原 MOVE 放行。TERMINAL-ONLY 对比后缀机制为次要比较。零误差/只有起步失败、物理误差独立、反馈错误独立、组合、可信能力违约负控均预先分开报告；不会把只在一个有利条件显著当所有情形有效。

### 14.2 参数化 Roster 与停止函数体

令 C 是尚未实例化、结果不可见时登记的公共运行合同，字段为 declared_sim_exposure、wall_cap、charged_work_cap、query_service_allotment、replicate_keys、factor_values 及保护参数登记的原身份。前四者分别是模拟时间暴露、墙钟限、计费工作限和可用查询服务表；它们不是保护符号的新释义，不在此给值、范围、默认值。若任何必要绑定缺失，函数返回 UNINSTANTIATED，不生成运行。只有合法且 declared_sim_exposure 严格为正的已登记合同才能 launch；这是分母合法性要求，不是对 H 等给区间。

FactorRoster 是以下因子存在/关闭的全组合，重复零模型归为同一规范键：D-start、空间运动误差、普通反馈错误、处理耗时；有误差的函数形式就是 §4/13，具体幅度/持续分布由未实例化 factor_values 登记，方法间相同。可信证据失真、包络越界、持久数据损毁作为独立域外负控类别，不和主总体混合。没有根据先导结果决定保留哪个因子组合的分支。

Roster(C)=SelectPublic 的所有合法去重源记录 × FactorRoster(C) × C.replicate_keys × 当前轨道合法 methods，按 (category,map blob,source key,profile key,replicate key,method id) 排序。每个配对块包含同一源/初态/任务规则/profile/外生根键的所有方法，method 只是块内处理标签。缺一个主方法的块仍保留为缺失/失败块，不能只对双成功块算效用。

Stop(C, log_prefix)：
- 若发现 oracle 碰撞、已承诺协议不变量反例、不可恢复输出/程序崩溃或数值验证无法继续，立即停止该运行计算并登记对应多标签；
- 否则若 elapsed_sim≥declared_sim_exposure，正常行政截止；
- 否则若 elapsed_wall≥wall_cap 或 charged_work≥charged_work_cap，行政删失并停止新计算；
- 否则继续。查询配额用尽只拒绝后续新 query，不使旧实体凭空停止或释放权利；它不是算法可选择的删样本触发。

停止前的旧 MOVE 仍由控制器/claim 的安全规则负责；“停止记录计算”不是一个释放资源事件。对未完整模拟至 declared exposure 的运行，剩余时间的评分采用零新增完成数的吸收扩展；它是预声明效用惩罚，不声称继续算过剩余物理过程，更不补出安全结果。

Exposure(C,log)=declared_sim_exposure 用于主效用分母，所有方法相同；observed_physical_exposure=min(最后被验证物理时刻,declared_sim_exposure) 另报用于安全观测时间，二者不得混用。每次 launch 从同一模拟起点开始，launch 后立即崩溃也有正 declared 分母和零完成数。若 C 不合法则不 launch，但保留全 roster 的 PRELAUNCH_INVALID 记录及原因。

Classify(log) 返回全部事实 flags，再给主终类：碰撞/障碍接触优先为 SAFETY_EVENT；无安全事件但模型界/信任合同违反为 MODEL_BREACH；否则协议/独立 verifier 反例为 PROTOCOL_INVALID；否则程序/输出错误为 EXECUTION_FAILURE；否则费用/墙钟上限为 ADMIN_CENSORED；否则到 declared cutoff 为 COMPLETED_EXPOSURE。持续不动而未证明死锁只标 STALLED_OBSERVED，不能因为有限时间没完成就证明无限死锁。缺日志同时标 UNVERIFIABLE；即使越界先发生，随后碰撞的 flag 也不删除。

Retry(log)=仅当失败发生在 launch 之前、没有任何物理推进或算法结果可见、且记录明确是获取依赖/基础连接的故障时允许恢复同一任务；launch 后科学失败、算法超时、低效、碰撞和删失均禁止重跑替换。基础设施恢复次数和每次结果完整保留，直到公共 wall_cap 拒绝继续；缺失主方法的原 roster 行仍在。重试不是新独立重复，不产生新随机根键。为避免通过“预先看了不满意结果再标基础设施故障”，任何已出现 START/PROCESS_SLICE/结果字段都使 Retry=false。

### 14.3 主目标量、权重与不确定性

公共任务 oracle 使用原公开任务流和实际 taskAssignmentStrategy；任务发放按该共同规则，任务完成仅由真实身体到达当前已分配目标且 terminal 驻留成立时计一次。它向算法输出的通知仍经共同观测通道，不能把 oracle 真值旁送候选。因完成时刻不同导致的后继任务分配差异属于闭环效应，原全局任务流和发放函数不变。每发起运行的 Q 为在验证过的时间区间内、且在首次安全/协议失效前由共同任务 oracle 确认的完成任务数。主率 Y=Q/declared_sim_exposure；失败之后不再加任务，失败也不删。任意碰撞/协议失效仍单独使安全资格失败，不能用碰前高完成数抵消。

配对差 d_b=Y_full,b−Y_roundrobin,b。预声明四类权重相等；每类内不同 map blob 权重相等；每地图内去重源记录权重相等；每源内合格主因子 profile 权重相等；每 profile 内预声明重复权重相等。由这些权重确定 Δ=sum_b w_b d_b，不以每类有多少重复把最大类变成总体。若某层为空，主总体 UNINSTANTIATED/UNESTIMABLE，不能运行后改权重。所有方法共享这些权重。

重复间的独立性假设是给定固定公开地图/任务和 profile 后，独立外生根创新；不是 block_id 字符不同就自动独立。相同地图、同公开任务源、同环境时间场的多个 agent/tick 不独立。推断目标首先是这组固定公共任务分布的条件平均，不外推全部仓库。置信区间在地图/任务源层保持配对聚类，重复只在对应层内重采样；若顶层独立来源不足，报告描述性配对差与全部来源逐项结果，不给虚假的总体显著性。

统计协议预声明一个主比较、双侧 95% 区间，不把多个消融里最有利者转 primary。聚类 bootstrap 使用预登记固定重采样索引生成合同，重采样次数与随机实现未实例化时不运行统计；算法为按原层级有放回抽样，块内方法和全部 flags 始终共同抽取，重算同一 Δ，取经验分位数区间。必须同时报告原始层级差和区间方法/独立层级，不能以 bootstrap 把固定同一任务片段复制成新增证据。若其适用样本条件不满足，区间输出 UNAVAILABLE，不能照常报 p 值。

解释效应的证据必须同时包含：绝对 Δ、相对基准率（基准率为零则 NA）、逐类别差、计算/查询/网络/事务费用、完成/失败/删失分母，以及 query→cut advance→resource retire→原 MOVE START 的计数漏斗。相对改善零分母不能被设成无穷大并当主要结果。

安全原假设不是“零次观测碰撞即证明真实零风险”。一旦定理前提均成立却有反例，70-B 被证伪；若全部测试零事件，只能作为有限暴露支持。查询数/START 数为零时比例记 (numerator,denominator) 与 NA，仍保留该运行主 Y 和失败/阻塞标签。主效用不按“发生过可释放阻塞”的结果条件筛块；该子集只作已标注的机制描述。

### 14.4 两种计算公平轨道

STRICT：各方法相同 charged_work_cap，规划、几何、消息、测量、事务、恢复、证书全部入账；不把 unused compute 换成额外真信息。公共物理底座的相同部分可分别列 shared cost，但总端到端主费用不得省略。计费工作单位与硬件执行时间的映射要在结果不可见时固定；超过配额的运算只能按公共可中断边界终止，不准把下一周期预算借给候选。

NATURAL：冻结算法使用自身实现路径，实测端到端墙钟包含适配器、等待查询、处理和恢复；同 CPU/线程/编译/资源隔离条件，并记录队列等待。不能给候选多核、给基线单核却只报算法时间。两个轨道分表，不把一次 strict 收益和另一次 natural 收益拼为同一结论。任何共享底座的运行成本都对所有方法以相同规则计入。

本稿尚未执行环境校准或费用映射。原型实现后若必须改变计费定义、模型、场景或主目标量，则新编号修订并重新顺序审查；不能追认旧预注册。

### 14.5 什么会推翻本路线

定理内的任何几何/事务安全反例、alternative MOVE、无驻留 WAIT、旧 tid 误释放或接受非法证书，直接阻止实现/实验资格。无反例但主 Δ 的区间不能支持正效应、效应只在免费查询下存在、退休不能转化为原 MOVE 放行、计算代价抵消完成数、几何保守导致大片结构阻塞，均削弱或否定对应效用主张；不得解释为“还需调参直到成功”。新组合可以保留为负结果或更窄的适用域，但更窄主张要另立新工件。

POD 等未得全文的近邻不会被一句“不一样”排除。即使最终无首创性，也可按用户要求评估具有清晰增量和充分对照的组合改进；论文贡献表述应与已完成来源证据一致，不能把未知缺口变成首创。

## 15. 六门、原异议追踪与后续审查顺序

当前六门在 69R4 的有效根裁决仍是 1 PASS / 3 UNKNOWN / 2 FAIL。70 以下只给候选证据，不自授 PASS：

| 门 | 70 提交的证据 | 本稿状态 |
|---|---|---|
| G1 实际问题 | §1/2/4 区分实体空间、运动、观测错误和延迟 | REVIEW-REQUIRED |
| G2 已发表锚点 | 13 项一手记录，4 份期刊完整提取文本与阅读限制；近邻未得全文标注 | REVIEW-REQUIRED，强新颖性排除 OPEN |
| G3 官方 PIE R0 | §3 固定对象、许可、真实动作/状态/seam、文档差异和未执行原法检查合同 | REVIEW-REQUIRED；原 69E1 回执未到 |
| G4 外部已发表方法 | §3 原 MCP tag/commit、源码、原样例引用闭合；§14 原版/适配版分轨 | REVIEW-REQUIRED |
| G5 数据与场景 | §12 SelectPublic/manifest，§13 事件语法与自己的闭环 payload | REVIEW-REQUIRED；未实例化，不当已经生成 manifest |
| G6 纯仿真设计 | §4–14 机制、证明、事务、故障、检查、配对/停止/分母/费用与证伪 | REVIEW-REQUIRED；没有提前实验 |

原始 bearing 必须逐条追踪，不按多数投票抵消：

| 69 原意见 | 70 的具体修复位置/承认边界 |
|---|---|
| R1-B01，LG-01 | §4/5 的单调物理模型、issue-before-act、下界未来包含、持久退休；§8 归纳 |
| R1-B02，R2-B01 | §5 有限记录/积域/线性可行性掩码；§7 输入齐全 verifier；§8 真实比特成本 |
| R1-B03，LG-02 | §1/7 撤回最小闭包/最大性；完整预留拒绝投机跟随；§8 不隐去重复验证 |
| R1-B04，R2-B03，LG-04 | §6 分角色票/决策/入口守卫、部分启动；W04–08、W18–19 |
| R1-B05，LG-05 | §10 冷原生恒等与共同底座运行时接管/排空分开，明确跨模型未保证前段 |
| R1-B06 | §2 阅读深度与近邻限制，§3 固定源码实核；未到旧报告不冒领 |
| R1-B07，R2-B07 | §12 确定选择器/去重/合法性，§13 完整事件与 NO_EVENT |
| R1-B08，LG-07 | §13 W22 闭环分叉，§14 原版/适配/共同底座增量及费用 |
| R1-B09，R2-B06，LG-06 | §14 method 块内标签、层级/权重、主差、失败和零分母 |
| R2-B02 | §7 先几何/entry 条件再 PREPARE，最终失败总分支，无未得 token 的 Seed 循环 |
| R2-B04 | §9 触发/候选/排序/拒绝/重试，§10 模式 |
| R2-B05 | §13 自身 payload + 共同外生创新、绝对时间/语义寻址分开 |
| R2-B08，LG-08 | §11 28 个未执行 witness，§12/14 Select/Roster/Stop/Exposure/Classify/Retry 的函数体 |
| LG-03 | §5 空知识与恢复，§7 原 WAIT/旧 tid/最终失败总表，§11 W14/16/17 |

一个修复章节的存在不算闭合；审查可以发现新的承重异议。70 固定 hash 后，先注册科研导师 task/输入/完整阅读要求/报告路径并取得真实完整回执，再独立注册 Nature（不给前路结论），其有效返回后才派明确完全不用 skill 的独立逻辑审查，最后根代理逐项验收。承重意见要求 71 或其他未占用新编号的新字节，不修改 70 来伪造原审查覆盖。所有阶段保留初末身份、完整阅读范围、真实句柄和非空最终正文。

## 16. 保护与完成判定

H、T_delay、B_CAL、B_max、B*、P_active、density N 均未赋值；原含义不变。本稿不给这些符号数值、区间、范围、默认值、先验、估计、调参方向或几何新定义。复杂度用 a/r/b 等集合规模，不用 density N。原论文/源码原样例中的数字只用于来源身份/语义审读，没有转为项目实验设置。

冻结文件不改；52 不加侧车，69 不修改/封存；桌面只读、旧 35–38 与受限 Q-CAL/Q-CONFIRM 载荷不读；文件编辑仅 apply_patch，新工件只写研究目录；所有 shell 段前缀 rtk。来源读取、纸面推导和文档身份检查不等于允许原法构建或机械测试。

Claude 69C2 有完整建设性 NONBALLOT 回执，其中保护符号误用和若干不正确推理已在对应根批注拒收；没有用它代替本文证明。69C3 实际 504、零 tokens、无构造正文，已作为 TRANSPORT-FAILED 登记；不计意见。69C4 实际完整回执已返回（exec 4355、exit=0、ADVICE-COMPLETE），只读摘要、无 skill/工具、NONBALLOT。采用其 2×2 对照与负例建议；明确拒绝“终点释放无条件安全”、监控能证明真界、违约后收回已退休资源和 q 方向错误等论述。详见 69C4 完整回执根批注；不替代三路独立正式审查。

全部显式要求的最终审计还必须核对：导师实际误差目标、PIE-D 保留、一手路线比较/可访问性、原 L1/E1 任务和约定报告状态、每个承重源码对象和接口、模型保持与资源事务、总算法/模式、故障反例和机械合同、公平纯仿真统计、保护边界、逐工件顺序审查、精确私有 GitHub 同步。任一资格门、协议、承重审查或必要来源回执尚未闭合，则不能宣告实验前工作完成。

最终控制状态：HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

