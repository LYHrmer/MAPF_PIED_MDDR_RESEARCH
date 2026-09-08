# 73E4：R0 LACAM 的 Agent 与求解器末端生命周期来源回执

日期：2026-09-08。性质：固定来源、五个新增完整源对象、NONBALLOT、有界静态补核；不是正式审查，不替原 69E1，不补冒缺失的 73E2。

## 1. 已补齐的边界

**Agent 的两条构造分支及求解器基类的显式生命周期已闭合到具体函数：`true` 创建 SIPP，`false` 创建 SpaceTimeAStar；两者只显式转入保存 Instance 引用的 SingleAgentSolver 构造。Agent 析构通过具有虚析构函数的基类指针删除对应求解器。** 两种派生求解器均未声明自定义析构函数，故剩余工作落在已列明的成员容器及默认基类析构，不是某个尚未定位的求解器析构函数体。

本次同时确认：BasicLNS 的完整类声明没有单体求解器成员；`reset()` 只累计并清零统计计数；`setIterations()` 只赋值；SingleAgentSolver 的 `compute_heuristics()` 当前有效函数体为空。上述源层显式构造、析构、计数和 setter 没有调用搜索、堆 push／pop 或随机比较器。

两种随机比较器的实际定义现已亲见，位于 LLNode 中；SIPP 与 SpaceTimeAStar 的四个堆类型都绑定到它们。需要库证据的剩余问题已缩小为这些具体 `pairing_heap` 实例的零实参构造、析构及由此实际调用的内部函数，不能凭默认空容器的经验判定比较器绝不被调用。本回执没有把这项尚未证明的库结论写成已通过。

## 2. 来源分层与授权范围

