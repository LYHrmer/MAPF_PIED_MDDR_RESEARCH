# 73E18：固定 R0 四堆调用域、ALWAYS_ADVANCE 继续域与最小来源修订

日期：2026-09-10。/root/source73_r0_remaining_contract；**NO-SKILL / CONSTRUCTIVE / NONBALLOT**。本件是新的有界来源建设，不是正式独立逻辑审查，不替失落旧任务，不投资格票。未修改 73 或源码；HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT，六门仍为 2 PASS、3 UNKNOWN、1 FAIL。

## 1. 可直接交根采用的结论

**对具名纯 LACAM 调用域，可以给出四种 LLNode 堆从建立到退出始终为空的条件归纳；正常软拒收不增加 Compare 调用边。当前应保留这两个谓词的原字节，并继续限定该来源入口。** 这是四种堆成员、两个谓词类型，不是四份不同随机函数。常驻的是每个 LNS Agent 的 SIPP OPEN/FOCAL；原提交验证还会建立并销毁每个临时 Agent 的 A* OPEN/FOCAL，后者不能漏掉。

这项结论没有把完整 ALWAYS_ADVANCE 继续域改成 PASS。新亲核 LaCAM 的 Planner::solve 存在“首次 while 因 deadline 未进入，仍先解引用空 H_goal”的具体控制流；它与四堆无关，却处于同一纯来源路径。既有第五堆、形状/索引/所有权/整数域、实际服务和构建绑定义务也不随四堆空而消失。**最小下一路线选择是 E6/E11/E12 的修复纯 LACAM-AA 适配，加一个精确的空 H_goal 失败分流；不改四个堆的比较器，不删除空求解器对象，不导入另一求解器或免费距离缓存。** 该选择仍是待资格化纸面合同，绝非“只修一个 comparator 即全源通过”。

C13 已成功取得真实完整 Opus/high 回执，支持条件归纳，但其 UB 三条件论、算法身份不变、审计费用代替运行费用及空解后自动重试均须修正；详见 §7 和独立完整回执。以下判断由本子代理不用任何 skill 独立完成，根仍须独立取舍。

## 2. 输入身份与实际读取层次

创建前已精确确认 E18 目标及 C13 prompt/raw/receipt 均不存在。先读以下报告的相关来源身份、调用路径及继续域条款；初次合并工具输出被裁剪，随后对 E6 §1–3/7–8、E11 §1–4、E12 §4–6/8–9 定点重新完整显示，不冒称本轮四件全部重新精读。E5 的 §1/4–6、依赖/入口及身份表相关内容与后续定点源正文交叉核验。旧报告身份如下，未编辑。

| 导航报告 | SHA256 | bytes / LF |
|---|---|---|
| 73E5_R0_LACAM_REACHABLE_DEPENDENCY_AND_LIBRARY_CONTRACT_20260908.md | cee608755ed49b43f690bcfe0c8bd56d827b5fea0365b6eac7f26c2b32a8ea53 | 38687 / 214 |
| 73E6_R0_REPAIRED_ADAPTER_MINIMAL_SOURCE_AND_LIFECYCLE_CONTRACT_20260909.md | 6f5205a871e6d8b2d45897283fd270d8c044fd48abeeac3b52acceab4b4a1dc6 | 34244 / 190 |
| 73E11_ROOT_R0_PRECOMMIT_SHAPE_AND_SOURCE_HISTORY_ALTERNATIVE_20260909.md | 9e3aa1ba8c3a6570b403f38780a5b17b9e8649058641fa5e816d07de121a02fd | 10985 / 61 |
| 73E12_ALWAYS_ADVANCE_SOURCE_HISTORY_FAIRNESS_AND_FAILURE_CONSTRUCTION_20260909.md | e4e6285012c53b3676a62bdab51b54798a8db225f3e95694f5a6a86b964ecc88 | 24294 / 137 |

此后只取得固定 R0 commit `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357` 的下表必要源码/头文件，通过官方 GitHub fetch_file 只读进入工具内存，未把源码落盘、配置或运行。每一完整返回对象均重算 Git blob，全部与 API 返回 sha 相符。SHA256 是返回 UTF-8 原文的字节身份，保留头文件 BOM；LF 与无末尾换行的物理行数分开。不是默认分支，不推断作者实际构建。raw URL 可由 `https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/` 加表中精确路径取得；本次实际调用为同 commit 的官方 API 对象。

