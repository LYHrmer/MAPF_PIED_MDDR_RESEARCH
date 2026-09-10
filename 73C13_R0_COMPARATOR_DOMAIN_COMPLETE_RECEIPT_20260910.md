# 73C13：四堆调用域建设意见完整回执与子代理独立复算

日期：2026-09-10；NO-SKILL / CONSTRUCTIVE / NONBALLOT。独立题号 C13，由 /root/source73_r0_remaining_contract 执行；不是正式逻辑审查，不替旧失落任务或 C12，不投资格票。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 唯一调用及实际终态

提示在调用前已核目标不存在并用 apply_patch 创建：[73C13 prompt](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73C13_R0_COMPARATOR_DOMAIN_CONSTRUCTION_PROMPT_20260910.md)，SHA256 `320f5d0d4cf3c45a8fe789e581a1e01d99ce3a9290fbef4dc725279381b2377b`，9506 bytes / 31 LF。输入仅为固定 R0 已亲核的必要源证据、既有 AA 规则和窄问题；没有其它模型意见或 skill 内容。

实际 CLI 请求 opus / high，timeout 480s、max-budget-usd 5，并带 safe-mode、permission-mode dontAsk、tools 空、disable-slash-commands、strict-mcp-config 的空 mcpServers、no-session-persistence、output-format json。按既有沙箱网络失败依据使用正常 require_escalated 机制；没有绕过权限。初次 exec 首等 1000 ms，实际 session_id **7933**、chunk **1fad5c**，无 stdout；原句柄后续观察 chunk 414c89、6936b1、02e75b、8d577d 均无新 stdout；最后 **8e8505 / exit 0** 返回完整 JSON。各次观察均未超过 30s。没有 ps 同名进程代证，没有重试，没有第二次 Claude 启动；完成后没有活句柄。

| 终态字段 | 实际值 |
|---|---|
| type / subtype / terminal_reason / stop_reason | result / success / completed / end_turn |
| is_error / api_error_status / permission_denials | false / null / [] |
| 实际 modelUsage 键与 canonicalModel | claude-opus-5；请求别名为 opus |
| duration_ms / duration_api_ms / num_turns | 173436 / 173368 / 1 |
| total_cost_usd | 0.32760375 |
| input / cache creation / cache read / output tokens | 2 / 6791 / 0 / 11406 |
| server web search / fetch requests | 0 / 0 |
| CLI session_id | c3cdaa4d-cdec-4bf0-80de-5f57ca78b9b2 |
| uuid | 5ca26d03-c9c1-43f1-a8e5-015b2a90fc2d |

完整 stdout JSON 的字段及 result 保存在 [原回执 JSON](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73C13_R0_COMPARATOR_DOMAIN_RAW_RESPONSE_20260910.json)，未删除 usage/modelUsage 等元信息。文件 SHA256 `734f3853a4e59da8e2ddeebbbef32e72aea90d1021925d228eca8c6d1bce64fc`，12759 bytes / 1 LF。result 为 6098 Unicode 字符，UTF-8 11531 bytes / 62 LF，SHA256 `6ef6e86121b61df68111399a6b2650100d9dd93a7b909303c5c5447743eb7c7f`，末尾 END-C13 完整。下节原样嵌入 result；分析位于其后，不在原文里改错。

## 2. 完整 result 原文

<!-- BEGIN-C13-RESULT -->
# 73C13 分析（固定 R0 = 0b5b336，纯 LACAM 会话）

前置声明：以下全部是对已亲核源正文的静态可达性与关系性质分析。未构建、未运行，因此任何结论都是"源级调用域"命题，不是"实际执行未发生"的观测命题。所有资格保持 HOLD，本文不构成资格票。

## 一、四堆始终空的归纳：可建立，但只在明确条件的合取下

**不变式 I**：会话内任一存活的 `SingleAgentSolver` 派生对象（LNS 持有的固定 N 个 Agent 的 `path_planner`，**以及** `validateCommitSolution` 内为全体临时构造的 `sipp=false` Agent）的两个堆成员 root 均为空；因此四种 Compare 一次也不被调用。

