69C3 — 根代理交给 Claude 的有限几何/相位构造任务（建设性 NONBALLOT）

请只依据本摘要做纸面机制与证明构造，不使用任何 skill、工具、文件、网络或子代理。不实现，不运行，不给实验/保护参数赋值，不产出实验载荷。你未读候选、报告或论文全文，不得声称读过；先前 69C2 已真实返回，但多处建议被根代理拒收。结尾必须 ADVICE-COMPLETE。保持 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。
本次请用约 5000–7000 中文字给出自足的建设方案及自攻击，而非投票。

项目不变边界：
- 只有 PIE 能产生新 MOVE；外层只能复制精确原 MOVE，或真实可执行的安全 WAIT，或继续/保有旧事务。绝不能生成替代 MOVE。
- H、T_delay、B_CAL、B_max、B*、P_active、density N 是项目保护符号，所有含义已经冻结。本次不要在公式中使用它们，更不能把它们当空间偏差、历史长度、查询数或新的变量。
- 物理定位/执行偏差须实际改变物理几何/占用，不能将 no-start 延迟重命名。连续/跨 tick 运动必须保留边上状态、区间占用和速度相关制动责任。
- 对非可信 COMPLETE/位置消息不因签名或新鲜性收缩状态；可信廉价/昂贵信息能力都需同底座比较与计费。算法不能读 ground-truth oracle。
- 局部资源 owner + 每个 tid 的协调者可以依赖精确公开的持久唯一决策接口；不声称靠普通消息实现了共识，不用全局强制停止掩盖缺口。

请评估并完成这个更弱的候选构想，也可指出它应被放弃：
A. 每机器人至多一个已发行但未终结 MOVE，固定 occurrence 身份，不存在任意 holes/跨历史指数状态。物理表示为 At(source)、Transit(原有边及有限相位)、At(dest)/Braked 等有限模式；每模式对应有理多面体占用包络。K_i 是有限 bitset，联合 concretization 明确为保守积域，账本独立精确。
B. 每个原 MOVE 的 swept mask 覆盖标称路径与有界定位/跟踪/制动包络接触的全部有限资源。固定控制器可含沿原轨迹的速度/横向跟踪修正，但不能改变 PIE 离散 MOVE；控制器和误差包络是共同仿真模型输入。必须区分：真实运动被已声明模型包含，是物理假设；互斥账本如何推出无碰，是待证结论。不要把“所有动作安全”作为底座公理。
C. 不依赖同批机器人必定释放起点，因此跟随/旋转可以被保守拒绝；同一个 agent 的旧 resident claim 与新 tid 之间需要准确转移。外层输出所有初始 WAIT/旧事务/异常知识的总分支。去掉 leastness/global maximality 的强主张，不禁止你对具体有限算法证明真实的多项式界。
D. PREPARE 获取全部目标 mask 的排他承诺；每 tid 持久 D∈{UNDECIDED,COMMIT,ABORT} 单次线性化决策，提交须有所有冻结有效票；ABORT 只释放本 tid 新准备义务，不释放旧常驻或已启动物理占用。任何未知保留。执行门验证完整 tid、epoch、resource generation 和已提交动作 identity，旧 tid 不可重放。
E. 主动取证改为定向获取阻塞者的、绑定 occurrence 和 resource generation 的有限相位/清空证据。由有限“阻塞原因表”给出确定查询排序，结果不复用为永久清空。请给出一个低复杂度可证 sound 的策略，使它确实比“一律等待全体新鲜证据”的共同安全基线有可证伪增量；不要承诺吞吐更高，也不把不嵌套/单指标失败判为整个方向没有科研价值。

你须给出：
1. 完整有限模式语法、每模式占用集合，以及至少一种足够具体但仍符号化的有界运动/测量模型。如何在不先实现控制器的条件下写出可纸面验证的包含/保持合同。
2. Init/Issue-before-act/Advance-silent/Observe/reboot/retire 各转移，尤其迟到证据、源位置旧 resident 权利、同一机器人授权接管、COMMIT 后未启动。
3. 一个不以“CERT 保证安全”为循环前提的确定判定，含自有占用的精确豁免和对其他 agent 的排除；给出不争用 MOVE、两者共享扩张 swept mask、一者 mid-edge/一者 WAIT 三个静态例。
4. 资源 owner/协调者/执行器分开的守卫；静态 COMMIT 与恢复 ABORT 竞争证明；资源 mask 保留如何防部分启动事故。
5. 原始 WAIT、抑制 MOVE、continue-old、empty-K、final-check-fail 的总决策表。
6. 模式启用/排空/停用合同：冷启动全程 inactive identity 单独证明；任意 runtime 切换保留安全但不宣称与从未干预 baseline 字节相同。
7. 对新构想最强的三条反对：是否过保守到无用、是否只是已有不确定性安全屏障和占用协议组合、哪些假设不可捍卫。列出最小可证伪效用目标与公平比较，不靠免费额外互锁获益。

已核实一手文献边界（仅摘要给你，不是你全文审读）：
Hönig RA-L2019 ADG/commit cut 已经处理执行依赖和边执行时序，但有不显著空间偏移、最终完成并及时通知的假设。
Zhong Autonomous Robots2026 planned synchronization 已有收费主动全状态观测、运动/测量噪声与观测耗时，不可把 active query 本身认新意。
Zhu/Brito/Alonso-Mora Autonomous Robots2022 B-UAVC 在 Gaussian 定位/传感误差下构造机会约束安全域、修改连续控制；双积分制动扩张是其明确写为 heuristic 的处理；空域减速不构成通用 invariant 证明；死锁处理会改变局部目标，不能无声接成精确 PIE MOVE。
POD2026 官方摘要与本项目话题高度重合，全文当前未读，绝不能断言它缺某一机制，也不能主张新颖性排除完成。

先前建议必须纠正：holes 的状态数量指数不等于 bitset 表示尺寸指数；非单调不推出不存在最小固定点；D=COMMIT 前必须核验所有有效持久票；空分母/全阻塞不从全部发起 episode 分母中删除；不能把 CLEAR 当前事实当未来永久通行证。