| 固定源码对象 | API blob＝独立重算 | SHA256 | bytes / LF | 实际阅读 |
|---|---|---|---|---|
| [CMakeLists.txt](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/CMakeLists.txt) | 148459bb9542731723e8125bb8d54da6a3ce954b | ecdf7e3c889ab8290eb9cc839543c0f281419db957982a03b79ae79da25dc899 | 2790 / 92 | 全文，仅定位 include/源路径和既有依赖身份，不执行配置 |
| [src/MAPFPlanner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp) | 94afb42df1a70f5e312a382e61cf83576fd7360e | c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1 | 6125 / 208 | 全文 L1–208；含有效各模式、loadPaths、planner_commit 与注释路径 |
| [inc/MAPFPlanner.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPFPlanner.h) | 68fbfd7a13d2a1513c6634d41d0dca5133740aeb | d25fbcb08b6d80b4f03234b4f7c3c08c553d7074a7e12c47fee86d336409633e | 971 / 42 | 全文；动态接口、字段初值与析构 |
| [src/MAPF-LNS2/src/LNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp) | 1fb0e54f8f2bb00af05de53233ae600774e36f2a | 0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2 | 53100 / 1486 | 完整构造 L7–53；checkReplan 383–443；fixInitialSolutionWithLaCAM/getInitialSolution 496–542；runPP 544–644；runLACAM2 648–714；vector<Path> loadPaths 1186–1216；commitPath/setStartGoal/clearAll/validateCommitSolution 1236–1483；全文方法/标识符定位，非全文语义审计 |
| [inc/MAPF-LNS2/inc/LNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h) | 5b9ce3ef4aeaf6fcfa88c211c0f536c66f8ae24e | c9751aca5f3c305d5da49c3445ec29cb19819655b496de12c522d83d7af7ad91 | 4201 / 119 | 全文 |
| [inc/MAPF-LNS2/inc/BasicLNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h) | c22e0b66cc58e9c9ce19d6b161e4f54dabfb4c15 | 9927e17d5c6dd3624ed4e5dc3cc81c20eec854b340ddf4723f93d873a6b526ff | 2042 / 76 | 全文，含 Agent/Neighbor/BasicLNS |
| [src/MAPF-LNS2/src/BasicLNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/BasicLNS.cpp) | c0c3ca34fb0f1c55cb67b0693de9e42d5b6503cf | 662f58b4c8241c97933ee1272cf0d13f1733a1dbd9a120db7b620dea84e793ba | 731 / 24 | 全文 |
| [inc/MAPF-LNS2/inc/SingleAgentSolver.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h) | c22f59ac763c3bc272a82b5c8e9793a91f5da94a | daafdc674f90bbe4b34031b19f2564fb93189f07d7ad15e0927e1574cbb5611f | 7935 / 226 | 全文，两个有效谓词、LLNode、构造/虚析构/reset |
| [inc/MAPF-LNS2/inc/SIPP.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SIPP.h) | 9f2366ad6e8bf4084299b6d3649414394c850694 | 8ebf98b9518844473ac66f6064e5c9810774fe4f7f79fdb7e25fe4c69abd318d | 5725 / 131 | 全文，含节点、两堆、构造/接口 |
| [inc/MAPF-LNS2/inc/SpaceTimeAStar.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SpaceTimeAStar.h) | cdb96d96e01ae5efa43688019972efa37df01834 | ef1416a0098f08a17606d734b77f3722a61c3984f795d17d681cdef1dd937909 | 4052 / 112 | 全文，含节点、两堆、构造/接口 |
| [src/MAPF-LNS2/src/SIPP.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp) | 7f8db084c2d03929f51c28a76a29895fbaaa1a64 | 3cb627fcd4a0ebe2646be9985e58bd16ef5f01ff3fce357ab4584b0045d2e2b7 | 30068 / 680 | 完整 timed findPath L30–182；getTravelTime/updateFocalList/push/erase/release 453–567；dominanceCheck 634–680；不称另一 findPath 全文已读 |
| [src/MAPF-LNS2/src/SpaceTimeAStar.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SpaceTimeAStar.cpp) | 1712e6d081337461437e3458c40fdcb8ef3de8ef | 4ccef3b2b34a964bd5377e6b742876f371b4fa553d3aa458926c56b2f6f485ac | 10923 / 300 | 完整 findPath L23–189；getTravelTime/pop/push/updateFocalList/release 192–299 |
| [inc/MAPF-LNS2/inc/Instance.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/Instance.h) | 97808fa7929c1f99772b05b047c20d48bb878814 | ed1dea14eba7373d13b2378e59839bf962085316ffb6527655f92dfc5aae565d | 4939 / 154 | 全文，字段/访问器与无 solver 反向指针 |
| [inc/MAPF-LNS2/inc/lacam2/lacam2.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/lacam2.hpp) | b12113c7e263ac570f53f0af533ec86de9a8bb4d | 64bdb7cc7b0c0d439bd3dc5a029db70102a1e538b21208b8b3ffb129dce1bfa9 | 481 / 13 | 全文 |
| [src/MAPF-LNS2/src/lacam2/lacam2.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/lacam2.cpp) | 75ee58f4e1adb46ad3b26991cc212929bbff5f60 | 107bdd83cef76baf86831c0a0f3c421d64e65c36381494d7438dfb1f6b1f2f05 | 464 / 10 | 全文，solve 外层及局部 Planner |
| [inc/MAPF-LNS2/inc/lacam2/planner.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/planner.hpp) | 48ec12187373e87d6a233bfebea5eaf8b26c9304 | 8e7c6b7221828ef17a73730a3a33c39d5fcc9ccd9f73a6697c7434162ae7312c | 3850 / 132 | 全文，LNode/HNode/LACAMAgent/Planner 类型和持有关系 |
| [src/MAPF-LNS2/src/lacam2/planner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp) | 4f46f988d2c16f09c5a6f65bb9cd70e8e01aa483 | 8d2fa9131f0691b109a00dd6267b3b48f80df7778643daeb806ff82e20fe2789 | 19115 / 615 | 全文，全部完整函数；615 LF、616 个物理文本行，末行无 LF |


