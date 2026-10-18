# SCI MAPF 支线

工作树 `/home/lyh/MAPF_SCI_RESEARCH`，分支 `research/sci-mapf`。[main 总体决定](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/docs/RESEARCH_PLAN.md)是唯一当前总体计划；本树的总体文件是创建时快照。算法只在本线维护，大论文引用核定提交。

当前候选为标准离散 MAPF 局部路径修复中的无效计算。**2026-10-18 已实现固定顺序 PP 宿主、剩余成本预算、原版 ADDRESS SIPP 回调及完整共同校验器；原版 SIPP 适配程序已编译链接。** 经用户明确授权的六臂DEV现已完成：原控制共48次搜索，增强臂根节点检查全部结束，最终SOC与路径SHA相同。三个初解都达到静态最短路和；保留经典界为强基线，停止这批任务上的学习候选。独立加速或创新尚未成立。见[完整结果](DEV_RESULT.md)。

## 实现与证据

| 文件 | 实际作用 |
|---|---|
| [pp_repair.py](pp_repair.py) | 固定邻域及顺序的 PP 修复；给低层传成本上限，整组通过共同校验和截止/版本检查后才替换 incumbent。 |
| [address_backend.py](address_backend.py) | 作者持久子进程、固定输入转换、相同地图/路径/预算/缓存身份检查、完整离散冲突校验、RPC 截止、失败关闭及子进程 CPU/RSS 记录。 |
| [address_sipp_bridge.cpp](address_sipp_bridge.cpp) | 调用未修改的作者 `Instance`、`PathTable`、`ConstraintTable`、`SIPP::findPath`；复用每车静态目标距离表，无自写搜索替身。 |
| [build_address_backend.py](build_address_backend.py) / [编译收据](build_receipt.json) | 按固定 Git blob/SHA 核对 7 份源文件及作者头文件，编译并只调用 `--describe`；记录编译器、头文件包版本、二进制 SHA。输出目录必须为新目录，保留失败与超时记录。 |
| [build_address_full.py](build_address_full.py) / [完整原版编译收据](full_address_build_receipt.json) | 固定作者86份文件、树外编译完整ADDRESS并只执行`--help`；已成功，未构造实例或搜索。完整系统的公平比较仍需初解与随机性适配。 |
| [test_pp_repair.py](test_pp_repair.py) | 28 项软件契约：脚本回调、明确给定的离散路径、假原生响应；没有初始化原生求解器或解科学实例。 |
| [address_remaining_budget.patch](address_remaining_budget.patch) / [原源码清单](address_source_manifest.json) | 先前对完整 `runPP` 的可审阅修改草案；`git apply --check` 通过，但未应用。实际新后端直接复用原版 SIPP，不依赖此补丁。 |
| [run_repair_dev.py](run_repair_dev.py) / [运行清单](RUN_CHECKLIST.md) | 完整案例监督器、单次消费和失败总账；固定六臂已按新授权运行并保留全部产物；许可已消费，不能再次执行。 |
| [repair_profile.py](repair_profile.py) / [后继诊断清单](PROFILE_CHECKLIST.md) | 已准备三类地图s01各16/32车的六份完整任务，复用不变运行器；只用经典强策略定位剩余瓶颈。输入重验和离线解析软件检查完成，科学运行待新授权。 |
| [ADDRESS_LICENSE.txt](ADDRESS_LICENSE.txt) | 作者原许可字节，限教育、研究、非营利；不能称 MIT。 |

作者固定提交 `b3d35c431ce03834f95e834d87986f2f341394a1`；原树在 `/home/lyh/.cache/mapf_research/address-b3d35c4`，保持原样。编译产物在本机 `.native_build_checked/`，不入库；前一次编译记录在 `.native_build/` 原样保留。当前二进制 SHA 为 `2f1f2ddc394961e055ad737debd700c7fc6b2b1c5c939767b8cd07ffb282f347`。收据是当前主机的构建证据，不是跨平台环境锁，也不代表完整 ADDRESS 系统或论文实验复现。

本线不消费原 v2 误差模块或 shared reader，不为未使用的接口增加 loader。冻结证据、作者代码和主稿未修改；L20/L21 和旧单组 DEV 不产生新学习标签。

## 具体规则与保证范围

固定邻域及 PP 顺序。设旧邻域整数路径成本为 `C_old`，严格改善目标为 `U=C_old−1`；已规划前缀成本为 `g`，剩余车辆同模型的可采纳下界为 `h_i`。

1. 若 `g+sum_remaining(h_i)>U`，结束当前尝试。
2. 下一车 `j` 的成本上限为 `U−g−sum_other_remaining(h_i)`。
3. 整组成本严格改善，外部路径不变，完整共同校验通过，且锁内总截止与版本检查通过，才接纳。

