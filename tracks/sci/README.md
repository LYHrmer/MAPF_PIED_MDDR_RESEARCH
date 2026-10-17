# SCI MAPF 支线

工作树 `/home/lyh/MAPF_SCI_RESEARCH`，分支 `research/sci-mapf`。[main 总体决定](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/docs/RESEARCH_PLAN.md)是唯一总体计划；[本线最新实现](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/research/sci-mapf/tracks/sci)。本树的总体文件是创建时快照，本页只维护本线具体实现与证据边界。

当前候选为标准离散 MAPF 局部路径修复中的无效计算。**2026-10-18 已实现 PP 剩余成本策略、完整修复终态与 incumbent 事务，并提供固定 ADDRESS 的实际源码补丁；只完成软件契约与静态核验。** 尚未构建或运行作者修复器，没有加速、路径质量或学习收益证据。经典下界先作为增强传统基线，不单独作为创新。

外部比较以NNS/ADDRESS/TACKLE同问题方法为主；固定路径的Improved GSES/ESADG只作问题边界参照。原v2误差底座不强制接入SCI，L20/L21与单组DEV不作新标签。新运行仍待具体授权。

## 当前可审阅产物

| 文件 | 实际作用 |
|---|---|
| [pp_repair.py](pp_repair.py) | 给现有低层搜索器编译每车成本上限、固定外部路径和当前已规划前缀；通过完整共同核验后原子接纳整组结果。没有内置搜索器。 |
| [test_pp_repair.py](test_pp_repair.py) | 13 个脚本 callback 契约检查，覆盖上限、残余下界、超时、异常、完整核验、缓存传递与并发版本失配；没有地图或科学实例。 |
| [address_remaining_budget.patch](address_remaining_budget.patch) | 针对作者固定版本的 `inc/LNS.h` 和 `src/LNS.cpp` 修改：开关、原生诊断终态、下界、`length_max`、返回后时限检查；禁用此入口的 bandit 奖励更新，仅供固定请求回放接入。未应用到作者缓存。 |
| [address_source_manifest.json](address_source_manifest.json) | 固定作者 commit、所读 6 个文件的 Git blob/SHA256、补丁 SHA；原文件逐项通过 Git blob 核对。 |
| [ADDRESS_LICENSE.txt](ADDRESS_LICENSE.txt) | 作者原许可原字节副本；允许教育、研究、非营利用途，整个作者项目不能标成 MIT。 |

本线此次不消费旧连续误差模块或 shared reader，因此没有为未使用的公共接口新增 loader；未来实际消费时再固定其 commit/blob/SHA。旧作者树、冻结证据和主稿均未修改。

## 具体规则及保证范围

固定本次邻域及 PP 优先顺序。设旧邻域整数路径成本为 `C_old`，严格改善目标为 `U=C_old-1`；已承诺前缀成本为 `C_prefix`，未规划车辆的同模型可采纳下界为 `h_i`。

1. 若 `C_prefix + sum_remaining(h_i) > U`，结束当前尝试。
2. 下一车辆 `j` 的成本上限为 `U-C_prefix-sum_other_remaining(h_i)`。
3. 完整修复的成本须严格小于 `C_old`，所有未选车辆路径不变，并由同一完整 MAPF 核验器检查地图、动作、顶点冲突、对向边冲突及终点驻留，才接纳新 incumbent。

任何可能严格改善的当前前缀延续都必须满足上述上限，因为其他剩余路径的成本不能低于其 `h_i`。这只是经典可采纳下界推理。它不排除改变当前 PP 顺序、已选前缀或邻域后得到改善，也不证明 MAPF 整体无解。`h_i <= 旧路径成本`只是必要一致性检查，不是下界可采纳性的证明；实际后端必须复用同一地图与目标的已核静态最短路下界。

Python 的 `Policy.ORIGINAL_PREFIX` 不向单车搜索传递新上限，仅按已发生的前缀成本停止；`REMAINING_BOUND` 使用剩余下界和每车 cap。双方共享完整终态处理、验证器、缓存对象及一个跨尝试的绝对预算。固定本次 order，模块不采样新邻域或优先级，不重开 L20/L21 组选取。

## Callback 与终态

`search(SearchRequest)` 收到 agent/start/goal、`max_cost`、不可变 `fixed_paths`/`prefix_paths`、model/constraint key、共同预算与缓存；返回 `SearchReply`。模型 key 必须标识同一地图和冲突语义。constraint key 绑定保留路径、前缀、车辆和 cap；实际后端缓存还需区分自身算法配置。费用包含 callback 内的缓存访问，不把特征或缓存构造免费移出总成本。

| 后端结果 | 解释与接纳 |
|---|---|
| `FOUND` | 仅为单车候选；仍检查端点、整数路径成本、cap，整组完成后共同核验。 |
| `EXHAUSTED_WITHIN_CAP` | 后端已穷尽当前改善上限内的搜索；记录 `NO_IMPROVEMENT`，不能称无限制无路。 |
| `INFEASIBLE` | 仅在没有改善 cap 且后端完成无限制问题搜索时允许；范围仍是当前固定前缀。 |
| `TIMEOUT` / `FAILED` | 部分搜索、后端异常、未知结果；保留 incumbent，学习标签为 `None`。 |

最终正标签只在整组严格改善、完整核验返回真正的 `True`、且锁内 deadline 与版本检查通过后产生。`NO_IMPROVEMENT`/已证明的前缀 `INFEASIBLE` 可作本次固定尝试的负标签，不是任意邻域修复能力的负标签。迟到 callback 即便返回完整路径也不接纳；最终校验迟到也不接纳。并发 incumbent 已变化时返回 `STALE_INCUMBENT`。

