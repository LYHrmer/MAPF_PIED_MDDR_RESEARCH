# 无误差完整任务三方案比较：已消费的冻结清单

**当前状态：六项×三臂已完成，零硬失败、零重试，本批许可已消费。** 运行使用本轮用户“先完成已准备好的……三臂运动比较”的新指示，未借旧SCI许可；[结果报告](MOTION_RESULT.md)、[实际授权与管理记录](results/nominal_motion_v1/AUTHORIZATION.json)及[批次收据](results/nominal_motion_v1/RUN_RECEIPT.json)保留完整先后与费用。下文原输入、预算、停止条件和命令作为冻结执行记录保留，不产生新授权。原JSON字节与SHA保持不变，因此其中历史 `PENDING_USER` 字段不得作为当前状态或新许可。没有运行求解器、训练、world或误差扩展。

## 固定输入与比较范围

配置：[nominal_motion_v1_manifest.json](config/nominal_motion_v1_manifest.json)，SHA-256：`dfac22c05d73e712cadc8937e2ccc4a855e2764ef8f2b4c5f4f9546dd33b3b7c`。代码与锁的完整8项SHA集合在配置中，缺项或变化拒绝启动。SCI输入、摘要、六份result/receipt共14个对象由现有[sci.lock.json](sci.lock.json)固定到提交 `535ee1adf3135ab79565e0b3aa5d189348fe7ab2`；总输入SHA为 `be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b`。执行前还应登记本配置对应的大论文提交，不能改用两个工作树的最新文件。

这些是旧 `repair_residual_v1 / REMAINING_BOUND` 六份完整DEV路径，**不是后来完整ADDRESS的六份结果**，也不冒充独立性能任务。使用原输入和当时完整最终路径，保留原始优化费用及其统计口径，仅新增运动适配比较；当前ADDRESS的预算退出修补与本批分开判断。共享完整validator及进程supervisor均从同一SCI固定Git对象加载，blob、提交和SHA先核对后执行，不复制优化器，不启动NativeBackend。

每任务固定三臂：

1. `original`：原完整合法方案。
2. `frozen_soc`：冻结SCI结果中的完整最终方案，等SOC也保留当时的真实改路，不静默替换为原方案。
3. `turn_aware`：复用整方案规则，在原方案、冻结方案及一次同时恢复等成本旧路径的批量方案中，按(SOC、内部四分之一圈数、改路车辆数)选取。每个候选先完整检查全体冲突及永久终点；不逐车回滚，不按本次运动完成时间反向挑选，也不是转向最优搜索。

三臂均使用同一运动、几何、初向和等待规则；先检查离散路径，再检查转弯/移动/等待/终点驻留的连续圆外包充分分离。

## 声明的仿真参数与限制

| 参数 | 固定值 |
|---|---:|
| 一格边长 | 0.5 m |
| 中心参考点矩形车身长×宽 | 0.22×0.16 m |
| 直线速度上限 | 0.5 m/s |
| 直线加/减速度上限 | 各0.5 m/s² |
| 角速度上限 | 1 rad/s |
| 角加/减速度上限 | 各1 rad/s² |
| 每台车初始朝向 | 全部向东，E=0 |

上述值是明确选择的理想仿真参数，**不是LIMO实测值**。初向不按每臂首条边变化。每步先全局转向barrier，随后移动者共享一条从静止到静止的进度曲线；短转向结束者等待最长转向完成；离散等待占一个完整直行槽。完成后永久驻留，驻留不计入完成前等待。该等待规则会增大保守性，结论只针对该模型，不外推最优连续调度或真实异步控制。空间误差未接入，不能用本批证明v2适用或持续跟踪扰动安全。

障碍宽相位只减少显然不可能触及的闭格方块：外接圆半径不大于(长+宽)/2，窗口外由轴向距离严格分离；窗口内仍用精确有理数最短距离。三臂共用，无额外算法贡献声明。

## 预算、费用和停止条件

固定按下列顺序执行6项；每项包含三臂，合计18个完整参考构造。每项从Python进入、导入、两次Git读取和SHA校验，到选方案、全部离散/连续检查、日程构造、指标检查、序列化、fsync和产物哈希，**成功准入总wall≤60秒**；worker CPU≤45秒、地址空间≤512 MiB、单文件≤16 MiB。预留2秒完成输出/哈希；外层62秒TERM、再2秒KILL，六项硬保护合计≤384秒。进程监督器复用固定 `run_repair_dev.py`，不重新实现。管理receipt的最终写盘和进程退出不含在60秒自计时内，由外层硬保护覆盖，并在收据明确说明。记录各臂构造/验证、选择、指标及写盘时间、共享读取成本和总准入成本；嵌套计时不相加。历史优化费用单列，不能冒充本次新增成本。