任何可能改善的当前前缀延续必须满足该上限。这是经典可采纳下界推理，只排除当前顺序及已固定前缀；不排除换顺序/前缀/邻域，也不证明 MAPF 整体无解。`h_i≤旧成本`仅为必要一致性检查；实际后端使用作者在同地图、同目标上构造的静态最短路表。

`ORIGINAL_PREFIX` 不传新增单车 cap，按已发生的前缀成本停止；`REMAINING_BOUND` 使用剩余下界和 cap。共同校验/终态处理/静态距离缓存/预算相同。作者原 `ConstraintTable.length_max` 和 SIPP 已支持有界搜索，本工作只提供更强的调用上限，不能称首次有界搜索或首次下界剪枝。

## 接口、费用与失败语义

模型明确为四邻域、单位步时与成本、允许等待、顶点/对向边冲突、终点永久驻留。整数顶点按行编码，不是米或秒。`GridProblem` 生成作者原格式，稀疏外部车号映射为稳定原生编号；不调用缺文件时的作者随机地图生成。完整校验展开到所有给定路径的最长长度，再利用各不重复终点恒定驻留的条件覆盖之后的离散时刻。它不证明连续车身安全。

`NativeBackend` 构造会初始化真实作者求解器，因此属于科学运行授权范围。导入模块、编译、`--describe` 不调用该构造。每臂一个持久作者子进程，距离表复用；无路径结果缓存。每次原生搜索的随机种子由相同车辆、固定 order 和前缀派生，不包含 cap；相同请求的两臂有相同随机起点，不保证剪枝改变后消耗同一 RNG 序列。不能把这一固定请求宿主称为完整 ADDRESS 自适应 LNS。

`search(SearchRequest)` 检查外部车辆集合和已规划前缀完整覆盖；传同一个绝对预算与缓存身份。返回的 `FOUND` 仍检查几何、cap、碰撞字段，完整修复后再共同校验。最终 `True` 标签仅由整组接纳事务产生；超时、异常、未知与版本失配标签为 `None`。

固定原版 `findPath` 的正常空返回只有起点不可用或搜索集合耗尽，内部没有超时返回。匹配cap且收到完整正常空回应时，采用作者离散SIPP的有限搜索语义，记为当前cap内穷尽；超时、缺字段或异常仍删失。默认 `MAX_TIMESTEP` 的空返回不作无限制不可行。此接口依赖作者算法，不是本项目独立完备性证明；详见运行清单。

RPC 使用非阻塞管道和同一单调时钟截止，原生子进程有 CPU/地址空间限制，异常时终止且无重启；请求/响应摘要、失败原因、RPC wall 及被回收子进程的 CPU/RSS 保留。已接通案例进程组监督器，超时/中断回收后代、保留退出费用，脚本子进程检查通过；六臂真实作者初始化及控制臂48次搜索已完成。完整费用包含 Python 导入、初解校验、原生初始化/距离表、序列化、搜索、恢复、完整校验、退出与写盘；Python `process_time` 不包含原生 CPU，不能只报它。共同验证器可能消耗预算，接纳前检查防止迟到采用，整体硬停由外层监督器承担。完整工作进程wall含最终结果写盘；父审计开销另列，末份审计收据自身写盘不在自身计时内，不以局部耗时宣称完整加速。

旧原生 `runPP` 补丁禁用尚未闭合的 bandit 奖励更新，只适合固定请求回放草案；它保留原 `random_shuffle`，不得用于宣称跨臂相同顺序。新的 Python 固定顺序宿主没有这个随机换序入口，也不实现作者邻域选择与 bandit 循环。

## 已完成的检查

- `python3 -B -m unittest discover -s tracks/sci -p test_pp_repair.py -v`：28 项软件契约通过，未调用真实搜索。
- 固定作者文件按 blob/SHA 核验；C++17 编译链接成功；只执行 `--describe`，明确 `solver_called=false`。原作者树前后保持干净。
- 旧补丁的 `git apply --check` 证据保留，未重写成完整系统复现。

若需重新编译，给出不存在的输出目录，例如：

```bash
rtk proxy python3 -I -B tracks/sci/build_address_backend.py \
  --author-root /home/lyh/.cache/mapf_research/address-b3d35c4 \
  --output /tmp/address-build-review
```

这条命令仅编译及查询描述。没有附带实例求解或训练命令。

## 近邻与下一项实质交付