`SharedBudget` 不会因失败重置；search-call 配额计已保留的调用尝试。wall/CPU 记录失败和异常阶段，`RepairResult` 记录整个 repair 调用耗时。它是合作式预算，不能抢占一个阻塞 callback；下一项科学运行必须使用进程级硬预算，并计入导入、外部预处理、序列化与日志成本。incumbent 是可信单进程宿主内的事务，不是恶意代码隔离或分布式机器人原子启动。

## ADDRESS 接入范围

固定作者版本 `b3d35c431ce03834f95e834d87986f2f341394a1`，可审阅原入口：[runPP](https://github.com/JimyZ13/ADDRESS/blob/b3d35c431ce03834f95e834d87986f2f341394a1/src/LNS.cpp#L462)、[ConstraintTable](https://github.com/JimyZ13/ADDRESS/blob/b3d35c431ce03834f95e834d87986f2f341394a1/inc/ConstraintTable.h)、[SIPP](https://github.com/JimyZ13/ADDRESS/blob/b3d35c431ce03834f95e834d87986f2f341394a1/src/SIPP.cpp#L25)。

原版已经在低层使用 `length_max`，SIPP 的 82/101 行及 SpaceTimeAStar 的后继检查可裁剪超长候选。本补丁只给已有算子提供来自 incumbent 与剩余 `h` 的上限，**不是新增有界搜索或首次下界剪枝**。公开开关 `pp_remaining_cost_bound=false` 为关闭新增界的共同控制臂，`true` 才开启。

本次原调用的 `ConstraintTable(...,&path_table)` 将已有路径传给 `path_table_for_CT`，软冲突表参数使用默认空值；不能将 SIPP 通用函数的“优先少碰撞”注释当作此处已完成的整任务安全证书。真实后端接入 Python 接纳层时仍须提供完整共同 validator；该 validator 本轮未连接作者系统。

原 `runPP` 在完整接纳检查前更新成功计数，且选择器在进入修复前已增加 `frequency`。只忽略 timeout 的奖励更新仍会把该次尝试带入后续均值分母，并不构成正确 censor。**本补丁直接禁用 runPP 的 bandit 奖励更新，仅允许准备固定邻域/顺序回放；不用于原版自适应 LNS 循环。** 原生 `complete && within_time && strict_improvement` 只是诊断终态，不是经过完整共同 validator 和宿主总截止检查的学习标签；只有 Python 接纳事务产生该标签。源码风险尚未测得实际发生频率，不扩展为对原论文结果的否定。

补丁是可应用的原生接入草案，沿用作者函数的单线程可变 path-table 与普通返回路径回滚，不把它声称为 Python 事务的异常隔离替代。低层 `findPath` 没有新增硬抢占；原生 `within_time` 取值不覆盖后续函数返回开销，因此 `IMPROVED` 不保证整函数及时完成。原生结果在后端返回后仍须经过共同总 deadline 和完整 validator 才能作为被接纳的任务结果。原作者 `random_shuffle` 入口仍保留；首次固定顺序回放须由实际后端明确绑定，不把设随机种子等同于跨臂固定 order。C++ 整库构建、固定 request/order 宿主、内存异常下的原生回滚、完整 validator 和进程预算接线均尚待完成；不得仅凭本补丁调用科学实例。

## 已完成的非科学检查

- `python3 -B -m unittest discover -s tracks/sci -p test_pp_repair.py -v`：13 项纯软件契约通过。
- 固定作者 6 个文件与 Git blob OID 一致；补丁对其精确字节运行 `git apply --check` 通过，未应用到作者缓存。
- Python 文件语法核验；补丁仅触及声明的 2 个作者文件。

脚本回调中的顶点整数只是软件值，验证回调是桩函数；这些检查不构成地图可行性、碰撞安全、科学运行、加速或训练结果。原始作者、共同终态修正版、修正版加剩余界须分别命名；不能把修复终态错误的收益算成下界算法优势。

## 直接近邻与下一交付边界

[NNS，ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/file/d41f8403e9bb5141bc2c81fad7658185-Paper-Conference.pdf)已学习选择需重规划的子集并共享表示计算；[ADDRESS，AAAI 2025](https://ojs.aaai.org/index.php/AAAI/article/view/34495)已有 top-K 种子与在线成功学习；[TACKLE，AAAI 2026 正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/40207)已有规则意图与反事实学习组合。TACKLE §5.4 的低覆盖/排序开销负例是待检查的预算现象，不是本项目已解决的缺口。NNS/TACKLE 作者仓库的许可本次未核定，不将“公开可读”写成可直接修改再分发。

[Improved GSES](https://ojs.aaai.org/index.php/AAAI/article/view/34487)是固定路径执行图优化，本地 MIT 作者版与预检保留；[ESADG v2](https://arxiv.org/html/2511.21886v2)仍按作者页核为预印本，已有组选取、收益估计与环修复，固定作者工件/许可未取得。两者不作为本次局部路径修复的同问题性能对照。

下一项仅接通一个固定作者修复后端、完整共同 validator 与原子宿主，再准备独立输入和一次有限预算清单。瓶颈假设是“当前改善已不可能时，仍支付后续修复搜索费用”；源码存在条件差别，实际占比尚未知。若增强廉价规则没有减少完整成本，或构造/核验费用抵消收益，记录停止或收缩；即便获得收益，也须进一步核对算法近邻，不能直接据此宣布 SCI 创新或开始网络训练。
