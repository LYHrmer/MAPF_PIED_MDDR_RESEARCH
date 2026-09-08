# 73E1：R0 纯 LaCAM 选择入口的有界静态来源回执

日期：2026-09-07。性质：固定来源、六对象完整阅读、NONBALLOT。未启动原法，未确认全程序域，不替代缺失的 69E1。

## 1. 结论与“纯”的界限

**固定 R0 源码确实提供有效的 `--mapfPlanner 1` 类别选择器，主入口将其描述为 `LACAM only`。** 它写入 `planner->mapf_planner`，初始化代码对应 `mapf_algo::LACAM`；该具名分支的初始规划、失败重试与后续修复都显式转向 LaCAM2 路线，没有在该分支体内调用 `LNS::run()` 或 `runPP()`。这是原源已有的选择接口，不需要为得到这一具名分支而静默改源。[主入口 O4](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp#L53)、[Planner O1](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp#L27)

但它仍复用 `LNS` 对象和配套数据结构；LaCAM 实现自身仍使用随机化。**六对象证据不能认证“整个程序、整个生命周期绝不执行任何 LNS/SIPP 随机比较器”。** 未读的枚举声明、Agent/求解器构造、inline 方法、调度器、依赖和构建入口仍未闭合。正确的有界结论是“官方提供 LaCAM-only 选路模式；所读具名分支及其展开的显式选路链绕过 LNS/PP 搜索分支”，不是“全程序无 LNS 类型、无 SIPP 对象、无随机、无未核库契约”。

本报告把“官方已支持的模式选择”“需要另名登记的改源适配”“尚未核实的全域声明”分开。若根任务需要后一个强声明才能采用该模式，目前应维持 UNKNOWN，不能用前一个较弱事实填补。

## 2. 授权范围、导航与实际读取

唯一目标仓库为 `YueZhang-studyuse/LMAPF-delay`，唯一允许 ref 为完整 commit `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。本次所有 GitHub 请求显式固定该 ref，未读默认分支、其他仓库或其他 commit。

本地只先检查新报告不存在，并读取 `72E1_R0_CORE_CLOCK_RANDOM_INPUT_INVENTORY_NONBALLOT_RECEIPT_20260906.md` 的标题索引及 L44–85 文件身份表作为导航。没有把其中旧搜索结果、比较器结论或身份表散列当成本次亲见源证据；下表源内容、blob 和散列均由本次固定 GitHub 对象另行获得和校验。

实际选取顺序：先核 `MAPFPlanner.cpp` 的模式分支，再沿 `LNS` 调用核完整实现；核导航中的旧 `lns_driver.cpp` 发现其入口全部注释，随后为追踪模式字段来源定点核 `src/driver.cpp`；最后沿 `runLACAM2 → solve → Planner::solve` 核两个 LaCAM2 实现对象。总计恰好六个源对象，无目录递归、无仓库下载。

六次正文均通过官方 GitHub 连接器 `fetch_file`、固定 commit、完整文件返回取得，正文只保留于本次内存。没有创建源代码文件。未读任何 config/map/agent/task/delay 载荷正文；主入口源码包含载荷读取代码和注释示例不等于本次读取或使用了那些文件。

未使用任何 skill，未运行、构建或测试 R0，也未运行实验或仿真。源正文仅以数据形式送入 `printf`/散列工具核验字节；shell 每段均带 `rtk`。本地新增仅本报告，编辑仅用 `apply_patch`。

## 3. 六个对象的完整身份与阅读强度

下表“行”指逻辑文本行；末尾无 LF 的最后一行仍计一行。Git blob 列先由 GitHub 返回，再对本次完整正文独立计算 `SHA1("blob " + UTF8字节数 + NUL + 原始正文)`，六项均相同；SHA256 对同一完整原始字节流独立计算。

| ID / 固定对象 | Git blob SHA-1（返回值＝独立重算） | 完整正文 SHA256 | bytes | 逻辑行 / LF 数 | 完整阅读强度 |
|---|---|---|---:|---:|---|
| [O1 · src/MAPFPlanner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp) | `94afb42df1a70f5e312a382e61cf83576fd7360e` | `c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1` | 6125 | 208 / 208 | L1–208 全文，包括注释与空行 |
| [O2 · src/MAPF-LNS2/src/LNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp) | `1fb0e54f8f2bb00af05de53233ae600774e36f2a` | `0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2` | 53100 | 1486 / 1486 | L1–500、501–1000、1001–1486，连续完整展开，无缺段 |
| [O3 · src/MAPF-LNS2/src/lns_driver.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lns_driver.cpp) | `9743c96f157b10895fcbb63155c1f5116644ec83` | `65745a880ce5d3865039c03b59fafe5ebe568232fe7e05027119e268935fad8e` | 16288 | 377 / 376 | L1–377 全文；保留 UTF-8 BOM，末尾无 LF |
| [O4 · src/driver.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp) | `b75764cc26c2374ce51dabb94e13a138e50f166f` | `3198636d1114e4901c9aae48d549787c9fb3bc3a0bdfd49b6445d81bb5fc4f44` | 6664 | 172 / 172 | L1–172 全文，包括主入口和参数赋值 |
| [O5 · src/MAPF-LNS2/src/lacam2/lacam2.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/lacam2.cpp) | `75ee58f4e1adb46ad3b26991cc212929bbff5f60` | `107bdd83cef76baf86831c0a0f3c421d64e65c36381494d7438dfb1f6b1f2f05` | 464 | 10 / 10 | L1–10 全文 |
| [O6 · src/MAPF-LNS2/src/lacam2/planner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp) | `4f46f988d2c16f09c5a6f65bb9cd70e8e01aa483` | `8d2fa9131f0691b109a00dd6267b3b48f80df7778643daeb806ff82e20fe2789` | 19115 | 616 / 615 | L1–330、331–616，连续完整展开；末尾无 LF |

实际读取总量为 101756 bytes、2869 逻辑行、六个固定源对象。行号复核使用同一已取得内存正文，没有追加第七个对象。完整阅读强度只针对这六个源文件，不能换算成依赖闭包、构建验证或全程序认证。

## 4. 有效入口参数与字段映射

有效选择器片段为 **`--mapfPlanner 1`**。这里 `1` 是源代码已有的离散算法类别标识，用于回答确切入口问题，不是本次选择的实验参数值；没有构造完整运行命令或绑定任何载荷。

| 映射层 | 亲见位置 | 本次能确认的事实 |
|---|---|---|
| 参数注册 | O4 L36–55，尤其 L53 | 有效 `main` 中注册整数选项 `mapfPlanner`；帮助串把类别 `1` 描述为 `LACAM only` |
| 解析 | O4 L59–68 | `parse_command_line` 写入 `vm`，随后 `po::notify(vm)` |
| 字段赋值 | O4 L107 | `planner->mapf_planner = vm["mapfPlanner"].as<int>()` |
| 模式设定 | O1 L27–32 | `mapf_planner == 1` 对应 `algo = mapf_algo::LACAM`；其他列出的类别分别指向 `LACAMLNS` 和 `LACAMLNS2` |
| 具名选路分支 | O1 L48–73 | `algo == mapf_algo::LACAM` 的分支体只采用 LaCAM 初始/重试/修复路线 |

O4 对算法模式的来源是命令行 `vm["mapfPlanner"]`，没有在所读主入口中看到从输入 JSON 的同名字段设置它。因此本报告确认 CLI 路径，不发明某个未读 config 文件里的可用字段。O4 还将规划对象交给系统对象并在 L162 调用 `system_ptr->simulate(...)`；该调度方法的实现未读，不能把它到 `initialize/plan` 的运行时调用桥说成已经亲见。

O1 的三种算法分支是独立 `if`，不是同一个 `else if` 链。初始化映射明确，但枚举声明所在 header 不在六对象内；将三种具名分支视为互斥，还依赖这些枚举值确实互异这一未在本次正文中核实的声明事实。主入口帮助与分支意图支持这种模式解释，却不替代声明核验。下节把这一条件显式保留，不以 C++ 枚举名称不同自动证明值不同。

## 5. 具名 LaCAM 分支的全部显式选路链

在 Planner 按其接口被正确初始化和调度、且三种模式枚举互异的条件下，所读 `mapf_algo::LACAM` 具名分支覆盖以下全部布尔情形。其证据不只来自一次成功初始化：

| `plan` 中的情形 | O1 直接调用 | 在 O2 中展开后的选路 |
|---|---|---|
| `initial_run` | L53–58：准备 dummy 信息，然后 `getInitialSolution()` | O2 L523–542：直接 `runLACAM2()`；成功/失败返回，无 PP/LNS fallback |
| 非首次且 `!initial_success` | L60–65：`clearAll("Adaptive")` 后 `getInitialSolution()` | 同上，重新走 `runLACAM2()` |
| 非首次且已有初始解 | L67–71：`fixInitialSolutionWithLaCAM()` | O2 L496–521：邻域非空或已有碰撞标记时 clear 后 `getInitialSolution()`；否则沿现有解返回，不调用其他规划器 |

核心直接调用链为：

```text
MAPFPlanner::plan [具名 LACAM 分支]
  ├─ 初始/失败重试 → LNS::getInitialSolution
  └─ 后续 → LNS::fixInitialSolutionWithLaCAM
                 ├─ 无修复需要：保留已有路径
                 └─ 有修复需要 → LNS::getInitialSolution
LNS::getInitialSolution
  → LNS::runLACAM2
  → solve(instance, LACAMInstance, ..., commit, ..., deadline, MT, ...)
  → Planner(instance, ...)
  → planner.commit_window = commit
  → Planner::solve
  → expand_lowlevel_tree / get_new_config / funcPIBT 等所读成员实现
```

O2 L648–714 亲见 `runLACAM2()` 建立 `LACAMInstance`、随机引擎与 deadline，调用 `solve`，再把其返回的联合配置转换为 agents 路径和 path table 项。O5 L3–10 亲见 `solve` 构造 `Planner`、赋 `commit_window` 并转入 `Planner::solve`；O6 L127–264 为实际搜索主函数。以上均是固定 R0 内部对象，没有更换上游仓库。[O2 调用点](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L648)、[O5 包装入口](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/lacam2.cpp#L3)、[O6 搜索](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp#L127)

O1 的该分支确有 `setIterations(0)` 调用，但本次没有读取 setter 的 header/inline 实现。因此“绕过 LNS 搜索循环”的主要亲见证据是该分支没有调用 `LNS::run()`，而不是假设 setter 已被完整核验、仅凭写了零就宣布所有 LNS 行为消失。

O2 的 `getInitialSolution()` 本体直接调用 `runLACAM2()`，没有根据 `init_algo_name` 字符串再选择其他算法。因此不能把构造参数里的字符串名称、旧注释中的 `initAlgo` 选项或文件名当成另一个已经证实的有效选路开关。

## 6. 哪些搜索路线被绕过，哪些包装仍存在

在第 5 节条件下，具名 LaCAM 分支不会沿所读显式控制流进入以下搜索调用链：

- O2 L56–213 的 `LNS::run()`，包括 L96 起的迭代改进循环、随机邻域生成、删除原路径、L143–144 的 `runPP()`；
- O2 L544–644 的 `runPP()`，包括随机打乱 agents 以及 L591 的 `agents[id].path_planner->findPath(...)`；
- O2 L445–494 的 `fixInitialSolutionWithLNS2()`，包括 `runPP()` 和 `InitLNS::run()`；
- O1 L75–139 的另外两种具名算法分支中，初始/重试 `lns->run()` 及后续修复后继续 `lns->run()` 的路线。

这给出了一条避免进入已核 LNS/PP 搜索调用点的源内选择路径。SIPP 随机比较器自身的实现文件与 header 不在六对象内，所以本报告不声称本次亲见了其比较器正文；“避免相应 SIPP 搜索调用”的证据限定在没有进入上述 `path_planner->findPath` 路线，而非对全部可能依赖作阴性证明。[O2 PP 调用点](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L544)

仍然存在的包装和未核边包括：

- O1 L11–20 无条件 `new LNS(...)`，不是另建一个无 LNS 类型的顶层 Planner；
- O2 L7–47 的 LNS 构造接受 `use_sipp` 并向 `agents.emplace_back(instance,i,use_sipp)` 转交；O1 对应实参是 `true`。Agent 构造实现未读，不能由此确认或排除其内部构造的具体求解器、容器和比较器行为；
- O1 L35–43 的 `loadPaths()` 仍使用 `clearAll/loadPaths/checkReplan`；所读 O2 方法体显式维护路径、状态和冲突标记，但所调辅助依赖未完全展开；
- O1 L141–166 的 `planner_commit()` 仍调用 LNS 对象的 `commitPath` 和 `validateCommitSolution`。O2 中这两个方法的主体已读，后者还构造 `Agent(...,false)`；其构造及更下层依赖仍未封闭；
- `Instance`、`LACAMInstance`、`PathTable`、`Agent`、求解器基类、header/inline 方法、系统调度和构建链接不在本次完整对象集合内。

因此“纯 LaCAM 选路”可以指源内既有的搜索模式，但不能改写成“整个生命周期完全不经过 LNS 包装与任何单体求解器相关代码”。后者没有得到本次证据支持。

## 7. LaCAM 自身的随机化与比较器契约边界

O6 完整实现仍有明确随机入口：L218–221 的随机重启选择；L311–320 在展开低层树时的 `std::shuffle`；L398–405 为候选顶点预先取得随机 `tie_breakers`。所以该官方模式不是无随机模式，也不是消除了所有随机输入的确定性算法。

O6 L414–421 的 `std::sort` lambda 比较 `getAllpairDistance(...) + tie_breakers[...]`；随机取得值的语句在该 sort 调用之前，lambda 正文没有调用随机函数。O6 L90–91 的另一处 sort 直接比较已存的 priorities。这是对本次所读比较器语句的精确描述，不能扩展为所有输入上的标准库契约证明。[O6 候选排序](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp#L398)

本次未完整核验这些键的所有初始化/取值域、随机辅助函数、全部索引合法性、外部状态可变性、无未定义行为或标准库版本。因而不能把“lambda 内没有直接抽随机数”提升为“已经完成整个比较关系的严格弱序证明”或“整个算法所有库契约均已认证”。这里只识别了一条源内既有的搜索模式边界，避免把未核库契约偷偷作为主适配定理前提。

## 8. 不能充当官方入口的注释材料

O3 `lns_driver.cpp` 从首行到末行的旧入口内容全部处于行注释中（另有空白行和 BOM）。其中可见的 `main`、`solver`、`sipp`、`initAlgo`、`maxIterations` 等注册文字都不是该文件中的有效可执行语句。

因此不能把旧注释里的 `--solver`、`--initAlgo` 或 `--maxIterations` 当成已经支持的现行配置，不能用其“看起来可把 LNS 关掉”的组合来回答本任务。O4 的有效 `mapfPlanner` CLI 注册与字段赋值才是本次亲见的入口证据。[O3 完整注释对象](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lns_driver.cpp)

O4 源码还包含某个可执行文件名的注释示例；本次未核 CMake/构建目标，因此不据此提供可运行的二进制命令，也不复制其中实验参数或输入路径。

## 9. 官方支持、改源适配、未知三分

| 类别 | 本次判定 | 命名与适配约束 |
|---|---|---|
| 官方已支持 | 固定 R0 `src/driver.cpp` 有效注册 `--mapfPlanner 1`；具名 LaCAM 分支采用第 5 节显式 LaCAM2 选路链 | 可以登记为“R0 固定 commit 的官方 LACAM-only 选择模式”，同时保留本报告的声明/调度/依赖条件；不称全程序已经认证 |
| 改源适配 | 删除 LNS 包装、直接新建顶层 LaCAM 入口、修改比较器、改写随机化、引入新配置通路、修补或绕开未核库行为，均不是本次已经找到的原生选择器本身 | 本次未做任何这类改动。若以后采用，必须另名、显式登记源差异；不能继续冒用“未改 R0 native”含义 |
| UNKNOWN | 全程序所有规划生命周期是否完全不执行任何 LNS/SIPP 随机比较器；三模式枚举定义、Agent/求解器构造、系统调度、inline/依赖闭包、构建目标、标准库契约与运行行为 | 六对象已用尽；不偷读第七对象，不用导航旧结论补空白，不输出全域阴性断言 |

若原比较对象使用的是另一个 R0 模式，改选官方 LACAM-only 仍然是一个需要明示的算法模式变化，不能保留原模式名称而隐藏选择器变化。若换成其他仓库的 LaCAM/LaCAM2，实现身份更已改变，不能以换源的方式偷偷保留 R0 native 名称。本次没有换源。

## 10. 非授权事项与最终来源界限

本任务完成的是源入口与显式控制流的有界静态核验，不是实验启动许可、源码修复、构建认证、基准结果、全程序域确认或新算法活性/安全证明。没有对实际运行表现、所有随机比较器不达、LNS 类型完全消失或纯 LaCAM 在真实负载中的成功率作确认。

没有选择实验参数值或范围；为准确识别官方入口而报告的算法类别 `1`，以及源码具名方法中的结构性常量，不构成本次实验设定。H、T_delay、B_CAL、B_max、B*、P_active、density N 均未赋值，未给默认值或范围，未生成或读取禁用载荷。

本文件仅为新的 73E1 NONBALLOT 来源回执。它不修改 73M1、73P1 或任何旧报告，不替缺失的 69E1，不把六对象的实际阅读强度推广为未读对象的证据。完成后停止。