唯一仓库为 `YueZhang-studyuse/LMAPF-delay`，所有本次网络源请求固定完整 commit `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。本次恰好读取下表五个新增对象，Agent 定义已经包含在 BasicLNS.h 中，没有另读 Agent 文件。BasicLNS.h 首次请求遭遇连接器传输错误，重试同一固定对象成功；没有换仓库、换 ref 或改用默认分支。

沿用的证据有两层，均不冒称本次重新取得：

- [73E1 回执](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73E1_R0_PURE_LACAM_ENTRY_DOMAIN_BOUNDED_SOURCE_NONBALLOT_RECEIPT_20260907.md) 已报告的 Planner／LNS 调用点与具名 LACAM 选路。本子任务已有其回执正文，没有其六个原始源正文缓存，故涉及这些函数体时标为“继承 73E1”，不凭摘要补造未记录语句。
- [73E3 冻结回执](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73E3_LACAM_REMAINING_CONSTRUCTOR_SCOPE_NONBALLOT_RECEIPT_20260908.md) 及本代理保留的四对象原始内存，尤其 SpaceTimeAStar.h／.cpp、BasicLNS.cpp 与 MAPFPlanner.h。使用这些旧缓存定位时仍标为“继承 73E3”，未重新请求源正文，也未改动冻结回执。

73E3 中“原 69E2”的文字按根任务行政说明视为笔误；本次不改冻结文件，缺失的约定回执编号为 73E2。本任务是新的 73E4，不声称失落任务已完成。

## 3. 五对象完整身份

正文通过 GitHub `fetch_file` 完整返回，无行裁剪，无源码落地。对同一完整 UTF-8 字节流重算 SHA256、字节数、LF／逻辑行，并重算 `SHA1("blob " + 字节数 + NUL + 正文)`；五项均等于 GitHub 返回的 blob SHA-1。校验仅将源码作为标准输入数据，不执行源码。

| ID / 本次完整对象 | Git blob SHA-1：返回＝重算 | 完整正文 SHA256 | bytes | 逻辑行 / LF | 阅读强度 |
|---|---|---|---:|---:|---|
| [A1 · inc/MAPF-LNS2/inc/BasicLNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h) | `c22e0b66cc58e9c9ce19d6b161e4f54dabfb4c15` | `9927e17d5c6dd3624ed4e5dc3cc81c20eec854b340ddf4723f93d873a6b526ff` | 2042 | 77 / 76 | L1–77 全文；末尾无 LF |
| [A2 · inc/MAPF-LNS2/inc/SingleAgentSolver.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h) | `c22f59ac763c3bc272a82b5c8e9793a91f5da94a` | `daafdc674f90bbe4b34031b19f2564fb93189f07d7ad15e0927e1574cbb5611f` | 7935 | 226 / 226 | L1–226 全文；保留 UTF-8 BOM |
| [A3 · src/MAPF-LNS2/src/SingleAgentSolver.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SingleAgentSolver.cpp) | `bbbc5d1745a8c649ddb29ecbc27122ba92f0a6ef` | `ef3f96da47b9fdd830e4aafff90677f85168370e3ae2fdbb0b402555d4539d30` | 6545 | 176 / 176 | L1–176 全文 |
| [A4 · inc/MAPF-LNS2/inc/SIPP.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SIPP.h) | `9f2366ad6e8bf4084299b6d3649414394c850694` | `8ebf98b9518844473ac66f6064e5c9810774fe4f7f79fdb7e25fe4c69abd318d` | 5725 | 131 / 131 | L1–131 全文；保留 UTF-8 BOM |
| [A5 · inc/MAPF-LNS2/inc/LNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h) | `5b9ce3ef4aeaf6fcfa88c211c0f536c66f8ae24e` | `c9751aca5f3c305d5da49c3445ec29cb19819655b496de12c522d83d7af7ad91` | 4201 | 119 / 119 | L1–119 全文 |

新增源总量：**26448 bytes、729 逻辑行、728 个 LF、五个对象**。所有正文包括注释和空行均完整阅读；末尾无 LF 的最后一行计入逻辑行。下面为对应原始内容的不可变 URL：

- [A1 原始正文](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h)
- [A2 原始正文](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h)
- [A3 原始正文](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SingleAgentSolver.cpp)
- [A4 原始正文](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SIPP.h)
- [A5 原始正文](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h)

## 4. 从已核调用点到本次亲见末端的链

### 4.1 官方模式下仍存在的 SIPP 对象构造

继承 73E1：MAPFPlanner 初始化无条件建立 LNS，传递的 `use_sipp` 为 true；LNS 构造遍历 agents，并把该布尔值传给 `agents.emplace_back(instance, i, use_sipp)`（73E1 O1 L11–20、O2 L7–47）。本次 A5 L23 亲见此成员类型为 `vector<Agent>`。随后可展开至本次源中的确定末端：

```text
MAPFPlanner 初始化 → new LNS(..., use_sipp=true, ...)       [继承 73E1]
  → agents.emplace_back(instance, i, use_sipp)            [继承 73E1]
  → Agent(instance, id, true)                            [A1 L12–18]
  → Agent::path 的默认构造（Path 定义不在五对象内）       [A1 L10；构造体前的成员初始化]
  → new SIPP(instance, id)                               [A1 L14–15]
  → SIPP::SIPP → SingleAgentSolver(instance, agent)       [A4 L105–106]
  → SingleAgentSolver::SingleAgentSolver：只绑定 instance [A2 L196–200]
  → SIPP 的容器成员按声明顺序默认构造                    [A4 L110–118]
  → SIPP 与 Agent 的显式构造体结束
```

A2 构造内 `compute_heuristics()` 是注释，没有调用；该构造没有读取 agent 对应的起点、终点或载荷。A3 L12–54 又亲见 `compute_heuristics()` 的有效体为空，旧局部堆搜索全部处于行注释中。因此这条构造链没有隐藏在该函数中的有效启发式搜索。[A1 Agent](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h#L12)、[A2 构造](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L196)、[A3 注释体](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SingleAgentSolver.cpp#L12)

这已足以否定“选 LACAM-only 后不再有 SIPP 对象”的强表述：对象构造与搜索模式选择是不同的已核调用事实。是否在任何隐式库生命周期中比较节点，则仍须第 7 节的限定库证据。

### 4.2 临时 Agent(false) 的 SpaceTimeAStar 构造与销毁

继承 73E1：`MAPFPlanner::planner_commit` 调用 LNS 的提交和校验方法，`validateCommitSolution` 内存在临时 `Agent(..., false)`；本次不凭回执补造其未记录的准确源码行号。A1 现在把这个已知布尔调用点精确展开为：

```text
planner_commit → validateCommitSolution → Agent(..., false) [继承 73E1]
  → new SpaceTimeAStar(instance, id)                         [A1 L16–17]
  → SpaceTimeAStar::SpaceTimeAStar                           [继承 73E3 N2 L91–92]
  → SingleAgentSolver(instance, agent)：只绑定 instance      [A2 L196–200]
  → A* 的 OPEN、FOCAL、节点表默认构造                        [继承 73E3 N2 L95–103]
