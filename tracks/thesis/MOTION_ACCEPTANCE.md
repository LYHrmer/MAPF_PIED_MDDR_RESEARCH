# 以运动完成时间接纳完整候选

2026-10-25。**实现及人工软件核验完成，科学任务运行0项。** 本接口只在提供的完整候选集合内选择，以同一名义局部依赖调度下的精确 `J=Σ_i T_i` 为目标；不是运动目标路径搜索器，不保证找到所有较快方案，也不是ADDRESS作者算法的新实验复现。当前下界筛选是简单强对照，不认定创新。

## 已接通的事务

现有 [plan_selection.py](plan_selection.py) 的 `MotionPlanSelector` 由 [compare_nominal_motion.py](compare_nominal_motion.py) 新协议 `thesis_motion_acceptance_v1` 的真实worker调用。两臂分别为 `full_recompute` 与 `primitive_lower_bound`，共用相同初解、固定候选顺序、模型、调度器、连续检查器和每臂绝对wall预算；后者只多一次廉价必要条件检查。没有新优化器或训练调用。

1. 先克隆固定验证器的problem与初向，将初始完整路径交给现有 [local_scheduler.py](local_scheduler.py) 构造和连续认证。未建立初始证书即到期或失败时，返回明确的初始化失败、无已认证结果，不能把原离散初解称作运动安全回退方案。
2. 建立证书后，将地图、端点、模型、初向、调度器、检查参数和完整路径绑定到私有序列化状态。调用方得到的是独立副本，修改输出或原problem不会改变已经认证的incumbent。
3. 每个候选先检查完整离散合法性。筛选臂复用精确原语块计算 `L=Σ(MOVE时长+TURN时长+原离散WAIT时长)`，包括每车任务初向产生的首个转向。原地等待也占原声明MOVE槽；180°使用自身原语，不能直接算两倍90°时长。额外依赖等待非负，因此 `J≥L`；若 `L≥当前精确J`，直接保留现方案。此下界不提供几何安全证书。
4. 未被拒绝者必须完成原局部依赖构造、初始/动作间等待、车身、障碍及永久终点驻留的连续充分检查。只有完整证书建立且精确有理数J严格减少，才在同一预算最后检查后交换整个状态。浮点展示值不参与接纳。
5. 环、充分分离未建立、显式非法候选、预算截尾均保留已认证状态；其中外包不分离不称真实碰撞，环不称全问题无解。内部意外异常另标 `IMPLEMENTATION_FAILED`，保留状态同时让worker/批次硬失败并停止余项，不能混入正常无改善。

`local_scheduler`新增可选checkpoint，贯穿原语块、依赖配对、DAG推进、动作遍历、区间细分和连续检查；不传callback的旧调用语义保持。截止异常不被吞为非法输入。初始和候选的构造、检查、快照、序列化和提交均计费；事务stage时间嵌套于整个arm/case，不能重复求和。

## 固定来源与已知边界

新增 [motion_acceptance.lock.json](motion_acceptance.lock.json) 读取SCI证据提交 `f9c651ad0680679cf99a4973f722b65fd6f7aa97` 的10个固定Git对象：完整输入、总收据和两份s05/n32任务的all/gate完整输出及其收据。对应ADDRESS科学代码为`2bd1916`；两个已有final依固定次序作为候选，不重新搜索。源批清单曾把邻域参数8误写为硬上限、实际三次达到9，该偏差保留为来源元数据。它们是已经参与设计的开发材料，不是独立留出测试。

候选提供者与底座版本分开标注：离散validator、`SharedBudget`和外层supervisor仍固定SCI `535ee1a`，经原blob/SHA读取器加载；旧 `sci.lock.json`、`plan_selection.lock.json`、`shared.lock.json`及全部科学证据不变。没有复制ADDRESS实现，不读取SCI工作树HEAD。旧REMAINING_BOUND结果没有被改称最新ADDRESS。

本接口消费的是已有ADDRESS最终候选，**未把运动目标接入一次新的ADDRESS搜索循环**。原SOC剪枝未必生成稍长但更快的路线，因此当前结果范围始终是给定候选集。后续若接入新候选生成，需单独声明生成阶段的SOC限制和完整费用。

## 软件核验与静态提案

现有 `test_local_scheduler.py`、`test_compare_nominal_motion.py` 共29项手写人工夹具通过，其中包括：初向/180°/离散等待下界，`L=J`不调用昂贵评价，无下界臂确实完整评价，同一候选集两臂一致，实际worker生成两臂产物，认证完成后到期不提交，初始认证到期无伪回退，环/证书失败/非法候选保留，外部对象篡改不影响私有状态，以及内部TypeError/KeyError/RuntimeError硬失败关闭后继候选。软件夹具不是新科学任务；没有调用冻结s05任务的调度构造或求解器。

独立代理另用5项人工反例核对初始认证晚返回、序列化跨截止、等号下界拒绝、输出对象篡改和下界内部意外异常；只验证软件合同，不认证新方法性能。可核对记录见 [软件收据](derived/motion_acceptance_software.json)。

[接口提案manifest](config/motion_acceptance_v1_manifest.json) 当前SHA为 `6b1e9de27e6f78d133b013ae560d35307d84c9ca5b6fe029372c39274342da10`。只执行了以下只读检查，返回 `PINNED_ADDRESS_INPUT_INTERFACE_ONLY_NO_MOTION_COMPARISON`，未构造任务、运动或搜索：

```bash
rtk proxy python3 -B tracks/thesis/compare_nominal_motion.py inspect --manifest tracks/thesis/config/motion_acceptance_v1_manifest.json --sha256 6b1e9de27e6f78d133b013ae560d35307d84c9ca5b6fe029372c39274342da10
```

提案写明每臂20秒评价＋2秒输出；每任务总准入60秒、worker CPU45秒/512MiB、单文件16MiB、外层62+2秒，两任务外层合计128秒、零重试、首硬失败停。**这是尚未验证能完成的接口预算，不是已就绪的科学运行清单。** 新32车初始完整认证耗时未知，旧16车的9秒数据不能用来保证它能在20秒完成；本轮不要求立即运行、不自行延长预算，也不重用旧授权。

固定 `SharedBudget`只做wall软截止，CPU仅计费；CPU硬限制由原supervisor执行。固定SCI离散validator内部没有checkpoint，单次Python/序列化操作也不能保证任意规模可抢占，外层进程限额仍必要。硬杀或初始化失败不能保证返回已认证方案；保留方案的合同适用于已经建立证书且正常走协作回退的事务。最终结果写盘、fsync、哈希与监督等待计入完整case费用，父管理收据自身写盘边界另列。

下一科学比较应先固定实际可承受的输入与预算，不从初始认证未知跳到大批量运行。比较最终完整J、SOC、makespan、候选拒绝/截尾/硬失败、所有构造检查与输出成本；同样J且更少评价只能支持该给定集合上的计算结果，不自动成为路径质量贡献。若简单规则解释全部差异，保留其强对照角色；只有同下界、同缓存、同回退的完整重算仍留出空间，再研究明确的增量更新。v2、学习和实物未接入本轮。
