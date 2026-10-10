# MAPF 项目当前状态

**研究路线更新（2026-10-10，P1）**：按用户最新要求，中心回到 **MAPF/LMAPF 结合空间跟踪误差**。候选主线为有界误差下的连续占用、冲突依赖与安全执行；先固定任务MAPF，LMAPF保留为同方法的持续任务扩展。允许基于已有方法组合改进，首个组合候选为有界误差占用＋ADG/SADG协调＋可选学习；查询与计费降辅助，两学习树合并研究职责；高斯限额探索，规划停止撤下活跃路线，既有NO_GO维持。追加反方检查恢复R8/R19正信号，限定R20负结果范围；仍未证明候选新意。详见[完整路线与各线建议](../RESEARCH_PORTFOLIO_20261010.md)及[P1记录](../GITHUB_PROGRESS.md#portfolio-p1)。当前新方法资格CONDITIONAL，本轮没有科学运行、训练或主稿修改；下列R54技术事实保持，旧研究优先级以P1为准。

**支线登记（2026-10-10，G1）**：按用户授权，新建独立高斯 MAPF 可行性支线 [`explore/gaussian-mapf-feasibility`](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/gaussian-mapf-feasibility/GAUSSIAN_HANDOFF.md)，提交 `44f7fdce65f3e9b869eb13a1db7853ccd92d44cc`。已登记候选问题、文献/作者工件、风险口径和六项资格卡；状态 CONDITIONAL，未构建原版、实现候选、运行科学实验或训练。主线保持有界模型和下列 R54 状态，主稿未提交修改保留。没有证据证明高斯模型天然更易录用；支线先查同风险要求下 MAPF 占用/冲突处理是否存在可改进空间，RL 后置。详见 [G1 记录](../GITHUB_PROGRESS.md#gaussian-g1)。

更新：2026-10-09，当前入口 **R54**。本轮发现旧完整训练数据合同无法满足至少两个TRAIN家族要求；按用户新授权另建三图来源登记，同时补运行监督、实际N端复制计量和成对超时清理。**查询价值学习仍未完成：0个新任务、0个合格TRAIN家族、0条可靠标签、0次训练与独立比较，研究有效性UNKNOWN。**

研究问题保持MAPF、有界空间跟踪误差与有限更新资源；方法主线为代价感知进度查询与安全协调。轻量价值回归/排序优先，RL为重点候选。只有独立比较显示同预算改善完成表现，或相近完成表现下降低完整资源，且安全与信息条件成立，才决定融入主线。

[仓库导航](../README.md) · [完整进度](../GITHUB_PROGRESS.md) · [R54](../GITHUB_PROGRESS.md#r54) · [R53](../GITHUB_PROGRESS.md#r53) · [物理边界](../GITHUB_PROGRESS.md#r47)

## 本轮实际成果

| 组件 | 实际交付 | 当前界限 |
|---|---|---|
| 训练资格判断 | 旧R44仅Berlin/Boston预留TRAIN；Boston原任务的乐观运动下界已超过H34，最多剩一个家族，少于拟合器要求的两个 | 旧完整标签合同NO_GO；研究整体CONDITIONAL，Berlin当前仅诊断并非永久排除 |
| 独立数据登记 | 核对empty-8-8、empty-16-16、maze-32-32-4的六个公开源文件、作者Git blob及全部公开端点 | 未选任务、分配角色或增加运行槽；两空地图结构相关，独立资格UNKNOWN |
| 名义生产监督 | 独立进程监督、真实身份/回收记录、失败非零退出及严格接纳后的原Batch生产调用入口 | 没有实际启动；Registration/Session尚未强制消费新ADMISSION |
| N端复制计量 | 实接Copy→Station→Event→Observer；累计/增量、失败前缀及新资源接纳入口 | 只覆盖模型内封装复制量；旧任务cost_audit尚未接，完整通信费用/报价UNKNOWN |
| 成对采集清理 | 每臂共享唯一cleanup截止；wait4成功后立即清除可发信号PID，再写日志 | 原参数不变；硬实时、阻塞I/O及完整进程树费用未合格 |

根与3子智能体定点互审；14个不同HOST源的最终对象统一编译并完成一项部分链接，已包含成对采集器修复，不重复计数。监督/数据模块仅做源码、AST、元数据及哈希检查；没有调用求解器、科学解析器或模型。

新来源登记得到用户明确授权，范围仅公开来源登记与静态检查。现拟合器以TRAIN内分组CV选择alpha，R53已移除query_threshold；最小2TRAIN+独立TEST在三图数量上可设计，独立CAL不是额外硬门槛。尚未锁定角色；文件不同不证明统计独立、查询机会或完整任务可完成。

## 判断与推进顺序

先冻结新来源的事前任务选择、角色与物理seed设计，避免按求解成功、参考距离或查询收益挑样本。继续补真实factory→三完整ELF/付费INIT→100实际计划→具体Session的持久化来源链，并让成对接纳消费；旧无条件来源阻断不能直接删除。

同镜像全栈/heap/有限窗口仍缺证明。当前逐行ServerMeter不是跨行账户；入账、预留、扣款和失败结算语义尚未给定，不能用row unused造余额。新增复制量只关闭一个计量分项，动态准备、传输、RA、清理、host及推理等完整未来报价仍UNKNOWN，单位分别保留。

运行条件齐备并取得具体授权后，先检验QUERY能否改变合法执行并改善完整任务，再采可靠标签、拟合冻结和独立比较。候选排序需要实际候选支持，未查询者无标签；RL还需多门状态、合法预算演化和完整episode，固定续策DeltaJ不是Q*。静态接线、中间提前或MSE不能证明方法有效。

主线仍四个重叠验收阶段：共同安全执行/费用资格；真实机会/可靠标签/方法冻结；授权独立比较；证据融合成稿。第一阶段未整体完成。20线本轮为5直接、8共享、4沿用、3后置：费用F有新增复制计量，价值V共享来源设计而无新模型。规划停止/文献/写作沿用，NO_GO不重开，持续任务/随机延迟/LIMO后置。

科研导师资格2PASS/4UNKNOWN、CONDITIONAL。查询价值支线位于/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY，explore/query-value-feasibility沿已提交explore/learned-query底座3c809f903e42ce33d287ca7f21e38924bd6dcffc。

## 数据、运行与保护

QUERY/WAIT保持同合法初态、同后续策略规则、配对外生来源，各臂仅读自身合法信息，动作可不同。普通END、WAIT、结构规则/EWMA及无额外/周期/年龄/阻塞对照保留；迟到、失败、零/负收益及未完成均保留。已查看R20只作开发，不挪用独立TEST。指标仍固定批次原任务末段service完成tick之和，不宣称吞吐；推理计入执行、训练另列，未知费用不记零。

授权仍为实现、静态检查、冻结和清单。科学目标、World、solver、仿真、codec/特征/模型/训练及机器人运行均0，NOT_AUTHORIZED / NOT_QUALIFIED / NOT_SCHEDULED。原名义提案ECBS w1.5、30秒、4GiB/进程、单worker、goal-hold、零重试不变；新外部监督45秒促停、50秒唯一结束界且不加额外宽限，仍不是内核硬截止。本轮未创建实际runtime输出。

H34/136、每tick2机会、8388608 B1/行、原64准备行、8192总行及原容量不变。q0共享50..100，q1共享150900..150963，第二QUERY尾290900..290963，结果/清理/Finish共享349001..349064。旧四图、split及Boston/brc原H34必要界排除保持，不删WAIT或放宽参数救资格。

本机入口implementation_binding_evidence/query_value_runtime_admission_20261009_r54/，含REPORT、MENTOR_DECISION、NEXT_METHOD、RUN_CHECKLIST、TRACKS及verify_delivery；三探索树research_update_20261009_r54/REPORT.md同步。五组件及联合只读核验PASS：892项去重pin，manifest fa53d0b3a4b4a1626d938266571bf84e167777867decb7e3d34d9cf51e29871a。四稿、旧冻结、输入、96234字节历史尾文及本轮前236100字节进度正文保护。

R54冻结后占用16,056,320B≈15.31MiB，无旧证据删除。此前10月9日净释放8,645,427,200B≈8.052GiB，10月8日约3.55GiB另计，不重复计入；约3.375GiB未合格旧候选保留，共享Git约3.73GiB不重复repack。[清理记录](../GITHUB_PROGRESS.md#storage-20261009)。

公共Git仅更新本文件与GITHUB_PROGRESS.md。年底成稿首投目标保持；无新缺陷依据不继续复制冻结或重复静态包装。旧9月21日交接仅历史，不重复已有完整查询闭环。
