# 等成本改路与运动适配：现有六任务的离线诊断

> 本文保留运动模块实现前的离线诊断，不再代表当前运行状态。六任务三臂比较已完成，最新结果及0.5m/格下v2资格决定见[MOTION_RESULT.md](MOTION_RESULT.md)；旧几何证据与下文历史判断原样保留。

状态：`OFFLINE_EQUAL_COST_AND_DISPLACEMENT_AUDIT`，`new_experiment=false`。本轮只解析SCI固定提交`535ee1adf3135ab79565e0b3aa5d189348fe7ab2`的输入及最终结果；未生成新路径、调用SIPP、枚举真实任务上的路径组合、启动world或训练。六项科学DEV许可已消费。两条研究线仍是候选问题，当前不承诺独立学习/RL章节。

## 现象分解：哪些车以什么代价改变了路线

[inspect_sci_paths.py](inspect_sci_paths.py)沿用[sci.lock.json](sci.lock.json)的14个SCI Git对象，逐一校验提交、blob、SHA以及result/receipt关联；本轮只新增独立`source_contract`字段绑定下面的v2条件文档。新产物[derived/sci_equal_cost_structure.json](derived/sci_equal_cost_structure.json)保存本轮lock SHA并保留全部六任务及每车条目。原[derived/sci_path_structure.json](derived/sci_path_structure.json)原位、原字节保留，对应历史生成器和旧lock见提交`32db58f`；当前生成器在原几何定义之上增加下列分组。

这里的“成本”是路径顶点数减一，包括移动和等待；“等成本改路”要求新旧序列不同且成本相等。转向量由移动格边方向变化计算，等待不产生新方向，180度计两个四分之一圈。这不等于真实车辆旋转或完成时间。

| 任务 | 完全未改 | 等成本实际改路：数量 / 转向变化 | 缩短：数量 / SOC变化 / 转向变化 | 变长：数量 / SOC变化 / 转向变化 | 总SOC / 转向变化 |
|---|---:|---:|---:|---:|---:|
| maze16 | 9 | 6 / +13 | 1 / -1 / -2 | 0 / 0 / 0 | -1 / +11 |
| maze32 | 24 | 4 / +8 | 3 / -5 / -2 | 1 / +3 / +12 | -2 / +18 |
| random16 | 16 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 |
| random32 | 1 | 29 / +113 | 1 / -2 / -5 | 1 / +1 / 0 | -1 / +108 |
| warehouse16 | 16 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 |
| warehouse32 | 32 | 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 |

random32中，29条确实改路的等成本路径贡献全部+113；它们合计移动和等待均未变化。agent19移动减少2步、转向减少5，agent3增加1步等待、转向不变，agent8完全未改。因此两条成本变化路径共同贡献SOC -1和转向 -5，而非“两条都缩短”。maze32也存在一个成本+3的agent31；整体接受不能理解为每台车都改善。

## 作者实现给出的线索及尚未成立的归因

