# 73E5：固定 R0 的 LaCAM 可达依赖、入口缺口与条件库生命周期合同

日期：2026-09-08。任务 /root/source73_r0_remaining_contract。**NONBALLOT / NO-SKILL；有界静态来源补证，不是正式审稿，不替失落 69E1 或 73E2。** 本回执不修改候选、源码或行政记录，不改变六门有效裁决；HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 可直接采用的结论

1. 四个 LLNode 随机堆的“实际绑定版本”仍没有证据。固定 R0 根 CMake 只提出 Boost 的最低／兼容版本要求，没有 EXACT；本次未取得任何实际构建缓存、编译所用头文件指纹或作者运行环境锁。所补 Boost 1.85.0 是继承 72E5 已登记的**条件版本**，不是实际部署版本，更不是本任务选定的软件配置。
2. LNS.cpp 全对象标识符检查把 init_lns 唯一有效显式赋值定位到 fixInitialSolutionWithLNS2。loadPaths、commitPath、clearAll 不赋或删除它；其声明初始化与唯一显式删除分别在 LNS.h。可以关闭“clearAll 是否偷偷建立 InitLNS”的具体疑问，不能由此确认全程序生命周期正常。
3. 在取得的 Boost 1.85.0 源中，四堆的零实参构造只建立比较器／基类并置空 root；**析构是 while 非空则 pop，不是调用 clear**。从构造后始终未取得节点的堆，析构体不会进入 pop／Compare；非空堆销毁则有条件进入 merge→Compare。这个条件结论不能替代实际绑定证据，不能写成所有析构无比较。
4. 沿真实初始化边另有**第五个局部 pairing_heap**：Instance::computeAllPair 的比较器返回 n1.value >= n2.value，数学自比较返回 true，不能保证严格弱序。它在 MAPFPlanner::initialize 中先于 LNS 构造调用，故官方 LACAM-only 选路不能豁免它。它不是 LLNode 随机比较器，不把确定的 >= 改写成 rand 问题，也不由此声称实际 Boost 运行已发生 UB。
5. 官方 driver 的三个带实参系统构造均未给 BaseSystem::init_time_limit 初值；已取得完整 header／system source／driver 内该成员只有声明和首次 plan 的读取，没有赋值。该 int 按值实参的求值在进入 MAPFPlanner::plan 之前已经需要读取成员；函数体之后覆盖 runtime limit 不豁免它。**在本回执核定的构造及调用链正常到达首次调用的前提内，缺失初始化是确定的源码问题；具体进程是否曾到达、运行后果及整个程序 UB 状态没有观测。**
6. 初始化等待超时后 detach、返回 false；initialize 的 false 分支只返回到 simulate，后者没有成功检查，仍可继续调用规划。log_fatal 的源码只是日志记录，没有显式退出。该继续边以日志及前置调用正常返回为条件；线程／异常／退出合同仍不完整。
7. 因而，不能以“再闭合四个空 LLNode 堆即可认证原生 R0”为下一步计划。当前有实际入口及额外预处理堆的阻碍，需要显式区分保真来源记录、带差异登记的修正版比较器／入口适配、以及独立已发表外部比较路线。

## 2. 本次亲见、继承证据与读取边界

先完整读取指定新交接、73E1、73E3、73E4，以及按具名引用定位的 72E5。E3/E4 首次合并显示被工具总输出裁剪，随后各自完整重新显示，没有用截断结果冒充全文。各文件实际 SHA256：

| 本地导航对象 | 本次实际 SHA256 |
|---|---|
| HANDOFF_NEW_CODEX_PREEXPERIMENT_DESIGN_20260908_CANDIDATE73.md | 915e8146c0f19f5a5ea30ca6d5d443c9bee5f68456d92fa1c24babb63d7e6f04 |
| 73E1_R0_PURE_LACAM_ENTRY_DOMAIN_BOUNDED_SOURCE_NONBALLOT_RECEIPT_20260907.md | 818c485355dafafe436b5f17235d2b18549974fdc303b58a0e6129ba5fb3fd2f |
| 73E3_LACAM_REMAINING_CONSTRUCTOR_SCOPE_NONBALLOT_RECEIPT_20260908.md | 98b837a30421bf382128848b97616fd0c9848c8ff2bf77b6c8b58692740ee37c |
| 73E4_LACAM_AGENT_AND_SOLVER_LEAF_LIFECYCLE_SOURCE_RECEIPT_20260908.md | 205dfcfaac3d09df60b0a6ba21a1e0e84c6fa539ec9abdb3ce4280268344c5a7 |
| 72E5_R0_BOOST_COMPARE_CONTRACT_BOUNDED_NONBALLOT_RECEIPT_20260907.md | b8875d3bfa6c86fd2a255cc6c74de8cd93ca7e04851801488c9d00ded67e3b74 |

