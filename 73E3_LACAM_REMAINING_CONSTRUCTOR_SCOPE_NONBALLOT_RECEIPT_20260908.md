# 73E3：R0 LACAM 剩余构造范围的有界静态来源回执

日期：2026-09-08。性质：固定来源、四个新增源对象完整阅读、NONBALLOT；不是正式审查，不替代原 69E1／69E2。

## 1. 本次结论

**三种算法枚举值确实互异；BasicLNS 与 SpaceTimeAStar 的本次亲见构造定义均为空函数体，所见显式初始化语句没有调用搜索、OPEN／FOCAL 的 push／pop 或随机比较器。** 但这只关闭枚举声明和这些显式语句层面的缺口，不能认证整个 LACAM-only 程序生命周期不执行随机比较器。

具体而言，BasicLNS 构造定义只显式初始化四个成员；SpaceTimeAStar 构造定义显式调用 `SingleAgentSolver(instance, agent)`，随后是空函数体。SpaceTimeAStar 类未声明自定义析构函数，配套源文件也没有该类的析构定义；不能据此省略其隐式成员／基类析构。本次没有读取 SingleAgentSolver、Agent、BasicLNS 头文件或 Boost 容器实现，因此这些更下层边仍未闭合。

本次亲见 SpaceTimeAStar 的 OPEN／FOCAL 操作存在于独立搜索及辅助成员函数中。不能把“类里存在这些函数”当成“构造已经调用这些函数”，也不能把“显式构造体没有调用”当成“所有隐式初始化、基类、析构、调度和外部调用都不会进入它们”。

## 2. 与 73E1、旧任务的关系

本次仅先完整读取本地 [73E1 来源回执](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73E1_R0_PURE_LACAM_ENTRY_DOMAIN_BOUNDED_SOURCE_NONBALLOT_RECEIPT_20260907.md) 作导航。以下属于继承信息，不是本次重新取得的源正文：官方 `--mapfPlanner 1` 映射到具名 LACAM 分支；该分支的已读显式选路不调 `LNS::run()`／`runPP()`，而经 `getInitialSolution()` 进入 `runLACAM2()`；初始化仍建立 LNS 对象；`validateCommitSolution` 中还有临时 `Agent(..., false)`。

73E1 已明确保留 Agent 构造、求解器基类、头文件、系统调度、库生命周期等未核边。本次不把 73E1 的六个源对象计作本次亲见，不沿用其散列冒充此次取得，也不读取第五个对象来填满依赖闭包。特别是“临时 Agent(false) 如何选择具体求解器”没有由本次四对象独立证明；下面对 SpaceTimeAStar 生命周期的分析以确实进入该构造的调用点为条件。

本任务编号为新的 **73E3**。交接说明旧 `/root/construct73_monotone_prefix_control` 已不可查询、其约定 73E2 回执不存在；这些是任务交接信息，本次没有另行核验旧代理状态，也没有补建旧编号文件或声称旧任务完成。本文件只承担本次四对象新增补核。

## 3. 固定来源、读取范围与身份核验

