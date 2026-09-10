# 73E17：根对QEMU固定身份、预算与时钟接缝的直接核验
2026-09-10，/root，NO-SKILL科研分析 / CONSTRUCTIVE / NONBALLOT。根实际全文读73E15，18619 bytes /100 LF，SHA256 3099877eee3f20a56c0b4d11a511f6580073f5b62d05bce1cea36835d8a5cfff；当前73为7197daafe3af9f1a3757ae9f230ee406dae346184064a97d51f7566d98b5a881，141042 bytes /490 LF。E15原件不改。本件补它未解析的标签身份并独立核关键原文，不授执行资格。

## 1. 实际一手身份链
根通过[GitHub tag ref API](https://api.github.com/repos/qemu/qemu/git/ref/tags/v10.2.0)实际取得v10.2.0指向annotated tag 75eb8d57c6b9577c8121e28169c3512cfe2d2544；再取[该tag对象](https://api.github.com/repos/qemu/qemu/git/tags/75eb8d57c6b9577c8121e28169c3512cfe2d2544)，object.type=commit、sha=698104725efad4b29079d857dfdebbd804e34c99。tagger.date为2025-12-23T03:44:07Z，GitHub verification返回verified=true/reason=valid。这里报告的是平台验签结果，根未独立运行PGP验签，不把它写为本地验签完成。
根先用标签取得下表三文件完整内容与API blob，实际全文读；再以该固定commit重取，三者逐字节相等。各对象在内存经UTF-8编码独立复算SHA256、Git blob frame SHA1与bytes/LF，计算blob与API一致。没有源码文件写入或构建。

| 固定commit下对象 | 根SHA256 | API及根计算Git blob | bytes / LF |
|---|---|---|---|
| docs/devel/tcg-icount.rst | 59f5b3a1db0493125ac673bd14675ca8565090f232a0b4a12bdcda928451e53d | a1dcd79e0fdd5142d6e876466e397cf8a25d6d89 | 3591 /88 |
| accel/tcg/icount-common.c | 6b85641f2ab23b7ea67d332b3b127203597bb176a54114caa582804ddfbfe868 | d6471174a3aae3310e36b175b93a1618b45cb447 | 16465 /503 |
| accel/tcg/tcg-accel-ops-icount.c | 30b346cf51c21fd3488195f8141ed58450b5e9ac9570ab7eeda3011459f03e88 | d0f7b410fab3186f0359eed2b0c50dcab7d58b3e | 5047 /160 |

固定一手链接：[文档](https://github.com/qemu/qemu/blob/698104725efad4b29079d857dfdebbd804e34c99/docs/devel/tcg-icount.rst)、[预算入口](https://github.com/qemu/qemu/blob/698104725efad4b29079d857dfdebbd804e34c99/accel/tcg/tcg-accel-ops-icount.c)、[icount与虚拟钟](https://github.com/qemu/qemu/blob/698104725efad4b29079d857dfdebbd804e34c99/accel/tcg/icount-common.c)。
根另取固定commit的[translate.c L1354–1469](https://github.com/qemu/qemu/blob/698104725efad4b29079d857dfdebbd804e34c99/target/i386/tcg/translate.c#L1354)，完整读do_gen_rep，API blob为0cb87d020125836a3e055f615c786161ba210770，与E15全对象计算值一致。根此处只读窗口，未独立取得该全文件字节，故不声称复算其完整SHA256。

## 2. 根直接判断
预算入口确实把调用者额度与内部limit取较小者，再拆到decrement/extra；结算依据原预算减余额。这给一个真实有限执行预算接缝，而非仅工具名。但内部limit也查看REALTIME timer，零额度可以触发虚拟timer处理；因此“没有额外guest指令”不等于“没有其他动作”。根支持E15关于受控外层仍需证明的结论，E16只继续这条调用链，不能无限扩查全模拟器。
原文说明过长TB在执行前退出并重译短块，MMIO重新对齐计数；根接受它在自身计数模型内的合同，没有独立读通用TB执行全过程就不扩大为所有异常/helper均闭。固定REP函数的can_loop在CF_USE_ICOUNT下为假，单个字符串迭代后回到同一指令边界；旧“整串任意长工作一次计费”的反例对这里不成立。仍不能把每次icount增加等同一次硬件宏指令退休。
根直接复算公共钟的不相容：icount_get取bias加指令数移位转换，预算内继续执行会改变读数；现73同公共PROCESS_SLICE行多次chrono可同值。另一方面，源两片之间停驻而世界O前进时，纯指令数并不随之推进。固定转换、不用自适应调速不足以解决；no-sleep分支还可按虚拟timer自行warp。必须明确区分guest内部调度时间、源所见公共t、源CPU服务日志，不能共享一个字段假装自然等价。
仅把chrono函数换接公共t也不是全外部输入封闭证明；实际ABI、vDSO、内联及必要guest时钟用途仍须列出。纯引擎翻译/宿主设备开销与业务复制/通信/输入服务必须分账，后者不能挂引擎名义免去服务容量。全系统架构能承载guest OS并不等于具体guest启动/源域/全部设备已经合格。

## 3. 研究路线取舍与下一步
QEMU路线此刻是具体但仍需定制控制外层的候选。根不把它作为论文贡献，也不把核更多模拟器代码当完成MAPF设计的替代；E16限三个新对象定位自动续跑/停驻边界后，若仍要求新增执行器，就把该复杂度明确留在路线比较中，停止泛搜。
另一新候选NP-SEALED正在交给Opus做有界因果构造：冻结输入的完整非抢占源作业可先在宿主计算，但结果/时长封存至合法虚拟完成点；途中取消明确关闭发布/新作业，所有实际已做工作及尾部全费，决不把成本裁成Stop前。它实质改变源抢占/故障服务，未被采用；能否保留固定TASK_SERVICE和原研究问题需独立证明。这里不重试C6旧题，也不把NP-LIVE或原严格服务的意见移植成它已通过。
用户新增明确最终以投稿为导向，完成大规模实验前设计后再评估会议/期刊；近期文献与改良由现有可用子代理接续独立L9/Opus C8L。新建额外代理曾实际因thread limit失败，没有新句柄；P7/L7仍实际pending_init，未重启。用户授权常规自主推进及必要阅读包更新保持，不能提前解除研究NO-GO。
本件只有只读一手核验、数学分析和文档；未实现/伪代码/构建/研究测试/仿真/配置/载荷/结果，未赋保护参数，未读35–38或受限载荷。73尚未固定未送审，六门2 PASS /3 UNKNOWN /1 FAIL、HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT保持。

## 4. E16实际完整接收后的根定点复核
73E16完整回执现已取得，根全文读取：8e477cff7ca98eb8ff8721e399443d1dc4b28bb22e939df1a99093632c6a68bc，13627 bytes /75 LF。根另经固定commit实际取得[rr_cpu_thread_fn L180–315](https://github.com/qemu/qemu/blob/698104725efad4b29079d857dfdebbd804e34c99/accel/tcg/tcg-accel-ops-rr.c#L180)完整函数，以及[CPU暂停函数L612–667](https://github.com/qemu/qemu/blob/698104725efad4b29079d857dfdebbd804e34c99/system/cpus.c#L612)。API blob分别f84342e0449196819c11bea92a1156d1f7f4264a、ef2d2f241faaa5d9da7b61caf04b5b0669e13bf3，与E16对应全对象计算值相同；根这里只取得窗口，未独立重算这两个全对象hash，也未另读第三cpu-exec全文件。
根直接看到外层while持续重新计算icount_percpu_budget，普通运行经prepare、tcg_cpu_exec、process_data后返回外层，无等待研究公共行授权的判断；这支持默认会重授额的局部结论。实际pause_all_vcpus确实逐CPU请求stop并等待all_vcpus_paused，而非仅发送kick；两者在所读代码中没有自动绑定。根因此接受需要修改运行外层的结论，不把外部异步stop当严格容量闸门。E16关于排队工作/设备的具体窗口由代理实际读取，本轮根不冒称已独立逐语句复核这些额外分支。
本轮到此停止泛查后端。C8S随后实际完整返回Opus，根独立C8SR指出全费封存的非抢占服务有条件因果构造，但时钟、故障、完成事件和原配对独立性未闭，暂不替换73；不能以简化基础设施为由重定义保护参数或降低来源资格。
