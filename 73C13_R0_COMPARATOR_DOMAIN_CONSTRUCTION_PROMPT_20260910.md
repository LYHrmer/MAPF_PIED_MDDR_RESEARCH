# 73C13：固定 R0 四个 LLNode 堆、AA 继续域与最小来源修订窄题

这是一次新的 NO-SKILL / CONSTRUCTIVE / NONBALLOT 建设题，不是正式评审、盲审或资格票。禁止使用任何工具、skill、外部搜索、代码执行、伪代码、实现、实验或参数赋值；仅依据以下已亲核证据分析。不要假定源码曾实际运行，不将条件可达、确实比较、关系不合格和实际 UB 混成同一结论。不重做 QEMU、服务模型或外部基线。请用中文给出完整独立分析，末尾写 END-C13。

固定唯一 R0：YueZhang-studyuse/LMAPF-delay，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。以下源正文全部由本子代理按该 commit 取得，Git blob 已独立重算匹配；不是仓库默认分支。未构建或运行。当前所有资格仍 HOLD。

身份：src/MAPFPlanner.cpp blob94afb42df1a70f5e312a382e61cf83576fd7360e，SHA256 c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1；src/MAPF-LNS2/src/LNS.cpp blob1fb0e54f8f2bb00af05de53233ae600774e36f2a，SHA256 0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2；inc/MAPF-LNS2/inc/SingleAgentSolver.h blobc22f59ac763c3bc272a82b5c8e9793a91f5da94a，SHA256 daafdc674f90bbe4b34031b19f2564fb93189f07d7ad15e0927e1574cbb5611f；src/MAPF-LNS2/src/lacam2/planner.cpp blob4f46f988d2c16f09c5a6f65bb9cd70e8e01aa483，SHA256 8d2fa9131f0691b109a00dd6267b3b48f80df7778643daeb806ff82e20fe2789。源 URL 统一为 https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/ 后接上述路径。

第一组已读证据：SingleAgentSolver.h 完整 LLNode 定义中只有两个有效比较器类型，分别绑定 SIPP OPEN/FOCAL 和 SpaceTimeAStar OPEN/FOCAL，共四种堆成员。OPEN 顺序键依次为 reached_goal_at、g_val+h_val、h_val；FOCAL 先 num_of_conflicts，再上述键。前键相等才进入后键；全部相等时 operator() 当场调用 rand()%2。不能把非平局的 >= 单独当自比较发生，因为那些分支具有前面的不等条件；全部相同落随机分支。比较器自身无自定义构造/析构。

第二组：BasicLNS.h 完整 Agent 的字段是 id、SingleAgentSolver* path_planner 和 Path，构造根据 sipp 选择 new SIPP 或 new SpaceTimeAStar，析构 delete path_planner。SingleAgentSolver 虚析构 default；构造只绑定 Instance 引用，不调用被注释的 compute_heuristics。SIPP.h 与 SpaceTimeAStar.h 两个完整 solver 构造都只有基类构造、空函数体，无自定义 solver 析构，堆成员无范围构造。LNS.cpp L7–53 构造先 reserve 全体 agent 数，再 emplace 同数对象；当前 MAPFPlanner::initialize 使用 SIPP 构造选择。BasicLNS.cpp 完整构造只存引用及标量，没有搜索。对象有效、固定 agent 数、未复制 Agent、未外部写入或破坏是需要说明的条件，不能用类型名自动证明整个程序安全。

第三组：MAPFPlanner.cpp 全文。initialize 顺序 initMap、computeAllPair、new LNS，再分配提交/未来容器并映射 algo。适配合同要求在初始化映射前显式选择纯 LACAM，期间不改模式；不依赖 MAPFPlanner.h 的另一个默认 algo。纯分支 plan：首次 prepareDummy→getInitialSolution；initial_success 为假时 clearAll→getInitialSolution；否则 fixInitialSolutionWithLaCAM。plan 为 void，后者 bool 未外传。其他模式可进入 LNS::run 或 fixInitialSolutionWithLNS2，但不属于该纯分支。LNS.h 的 setIterations/setRuntimeLimit 只赋标量，init_lns 在声明处空指针。

第四组：LNS.cpp 已逐行读完整以下函数。getInitialSolution L523–542 只整理 neighbor.agents/统计并调 runLACAM2，绝无 runPP fallback。fixInitialSolutionWithLaCAM L496–520 在 neighbor 非空或 initial_collision 时 clearAll→getInitialSolution，否则直接返回 true。runLACAM2 L648–714 以本次冻结 env 建立独立 LACAMInstance、本次局部 mt19937、Deadline，调用 LaCAM solve，空 solution 返回 false；非空时把 solution 写回 agents.path 和 path_table。局部 MT 按源码每调用重新构造，不能称 AA 必然让该 MT 跨调用连续。

第五组：正常后继 loadPaths 在 initial_success 且非 initial_run 时依次 clearAll、loadPaths(vector<Path>)、checkReplan。clearAll L1360–1430 清 path table 和 agent.path，按当前 env 写求解器起终点、other_goal_locations、commit_window，清 neighbor/统计；没有 findPath、getTravelTime、OPEN/FOCAL、堆移动或替换。vector<Path> loadPaths L1186–1216 只复制和按原规则延长路径，空路径跳过；checkReplan L383–443 只判断路径起点/目标/碰撞、清部分路径并维护路径表。PathTable::insertPath 的空路径早返回已有 E11 确证，不把它重复说成 UB。

