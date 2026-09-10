# 73E15：QEMU icount 全系统来源服务接缝的一手核验

日期：2026-09-09。性质：独立 NO-SKILL / CONSTRUCTIVE / NONBALLOT 来源接口分析；不是正式逻辑审查、资格票或根验收。结论保持 **HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT**。

## 1. 本次结论与严格边界

QEMU TCG full-system icount 是比裸 CPU 引擎更具体的候选接缝：官方说明承诺按指令预算阻止过长 TB 执行，源码确有接收 CPU 预算、限制余额、结算的入口；固定 x86 翻译器还明确禁止 icount 模式在一段内部循环中完成整个 REP 字符串。因此，“REP 整串只收费一次后任意跑完”不能继续作为这个固定模式的否定证据。

但它**尚不是当前 73 的可直接绑定后端**。本次没有找到并核实“每一公共 PROCESS_SLICE 授额—耗尽后停驻—无自动续跑—对外输出封存”的完整控制调用链；icount 的 guest 时间也不满足原公共行读钟。设备回调、翻译等宿主工作与 guest 指令计数不是同一费用域。下文只选择一个明确的内部预算接缝，给出可闭的局部事实和阻断它直接合入 73 的最小反例，不再枚举其它工具，不把后端名称当证明。

当前来源制度按根已采用的 ALWAYS_ADVANCE / FAIL_STOP_SOURCE 理解：持续会话，不做逐 job 快照、提升或回滚。E14 暂不采用 NP-LIVE 的决定保持；本报告不改变 TASK、故障、固定配对推断或服务模型。本次没有运行 QEMU，未安装、配置、构建、实现、写伪代码、测试、仿真或生成任何实验载荷；保护参数及其范围、默认值均未赋值。

## 2. 输入身份、实际阅读与获取记录

研究正文仅定点核对了 `73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md` 的时钟、公共 O、服务/费用和来源生命周期：实际完整窗口 L172–218、L240–255，另作相关关键词检索；没有声称本轮全文读完。读时观察身份为 SHA256 `7197daafe3af9f1a3757ae9f230ee406dae346184064a97d51f7566d98b5a881`，141042 bytes、490 LF；该正文仍由根编辑，以上不是固定送审身份。

外部对象严格限于下表四个，按文档→运行预算→时钟→x86 翻译依赖读取。URL 均为 QEMU 官方 GitHub 仓库的 `v10.2.0` 标签路径。没有额外读取第五个官方对象、版本发布页、guest 镜像、内核、设备实现或其它载荷。全对象原始字节用于哈希；人工语义阅读范围另列，二者不混淆。