临时 Agent 的生命周期结束
  → Agent::~Agent → delete path_planner                     [A1 L19]
  → 经 virtual ~SingleAgentSolver 分派到动态求解器析构      [A2 L201；C++ 生命周期解释]
  → SpaceTimeAStar 隐式析构：节点表、FOCAL、OPEN             [继承 73E3 完整类；逆声明顺序]
  → SingleAgentSolver 默认析构                             [A2 L201]
  → 返回 Agent 析构体后，析构其 Path path 成员              [A1 L10；Path 定义不在五对象内]
```

这里已关闭 73E3 对 Agent(false) 选路和基类虚析构的缺口。SpaceTimeAStar 的 `releaseNodes()` 是普通成员，73E3 亲见它被搜索函数调用；没有自定义析构调用它的源码，不能在上面的链中擅自插入 `releaseNodes()`、`findPath()` 或 `getTravelTime()`。

### 4.3 BasicLNS 是另一个初始化分支，不是求解器成员的持有者

A5 L20 亲见 LNS 继承 BasicLNS。继承 73E3：BasicLNS.cpp L2–3 显式初始化 Instance 引用和三个标量，函数体为空。A1 L37–77 的完整 BasicLNS 声明现在显示，它持有统计 list、destroy_weights、Neighbor、edges_count 等成员，**没有 Agent、SIPP 或 SpaceTimeAStar 成员**，也没有基类。因此不能把“BasicLNS.h 同时定义 Agent”误写成“每次 BasicLNS 构造都因成员构造创建求解器”。

Agent 的实际持有者在本次所读 LNS 类中是 `vector<Agent> agents`。BasicLNS 仍有容器默认构造／析构，但它们不使用 LLNode 的 OPEN／FOCAL 比较器类型；不应把这部分标准容器初始化混进四个求解器堆的比较器问题。[A1 BasicLNS 完整类](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h#L37)、[A5 继承与 Agent 成员](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h#L20)

### 4.4 LNS 与 SIPP 的销毁链

继承 73E3：MAPFPlanner 虚析构中 `delete lns`。本次 A5 L41–44 亲见 LNS 析构体执行 `delete init_lns`，随后按 C++ 规则析构其成员与 BasicLNS 基类。agents 成员销毁时，每个有效 Agent 都进入 A1 L19 的删除链：

```text
MAPFPlanner::~MAPFPlanner → delete lns        [继承 73E3 N4 L17]
  → LNS::~LNS → delete init_lns               [A5 L41–44]
  → LNS 成员析构，其中 vector<Agent> agents  [A5 L23；逆声明顺序规则]
  → Agent::~Agent → delete path_planner      [A1 L19]
  → 对正常持有 SIPP 的 Agent：SIPP 隐式析构  [A4 完整类 + A2 L201]
  → useless_nodes、allNodes_table、FOCAL、OPEN [A4 L110–118；逆声明顺序]
  → SingleAgentSolver 默认析构              [A2 L201]
