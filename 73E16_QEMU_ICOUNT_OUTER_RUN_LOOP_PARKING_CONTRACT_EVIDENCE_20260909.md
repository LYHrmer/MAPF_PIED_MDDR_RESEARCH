# 73E16：QEMU icount 外层授额、耗尽及 CPU 停驻合同

任务编号及文件名保留派发日 20260909；本轮读取、完成日期为 2026-09-10。性质：独立 NO-SKILL / CONSTRUCTIVE / NONBALLOT，一手源码有界核验，不是资格票或正式独立逻辑审查。状态：**HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT**。

## 1. 可以停止调查的明确结论

固定 QEMU 外层的默认行为已经查清：**一轮 icount 预算耗尽不等于停驻等待外部新额度；round-robin CPU 线程会返回外层并自动重新计算、授予下一轮预算。** 现有 CPU 暂停握手则确实可以等待各 vCPU 的 stopped 确认，强于单纯 kick；但它不是与本轮额度耗尽自动绑定的接口，也不表示设备及排队宿主工作完全静止。

因此，E15 的内部授额接缝可定位到具体改动边界，但当前 73 不能通过现成“启动 icount，再在宿主观测计数后发送 stop”获得精确 PROCESS_SLICE。那会留下重新授额的竞争窗口。继续采用此路线，至少需要一个**预算代际与 CPU 停驻原子衔接的 QEMU 运行外层适配**，还要承担 E15 未闭的 clock ABI 与限定 I/O 费用合同。这已经超过简单调用现成计数工具；本轮到此停止扩大 QEMU 调查，不读第四个新代码对象，不追所有设备或 helper。

对 MAPF 论文准备的建议是：把本候选记为“运行循环需要显式适配，暂不直接绑定”，而非继续把调查工具库当研究主线。它能保留原离散收费模型的方向，但必须由根明确判断维护模拟器适配是否值得；若选择更简单的服务定义，须另审其因果和成本变化，不能冒称与原模型等价。本报告不给替代服务路线投票。

## 2. 本轮对象身份与阅读范围

E15 实际全文及身份已由根确认，本轮不修改、不重复其四对象范围。新增代码严格只有以下三份，先读原授额函数调用者，再读计数耗尽处理，最后读被该线程调用的公共 CPU 事件及暂停处理。