参考库合同**继承 E6 对根 E7 的核验**，不是本次再次读本机或泛查 Boost：所核主机 Boost 1.74 pairing_heap.hpp SHA256 668543a7a2ab2b4519452a5f841d36f30761cb99b102e3273d999adb3afe9fcd、stable_heap.hpp SHA256 24d78657787040120778df3d60396c1b1c16d6f5babc612431a028b9a387e371。默认构造置空 root，复制比较对象不调用 operator()；始终空的析构 while 不进入 pop；非空析构可能 merge→Compare。现主机头身份已知，未来实际解析 include、ABI、产物绑定仍 NOT_CONFIGURED / NOT_BUILT。E5 的条件 1.85 和最低版本不能替代该绑定。

## 3. 四堆在每一阶段的准确裁定

| 阶段/入口 | SIPP OPEN/FOCAL | A* OPEN/FOCAL | 裁定依据与限定 |
|---|---|---|---|
| MAPFPlanner 初始化的 LNS 建立 | 每 Agent 建立两个空堆，构造无比较 | 此持有集合不建立 A* | LNS 构造先 reserve，再 emplace；当前调用使用 SIPP；BasicLNS/SingleAgentSolver 构造不搜索。第五个 Instance 局部堆先于此存在，另论 |
| 首次纯 plan、initial_success 为假的合法源后继 | 不入堆，不调 Compare | 无新 A* 搜索 | prepareDummy/clearAll→getInitialSolution→runLACAM2；getInitialSolution 不看 init_algo_name 再偷偷选 PP，没有 PP fallback |
| initial_success 为真的正常后继 | clear/load/check 仅写路径/标量/表，之后直接返回或完整重新 LaCAM | 提交前无 A* 搜索 | fixInitialSolutionWithLaCAM 的所有有效分支已读；没有 LNS::run、LNS2 或 findPath |
| PRE_COMMIT_SHAPE 后的原提交验证 | 常驻 SIPP 仍空 | 新临时 A* 两堆从构造到析构均空 | validateCommitSolution reserve/emplace 后只复制路径、validMove/冲突检查，没有任何单体搜索；失败返回的临时对象展开也受同一空状态条件 |
| 合格完整事务被中心 STALE/版本变化/CAS 等软拒收后的下一合法输入 | 仍空；外部拒收不写堆或改模式 | 下一次验证重新建立空 A* | E12 的来源状态保留与 Π 权威分开；下一输入重装只在上述支路间选择，无新的调用边 |
| 部分输入安装、源异常、NO_PROPOSAL_SHAPE、内生 INVALID_OUTPUT | 不允许以未知状态继续归纳 | 不允许借验证正常返回推全源有效 | E12 会话停止，没有下一合法热继续；没有观测过实际损坏/UB。合法构造失败在所述空成员/库/所有权条件下展开，不凭进程隔离跳过证明 |
| profile 外的 runPP→timed SIPP findPath | 已见 FOCAL 入堆；不能据此说 OPEN 同时活动 | 不是这个调用选择 | SIPP L30–182 经 pushNodeToFocal；新旧节点需真正并存/合并才可能 Compare，实际随机平局需进一步条件；未运行 |
| profile 外的 SIPP/A* getTravelTime 或 A* findPath | getTravelTime 明确有 OPEN push | getTravelTime 有 OPEN push；一参 findPath 有 FOCAL push | 各完整函数已读；这是具名域外入堆路径，不是本域可达，也不是该函数每次必比较；其它前置定义域、堆节点状态仍有条件 |