唯一仓库为 `YueZhang-studyuse/LMAPF-delay`；每次源与目录请求均显式固定完整 commit `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。源文件通过 GitHub 连接器 `fetch_file` 完整取得，未指定行裁剪，正文只保留在工具内存；没有下载源仓库或落地源码文件。

导航中的候选路径有四次 404：`src/MAPF-LNS2/inc/SpaceTimeAStar.h`、`src/MAPF-LNS2/include/SpaceTimeAStar.h`、`inc/MAPF-LNS2/SpaceTimeAStar.h`、`include/MAPFPlanner.h`。这些请求没有返回源正文。为确定实际布局，仅另读固定 ref 的三个单层目录元数据：`src/MAPF-LNS2`、`inc`、`inc/MAPF-LNS2`，没有递归列仓库，也没有打开其中其他文件。实际枚举头为 `inc/MAPFPlanner.h`；实际 SpaceTimeAStar 头为 `inc/MAPF-LNS2/inc/SpaceTimeAStar.h`。

以下 Git blob SHA-1 均先由 GitHub 返回，再对同一本次完整 UTF-8 正文独立计算 `SHA1("blob " + 字节数 + NUL + 正文字节)`，四项全部一致；SHA256、字节数和行数也对这份原始字节流计算。散列命令只把正文作为标准输入数据交给校验代码，不运行源代码。逻辑行以 LF 分隔；以下四个文件均以 LF 结尾，逻辑行数等于 LF 数。

| ID / 本次完整对象 | Git blob SHA-1：返回＝重算 | 完整正文 SHA256 | bytes | 逻辑行 / LF | 实际完整阅读 |
|---|---|---|---:|---:|---|
| [N1 · src/MAPF-LNS2/src/BasicLNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/BasicLNS.cpp) | `c0c3ca34fb0f1c55cb67b0693de9e42d5b6503cf` | `662f58b4c8241c97933ee1272cf0d13f1733a1dbd9a120db7b620dea84e793ba` | 731 | 24 / 24 | L1–24 全文 |
| [N2 · inc/MAPF-LNS2/inc/SpaceTimeAStar.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SpaceTimeAStar.h) | `cdb96d96e01ae5efa43688019972efa37df01834` | `ef1416a0098f08a17606d734b77f3722a61c3984f795d17d681cdef1dd937909` | 4052 | 112 / 112 | L1–112 全文；保留 UTF-8 BOM |
| [N3 · src/MAPF-LNS2/src/SpaceTimeAStar.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SpaceTimeAStar.cpp) | `1712e6d081337461437e3458c40fdcb8ef3de8ef` | `4ccef3b2b34a964bd5377e6b742876f371b4fa553d3aa458926c56b2f6f485ac` | 10923 | 300 / 300 | L1–300 全文 |
| [N4 · inc/MAPFPlanner.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPFPlanner.h) | `68fbfd7a13d2a1513c6634d41d0dca5133740aeb` | `d25fbcb08b6d80b4f03234b4f7c3c08c553d7074a7e12c47fee86d336409633e` | 971 | 42 / 42 | L1–42 全文 |

实际新增源正文总量为 **16677 bytes、478 逻辑行、恰好四个对象**。阅读包含所有注释和空白行；工具显示时按 LF 切分产生的尾部空字符串不额外计一行。完整阅读强度限于四对象，不等于传递依赖闭合。

原始内容的不可变 URL（全部固定同一完整 commit）：

- [N1 原始正文](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/BasicLNS.cpp)
- [N2 原始正文](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SpaceTimeAStar.h)
- [N3 原始正文](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SpaceTimeAStar.cpp)
- [N4 原始正文](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPFPlanner.h)

## 4. BasicLNS 构造与随机调用的准确位置

N1 L2–3 为完整的 `BasicLNS::BasicLNS` 定义。显式初始化列表包含 `instance`、`time_limit`、`neighbor_size`、`screen`；函数体为空。该定义未显式调用任何搜索函数、SpaceTimeAStar、OPEN／FOCAL 操作或比较器。[N1 L2](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/BasicLNS.cpp#L2)

N1 L5–24 的 `rouletteWheel()` 是另一个成员函数，L16 调用 `rand()`，后面根据累加阈值选择邻域。构造定义没有调用它。这一随机调用不是该文件里的堆比较器定义，不能把它归入“构造时随机比较”。[N1 L5](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/BasicLNS.cpp#L5)

N1 包含 `BasicLNS.h`，但该头不在本次四对象内。因此本次没有亲见 BasicLNS 的完整成员类型、默认成员初始化器、基类声明或析构声明。不能用空构造体证明其所有隐式初始化／析构没有其他工作，也不能仅凭本文件没有 `SpaceTimeAStar` 字样证明整个 BasicLNS／派生 LNS 生命周期从不建立单体求解器。

## 5. SpaceTimeAStar 的构造、析构和堆操作

N2 L66 表明 SpaceTimeAStar 继承 SingleAgentSolver。N2 L91–92 的构造定义显式转入 `SingleAgentSolver(instance, agent)`，随后为空函数体。N2 L95–103 声明 OPEN、FOCAL 两个 `pairing_heap` 成员及 `unordered_set` 节点表；堆类型分别绑定 `compare_node` 与 `secondary_compare_node`。这是容器／比较器类型存在的亲见证据，不等于比较器调用发生。[N2 L66](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SpaceTimeAStar.h#L66)、[N2 L91](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SpaceTimeAStar.h#L91)

SpaceTimeAStar 完整类声明（N2 L66–112）没有自定义析构声明，N3 全文没有该类的析构定义。依据 C++ 类生命周期规则，应考虑隐式析构及成员／基类的析构；不能补造一个显式析构体，也不能把 `releaseNodes()` 当作自动调用的析构函数。N2 L35 的空析构属于 **AStarNode**，不是 SpaceTimeAStar。

| 本次亲见成员 | 位置 | 相关操作与调用边界 |
|---|---|---|
| SpaceTimeAStar 构造 | N2 L91–92 | 仅显式调用基类构造；没有显式调用下列搜索／辅助成员，没有直接 `rand()`、堆 push／pop 或比较器调用 |
| `findPath(const ConstraintTable&)` | N3 L23–189 | L45 首次 FOCAL push；L51–52 top／pop；L154、172 继续 push；L179 update；L187 调 `releaseNodes()` |
| `getTravelTime(...)` | N3 L192–254 | L198 OPEN push；L203 top／pop；L233 push；L243 increase；L249 调 `releaseNodes()` |
| `popNode()` | N3 L256–263 | L258 FOCAL top／pop，L259 OPEN erase |
| `pushNode(...)` | N3 L266–273 | L268 OPEN push；L272 条件性 FOCAL push |
| `updateFocalList()` | N3 L276–289 | L278 OPEN top，L285 条件性 FOCAL push |
| `releaseNodes()` | N3 L292–299 | OPEN clear、FOCAL clear、删除节点、节点表 clear；自身没有显式 search、push／pop 或 `rand()` |

上表区分有效语句与注释：例如 N3 L68–104 的目标节点候选操作是被注释掉的旧代码，未计作有效 FOCAL push／update。[N3 搜索](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SpaceTimeAStar.cpp#L23)、[N3 OPEN 搜索](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SpaceTimeAStar.cpp#L192)、[N3 清理](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SpaceTimeAStar.cpp#L292)

N2／N3 中没有直接 `rand()` 调用；两种堆比较器的定义则不在这两个正文里。对“构造／析构是否会随机比较”的本次答案是：**显式构造语句没有这种调用，自定义析构没有声明；基类和库容器的隐式生命周期是否调用相关逻辑仍未独立核实。** 本次未把比较器名字、默认容器经验或 73E1 的未核边换算成全程序不达证明。

## 6. 枚举互异与顶层析构

N4 L8 亲见无显式赋值的顺序声明：`LACAM`、`LACAMLNS`、`LACAMLNS2`、`ALGO_COUNT`。依据 C++ 枚举的默认递增规则，三种算法的底层整数值依次为 0、1、2，彼此互异；计数项为 3。这些是源声明的值，不是实验参数。本次因此消除了 73E1 第 4／5 节关于“三种具名枚举可能同值”的保留条件。[N4 L8](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPFPlanner.h#L8)

73E1 所继承的 CLI 类别值 `1` 被显式映射到 `mapf_algo::LACAM`，而枚举 LACAM 的底层值为 0；这是两个不同层面的编码，不能直接拿 CLI 数字与枚举整数比较来改写映射。在初始化及调度正确、`algo` 不在分支间被另行改变的条件下，单个 `algo` 值不能同时等于这三种枚举，从而支持 73E1 的具名分支排他解释。正确调度、对象存活和状态变更的完整证明仍不是本次四对象的结论。

N4 L17 还亲见 MAPFPlanner 的虚析构函数依次 `delete env`、`delete lns`。这说明顶层析构存在对子对象的清理边；不能把选择 LACAM 模式说成不再涉及 LNS 对象析构。LNS／Agent／单体求解器的析构链和指针所有权没有在本次范围内完整展开。[N4 L17](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPFPlanner.h#L17)

## 7. 可供主稿采用的边界

| 问题 | 本次可采用的结论 | 仍不能声称的内容 |
|---|---|---|
| 三个 algo 值是否互异 | 是；本次亲见声明并按 C++ 规则解释 | 不能顺带确认完整初始化／运行时调度 |
| BasicLNS 的显式构造是否调搜索或随机比较 | 所读定义没有这些显式调用；`rouletteWheel()` 的 `rand()` 位于另一成员 | 默认成员初始化、头内定义与析构闭包未核 |
| 确实进入 SpaceTimeAStar 构造时是否显式搜索或 push／pop | 构造只显式转基类，空函数体 | SingleAgentSolver 与库容器初始化未核 |
| SpaceTimeAStar 析构是否显式调搜索或堆操作 | 完整类没有自定义析构声明；不能虚构显式调用 | 隐式成员／基类析构和比较器调用性未核 |
| 临时 Agent(false) 是否建立 SpaceTimeAStar | 本次仅继承 73E1 关于临时 Agent(false) 的存在 | Agent 选路／释放实现不是本次亲见 |
| 官方 LACAM-only 全生命周期是否从不执行随机比较器 | **UNKNOWN，未作全域阴性确认** | 不能由具名 plan 选路或本次空构造体推得全程序结论 |

主稿可将结果表述为：“73E1 已核显式 LACAM 搜索选路；73E3 新核三模式枚举互异，并确认 BasicLNS／SpaceTimeAStar 所见显式构造没有搜索及 OPEN／FOCAL 操作。求解器基类、Agent、隐式容器生命周期和调度仍在未闭合边界内。”这不授予‘全程序无 SIPP 对象／随机比较器’的结论，也不构成标准库比较关系契约证明。

## 8. 非授权事项与停止点

本次未使用任何 skill，未实现或修改算法，未构建，未创建或运行测试，未启动实验或仿真；没有读取 map／scen／config／agent／task／delay 载荷、桌面材料、35–38、Q-CAL／Q-CONFIRM。源文件中的相关类型或方法名属于源对象正文，不等于读取那些载荷。

shell 每个命令段均以 `rtk` 前缀执行；仅以 `apply_patch` 新增本研究目录内的本回执，未编辑其他文件。未赋值 H、T_delay、B_CAL、B_max、B*、P_active、density N，未给范围或默认值。73E3 是新增 NONBALLOT 有界来源回执，不是正式审查，不替原 69E1／69E2，不补冒旧 73E2；完成本文件的字节／行数／SHA256 回执后停止。