**基础步**：`LNS` 构造 L7–53 先 reserve 全体 agent 数、再 emplace 同数对象；`Agent` 构造按 sipp 选 `new SIPP`/`new SpaceTimeAStar`；两个 solver 构造体为空、只走基类构造；`SingleAgentSolver` 构造只绑 Instance 引用，被注释的 `compute_heuristics` 未调用；堆成员无范围构造。按 E6/E7 已核的参考 Boost 1.74 语义，默认构造置空 root 且不调用 Compare。故构造后 I 成立。

**保持步**（纯分支逐函数）：
- `initialize`：initMap、computeAllPair、new LNS，再分配容器并在**显式选定纯 LACAM 之后**映射 algo（不依赖 MAPFPlanner.h 的另一个默认 algo）。
- `plan` 纯分支：`prepareDummy`→`getInitialSolution`（L523–542 只整理 neighbor.agents/统计并调 `runLACAM2`，无 runPP fallback）；失败则 `clearAll`→`getInitialSolution`；否则 `fixInitialSolutionWithLaCAM`（L496–520 要么 clearAll→getInitialSolution，要么直接 return true）。
- `runLACAM2` L648–714：以冻结 env 建独立 LACAMInstance、局部 mt19937、Deadline，调 LaCAM solve；空 solution 返回 false，非空写回 `agents.path` 与 path_table。写路径与路径表不是压堆。
- LaCAM 子系统：入口签名只含 `const Instance&`、LACAMInstance、时钟/MT 与参数，无 LNS/Agent/SingleAgentSolver 句柄或回调；Planner 自带 LACAMAgent/LNode/HNode/占用数组/tie_breakers，OPEN 是 `std::stack<HNode*>`；完整 planner.cpp 无 LLNode/SIPP/SpaceTimeAStar/path_planner 引用，Instance.h 无反向指针。故该子系统与四堆图上不连通。
- 正常后继：`clearAll` L1360–1430 只清表、写起终点/other_goal_locations/commit_window、清 neighbor 与统计，无 findPath/getTravelTime/堆动作；`loadPaths(vector<Path>)` L1186–1216 只复制与按原规则延长，空路径跳过；`checkReplan` L383–443 只判几何/碰撞并维护路径表。
- 提交：`commitPath` L1236–1339 不搜索不动堆；`validateCommitSolution` L1433–1483 reserve 后临时构造全体 `sipp=false` Agent，只复制提交路径并检查几何/冲突，**未调用任何 solver 搜索或堆方法**，临时对象正常析构（空 root 的析构 while 循环零次，不进 Compare）。

唯一能压堆的入口是 `findPath`/`pushNodeToOpenAndFocal`/`pushNodeToFocal`/`pushNode`/`getTravelTime`，其调用者只在 `runPP` L544–644、`LNS::run`、`fixInitialSolutionWithLNS2` 一侧；纯分支不经过它们，`init_lns` 在 LNS.h 声明处即空指针且纯分支不构造它。因此在纯分支内**无法给出合法反例**：任何反例都必须切换模式或让未经资格的新输入进入，二者都被本题禁止。

**最弱必需条件**（缺一则归纳断裂）：
1. 模式在 initialize 中于 algo 映射前显式定为纯 LACAM，且会话生命期内不变；
2. 会话可达调用集封闭于上面列举的那些函数，禁用 runPP / LNS::run / fixInitialSolutionWithLNS2 / init_lns 构造与全部 findPath·pushNode·getTravelTime；
3. 固定 agent 数、reserve 后 emplace 同数、无 Agent 复制/移动（避免 vector 扩容触发容器复制/移动这一未证明语义的路径）；
4. 对象有效、单 worker、无外部写入或破坏，走 E6 的同步初始化隔离入口（避开原 driver 未赋 init_time_limit/detach）；
5. AA 软拒收后的下一 job 仍从权威已接纳历史 Π 与合法交付知识取 env/unexecuted_paths，拒收的内部 future_paths 不冒作已接纳——由此下一 job 的调用链与本 job 同构，归纳可跨 job 延续。