第六组：planner_commit 先清两输出容器，再 commitPath，再 validateCommitSolution，后者失败退出。commitPath L1236–1339 不搜索，不操作堆，但空/单点原路径会使已清空提交容器 back 不合法，故共同外层 PRE_COMMIT_SHAPE 必须先于此调用。validateCommitSolution L1433–1483 先 reserve，再为全体临时构造 sipp=false 的 Agent；只复制提交路径及检查几何/冲突，没有调用 solver 的搜索或堆方法，临时对象会正常析构。不能遗漏这两个临时 A* 堆。

第七组：独立 LaCAM 的 lacam2.hpp/.cpp、planner.hpp/.cpp 已全文读。入口只接受 const Instance&、LACAMInstance、时钟/MT及参数，没有 LNS/Agent/SingleAgentSolver 句柄或回调。Planner 有自己的 LACAMAgent、LNode、HNode、占用数组、tie_breakers；OPEN 是 std::stack<HNode*>。完整 planner.cpp 没有 LLNode/SIPP/SpaceTimeAStar/path_planner 的引用或调用；Instance.h 无到 LNS/Agent/solver 的反向指针。其 funcPIBT 在 std::sort 之前采样 tie_breakers，sort 谓词只读取固定已采样分数，递归发生在本次 sort 返回之后。这与 LLNode 谓词内现抽 rand 不同，不据此认证 LaCAM 所有索引或排序域。

第八组：已读 LNS::runPP L544–644 确实调 path_planner->findPath(ConstraintTable,timeout,timeout_flag)。SIPP.cpp 完整该 timed findPath L30–182 经 pushNodeToFocal，把起点及条件后继放 FOCAL；pushNodeToFocal L530–536 只放 FOCAL。其 pushNodeToOpenAndFocal L521–529 才操作两堆。A* 完整一参 findPath L23–189 也是 FOCAL；另有 pushNode/getTravelTime 相关堆操作。不要仅因函数被编译、虚表存在或容器类型已实例化便称四种 Compare 都被调用；也不能由 timed SIPP 有 FOCAL 推 OPEN 同时活动。

库层继承 E6/E7 已核的参考 Boost 1.74：默认 pairing_heap 构造置空 root，不调用 Compare；empty 只看 root；析构 while 非空 pop，始终空不进 Compare。非空销毁可经 merge 调 Compare。现主机 header 身份已有，未来实际 include/ABI/构建绑定仍未取得，不把最低版本当实绑，也不称所有析构无比较。

当前 AA/FAIL_STOP_SOURCE 规则：来源状态只在同一单 worker 中原地变化；完整合法事务结束后，无论中心接受或 STALE/版本变化等软拒收都保留源状态。中心终态付费交回且释放待结果槽后才可下一 job；下一 env/unexecuted_paths 必须来自权威已接纳历史 Π 与当前合法交付知识，拒收内部 future_paths 不得冒作已接纳。PRE_COMMIT_SHAPE 失败、内生非法输出、异常/损坏或无法证明继续域则会话停止，无自动重启/回滚。E6 已选同步初始化隔离入口，避开原 driver 未赋 init_time_limit/detach；第五个 computeAllPair 堆的 >= 改严格 > 是已登记拟修复。该第五堆不是四个 LLNode 堆。所有 D/R/E0 共用来源/适配/费用，不把共同修复归 D。

另一个不可忽略的亲见边：Planner::solve L130–145 建立 A/H_init/OPEN/EXPLORED，H_goal 与 curr_best 初始为空；L148 while 条件先看 !is_expired(deadline)，curr_best 仅在循环内写；若循环根本未进入，L240–245 把仍空 curr_best 给 H_goal，随后先输出 H_goal->num_agent_reached；L248 才做 H_goal 非空检查。这里未观测实际执行，只给精确分支。不要靠给预算设默认值/数值下限排除；源 deadline 可包含调用前建立结构的费用。即使证明四堆一直空，也须面对源内此类已知边，不能用 plan 正常返回或运行时万能验证器代替事前资格。

请集中回答四项：一、依据上述完整函数与接口，可否在允许 AA 正常软拒收的纯 LACAM 会话内建立四堆始终空的归纳；明确最弱必需条件和没有被证明的东西。如提出反例，必须给合法调用链，不能偷换到 LNS/PP 或使新输入未经资格进入。二、分析比较器关系不合格与该会话实际随机消费/风险的区别；能否因 AA 而突然使某堆可达，为什么。三、选一个具体最小的下一步来源合同：保留四谓词并给可审查调用域，或有必要的明确修订，解释算法身份、必要费用、失败后继；不要泛列库或声称修一个比较器即通过全源。四、对 deadline-before-first-iteration 边提出最小纸面处理，不能改成无费预跑或补路径；明确它与堆证明及全部继续域资格的关系。总长度适中，允许说有界证据不足但要指出准确缺口；不要扩大为全仓缺陷清单，不给实验保护参数数值/范围/default，不作资格票。
