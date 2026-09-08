# 73L1：Hönig 2019 persistent execution 外部 lifelong 对照适用域核对

状态：NO-SKILL / CONSTRUCTIVE / NONBALLOT。只读公开一手材料后的范围判断；不是正式审查、实现完成回执或主对照通过票。

## 1. 结论与最小缺口

**该方法确实包含 lifelong/replanning，可以保留为主 lifelong 外部方法候选；当前证据还不足以把它固定为已复现、已与本项目共同物理/信息/成本域匹配的主对照。**
不能因为内部调用 single-shot solver 就否定其 lifelong 功能；本次依据包括正文 IV-C 与 Algorithm 2，不依据摘要作否定。
也不能把内部 R-S/E0 换名为 Hönig 2019：外部身份需要实际保留其 ADG 动作依赖、动作状态、commit-cut 重规划及可追溯原规划来源。

最小缺口有三项：

1. **整法身份缺口：** 已确认作者规划库及其 ECBS-TA 接口；尚未确认与 2019 论文匹配的完整 ADG、commit-cut、仓库任务适配和 execution monitor 作者源码及提交。库存在不等于整法源码已取得。后继可以取得完整作者代码，或明确选择按论文重构并另证符合其规则；后者必须标为重构，不能称作者原字节实现。
2. **任务/源接口缺口：** 必须明确如何把本项目指定的任务实例、服务规则、起终点资格与原规划输入对齐，以及保留还是替换原任务分配和规划器。此处没有读取任何本地任务/地图载荷，故不判断具体实例是否满足原域条件。
3. **guarded 共同域缺口：** 必须公开本报告 §5 的新合同并给出组合证据。相同 K、可信服务和控制器不会自动把原结论变成适用于新系统的证明。

因此，当前是否“已足以作匹配的主 lifelong 外部比较”的回答为**否，尚未完成接口与可复现身份闭合**；否定的是当前可直接准入的状态，绝不是“原论文没有 lifelong”。

## 2. 一手来源身份、原始入口与实取指纹