**未被证明的**：实际 include/ABI/构建对 pairing_heap 的绑定（1.74 是参考版本，不是实绑；空对象析构不进 Compare、以及复制/移动语义都挂在这个缺口上）；调用图的封闭性只覆盖已亲读的函数，未读的、可持有 `path_planner` 的翻译单元不在覆盖内；关系合法性完全未被证明（实际是被证否，见二）；四堆为空**不等于**本会话不触及可疑堆——纯链的 initialize 确实经过 computeAllPair 的第五个堆，其 `>=`→严格 `>` 是已登记拟修复，且不属于这四个。

## 二、关系不合格 ≠ 实际随机消费/风险

三层必须分开：
- **关系不合格（静态）**：四个 Compare 在"前键全相等"分支现场调 `rand()%2`，故同一元素自比较可返回 true，两个各字段全等的不同元素可互相 true——严格弱序公理被破坏。这是类型的性质，与是否执行无关。非平局的 `>=` 分支受前置严格不等条件保护，不能单独算作自比较发生。
- **条件可达（中间）**：调用点存在、模板已实例化、虚表存在、容器类型已具化——这些都**不等于**被调用。同理，timed SIPP findPath 经 `pushNodeToFocal`（L530–536 只放 FOCAL）不能推出 OPEN 同时活动；只有 `pushNodeToOpenAndFocal` L521–529 才动两堆。
- **实际比较与实际 UB（最强）**：需要堆非空到发生 Compare、该次比较恰落全等分支、且库随后依赖被破坏的公理产生未定义行为。三者缺一都不是 UB。

若一的不变式成立，则本会话四堆的 Compare 调用数为零，因而**由这四个谓词引起的 rand() 消费为零**，不扰动任何其他 rand() 使用者的全局序列；会话层面的确定性/合法性讨论应改挂在第五堆（已登记修复）上，不要混算。LaCAM 侧 `funcPIBT` 在 `std::sort` 前采样 tie_breakers、谓词只读已采样的固定分数、递归发生在 sort 返回之后，与"谓词内现抽"结构不同；但据此不认证 LaCAM 其他索引或排序域。`runLACAM2` 的局部 mt19937 按源码每次调用重构，不能说 AA 让它跨调用连续。

**AA 能否突然使某堆可达**：不能，仅凭软拒收不能。AA 规则改变的是**输入**（env、unexecuted_paths）与事务/槽位状态，不改变 initialize 一次性写定的模式，不构造 init_lns，不新增调用边。输入变化只影响纯分支内部走哪一支（initial_success 真假、neighbor 空否、fixInitialSolutionWithLaCAM 直接 return），而这些支路已逐一读过且均无堆动作，故输入变化跨不过边界。真正会使堆可达的是：重入 initialize 而丢掉显式纯选择（退回 MAPFPlanner.h 的另一默认 algo）、进入 LNS::run/fixInitialSolutionWithLNS2/runPP、构造并使用 init_lns、或让未经资格的输入入场——这四件都不是软拒收所授权的。AA 输入变化真正抬高的是**别的**风险：空/单点原路径使已清空提交容器 `back` 不合法（故 PRE_COMMIT_SHAPE 必须先于 commitPath），以及第四项的 deadline 边。

## 三、最小下一步来源合同：保谓词 + 可审查调用域

推荐**不改四个谓词**，只交付一条域合同（记 `LLNODE_HEAP_EMPTY_DOMAIN`）。理由：四谓词在已资格化的纯链上不可达；改写它们会改变 SIPP/A* 的平局展开顺序，即改变算法身份，连带需要对 LNS/PP 域重做基线，而那些域根本不在本题范围。