在固定 R0 的 SingleAgentSolver.h 中，两个有效谓词先比较前置键，全键相等才现抽 rand；非平局分支的 >= 处已经有键不相等条件，不能单独把这些分支指认为“自己比较自己返回真”。真正的问题是全相等时比较结果依赖再次随机消费，不能保证同一稳定严格弱序。未发生调用不把这个关系修好，关系不合格也不自动证明当前会话执行它或已发生 C++ UB。

纯 LaCAM 的 LNode、HNode、LACAMAgent 与 LLNode/Agent 是不同类型；其 OPEN 是 stack，名字相似不等于同一堆。funcPIBT L393–471 在 sort 之前填 tie_breakers，谓词只读取本次固定分数，递归在 sort 完成后才发生。这里不是谓词里现抽 rand；不据此豁免浮点值域、索引和全部排序前提。runLACAM2 的局部 MT 按原源码每次重建，不能说 AA 必然保持它跨调用连续，也不能把本件四谓词没有贡献的随机消费扩写成整个源无随机性。

## 4. 可审查的空堆归纳及 AA 的作用

本件的不变量是：**当前合法存活的常驻 SIPP 对象及当前验证作业内临时 A* 对象，其两个 heap root 均空，且没有未完成的搜索节点/handle 所有权。** 这是对这些确切对象的命题，不是全进程所有堆为空。

基础由完整构造链与参考库的零节点构造成立。Agent 拥有裸 solver 指针，故合同保留 fresh vector 的 reserve 后 emplace、固定编号/数量和不复制 Agent；不能只因它是 vector 就假设复制/搬移所有权安全。基类虚析构已亲见，不再虚构非虚析构问题。构造失败展开中的已完成 solver 堆仍空；尚未建立的对象不凭空取得 LLNode。实际标准库/分配/展开行为仍须在后来绑定中兑现，空堆命题不认证所有异常路径。

保持步使用 §3 的完整函数，而非仅负搜索：输入重装写 env/paths，LNS 路径维护写 path、表和 solver 标量；两种 plan 后继都回到同一个独立 LaCAM；提交函数不搜索，临时 A* 验证不入堆。LaCAM 的持有集合与 Instance 头没有到这批 solver 对象的指针/回调，所读完整 Planner 实现也无相关调用。由此，在对象有效、普通合法 C++ 调用及所列入口封闭前提下，既有空 root 不会在下一步变成非空。