继承而非本次重取：73E3 的枚举及 SpaceTimeAStar 声明、73E4 的 Agent／SingleAgentSolver／SIPP 声明和无自定义求解器析构链、72E5 的官方 Compare 文档与数学接口分析。下面二十个新取得对象另有本次完整字节指纹；“新取得”不表示此前其他报告没读过。它们全从官方 GitHub fetch_file 获得，R0 固定完整 commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357；Boost 仅固定已登记官方 boost-1.85.0 标签及本次返回 blob／正文指纹。

本次没有下载仓库、列远端目录、读其他 ref 或本机 Boost／构建缓存；本地只作目标精确存在性检查、具名 72E5 文件定位、上述文档读取与摘要核验。目标 73E5 在创建前不存在。所有源码仅在工具内存及只读散列命令的参数数据中，不保存源码文件，不执行源码。

## 3. 先核库版本：实际绑定没有闭合

固定 [CMakeLists.txt](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/CMakeLists.txt#L30) L33 请求 Boost 1.49.0 及具名组件，L35 使用 Boost_INCLUDE_DIRS，L67–72 的非 Python 分支收集 MAPF-LNS2／LaCAM2 源并链接 Boost_LIBRARIES。源码没有 EXACT。最低／兼容版本与精确版本的区别继承 72E5 已核 CMake 官方说明；本次不重搜所有库，也不把系统碰巧安装的版本当作 R0 所用版本。

“实际绑定 UNKNOWN”限定于现有证据，**不是宣称整仓任何地方都不存在版本记录**。本次没有展开全仓依赖锁检索，也没有作者运行元信息。即使未来选择某个版本完成可重复适配，也必须明示那是后来登记的环境，不能倒填作者原实验或本次 R0 的实际库身份。

本次 Boost 三个返回 blob 均与独立重算匹配，且与 72E5 正文指纹一致；增强的是“本次确实取得同一版本化内容”的身份，不是实际链接证明。标签所指仓库 commit 本次仍未解析，内容身份由返回 blob 与 SHA256 固定。

## 4. init_lns 的全部具名状态边

以下仅对本次完整 LNS.h、LNS.cpp 的所有 init_lns 标识符与相关方法有效语句作穷尽检查，不冒称全仓搜索或排除内存破坏。

| 状态／操作 | 亲见位置 | 具体含义 |
|---|---|---|
| 默认声明 | LNS.h L78 | private InitLNS 指针在声明处初始化为 nullptr |
| 构造 | LNS.cpp L7–53 | 构造初始化列表／函数体没有改写该指针 |
| 唯一有效显式赋值 | LNS.cpp L467–468 | fixInitialSolutionWithLNS2 的修复分支 new InitLNS 后写指针；此前同分支可先 runPP |
| 非空对象操作 | LNS.cpp L469–479 | 写 commit，run，取 timeout_flag；重建 path table；调用 clear，读取成本；clear 是成员调用，不是 delete，也没有把指针置空 |
| 报告访问 | LNS.cpp L1019–1021、1054–1056 | 先检查非空再调用 InitLNS 输出方法，没有赋值／删除 |
| 显式销毁 | LNS.h L41–44 | LNS 析构体 delete init_lns；LNS.cpp 无该指针的另一 delete、reset、exchange 或重新置空 |
| 路径维护 | LNS.cpp L1111–1216、1236–1339、1360–1430 | 三个 loadPaths、commitPath、clearAll 都不赋／删 init_lns |

[唯一赋值源](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L445) 与 [声明／析构源](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h#L41)。

对**新建、未复制、对象有效、没有进入 LNS2 修复或外部改写的 LNS**，init_lns 从 nullptr 保持不变；具名 LACAM 分支不调用该唯一显式写入方法，见本次 MAPFPlanner.cpp L48–73 与 LNS.cpp L496–542。这个状态归纳可关闭该限定入口的 delete-null 边，但需要第 7 节入口前提成立。不能写成所有模式 init_lns 永远空。

若进入 LNS2，源码在再次 new 之前没有 delete 旧指针这一事实须保留；本次未证明实际重复进入、泄漏量或后果。InitLNS.h 完整类没有自定义析构，持有 agents 引用而非 agents 副本，另有 PathTableWC／字符串／容器成员。隐式析构不会因引用成员自动删除原 agents。非空模式下 InitLNS::clear 的具体实现未取得，故不认证其完整搜索及清理合同；这不是用“默认空指针”隐藏的未知项。

## 5. loadPaths、commitPath、clearAll 与外围类型

### 5.1 入口实际选择的重载

SharedEnv.h L24 明确 unexecuted_paths 是 vector<Path>。MAPFPlanner::loadPaths 在 initial_success 且非 initial_run 时依次 clearAll、loadPaths(env->unexecuted_paths)、checkReplan（MAPFPlanner.cpp L35–43）。因此这个具名入口匹配 LNS.cpp L1186–1216 的 vector<Path> 重载；另两个重载存在，不自动视为当前入口所调用。

| 方法 | 实际有效语句 | 必须保留的前提／边界 |
|---|---|---|
| loadPaths(string) L1111–1152 | 打开文件，逐行 tokenizer，按 agent_id 追加 PathEntry，核起点，设置 has_initial_solution；文件打不开返回 false，起点不符显式 exit | 只读 parser 源，没有读取路径载荷；L1127 是串联比较形式的断言，不能把它当作已证明 agent_id 合法；迭代器／path.front 的非空仍需输入合同 |
| loadPaths(vector<list<int>>) L1154–1184 | 按默认 agent 数访问输入；空单路径跳过，否则追加全部位置，再以末位置补足提交覆盖；累计 initial_sum_of_costs，设置 has_initial_solution | 路径表 insert 调用是注释；不调用求解器 reset／findPath，不自动清空已有 agent.path |
| loadPaths(vector<Path>) L1186–1216 | 同样追加 PathEntry、按末项延展并累计；实际入口使用此重载 | 输入外层长度须覆盖 agent 索引；空路径可保留为空，不从“返回 true”推得每个 agent 已有可提交路径 |
| commitPath L1236–1339 | 按路径长短分支，将前段追加到 commit_path、重合边界与后段追加到 future_path；短路径用提交列表末项补长，并更新 stay_target | 不调用 reset／搜索／堆；不负责清空输出。短／空路径情况下 back、debug front 的合法性须另证；源码未使用 current_time 形参 |
| clearAll L1360–1430 | path_table.reset；复制 starts/goals/dummy goals；清 agent.path，写求解器起终点／其他目标／commit_window；清邻域与统计，重置若干标量，设置 destroy 模式 | 没有求解器 reset、releaseNodes、findPath、OPEN／FOCAL 操作或 init_lns 删除；goals[a.id][0] 等直接索引仍要求已给合法环境 |
| validateCommitSolution L1433–1483 | reserve 临时 Agent vector，每项以 false 建立求解器，复制提交路径，按 validMove／重合区间顶点和对向边判断 | 这是几何离散路径校验，不是调用求解器搜索；未覆盖所有持久终点或全部物理误差语义，不构成完整安全证明 |

唯一亲见 path_planner->reset() 位于 writeResultToFile 的 L1078–1084，只累计／清理计数的函数体继承 73E4；不能将它移接到路径维护函数。MAPFPlanner::planner_commit（L141–166）先清 future_paths／commited_paths，再调用 commitPath、validateCommitSolution；后者失败时显式退出，再复制到外部 curr_commits。该外部容器自身长度及生命周期不是上述清空操作自动保证的。

### 5.2 类型与辅助调用的有限闭合

- lns_common.h L13、19–22 直接包括 Boost pairing_heap 并给出 using 声明；未限定 pairing_heap／compare 和 unordered_map／unordered_set 的共同头来源现已亲见。A* 头与逐级 include 证据仍继承 73E3/E4；实际预处理后文件解析未运行。
- inc/common.h L41–48 定义 PathEntry（仅 location 标量及显式构造）和 Path = vector<PathEntry>；lns_common.h 中旧 Path 定义已被注释。因此 Agent 的 Path 成员不是未识别的自定义搜索对象。此结论不把实际 STL 版本及所有 allocator 合同宣告完成。
- lns_common.h L76–80 的 PIBTPPS_option 仅三个标量成员，没有用户构造／析构／默认成员初值。LNS.h 声明 pipp_option，完整 LNS.cpp 没有其标识符的有效使用。无初值与实际读取是不同事实；不替这些源码字段填写值，不宣称因此发生 UB。
- PathTable.h L9–14、27：成员为 vector 结构与 makespan，构造只建立表／goals，reset 只保存表尺寸、清空／resize／assign 并重置 makespan。dummy_goals 没有在 reset 中重置。本次没有把 reset 等同于所有成员重新构造。
- PathTable.cpp L3–17 的 insertPath 对非空路径写 table／goals／makespan；L19–39 的 deletePath 改表并可能重算 makespan，没有 LLNode Compare。索引合法与冲突前提仍需输入／调用合同，不由模板类型推得。
- checkReplan（LNS.cpp L383–443）清不再从预期起点出发或未到目标的路径；以 Instance::hasCollision 对已接受路径作离散冲突检查，条件满足则 insertPath。Instance.cpp L373–399 的有效 hasCollision 只查共同长度内的顶点／对向边，较短路径终点的延续检查处于注释。
- Instance.h 的 getDummyGoals 返回成员 vector 副本；validMove 检查下一位置范围／障碍和曼哈顿距离，辅助坐标函数直接用 env->cols。源码没有替这些索引、除数、位置或目标集合提供完整合法域证明。

这些事实关闭了具名依赖的函数体和类型身份，不是全实例合法性通过，也不是读／运行了任何环境载荷。

## 6. 四个 LLNode 堆：Boost 1.85.0 的条件生命周期

四个类型继承 73E4 的精确映射：SIPP OPEN／FOCAL 和 SpaceTimeAStar OPEN／FOCAL，分别绑定 LLNode::compare_node 或 secondary_compare_node。R0 类型只显式给元素类型与 compare 选项，没有传节点范围或运行时比较器对象。两个原比较器没有自定义构造／析构；随机逻辑位于 operator()，不能把比较器对象被默认构造或复制当成其 operator() 被调用。

在本次取得的官方 [pairing_heap.hpp](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/pairing_heap.hpp)／[stable_heap.hpp](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/detail/stable_heap.hpp)／[policies.hpp](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/policies.hpp) 下：

| 链 | 亲见语句／推论 |
|---|---|
| 模板与缺省选项 | pairing_heap L42–70、126–141；stable_heap L556–565；policies L87–98。Compare 保留显式类型，allocator 取标准 allocator，未给 stable 时进入非 stable heap_base，size 采用该版本缺省选项。这里是库身份解释，不是部署或实验赋值。 |
| 零实参构造 | pairing_heap L235–237 建立默认 value_compare，传给 super_t 并将 root 置空；make_pairing_heap_base::type L68–70 只传给 base_type，allocator 基类默认构造。 |
| 基类 | 非 stable heap_base L147–171 将比较器复制到基类或 MSVC 对应成员；size_holder L37–39 初始化计数。已读该非 stable 类到结束 L284，无自定义析构。对象构造／复制不调用 LLNode 的 operator()。 |
| 空状态检查 | pairing_heap L286–289 的 empty 只比较 root 与空指针；不比较元素。 |
| 析构 | L279–283 是 while (!empty()) pop()。若 heap 自建立后未插入／移入／改写节点，root 保持空，循环体不执行；基类／比较器销毁没有节点值比较。条件是这种有限生命周期，不是“所有析构”。 |
| 非空销毁 | pop L397–402 → erase L516–534；根有孩子时进入 merge_node_list，再经 merge_first_pair L682–694 到 merge_nodes L696–703；当需要合并两个孩子时，L698 调基类谓词，stable_heap L209–211 再调原 Compare。非空并不保证每次都比较，但不能宣称不比较。 |
| clear 与析构不同 | clear L311–322 在非空时调用节点清理；本次目标析构没有调用 clear，不能拿 clear 的实现替代析构证明。 |

因此，**若**实际采用上述精确头文件、正常新建的四个求解器堆始终没有节点、没有其他搜索／外部改写或失败破坏，构造到销毁这段不会执行 LLNode 随机比较。源内 LaCAM 选路与计数／路径维护的已读事实支持核查这种局部条件，但实际版本、全调度以及第 7 节新增问题没有被消除。

保留 72E5 的层次：原随机平局谓词不能保证严格弱序；官方所读 Compare 文档说明堆序用途，没有取得可无条件套用的第三方“违反严格弱序即已发生 C++ UB”特定条款。不把 std 库概念机械移到 Boost，也不把未证明 UB 当作算法正确性背书。

## 7. 实际入口补核：三项不能被四空堆豁免的问题

### 7.1 初始化预处理存在第五堆

MAPFPlanner.cpp L6–20 的顺序是 initMap → computeAllPair → new LNS。Instance.cpp L129–186 的 computeAllPair 在每个非障碍起点建立局部 boost::heap::pairing_heap；L143–149 的 Node::compare_node 按 value 返回“大于等于”，L166 给出容器类型，L171／182 push，L174／175 top／pop。这不是只存在于未调用的搜索成员中的定义：[固定预处理源](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/Instance.cpp#L129)。

对字段有效的相同 Node，比较自己的 value 得到 true；仅此已否定“该关系保证不可自反”的表述，不需随机序列或实验。实际 heap 操作是否比较同一对象、何时出现同键不同节点、结果错误与运行 UB 均不由此直接推出。实际库仍未绑定，72E5 对第三方条款适用范围的限制也继续成立。

这个对象使“纯 LaCAM 避开 LLNode 搜索即可消除全部不合格排序关系”的路线不成立。该初始化在 algo 选择映射之前执行，官方 mapfPlanner 类别不跳过它。空图／提前退出或不进入初始化不构成有用 lifelong 主比较域的替代证明。修正该关系、换 all-pairs 实现或导入外部缓存都要登记为源码／计算组织变化，并核其正确性与费用；不能继续冒称未改 R0。

### 7.2 首次按值读取未初始化的 init_time_limit

实际构造链已展开，而非只凭成员名猜测：

- driver.cpp L87 new MAPFPlanner；L124、128、137 通过三个带实参 std::make_unique 分支分别建立 TaskAssignSystem、InfAssignSystem、FixedAssignSystem。
- CompetitionSystem.h L139–163、181–197、213–230 的对应派生构造都调用 BaseSystem(grid, planner, model)。BaseSystem L25–27 只在初始化列表写 map、planner、env、model，构造体为空。
- 同一 header L87 声明 int init_time_limit，无默认成员初值；完整各构造体都不赋它。不同于该类另一些有默认成员初值的字段，不能因对象由 make_unique 创建就给这个标量补成零初始化。
- 完整 CompetitionSystem.cpp 内该标识符只在 L356 出现：planner->plan(init_time_limit)。driver 全文内相关 CLI 名只在 L49 注册；实际 setter 调用 L146–158 没有将其转赋，也没有已声明的 init-time setter。完整 header/source/driver 的这些标识符检查没有发现赋值、取址后赋值或静态配置接线。
- initialize、三个 update_tasks、InfAssignSystem::sync_shared_env 的有效语句已读，均未给此成员赋值。两个其他系统的 sync_shared_env 在 header 中为空。未把外部模型或日志的未知运行行为当作对这个成员的初始化接口。

MAPFPlanner::plan 的形参是按值 int（MAPFPlanner.cpp L46）；在正常到达 L356 并调用时，从此成员初始化形参需要 lvalue-to-rvalue 求值。官方 LACAM 函数体 L50 先把形参送进 setRuntimeLimit，L53 之后才进入首次分支并覆盖 runtime limit。后一次覆盖不能改变此前实参已经求值的语义。[调用源](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/CompetitionSystem.cpp#L341)、[成员和构造](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/CompetitionSystem.h#L25)。

精确判断是：**在这些源码构造和进入首次 plan 的前提内，成员无定义初值而被按值求取，是源码前提内确定的未初始化读取问题。** 没有运行或构建，故不报告某个具体进程已触发了 UB、崩溃或错误结果。也不因未观测运行，反过来把这条源码链降格为可以忽略的纯假想风险。

设置原 CLI initTimeLimit 本身不修复所见缺失接线；mapfPlanner 选项也不绕过函数调用的实参求值。所读正常入口没有可据此认证的原样配置规避。其他未读翻译单元／非官方外部封装是否增加了初始化，没有证据，不能倒填为现入口已有行为。需要引入并记录构造／受控适配层初始化和参数传递，不给该字段或任何保护参数选取数值。

### 7.3 初始化失败、计时与退出合同

CompetitionSystem.cpp L101–115 将 MAPFPlanner::initialize 放入局部 packaged_task／thread。wait_for ready 时 join 后返回 true，没有 future.get；不能把这个布尔返回直接当作“初始化无异常成功”的完整确认。非 ready 时 detach 并返回 false。BaseSystem::initialize L516–520 记录状态后仅 return；simulate L344 调用该 void 方法后，无返回成功条件，L352–363 继续同步／loadPaths／plan／commit。

为避免把函数名 fatal 当作退出机制，本次精确补读 Logger.h/.cpp。Logger.cpp L48–61 的两个 log_fatal 只组成消息并写 Boost 日志，无显式 exit／throw／终止语句。所以在日志及随后调用正常返回的条件下，初始化超时后继续链确实由所读语句支持。未核实际 Boost 日志异常或进程信号状态，不声称这一条件在某次运行已满足。

CompetitionSystem.h L29–40 的析构在 started 为 true 时 join 成员 task_td，再 delete planner。已读类的 started 有默认 false；完整 system.cpp 没有该成员的赋值。planner_initialize 创建的是局部 init_td，超时后已 detach，不是这个成员线程。因而所见析构 join 不能被拿来证明 detached 初始化线程已经安全结束。实际线程 interleaving、竞态／悬垂是否发生未观测，不能静态可达便记成已发生。

driver L25–32 的信号路径调用保存后 _exit；正常末尾 L169–171 删除 model/logger 并返回，system_ptr 是文件作用域 unique_ptr。退出与析构链须分轨，不能把正常 delete 结论外推到信号强退；本次没有认证保存、日志或信号处理的完整安全性。

此外，simulate L354／388 的 loadPaths 在计时起点之外；L355–359／389–393 的 steady_clock 区间只包住 plan，commit 在计时区间之后。源码注释也明确把加载视作免费。固定 R0 原生计时记录与后来公平全服务费用适配必须分开登记，不能把本次源码窗口称成已满足 73 的完整费用协议。

## 8. 对路线选择的建设性约束

以下仅是可审查的设计选项，不是改码许可、部署选择或已通过资格：

| 路线 | 可以诚实保留的内容 | 必须新增的证据／不得省略的代价 |
|---|---|---|
| 原生 R0 保真记录 | 固定 commit、官方 LACAM 选择器和原时钟／随机／加载语义；承认上述源缺口 | 保真档案不等于合格主基线；不能仅挑进入正确状态的成功运行来补初始化契约，不能把后续修复回填原作者代码 |
| 显式修正版 R0 适配 | 为 init_time_limit 增加明确的受控初始化／接线；为初始化返回定义成功、异常、超时与终止；修复预处理比较关系或更换经证明等价的组件 | 必须单列改动身份及新版本名；传播失败状态至 simulate，保证规划前置条件与线程所有权；原有日志文本不自动充当安全停止。外层如果通过派生封装初始化受保护成员，也仍是新适配入口 |
| 受限调用 R0 规划内核 | 在充分说明不使用原 driver／系统 harness 的前提下保留某些规划内核源码 | 独立生命周期／时钟／输入合法性与全部准备成本仍须自给；不能称完整原生 PIE-D；第五堆若仍调用便仍有同一义务 |
| 其他官方／已发表实现比较 | 选择真正满足最终 lifelong 假设的独立方法，继续保留 PIE-D 的学科锚点及保真轨 | 外部算法身份、来源许可、同域适配、费用与竞争强度仍须单独闭合；不能因 R0 有缺口而降低比较标准或宣布当前方案唯一 |

所谓“外层失败截断”必须有可观察、可信、完整的初始化状态及线程回收合同。现有 simulate 没有成功返回值接线，简单在外部宣称“只运行成功初始化”并不是已存在的官方可配置行为。未来若为公平适配加入该机制，应把初始化失败及其耗时计入共同固定观察期和全 roster，不能删去失败实例。以上不给保护参数数值／范围／默认值，不生成配置或实验载荷。

## 9. 本件可闭合项与精确剩余项

| 问题 | 本件状态 |
|---|---|
| init_lns 默认声明后的有效显式赋值／删除、路径维护是否改它 | 在 LNS.h/.cpp 范围闭合；唯一写分支与删除边明确，限定 LACAM 状态归纳成立 |
| 实际 loadPaths 重载、clearAll／commitPath／reset 的逐句关系 | 闭合到所列源语句；输入／状态合法域未认证 |
| Path、PIBTPPS_option、PathTable 构造／reset、辅助插删的类型和显式行为 | 已取得具体声明／实现；实际标准库及全下游未无限展开 |
| 四堆实际 Boost 版本 | UNKNOWN；无实际绑定证据 |
| 四堆在登记 Boost 1.85.0 下的有限构造／空析构行为 | 条件源码结论完成；非空析构可以进入 Compare，不允许泛化 |
| 初始化第五堆 | 新定位且不能保证严格弱序；不能被纯 LaCAM 搜索选路豁免 |
| 初次 plan 的 init_time_limit | 原源所读正常调用链无初始化而按值读取；不是 CLI 参数存在便闭合 |
| 调度和退出 | 正常显式调用桥已取得；失败继续、异常确认、detached 线程、信号退出仍不合格／未闭 |
| 全程序原样语义域／所有运行 UB／可复现行为 | 未证明、未运行；不得标 PASS |
| G3 或六门正式投票 | 本件 NONBALLOT 不投票；根须独立评估新证据，不能仅按原“四堆缺口”继续推进 |

仅列未执行合同，未创建或运行研究测试：

- 输入与对象合同：合法 env／目标／路径容器，所有 front/back／索引／除法的前提与失败口径；不可把函数 true 返回当作所有前提已满足。
- 初始化合同：标量初始化来源与首次调用前的赋值链、完成／异常／超时的可信状态、线程存活与持有关系、失败后的合法停止；仅设置原选项不能补缺失接线。
- 库合同：先给实际头／编译身份，再将确切版本四堆及第五堆对应操作展开；数学关系与实际运行发生分开。
- 比较身份合同：若有修正，保留固定原源、差异及适配名；时钟、随机消耗、预处理、路径加载、提交、异常和退出费用按最终协议计费；不隐去原计时区间外的服务。
- 审查合同：以上来源要进入根无 skill 分析与后继候选完整规格，正式导师→Nature→明确无 skill 逻辑→根验收的顺序不被本件代替。

## 10. 获取失败、身份及实际阅读层次

一次误猜 inc/MAPF-LNS2/inc/common.h 返回 404；随后沿 PathTable.h 实际 include 取得 lns_common.h，再沿其 include 取得 inc/common.h，没有扫描目录。Logger 两个精确对象首次均 Transport error，重试同一 ref／路径成功；未把失败算正文。批量散列命令首次因参数过长未创建进程，随后拆为有限内存数据批次成功；没有把源码当程序执行。

全部二十对象完整取得为 197761 bytes、6239 逻辑行；逻辑行包括无末尾 LF 的最后一行。这是取得／摘要范围，**不是全文语义阅读量**。本次语义范围在下表最后一列；其余部分仅用于同对象身份和具名标识符／方法定位。每个 blob 都是 GitHub 返回值并与 SHA1(blob 长度头 + 原始 UTF-8 正文) 独立重算相同，SHA256 同时按完整字节计算。

| 官方对象（页面／原始字节） | 返回且重算匹配的 Git blob | SHA256 | bytes | 逻辑行／LF | 实际阅读层次 |
|---|---|---|---:|---:|---|
| [CMakeLists.txt](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/CMakeLists.txt) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/CMakeLists.txt) | 148459bb9542731723e8125bb8d54da6a3ce954b | ecdf7e3c889ab8290eb9cc839543c0f281419db957982a03b79ae79da25dc899 | 2790 | 92 / 92 | L1–92 全文 |
| [src/MAPF-LNS2/src/LNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp) | 1fb0e54f8f2bb00af05de53233ae600774e36f2a | 0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2 | 53100 | 1486 / 1486 | L1–55、383–544、1017–1060、1074–1088、1111–1486；全文 init_lns／pipp_option／path_planner／reset／delete 与方法定位 |
| [inc/MAPF-LNS2/inc/LNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h) | 5b9ce3ef4aeaf6fcfa88c211c0f536c66f8ae24e | c9751aca5f3c305d5da49c3445ec29cb19819655b496de12c522d83d7af7ad91 | 4201 | 119 / 119 | L1–119 全文 |
| [inc/MAPF-LNS2/inc/InitLNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/InitLNS.h) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/InitLNS.h) | e3a93022b865afbcd539e9305e618ddc29829c5e | 7fe9f3e25a9ce2c77a83e8ec3c6177195d464890b1b9690f42abbca25d4d8901 | 1838 | 58 / 58 | L1–58 全文 |
| [inc/MAPF-LNS2/inc/PathTable.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/PathTable.h) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/PathTable.h) | 0ae813e9526367d3076c297deba51fc0ad3a5a76 | 909a0fe4a8ebb89a69819d47cf80db579ed1793a75d1936dc2787edddd5ecbc2 | 3090 | 56 / 55 | L1–56 全文 |
| [inc/MAPF-LNS2/inc/lns_common.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lns_common.h) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lns_common.h) | 3bddf54ab74388904064a60a92346883a52c10cb | 8994fbaf6e022f7b233b7015741ae277d5773f3c84665845ecc654b44a51ccf6 | 2890 | 102 / 102 | L1–102 全文 |
| [src/MAPF-LNS2/src/PathTable.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/PathTable.cpp) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/PathTable.cpp) | 1dd06d5c8ef71841409a88517cc419df841fefb8 | 96cb8eaef095e01f99f69b91951372c5c2d2f966c6c2c126f315bdbdc429321c | 12025 | 374 / 373 | L1–40、369–374；全文方法声明定位 |
| [src/MAPFPlanner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp) | 94afb42df1a70f5e312a382e61cf83576fd7360e | c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1 | 6125 | 208 / 208 | L1–208 全文 |
| [inc/MAPF-LNS2/inc/Instance.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/Instance.h) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/Instance.h) | 97808fa7929c1f99772b05b047c20d48bb878814 | ed1dea14eba7373d13b2378e59839bf962085316ffb6527655f92dfc5aae565d | 4939 | 154 / 154 | L1–154 全文 |
| [inc/common.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/common.h) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/common.h) | 9ddeff363a76cbd70a3e6e1ca98cfd79f69c8237 | 6d0aaa271e61201ffc6313e9ae1210f9b4e75fea6711a6edca7117be4dc3b67d | 5954 | 224 / 224 | L1–224 全文；仅源码，不打开其读取目标 |
| [src/MAPF-LNS2/src/Instance.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/Instance.cpp) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/Instance.cpp) | 2183ba41c4a04278fafa0c4ed0605762abd5fb7c | dcfd6fb4b134dcc437b6124d5bf099e4fd6a977e9f749607446e87b7fedae2ac | 14658 | 455 / 454 | L1–90、129–207、373–447；全文方法定位 |
| [src/driver.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp) | b75764cc26c2374ce51dabb94e13a138e50f166f | 3198636d1114e4901c9aae48d549787c9fb3bc3a0bdfd49b6445d81bb5fc4f44 | 6664 | 172 / 172 | L1–172 全文 |
| [inc/SharedEnv.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/SharedEnv.h) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/SharedEnv.h) | 7f4b4678ca9da7278e92fd4cdf9eed043f03a8e2 | 8acce1b85b0878e575606e0058e10b46366bdc1eae4e4d9982dd5f355e627de0 | 573 | 27 / 27 | L1–27 全文 |
| [inc/CompetitionSystem.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/CompetitionSystem.h) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/CompetitionSystem.h) | 6daf0b9e3fa1015e49893b09be87940577427189 | e4e0b26e30412503e496d56af1b1fd841fe9ff01b99ca425316027538bcc0f55 | 6753 | 243 / 243 | L1–243 全文 |
| [src/CompetitionSystem.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/CompetitionSystem.cpp) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/CompetitionSystem.cpp) | 4e9a86921fda3fd15bd616c3c0dff461688254ed | fe7532c9fe4e4dfe19d8e5e7c2192635c99a5fbd8c4d95db728ae02336839604 | 27752 | 885 / 884 | L52–146、341–530、830–885；全文 planner／BaseSystem／init_time_limit／started／线程及方法定位 |
| [include/boost/heap/pairing_heap.hpp](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/pairing_heap.hpp) · [raw](https://raw.githubusercontent.com/boostorg/heap/boost-1.85.0/include/boost/heap/pairing_heap.hpp) | c591cc9e80dbce40b351a0f90ab4210d2a2a4a54 | 668543a7a2ab2b4519452a5f841d36f30761cb99b102e3273d999adb3afe9fcd | 22458 | 715 / 715 | L30–103、126–159、226–332、380–423、511–551、635–707；全文构造／析构／include 定位 |
| [include/boost/heap/detail/stable_heap.hpp](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/detail/stable_heap.hpp) · [raw](https://raw.githubusercontent.com/boostorg/heap/boost-1.85.0/include/boost/heap/detail/stable_heap.hpp) | bfec26d63c2b605bb4f47b5cae7baf066c1d8cdc | 24d78657787040120778df3d60396c1b1c16d6f5babc612431a028b9a387e371 | 14940 | 585 / 585 | L37–294、553–582；全文构造／析构／include 定位 |
| [include/boost/heap/policies.hpp](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/policies.hpp) · [raw](https://raw.githubusercontent.com/boostorg/heap/boost-1.85.0/include/boost/heap/policies.hpp) | 6a251a9faafdeca593ab45f741d47a67b02ef9d0 | 5d186a313d2281d6504c4b656b069047e3ef0cb81ea873c5df102ac4da20e079 | 4413 | 174 / 174 | L18–37、81–124 |
| [src/Logger.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/Logger.cpp) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/Logger.cpp) | 3e09d1c84979f429730c1196130a9982b62076a5 | 416636b5ee9b918c0f4f76579db2c44d624c02b41046f7972477a89c2a05c67e | 1668 | 77 / 77 | L1–77 全文 |
| [inc/Logger.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/Logger.h) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/Logger.h) | 7805a13395e509d4d4c3ec3787836e90555f17d0 | 7e92fbf177edd992bc88f70ff8c9f5104b0be65600cab0e38e73efb2a68c3606 | 930 | 33 / 33 | L1–33 全文 |

本件未读取任何 map／scen／config／agent／task／delay 载荷正文，没有访问桌面、35–38、Q-CAL／Q-CONFIRM 或实验结果。只取得 parser／源程序中的读写语句，不打开其文件目标。未实现、构建、编写或执行研究测试、仿真、调参或控制机器人；没有给 H、T_delay、B_CAL、B_max、B*、P_active、density N 数值、范围、默认值或新含义。

新工件仅本研究目录的本报告，用 apply_patch 创建；所有 shell 段均有 rtk 前缀。没有修改 73、冻结文件、行政页或 Git 状态，不同步远端，由根按精确白名单处理。本件完成后的文件身份单独回报，停止本有界来源任务；研究目标及各门保持未完成。