同问题参照为 [NNS，ICLR2024](https://proceedings.iclr.cc/paper_files/paper/2024/file/d41f8403e9bb5141bc2c81fad7658185-Paper-Conference.pdf)、[ADDRESS，AAAI2025](https://ojs.aaai.org/index.php/AAAI/article/view/34495)、[TACKLE，AAAI2026正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/40207)。NNS/TACKLE 新增作者代码许可未核，不直接修改再分发；既有学习选邻域/共享计算/反事实组合不能当作本项目原创。固定路径的 Improved GSES、ESADG 不直接作为路径修复的公平性能对照，后者仍按已核来源标作预印本。

**六臂DEV已完成，授权已消费。** [结果](DEV_RESULT.md)表明三个初解均已达到同模型下界，廉价根节点检查解释了全部搜索减少；增强臂未实跑逐车cap分支。下一项先核定具有同模型非零余量的既有完整任务，再研究共享根节点检查之外的具体求解差异。scenario末列与四邻域h不一致，不能用其差额制造“协调余量”。旧输入只是DEV，不是独立测试；没有world或训练。

本轮决定是保留强基线并停止零余量任务上的学习投入。单次完整wall的差异不足以证明稳定加速；所有后继方法必须共用这一廉价检查。新运行须另给清单与真实授权，不能复用本批许可。

后继的[具体诊断](PROFILE_CHECKLIST.md)已准备：六份已有完整16/32车初解；按固定8车组及两项整任务顺序诊断根拒绝、前缀拒绝、有限cap穷尽、接受和总费用，输入SHA `be1e912e…1c0e5b`、清单SHA `cff28cdb…987039`。没有初始化新的作者实例，没有计算其同模型h。新增5项离线解析/固定范围软件检查通过；正差额、真实接受、超时/未知严格分开。

作者原版driver未提供加载现有完整初解的选项，完整ADDRESS公平对照仍需初解适配。上述ID分组固定探针也不是其自适应选组策略；后继六项只作一次瓶颈筛选，不是独立性能实验、加速对比或学习标签集。

## 完整原版ADDRESS工件及适配缺口

已按作者原CMake树外编译完整可执行程序，保留作者所有源码字节。86份源/头文件、CMake与许可等逐项固定blob/SHA；配置、编译均退出0，原版`--help`按其入口约定退出1，在`Instance`与`LNS`构造之前返回。完整二进制位于`.full_address_build/build/address`，SHA256 `837a15e82251a92cf025bdf067811dae02e82a792dfb7b17238c45019d51268b`。这是编译与入口证据，没有执行完整ADDRESS科学任务。

配置/编译/help原始日志在`.full_address_build/`，其SHA与命令在[固定收据](full_address_build_receipt.json)，收据SHA `c2d22fececdfc4288d438d6d7004aa52a6fa33c079ea620f2f113e7ff2dbfb62`。本机GCC11、Boost1.74、Eigen3.4编译成功；作者README要求Boost1.81，不宣称环境完全匹配。编译保留`LNS::wrapper`的非void函数末端返回告警，未静默修改作者代码。

以下均为固定源码的定点结论，不是新实验结果：

- [driver.cpp](https://github.com/JimyZ13/ADDRESS/blob/b3d35c431ce03834f95e834d87986f2f341394a1/src/driver.cpp#L49)默认`maxIterations=0`；`run()`先记录一次初解，再检查`iteration_stats.size() <= num_of_iterations`，因此默认不做修复迭代。原README运行示例显式给了非零上限，后续必须固定完整方法配置，不能把默认调用当完整ADDRESS性能。
- [LNS.cpp](https://github.com/JimyZ13/ADDRESS/blob/b3d35c431ce03834f95e834d87986f2f341394a1/src/LNS.cpp#L1188)的`bernoulie()`每次从`random_device`构造独立mt19937；命令行`seed`控制的`rand`不覆盖这部分。共同种子声明需明确适配，不能只传`--seed`就写成可重复配对。
- 同文件构造器会把`neighbor_size`赋为8；需要核对实际行为，不能仅依据`--neighborSize`宣称改变了邻域规模。本批已准备的固定宿主也不替代作者自适应选组。
- `getInitialSolution()`仍调用规划器，没有外部完整初解入口。公平比较可选择显式适配初解导入，或为双方采用相同端到端初解策略；在诊断结果明确前不自行切换问题或运行原版生成新初解。
- 原版`runPP`在完整接纳/回滚前更新部分bandit字段；此前剩余下界补丁未闭合这部分反馈语义。后续共同强基线必须处理完整接纳奖励和失败删失，不能把旧禁用学习更新的补丁直接叫完整ADDRESS。

该完整二进制不是当前待授权六任务清单锁定的SIPP桥接二进制，不得替换运行器或扩大授权。只有共同初解、原版随机性、完整费用与奖励适配闭合后，才准备完整系统比较。此工件不是新的算法贡献，也不改变“先看强传统方法之后的真实剩余瓶颈，再决定学习”的研究顺序。
