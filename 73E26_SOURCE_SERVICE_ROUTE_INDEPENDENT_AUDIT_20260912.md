# 73E26：源服务路线独立有界核验

2026-09-12；/root/source_service_audit；NO-SKILL / CONSTRUCTIVE / NONBALLOT。本件只结束已授权的源码/API阅读与路线判断，不是正式审查或执行资格票。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT保持。

## 1. 明确选择

建议选择**全站确定性模拟工作计量，真实宿主CPU/elapsed/内存独立报告**，作为下一完整设计的计算模型。有限供给、FIFO、收费读状态、后继发表、处理等待和处理期间物理/真实任务继续均保留；取消“模拟基本步等于本机机器指令或真实CPU硬配额”的主张。原保护参数保持原义且UNASSIGNED。这是计算模型变更，不是把未实现后端判为设计失败。

原严格PROCESS_SLICE需要真实执行前闸门与公共钟绑定；P29非抢占实测elapsed虽有条件非预知，却把宿主历史带入Q，并未解决其它站的发布计量。两者都不应继续充当唯一可选前提。确定性模型保留研究“空间证据在有限处理/通信资源下能否改善真实服务”的问题；结论只能对明示模拟机器成立，不能宣传为实机吞吐或任意计算平台不变的优势。

根已通知新稿采用P_model；本代理没有审读该新稿，以下只对已读输入与接口负责。

## 2. 实际输入范围

完整读取20260911交接、P29、C22的prompt/raw/receipt、E17、E25、C8SR、E8及C24完整receipt；读取当时73的完整§8/9/10/12，截断处分别补齐。科学输入是旧主稿SHA256 **9e06199cc6045ddd750b861b3091ec239c7c6ff2ae7eeaebbdd0e7fde61ec113**（216498 bytes/665 LF），不是根刚修订的新身份。

E8具体否决fork/COW＋普通墙钟组合，没有评估或否决Wasmtime。C23/C24及E25在本轮开始前已存在；C24引用P32，但本轮具名文件检索未找到P32，不据其文字假定该组合报告已交付。研究目录及/home/lyh的AGENTS.md、研究目录.codegraph本轮均不存在，未创建索引。

直接读取固定R0 commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357的[MAPFPlanner.cpp全文](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp)：初始化、loadPaths、plan分支及planner_commit之间确有不同工作，cout/endl和exit也真实存在。完整源体不能只测plan函数；日志写出和提交不能藏为免费尾部。另读本机/usr/include/c++/11/chrono L1114–1194，high_resolution_clock明确alias system_clock；该类型名字不证明单调，也不证明未来Wasm链接身份。误猜lacam2头路径两次404，未获得该对象，不据此补造取时覆盖。

## 3. 三条路线的实质边界

| 路线 | 可保留的具体结论 | 本次选择 |
|---|---|---|
| 严格本机指令/CPU片 | E17已定位QEMU预算、外层重授额、暂停握手与公共chrono不相容；不是所有模拟器均不可行 | 不再把定制QEMU控制器作为本研究设计闭合的前置条件 |
| P29非抢占源＋原行发表 | a+d可作隐藏阈值；严格后继行防同一行递归；AA正常历史与中心接纳分开 | 保留备选，不作为新主模型；源硬故障须显式改REVOKE_AND_DRAIN，实测elapsed推断另需合同 |
| 确定性模拟基本步 | 状态转移只依合法输入、固定表示/操作法、公共O及独立block创新；宿主求值耗时不回写模拟时刻 | 推荐主设计；工具仅作未来实现候选，不把某工具默认fuel冒充完整基本步表 |

P29将处置核验移到原Srv_P发布容量，确实修补“删除原指令片后收件无执行载体”的接缝；若该容量仍指未具备的真实CPU硬闸门，问题只是移位。pending是有定义状态，不能由停滞推全世界无定义；也不能靠所有路径pending冒充有效研究域。非抢占撤权与原硬终止不得同时宣称成立。

