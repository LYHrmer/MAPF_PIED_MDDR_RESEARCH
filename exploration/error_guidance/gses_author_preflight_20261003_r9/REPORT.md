# R9：作者 GSES / Improved GSES 可执行预检

本轮已从作者仓库编译并运行 GSES 与 Improved GSES。这里完成的是外部基线 R0：固定来源、保留作者实现和运行语义、跑通作者输入；尚未完成与我们的连续执行 / FIFO 任务环境的公平对照。

来源：[作者 STPG 仓库](https://github.com/DiligentPanda/STPG)，[AAAI 2025 原文页面](https://ojs.aaai.org/index.php/AAAI/article/view/34487)，*Speedup Techniques for Switchable Temporal Plan Graph Optimization*，He Jiang、Muhan Lin、Jiaoyang Li，DOI 10.1609/aaai.v39i22.34487。

## 固定实现与实验

- 作者提交 `25fb931eff03f1cce23a22a68ab42b7533f85ab3`，PBS 子模块 `f1e08e104c0cb575d6f9ed8b26344c0b982f422d`，pybind11 子模块 `19a6b9f4efb569129c878b7f8db09132248fbaa1`。
- 作者源码零修改；MIT 许可和选取的核心源码随本目录归档，完整文件 SHA 在 `PROVENANCE.json`。
- C++17 Release，原 CMake，系统 Boost 1.74；原 CMake 还要求 SFML。缺少 SFML 的初次失败保留，六个 Ubuntu 2.5.1 包只解包到私有 sysroot，未安装或修改系统库。包 SHA 在 `DEPENDENCY_PACKAGES.json`。
- 先跑作者 `simulate.sh` 的 lak303d 示例：`simple` 分组、非增量，90 秒上限，成功，10496 → 10229。它不是下面 Improved GSES 完整配置的替代。
- 正式预检在看结果前选定作者四图最低代理数、instance 1、situation 0、`p01` 输入；每个输入跑作者 `run_exps.py` 中的基础与完整配置。查询随机种子 10，启发式/焦点权重均 1，作者搜索限时 16 秒。
- 同机顺序执行，外层超时 120 秒，CPU 限额 90 秒；两种方法均限 4 GiB 地址空间（作者批处理为 16 GiB）。本轮未出现内存限制错误。这是预检资源口径差异，不能据此声称复现论文性能。

## 实测

| 作者地图 / agents | 原成本 | GSES 状态 / 成本 | Improved GSES 状态 / 成本 | GSES 搜索秒 | Improved 搜索秒 |
|---|---:|---:|---:|---:|---:|
| random-32-32-10 / 60 | 1375 | Succ / 1292 | Succ / 1292 | 0.0531 | 0.0061 |
| warehouse-10-20-10-2-1 / 110 | 10816 | Succ / 10804 | Succ / 10804 | 1.3161 | 0.0601 |
| Paris_1_256 / 120 | 29860 | Timeout / 29860 | Succ / 29786 | 16.2403 | 0.3677 |
| lak303d / 41 | 10496 | Timeout / 10496 | Succ / 10229 | 16.8485 | 0.4162 |

以上是四组预先选择的确定性实例，无重复统计。作者超时判断和费用回退保持原样；`Timeout` 臂回报原成本，不是成功优化。作者 `total_time` 不含所有构图、分组和进程开销，且超时臂将其截为 16 秒，因此 `summary.csv` 同时列出 grouping、search、reported total 和实测进程 wall 时间。不要把这些时间混用。

8 臂进程均正常退出，作者模拟器的顶点 / 跟随冲突检查均未报错，日志无 `all stucked`。但单 situation CLI 接收 `new_path_ofp` 后没有真正写出路径；本轮没有独立完整轨迹重放，不能将作者内部检查写成我们的连续物理验证。可用性结论是 Improved GSES 4/4 成功，基础 GSES 2/4 成功、2/4 超时。

## 与第三线如何衔接

| 项目 | 作者 STPG | 当前第三线 | 公平对照需要做的工作 |
|---|---|---|---|
| 核心决策 | 固定路径上的执行依赖切换 / 优先次序优化 | OnlineGGO 路径导引 + 原局部 ADG 执行 | 先选共同的调度决策问题；不要把重路由收益算成学习调度收益 |
| 执行 | 离散路径状态、给定 `delay_steps` | 半 MOVE / TURN / 20 tick STATION，连续机器人仿真 | 用共同外生扰动生成器，逐物理 primitive 映射依赖；不能把既有结果轨迹当成其他策略必然遇到的误差 |
| 目标 | 剩余路径离散累计完成成本 | H 内 FIFO 任务数 + 固定任务前缀截断完成时间 | 分开报告原问题结果；适配比较统一任务、时限和完成定义 |
| 可观测信息 | 原路径、当前位置、delay situation | 当前任务头、公开 proposal / admit / END | 禁止把未来真实误差给待比较的在线方法；已知当前延误与预测未来延误分别注册 |
| 安全检查 | 离散顶点及跟随冲突 | 原 ADG + 连续执行采样 | 单元边占用和机器人闭 footprint 的映射要校验，保留共同底层安全控制 |

建议保留目前“误差感知局部执行”的分支，同时把 Improved GSES 纳入真正可执行的外部调度比较候选。若文章改为“预测 primitive 完成时间 → 优化关键依赖 / 切换次序”，STPG 比 PIE-D 的付费位置查询接口更直接；若仍主张 LMAPF 重路由吞吐提升，STPG 只能作为调度比较或相邻工作，不能替换同任务的 LMAPF 作者基线。

下一步具体实现：先做小规模固定路径的 TURN / 半 MOVE 依赖映射，验证无学习原版适配的结果及安全性；再在同一个求解器里比较无预测、历史统计、学习预测，独立报告预测误差和决策收益。适配代码明确标记为作者算法的接口移植，作者原版预检继续保留。不要因本轮学习臂 188 对 186 的单条件增益就更换整篇论文叙事。

## 复现与保留材料

`REGISTERED_CASES.json` 包含四组输入的原路径与 SHA；`inputs/` 仅带这八个实际用到的作者文件。`commands/` 保留初次缺依赖失败、成功配置 / 编译、原始示例与八臂的 stdout、stderr、stats、完整命令、退出码及耗时。`ROOT_AUTHOR_AUDIT.json` 验证输入配对、源码零修改和结果口径。

完整作者仓库与子模块可用固定提交从上述仓库恢复；本目录 `author_core_source.tar.gz` 只保存作者 src/inc、CMake、运行脚本与许可，不冒充完整子模块快照。`reproduce.py` 对现成的相同作者二进制和本目录输入重跑八臂，拒绝覆盖旧运行结果；本机绝对路径见原始 receipt，仅用于溯源。
