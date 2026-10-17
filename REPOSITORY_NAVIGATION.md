# 当前工作区与历史归档

2026-10-16。按现行职责保留四个活动分支，旧学习分支由历史标签保存。本页同时记录入口整理和之后的有限物理清理；工作树、实验原始记录和冻结证据保留。

**当前：CTC同模型消元适配得到相同联合相位界，关闭独有收紧候选。** 两个有效动作对独立投影相等，其余九对同一回退，十一最终约束不变。完整PSIPP/CTC系统复现、T1全流、独立任务及总成本仍缺；不把本项目适配写成作者原版能力。C1平移投影及同信息放行的旧负结果保持。四分支按需要分工，不扩为四个课题或强求每轮代码；旧学习停止。[唯一当前判断](SPACE_TIME_INTERFACE_PLAN_20261016.md) · [公式、实现与证据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/DEPARTURE_NOTICE.md#ctc同模型消元适配联合相位收紧不是独有能力)。各分支从`.github/README.md`进入，旧清单不构成重启授权。

| 入口 | 当前职责 | 本机路径 |
|---|---|---|
| main | 一个论文问题、统一合同、验收和结论 | `/home/lyh/MAPF_PIED_MDDR_RESEARCH` |
| explore/error-aware-guidance | 空间占用—冲突—释放及完整执行比较 | `/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE` |
| explore/gaussian-mapf-feasibility | 声明动力学、动作条件、误差范围及覆盖 | `/home/lyh/MAPF_GAUSSIAN_FEASIBILITY` |
| explore/query-value-feasibility | 合法反馈、配对日志及费用工具 | `/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY` |
| archive/learned-query-20261016（标签） | 停止的查询学习历史、正负结果 | `/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE`，detached HEAD |

分支名称保留以免扰动其他窗口，但 gaussian/query 不代表独立选题。main只维护问题、证据和决定；执行分支只推进连续占用、时窗和构造；来源分支负责传播与覆盖，不要求高斯；工具分支负责合法反馈、配对和完整成本，不恢复“查询谁”。公共协议已有字段够用，算法确需新字段时才改。RL、换序和LMAPF后置；不以提交轮次或检查数量表示科研进展。

## 日常只读这些入口

1. [统一研究方案](SPACE_TIME_INTERFACE_PLAN_20261016.md)：问题、模型、四组比较、外部基线、继续/停止条件。
2. [最小空间—执行实例](SPACE_TIME_MINIMAL_EXAMPLE_20261016.md)：坐标、约束、释放及失效情形。
3. [当前进度](GITHUB_PROGRESS.md)：已完成、失败、待验证与运行状态。
4. [最新来源报告](PROBABILISTIC_ERROR_SOURCE_20261016.md)：G2c 两次失败、短 IPC 清单及边界。
5. [文献依据](LITERATURE_GUIDED_RESEARCH_PLAN_20261016.md)：固定版本和近邻定位，后续决策以统一方案覆盖。

MANUSCRIPT_PREEXPERIMENT.md 保留用户未提交修改。旧概率诊断、仿真说明及编号文档是证据；不把旧“下一步”或已消费授权作为当前任务。

## 清理范围与恢复

| 快照标签 | 原提交 | 从当前 Git 列表退出的文件数 |
|---|---|---:|
| archive/pre-cleanup-main-20261016 | bedf23b8 | 263 |
| archive/pre-cleanup-execution-20261016 | 0e1cc23b | 293 |
| archive/pre-cleanup-source-20261016 | e48d218f | 293 |
| archive/pre-cleanup-tools-20261016 | 36564301 | 1698 |
| archive/learned-query-20261016 | 57aee7b6 | 整条停止分支归档 |

共 2547 个重复/历史文件退出活动 Git 列表，其中公共工具分支的 1405 个旧学习文件回到历史快照。main 保留当前文稿引用闭包内的 27 个编号文件及统计工具，避免破坏在用引用。三个支线的旧根 README、旧主稿和导师简报也退出当前 Git 列表，改用 `.github/README.md` 指向 main。

上述归档标签已先推送并核对远端 SHA。2547 项使用 `git rm --cached` 保留冻结原路径字节；这一步没有物理删除数据，也没有回收磁盘空间。本机根目录仍可见冻结文件，GitHub 当前文件列表与日常入口已精简。main 的约 69 GB 主要是历史证据、第三方依赖和 Git 对象，不能按“旧文件”整体清空。不得用 `git clean -fdx` 清理这些保留文件。

历史内容可在 [GitHub 标签列表](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tags) 查看。读一个旧文件可使用：

```bash
rtk proxy git show archive/pre-cleanup-main-20261016:GITHUB_PROGRESS.md
```

若以后确需恢复旧分支，先检查本机 detached 工作树和其他窗口，再从 `archive/learned-query-20261016` 建分支；不直接覆盖现有目录。旧学习分支存在 16 个独有历史提交，标签完整保护；其已跟踪代码与公共工具分支旧快照相同，但本机未跟踪内容不同，故保留原目录。

本机整理前逐文件 SHA、移出清单与整理后核验保存在 `implementation_binding_evidence/repository_cleanup_20261016/`。未复制大型目录，冻结证据及失败不回写。后续新增代码进入各分支单一活动模块，轮次写入同一进度文件，不再每轮生成一套孤立目录。

## 追加物理清理

已删除根目录中四份过时说明：`task_plan.md`、`findings.md`、`progress.md` 和 `RESEARCH_DIRECTION_RECOMMENDATION_20260919.md`。前三份停留于 9 月 14 日的旧付费查询准备，后一份仍以查询评分为主要方向，均已由现行方案覆盖。删除前，原文保存至 [archive/superseded-local-notes-20261016](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/archive/superseded-local-notes-20261016)，归档提交 `ed5dc232`；远端提交和逐文件 SHA 核对后才删除本地副本。

四份文件共 31,752 字节，另删除 13 个空的 `__pycache__` 目录。本次清理量很小，没有显著回收磁盘空间。逐项清单保存在同一清理目录的 `PHYSICAL_CLEANUP_20261016.json`，没有新增科学运行。

`LEARNING_ASSISTED_OPTIMIZER_PLAN_20261011.md` 和 `RESEARCH_PORTFOLIO_20261010.md` 已过时，但历史交付清单仍绑定其绝对原路径和 SHA，须原位保留；不能以标签备份替代这项约束。旧学习目录的部分编译文件也已进入冻结或执行收据，保留原路径。主稿未提交修改保持不变。

## 停止路线留下的经验

- **先消除对照的信息差。** 当前例中，几何、反馈和事件粒度相同时，SADG 事件适配也能得到相同放行。相对粗 END 的提前不能直接算作独立调度贡献；这个结果也不说明所有任务上方法等价。
- **动作拼接必须继承误差。** 每台车整条轨迹共享任务初始位置与朝向的联合参数，车身朝向使用同一偏差。旧固定初态界的拼接失败应保留，不能在路点重置误差后扩实验。v2 的同步实际输入条件改变后，推导也要重做。
- **空间和时间都要保留。** 扫掠外包重叠不等于发生碰撞，依赖图无环也不等于连续执行可行。还要检查已承诺动作、等待、制动及永久驻留；放行须依据有效反馈支持的范围，计划时钟不是退出确认。
- **学习需要明确用途。** 简单解析模型不必训练误差预测器。以后学习即使不改变最终决策，也可凭含校验、回退和数据成本的净计算收益进入比较；相对调优后的解析方法和查表仍无增量，就停止该候选。
- **把接口、实验和论文证据分开。** 合同检查通过及两三车任务验收是必要准备，不能代替独立任务表现。旧查询学习、规划停止和 L20/L21 扩展保持停止，不通过增加分支或场景寻找正结果。
- **归档与删除分别处理。** Git 忽略、停止使用和可删除不是同一件事。先核对活动引用与冻结路径，保存尚未备份的原文，再删明确过时的副本；后续在现有模块中迭代，避免再次复制整套目录。

## 三轮后继的最新入口

四个活动分支在T1之后又完成三轮实质推进：全局事件因果性修正 → 首尾窗口等价构造 → 完整消息配对和失败账目。累计15→53→99项静态检查通过；22个动作—区域窗口与12条约束保持精确一致，外包求值8738→446。此为工程操作数改进，总实耗仍未测。两臂同样采用优化，旧放行相同的结果保留。

现从[统一方案的后继三轮节](SPACE_TIME_INTERFACE_PLAN_20261016.md)和[QUALIFICATION_NOTICE.md](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/QUALIFICATION_NOTICE.md)进入。来源/工具各在原模块增加 `qualification.py`，执行复用原 S1 模块的 `qualified_session.py` 和 `verify_qualified.py`，不复制框架。T1旧入口继续冻结。

“相同证书事件接线”已退出独立论文贡献候选，非学习工程基座仍保留。用户最新明确只实现和静态核验，所有科学运行待授权；后继不能沿用或静默替换T1清单。下一终端先核定具体额外贡献再决定是否准备后继运行，不重做已完成三轮、不恢复旧查询/LMAPF。主稿未提交修改及冻结证据继续保留。

## T1入口（后继沿用的冻结基座）

物理时间占用和两/三车完整公共消息接口已实现，87项新静态检查及63项C1回归通过。固定夹具的两臂放行、完成、消息流及证书工作量相同，没有独有保证；总进程成本未测。旧C1和早期冻结结果不变，主稿未提交修改保留。

下一终端先读[方案最新T1节](SPACE_TIME_INTERFACE_PLAN_20261016.md)和[执行模块T1说明](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/TIMED_NOTICE.md)。来源新增 `spatial_source/timed.py`，公共工具新增 `execution_feedback/timed_protocol.py`，执行仍在原 S1 模块，不新建研究分支或复制框架。

自主完整事件循环入口已准备但未执行；[有限运行清单](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/TIMED_RUN_CHECKLIST.md)固定4子进程及输入SHA，须有绑定该清单的新明确授权才能启动。不要再次实现相同接口，也不要把静态夹具时间写成自主运行结果。若当前同证书接线在约束、算法成本和保证三项均无增量，结束候选，保留接口；不能靠新场景、训练或删弱基线制造结果。

## 上轮交接说明（已由上述T1实施推进）

请接续 `/home/lyh/MAPF_PIED_MDDR_RESEARCH`，先读 `REPOSITORY_NAVIGATION.md`、`GITHUB_PROGRESS.md` 和 `SPACE_TIME_INTERFACE_PLAN_20261016.md` 的最新补充，再读执行分支的 `COMPOSITION_NOTICE.md`。四个活动分支只分担同一论文问题，复用已有 v2 来源、C1 实例、SADG 事件适配及合法反馈/计费组件，不重搭框架。先在现有模块中补齐保留物理时间的连续占用：每台车整条轨迹共享同一任务初始位置—朝向联合参数，车身旋转使用同一朝向偏差，遵守 v2 同步实际输入及共同暂停、恢复、切换时钟的条件，不在路点重置误差。固定 MAPF 路径和已有通行次序，复用现有无环及起终点占用检查，补新增时空约束的时间可行性、已承诺动作、制动和驻留检查；不满足就明确报告不可行，不把外包重叠直接当作碰撞。随后补两三车从控制、合法反馈、释放到最终 END 的完整任务接口及总在线成本记录；放行依据有效反馈支持的状态/进度范围，不能只看计划时钟。向公平适配后的强基线提供相同几何、反馈、事件粒度、运动条件和安全要求，分别检验是否减少保守约束、降低总构造/更新成本或增加可证明保证；当前例放行相同的结论保留，三项均无增量则结束该贡献候选。先完成实质实现和必要静态检查，准备含具体命令、输入 SHA、预算、失败保留及停止条件的有限运行清单；本次不启动新 world、训练或旧查询学习/LMAPF 扩展，不复用已消费许可，科学运行按现行授权边界另行处理。保护主稿未提交修改和全部冻结证据，及时同步 GitHub，只提交本次明确修改的文件。