软拒收时中心只处理提议及公开版本，不读取或修改半成品 worker；完整正常源状态按 AA 保留。下一 job 仍须等待中心终态付费交回和占槽释放，由权威 Π 与当前已交付任务构造冻结 env。初始成功标志不同、neighbor 非空、目标变化或旧路径不能重用，只会使已读纯分支重走 LaCAM；**没有“拒收即改走 PP”的源码边**。因此这段空堆归纳不需要逐 job 快照、RNG 回滚或对不同臂补相同次数的调用。

这给的是具体充分条件，不宣称逻辑上最弱。Π 输入权威对整个协议必需，但来源错配若尚未造成非法访问，也不必然触发 LLNode 堆；不能把一切协议错误都称为该归纳的合法反例。反过来，换成派生 MAPFPlanner 的虚方法、引入搜索诊断、重入初始化改变选择、复制 Agent 或放开外部写权限，都会退出本件已证域；不是 AA 自带能力。

**入口合同必须可检查：** worker 只拥有固定具体 MAPFPlanner，无未登记虚覆盖；单次初始化后固定 LACAM 选择/agent 身份/拓扑；只允许具名 loadPaths→plan→PRE_COMMIT_SHAPE→planner_commit 调用包及 E6 生命周期。拒绝向策略/监管暴露 runPP、LNS::run、LNS2、findPath、getTravelTime 等搜索接口；输出/计数采集不得借这些函数算“诊断”。模式/身份/输入检查若运行即在原服务内付费，不能以这份纸面符号表冒称已有编译隔离或万能运行时验证器。

因此，源码层的四堆具体排除已从宽泛 UNKNOWN 收窄到有函数体支持的条件命题；未来完整 worker 的实际调用封闭、所有未读可达叶的输入/生命周期前提及实际库绑定仍不能写作实测通过。没有必要因这个局部结论再扫描所有无入口翻译单元，也没有理由以它停止其它具名源资格工作。

## 5. 当前纯来源仍未闭的具体见证

**首次搜索迭代之前截止。** planner.cpp L130–145 已分配 A、H_init、OPEN、EXPLORED，H_goal/curr_best 均空；L148 的 while 在进入正文前检查 deadline。若此时已到截止，curr_best 从未获值，L240–243 仍把空值赋给 H_goal，L245 先访问 H_goal->num_agent_reached，L248 才检查非空。该控制流在源条件成立时有明确空指针读取问题，不需要先让任意 LLNode 堆非空；本轮没有运行或声称哪一个实例实际经历它。

deadline 在 runLACAM2 内建立后才进入 solve 的结构建立；本次不重定其时间域。既有预算声明及 PROCESS_SLICE 不能自动证明建结构后仍有余量，也不能给预算补默认值/下限或不收费预跑来排除该分支。源内发生非法访问后，外层 PRE_COMMIT_SHAPE 已经太晚；“plan 为 void 但返回了”同样不是保护。

另一个精确保留项是**目标索引覆盖**：已读 HNode 构造 L59–68 会按 reached-goal 索引访问后继目标，funcPIBT L411 和 swap 检查 L509–512 也访问带内部目标索引的冻结目标队列。仅证明 goal_locations 的队首非空不覆盖这些访问。域合同必须依据真实已交付目标序列及所有可达索引证明覆盖，不能复制一个目标、读未来任务或修改参数来补齐。E11 的输出形状检查在求解之后，不是这些提前访问的充分守卫。本件不宣称已找到合法输入触发实际越界，不递归所有目标/图叶函数来拼一份全源通过报告。

实际内存所有权/持久计数/可表示整数、输入矩阵形状、全部 LaCAM 访问域、第五堆最短距离正确性及服务/时钟/ABI 仍按原资格逐项处理。它们是具体领域义务，不能把“对象有效”作为未经证明却自动满足的万能假设。若其中不能闭，当前 profile 不具实验资格；四个随机谓词换成稳定排序也不会修复这些问题。

## 6. 唯一选择的最小来源修订合同

采用候选名称 **R0-REPAIRED-LACAM-AA-GUARDED**，保留固定 R0 原样档案，并单独登记差异。此名字是下一工作路线，不是新算法已经实现、固定或通过。相对 E6/E11/E12，唯一新增内部源码改动位于 planner.cpp 的 H_goal 读取/回溯分流；四种 LLNode 堆及两个谓词不改。其余具体约束如下。

