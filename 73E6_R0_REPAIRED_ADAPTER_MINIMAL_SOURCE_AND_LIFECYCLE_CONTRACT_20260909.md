# 73E6：R0 修复适配的最小源码差异、初始化与生命周期合同

日期：2026-09-09。任务 /root/source73_r0_remaining_contract。**NONBALLOT / NO-SKILL；供根独立判断的建设性纸面合同，不是正式审查，不代表采用、固定或通过。** 当前保持 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT；没有源码修改、实现、伪代码、构建、测试、仿真、调参或实验载荷。

## 1. 本件只提出一个可纳入候选的方案

建议名称为 **R0-REPAIRED-LACAM-ADAPTER**，其来源仍是 YueZhang-studyuse/LMAPF-delay 的固定 commit `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。选择如下唯一组合，不并列互不相容的备选：

- 使用 73 已要求的隔离事务 worker，规划对象及其整个可变地址空间归该 worker；初始化在其中同步调用。适配轨不进入原 driver、BaseSystem::simulate 或 BaseSystem::planner_initialize。
- 首次 plan 的初始化预算来自已经验证的必填输入，显式按值传给 MAPFPlanner::plan；不读取 BaseSystem::init_time_limit，也不假称原 CLI 接线已经修好。
- 内核源码内部只拟修正 Instance::computeAllPair 中局部 Node 比较关系：按 value 使用严格“大于”，相等时双方均不优先。不换 all-pairs 算法、不导入免费距离缓存、不改四个 LLNode 随机谓词来掩盖模式边界。
- 失败／超时撤销发布资格，终止及回收整个隔离进程；不在活线程上 delete planner/env/lns，不复用原 detach。正常淘汰也采用同一种完整进程回收，避免另设未经证明的跨线程 C++ 对象销毁路线。
- 所有共享 R0 比较臂使用相同修复、来源 profile、worker 事务机制、预处理和计费接口。D 与对照的区别只来自后继固定协议允许的查询／证据策略。

“最小”限定为保留具名 R0 求解路径、仅一处内部比较关系修正及一个外部生命周期入口，**不表示新的监管／计量运行时已经存在或无需资格证明**。事务快照、暂停计量、进程回收和实际库绑定仍有具名未闭项，不能用这份规格将 G3 改成 PASS。该修复适配只是下一候选可选择的来源轨，不能取消独立已发表外部基线，也不把它宣布为研究唯一答案。

## 2. 输入身份、亲见范围和继承范围

本次核得 73 当前实际 SHA256 为 `decef3a8908b21796c3ff86eaf2a8361289c76d13cbd09b1f45d66c1b138b38f`；其仍是未固定草稿。73E5 实际 SHA256 为 `cee608755ed49b43f690bcfe0c8bd56d827b5fea0365b6eac7f26c2b32a8ea53`。本次重新分段读取 73E5 全文；73 只按具名入口读取 §8–9 的 worker／时钟／收费条款及相关定位，不冒称本轮重新全读 73。原交接和 E1/E3/E4/72E5 的读取身份继承 E5，不假称本轮再次重取。

本件最多三个明确来源下一跳：固定 R0 的 MAPFPlanner.h，以及 POSIX Issue 8 的 wait 和 kill 两个官方页面。没有递归仓库、扫描目录或打开任何输入载荷。两页 web 先返回 403；同一 URL 的 raw curl 随后实际取得正文。wait 同页重取时一次连接失败，按 require_escalated 重试成功；没有改用其他来源绕过权限，也没有将失败响应的空正文摘要当作证据。

| 本次新亲见对象 | 身份 | 实际阅读层次 |
|---|---|---|
| [R0 inc/MAPFPlanner.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPFPlanner.h) · [raw](https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPFPlanner.h) | Git 返回且独立重算匹配 blob `68fbfd7a13d2a1513c6634d41d0dca5133740aeb`；SHA256 `d25fbcb08b6d80b4f03234b4f7c3c08c553d7074a7e12c47fee86d336409633e`；971 bytes／42 行 | 全文；lns 在声明处为 nullptr，两个构造、析构、公开调用接口与选择字段 |
| [POSIX wait/waitpid](https://pubs.opengroup.org/onlinepubs/9799919799/functions/wait.html) | The Open Group Base Specifications Issue 8／IEEE Std 1003.1-2024；本次 HTML SHA256 `8c9d5d9bf54b098e460832d466503567376fdd61d24cbef0d461389d113a36e5`；36271 bytes／595 行 | DESCRIPTION、RETURN VALUE、ERRORS 全部规范段；初次混合输出裁剪后，已单独重取并完整显示这些段；不称全文历史注释均精读 |
| [POSIX kill](https://pubs.opengroup.org/onlinepubs/9799919799/functions/kill.html) | 同一 Issue 8；本次 HTML SHA256 `779bf66b859e9d5f10c5adc4ccac0afb2b1088daa3eaaa81a22e40751f1a0cc2`；15293 bytes／219 行 | DESCRIPTION、RETURN VALUE、ERRORS 全部规范段，以及关于不能用空信号代替子进程终止查询的 rationale |

这些页面是接口标准证据，不是所用内核、libc 或监管器实现身份证明。来源文件只在工具内存读取、散列，没有落盘源码或 HTML。一次本地精确读命令拼错旧报告文件名而返回不存在，随后使用正确具名 E5；没有据此展开目录扫描。

根另完成 [73E7_ROOT_HOST_BOOST_174_IDENTITY_AND_PAIRING_HEAP_CONTRACT_20260909.md](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73E7_ROOT_HOST_BOOST_174_IDENTITY_AND_PAIRING_HEAP_CONTRACT_20260909.md)，本子代理已实际全文读取该完整回执并核得 SHA256 `9c0e7effe9320ae5e91199b4162bd8d5f2a35369d28e045d4577056db5059a09`。E7 记录 /usr/include/boost/version.hpp 可见 BOOST_VERSION 107400、BOOST_LIB_VERSION “1_74”；c++ 为 Ubuntu 11.4.0-1ubuntu1~22.04.3，glibc 2.35，Linux 6.8.0-138-generic x86_64。**系统文件和命令是根亲见，本子代理亲见的是完整 E7 报告，没有另取系统头。** 根已把本次核定的 1.74 头文件选作本适配器的纸面参考 Boost 合同；本机头身份不再完全 UNKNOWN，未来实际构建仍 NOT_CONFIGURED / NOT_BUILT。

E7 给出的本机 pairing_heap.hpp SHA256 为 `668543a7a2ab2b4519452a5f841d36f30761cb99b102e3273d999adb3afe9fcd`，stable_heap.hpp 为 `24d78657787040120778df3d60396c1b1c16d6f5babc612431a028b9a387e371`。这两个完整字节身份恰与 E5 条件 1.85.0 所读对象相同，但本件采用的是 E7 对本机 1.74 实际窗口的直接核验，不以版本近似推论替代正文。未核的其余 Boost 文件、编译解析与实际产物不因两文件相同而整体通过。

## 3. 明确的保留、删去与拟修改点

以下是将来获准实施阶段的差异规格，不是本次实施记录。原 R0 快照保持原样身份，所有差异进入单独补丁／适配身份；不覆盖原作者 source hash。

| 原位置／行为 | 本方案的单一处理 | 对保真和归因的影响 |
|---|---|---|
| src/driver.cpp 的系统构造、参数 setter、simulate；inc/CompetitionSystem.h 与 src/CompetitionSystem.cpp 的原系统入口 | 从适配轨入口中移除调用；原文件不改，保留在原样档案。新入口直接拥有 MAPFPlanner 的工作进程 | 明确是内核适配，不能叫原生 PIE-D 全程序复现 |
| BaseSystem::init_time_limit 的缺失初始化／CLI 未接线 | 适配入口禁止引用此成员；从必填输入得到首次 plan 的独立预算字段，验证完成后显式传值 | 消除所选入口对该未初始化读取的依赖；不证明原入口已修复，也不把 plan 内部覆盖当豁免 |
| BaseSystem::planner_initialize 的 packaged_task／局部 init_td／wait_for／join／detach，及 simulate 的无状态继续 | 整段不进入；由 worker 同步初始化及监管状态机替代 | 不保留 ready 即成功，不保留超时 detach，不补一个 future.get 后继续沿旧失败路径 |
| Instance.cpp L143–149 的第五堆比较关系 | 只将非严格 value 顺序改为严格 value 顺序，相等为等价优先级 | 这是实质源码修复；不承诺与不合格关系下的原运行顺序／性能完全等价 |
| MAPFPlanner::initialize、loadPaths、plan、planner_commit；具名 LACAM 求解链 | 保留调用主体、顺序和分支；只在外层加输入资格、事务与结果接纳边界 | 不插入替代搜索、免费预解或成功重试选择；外层拒绝／失败照常计费 |
| 原 simulate 中只包住 plan 的性能计时窗口 | 原样档案保留；适配轨以完整服务费用为比较账，不采用原窗口作为总开销 | 预处理／加载／提交费用变化属于共同适配，不属于 D |
| MAPFPlanner.h 的 env→lns 析构次序 | 本件不据臆测修改该 header。适配 owner 不手动调用该总对象析构；对象存活至整个 worker 退出，外层仅在回收确认后清理自己的引用 | 这是整体回收的生命周期差异。不能据此宣称内部局部对象／构造失败展开不再需要库合同 |
| 原文件／信号保存、全局 system_ptr 清理路线 | 不进入适配轨；日志、结果只经付费消息转交监管端 | 不调用原 driver 信号处理器保存共享研究状态；worker 无物理实体、权威账本或研究文件写权限 |

新亲见 MAPFPlanner.h 已给 lns 声明初值，故本件**没有虚构“lns 也未初始化”并提出多余修复**。源析构先删除 env，再删除 lns 是亲见顺序；本件不据此宣告运行中已经出现悬垂使用。整个进程回收可以避开适配 owner 主动沿这个次序析构，但正常函数返回和异常展开中的容器／局部堆析构仍会发生；不能拿隔离进程取消那些前提。

## 4. 总输入接口：初始化预算不再来自未赋成员

一个适配实例的输入分为来源身份、软件 INIT 输入和规划事务输入。所有字段是规格中的类型位置，本件不填值、不产出 manifest。

来源身份必须能唯一指向 R0 commit、拟修改的那一处比较关系及完整适配差异、选定 LACAM 类别、编译 ABI、实际库、时钟／随机映射、计量与隔离运行时。未固定身份进入 UNINSTANTIATED；身份矛盾或非白名单改动进入 INPUT_INVALID／PROTOCOL_OR_SOURCE_INVALID，不通过“先随便跑一次”补身份。

软件 INIT 输入必须含初始化预处理预算、**首次 plan 的预算**和后续 plan 的预算这三个有区别的必填字段，以及现有来源需要的提交语义字段、合法 SharedEnvironment 和 profile 身份。字段可用与其源接口匹配的类型表达、来自哪个获准 manifest 项、是否通过合法域验证，必须在构造前已有记录；缺失时不创建工作对象，不继承栈垃圾、全局偶然值或新默认值。首次预算不是 H 或其他保护参数的别名，也不替它们改变含义。

外层初始化截止边界与三个源调用预算分账。本方案选择从本臂软件 INIT 入队的公共行开始衡量初始化期限，包含排队、解析／复制、worker 创建、computeAllPair、LNS 建立及 READY 消息接收／验证；不从首次取得 CPU 服务时重新起算，不在失败后重置。边界本身须在未来共同协议中具名固定，本件不给数值、范围或默认值。源预算传入后，MAPFPlanner 原本的 runtime limit 设置、覆盖、递增和原时钟读取语义仍按 73 的映射保留；外层生命周期超时不冒充原内部返回条件。

规划事务输入继承 73 §8：只含已交付知识、不可变路径历史尾、合资格任务投影、合法可复用未来段及版本，不取隐藏实际位置或未来任务。在 loadPaths／clearAll／commitPath 前，外层资格必须覆盖输入外层与 agent 索引匹配、需访问的目标非空、位置合法、路径锚点及输出容器形状。输出只有经过全体 agent、共同段长度、顶点／对向边及历史版本检查才可接纳；单个原函数返回 true 不代替这些前提。

初始化完成后，中心在自己的付费提交中向首个合格规划事务绑定首次预算，并单调消费该来源会话的首次事务资格；worker 到达 plan 时显式传入该事务携带的预算。尚未创建合格事务的输入拒绝不消费资格；已经发布的首个事务即使取消、失败或结果拒收，也不退还首次资格，后继事务读取后续预算。该记录位于 worker 快照之外，与源内 initial_run 字段分别记载，不要求中心无费窥视 worker 恰好执行到哪条指令。这是明示的适配调度规则，不宣称原 native 有相同取消机制。选择字段在 MAPFPlanner::initialize 将其映射成 algo 之前，已经由适配输入明确指定 LACAM 类别，不依赖 header 中另一个模式的默认 algo 或未赋 mapf_planner。source 中已有常量与覆盖语句不在本件擅自调节。

## 5. 同步初始化与失败传播：不再保留 future 成功歧义

worker 只在 Srv_P 获得付费执行片段时推进同步初始化。监管端的消息等待是异步通信，**不是继续使用原 packaged_task/future**。因此 future 的 ready、原 bool、日志 fatal 文本和 join 是否返回，都不是本方案的初始化成功信号。

| 初始化内部状态／事件 | 唯一可产生的外部结果 | 允许的后继行为 |
|---|---|---|
| 输入尚未完整合格 | UNINSTANTIATED 或 INPUT_INVALID | 不构造内核；保留已发生的验证费用 |
| 已构造 worker，初始化未完成 | INIT_PENDING | 仅继续有费初始化／等待或受控停止；禁止 loadPaths、plan、commit |
| MAPFPlanner::initialize 正常返回，入口后条件与完整消息已封存 | INIT_RETURNED，仍不是中心 READY | 等待中心独立付费验证；不自行规划、不授予实体权限 |
| 中心在截止／取消之前验证 INIT_RETURNED 的 job 身份、来源身份与后条件并发布 | INIT_READY | 后继公共行才可建立首个规划事务 |
| 同步调用或后条件检查抛出可捕获异常 | INIT_EXCEPTION | 记录阶段／异常类型及费用，取消发布资格，转停止回收；不能继续 plan |
| worker 明确非正常退出、消息残缺或原 source 显式退出 | INIT_SOURCE_FAILURE，或无法核明时 UNVERIFIABLE | 不补作成功；转停止回收／状态核验 |
| 公共截止或取消先于中心 READY 发布 | INIT_TIMEOUT 或 INIT_CANCELLED | 先撤销资格，再停止回收；迟到的 INIT_RETURNED 不恢复资格 |

INIT_RETURNED 的后条件至少包括：对象构造及初始化主体已返回；env／instance／lns 的所有权属于同一隔离执行域；预处理结果形状与输入版本相容；LACAM 选择已经显式生效；所需输入合法域仍成立；消息所引用数据完整封存。它还必须携带已付费建立的初始化结束检查点，只有中心 READY 发布后该检查点才成为首个规划事务的基准；在此之前不能自行使用。检查点建立也落在 INIT 截止范围内，失败／超时后的检查点按引用规则回收。形状检查不是 all-pairs 正确性的替代证明，数学和来源义务仍见 §7。可捕获异常边界也不声称可以捕获任意 UB；源／运行时域不成立时按 source invalid 处理。

初始化成功后仍没有免费的首条路径。第一次 loadPaths、plan、planner_commit、结果复制与验证均是普通付费事务。初始化失败不让 simulate 继续，因为适配轨没有那个调用边；失败记录进入全 roster，实体保持 73 已有 bootstrap／HOLD 责任，物理时钟和真实 TASK_SERVICE 不因软件失败冻结。

“先成功但后来才收到”由公共行序裁决：中心 READY 发布尚未完成而截止已生效，结果为超时；不能按 worker 私有完成时标倒写中心历史。消息到达、验证未结束时仍是 pending。故既不以 future 就绪代替成功，也不以源码某行返回代替中心已提交的权限。

## 6. 隔离所有权、事务状态与停止回收

### 6.1 唯一所有权和事务机制

规划对象、SharedEnvironment 副本、Instance、LNS／Agent／求解器、堆、容器、所有过程内可变静态状态及 C/MT 随机状态，都属于同一受控进程执行域。外层持有带来源和生命周期 generation 的 worker 句柄及不可变消息，不能持有可用于跨进程解引用的原对象指针。进程无物理控制、权威账本修改或研究文件写权限；禁止未登记的后代进程／后台线程逃逸该执行域。

为落实 73 已有“丢弃状态不继承”要求，本方案选定**保持虚拟地址关系的完整执行域检查点／恢复**，不复制 C++ 裸指针对象图，不在丢弃后通过重新播种冒充回滚。最近一次被接纳的 core 状态是只读检查点；同一时刻只允许一个活动规划事务和一份待处理结果。恢复、检查点建立、写时复制的实际物化、内存保留与清理均收费。所有仍影响后续行为的进程内状态必须被检查点覆盖，过程外时钟、熵、文件或同步对象则必须通过既定映射，不可漏在状态外。

活动事务从该检查点恢复后，先付费把本事务冻结输入安装到其私有 env 的合法存储中，保持 Instance／LNS 所依赖的对象地址及固定地图／来源身份；不得误用上一次 env、以外部可变引用替代复制，或把地图变化悄悄接到旧预处理表。完成输入安装和资格检查后，依次走所选原 loadPaths、plan、planner_commit 主体；完成结果与该事务结束状态一起封存。中心通过当前 PROJECT／版本 CAS 后，才可将该结束状态登记为下一检查点。过期、异常或被取消事务的状态不提升；保留旧检查点。中心在自己的提交中只改变不可变版本引用，完整复制已经由所属作业付费完成。检查点仍被任何有效事务／消息引用时不删除。外部公共时钟、完整费用账、已消费的首次事务资格及取消／版本历史从不随 core 快照回滚；源时钟读取继续由当前公开时刻和该 job 已完成付费服务映射，不能恢复旧时刻来追回预算。

这里选择的是完整执行域机制，并没有声称现有主机已提供合格实现。**检查点保存／恢复的实际工具、ABI、地址与运行时状态覆盖、有限计量边界均未取到实现正文，保持 UNKNOWN。** 不能退化成“随便 fork／memcpy 应该等价”，也不能绕过这项直接运行。若该机制不能资格化，应由根调整候选及重新审查；本件不静默切换到别的状态策略。

### 6.2 停止与回收是不同状态

生命周期分为 LIVE、STOP_REQUESTED、REAP_PENDING、REAPED、RELEASED。STOP_REQUESTED 立即禁止新的规划输出获得接纳资格，但不是“对象已经可以删除”。REAP_PENDING 保存完整 owner／generation／费用记录；REAPED 要求可信终止状态和执行域完整退出证明；RELEASED 还要求所有外部不可变消息／检查点引用已完成或失效并完成付费清理。

监管器是该 worker 终止状态的唯一消费方，按创建回执、进程身份与 generation 匹配结果，防止 PID 复用或其他等待者消费状态造成误认。只发送终止信号、收到 SIGCHLD、子进程停止、空信号查询成功、WNOHANG 尚无状态或一个不明 ECHILD，均不能发布 REAPED。EINTR／未就绪继续作为待处理事件；没有固定时间内一定回收的假设。该区分有 [POSIX wait/waitpid 的状态及返回合同](https://pubs.opengroup.org/onlinepubs/9799919799/functions/wait.html) 和 [kill 的发送／错误合同](https://pubs.opengroup.org/onlinepubs/9799919799/functions/kill.html) 支撑，实际主机实现仍待绑定。

正常淘汰、初始化异常、超时和运行异常均走整体进程退出／回收，不在仍执行源调用的线程上运行外层 planner 析构，也不在 detached 线程之后删除 env。外层自己的句柄、输入消息和共享不可变存储直到对应引用消退才释放。一个源调用里可能发生的正常局部析构／异常展开是另外的库义务，不能因最终进程回收而省略。

若终止确认迟迟不能取得，仍有定义的状态是 REAP_PENDING；该 planner 服务容量不能交给下一事务，资源保留费用继续记录。其他实体物理过程继续按已提交责任运行；不能把未回收 planner 记成空闲，也不能用新 worker 并行越过这次滞留。若监管／执行域身份或用量无法核清，记录 UNVERIFIABLE／PROTOCOL_OR_SOURCE_INVALID，不能给常规合法搜索超时记账后假装可以恢复。

### 6.3 取消与计量不能靠免费后台线程完成

Srv_P 的正常推进、初始化、停止控制、检查点和回收管理使用同一登记服务域；Srv_C 的取消发布及结果拒绝使用中心付费提交。取消请求仅使后继服务不再授予 core 计算权限，控制、核验和清理自身仍占所属容量。不得持有中心槽阻塞等待 worker，也不额外安排不收费的清理线程。

合格执行后端必须保证：只有已授予的有限 PROCESS_SLICE 能推进 worker；暂停期间没有未登记的 source／库工作；取消在明确有限执行边界转入停止阶段；若一个片段不能完成某个动作，状态与剩余工作继续保留而非瞬时完成。POSIX kill/wait 接口本身不提供这一指令计量保证。若真实宿主在逻辑暂停或取消后仍运行，所有这样的工作必须完整计入相同用量和物理进度映射；不能核清就使该次执行不可验证，绝不补成零费用。

观察期终点不等于允许丢掉仍活 worker。到 Stop 为止的资源占用和真实服务按原观察期记录，Stop 后仅为清理发生的用量单列，不能产生被计入观察期的算法结果或任务完成。尾部回收未闭时不得把费用账标为完整；尾部费用不能后移隐藏成 D 的吞吐改善。

## 7. 第五堆的唯一修正与实际 Boost 绑定

E5 已证 Instance::computeAllPair 在 MAPFPlanner::initialize 中先于 LNS 建立，而且使用局部 pairing_heap；其 value 比较关系不可自反性失败，不能被四个空 LLNode 堆豁免。具体定位继承固定 [Instance.cpp L129–186](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/Instance.cpp#L129) 及 E5 的完整对象指纹，本件未再次获取该源对象。

唯一拟修正为严格 value 优先关系。对有效整数 value，该关系不可自反、传递，等价类由相同 value 构成并满足传递；不加入随机平局消耗或位置次级键。computeAllPair 的起点循环、初始距离、邻居展开、改善条件、入堆／出堆、存储结构均保持原样。修改后数学目标是同一合法单位代价图上的最短距离；需要在合法索引、可表示距离、有限图及实际堆优先语义前提下给出不变式证明，不能仅凭换成严格符号宣布 all-pairs 已证明正确。

平局访问次序可能改变，原不合格比较关系下不存在可据此保证的标准顺序，所以本方案不声称逐指令、逐节点或性能等价。若距离输出一致，那也只是限定合法域上的结果性质；修复可能改变初始化工作量与后续时序，须作为共同适配成本，不能归入 D 的机制收益。

实际绑定的通过条件不是“机器装了 Boost”或 CMake 的最低版本声明。本方案的参考合同已按根 E7 限定到所核本机 1.74；未来唯一 profile 必须给出实际解析头文件路径与内容指纹、真正参与编译的版本和选项、编译器／标准库／ABI／平台身份以及产物可追溯性；本次不构建来生成这些。与参考身份不一致时为 DEPENDENCY_NOT_MATCHED，不继承该合同。E7 已补构造复制比较对象、空析构、非空 pop→erase→merge 和两个比较分发窗口；四个 LLNode 堆和第五个局部堆仍须按**同一实际 profile**满足各自可达状态／输入前提，尤其构造失败的展开。不得把最低 1.49.0、条件 1.85.0 与实际 1.74 任意互换。

四个 LLNode 谓词保持源原样，因此仍须证明具名 LACAM 生命周期内它们从未取得节点、未进入随机 Compare；若进入 A*／SIPP 搜索、LNS2 路径或不符合已证空状态，直接超出本 profile 资格，不能临时改词说“仍然纯 LaCAM”。进程退出省去适配 owner 的总对象析构，不省去构造失败展开和内部调用可能触及这些类型的证明。

## 8. 原固定 PIE-LACAM 核心路径的保真边界

E5 对固定 MAPFPlanner.cpp 与 LNS.cpp 的源码读取支持以下具名顺序：MAPFPlanner::initialize 的 initMap／computeAllPair／LNS 建立；实际 loadPaths 的 clearAll、vector<Path> 重载和 checkReplan；所选 LACAM 初始／重试 getInitialSolution、其 runLACAM2、LaCAM solve／Planner::solve，以及后继 fixInitialSolutionWithLaCAM。本方案保持这条路径，不调入 LNS2 修复、不去除 Agent/SIPP 对象来假装原算法更便宜。

source 的随机洗牌、预采样 tie、原 C 与 MT 状态使用和时钟读取保留 73 §9 的来源映射；不增加对成功随机序列的筛选，不把原内部时钟统一改成新的 CPU 截止。适配检查不窥视未交付真值；生成 MOVE 的资格仍只来自合格 R0 输出及中心既有协议的后继接纳。

输入拒绝只拒绝原调用会缺失定义域前提或版本不合法的情况，不按预计表现决定是否调用。core 返回后，planner_commit 的输出切分、未来段重合边界及原几何检查主体照常发生；外层完整验证是另外一项付费工作，不以自己生成的安全路线替换 source 输出。空或非法输出不从其他 solver 补齐；明确返回 NO_PROPOSAL／INVALID_OUTPUT 或 source failure。

保真主张因此严格限为“固定来源核心经列明修正与包装后的同一具名调用路径”。未改的 native R0 档案继续记录 init_time_limit、future／detach、第五堆比较关系和费用窗口问题；没有声称其已符合本适配轨，更没有执行它来制造不安全的对照结果。

## 9. 费用封闭：loadPaths／commit 不能继续免费

原 simulate 在 loadPaths 之后开始计时、在 planner_commit 之前结束 plan 的窗口，见 E5 §7.3。本方案将以下全部实际工作纳入既有 73 服务器分工，不因函数名为 preprocessing、copy、validation 或 cleanup 排除。

| 阶段 | 归属 | 计费内容与完成边界 |
|---|---|---|
| 初始资格、规划请求和冻结 SharedEnv | Srv_C | 解析／合法域核验、版本与任务投影、历史尾核验、所有复制／封装；完整冻结后才有后继 worker 请求 |
| worker 与输入安装 | Srv_P；跨域消息另经 Srv_N | 进程／执行域建立、地址空间／输入复制、所有权登记、来源配置、时钟／随机状态；未完成不运行 core |
| 原初始化 | Srv_P | initMap、computeAllPair 全部非障碍起点／堆操作、距离表分配和访问、LNS／Agent／求解器／PathTable 建立、异常展开；不得离线免费预热 |
| 事务准备与原 loadPaths | Srv_P | 检查点恢复、实际复制、clearAll、vector<Path> 加载／补长、checkReplan、路径表／统计维护；计入同一作业 |
| 原求解与原 commit | Srv_P | plan 全分支和失败工作，planner_commit 的清容器、commitPath 切分／填充、validateCommitSolution 及复制；原内部计时仍可作来源诊断但不代表总费用 |
| 输出和下一状态封存 | Srv_P，通道 Srv_N | 原输出到不可变消息、检查点存储和核验、编码／传送／接收字节；失败或迟到也收费 |
| 中心接纳或拒绝 | Srv_C | 完整路径／任务／版本检查和 CAS、空输出／去重／过期拒绝、状态引用提升；不借监管元层免费读 payload |
| 停止／回收／保留内存／日志 | 对应 owner 的原服务域 | 取消处理、终止状态核验、等待管理、引用／检查点清理、源与监管日志；无免费 detached 或 GC 后台线程 |

初始化、失败、取消、过期和重复工作都保留；没有成功结果时已经消耗的容量也不退费。只读检查点自身不推进算法，但占用内存与复制费用；写时复制不会让真实页物化成本从账中消失。中心取消先撤销接纳资格，后续 Srv_P 停止工作和中心收到回执各自收费，不通过跨 writer 同步锁隐藏等待。

NATURAL 仍记录同容量下的实际服务；STRICT 仍按 73 规定包括预付未用供给和实际用量向量。既有容量、共同物理时钟和真实任务服务定义不由本件赋值或改变。实际宿主耗时可另作工程诊断，但不替代付费虚拟服务账，也不在原算法内部悄悄混入宿主墙钟。

## 10. 成对公平与结果口径

共享 R0 的 D、E0 及其他已登记比较臂必须使用完全相同的修复版身份、INIT 后条件、截止起点、输入资格、事务回滚、第五堆关系和费用规则；不能仅为 D 修初始化、为对照保留损坏入口。原生 R0 保真档案可以并列说明来源差异，不能作为“D 战胜未修错误”的效果估计。

修复不是与查询策略随机绑定的处理变量。D 与对照在共同合法输入上出现不同调用次数、路径复用或取消量时，差异可以进入各臂真实账；同一源修复的收益本身不能命名为 D 创新。比较器修改、生命周期替换和全成本计费影响基线身份，必须在结果命名及方法说明中一并公开。

INIT_TIMEOUT／INIT_EXCEPTION 属于何种结果，需要保留两层：作业事件原由；以及 73 §12 的全臂资格／观察结果。合格后端上的合法失败可以保留 INIT_INCOMPLETE 与完整 roster／真实 Q；源定义域、计量或回收身份未闭则另记 PROTOCOL_OR_SOURCE_INVALID／UNVERIFIABLE 并使相关推断不可用。不能把所有源错误洗成正常搜索失败，不能删去失败臂、只保留成功配对，也不能把保留 HOLD 的实体误记为已消失或把真实任务完成数强制清零。

本件没有把 NET_DELAY、随机执行延迟或 CLOCK_LABEL_SKEW 改称实体误差；PIE-LACAM 来源修复也不能替代 73 对空间／运动误差和可信证据的独立资格。外部已发表基线继续按自己的原法身份及相同域适配审查，不以 R0 有缺口为理由降低比较强度。

## 11. 根可采用的规格闭合与未闭资格

| 义务 | 本件实际完成 | 仍不能宣称的内容 |
|---|---|---|
| 首次 init_time_limit 正常入口 | 选定直接核心入口、必填字段与首次显式传值；原未赋成员完全不在适配调用链 | 原 driver 已修复；将来实现已满足接线 |
| future 异常／超时传播 | 明确整段替换为同步 worker；成功／异常／截止／迟到的公共状态与禁止 plan 边已写清 | 已有代码处理了所有异常；未取得的运行时域已通过 |
| 活线程对象释放 | 所有权、取消、REAP_PENDING、终止确认、引用消退和不复用规则完整给出 | 发信号即回收；固定时长内一定退出；实际 OS／监管器实现已绑定 |
| 第五堆 | 唯一严格 value 修正与数学顺序性质、保留算法和费用范围明确 | all-pairs 完整正确性已证；已观测原程序 UB／错误距离；四堆义务消失 |
| Boost 实际绑定 | 已全文接收根 E7，参考合同选定所核 1.74 头文件及指定窗口；主机头身份已有证据 | CMake／产物已实际绑定 1.74；两个相同头 hash 已证明整个运行时 |
| core 状态事务 | 唯一完整执行域检查点／恢复合同明确；丢弃状态不继承、复制和存储收费 | 具体检查点／有限计量工具已存在、fork 或裸指针复制已验证等价 |
| loadPaths／commit／INIT 全成本 | 归属、失败费用、待回收占用与 Stop 后尾费闭合到规格 | 已有成本测量、容量配置或实验结果 |
| 原核心路径和原生身份 | 原文件保留，唯一内部修正、外部入口替换和效果归属列明 | 未改原生全程序资格；修复收益可归 D；候选已经唯一采用本路线 |

有界下一步是根决定是否把此单一方案写入尚未固定的 73，并将**E7 参考合同到后继实际 profile 的绑定、四堆空状态及异常展开的入口前提、完整执行域检查点与有限计量/回收后端身份、合法 all-pairs 证明**登记为明确的源资格义务。E7 已取得的本机堆身份／窗口不重复写成失落证据，也不需要另起全仓穷举；当前没有对应完整正文／证据的剩余项仍保留 UNKNOWN。

上述义务在不实现条件下可先完成接口一致性、数学证明和既存来源证据审查；本件不授权为了补证开始构建或运行。正式环节仍须依序科研导师 skill、Nature reviewer skill、明确不使用任何 skill 的独立逻辑审查及根验收，每次 skill 意见再由根无 skill 分析；本件不是其中任何一票。

## 12. 未执行合同与真实完成范围

后继获准阶段需要证明或验证的对象已具名：首次预算全调用链；初始化异常和迟到消息状态；取消与 READY 同行次序；回收未确认时 owner 不释放、容量不复用；地址空间检查点覆盖全部行为状态；第五堆在所选域的距离不变式；实际库四空堆的构造／异常展开；完整服务账与生命周期尾账；共享臂只差策略。这里只记录验收义务，没有编写测试、伪代码或运行模板。

本次未访问桌面论文包、旧桌面备份、35–38、Q-CAL／Q-CONFIRM、地图／scen／agent／task／delay／配置载荷或实验结果，没有给 H、T_delay、B_CAL、B_max、B*、P_active、density N 或其他保护参数填数值、范围、默认值或新含义。未读配置载荷来“确认”入口分支，未下载全仓、未修改任何旧报告、73、行政页、源码或 Git；没有 spawn，也没有调用任何 skill。

目标文件创建前精确检查不存在。新工件仅本研究目录的本文件，使用 apply_patch 创建；shell 每段均为 rtk 前缀，原文核验用 rtk proxy。提交本件完整文件及独立 hash／bytes／lines 回执后，本有界任务完成；研究未完成、候选未固定，HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT 保持。