合同内容（最小）：
- **范围**：恰为绑定 SIPP/SpaceTimeAStar OPEN/FOCAL 的四个堆成员；四个 Compare 函数体逐字节不动。
- **义务**：(a) 纯 LACAM 在 algo 映射前显式选定且会话内不可变；(b) 会话可达调用集按一中的列举**封闭**，并附可检查的禁用符号清单（findPath / pushNodeToOpenAndFocal / pushNodeToFocal / pushNode / getTravelTime / runPP / LNS::run / fixInitialSolutionWithLNS2 / init_lns 构造）；(c) 固定 agent 数、reserve-then-emplace、无 Agent 复制/移动、单 worker、E6 同步初始化入口；(d) 不变式显式覆盖 `validateCommitSolution` 的临时 Agent 那两个额外堆。
- **算法身份**：不变——这是域限制而非代码编辑，同输入下纯 LACAM 输出与所读源一致（第五堆与 rand() 序列的说明另计）。
- **必要费用**：一次性源级审计（大部分已付：相关函数已全文读毕）；余额是取得实际构建/include 对 pairing_heap 的绑定以闭合版本缺口，并把封闭调用集登记为可审查条款。无运行时验证器、无实验。
- **失败后继**：任一审计项不成立（实绑 heap 头在空析构或复制/移动上与参考语义不同；纯链中发现 findPath 的可达调用者；模式不可变性无法证明），则该域条款失败，按 FAIL_STOP_SOURCE 会话停止，无自动重启/回滚；替代不是"改一个比较器"，而是缩小域重新申报，或另立带完整 SIPP/A* 重基线的四谓词修订。
- **界限**：本合同不修 computeAllPair 第五堆（独立已登记修复，D/R/E0 共用来源/适配/费用，不归 D）；修好一个比较器也不使全源通过。

## 四、deadline-before-first-iteration 边的最小纸面处理

亲见分支：`Planner::solve` L130–145 建 A/H_init/OPEN/EXPLORED，`H_goal` 与 `curr_best` 初始为空；L148 while 先测 `!is_expired(deadline)`；`curr_best` 仅在循环内写；若循环一次未进，L240–245 把仍空的 `curr_best` 交给 `H_goal`，随后**先**输出 `H_goal->num_agent_reached`，L248 才做非空检查——解引用支配于检查之前。不能用给预算设默认值/数值下限来排除，源 deadline 可含调用前建结构的费用。

**最小处理**：只做支配关系的顺序修订——把源内**已存在的** L248 非空检查上提到首次解引用之前，为空时返回与既有"空 solution"路径相同的返回值。性质：(i) 算法身份不变，任何至少进入一次循环的执行行为完全不变，唯一被改的是原本未定义的那一支，且被映射到源内已有契约（`runLACAM2` 对空 solution 已 return false）；(ii) 费用最小，无预跑、无补路径、无新预算或默认值；(iii) 失败后继已在源内闭合：空 solution → `getInitialSolution` 失败 → 纯分支 `initial_success` 为假 → clearAll→getInitialSolution，若再失败由会话级 PRE_COMMIT_SHAPE / FAIL_STOP_SOURCE 接管；须同时确认无调用者把空当成功（已读部分支持这一点）。

**与堆证明及继续域的关系**：正交且**不可互相替代**。四堆空的归纳无论此边如何都成立，但此边就在纯链上（runLACAM2→LaCAM solve），故会话继续域资格是合取式：四堆空 ∧ 第五堆修复 ∧ PRE_COMMIT_SHAPE 先于 commitPath ∧ 本边处理。任一不成立即会话停止；`plan` 返回 void、看似正常返回，或任何运行时万能验证器，都不能替代事前资格。

**准确缺口**（有界证据不足）：实际构建对 pairing_heap 的版本/ABI 绑定未取；调用图封闭性仅覆盖已读函数；本文未认证 LaCAM 除上述结构点外的索引与排序域。

END-C13
<!-- END-C13-RESULT -->

## 3. 子代理不用任何 skill 的独立分析