| 位置/责任 | 唯一处理 | 身份与费用 |
|---|---|---|
| 原 driver/未赋 init_time_limit/detach | 沿 E6：不进入；隔离 worker 同步初始化，必填预算显式传递，真实停止回收 | 仍是修改版内核适配，非 native 全程序 |
| Instance::computeAllPair 第五堆 | 保留 E6 已拟定严格 value 关系修复及原算法主体 | 独立源码差异，所有引用此 profile 的臂共同应用；预处理全费 |
| 四 LLNode 堆 | 保留原比较器、Agent 与 solver 对象，按 §4 的入口/空状态域使用 | 不人为消耗随机数，不删除空对象来降低对照成本；不扩到 SIPP/LNS 搜索域 |
| Planner::solve 空 H_goal | 在首次解引用之前分流；仅非空目标进入现有目标日志/回溯，空目标不补路线，继续到原内存清理及空 solution 返回 | 新增守卫/分支和实际分配/清理均收费；不把提前 return 省去清理当最小修补，不承诺时序或结果与原字节程序完全等价 |
| loadPaths/plan/commit 输入与形状 | 保留原主体和顺序；源前输入资格覆盖实际可达目标/位置索引，E11 PRE_COMMIT_SHAPE 仍早于 planner_commit 的清容器/切分 | 缺已交付输入的事前拒绝不改源状态；进入事务后不可证明域则会话停止。未闭来源前提阻止资格，不临时补 WAIT/任务 |
| 正常外部软拒收 | 原 AA 完整完成节点保留；中心终态交回后才取下一合法输入 | 不回滚，不自动重启；源内 initial_success 与外部接受标志不同 |
| 此次空 solution | 原 runLACAM2 识别空解返回失败，本次外层形状拒绝即进入 NO_PROPOSAL_SHAPE / FAIL_STOP_SOURCE | 不进入危险 commit，不再给一次 clearAll 重试；已有物理责任、完整 roster 和全部费用保留 |

空目标处理只调整首次解引用的支配关系及空目标失败路径，不换搜索、重播 RNG、延长截止或提前产生动作。若 while 未进入且前置结构建立有定义，原 A 和 EXPLORED 中 H_init 已实际分配，后续原清理仍必须发生；若构造/清理本身异常，沿 E6 真正退出回收而非谎称清理成功。本件不证明其它循环退出或全部 EXPLORED 所有权已经闭合。

尤其注意：后继 fixInitialSolutionWithLaCAM 的 false 不会被 MAPFPlanner::plan 回写 initial_success。故“空解使标志变假→下一次 clearAll 再试”不是一个覆盖各分支的源事实，更不是 E12 授权的失败制度。本方案在本次事务边界就终止不合格会话。合法非空完整输出可携带原内部布尔历史；若无全继续域证明仍不得热用，不能按计划表现选择性保留。

事前尚未固定 profile/绑定/域时保持资格未获准，不造一条实验 FAIL_STOP 记录。未来合法守卫失败沿声明式失败制度保留真实 Q；实际源定义域/身份已失效则另标 SOURCE_INVALID/INFERENCE_UNAVAILABLE，不能把 UB 或缺失证据折算成有利于某臂的合法零分。

**公平费用及主张：** D-S/R-S/D-F/R-F/E0，以及实际引用该共同来源 profile 的其它适配臂，均用同一差异、守卫、AA、单槽屏障和失败语义。Agent/空堆建立、验证临时 A* 建立/销毁、预处理、输入复制、clear/load/check、solve、守卫、commit、中心拒收、保留内存及停止尾部全部入各自真实成本。一个臂合法调用次数更多可以有更多成本；不能给对照虚构等次数，也不能只计接受 job。取消根本未发生的 Compare 无需收费，但空对象成本仍发生；研究者审源码的费用不是实验服务工作量。不同独立来源只记它们的真实工作，不虚构拥有 R0 空堆。

