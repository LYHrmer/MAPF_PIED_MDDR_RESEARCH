# R0 两处随机比较器的容器用途与直接可达性静态回执

- 性质：**NONBALLOT / NO-SKILL**；不是正式审稿、不是旧任务替身，不给候选通过票。
- 官方仓库：YueZhang-studyuse/LMAPF-delay。
- 固定提交：`0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。
- 起始材料：研究目录内 `72E1_R0_CORE_CLOCK_RANDOM_INPUT_INVENTORY_NONBALLOT_RECEIPT_20260906.md`，实际读取 L1–240。
- 本次只读取得必要官方源码至工具内存并计算对象摘要；没有保存源码副本、改变候选、实现、构建、编写或运行测试、仿真、调参或实验赋值。未读取桌面、旧 35–38、受限载荷、结果、skill、审稿或顾问文件。
- 本件创建前执行目标路径存在性检查，返回不存在；唯一新文件为本回执，通过 apply_patch 写入。

## 1. 结论及强度

**两处比较器均确实被用作 Boost pairing heap 的排序谓词，不只是未使用的 struct。已知 PP→SIPP 带超时 findPath 直接接到的是 L93 的 FOCAL 比较器；L51 的 OPEN 比较器有 SIPP::getTravelTime 方法内使用，但本次限定直接来源未找到该方法调用，不能把两者写成同等入口可达。**

| 要区分的命题 | 本次可支持的强度 |
|---|---|
| 比较器可能不满足严格弱序契约 | 有源码层面的具体理由：全部排序键相等时返回依赖外部 C 随机状态的布尔值，而不是由节点键确定的固定关系；不保证不可自反性、方向一致性、传递性或同参重复调用一致性。 |
| 具体比较会发生 | 类型绑定与 FOCAL 的 push/pop/erase 调用均已坐实；对某次输入，哪一对节点实际被比较、是否满足全部同键条件、是否消费 rand()，均没有运行证据。不能把“构造容器”或“push 调用存在”写成“必然进入随机分支”。 |
| 标准意义后果 | ISO 标准库排序算法要求严格弱序；违反适用的标准库前置条件可有未定义行为后果。但这里确定的类型是第三方 boost::heap::pairing_heap，不能不经版本与实际实现核验，直接移植 std::sort/std::priority_queue 条款，宣称这个 R0 已发生 ISO 意义运行 UB。可支持的限定结论是：用于堆排序的关系缺乏严格弱序保证，基于一致 heap order 的正确性保证不能据此直接成立。 |
| 实际运行是否触发 | **UNKNOWN**：没有运行 R0，没有指定运行输入，没有日志、trace、崩溃、错误解或失败复现证据。 |

本件没有修比较器，也不建议将修过的实现暗称为同一固定版本。

## 2. 两处有效比较器及容器类型

在 [SingleAgentSolver.h L40–59](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L40-L59)，`LLNode::compare_node` 依次检查 `reached_goal_at`、`g_val+h_val`、`h_val`；全部相等时，L51 执行 `rand() % 2 == 0`。

在 [SingleAgentSolver.h L81–103](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L81-L103)，`LLNode::secondary_compare_node` 先检查 `num_of_conflicts`，再检查上述键；全部相等时，L93 执行同一随机表达式。这两段是有效代码；上方另有注释掉的历史定义，本件没有把注释定义当实际路径。

由这个实现可以直接说明：若对同一个有效节点做自比较，所有相等判据必然成立，结果却没有保证为 false；对两个同键节点，结果也没有绑定到节点身份或已保存的固定随机键。此为未满足严格弱序保证的静态论证，**不是声称实际容器曾做自比较，或某个具体随机序列已经产生矛盾**。其余返回语句虽使用 >=，但在各自到达分支上对应相等情形已先分流；本件风险依据是上述有效随机平局分支，不是仅凭 >= 字符下结论。

[SIPP.h L6–11、L88–113](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SIPP.h#L6-L113) 确定：

- `SIPPNode` 继承 `LLNode`，其 handle typedef 引用继承的两个比较器。
- `SIPP` 继承 `SingleAgentSolver`。
- `heap_open_t` 为 `boost::heap::pairing_heap<SIPPNode*, boost::heap::compare<LLNode::compare_node>>`，L112 声明 `open_list`。
- `heap_focal_t` 为 `boost::heap::pairing_heap<SIPPNode*, boost::heap::compare<LLNode::secondary_compare_node>>`，L113 声明 `focal_list`。

[lns_common.h L13、L19–20](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lns_common.h#L13-L20) 包含 Boost pairing_heap 头并引入 pairing_heap/compare 名称。这里不是 unordered_map 的 hash/equality 谓词，也不是仅由注释声称“用于 OPEN/FOCAL”。

## 3. MAPFPlanner→LNS→SIPP：构造与 FOCAL 调用闭合

构造关系：

1. [MAPFPlanner.cpp L11–20](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp#L11-L20) 调用 LNS 构造；与 [LNS.h L37–40](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h#L37-L40)、[LNS.cpp L7–10](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L7-L10) 对位，`use_sipp` 传入 true，`replan_algo_name` 传入 PP。
2. [LNS.cpp L43–45](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L43-L45) 将 `use_sipp` 转交 `agents.emplace_back(instance, i, use_sipp)`。
3. [BasicLNS.h L6–18](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h#L6-L18) 的 Agent 持有 `SingleAgentSolver*`；sipp 分支构造 `new SIPP(instance, id)`。
4. [SingleAgentSolver.h L176–179](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L176-L179) 把带超时 findPath 声明为 virtual；[SIPP.h L99–106](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SIPP.h#L99-L106) 提供同签名方法和构造。

调用关系：

- [MAPFPlanner.cpp L75–104、L107–137](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp#L75-L137) 的 LACAMLNS/LACAMLNS2 分支调用 `lns->run()`；L134 另有 `fixInitialSolutionWithLNS2()`。
- [LNS.cpp L96–144](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L96-L144) 中 run 在其预算／迭代／timeout、邻域生成等条件满足后，对 PP 分支调用 runPP；[L445–456](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L445-L456) 的修复方法在非空待处理邻域条件下也调用 runPP。本件没有断言这些条件对任何输入必然成立。
- [LNS.cpp L570–591](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L570-L591) 的 runPP 在剩余代理与时间条件满足时，经 `path_planner` 调用带超时 findPath。结合上述动态类型，目标为 `SIPP::findPath(const ConstraintTable&, double, bool&)`。
- [SIPP.cpp L30–88](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp#L30-L88) 包含前置返回、初始 `pushNodeToFocal(start)`、FOCAL 循环和 pop；[L125–139、L169–182](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp#L125-L182) 在 dominanceCheck 通过时推入后继，并在方法末清理。
- [SIPP.cpp L530–535](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp#L530-L535) 的 `pushNodeToFocal` 真正执行 `focal_list.push(node)`，不向 OPEN 插入；[L537–551、L633–655](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp#L537-L655) 还显示 dominanceCheck 可经 helper 删除 FOCAL 中节点。

所以可成立的是一条**带分支条件的静态调用链**：

`MAPFPlanner::plan → LNS::run / fixInitialSolutionWithLNS2 → LNS::runPP → virtual SIPP::findPath(带超时) → pushNodeToFocal / focal_list.pop / erase → 已绑定的 LLNode::secondary_compare_node → 同键时 L93`。

`use_sipp=true` 本身只证明构造选择，不能跳过 runPP/搜索循环/同键条件而称 rand() 必达。容器内真正进行的比较对、调用次数与自比较情况还取决于实际 Boost 实现和运行状态，本件均未获得。

## 4. L51 的 OPEN 用途：方法内明确，上层入口仍未接通

[SIPP.cpp L453–503](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp#L453-L503) 的 `getTravelTime` 调用 `pushNodeToOpenAndFocal`，并对 `open_list` 执行 top/pop；通过过滤的后继再次进入该 helper。[L521–528](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp#L521-L528) 确认 helper 执行 `open_list.push(node)`。

所以方法内的链为：

`SIPP::getTravelTime → pushNodeToOpenAndFocal → open_list.push / pop → 已绑定的 LLNode::compare_node → 同键时 L51`。

对已取得的 LNS.cpp、MAPFPlanner.cpp、BasicLNS.h、SingleAgentSolver.cpp 做限定 `getTravelTime` 文本查找，没有调用命中。SIPP 中存在公开方法定义与基类虚接口，不等于已知 MAPFPlanner→runPP 链实际调用它。**本件未建立 L51 从该入口的直接可达性，也未证明整个仓库或任意链接程序全局不可达。** 本件没有为找全所有调用者扩大到全仓搜索或构建链接审计。

## 5. LaCAM2 的直接路径与边界

[LNS.cpp L523–541](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L523-L541) 的 getInitialSolution 调用 runLACAM2；[L648–714](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L648-L714) 构造 `LACAMInstance` 后调用自由函数 solve，随后只将返回解转入 agents 的 Path 与 PathTable。本次完整核对该函数体，未见调用 SIPP/findPath/getTravelTime。

[lacam2.cpp L3–9](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/lacam2.cpp#L3-L9) 中自由 solve 构造 LaCAM 的 `Planner` 并调用 `planner.solve`。[planner.hpp L28–35、L38–71、L74–114](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/planner.hpp#L28-L114) 显示其独立 LNode/HNode/Planner 类型，而非 LLNode/SIPP 继承链。

[planner.cpp L127–147](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp#L127-L147) 的高层 OPEN 是 `std::stack<HNode*>`，不使用排序比较器。[L88–91](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp#L88-L91) 与 [L393–421](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp#L393-L421) 的两个 std::sort 使用本地 lambda：前者读 priorities，后者读距离与 tie_breakers；后者的随机 tie_breaker 赋值发生在 sort 调用前的候选循环，lambda 内没有本件两处 rand()。这只是在识别不同比较器，不是对 LaCAM 其他排序逻辑的完整正确性背书。

在固定 planner.cpp 全文定点查找 `SIPP|SingleAgentSolver|LLNode|getTravelTime|findPath|pairing_heap|compare_node` 无命中。所核**直接 LaCAM2 求解路径未接到本件两处比较器**；采用 LaCAM 初解后，再返回上层 LNS 执行 PP 的组合路径，仍可走第 3 节 FOCAL 链，不能因名称含 LaCAM 就排除它。本件没有审计其他外部头、完整动态调用闭包、预处理宏或链接替换，所以不声称无条件的全程序不可达证明。

## 6. 严格弱序与标准后果的来源边界

- C++ 工作草案 [alg.sorting.general](https://eel.is/c++draft/alg.sorting.general) 要求相应标准算法的 Compare 诱导严格弱序，给出不可自反性以及 comp/equiv 的传递性条件。
- 工作草案 [structure.specifications](https://eel.is/c++draft/structure.specifications#3.4) 说明违反适用的前置条件会产生未定义行为。
- Boost 官方 [Data Structures / Configuration](https://www.boost.org/doc/libs/latest/doc/html/heap/data_structures.html#heap.data_structures.configuration) 将 compare 定义为决定 heap order 的谓词；[Concepts & Interface](https://www.boost.org/doc/libs/latest/doc/html/heap/concepts.html) 将优先队列规定为按优先级有序并返回最高优先级项的数据结构。

以上文档实际通过 web 取得。Boost 所读通用文档没有在该页逐字写出 pairing_heap 的 StrictWeakOrdering 前置条件；**本件不伪造这种逐字条款**。数学上，随机比较没有保证固定严格弱序；工程上，它已被用来决定堆序。二者不能自动升级成“已核明 R0 所用 Boost 版本的某条前置条件、并证明该次运行发生标准 UB”。

本次没有读取或锁定构建实际使用的 Boost 头、版本与工具链。因此“精确到该 Boost 版本的契约措辞、比较调用机制与后果分类”仍为 UNKNOWN。没有发现的调用或失败不等于证明不存在。

## 7. 官方对象身份与阅读范围

四个 raw URL 首次经 web 打开返回 cache miss。第一次沙箱网络请求返回 PermissionError；随后按沙箱流程请求获准的只读联网，成功重新取得下表所有固定 R0 对象。所有 Git blob SHA-1、全文 SHA256、bytes、行数均由取得的原始 bytes 当场计算，并与 72E1 所列对应对象逐项一致；BOM 计入 bytes，不影响原始行号。完整获取仅用于身份校验与限定检索，不等于全文语义审计。

| 固定文件 URL | Git blob SHA-1 | 全文 SHA256 | bytes | 行数 |
|---|---|---|---:|---:|
| [inc/MAPF-LNS2/inc/SingleAgentSolver.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h) | `c22f59ac763c3bc272a82b5c8e9793a91f5da94a` | `daafdc674f90bbe4b34031b19f2564fb93189f07d7ad15e0927e1574cbb5611f` | 7935 | 226 |
| [inc/MAPF-LNS2/inc/SIPP.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SIPP.h) | `9f2366ad6e8bf4084299b6d3649414394c850694` | `8ebf98b9518844473ac66f6064e5c9810774fe4f7f79fdb7e25fe4c69abd318d` | 5725 | 131 |
| [src/MAPF-LNS2/src/SingleAgentSolver.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SingleAgentSolver.cpp) | `bbbc5d1745a8c649ddb29ecbc27122ba92f0a6ef` | `ef3f96da47b9fdd830e4aafff90677f85168370e3ae2fdbb0b402555d4539d30` | 6545 | 176 |
| [src/MAPFPlanner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp) | `94afb42df1a70f5e312a382e61cf83576fd7360e` | `c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1` | 6125 | 208 |
| [src/MAPF-LNS2/src/LNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp) | `1fb0e54f8f2bb00af05de53233ae600774e36f2a` | `0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2` | 53100 | 1486 |
| [inc/MAPF-LNS2/inc/LNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h) | `5b9ce3ef4aeaf6fcfa88c211c0f536c66f8ae24e` | `c9751aca5f3c305d5da49c3445ec29cb19819655b496de12c522d83d7af7ad91` | 4201 | 119 |
| [src/MAPF-LNS2/src/SIPP.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp) | `7f8db084c2d03929f51c28a76a29895fbaaa1a64` | `3cb627fcd4a0ebe2646be9985e58bd16ef5f01ff3fce357ab4584b0045d2e2b7` | 30068 | 680 |
| [inc/MAPF-LNS2/inc/lns_common.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lns_common.h) | `3bddf54ab74388904064a60a92346883a52c10cb` | `8994fbaf6e022f7b233b7015741ae277d5773f3c84665845ecc654b44a51ccf6` | 2890 | 102 |
| [inc/MAPF-LNS2/inc/BasicLNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h) | `c22e0b66cc58e9c9ce19d6b161e4f54dabfb4c15` | `9927e17d5c6dd3624ed4e5dc3cc81c20eec854b340ddf4723f93d873a6b526ff` | 2042 | 77 |
| [inc/MAPF-LNS2/inc/lacam2/planner.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/planner.hpp) | `48ec12187373e87d6a233bfebea5eaf8b26c9304` | `8e7c6b7221828ef17a73730a3a33c39d5fcc9ccd9f73a6697c7434162ae7312c` | 3850 | 132 |
| [src/MAPF-LNS2/src/lacam2/lacam2.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/lacam2.cpp) | `75ee58f4e1adb46ad3b26991cc212929bbff5f60` | `107bdd83cef76baf86831c0a0f3c421d64e65c36381494d7438dfb1f6b1f2f05` | 464 | 10 |
| [src/MAPF-LNS2/src/lacam2/planner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp) | `4f46f988d2c16f09c5a6f65bb9cd70e8e01aa483` | `8d2fa9131f0691b109a00dd6267b3b48f80df7778643daeb806ff82e20fe2789` | 19115 | 616 |
| [inc/MAPF-LNS2/inc/lacam2/lacam2.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/lacam2.hpp) | `b12113c7e263ac570f53f0af533ec86de9a8bb4d` | `64bdb7cc7b0c0d439bd3dc5a029db70102a1e538b21208b8b3ffb129dce1bfa9` | 481 | 13 |

定点语义核对范围（其余全文仅保留于内存或用于上述限定关键词检索）：

- SingleAgentSolver.h：L1–125、L161–226。
- SIPP.h：L1–131。
- SingleAgentSolver.cpp：L1–90；没有把其中另一个局部 Node 比较器扩展为本件新审计议题。
- MAPFPlanner.cpp：L1–155，重点是构造参数对位和 LACAM/LACAMLNS/LACAMLNS2 的分支方法调用。
- LNS.h：L1–62 与构造／方法声明检索命中。
- LNS.cpp：L1–158、L445–475、L496–610、L648–741，重点见本件具体引文；没有将显示窗口内无关常量转为实验配置。
- SIPP.cpp：L30–88、L125–139、L169–182、L453–555、L633–680；另外全文检索 findPath/getTravelTime、OPEN/FOCAL 操作与 helper 名称，历史注释命中单列识别。
- lns_common.h：include、using 与 boost/heap/compare 的定点命中，核心 L13、L19–20。
- BasicLNS.h：L1–58，核心 Agent L6–18。
- lacam2/planner.hpp：L1–115。
- lacam2/lacam2.cpp：L1–10；lacam2/lacam2.hpp：L1–13。
- lacam2/planner.cpp：L1–14、L83–98、L127–147、L389–443，以及本件第 5 节明确列出的全文定点标识符检索。

这些是文本与类型／构造／直接调用关系证据，不是 C++ AST、编译器、链接器或运行时验证。