| 号 | 官方原始对象 / blob | bytes / LF | 实际语义阅读 |
|---|---|---|---|
| R1 | [accel/tcg/tcg-accel-ops-rr.c 原始](https://raw.githubusercontent.com/qemu/qemu/v10.2.0/accel/tcg/tcg-accel-ops-rr.c) / [blob](https://github.com/qemu/qemu/blob/v10.2.0/accel/tcg/tcg-accel-ops-rr.c) | 9921 / 348 | L1–348 全文 |
| R2 | [accel/tcg/cpu-exec.c 原始](https://raw.githubusercontent.com/qemu/qemu/v10.2.0/accel/tcg/cpu-exec.c) / [blob](https://github.com/qemu/qemu/blob/v10.2.0/accel/tcg/cpu-exec.c) | 33807 / 1089 | 全文件定点检索 icount、TB_EXIT_REQUESTED、EXCP_INTERRUPT、cpu_exec_step_atomic、cpu_exec_loop 等并读相邻窗口；核心连续窗口 L687–823、L860–978、L985–1048，另读 L549–596 原子回退窗口及前部时钟/TB 执行窗口。不是全文语义审计 |
| R3 | [system/cpus.c 原始](https://raw.githubusercontent.com/qemu/qemu/v10.2.0/system/cpus.c) / [blob](https://github.com/qemu/qemu/blob/v10.2.0/system/cpus.c) | 20612 / 919 | 全文件检索 pause/resume、stop/stopped、idle、公共事件及 vm_stop，阅读命中窗口；完整函数包括 cpu_is_stopped、cpu_thread_is_idle、all_cpu_threads_idle、do_vm_stop、cpu_can_run、qemu_cpu_stop、qemu_process_cpu_events_common、cpu_pause/resume、all_vcpus_paused、pause/resume_all_vcpus、vm_stop。不是全文语义审计 |

| 号 | 原始完整字节 SHA256 | 按完整字节计算的 Git blob SHA1 |
|---|---|---|
| R1 | `fe94c401c523788d8a7a3266c7b6bdd05baf0c07e69fca49ee8be461b141913d` | `f84342e0449196819c11bea92a1156d1f7f4264a` |
| R2 | `96c9c88df8d0a7b432993f250784e635c810ac1de5552529eae0eb6e1e6886a7` | `7c20d9db122e5a1361fb71c64a9b80a6969845b4` |
| R3 | `5ab1280941c43414d61219002bacb763146cb77b94dd4e84ee516887020e804f` | `ef2d2f241faaa5d9da7b61caf04b5b0669e13bf3` |

本人尝试 GitHub tag metadata 返回 HTTP 403，未取得正文，不算本人解析成功。根随后提供其实际 API 解析：`refs/tags/v10.2.0` 指向 annotated tag `75eb8d57c6b9577c8121e28169c3512cfe2d2544`，再指向 commit `698104725efad4b29079d857dfdebbd804e34c99`；tagger 日期 `2025-12-23T03:44:07Z`，平台 verification 为 verified/valid。以上明确为**根提供的实测元信息**，本人未独立验 PGP，也未在本轮以 commit URL 重取并核对这三份字节。本文实际源码证据来自 tag URL 和上表完整字节身份，计算 blob 不冒称 API 回执。

R2/R3 的沙箱内原始 curl 连接失败，均按 require_escalated 对同一对象重试成功，没有换源规避权限。没有空正文当成功；没有运行 QEMU 或其它源程序，未安装、配置、实现、写伪代码、构建、测试、仿真或生成载荷。所有 shell/链段使用 rtk，新工件只由 apply_patch 写研究目录。没有读 35–38、受限 Q、实例数据或桌面；保护参数没有赋值。

## 3. 外层会自动续跑：已是实际源码结论

R1 的 `rr_cpu_thread_fn` L180–315 是原授额/结算函数的真实调用者。线程在 L214 进入无限外层循环；先处理等待/公共 CPU 事件，再在 L242–254 处理 warp/deadline 并调用 `icount_percpu_budget` 重算本轮预算。可运行的 CPU 在 L278–289 依次获得 `icount_prepare_for_run`、进入 `tcg_cpu_exec`、随后执行 `icount_process_data`。源码没有在普通额度耗尽返回时设置 stopped、消费外部公共行 token 或等待下一次研究服务授权。[R1](https://github.com/qemu/qemu/blob/v10.2.0/accel/tcg/tcg-accel-ops-rr.c#L180)

单 vCPU 的普通可运行情形也不会例外：内层 L307 前进到 CPU_NEXT 后结束；外层再次执行，L258–260 会重新选 first_cpu。R3 L87–114 表明可运行且未 halted 的 CPU 不满足 all_cpu_threads_idle，因此 R1 L108–122 的条件等待不会仅因上轮指令预算归零而阻塞。下一轮会重新授额。这里不依赖多核、公平调度假设或设备是否繁忙，也不把“每轮有预算”误认为“外部只允许一轮”。[R3](https://github.com/qemu/qemu/blob/v10.2.0/system/cpus.c#L87)

精确反例形状：公共源服务片只支付其有限预算，guest 是合法的持续可运行计算；首次执行耗尽并结算以后，宿主尚未提出/处理停止请求，R1 先进入下一次外层授额。新增 guest 工作已发生，即使后来把计数差补到账上，也越过原公共片的供给边界。无需无限执行或数值配置即可得到这个反例。不能以外部轮询得足够快修复它。

## 4. “补充 decrementer”与“新轮授额”是两件事

R2 L886–930 的 `cpu_loop_exec_tb` 在 TB_EXIT_REQUESTED 后先区分一般退出请求与计数耗尽。计数路径调用 `icount_update`，再以**剩余 cpu->icount_budget**填充较小的 decrementer；若下一 TB 长于剩余额度，L924–928 设置精确的下一 TB 指令数。这是同一运行预算内部的分段，不是发现了越权补充公共服务容量。[R2](https://github.com/qemu/qemu/blob/v10.2.0/accel/tcg/cpu-exec.c#L886)

真正余额归零时，R2 L768–777 的 `icount_exit_request` 在通常计数分支返回真；L872–881 的中断处理据此设置 EXCP_INTERRUPT 并离开内层执行；L687–709 将这类退出交给外层，L934–1048 展示 cpu_exec_loop 到 cpu_exec 的返回。因而“通常计数退出”确有源码路径。它返回 CPU 执行层，**没有同时宣告 VM 停驻**；R1 随后结算并重新外循环的事实独立成立。

阅读层次须准确：本轮没有读 `tcg_cpu_exec` 包装器定义，R1 直接调用该名称，R2 直接核到 `cpu_exec` 定义；不能把两者之间未读的一跳写成“本人已全文核完所有调用帧”。这不影响 R1 自身的返回后自动续跑结论，也不靠该未读包装器推断设备静止。

还看到两个不能省略的分支义务。R2 L690–696 为 replay 待处理异常允许设置不含 CF_USE_ICOUNT 的下一指令标志；L773–775 对这种标志不按余额归零退出。R1 L294–298 在 EXCP_ATOMIC 时先完成通常结算，再调用 `cpu_exec_step_atomic`；R2 L549–596 显示其独占、短块执行形状。这些是源码存在的分支，**不是本次选定单 vCPU、普通运行一定会触发的证据**，亦未证明无计费漏洞。将“任何返回都立即发布准确源片收据”作为适配合同之前，必须限定这些分支不可达，或在同一已授权预算内定义其结算；不能继续把所有返回当一个普通结束。这里不扩查所有触发 helper。

## 5. 真正的 CPU 暂停握手与其限制

R3 L612–667 给出实际握手。外部 CPU 线程以外的正确调用上下文执行 cpu_pause 时，设置 `stop` 并请求退出；CPU 到达公共事件处理后，L442–460 的 qemu_cpu_stop 清 stop、置 stopped，并通知 pause 条件变量。`pause_all_vcpus` 禁用 QEMU 虚拟钟，向各 CPU 请求暂停，按函数所示 BQL/replay 锁协议等待 `all_vcpus_paused` 为真，然后返回。它检查的是确认字段 stopped，强于“已经发信号”。[R3](https://github.com/qemu/qemu/blob/v10.2.0/system/cpus.c#L612)

实际停驻路径可分段对应到已读语句：请求 stop/退出 → R1 执行返回/不再满足 cpu_can_run → R1 的 rr_wait_io_event 调用 qemu_process_cpu_events_common → qemu_cpu_stop 写 stopped 并通知 → 暂停等待方观察全部 stopped。未 resume、无其它改变状态的控制行为时，R3 L331–340 排除已 stopped CPU 继续 guest 指令；R1 下一外层可以进入 idle 条件等待。R2 L752–765 的 kick 本身只写退出相关标志，不能代替这份确认。

但三个限制均有实际语句支持。第一，暂停请求到确认之间可能先执行 guest 指令；这个接口没有与指定指令预算绑定，不能由外部请求时间推出精确收费边界。第二，R3 L453–460 在处理 stop 后仍调用 `process_queued_cpu_work`，R1 的 idle 条件也会因 work queue 非空而让 CPU 线程处理工作。stopped 约束 guest 指令，不等于全部宿主回调停止。第三，R3 L294–321 的 do_vm_stop 在暂停之后还有状态通知、block drain/flush 等动作；不能将 STOP 事件或 CPU 确认升级成“所有 I/O 已完成且费用有限”的总收据。[R3](https://github.com/qemu/qemu/blob/v10.2.0/system/cpus.c#L294)

`vm_stop` 若从 vCPU 线程调用，R3 L742–755 是提交停止请求并 cpu_stop_current 后返回，源码还留有返回设备代码的 FIXME；它不是当前线程同步完成全部停驻。若从其它上下文调用则走 do_vm_stop，仍需满足正确锁/线程前提。本次没有读取 QMP 命令解析或给出外部命令使用合同，更没有运行这些接口。

## 6. 最小接入与为 MAPF 增加的必要复杂度

原 E15 候选若保留，最小接入点现可明确为：**R1 完成本次通常执行结算、尚未进入下一次自动授额之前，必须以同一预算代际决定继续当前已付片段还是转入确认停驻；新的公共源片授权到来之前不得重走自动授额。** 这是一项未来受控运行外层适配的语义要求，不是本文生成的代码或伪代码。不能用外部 stop 追赶已经重启的循环；也不能仅改 prepare 的参数而留下外层无限调用。

接口必须同时区分普通片额度耗尽、提前 I/O/异常退出、真正源事务结束、硬 Stop、未确认故障。同一源片未耗尽的提前退出只能在原余额内继续；完整结算只发布一次。原子/replay 特殊路径须有可执行域限制或同预算处理，既不凭源码存在宣称实际违规，也不假设它们自然被覆盖。公共 Stop 先撤销后继源授额，随后保留既有生命周期的真实回收确认；CPU stopped 不等于进程死亡或对象已安全释放。

这只关闭“应该改哪一层”的不确定性，没有取消 E15 的两个大项：源 chrono/CPU 日志与公共 t 的 ABI 映射，以及限定 guest/设备 I/O 的信息与费用边界。全 guest OS/loader/库指令仍有费用；排队工作、设备、翻译、回收的宿主费用不能由 icount 代替。固定模拟器版本与适配差异需要形成可审计的构建身份，未来才有资格讨论重放；当前没有实际构建。

对研究范围的直接代价是：维护一个修改过的执行循环及其暂停/异常接口，并固定 guest 与时钟 ABI，才能把成熟 MAPF 规划核心放进精确离散服务台。这些工作支持评价可信度，但本身不证明前缀协议、付费观测策略或大规模 lifelong 性能的新颖性；所有相应内部臂共享这些修复和开销，不能计作 D 的方法收益。除非该严格服务模型的科学必要性足以承担这项基础设施工作，否则有充分理由在这里停止后端深挖，由根比较已明确改变语义的更简单共同服务候选。这个停止依据是实际调用结构及必要适配复杂度，不是为了让资格表更容易通过。

## 7. 完成范围

本次可闭：通常计数额度耗尽的局部返回路径、默认 RR 外层自动重授额、CPU 暂停请求/确认握手，以及 CPU stopped 不能替代全部外部工作的静止证明。仍未闭：完整严格公共行适配、所有必要异常域、公共 clock ABI、限定 I/O 与完整费用/回收。不声称已经实现或证明全系统可直接用于主实验。

新增代码对象到三份即停止。E15、73、旧报告与 Git 未修改；没有参数、镜像、命令配置或实验工件产生。最终资格状态保持 HOLD。
