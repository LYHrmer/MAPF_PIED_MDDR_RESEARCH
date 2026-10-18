# 原生一次失败恢复：实现范围与核验边界

**状态：源码扩展、软件契约核验及完整编译/help完成；无恢复科学运行、无收益结论。**
该模块不修改冻结的六项共同初解清单、原适配器或作者缓存，也不复用它们的授权。
旧17项 `EMPTY_CAPPED` 来自Python固定组宿主，不能直接当作完整ADDRESS的失败分布。
原始计数和候选依据继续见[离线失败诊断](LATE_FAILURE_DIAGNOSIS.md)，本页不另复制结果表。
本轮完整ADDRESS已运行案例的改善，也不能证明恢复机会存在，因为原运行没有逐次PP失败轨迹。

## 在原框架中改变什么

`address_recovery.adapt(files)` 接收完整源映射，顺序为作者固定源码 →
`address_adapter.adapt` → `address_loop_guard.adapt` → recovery，返回四个changed-only文件：
`src/LNS.cpp`、`src/SIPP.cpp`、`src/driver.cpp`、`inc/address_recovery_support.h`。
构建阶段没有创建机器人实例或调用搜索；运行器尚不接受恢复variant。

参数是 `--recoveryPolicy abandon|random|anchor`（默认abandon）、
`--recoveryCalls 1..8`（默认8）、`--recoveryTrace <新JSONL路径>`。
一个PP主尝试至多触发一次额外恢复，不递归恢复尾段失败。

SIPP只增加返回位置标签：`FOUND`、`START_BLOCKED`、`FOCAL_DRAINED_EMPTY`。
它们是固定源码的执行位置记录，**不是本项目独立完备性证明**。
调用后优先核对原repair与全任务共同绝对截止；超时优先记为`DEADLINE`，
包括返回FOUND但已经超时。无标签的空返回为`EMPTY_UNCLASSIFIED`，不得触发恢复。

原ADDRESS的`runPP()`使用默认`MAX_TIMESTEP`，没有旧诊断的剩余h逐车cap。
当前扩展只对在截止内正常耗尽focal、位于后半且失败车旧路径受到新prefix阻挡的
情形考虑恢复。`START_BLOCKED`、累计成本停止、异常、未知、超时不触发。
检查的是严格改善要求下的**已实现前缀成本预算**，不偷偷套用旧cap或引入新h剪枝。

anchor保留最早阻挡位置之前的prefix，在该处插入失败车旧路径，再按原相对顺序
重算其余尾段。旧路径与固定外部路径、保留prefix必须相容，覆盖顶点、对向边及
永久终点驻留；尾段必须不超过调用配额。random采用相同资格门槛和调用配额，
做一次全邻域随机重排。abandon在同样记录后继续原ADDRESS外层搜索，不闲置剩余时间。
若额外配额小于完整邻域大小，三个机制臂都不进入恢复；不能利用random无法完成
整组请求、anchor仍能完成短尾段的不同资格分母制造收益。首轮固定8次配额。

## 事务、奖励与期限

额外搜索在私有`PathTable`中进行。其构造、插入及查询费用全部保留，构造后再次
检查截止才启动无内部时钟的SIPP；准备已超时则不计成实际SIPP调用。
原primary的`agents.path`和`path_table`在候选完成前都不改变；任何尾段失败直接走
作者原回滚。完整新联合方案通过全检、严格SOC改善与截止检查后，才替换整个邻域，
同时更新路径表、迭代指针和累计成本；`neighbor.agents`与`old_paths`映射不重排。

作者种子奖励块逐字保留，仍对**原primary尝试的接纳前状态**更新一次；恢复不额外
奖励、不将失败前缀奖励改称完整成功收益。当前仅适用已核RandomWalk/Bernoulli配置，
扩展ALNS另需检查外层奖励。增加的SIPP会消耗全局`rand`，因此即使初始seed相同，
后续邻域提议也可能分化，不能声称配对中始终使用同一提议流。

恢复复用原repair起点和T，以及全任务剩余期限的较小值，不重开一段时间预算。
共同修正原循环“最后一次FOUND返回后可能越过T仍接受”的边界；primary和恢复
完整候选都必须在准入截止前完成校验和替换。最后逐尝试trace写出/flush单列为
准入后的诊断I/O，仍计入原生过程与全任务预算，没有额外免费任务时间。

JSONL覆盖每次到达runPP的成功、无触发和失败：原顺序、失败位置/车、返回分类、
旧路径阻挡车、是否实际检查阻挡、primary调用数、额外请求与实际调用数、各次额外
返回、保留prefix/尾段规模、原/最终组SOC、接纳结果、诊断/搜索/校验计数与wall。
未做阻挡分析明确标记false，不能解读为“没有阻挡”。完全未进入runPP的构组失败
不在本trace中，不能据此推断构组成功率。`search_ns`含私有表准备和搜索；
`attempt_wall_before_trace_ns`包含其他转换/提交成本，二者有包含关系，不能相加。

## 对照不能人为加重强基线

三mode共用诊断和校验协议，仅用于分析恢复机制。带这些额外检查的abandon
**不能替代**未强加恢复诊断的完整ADDRESS成本基线。后继完整预算比较还必须包含
独立的`loop_guard`版本：其原`runPP()`没有旧路径阻挡分析和多次全检；各方法计入
自己的真实全部开销。不得给强基线强塞诊断后再宣称完整加速。

当前还存在一个必须在正式比较前对齐的契约差异：三mode拒绝最后FOUND或末检
越过原repair T后的接纳，纯`loop_guard`则逐字保留原runPP的软T行为（两者仍受
相同全任务总准入）。因此现在不能声称它们已有“相同单次修复期限”的公平比较。
后继应把最小截止修正也适配给无恢复诊断的强基线，再冻结比较版本；不能更改
本轮已运行结果或当前四项仅验证根界终止的功能清单。

纯C++fake callback检查了prefix保留、一次尾段、random/abandon、请求配额、
目标驻留与对向边、未知/成本/超时不触发、FOUND超时拒绝、准备超时零实际调用，
以及原incumbent不被部分失败覆盖。实际三个翻译单元的语法编译通过，原奖励与
回滚段字节保持检查通过。假例没有执行SIPP或作者Instance，不能算性能实验。

随后通过现有`build_address_full.py --adapter --extension recovery`完成全程序编译，
只执行在Instance构造前返回的help。[构建收据](recovery_build_receipt.json)固定
作者文件、base/guard/recovery叠加源码、工具链和阶段日志；本机独立二进制为
工作树根`.address_recovery_build/build/address`，SHA
`57cdf07b1b8b6c90ac76b87991d9b6a089d5948561335f1a15138139d5d1d3fb`。
原失败二进制和纯根界二进制都未覆盖。完整链接成功不表示恢复事务已在真实任务上运行；
科学运行器仍明确拒绝recovery变体。

后继先核对完整ADDRESS是否有足够的同类失败，再申请具体科学比较。若没有，
停止这一恢复候选；若存在，还须正面对照相同问题和预算的优先级搜索/回退方法。
“回退＋换序＋复用”本身不是新颖性结论。