直接读[Linux取时说明](https://man7.org/linux/man-pages/man2/clock_gettime.2.html)中的钟域、返回/版本等窗口及[pidfd说明](https://man7.org/linux/man-pages/man2/pidfd_open.2.html)的DESCRIPTION至NOTES：BOOTTIME包含挂起，进程CPU钟计线程CPU，分辨率不保证读数严格递增；pidfd身份、可读退出通知和wait终态不是同一事实。这支持非抢占计量/退出接口设计，不提供精确片停止。新确定性主模型的源chrono应由声明公共时刻供应，不能默认接这些宿主钟。

## 4. Wasmtime实际已核与未核

读取的官方Rust API页面自标 **wasmtime 50.0.0-dev**。这是滚动开发版文档，**没有成功绑定稳定发行版、固定commit或未来二进制**。固定commit请求未取得可用身份；最后网络调用被打断，没有后续成功回执。本件据已得正文结束检索，不猜版本。

1. [Config::consume_fuel及epoch说明](https://docs.wasmtime.dev/api/wasmtime/struct.Config.html#method.consume_fuel)明确支持确定性fuel计量；fuel耗尽产生trap。epoch是不同的非确定性中断机制，不能代替主模型计量。
2. [Store::fuel_async_yield_interval](https://docs.wasmtime.dev/api/wasmtime/struct.Store.html#method.fuel_async_yield_interval)要求async入口，可按fuel间隔暂停并让调用方重新取得控制。Future会自行标记可再poll，因此“有yield”不等于“已等到下一公共行”；外层只可在获准行恢复同一调用，不得由通用executor自动续跑。同一future的协作暂停/后续继续有接口依据，未证明任意一次poll精确等于一片或任意研究基本步数。
3. [TypedFunc::call_async](https://docs.wasmtime.dev/api/wasmtime/struct.TypedFunc.html#method.call_async)返回原调用结果或trap；Config的async_stack说明每次异步调用有独立运行栈。应区分保留暂停future和重新调用函数：后者不能假装恢复原PC/调用栈/随机历史。耗尽trap也不能直接当可恢复暂停；本轮没有读出“trap后从原位置续跑”的保证。
4. 官方Config明确fuel/epoch不处理阻塞host call；bulk memory操作内部也没有一般逐字节抢占承诺。dev文档的operator_cost/OperatorCost::variable提供按字节、元素、页计费的入口，但本轮未核其固定实现、边界扣费和yield精确性，不能称已满足M1。Store::set_hostcall_fuel只限定component guest向host传入的数据规模，不是所有host计算的CPU计量。
5. C++/Boost迁至Wasm/WASI改变ABI、标准库、分配/浮点及随机调用实现；时钟、熵、日志与文件必须用明确授权imports。不能把本机Boost/chrono身份证据继承为Wasm已合格，不能称native逐结果等价。R0与ECBS采用相同计量规则但仍各付自身搜索、适配、日志与失败工作，不强求两者实际成本相同。

故Wasmtime提供一个可信的实现方向，尚不提供完整后端资格。模拟规则可以先完整审查，未来再按规则检验这个后端；规则不得反过来随工具不足或有利结果暗改。

## 5. 设计审查与未来资格的分界

现在必须闭合的是：基本步与表示；变长操作不恒价；host业务进口的收费及暂停边界；发布/处置归属；同原行动态guard的收费与失败；源时钟和AA；故障撤权；全部线上费用与宿主账分离。已知未修的越界/UB、同一条款同时要求非抢占与精确硬停止、或将未映射宿主时间输入Q，属于实质设计问题。

未来资格验证的是：固定工具链/模块/import清单；操作法与实际yield/恢复符合性；跨行clock和持续状态；表示耗尽/异常；日志/计量/退出回执。未构建、未测量、没有完成所有库的机械证明本身不等于设计FAIL。资格仍须在主实验前完成；没有证据不能把不明源行为统一填零、删roster或声称已有性能。

若采用确定性模拟法，STRICT仍预付原共同供给，NATURAL记实际工作；不足不烧掉未执行额度；PARTIAL_GUARD不自动消耗尝试水位；SOURCE_EXCEPTION不令已经合法运动的实体瞬时HOLD。费用记账和确定性都不能替代完整primitive定义，宿主费用亦不得漏报或混成模拟CPU。

本件唯一新增工件通过apply_patch写入；未改旧报告/主稿/规划/Git/桌面，未调用Claude，未实现、写伪代码、构建、测试或实验；未读取/生成受限载荷，未赋保护参数。本文完成不授设计GO或实现授权。
