# R18：标准地图上的 SADG 误差与查询比较

标准地图、多智能体规模和执行扰动的完整对照已经完成：45/45 作者 ECBS 初始路径有效，236 条 TRAIN、135 条 CAL、270 条 TEST 执行均收齐。[完整结果](REPORT.md) · [科研导师后续设计](NEXT_METHOD_DESIGN.md) · [机制诊断](MECHANISM_REVIEW.md) · [交付核对](COMPLETION_CHECKLIST.md)。模型相对无查询的测试时间和少 9（0.0133%）、花费 1000 次查询；相对强历史规则为 1 优、1 劣、52 平，不宣称稳定学习优势。冻结研究定义保留在 [PROTOCOL.md](PROTOCOL.md)。

## 固定对象

- MovingAI `random-32-32-10`、`maze-32-32-2`、`warehouse-10-20-10-2-1`。
- 8、16、32 个机器人；官方 random 场景 1/2 训练、3 校准、4/5 测试，全部尺度和扰动按地图/场景族隔离。
- 原作者 ECBS 统一 `w=1.5` 生成45组共用初始路径；45/45有效，详细来源、许可证说明、离散审核及压缩数据在 [data/README.md](data/README.md)。
- 固定路径 SADG 作者优化器 `c2626d996121a9d6c128844a167b917db24418ac`，原算法不改；全部方法共同使用已登记的 R16 k0/all-heads 适配及本轮连续执行器。
- 稳定、动作中短暂停滞、动作序号触发的持续速度变化；真实扰动只供执行器和审计器。

## 实验臂

`history_only`、`fixed_update`、`history_rule`、`learned_query` 使用同一 SADG 核心和相同信息可见性，查询臂共享总预算 N 与每 gate ceil(N/8) 上限。`dense_position` 查询所有当前 active 机器人，明确不受同预算约束，作为额外信息充分时的参考。

模型以训练族实际执行的“查询一个目标／不查询”完整后果差作为标签，之后进行新的完整学习策略执行。22个特征全部来自公共快照；按独立族选择正则和标准化。单目标训练值不能直接证明多目标/多gate部署收益，最终结论以独立 TEST 结果为准。

## 运行和恢复

已有工件首先按hash复用，不再执行相同初始路径、完整episode或作者输入。下面命令使用本项目已固定的作者虚拟环境：

```bash
rtk proxy /home/lyh/.cache/mapf_research/sadg-r16-venv/bin/python exploration/error_guidance/sadg_benchmark_20261005_r18/run_benchmark.py register
rtk proxy /home/lyh/.cache/mapf_research/sadg-r16-venv/bin/python exploration/error_guidance/sadg_benchmark_20261005_r18/run_benchmark.py all
rtk proxy /home/lyh/.cache/mapf_research/sadg-r16-venv/bin/python exploration/error_guidance/sadg_benchmark_20261005_r18/analyze_results.py
```

工作目录为本分支仓库根。`all` 的执行顺序是收集TRAIN配对→冻结模型→CAL/TEST全部对照→原始汇总。也可分别调用 `collect`、`fit`、`evaluate`、`summarize`，但模型冻结是新评价的硬前置条件。脚本要求当前源码与登记hash相符；若既有 `STARTED.json` 没有完成收据，会停下要求先核实原进程，避免把观察超时当作任务失败而重复启动。

本机作者源码与环境依赖路径见 [ENGINE_NOTES.md](ENGINE_NOTES.md) 和 [ENGINE_VALIDATION.json](ENGINE_VALIDATION.json)。这是已有作者环境中的可复现执行入口，不能把硬编码本机路径称为任意机器免配置安装包。数据归档包含未修改作者源码和初始路径的恢复说明。

## 工件

|路径|内容|
|---|---|
|`data/REGISTERED_MATRIX.json`、`data/CASES.json`|45初始路径登记、输入及原作者规划输出；含全部失败分母|
|`EXPERIMENT_REGISTRATION.json`|科学运行前的扰动、尺度、split、预算及源码固定值|
|`engine.py`、`PUBLIC_SCHEMA.json`|连续执行、END/POSITION可见性、作者优化调用与共同采用约束|
|`policies.py`|固定/历史/学习查询和按族训练|
|`training/PAIRS.json`、`LABELS.json`、`OMISSIONS.json`|实际完整配对、公开前缀、合法标签和缺失原因|
|`MODEL_FROZEN.json`、`MODEL_FREEZE_RECEIPT.json`|训练得到的模型、hash及先于新评价的冻结时间|
|`episodes/`、`author_cache/`|逐执行日志、原图/采用图、约束模型、精确内容复用来源|
|`review/`|不导入候选引擎的独立输入、轨迹、约束、模型与完整矩阵核验|
|`SUMMARY.*`、`TOTALS.csv`、`ANALYSIS.json`|完整分母、逐场景结果、按独立族配对与描述性不确定性|
|`figures/`|从冻结汇总读取生成的SVG/PDF/600dpi PNG，不触发新仿真|

全部登记结果和独立核验已完成。逐执行原始证据、缓存及审核明细通过 `package_results/` 无损分卷保存；直接阅读入口保留源码、模型、汇总、报告和图。恢复说明、逐成员 SHA256 与依赖关系见 `package_results/PACKAGE_MANIFEST.json`，完整性终标记为 `PACKAGE_COMPLETE.json`。

## 边界

本轮是标准 MAPF 路径上的连续点机器人执行实验，不是 ROS、非零足迹控制保证或持续任务开放 LMAPF。所有方法共用的作者适配明确登记；内部查询规则是信息策略对照，不冒充独立发表算法。六个测试地图/场景族支持本组新场景比较，不能声称未见地图类型泛化。模拟执行时间和实际求解wall time分列，未把求解耗时折算成实际在线延迟或生产收费。