| 编号 | 对象、原始 URL 与 blob 页面 | 实际阅读层次 | bytes / LF |
|---|---|---|---|
| Q1 | [docs/devel/tcg-icount.rst 原始](https://raw.githubusercontent.com/qemu/qemu/v10.2.0/docs/devel/tcg-icount.rst)；[blob](https://github.com/qemu/qemu/blob/v10.2.0/docs/devel/tcg-icount.rst) | L1–88 全文 | 3591 / 88 |
| Q2 | [accel/tcg/tcg-accel-ops-icount.c 原始](https://raw.githubusercontent.com/qemu/qemu/v10.2.0/accel/tcg/tcg-accel-ops-icount.c)；[blob](https://github.com/qemu/qemu/blob/v10.2.0/accel/tcg/tcg-accel-ops-icount.c) | L1–160 全文 | 5047 / 160 |
| Q3 | [accel/tcg/icount-common.c 原始](https://raw.githubusercontent.com/qemu/qemu/v10.2.0/accel/tcg/icount-common.c)；[blob](https://github.com/qemu/qemu/blob/v10.2.0/accel/tcg/icount-common.c) | L1–503 全文 | 16465 / 503 |
| Q4 | [target/i386/tcg/translate.c 原始](https://raw.githubusercontent.com/qemu/qemu/v10.2.0/target/i386/tcg/translate.c)；[blob](https://github.com/qemu/qemu/blob/v10.2.0/target/i386/tcg/translate.c) | 全文件检索 `repz/repnz/gen_rep/CF_USE_ICOUNT/gen_io_start/DISAS_TOO_MANY/translator_loop` 等并读命中相邻窗口；另完整读 L1290–1496、L3429–3463、L3740–3830。重点完整函数为 do_gen_rep、do_gen_string、gen_repz、gen_repz_nz；不是全文语义审计 | 124500 / 3932 |

| 编号 | 原始字节 SHA256 | 由本次原始字节计算的 Git blob SHA1 |
|---|---|---|
| Q1 | `59f5b3a1db0493125ac673bd14675ca8565090f232a0b4a12bdcda928451e53d` | `a1dcd79e0fdd5142d6e876466e397cf8a25d6d89` |
| Q2 | `30b346cf51c21fd3488195f8141ed58450b5e9ac9570ab7eeda3011459f03e88` | `d0f7b410fab3186f0359eed2b0c50dcab7d58b3e` |
| Q3 | `6b85641f2ab23b7ea67d332b3b127203597bb176a54114caa582804ddfbfe868` | `d6471174a3aae3310e36b175b93a1618b45cb447` |
| Q4 | `13a7b04ce90de5fcb0369ed1590cab9ff96fd4a665abf7f55e6205c7081fe7be` | `0cb87d020125836a3e055f615c786161ba210770` |

本次没有独立解析标签到 commit，也没有核验签名；不能把上述计算 blob 值写成 GitHub API 实际返回值，更不能声称已固定可执行构建。原始 URL、读日、全文哈希足以明确本报告实际依据的四组字节，未来构建仍须固定 tag 所指 commit、构建选项和实际二进制。Q1 文件头有 Linaro 版权和作者；Q2/Q3 文件头提供宽松许可全文；Q4 文件头标明 LGPL 2.1-or-later。本报告仅作短标识引用与分析，没有复制源码工件。

获取实际状态：Q1 首次 web 打开失败（Cache miss），不算正文证据；随后原始 curl 成功。部分沙箱内重取返回连接错误，已按授权机制用 require_escalated 重试相同对象成功，没有绕过。一次失败流水线曾输出空字节哈希，该值已明确排除；后续均检查非空并记录上表真实字节。未读 35–38、受限 Q、实例数据或桌面。

## 3. 指令额度、timer 和 TB：确有接缝，但不是整套外部协议

Q1 的核心说明是：TB 开始处先扣除该块将执行的指令数，再检查余额；会使余额负值的块不直接执行，而重新产生满足剩余额度的短 TB。因此定时预算不必容忍整个长 TB 越界之后才结算。MMIO 情况则恢复尚未执行的额度、重新翻译当前指令的短块再执行，以便 I/O 看到准确的当前计数。这里的重新翻译及计数恢复属于模拟器内部会计，不是撤销已完成的源副作用，也不恢复 accepted-only 来源制度。[Q1](https://github.com/qemu/qemu/blob/v10.2.0/docs/devel/tcg-icount.rst)

Q2 L105–148 提供具体入口：`icount_prepare_for_run(cpu,cpu_budget)` 将运行预算取调用者预算与当前限制的较小值，装入 decrement/extra 字段；`icount_process_data` 更新已执行量后清理运行计数。Q3 L68–105 的已执行量由原预算减当前余额计算。因此可定位的未来接缝是**内部 vCPU 运行授额/结算对**，不是一个已审定的外部“运行恰好若干源步并冻结全部 VM”命令。[Q2](https://github.com/qemu/qemu/blob/v10.2.0/accel/tcg/tcg-accel-ops-icount.c#L105)；[Q3](https://github.com/qemu/qemu/blob/v10.2.0/accel/tcg/icount-common.c#L68)

Q2 L37–67 的限制还查看 guest 虚拟 timer 和 REALTIME timer；L69–89 会通知 AioContext 并运行虚拟 timer 回调。预算为零也可能进入 timer handler，不能由“guest 没多执行指令”推出“没有任何其它工作或副作用”。本次未读 `cpu-exec`、通用 TB 计数生成及外围 vCPU 循环，所以没有声称亲核所有短块重编译路径、异常恢复及自动再授额分支；Q1 是这一层的官方合同证据，Q2/Q3 是局部实现证据。

还须限定“精确 timer”的单位。Q3 L157–160 以固定转换得到指令虚拟时间，L226–230 将 timer 间隔向可计数的指令预算取整。不能把官方在其指令时间模型中的精确退出，夸成任意连续物理时刻的精确退出。此报告不取任何转换参数值，也不把 73 公共 Stop 时刻塞入该 timer 后声称合同已等价。

## 4. x86 REP：已排除一个强反例，仍不等于宏指令退休计数

Q4 L1354–1469 的 `do_gen_rep` 明确把 `CF_USE_ICOUNT` 与单步标志列入禁止内部循环的条件。在这个分支，字符串操作函数执行一个迭代，更新计数寄存器与标志，再跳回同一指令地址的执行边界；依 REP 条件结束时才离开。L832–841 的 movs、L1263–1288 的 stos/lods/scas 和 L1290–1349 的 cmps/ins/outs 也显示一个迭代所产生的访存或 I/O 工作。故在此固定版本的该翻译路径上，不能假定整个由计数寄存器指定的长字符串在一个收费点内无界循环。[Q4](https://github.com/qemu/qemu/blob/v10.2.0/target/i386/tcg/translate.c#L1354)

这同时说明计数名词需要准确：一个 x86 REP 宏指令可能多次到达同一 PC 的翻译执行边界，不等于硬件“整条宏指令退休一次”。禁循环分支在末次迭代后还可能重新进入零计数出口检查；不能仅由本函数断言初始重复次数恰好等于最终 icount 增量。精确的所有异常、重试及零计数统计仍依赖本次未读的通用计数路径。这里证明的是内部整串循环被禁止，不是模拟器所有 helper 都有统一宿主执行时限。

REP 中途暂停还会保留已写入的部分内存及更新后的寄存器，它不是把整条 REP 视为可回滚原子事务。只要这仍是私有 worker/guest 状态，源可在后续合法服务片继续；若是公共硬 Stop 则不得再获源执行容量，走会话终止。不得把单步的中间状态发布为完整提议，亦不得把通知停止当作 guest 全状态已经停驻。Q1 的 TB 检查及 Q4 的迭代边界尚不提供同步停驻收据。

## 5. 三类时间和完整成本不能合并

Q3 L123–160 的 guest 虚拟时间来自计数转换加 bias；L170–224 的自适应路径受实际时间影响；L293–392 显示空闲时还能通过 warp 推进虚拟时间、通知 timer。于是即使采取固定转换，单说“禁用随宿主调速”也不等于消除了空闲跳时。Q1 还明确限定 system emulation、排除 multi-threaded TCG，并说明 icount 不是 cycle-accurate 模型。[Q3](https://github.com/qemu/qemu/blob/v10.2.0/accel/tcg/icount-common.c#L293)；[Q1](https://github.com/qemu/qemu/blob/v10.2.0/docs/devel/tcg-icount.rst)

73 L176 要求同一公共行内源 chrono 读取同一世界 t，暂停排队后读到推进后的 t；L178 另定义本 worker 已完成收费服务的 CPU 域。最小不相容见证是：一个服务行内，源在若干计算之前、之后各读 chrono。73 允许两读相同；若直接把它们接到 icount 虚拟钟，中间指令会使后读增加。反向见证是 VM 在两次源片之间停驻，而公共物理时间已经推进；纯指令钟可能不变。warp 若擅自补齐又可能触发其它 timer。两种钟不存在无条件的一一替代关系。

因此唯一候选必须分离三域：QEMU 内部计数/guest 调度时间；源 chrono 所见的当前公共行 t；源 CPU 日志所见的 73 已付费服务量。后两者需要覆盖实际 ABI 的明确适配；不能只替换某个动态函数后假设 vDSO、内联、其它时钟入口已经覆盖。Q4 L3452–3461 见到 rdtscp 调用 I/O 起点及 rdtsc helper，L3030–3065 见到随机指令 helper；本次没有读取这些 helper 正文，不给它们编造“已返回公共 t / 已使用指定随机流”的合同。[Q4](https://github.com/qemu/qemu/blob/v10.2.0/target/i386/tcg/translate.c#L3452)

全系统的意义是允许将真实 guest OS/loader/libc/syscall 执行域纳入一个机器，而不必像裸引擎那样另造完整 Linux 用户态服务层；这不是本次已验证某个 guest Linux 镜像启动成功。候选所有 guest 启动、装载、动态链接、内核工作、库调用、源预处理、日志及失败清理的**实际 guest 指令**都须纳入既有 Srv_P 费用域，不以“不是 planner 函数”排除。不把准备好的 VM 起点免费当首次初始化，也不因 AA 而把 guest OS 费用删掉。

与此同时，TB 生成/重编译、设备模型、宿主文件访问、内存分配及主循环回调不是 guest 指令，不能以 raw icount 代替其真实宿主成本。作为纯执行引擎的宿主费用可依 73 元评价器规则另列实测；凡回调替应用复制、编码、读取新信息或完成业务服务，仍须进入相应付费应用服务，不能挂“模拟器”名义免费完成。有限 guest 指令预算既不是宿主 elapsed 上界，也不是处理器周期数。报告两账不意味着可从公共服务账中移走本应收费的应用工作。

## 6. 唯一候选与最小未闭接口

只保留一个纸面候选：**隔离的单 vCPU full-system TCG 持续 guest，采用固定指令计数模式；每个合法 Srv_P 行通过 Q2 的内部预算入口授予本行已付费额度，保持 AA 源状态；公共时钟与 CPU 日志由单独的显式 ABI 映射提供。** “单 vCPU”是隔离拓扑选择，不为研究保护参数赋数；不提供启动命令、配置、镜像或实现。下列要求是此候选仍需证明的合同，不是已存在的完整 QEMU API。

1. **行授额与停驻收据。** 本行服务容量只转换为不会超出已付费用量的 guest 预算；转换语义还须与 73 费用表共同登记。额度消耗/提前退出后，外层不能自动再授额，须返回准确已执行计数、私有终态或未完成状态，冻结 guest 与会改变应用可见状态的设备活动。Q2 给出局部入口，但外层循环、异常后计数及真正停驻点尚未核实。只在后继合法源片继续同一 job；余量不运行新 job。
2. **双源钟与封闭外部输入。** 源全部经过钟、CPU 钟、熵和阻塞接口必须分别映射到 73 既有域。guest 自身 timer 可供内部 OS 机制使用，但不得成为源偷读公共未来的路径。输入只安装付费捕获的冻结上下文，输出只写私有封存槽，经原中心付费验证和后继发布。真实主机网络、墙钟、熵或主动 I/O 完成不能未登记就影响源结果。仅有 record/replay 名称或一致种子不证明这一点；本次没有审计其全链。
3. **设备/ABI 身份和费用闭包。** guest kernel、loader、libc、编译器、R0 修复适配二进制与依赖均须固定；每种必要设备交互是 guest 内完成、无业务含义的宿主模拟开销，还是外部付费应用服务，必须唯一分类。不能由“MMIO 有准确 icount”跳到“其宿主 callback 内任意工作已经收费并可在任意点抢占”。本次四对象没有提供设备回调完整包络，这一项仍是阻断，不能用无限扩查所有 QEMU 设备回避限定接口的选择。

一个足以阻断“原配置直接满足 73”的具体反例是：已授额 guest 指令访问设备，模拟器在该 I/O 的计数边界准确执行宿主回调；回调却立即把本 job 的内容交给外部接收方，或从主机读入会变化的数据。即便 guest 指令数一条未超，73 的严格后继付费发布/冻结输入仍被破坏。Q1 的 I/O 对齐保证不禁止这种回调语义，Q2 的 timer/Aio 路径也不证明所有外部活动已停。因此必须先给限定设备/通信通道合同，不能凭计数精确推信息边界精确。本报告未声称任何未读具体设备一定执行了此反例；这是当前宽泛候选没有排除的合法行为形状。

这套接缝无需新增 Linux syscall 仿真器，却仍需要一个受控运行外层、完整 clock ABI 和限定 I/O 边界。它是比 E9 更窄的剩余工程/证明面，并非“安装 QEMU 即可”。若将这些宿主动作也要求为与 guest 指令同一计数器下的有限可抢占机器步骤，四对象没有这样的接口；必须改变计量层或费用模型另审，不能在本报告里把 UNKNOWN 换成 PASS。

## 7. 公共 Stop、宿主中断与来源身份

在当前离散公共 O 中，Stop/WORKER_FAIL 在其公共行处理。符合上节停驻合同的 VM 应在前一源片结束后已经停止授额；处理公共 Stop 时无需先把整个 planner job 算完再裁掉账本，也不以其私有完成输出延长来源历史。已完成的片段费用保留，已撤销提议不发布，必要真实回收独立登记。正在 REP 中间也不获得“完成本条宏指令”的额外免费容量。

但 Q3 L495–503 的 `icount_notify_exit` 只发出 kick/clock 通知；Q2 说明 decrement 高位可异步变化。它们不是“调用返回时全部线程/设备已停”的同步证明。若宿主在处理某个 helper、翻译或设备回调时故障、卡住或被墙钟 watchdog 中断，本次没有有限宿主完成保证及可靠原子收据，须区别实际停止、未确认和计量不可验证；不能根据通知时间补造源完整返回，亦不能把超时判为通过。[Q3](https://github.com/qemu/qemu/blob/v10.2.0/accel/tcg/icount-common.c#L495)

原 R0 commit `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357` 身份保持，QEMU 不修复其原生生命周期或比较器问题。计划 guest 中的来源仍应标 `R0-REPAIRED-LACAM-ADAPTER / ALWAYS_ADVANCE / FAIL_STOP_SOURCE`，另记实际 guest ABI/clock 后端。已有共同修复、全系统执行成本和新增时钟适配不能只给 D，不能归为 D 的证据查询收益；相应 D/R/E0 必须同能力、同计费规则、同失败语义。原 PIE/LACAM 核心链可计划保留，但未编译未运行，不能承诺与 native R0 逐输出相同，也没有为新的宿主噪声统计模型背书。

## 8. 可交给根的精确状态

| 命题 | 本次状态 |
|---|---|
| 固定官方 icount 文档、预算/结算入口及 guest 时钟公式有实际正文 | 来源层已核，四对象身份如上 |
| 文档所述过长 TB 会先退出、短块重译，MMIO 会计数对齐 | 官方合同已读；通用实际执行链未完整源码审计 |
| 此 x86 REP 翻译在 icount 下禁止整串内部连续循环 | 特定源函数可闭；不外推所有 helper 或退休计数 |
| 指令计数等于周期精度/宿主 elapsed 上界 | 不成立 |
| guest icount 时间可直接替代 73 公共 t 和 CPU 日志 | 不相容，已有两读/停驻反例 |
| full-system 消除了裸 CPU 引擎所缺的 guest OS 服务层位置 | 架构接缝明确；具体 guest 身份及运行仍未绑定 |
| 每行授额后完整停驻、封闭 I/O、费用闭包及实际 clock ABI | 未闭；上节三个接口是必要缺口 |
| 73 可因此变更为执行资格通过 | 否；EXECUTION_BACKEND_UNKNOWN 保持 |

本次已完成有界一手接口核验和反例分析，不再追加第五对象。后续若根继续此路线，最先需要审定的是“该内部授额点的外层停驻/设备包络”与“原源时钟 ABI 的完整映射”，而非重新泛搜计数工具。所有旧报告、P8/P9、73 与 Git 均未修改；没有实现或实验授权由本报告产生。