1. **条件空堆归纳可采用，措辞须降到已证范围。** 构造、pure plan 两类后继、load/clear/check 与临时验证 A* 分别保持空堆；软拒收不自动建立新的搜索调用。条件包含实际对象/输入仍有定义、固定具体 MAPFPlanner 动态类型、固定选择及 agent 集、唯一 owner、不复制 Agent、不引入搜索诊断调用、实际库绑定相容。不是从“无反例”推全仓不可达，也不声称这份合取是逻辑上最弱条件；例如外部路径来源正确是整个协议必要前提，但一条来源错误却仍有定义的路径也可能完全不触堆，故不能说缺一必然触发比较。
2. **不采纳“唯一所有压堆调用者”的全仓断言。** 本轮确证具名纯调用链未触这些入口，另亲读 runPP→timed SIPP FOCAL 及两个 getTravelTime→OPEN 的完整函数。未穷尽全仓所有调用者；编译了别的翻译单元不等于它们可由受限入口执行，反过来也不以负文本检索替代封闭入口合同。C13 关于未读持有 path_planner 的单元的保留项需要这个限定。
3. **不采纳其实际 UB 三条件必要论。** 随机谓词不能保证稳定严格弱序，这是关系缺陷；本域不调用它们是单独的可达性命题。尚无可无条件套用的具体 Boost 条款支持“必须实际落全等分支且库随后产生错误才算 UB”或“三者缺一都不是 UB”。其它源操作也可能独立失去定义。仅报告没有运行、没有实际比较/UB 观测，不把缺少观测当成无 UB 证明。
4. **保四谓词合理，但不接受整个算法身份不变的外推。** 不改四谓词使其原字节身份保持；第五堆修复、隔离入口、AA、形状守卫和新增空目标守卫依然共同构成修改版来源。即使新守卫在某非空目标路径上不改变抽象返回解，也有实际分支、费用及后继时序，不承诺同墙钟截止下逐指令/逐结果等价。“不影响当前分支”不能等同 native 全程序等价。
5. **其费用表不构成实验费用闭合。** 阅读与研究审计属于证据准备，不能代替初始化预处理、Agent/两堆构造、临时 A* 构造/析构、路径输入复制、守卫读取、失败记录、内存保留、停止/退出等各臂真实工作。实际未进入 Compare 不虚收比较/随机数费用；实际存在的空对象构造不删除。D/R/E0 同规则按真实调用数计费，不要求伪造相同工作量。
6. **空 H_goal 修订方向可采用，须保留清理并明示源码差异。** 在原首次 H_goal 解引用之前作非空资格分流；空目标不打印解引用、不回溯、不补路径，沿本次已构造对象的原清理路径完成空 solution 返回。不能把“返回空”写成跳过清理的早退。首次循环未进入时，已插入的 H_init 和 A 仍有真实分配/清理费用。此修改不认证其它出口、所有权或中断展开。
7. **拒绝“先 clearAll 再试，若再失败才交会话守卫”。** E12 已规定本次 NO_PROPOSAL_SHAPE/不具继续域即会话停止，不授权在空解后自动再给一次源尝试。后继 fixInitialSolutionWithLaCAM 的 false 在 MAPFPlanner::plan 内并不会回写 initial_success；C13 的统一失败链也与这个源事实不符。所选适配路线是本次 plan 返回后形状检查即停止空解会话，绝不进入危险 commit 或下一 clearAll 重试；合法非空完整事务的布尔历史另按原样保持。
8. **事前资格失败与运行终态必须区分。** 尚未绑定库、入口闭包未建立时不得开始实验；不能虚构一个已启动会话的合法 FAIL_STOP 结果。未来实际证实源/协议失效应列 SOURCE_INVALID/INFERENCE_UNAVAILABLE 等原责任，不能一律洗成合法算法失败。只有经资格的具体守卫失败才沿已登记会话停止并保留真实世界评分与完整 roster。
9. **四堆不发生 rand 仅是零贡献，不是整个源无随机历史。** 局部 MT 每调用重建，预采样 tie 与现抽 rand 分别处理；AA 仍可通过布尔标志、输入、缓存/分配/计数和所有实际随机/时钟历史改变未来。不能据本件把全源随机消费归零，或把会话确定性问题只归第五堆。

主报告 E18 据这些独立修正给出唯一纸面来源路线和明确未闭资格，不以 C13 为确认性评审。本文仅保存完整结果及复算；未实现、构建、运行源、测试、仿真、调参或生成载荷/结果，没有修改 73、行政页、Git、桌面或旧完成报告。

保存阶段一次 functions JavaScript 模板字符串因原文反引号而语法失败，发生于工具执行之前，未落盘、未启动或重启 CLI；随后按原 JSON 字段完整保存，原 result 未改。该保存错误不是 Claude 失败或重试。保持全部冻结/禁读/保护参数边界，HOLD。