零重试。任一输入/代码/SHA变化、异常、非法离散输入、缺初向、时间无法表示、CPU/内存/输出超限、非零退出、强制清理、输出不完整或总准入超预算，立即停整批，保留已完成、失败和未运行名单，不用剩余额度修复后续跑。每项独占输出目录，已有目录拒绝覆盖，后项要求所有前项收据成功。

正常的 `CIRCLE_*_NOT_ESTABLISHED` 返回记为 `SUFFICIENT_SEPARATION_NOT_ESTABLISHED`：保留原因，完成时间/等待为null，不记成碰撞、不从分母删除，不自动调整车身/尺度/时间；这是一项完整得到的科学负结果，允许按原顺序继续。invalid输入/日程异常则停批。

结果保存 `tracks/thesis/results/nominal_motion_v1/<case>/`：attempt、worker stdout/stderr、每臂完整参考或拒绝原因、任务result和成本/哈希receipt。结果主指标是完成时间之和，辅以makespan、完成前等待（转向barrier与离散等待分列）、可行充分条件状态、每车完成时间与全部计算成本；保留无收益和失败项。只有三臂同模型完整比较后才判断离散收益是否保留；无差异就保留模型适用性结论，不声称方法创新。

## 具体命令

工作目录 `/home/lyh/MAPF_THESIS_RESEARCH`。授权前可执行下列固定字节检查，它不构造任何真实任务运动日程：

```bash
rtk proxy python3 -B tracks/thesis/compare_nominal_motion.py inspect --manifest tracks/thesis/config/nominal_motion_v1_manifest.json --sha256 dfac22c05d73e712cadc8937e2ccc4a855e2764ef8f2b4c5f4f9546dd33b3b7c
```

取得本批原始用户授权后，先另存实际授权引用和本次提交，再将下列占位引用替换为该引用；文件/参数本身不产生授权。每次核对收据与三个臂结果后才执行下一条，禁止并行或循环忽略退出码。

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 62s python3 -B tracks/thesis/compare_nominal_motion.py run --manifest tracks/thesis/config/nominal_motion_v1_manifest.json --sha256 dfac22c05d73e712cadc8937e2ccc4a855e2764ef8f2b4c5f4f9546dd33b3b7c --case maze-32-32-2__s01__n16 --authorization-reference 'REPLACE_WITH_ACTUAL_NEW_USER_AUTHORIZATION'
rtk proxy timeout --signal=TERM --kill-after=2s 62s python3 -B tracks/thesis/compare_nominal_motion.py run --manifest tracks/thesis/config/nominal_motion_v1_manifest.json --sha256 dfac22c05d73e712cadc8937e2ccc4a855e2764ef8f2b4c5f4f9546dd33b3b7c --case maze-32-32-2__s01__n32 --authorization-reference 'REPLACE_WITH_ACTUAL_NEW_USER_AUTHORIZATION'
rtk proxy timeout --signal=TERM --kill-after=2s 62s python3 -B tracks/thesis/compare_nominal_motion.py run --manifest tracks/thesis/config/nominal_motion_v1_manifest.json --sha256 dfac22c05d73e712cadc8937e2ccc4a855e2764ef8f2b4c5f4f9546dd33b3b7c --case random-32-32-10__s01__n16 --authorization-reference 'REPLACE_WITH_ACTUAL_NEW_USER_AUTHORIZATION'
rtk proxy timeout --signal=TERM --kill-after=2s 62s python3 -B tracks/thesis/compare_nominal_motion.py run --manifest tracks/thesis/config/nominal_motion_v1_manifest.json --sha256 dfac22c05d73e712cadc8937e2ccc4a855e2764ef8f2b4c5f4f9546dd33b3b7c --case random-32-32-10__s01__n32 --authorization-reference 'REPLACE_WITH_ACTUAL_NEW_USER_AUTHORIZATION'
rtk proxy timeout --signal=TERM --kill-after=2s 62s python3 -B tracks/thesis/compare_nominal_motion.py run --manifest tracks/thesis/config/nominal_motion_v1_manifest.json --sha256 dfac22c05d73e712cadc8937e2ccc4a855e2764ef8f2b4c5f4f9546dd33b3b7c --case warehouse-10-20-10-2-1__s01__n16 --authorization-reference 'REPLACE_WITH_ACTUAL_NEW_USER_AUTHORIZATION'
rtk proxy timeout --signal=TERM --kill-after=2s 62s python3 -B tracks/thesis/compare_nominal_motion.py run --manifest tracks/thesis/config/nominal_motion_v1_manifest.json --sha256 dfac22c05d73e712cadc8937e2ccc4a855e2764ef8f2b4c5f4f9546dd33b3b7c --case warehouse-10-20-10-2-1__s01__n32 --authorization-reference 'REPLACE_WITH_ACTUAL_NEW_USER_AUTHORIZATION'
```
