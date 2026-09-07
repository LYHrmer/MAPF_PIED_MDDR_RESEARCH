# R0 Boost 版本要求与随机 Compare 合同：有界来源回执

- **NONBALLOT / NO-SKILL**；独立来源任务，不是正式逻辑审查，不是后继候选，不替旧 69E1，不投票。
- R0 官方仓库：`YueZhang-studyuse/LMAPF-delay`；固定 commit：`0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。
- 不修改固定 72、72E4 或任何候选源码。未使用 skill、未派子代理、未实现／构建／编写或运行测试／仿真／调参；未读取本机配置、秘密、载荷、旧 35–38、Q-CAL 或 results。
- 本次只取根 CMakeLists.txt；不递归查依赖树。有关 R0 类型／调用证据复用本代理仍存在的、此前按固定 URL 取得并计算过摘要的源码内存，重新显示必要窗口，没有读取 72E4 文件。
- 本件唯一新文件通过 apply_patch 创建；此前目标路径存在性检查返回不存在。
- 文内版本号仅为源码／文档身份元数据；不是选定部署版本，也不是对任何保护参数赋值。

## 1. 可直接采用的来源结论

1. **R0 有 Boost 版本要求，但没有精确锁定部署版本。** 根 CMakeLists.txt L33 请求 Boost 1.49.0，未使用 EXACT。不能写成“没有版本约束”，也不能写成“部署必为 1.49.0”。
2. **原 FOCAL 比较器被作为决定堆序的谓词实际配置。** 类型与 LNS/PP/SIPP 的条件调用链已闭合；其同键分支每次调用 rand()，不把随机平局值固定在节点或键上。
3. **数学判断不需要运行实验。** 对字段有效、求和无溢出的同一个节点做形式自比较，全部同键判据成立；若该次 rand() 返回偶数，谓词返回 true，直接违反严格弱序的不可自反性。源码没有排除这一允许的返回情形。因此它不能作为一个对合法调用保证严格弱序的实现被认定合格。这个接口性质判断不等于已观察到容器自比较、矛盾比较序列或运行错误。
4. **Boost 官方 1.85.0 只作一个明确版本的条件证据。** 所核该版本正式文档与 Compare 声明规定其为 heap-order 谓词；在本件限定原文中没有找到显式的 StrictWeakOrdering 概念要求或“违反该概念即 UB”的条款，不伪造这种条文。
5. **精确到条件版本的比较调用现在可源证。** 若实际使用本件所取 Boost 1.85.0 头文件、FOCAL 非空并执行成功的 push，push 会合并根与新节点并调用原 Compare；若这些节点的所有比较键相等，则进入原 L93。空堆首次 push 不作这个比较。是否满足这些运行条件仍 UNKNOWN。
6. **尚不能写“R0 已发生 C++ UB”。** 第三方 pairing_heap 的排序关系缺口，与标准库模板的适用要求、语言级 UB 触发机制、具体运行失败，是不同证据层。未找到精确版本显式条款不构成对源比较器行为的正确性背书。

## 2. CMake 到 Boost 的明确约束

[固定根 CMakeLists.txt L30–35](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/CMakeLists.txt#L30-L35) 的有效声明为：

`find_package( Boost 1.49.0 REQUIRED COMPONENTS program_options system filesystem log log_setup)`

L35 将 `Boost_INCLUDE_DIRS` 送入 include_directories；[L63–72](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/CMakeLists.txt#L63-L72) 的非 Python 分支收集直接相关 MAPF-LNS2/LaCAM2 源文件并以 `Boost_LIBRARIES` 链接目标。本件只观察声明，没有配置或构建目标。

CMake 官方 [3.16 FindBoost 文档](https://cmake.org/cmake/help/v3.16/module/FindBoost.html) 明示 version 参数为最低版本或 EXACT 版本；官方 [find_package 文档](https://cmake.org/cmake/help/v3.16/command/find_package.html#version-selection) 进一步区分请求兼容版本与精确匹配，并说明 Config 模式的兼容性由包的版本文件判断。因而：

- “请求最低／兼容版本 1.49.0”有来源；“EXACT 1.49.0”与源文不符。
- 已读根文件没有 Boost 的精确包版本锁、头文件摘要、具体安装前缀或包来源锁定。
- REQUIRED 与组件列表也影响包是否可用；不能仅凭版本参数保证任何给定安装都能配置成功。
- 实际 CMake 版本、查找模式、找到的 Boost 包／头、配置缓存、分发补丁与最终编译采用的文件身份均未核，仍 UNKNOWN。没有读取本机来补这些信息。

根文件 L4 使用 C++14 标准设置；本件因此以官方草案仓库的 n4140 相关条款解释标准库要求的范围，不推断最终工具链／编译模式已得到验证。CMake 其他分支的设置不转为部署选择。

## 3. 一个明确 Boost 版本的正式合同与原文阴性

条件对象为官方 `boostorg/heap` 的 `boost-1.85.0` 标签。选择它是为了取得一个可指认的条件实例，**没有为未来 manifest 选版本**。取得的四个原文对象及其内容摘要见第 8 节。

正式原文所能支持的是：

- [doc/heap.qbk L49–53](https://github.com/boostorg/heap/blob/boost-1.85.0/doc/heap.qbk#L49-L53) 将优先队列描述为按优先级排序、支持访问最高优先级元素与移除它的数据结构。
- [doc/heap.qbk L367–369](https://github.com/boostorg/heap/blob/boost-1.85.0/doc/heap.qbk#L367-L369) 对 compare 的描述是 “Predicate for defining the heap order”。
- [policies.hpp L117–120](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/policies.hpp#L117-L120) 的 Doxygen Compare 声明表达同一作用；实际非 Doxygen 分支 [L29–31](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/policies.hpp#L29-L31) 使用 Boost.Parameter 模板关键字声明。它是配置谓词的接口，不是仅因名字为 compare 就自动成为 ISO 标准库的 Compare 概念声明。
- [pairing_heap.hpp L111–119](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/pairing_heap.hpp#L111-L119) 列出 compare 选项；官方 [1.85.0 pairing_heap 接口页](https://www.boost.org/doc/libs/1_85_0/doc/html/boost/heap/pairing_heap.html) 的 top/push/pop 规定最大元素、加入元素和移除顶端元素的语义。

对取得的四个完整原文逐行检索以下模式：

`\b(?:strict|weak|StrictWeakOrdering|StrictWeakOrderingConcept|BinaryPredicate|BinaryPredicateConcept|BOOST_CONCEPT_ASSERT|requires|Requires|Requirement|requirement|undefined|extract_stable)\b`

strict、weak、上述严格弱序／BinaryPredicate 概念名、BOOST_CONCEPT_ASSERT 在这四个对象中无命中。命中的 requires 是有序迭代器记账的普通描述；undefined 出现在稳定性和修改节点后的更新条款。**这个有界阴性不等于所有 Boost 文档／头文件都没有相关要求，更不等于数学排序关系可以任意变化。** 本件不为追一个期望的条款扩成全 Boost 审计。

### 不可移用的两类表述

[heap.qbk L273–279](https://github.com/boostorg/heap/blob/boost-1.85.0/doc/heap.qbk#L273-L279) 允许非 stable 队列中同优先级节点的弹出顺序未规定。这涉及已由排序关系确定的等价优先级项之间是否保留插入顺序，**不证明一个在同参重复比较或反向比较时可改变关系的随机谓词满足严格弱序**。不能以“队列本来不稳定”替源行为辩护。

[pairing_heap.hpp L429、L468、L500](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/pairing_heap.hpp#L429-L500) 及对应官方接口页中的 undefined-behavior 表述，是节点值更新后未调用规定更新接口的情形。本件没有对该独立前提作触发证明，不能把这个条款无条件贴到 L93 的 rand() 上。

## 4. 原 FOCAL 比较器：数学不满足与接口边界

固定 [SingleAgentSolver.h L81–103](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L81-L103) 依次比较：

`num_of_conflicts → reached_goal_at → g_val+h_val → h_val`

所有这些键相等时，L93 执行 `rand() % 2 == 0`。OPEN 的 [L40–59](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L40-L59) 少一层冲突数键，L51 有同一问题；本节聚焦已明示 LNS/PP 链使用的 FOCAL。

把一次调用记为 `C(p,q;s)`，其中 s 是 C 随机生成器的外部状态。对于一个有效节点 p，形式调用 `C(p,p;s)` 的所有相等判据成立，其返回值依赖该次 rand() 的奇偶性。源码没有“同一对象必须返回 false”的保护，也没有把平局比较固定为某个不随比较调用改变的二元关系。

严格弱序的要求是对其定义域的关系成立，不是“多数比较大概成立”。只要允许的 rand() 返回情形使 `C(p,p;s)` 为 true，就不能把这个实现证明为满足不可自反性的通用 Compare。对两个同键节点，接口也未排除先后两次反向比较都为 true，或同参重复比较给出不同结果；这些只是源码未约束的情形，**不是本件声称实际 libc 已产生的返回序列**。单凭外部状态存在并不使任意比较器违规；这里关键在于外部状态直接决定返回真假，而节点键未变。

C++ 官方草案仓库 [n4140 algorithms.tex L2339–2418](https://github.com/cplusplus/draft/blob/n4140/source/algorithms.tex#L2339-L2418) 给出严格弱序的不可自反性、comp 的传递性和由双向“不小于”定义的 equiv 传递性。数学反例直接针对不可自反性，已经足以说明源码没有满足严格弱序保证；不需要额外实验构造传递性失败轨迹。

这一区分应保留：

- **可判断：** 固定源的随机平局谓词不是一个对全部允许调用保证严格弱序的实现，不能把严格弱序作为已满足的接口性质。
- **尚不能由此判断：** 任意一次具体运行都已执行自比较或得到矛盾比较结果、当前有限调用集合必然出现性质反例、实际部署已经崩溃／错误求解／触发语言 UB。
- **正式 Boost 条款证据边界：** 本件取得的是 heap-order 谓词与优先队列语义声明，没有取得该版本显式命名 StrictWeakOrdering 的条文；不得把数学不满足与“已命中某条未取得的库合同”混写。

## 5. R0 到 FOCAL，再到条件版本的真实比较调用

固定源码的直接构造／调用链：

1. [MAPFPlanner.cpp L11–20](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp#L11-L20) 与 [LNS.h L37–40](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h#L37-L40) 对位为 use_sipp=true 与 PP 重规划。
2. [LNS.cpp L43–45](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L43-L45) 把该布尔量交给 Agent；[BasicLNS.h L6–18](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h#L6-L18) 将其 SingleAgentSolver 指针绑定到新建 SIPP。
3. [LNS.cpp L570–591](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L570-L591) 在 PP 循环条件满足时调用带超时的虚 findPath；[SingleAgentSolver.h L176–179](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L176-L179) 与 [SIPP.h L99–106](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SIPP.h#L99-L106) 确定签名与动态目标。
4. [SIPP.cpp L54–70、L125–133、L169–181](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp#L54-L181) 使用 FOCAL；[L530–535](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp#L530-L535) 的 helper 执行 focal_list.push。
5. [SIPP.h L110–113](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SIPP.h#L110-L113) 将 focal_list 的 pairing_heap Compare 明确配置为 LLNode::secondary_compare_node。

**以下新增调用证据仅以本件取得的 Boost 1.85.0 文件为条件：**

- R0 的该类型没有 stable 选项。[policies.hpp L87–98](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/policies.hpp#L87-L98) 从未指定的该选项导出 false；[stable_heap.hpp L556–565](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/detail/stable_heap.hpp#L556-L565) 将传入的 Compare 和此选项接到 heap_base。这是读取该版本的类型绑定规则，不是对部署增加设置。
- [pairing_heap.hpp L356–364](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/pairing_heap.hpp#L356-L364) 的 push 构造节点后调用 merge_node。
- [L655–661](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/pairing_heap.hpp#L655-L661)：已有 root 时调用 merge_nodes；空堆只记录新 root。
- [L696–703](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/pairing_heap.hpp#L696-L703)：merge_nodes 在两个节点值上调用基类谓词，并按结果决定根与孩子关系。
- [stable_heap.hpp L209–211](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/detail/stable_heap.hpp#L209-L211)：基类谓词直接转发给 value_comp 的 operator()，因此可接到原 LLNode::secondary_compare_node。

所以，比“模板声明可能用到 Compare”更强的**条件命题**现已证实：在这些头文件下，成功向非空 FOCAL push 会作一次此路径的节点比较；若比较键全部相等，会消费 rand()。没有从静态源码得到 FOCAL 在某个实际运行何时非空、键是否相等、比较返回值、总比较次数或某对节点的实际次序。

## 6. 为什么仍不能称为已证实的 C++ UB

官方草案仓库 [n4140 lib-intro.tex L2323–2364](https://github.com/cplusplus/draft/blob/n4140/source/lib-intro.tex#L2323-L2364) 对不满足要求的程序提供组件规定了标准不再施加要求／相关效果未定义的后果，其上下文明确是标准库依赖的替换函数、处理函数和标准库模板实例化等。结合第 4 节标准排序算法条款，可以支持**对适用标准库组件违反其比较器要求**的条件性结论。

本件已经确定的容器是 boost::heap::pairing_heap。所核 push→merge_nodes 路径直接调用用户谓词；其中的 std::swap 交换节点指针，它没有把原谓词转交给 std::sort 或 std::push_heap。因此：

- 不能只因出现 compare 这个名字就把标准库模板要求自动扩大到第三方模板。
- 不能用文档中另一操作的 undefined-behavior 警告，替代本题必须证明的适用前提。
- 不能把“不保证按一个严格弱序排序”直接写成“已证实空指针、越界、算术溢出、数据竞争或其它语言 UB 机制”。本件没有建立这类机制，也没有审计所有下游后果。
- 反过来，**未证实 UB 绝不等于证实安全、正确、可复现或可作为已满足严格弱序契约的原法实现**。本件也没有用“不报错”或“可能工作”替算法背书。

| 层次 | 本件结论 |
|---|---|
| 原源码数学接口 | 不能保证严格弱序；存在直接的不可自反性反例条件，已由有效源码定位。 |
| 配置用途 | 明确是决定 FOCAL 堆序的原 Compare；不是孤立或仅注释定义。 |
| 单版本具体调用 | 在所取 Boost 1.85.0 实现下，成功向非空 FOCAL push 会调用原 Compare；同键则进 L93。 |
| Boost 显式 SWO／UB 条文 | 所读正式文档与四对象中未取得该特定显式条文；不外推为全 Boost 阴性。 |
| 部署版本及精确运行 | UNKNOWN；根 CMake 没有精确锁定，未配置、构建或运行。 |
| 实际 C++ UB／失败 | UNKNOWN；不能由当前证据称已发生，也不能称已排除。 |

本件不修比较器、不提出悄悄修改原法并继续标同固定版本。

## 7. 获取回执、失败与身份边界

- 固定 R0 根 CMakeLists.txt 通过固定 commit 的官方 raw URL 新取得；其余七个 R0 对象复用仍存内存的已核固定源码。
- Boost 1.85.0 pairing_heap 官方接口网页取得成功；同版本 concepts/data_structures/compare 的若干 web URL 返回 cache miss，随后取得同官方标签的 doc/heap.qbk 与三个直接相关头文件，作为实际原文。
- Boost 标签 Git API 的只读网络请求发生 TLS 错误；只读 git ls-remote 同样发生 TLS 错误；web 对 API／tree 也未取得有效元数据。因此 **boost-1.85.0 标签当前所指仓库 commit 未独立解析，UNKNOWN**。本件用官方标签 URL 加下表实际内容指纹固定“读到了什么”，不虚构一个未取得的 commit，也不声称已把计算 blob 与 API 目录元数据交叉验证。
- C++ 官方 WG21 n4140 PDF URL 通过 web 未取得、随后只读请求返回 404。最终成功取得官方 cplusplus/draft 仓库 n4140 标签的两个原文文件；其标签所指仓库 commit 没有另行解析。本件引用原文内容身份，不把镜像页面当原法依赖。
- 首次 C++ 条款提取有两个模式过度转义，未抽到目标窗口；改正后重新取得同标签文件并取出 alg.sorting/res.on.functions，两次 SHA256、bytes、行数一致。未把首次空窗口当作源码阴性。
- 没有保存任何下载源码、PDF、配置或本地测试文件；没有读取环境变量／依赖缓存／本机 Boost 头。读取失败是来源限制，未被替换成推断。

## 8. 完整源码对象身份与实际阅读边界

下表 Git blob 是按所取原始 bytes 计算的 Git blob SHA-1；SHA256 也基于原始 bytes。固定 R0 七个复用对象的摘要与此前实际取得时一致。完整取得或哈希不等于全文语义审计。

| 官方源对象 | 计算的 Git blob SHA-1 | 全文 SHA256 | bytes | 行数 |
|---|---|---|---:|---:|
| [CMakeLists.txt](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/CMakeLists.txt) | `148459bb9542731723e8125bb8d54da6a3ce954b` | `ecdf7e3c889ab8290eb9cc839543c0f281419db957982a03b79ae79da25dc899` | 2790 | 92 |
| [src/MAPFPlanner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp) | `94afb42df1a70f5e312a382e61cf83576fd7360e` | `c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1` | 6125 | 208 |
| [inc/MAPF-LNS2/inc/LNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h) | `5b9ce3ef4aeaf6fcfa88c211c0f536c66f8ae24e` | `c9751aca5f3c305d5da49c3445ec29cb19819655b496de12c522d83d7af7ad91` | 4201 | 119 |
| [src/MAPF-LNS2/src/LNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp) | `1fb0e54f8f2bb00af05de53233ae600774e36f2a` | `0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2` | 53100 | 1486 |
| [inc/MAPF-LNS2/inc/BasicLNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h) | `c22e0b66cc58e9c9ce19d6b161e4f54dabfb4c15` | `9927e17d5c6dd3624ed4e5dc3cc81c20eec854b340ddf4723f93d873a6b526ff` | 2042 | 77 |
| [inc/MAPF-LNS2/inc/SingleAgentSolver.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h) | `c22f59ac763c3bc272a82b5c8e9793a91f5da94a` | `daafdc674f90bbe4b34031b19f2564fb93189f07d7ad15e0927e1574cbb5611f` | 7935 | 226 |
| [inc/MAPF-LNS2/inc/SIPP.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SIPP.h) | `9f2366ad6e8bf4084299b6d3649414394c850694` | `8ebf98b9518844473ac66f6064e5c9810774fe4f7f79fdb7e25fe4c69abd318d` | 5725 | 131 |
| [src/MAPF-LNS2/src/SIPP.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp) | `7f8db084c2d03929f51c28a76a29895fbaaa1a64` | `3cb627fcd4a0ebe2646be9985e58bd16ef5f01ff3fce357ab4584b0045d2e2b7` | 30068 | 680 |
| [doc/heap.qbk](https://github.com/boostorg/heap/blob/boost-1.85.0/doc/heap.qbk) | `827aedaf650c056f8424358a068cd618cb67aa02` | `4f6610e7191d91749560eed0c843ca88df15bf81611f43141e694ab7f73e308b` | 18559 | 422 |
| [include/boost/heap/policies.hpp](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/policies.hpp) | `6a251a9faafdeca593ab45f741d47a67b02ef9d0` | `5d186a313d2281d6504c4b656b069047e3ef0cb81ea873c5df102ac4da20e079` | 4413 | 174 |
| [include/boost/heap/pairing_heap.hpp](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/pairing_heap.hpp) | `c591cc9e80dbce40b351a0f90ab4210d2a2a4a54` | `668543a7a2ab2b4519452a5f841d36f30761cb99b102e3273d999adb3afe9fcd` | 22458 | 715 |
| [include/boost/heap/detail/stable_heap.hpp](https://github.com/boostorg/heap/blob/boost-1.85.0/include/boost/heap/detail/stable_heap.hpp) | `bfec26d63c2b605bb4f47b5cae7baf066c1d8cdc` | `24d78657787040120778df3d60396c1b1c16d6f5babc612431a028b9a387e371` | 14940 | 585 |
| [source/algorithms.tex](https://github.com/cplusplus/draft/blob/n4140/source/algorithms.tex) | `147c55174cb43a3bbc98906cf5ab7b1f8030cec4` | `d066ad0330680cff28cbf3085ee86504eac9a6fa0c7104319f68a5e249ad5580` | 118263 | 4002 |
| [source/lib-intro.tex](https://github.com/cplusplus/draft/blob/n4140/source/lib-intro.tex) | `e8907bb03721d90bf8af1e31587a7334747344ac` | `3befdee69ec7c074ad33921ae62d5353ff823dc1c31b2991d24fd8e75412df9a` | 103198 | 2800 |

本任务的语义阅读／定点检索窗口：

- R0 CMakeLists.txt：L1–92 全文，结论只用 L3–4、L30–35、L63–72；未沿 glob 递归取文件。
- R0 MAPFPlanner.cpp：L11–20；LNS.h：L37–40；LNS.cpp：L7–10、L43–46、L570–572、L589–592。
- R0 BasicLNS.h：L6–18；SingleAgentSolver.h：L40–59、L81–103、L176–179。
- R0 SIPP.h：L88–113；SIPP.cpp：L30–40、L54–70、L125–133、L169–181、L530–535。
- Boost heap.qbk：L30–56、L270–281、L360–376；全文只做第 3 节明确模式与比较／堆序关键词检索。
- Boost policies.hpp：L18–37、L81–110、L112–124；同上全文定点检索。
- Boost pairing_heap.hpp：L38–78、L106–125、L330–367、L651–713，以及 L429/L468/L500 的实际文档命中；同上全文定点检索。未展开其它堆、测试、基准或完整 include 闭包。
- Boost stable_heap.hpp：L99–171、L202–258、L269–290、L553–582；同上全文定点检索。
- C++ n4140 algorithms.tex：定位并阅读 L2339–2418；lib-intro.tex：L452–513、L2323–2402。其余全文仅为提取指定条款定位及计算摘要。
- CMake 官方版本化网页：FindBoost 的调用语法／最低与 EXACT／结果变量说明，find_package 的 basic signature 与 Version Selection。
- Boost 官方版本化网页：1.85.0 pairing_heap 的 Description、比较选项及 top/push/pop/update/value_comp 对应接口段。
- 辅助读过 SGI Strict Weak Ordering 页面和 n4140 的 HTML 呈现窗口；正式结论最终回到上列已实际取得的官方原文，不把 SGI 页面冒充 Boost.Heap 特定合同。

本件只交付来源与静态条件证据，不能当作正式候选审查票或部署验收。