共同源码修复及 AA 改变可以影响所有臂的时序、失败概率和闭环 Q，不能归给 D 的查询贡献。本件不增加确认性对照或数据请求，不因来源修复困难降低 R/E0 或已发表外部比较。若这条明确路线最终仍不能取得来源域与服务资格，应在来源选择层另立有身份的替代稿；当前没有证据允许宣称某个未取得的新仓库/版本已经可替换。现在可停止重复追查这四个谓词，转向上述具名剩余源接口。

## 7. C13 真正终态、原文与独立取舍

新 C13 一次调用：原 exec **7933**，首 chunk 1fad5c；最后 chunk **8e8505 / exit 0**；实际 **claude-opus-5**，success/completed/end_turn，完整 END-C13；duration 173436 ms，API 173368 ms，USD 0.32760375，无 permission_denials、无工具请求、无重试、无活句柄。请求 opus/high、480s、budget 5、安全无工具/skill 配置与每次短观察见完整回执。

| 工件 | SHA256 | bytes / LF |
|---|---|---|
| 73C13_R0_COMPARATOR_DOMAIN_CONSTRUCTION_PROMPT_20260910.md | 320f5d0d4cf3c45a8fe789e581a1e01d99ce3a9290fbef4dc725279381b2377b | 9506 / 31 |
| 73C13_R0_COMPARATOR_DOMAIN_RAW_RESPONSE_20260910.json | 734f3853a4e59da8e2ddeebbbef32e72aea90d1021925d228eca8c6d1bce64fc | 12759 / 1 |
| 73C13_R0_COMPARATOR_DOMAIN_COMPLETE_RECEIPT_20260910.md | d92c31e89a9f5271459a317f10d41a03d7f265625216d2e1041021ef2f4045bc | 19190 / 108 |

[完整 C13 及不用 skill 的逐条分析](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73C13_R0_COMPARATOR_DOMAIN_COMPLETE_RECEIPT_20260910.md) 原样保留全部 result；抽取正文与 JSON result 实际逐字相等，result SHA256 6ef6e86121b61df68111399a6b2650100d9dd93a7b909303c5c5447743eb7c7f，11531 UTF-8 bytes / 62 LF。主要取舍：采用条件空堆归纳与保四谓词；拒绝全仓唯一调用者/逻辑最弱条件的夸大；拒绝实际 UB 必须三条件的未经支持断言；限定“算法身份不变”只到未改谓词原字节，整适配明确修改版；修正研究审计与实验费用混淆；空解分流保留清理；拒绝自动 clearAll 再试；区分未获资格、合法守卫失败与源/协议失效；不把四谓词没有 RNG 消费扩写为全源随机历史为零。不是模型同意就改门票。

## 8. 真实失败记录与未运行合同

本次一次 GitHub fetch_file 初始参数误用 repository 而非 repository_full_name，被 schema 拒绝；随后以正确参数取得固定对象。Agent.h、LLNode.h 两个错误假定路径及两个错误 LaCAM2 路径各返回真实 404；按实际 BasicLNS/SingleAgentSolver/CMake include 路径取得上表文件，没有扫仓库目录或读载荷。一条把全部源码作为散列参数的只读命令在进程创建前因 argument list too long 失败，随后对同一批已取得对象分小组散列，全部 blob 匹配；未执行这些源。一次 C13 JSON 保存的 functions 模板字符串语法失败在工具执行前，无文件/CLI 副作用，随后完整保存。所有失败都不算正证据或 Claude 重试。

本件只新增 E18 主报告及 C13 提示、JSON、完整回执，共四件；没有修改 73、行政页、Git、桌面、完成旧报告或源代码；没有读取 35–38、Q-CAL/Q-CONFIRM 或任何公开/受限 map/scen/config/agent/task/delay/result 载荷。没有 skill、构建、测试、实现、伪代码、仿真、调参、运行来源程序或实验载荷/结果，保护参数原义且未给数值、范围或默认值。本报告源码中原有字段/条件的说明属于原文身份与静态域分析，不是赋值建议。下一步仍需根独立验收建设结论，以及待资格闭合后按约定顺序进入正式科研导师、Nature reviewer、完全无 skill 独立逻辑审查及根验收；当前 HOLD 不变。