LNS 成员结束后 → BasicLNS 隐式析构           [A1 完整类；无自定义析构]
```

SingleAgentSolver 没有基类，两个直接容器成员是 `vector<int> other_goal_locations` 与 `vector<int> my_heuristic`（A2 L160、164）；其默认析构不含用户编写的搜索调用体。Instance 成员为引用，未拥有该 Instance。A4 完整 SIPP 类没有析构声明；L32 的空析构属于 SIPPNode，不是 SIPP。

`init_lns` 在 A5 L78 有默认成员初始化 `nullptr`。这只证明初始声明默认值，不独立证明所有后续调用都保持该值；本子任务只有 73E1 回执而无其 LNS.cpp 全文缓存，因此没有把 `delete init_lns` 自动折叠成空操作。若指针非空，其动态对象的析构需 InitLNS 定义；该头不在本次五对象内。此缺口定位于这一条具体删除边，不影响本次已核 Agent 的两种动态求解器选路。

## 5. reset、setIterations、loadPaths 与 commitPath 的头内范围

| 方法 | 本次亲见位置 | 有效语句与本次结论 |
|---|---|---|
| `SingleAgentSolver::reset()` | A2 L202–214 | 根据生成数决定是否累计三个计数和运行次数，再把本轮三个计数清零；没有容器、搜索、随机函数或比较器调用；也没有清空 OPEN／FOCAL |
| `LNS::setIterations(int)` | A5 L61 | 仅把形参写入 `num_of_iterations`；继承 73E1 的具名 LACAM 分支对此 setter 的调用，现在落到已读赋值末端 |
| `LNS::setRuntimeLimit(int)` | A5 L62 | 仅赋 `time_limit` 与按比例计算 `replan_time_limit`；没有搜索／堆操作 |
| `LNS::setHasInitialSolution(bool)` | A5 L64 | 仅赋布尔字段；没有搜索／堆操作 |
| `loadPaths` 的三个重载 | A5 L50、56–57 | 只有声明，没有头内定义或默认参数表达式；不能在该头里额外引入隐藏的内联搜索，也不能据声明认证源文件函数体 |
| `commitPath(...)` | A5 L58 | 只有声明，没有头内定义或默认参数表达式；其已有源函数体证据来自 73E1 |
| `clearAll(...)` | A5 L63 | 只有声明；没有本次新增的头内执行体 |

本次不能把 `loadPaths`／`commitPath` 自行连到 `reset()`：A5 只有声明，73E1 回执没有列出足以定位这条直接边的具体语句。可采用的完整分层是：73E1 已核 Planner 到 LNS 提交／路径维护的显式调用及 LNS 源方法体；73E4 新核相关头没有额外内联体，并核实 `reset()` 本体的计数语义。调用边若需逐行重建，应使用原 73E1 的源缓存，不能由函数名推测。[A2 reset](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L202)、[A5 方法声明与 setter](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h#L50)

## 6. 已定位的比较器与独立搜索成员

A2 L41–59 为有效 `LLNode::compare_node`：在相关字段相等时，L51 调 `rand() % 2`。A2 L81–103 为有效 `LLNode::secondary_compare_node`：在其平局条件下，L93 同样调用随机函数。前面分别存在被注释掉的旧定义，本回执以有效定义为依据。二者只有比较运算符的用户函数体，没有用户编写的构造／析构函数；不能把比较运算符里的随机调用当作默认构造比较器对象时的显式调用。[A2 OPEN 比较器](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L41)、[A2 FOCAL 比较器](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L81)

A2 L106–140 的 LLNode 构造、默认析构及 `copy()` 只涉及字段与标量条件，没有随机、堆或搜索调用。A4 的 SIPPNode 构造／copy 同样只转入这些基类函数并操作字段；声明节点类型和句柄类型本身不是创建搜索节点。

A3 另有真实的独立搜索函数 `findMinimumSetofColldingTargets(...)`（L58–170）：它在 L95 建立局部 `pairing_heap<Node*, boost::heap::compare<Node::compare_node>>`，L102／143／156 push，L108 pop，L161 increase。其局部比较器位于 L74–89，没有直接 `rand()`；这不是严格弱序认证。构造、默认析构、reset 和 setter 中均没有调用该搜索函数。本次精确识别其存在，未把它并入初始化链，也未认证整个程序不存在其他调用者。[A3 独立搜索](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SingleAgentSolver.cpp#L58)

继承 73E3：SpaceTimeAStar.cpp 中实际 OPEN／FOCAL 操作位于 `findPath`、`getTravelTime`、push／pop 辅助成员和清理成员。本次 SIPP.h 中搜索、push／erase／清理方法只有声明；未读 SIPP.cpp，不声明其搜索实现完整通过。继承 73E1 的具名 LACAM 显式选路不进入 `runPP → path_planner->findPath`，是避免该已知搜索调用点的依据；不是比较器全程序不达的替代证明。

## 7. 有限、具体的库生命周期缺口

### 7.1 四个直接关联随机比较器的堆实例

下表保留源码的准确类型拼写。SpaceTimeAStar 的未限定名字来自继承 73E3 缓存；其 `AStarNode::compare_node` 和 `secondary_compare_node` 由 LLNode 继承，本次 A2 已读实际定义。

| 持有者与成员 | 源码类型／显式选项 | 构造点与析构点 |
|---|---|---|
| SIPP `open_list` | `boost::heap::pairing_heap<SIPPNode*, boost::heap::compare<LLNode::compare_node>>` | A4 L110、112；SIPP ctor 未指定该成员初始化器，故零实参默认构造；SIPP 隐式析构时析构 |
| SIPP `focal_list` | `boost::heap::pairing_heap<SIPPNode*, boost::heap::compare<LLNode::secondary_compare_node>>` | A4 L111、113；同上 |
| SpaceTimeAStar `open_list` | `pairing_heap<AStarNode*, compare<AStarNode::compare_node>>` | 继承 73E3 N2 L96、98；A* ctor 未指定该成员初始化器，故零实参默认构造；A* 隐式析构时析构 |
| SpaceTimeAStar `focal_list` | `pairing_heap<AStarNode*, compare<AStarNode::secondary_compare_node>>` | 继承 73E3 N2 L97、99；同上 |

这四处源声明都只显式提供节点指针类型和 compare 选项，没有提供运行时节点范围、初始节点、比较器对象或其他模板选项。默认选项的具体值、零实参调用命中的实际库构造签名，以及 A* 未限定模板名的命名空间绑定，不在本次五个正文中定义；本次没有替它们填写某个系统 Boost 版本的默认值。

后续若要证明“仅构造与析构这些成员不会调用上述随机比较运算符”，所需证据应严格限定为：实际构建所绑定库版本中，上表四个实例的 `pairing_heap` 模板声明及默认选项展开、零实参构造所选函数、`~pairing_heap()`、以及这些函数实际调用的基类／成员构造析构与内部清理函数。若实现的析构确实调用 `clear` 或某个节点处置函数，再沿该实际调用补核；本次不预先虚构具体库版本的内部调用链。比较器对象的初始化、复制、销毁与其 `operator()` 是否被调用应分别记录。

这里缺少的是四个实例的有限生命周期证明及实际库绑定，不是要求审核“所有 Boost”。本次 R0 的软件实例没有向这些成员显式提供搜索节点；但没有库证据就不以“默认应为空”跳过构造／析构中是否调用 Compare 的问题。

### 7.2 其余直接容器，及它们与随机 Compare 的区别

| 持有者／成员 | 本次或继承源码所见类型 | 尚需何种证据才算完整生命周期闭合 |
|---|---|---|
| Agent `path` | `Path`；A1 L10 | Agent 构造体执行前默认构造，析构体结束后销毁；Path 的具体类型／别名定义未包含在本次五对象内，不能凭名字补成已核容器 |
| SIPP `allNodes_table` | `boost::unordered_map<SIPPNode*, list<SIPPNode*>, SIPPNode::NodeHasher, SIPPNode::eqnode>`；A4 L116–117 | 默认构造、默认模板参数、析构及键／值处置；其显式 Hash／Eq 是 A4 L42–85 的节点哈希与相等谓词，不是 LLNode 随机 Compare |
| SIPP `useless_nodes` | `list<SIPPNode*>`；A4 L118 | 默认构造与析构；它没有 LLNode Compare 模板参数；指针元素类型与删除所指对象是不同操作 |
| SpaceTimeAStar `allNodes_table` | `unordered_set<AStarNode*, AStarNode::NodeHasher, AStarNode::eqnode>`；继承 73E3 N2 L101–103 | 实际未限定名绑定、默认构造／析构；显式 Hash／Eq 已在 73E3 头内读到，不是 LLNode 随机 Compare |
| SingleAgentSolver 两个 vector | `vector<int>`；A2 L160、164 | 默认构造／析构及实际库绑定；没有节点比较器参数 |
| BasicLNS 的容器 | `list<IterationStats>`、`vector<double>`、Neighbor 内的 `vector<int>`、两个 `set<pair<int,int>>`、`vector<Path>`，以及 `unordered_map<pair<int,int>,int>`；A1 L27–35、42、67、74 | 默认构造／析构、未限定名及默认模板参数、IterationStats／Path 的定义；未绑定 LLNode Compare，不把它们记为四个堆的随机比较证据 |
| LNS 的外围成员 | `vector<Agent>`，三个 `string`，`PIBTPPS_option`，`PathTable`、`unordered_set<int>`、`list<int>`、`vector<int>`；A5 L23、79–95 | Agent 删除边已核；PathTable、PIBTPPS_option 内部及外围容器／别名定义未在五对象内展开。它们不得被本回执认证成完整系统生命周期 |

本次没有取得库声明，故表内省略的 allocator、hash／equal 默认项等均只登记为“源码未显式提供、须由实际库声明解析”，不伪造具体默认值。SIPP 的 NodeHasher 显式调用 `boost::hash_combine`，A* 的 NodeHasher 使用 `std::hash<int>`（继承 73E3）；这些辅助库调用也不能被当成已经亲见的 LLNode 随机比较调用。

## 8. 本次完成项与剩余精确缺口

已完成：Agent 的 true／false 动态对象选择；经虚基类析构的删除链；SingleAgentSolver 的无搜索构造与默认析构声明；BasicLNS 实际成员范围；两个求解器无自定义析构的声明事实；reset／setter 的有效语句；随机比较器定义与四个堆的类型映射；被注释启发式搜索与真实独立搜索的区分。

尚未闭合的具体项目为：

1. 第 7.1 节四个 pairing_heap 实例在实际绑定库版本中的默认构造／析构及 Compare 调用性；默认选项和 A* 未限定模板名字的实际绑定也待该版本证据。
2. `LNS::~LNS → delete init_lns` 的空／非空状态链，以及非空时 InitLNS 的析构实现；不能由头内默认 nullptr 单独证明全部后续状态。
3. 73E1 源缓存中 loadPaths／commitPath／clearAll 的逐语句调用边，本子任务没有将其回执未列出的 reset 或其他辅助调用自行补入；相关头只有声明这一新增事实已经核清。
4. 第 7.2 节列明的 Agent::Path 成员、外围容器、PathTable／PIBTPPS_option／别名生命周期，以及系统调度到正确初始化、具名 LACAM 分支和退出的调用约束；这些均未由新五对象转为全程序认证。

因此适合主稿使用的新增结论是：**官方 LACAM-only 仍建立 SIPP 对象，提交校验中的 Agent(false) 建立 A* 对象；本次已展开两类对象的显式构造和虚析构删除链，它们没有用户编写的初始化搜索。随机 Compare 的剩余初始化／销毁问题已具体定位到四个堆实例及其实际库实现。** 本回执不把该有限未证库结论扩大成全域失败，也不把它缩写为已证明全生命周期不达。

## 9. 非授权事项与停止点

未使用 skill，未实现／修改算法，未构建，未创建或运行测试，未运行实验／仿真；未读取任何 map／scen／config／agent／task／delay 载荷、桌面、35–38、Q-CAL／Q-CONFIRM。源码类型名、成员名和载荷访问代码不是载荷读取。

所有 shell 命令段均有 `rtk` 前缀，正文散列只在内存／标准输入中计算，未下载仓库或落地源文件。仅以 `apply_patch` 在研究目录新增本 73E4 回执，保持 73E3 与其他报告不变。H、T_delay、B_CAL、B_max、B*、P_active、density N 未赋值，未给范围或默认值。完成本文件 hash／bytes／lines 回执后停止；不补冒失落 73E2。