实际SCI桥接入口是固定提交`535ee1a`中的[address_sipp_bridge.cpp](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/535ee1adf3135ab79565e0b3aa5d189348fe7ab2/tracks/sci/address_sipp_bridge.cpp#L70)：每次请求设定seed后调用原版`SIPP::findPath`。只读核对的作者缓存HEAD是`b3d35c431ce03834f95e834d87986f2f341394a1`且工作树干净。

- [SIPP::findPath](https://github.com/JimyZ13/ADDRESS/blob/b3d35c431ce03834f95e834d87986f2f341394a1/src/SIPP.cpp#L28)从FOCAL取节点，接受满足目标驻留条件的到达路径。
- [LLNode::secondary_compare_node](https://github.com/JimyZ13/ADDRESS/blob/b3d35c431ce03834f95e834d87986f2f341394a1/inc/SingleAgentSolver.h#L36)依次比较冲突数、f、h，最后用`rand()%2`打破平局。原节点/比较器没有朝向、累计转向或原路径相似度目标；[SIPP状态等价](https://github.com/JimyZ13/ADDRESS/blob/b3d35c431ce03834f95e834d87986f2f341394a1/inc/SIPP.h#L43)也不包含朝向。
- [Instance::getNeighbors](https://github.com/JimyZ13/ADDRESS/blob/b3d35c431ce03834f95e834d87986f2f341394a1/src/Instance.cpp#L455)按右、左、下、上构造合法邻居。

这些代码支持“现有求解器没有主动维持等成本旧路径或最小转向”的判断。它们尚不能证明+113由随机平局或某个邻居顺序导致；允许约束、其他车辆路径和顺序同时变化，部分等成本改路可能为别车释放空间。也不能只改堆比较器就声称求得最少转向路径：朝向相关代价还会影响状态合并和支配规则。本轮未修改作者实现，也未做归因实验。

## 已实现的简单整方案对照

[plan_selection.py](plan_selection.py)接收合法初解和一份已生成的完整候选；不提供路径搜索器。通过[plan_selection.lock.json](plan_selection.lock.json)引用SCI同一固定提交的`pp_repair.py`和`address_backend.py`，先核验所有模块字节再导入；只使用现有`GridProblem.validate`，不构造`NativeBackend`。不复制优化器或validator。

| 规则 | 被检查的完整方案 | 选择目标（字典序） |
|---|---|---|
| `soc_only` | 初解、原候选 | SOC；相等保留初解 |
| `preserve_equal_cost` | 上述两项，另加一次同时恢复所有等成本旧路径的批量候选 | SOC、改变路径数 |
| `turn_aware` | 与保留规则完全相同的三项 | SOC、内部转向量、改变路径数 |

每个候选必须通过全体车辆的地图、端点、顶点、对向边及永久终点占用检查；非法混合方案整个拒绝。选择后再检查最终整方案。不逐车贪心提交，不枚举组合，不声称最优转向、不改变主要SOC目标。转向规则只在给定候选中使用几何次目标，不能作为新的路径优化算法贡献。

软件夹具已经覆盖：旧路径单独恢复后与别车冲突而必须拒绝；相同SOC下保留规则与转向规则选择不同；候选穿过其他车永久终点或缺车时保留合法初解；非法初解不可悄悄修复。9项路径/选择软件检查通过（其中5项几何与固定证据检查、4项整方案规则检查）。未把该选择器用于六个真实DEV任务生成新比较结果。

```bash
rtk proxy python3 -B tracks/thesis/test_export_frozen_trace.py SciPathStructureTests WholePlanSelectionTests
```

后续比较须把候选构造、完整检查和最终检查全部计入总预算，并与各规则共享同一候选来源和验证器。这里的接口没有给当前六任务新增任何性能结果或运行许可。

## 先无误差运动，再检查v2误差来源是否适用

下一阶段首先声明统一直行、转向和等待原语，以相同车身和运动条件重排全部车辆时序，检查转弯扫掠、等待和终点驻留，判断离散收益能否保留。不能用每车转向数量相加代替全车连续安全检查。该适配尚未实现；此时不把误差导致的保守性与名义运动代价混合。

之后再加入误差：现有v2每车一组初始位置/朝向偏差贯穿整个任务，实际与参考采用同一实际输入、暂停/恢复/动作时钟同步；零输入等待无漂移。不逐段或在路点重置，也不称一般持续跟踪误差。固定外包与传播外包须共享允许初态集合、原语、信息和调度器，分别核对哪条约束改变、增加多少等待、哪些方案失去可行性。无差异就保留适用性/敏感性分析。

原v2必要条件包括每轴相对初点位移不超过8m、MOVE长度0.25–3m以及其他速度/控制/坐标条件。来源是固定[COMPOSITION.md](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/16b1ee089be20cafaf4818c3dbb7b259659b021d/exploration/spatial_source/COMPOSITION.md)，完整commit、blob和SHA登记在lock的`source_contract`及新产物中；分析器校验文档字节和这两条原声明，不导入或执行误差模型。对旧初解和已接受结果，离线最大轴位移完全相同：

| 任务 | 最大相对x/y位移（格） | 若一格边对应原MOVE，统一尺度s的必要区间（m/格） |
|---|---:|---|
| maze16 | 22 / 29 | [1/4, 8/29] |
| maze32 | 28 / 29 | [1/4, 8/29] |
| random16 | 28 / 29 | [1/4, 8/29] |
| random32 | 30 / 29 | [1/4, 4/15] |
| warehouse16 | 133 / 49 | 空：1/4 > 8/133 |
| warehouse32 | 136 / 49 | 空：1/4 > 1/17 |

依据是`s >= 0.25`且`s*Dmax <= 8`。这只适用于“每格边为一个原MOVE、全图统一尺度”的映射；不推广到重定义动作/模型。warehouse两案不能仅靠这种统一缩放满足两条必要条件；maze/random区间非空也不代表车身净空、绝对坐标≤10m、原语速度/制动或同步条件成立。假设1m/格时六案全部不满足8m轴界。当前没有选择地图尺度、自动缩放或扩大v2适用域。

后继的具体交付是：在新科学比较前补齐完整多车无误差原语适配及独立检查；选择尺度/车身/控制条件后单独做v2资格报告，再考虑误差比较。两台LIMO自身定位/里程计不提供独立真值，实物仍是可选验证。
