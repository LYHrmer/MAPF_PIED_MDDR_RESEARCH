# SCI MAPF 支线

工作树 `/home/lyh/MAPF_SCI_RESEARCH`，分支 `research/sci-mapf`。[main 总体决定](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/docs/RESEARCH_PLAN.md)是唯一当前总体计划；本树的总体文件是创建时快照。算法只在本线维护，大论文引用核定提交。

当前候选为标准离散 MAPF 局部路径修复中的无效计算。**2026-10-18 已实现固定顺序 PP 宿主、剩余成本预算、原版 ADDRESS SIPP 回调及完整共同校验器；原版 SIPP 适配程序已编译链接。** 尚未调用真实实例初始化或路径搜索，没有加速、路径质量或学习收益证据。经典下界先作为增强传统基线，不单独作为创新。

## 实现与证据

| 文件 | 实际作用 |
|---|---|
| [pp_repair.py](pp_repair.py) | 固定邻域及顺序的 PP 修复；给低层传成本上限，整组通过共同校验和截止/版本检查后才替换 incumbent。 |
| [address_backend.py](address_backend.py) | 作者持久子进程、固定输入转换、相同地图/路径/预算/缓存身份检查、完整离散冲突校验、RPC 截止、失败关闭及子进程 CPU/RSS 记录。 |
| [address_sipp_bridge.cpp](address_sipp_bridge.cpp) | 调用未修改的作者 `Instance`、`PathTable`、`ConstraintTable`、`SIPP::findPath`；复用每车静态目标距离表，无自写搜索替身。 |
| [build_address_backend.py](build_address_backend.py) / [编译收据](build_receipt.json) | 按固定 Git blob/SHA 核对 7 份源文件及作者头文件，编译并只调用 `--describe`；记录编译器、头文件包版本、二进制 SHA。输出目录必须为新目录，保留失败与超时记录。 |
| [test_pp_repair.py](test_pp_repair.py) | 23 项软件契约：脚本回调、明确给定的离散路径、假原生响应；没有初始化原生求解器或解科学实例。 |
| [address_remaining_budget.patch](address_remaining_budget.patch) / [原源码清单](address_source_manifest.json) | 先前对完整 `runPP` 的可审阅修改草案；`git apply --check` 通过，但未应用。实际新后端直接复用原版 SIPP，不依赖此补丁。 |
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

作者空路径目前保留为 `EMPTY_CAPPED/EMPTY_BASE_LIMIT` 原生诊断，并在修复层记为 `FAILED`（未知、删失），不自动当作已核穷尽搜索或无限制不可行。仅 Python 下界直接排除、完整无改善等已核条件形成当前尝试的负标签。空返回语义的原生资格仍待闭合。

RPC 使用非阻塞管道和同一单调时钟截止，原生子进程有 CPU/地址空间限制，异常时终止且无重启；请求/响应摘要、失败原因、RPC wall 及被回收子进程的 CPU/RSS 保留。**这些尚不代替完整案例的进程监督器。** 完整费用仍须包含 Python 导入、初解校验、原生初始化/距离表、序列化、搜索、恢复、完整校验、退出与写盘；Python `process_time` 不包含原生 CPU，不能只报它。共同验证器可能消耗预算，接纳前检查防止迟到采用，整体硬停仍由外层监督器承担。

旧原生 `runPP` 补丁禁用尚未闭合的 bandit 奖励更新，只适合固定请求回放草案；它保留原 `random_shuffle`，不得用于宣称跨臂相同顺序。新的 Python 固定顺序宿主没有这个随机换序入口，也不实现作者邻域选择与 bandit 循环。

## 已完成的检查

- `python3 -B -m unittest discover -s tracks/sci -p test_pp_repair.py -v`：23 项软件契约通过，未调用真实搜索。
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

**下一交付：完整案例宿主与固定配对输入。** 先接进程级硬预算、统一产物写盘、空返回语义；再固定少量完整初解、邻域/顺序、输入 SHA、命令、总预算与零重试/失败保留清单。只有取得新科学运行的真实授权才调用后端。强基线和候选共同计入初始化/缓存/搜索/验证/写盘，不将预处理移出计时。

获授权后，先检查“已经不可能改善时仍继续搜索”是否占实际完整费用、增强规则能消除多少。若完整成本无净收益或低成本规则已解决主要浪费，记录停止/收缩，不为保留学习而扩大任务；若仍有可重复的预算错配，再选择一个学习任务。不能把编译、接口检查或经典下界升级为 SCI 创新证据。