论文：Wolfgang Hönig、Scott Kiesel、Andrew Tinka、Joseph W. Durham、Nora Ayanian，*Persistent and Robust Execution of MAPF Schedules in Warehouses*，IEEE Robotics and Automation Letters，4(2)，1125–1131，2019，DOI `10.1109/LRA.2019.2894217`。
作者 PDF 自标为 accepted December 2018 的 preprint；这与正式卷期年 2019 不混用。[作者论文条目](https://whoenig.github.io/)；[作者实验室书目条目](https://github.com/USC-ACTLab/usc-actlab.github.io/blob/master/publications.html)。

| 对象 | 原始/固定 URL | 实取 SHA-256 | bytes | 阅读/长度说明 |
|---|---|---|---:|---|
| 作者 PDF | [2019_RA-L_Hoenig.pdf](https://whoenig.github.io/publications/2019_RA-L_Hoenig.pdf) | `3b82372d6c6c67aaac6b67eaf91d1bc86529c2671f50dbabbf80e560a9fdb849` | 1188912 | 7 页；web 提取全文 L0–872，共 873 文本行。二进制换行计数不是论文行数 |
| 作者规划库入口 | [whoenig/libMultiRobotPlanning](https://github.com/whoenig/libMultiRobotPlanning) | 不以网页 hash 替代 Git 身份 | — | 作者主页明确列自己为作者/维护者，并直接链接此仓库 |
| ECBS-TA 接口源码 | [固定提交 ecbs_ta.hpp](https://raw.githubusercontent.com/whoenig/libMultiRobotPlanning/4c75fa20c435c440d8b6bd6dc81668ddc7296ba0/include/libMultiRobotPlanning/ecbs_ta.hpp) | `bd3fd48c902b545118e1f9e926ba36c7d219a390d4f2a2edae70f89bdd3a26bb` | 17248 | 全文件 L1–502 已读 |
| 规划结果接口 | [固定提交 planresult.hpp](https://raw.githubusercontent.com/whoenig/libMultiRobotPlanning/4c75fa20c435c440d8b6bd6dc81668ddc7296ba0/include/libMultiRobotPlanning/planresult.hpp) | `0a72a1504b97b77d09e7a90c2eda13444ef33a25880d07873cda6b70272f1bff` | 941 | 全文件 L1–30 已读 |

作者主页的 2019 论文条目在本次可见窗口列 PDF、Video、DOI，未列代码按钮；其另一个开源代码条目直接指向上述规划库。这只界定本次找到的入口，不证明完整作者执行器从未公开。
`git ls-remote` 实取 `refs/heads/main=4c75fa20c435c440d8b6bd6dc81668ddc7296ba0`。这是本次查询时的当前库提交，**不是已证的 2019 实验提交**。
上述 PDF 与源码以公开 HTTP 内容流读取/计算摘要，未在磁盘保存源副本；报告中固定源码 URL 包含完整提交。

## 3. 原文事实胶囊：全文核实，保持短摘要

下面 P1–P7 是对同一论文的精简改述；后文编号引用这些事实，新增设计判断与原文结论分开。[作者 PDF，§III–V](https://whoenig.github.io/publications/2019_RA-L_Hoenig.pdf)。

- **P1:** Tasks can arrive online. Section IV-C overlaps planning and execution through a predecessor-closed commit cut.
- **P2:** ECBS-TA supplies timestamped warehouse actions; SIPP is another discussed solver. State includes location, heading, task and stage.
- **P3:** Dispatch accepts Type-1 predecessors that are enqueued or finished, but requires Type-2 predecessors finished. Robot success notifications mark completion.
- **P4:** Assumptions include eventual action completion, timely notification, limited spatial deviation, circular robots and accommodating grid cells.
- **P5:** Synchronous rotations can induce ADG cycles; detection or extra planning conflicts address them. Persistent guarantees use well-known infrastructure.
- **P6:** The cut shifts new-plan time origins to exclude new-to-old dependencies. Desired lookahead is domain-specific; evaluation demonstrates overlap.
- **P7:** Unexpected obstacles trigger autonomous stopping, command-queue clearing and replanning. Evaluation reports warehouse utilization and waiting.

定位：P1/P6 在 PDF pp.5–6、提取 L566–668；P2 在 pp.3–4、L274–361；P3 在 p.4、L481–500；P4 在 pp.2–3、L168–243；P5 在 p.2 L147–167 及 p.4 L410–480；P7 在 p.4 L496–500 与 pp.6–7 L669–794。

## 4. 作者源码接口核实：原 MOVE 从哪里产生

本次固定头文件的 `ECBSTA<State,Action,Cost,Conflict,Constraints,Task,Environment>::search(initialStates,solution)` 是可辨认的原规划入口；`Environment` 负责邻接动作、目标判断、冲突和约束，搜索调用 `nextTaskAssignment`。`PlanResult` 分别存有序 states/actions 及其代价。[固定 ECBS-TA 源码](https://raw.githubusercontent.com/whoenig/libMultiRobotPlanning/4c75fa20c435c440d8b6bd6dc81668ddc7296ba0/include/libMultiRobotPlanning/ecbs_ta.hpp)；[固定结果接口](https://raw.githubusercontent.com/whoenig/libMultiRobotPlanning/4c75fa20c435c440d8b6bd6dc81668ddc7296ba0/include/libMultiRobotPlanning/planresult.hpp)。
由这个模板接口可提出的适配接缝是：冻结完整 State/Action/Task/Conflict/Environment → 调用原求解器 → 全检结果 → 编成带 plan/action 身份的 ADG。**这个接缝是本次设计判断；本次没有实现它，也没有取得论文专用 Environment。**
P2 与该接口支持将外部原 MOVE 追溯到其原规划输出；ADG 自身不应被描述为另一个偷偷生成几何新 MOVE 的规划器。
只加载这个搜索模板、喂本项目当前计划、再套内部 release 规则，不能据此声称复现整套已发表方法。
若后继坚持与本项目共用另一原规划源，应命名为“共同来源计划上的 ADG 执行适配”，只比较执行调度；不能把原 lifelong driver 的任务/规划贡献一并算作已保留。

## 5. native 与 guarded 两轨的候选合同

本节全为本项目需要公开的新设计条件，不是声称论文已提供这些接口。
native 的含义是保留 P1–P7 与相应作者/明确重构实现的原作用域；guarded 的含义是保留可识别的原 ADG/commit-cut/规划职责，同时插入共同物理与观测责任。两者分别命名、分别报告。

| 项目 | native 身份应保留什么 | guarded 必须新增并公开什么 |
|---|---|---|
| 原 MOVE 来源 | 与 P2 对应的求解器、状态/动作语义、任务分配、冲突规则及版本 | 固定输入快照与动作身份；共享任务接口如何映射；新旧提交锚点检查；失败不得用内部策略生成替代 MOVE |
| ADG 完成位 | P3 的真实语义及实现中的消息/队列约定 | action_id/plan_epoch 完整绑定；成功 END 证据付费捕获、交付、验证；超时/普通反馈不能置 finished；重复旧通知不得释放新动作 |
| 连续形体 K | 不把原域的空间前提自行放宽 | 对每条原动作证明整个运行/制动/HOLD 中真实占据始终包含于共同 K 包络；跨动作转向和 endpoint 也须覆盖；相邻几何冲突不能只由顶点/边冲突代替 |
| 排队与控制 | 保留 P3 可识别的 Type-1/Type-2 使能规则及原控制意义 | 已入队不等于可越过共同授权；每次实际 START 需相应覆盖和身份检查；新增 gate 只能延后原动作，不能无记录地改动作来源或依赖 |
| 终点与逻辑消费 | 明确原 action finished 对应的语义 | 区分物理 END、中心接受 END、依赖解除与 executor 一次消费；中心/查询/planner 不因本地推进得到免费 c/pose；正确下一 slot 须走声明的付费接口 |
| 重规划与 cut | 保留 P1/P6 的旧承诺及新旧图交接规则 | 对已交付完成位、已承诺队列、任务和计划版本做付费一致快照；计算期间物理继续；新结果提交检查依赖/锚点/身份；失效计算付费后丢弃，不撤回正在执行的原责任 |
| 障碍/取消 | P7 的原适用域作为独立 native 能力 | 若共同域包含新障碍，须具体区分未发、已排队、已授权、正在执行的动作可否取消及谁继续覆盖；若只比较延迟域，公开该限制，不宣称保留整个 P7 能力 |
| 循环与新阻塞 | 用 P5 对应的源约束/检测策略处理 ADG 环 | 新几何 gate 增加的等待关系也须检查；可按公开失败规则停留/报错，不把临时全体停走当作已证无死锁；失败不能被从结果中悄悄删除 |
| 费用与机会 | 原实验时间/消息语义的独立记录 | ADG 构造、状态扫描、cut 闭包、规划/丢弃、所有输入捕获、消息编解码/每接收端、验证/拒绝/重放、几何/资源访问、控制/日志/GC 全计实际工作；共同机会与容量不由臂收益改写 |
| 真实任务服务 | native 原任务身份与原目标函数 | 共同任务实例、到达/服务资格、完成去重和真实账本更新；真实服务与算法收到任务/终点回执解耦；不得用 ADG 队列完成数冒充真实任务数 |

P3 允许的队列提前入队和控制连续性，是容易被共同 gate 改变的地方。若适配后实际要求每条 MOVE 在终点停止并等待确认，必须列为 guarded 的新增延迟/控制约束；不能把 resulting slowdown 解释成原法固有的性能。
反过来，也不能为了保留 native 平滑性让 guarded 在未覆盖后继动作时连续穿越。共同控制合同若不能同时容纳此行为，应报告接口不匹配，或者明确声明所评估的是受限扩展轨。
共同可信服务可以复用同一已付费对象；“可购买能力相同”不意味着双方实际采样次数、通信量或处理工作被强制抹平。

## 6. 不能继承的结果，以及仍能说的最窄结论

以下均为组合后的推论边界，不是替作者重新宣称定理。

- **连续安全不能直接继承。** 必须另证共同 K 包络、gate 授权、动作身份与证据延迟下的责任保持。原 ADG 结构本身不补上新空间域的证明。
- **无死锁/活性不能直接继承。** 原 ADG 无环不足以排除新增几何资源等待环；通信永久丢失、动作永不完成或共同 writer 永久得不到工作容量时，也不能推出持续进展。
- **无规划等待不能直接继承。** 引入付费查询、迟到完成证据、cut 扫描和结果验证后，原本足够的期望 lookahead 不保证仍足够；本报告不赋任何阈值。
- **求解器次优界不能变成闭环吞吐界。** 需要分别报告源计划指标、任务服务指标和付费闭环时延，不能把头文件中的搜索性质跨域传播。
- **native 身份不能由 guarded 成功替代。** 共同 gate 的安全收益与额外延迟应归属新增接口；原方法名不能掩盖它。
- **整法比较不能直接归因于查询策略。** 若外部方案保留自己的任务分配/规划器/cut，则终端性能差异包含这些因素；若替换为共同来源，则必须承认比较对象范围已缩为执行适配。

在尚未实现和组合证明前，最窄可说的结论是：这是具备真实 lifelong 内容、机制可辨认的已发表外部候选，具有明确可设计的 guarded 接缝；不是当前已完成的主比较。
本报告没有通过读取摘要认定“不支持 lifelong”，也没有根据代码入口未找到而认定“不存在作者代码”。

## 7. UNKNOWN 与下一步的最小材料要求

| UNKNOWN | 为什么仍未知 | 最小补齐材料 |
|---|---|---|
| 完整 2019 作者实现及提交 | 论文正文、作者论文条目和规划库接口不足以绑定完整 monitor/cut/warehouse driver | 作者明确源码入口及版本，或明确选定按论文重构并提供规则对应证据 |
| 当前库与 2019 仓库实验实现的对应 | 当前 main 不是历史实验身份凭证；未读全部仓库实现 | 原实验提交/专用适配源码的出处与差异说明 |
| 项目实例是否属于原适用域 | 本任务禁止读取具体地图/任务载荷，且未获这些实例的共同域证明 | 后继获准的输入资格证明；本次不生成实例 |
| 源动作与共同任务服务的一一映射 | 两端任务/服务语义尚未给出可审计接口 | action/task 实例身份、服务谓词、失败及去重规则 |
| 新形体/控制/采样/资源 gate 的组合安全与活性 | 原文不是该新系统的证明 | §5 对应的明确前提与逐项保持论证；不能只贴原论文安全结论 |
| 有限计算/消息延迟下的真实效果 | 未运行任何实验 | 先补设计合同；本次无实验许可，不生成载荷或数值结论 |

补齐前保留候选即可，不必将它冒充已经匹配的主对照，也不必据此扩展成新的大规模文献检索。

## 8. 阅览范围、失败与实际动作回执

起始工具时钟：`2026-09-07 13:42:33 UTC`。写入前工具时钟：`2026-09-07 14:05:39 UTC`。均为真实工具返回，不作为未发生实验的时间记录。
目标文件在创建前经 `rtk proxy test ! -e` 确认不存在，退出码 0。

**论文范围：** 已完整阅读作者 PDF 的提取文本 L0–872，覆盖全部 7 页（正文、算法、实验和参考文献）。主要累计可见窗口依次为 L0–471、L370–587、L572–708、L725–827、L684–781、L814–872；其并集完整覆盖全文。部分后继短 open 只返回数行，没有被当作额外全文。
请求过 PDF 零基页 3、4 的 screenshot；工具返回引用，但本次未对可见图像逐图核验。图表视觉细节未用于新增结论；本次“全文”严格指完整提取文本阅读，不声称逐图视觉审查。

**作者入口与代码范围：** 作者主页定向窗口涉及 2019 论文条目、开源库身份；GitHub 根页仅目录/README；include 目录仅名称列表；ecbs_ta.hpp 先读 GitHub 接口窗口，随后固定提交全文件 L1–502；planresult.hpp 固定提交全文件 L1–30。没有读 example/benchmark/test 中的实例内容，没有 clone 仓库，没有构建或执行作者代码。
论文题名加 code/github 的一次定向检索返回了作者/机构材料及第三方引用；仅将作者/机构材料用于证据。之后两次限定作者/实验室路径的窄检索返回偏题结果，均未继续打开或用作证据。没有扩展其他论文或第三方实现。
作者实验室书目使用搜索返回的对应条目窗口；未称完整读取其整个 publications.html。

**真实失败与恢复：**

- web 打开 raw main 的 ecbs_ta.hpp 返回 Cache miss；打开 GitHub API commits/main 返回不可打开；GitHub commits/main 页面返回 Internal Error。均未据此推断源码不存在。
- 首次普通权限 `rtk git ls-remote` 退出 128，报 TLS/gnutls 连接提前结束；按权限规则升级后同一只读命令成功，取得上列 main 身份。
- 固定提交的两个 raw 头文件直接 curl 读取成功，退出码均为 0，未保存副本。
- PDF 和两个头文件的流式摘要管道首次均遭 curl 连接失败，空流保护返回 EMPTY_STREAM/退出 1；未接受空内容摘要。按权限规则逐项升级后全部成功，退出码均为 0，得 §2 摘要与长度。
- 流式 Python 仅从 stdin 计算 SHA-256、字节长度及换行计数；没有执行源码、生成算法代码或运行测试。PDF 流式换行数 7763 是二进制字节统计，未当作论文行数。

**写入与边界：** 本报告仅通过 apply_patch 新建/文字修正；原 73T1 及任何旧报告未改。没有读取任何本地旧候选/审稿材料、skill、35–38、Q-CAL/Q-CONFIRM、桌面，或 map/task/scen/config 实验载荷。
本次未创建子代理、未正式审查、未构建/实现/测试/仿真/调参、未生成 O 或实验载荷，未发送邮件或联系作者。
H、T_delay、B_CAL、B_max、B*、P_active、density、N 均未赋值、范围或默认。
本报告写入后的 SHA-256、bytes、lines 在独立只读核对后随交付消息报告；正文不嵌入自指终稿摘要。
