# 工作树与模块导航

当前总体决定只有 [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)。2026-10-18起是两条研究线；main负责入口、必要公共组件和经核成果集成。旧三个探索分支属于底座交接，不计作研究选题。

| 分支/状态 | 本机工作树 | 当前职责 |
|---|---|---|
| main | `/home/lyh/MAPF_PIED_MDDR_RESEARCH` | 总入口、共享版本、已核成果 |
| research/sci-mapf | `/home/lyh/MAPF_SCI_RESEARCH` | `tracks/sci/`：局部路径修复方法与后续学习候选 |
| research/thesis-integration | `/home/lyh/MAPF_THESIS_RESEARCH` | `tracks/thesis/`：论文集成、执行误差与系统验证 |
| explore/error-aware-guidance，交接 | `/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE` | `exploration/spatial_constraints_s1_20261016/`：连续约束与完整执行DEV |
| explore/gaussian-mapf-feasibility，交接 | `/home/lyh/MAPF_GAUSSIAN_FEASIBILITY` | `exploration/spatial_source/`：v2来源与传播 |
| explore/query-value-feasibility，交接 | `/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY` | `exploration/execution_feedback/`：反馈和费用 |
| archive/learned-query-20261016，detached | `/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE` | 停止的查询学习与失败证据，HEAD `57aee7b` |

两研究树的总体README/计划/进度/导航已改为main与本线入口的简短索引；创建时快照保留在历史提交中。唯一当前总体决定始终读取main的`docs/RESEARCH_PLAN.md`。SCI最新[种子对照证据](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/fde3409c17b9de68691f9233161cc2dcca03dbef/tracks/sci/ADDRESS_SEED_RESULT.md)对应科学代码`93af30f`；硕士运动证据为`4fc3a54`（科学代码`a4ad94c`、旧SCI锁`535ee1a`）。历史阶段计时`d51fff2`、失败记录`7e77e9a`和共同预算`97d88a2`继续冻结。main用固定提交索引，不复制算法；全部消费/关闭许可不得复用。

当前SCI实现入口 [34a80e3](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/34a80e37034ef47608d609195070e6d4b34a23e9/tracks/sci/README.md)：共同预算执行合同与真实执行观测已完成软件核验，说明在`ADDRESS_BUDGET.md`，构建收据`shared_budget_build_receipt.json`；没有新科学运行。旧[f9c651a门控结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/f9c651ad0680679cf99a4973f722b65fd6f7aa97/tracks/sci/ADDRESS_VALIDATION_RESULT.md)及`results/address_candidate_validation_v1/`保持原字节：科学代码`2bd1916`、4项许可消费，校验费用下降但质量退化/持平，邻域参数表述偏差保留。默认legacy/all不变，不扩大旧门控性能候选。

硕士当前实现入口 [34d0cac](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/34d0cacc835d50c4b77254df6e18240ccf9de895/tracks/thesis/README.md)：运动目标接纳器在既有`plan_selection.py`与`compare_nominal_motion.py`，边界见`MOTION_ACCEPTANCE.md`，软件收据`derived/motion_acceptance_software.json`。新锁固定SCI`f9c651a`的10个候选输入/结果对象，校验器/预算/监督器仍固定`535ee1a`；不复制优化器、不追随HEAD。新32车输入尚未进行运动比较，manifest只作接口提案。旧[906ba90调度结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/906ba90aa7274f4035cf56d1b2cc323a642b1516/tracks/thesis/SCHEDULER_RESULT.md)及`results/scheduler_motion_v1/`不变，科学代码`76a6a99`、12臂许可消费。旧R16误差两项仍未运行，须使用冻结`5d85f62`和原清单。v2来源`43806cf`、输入适配`81f5866`、读取器`4a89183`不变。

SCI六份16/32车诊断已获本批新授权并全部完成：[PROFILE_RESULT.md](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/535ee1adf3135ab79565e0b3aa5d189348fe7ab2/tracks/sci/PROFILE_RESULT.md)。配置在`tracks/sci/config/repair_residual_v1_*`，冻结结果在`tracks/sci/results/repair_residual_v1/`；`PROFILE_CHECKLIST.md`许可已消费。`repair_profile.py`增加仅解析已有记录的费用拆分，不替换原运行代码或旧消费记录。

SCI[65a968c](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/65a968c7138cfdc6097a81178362c6e03f2dfbd3/tracks/sci/README.md)保存两批完整ADDRESS功能结果：原批2成功、1失败、3未运行，科学代码`032bf22`、产物`results/address_common_initial_v1/`；根界修补批1成功、1失败、2未运行，科学代码`eb4a60f`、产物`results/address_loop_guard_v1/`。两批均零重试、许可关闭，原证据未回填。`ADDRESS_GUARD_RESULT.md`记录当时退出缺口与其后的共同预算修补；恢复原型只编译/help与软件检查，运行器尚拒绝该变体。

SCI[97d88a2结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/97d88a2e49a5a77078f56d6447e632fd5692d401/tracks/sci/ADDRESS_BUDGET_RESULT.md)保存科学代码`101f18c`的三项共同预算功能验收，全部COMPLETE、零重试、许可已消费。产物位于`tracks/sci/results/address_budget_guard_v1/`，包含实际授权、逐项输出和总收据，不覆盖旧批。`ADDRESS_BUDGET_CHECKLIST.md`现标记已消费，JSON保持原SHA。

SCI[7e77e9a结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/7e77e9a4310928a7a273d4dac458d5536e7450d4/tracks/sci/ADDRESS_TRACE_RESULT.md)保存两项逐次失败记录DEV，科学代码`b0fa19e`，全部COMPLETE、零重试、许可消费。产物在`tracks/sci/results/address_attempt_trace_v1/`，总收据SHA `308e5a65…a8632`，独立审计在原收据后附加。17次成本停止及2次前半段空返回不满足原后段门槛，停止当前材料上的候选。原`.address_attempt_trace_build/`、`.address_recovery_budget_build/`及构建收据未改；恢复变体未执行科学任务。

SCI[d51fff2阶段计时结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/d51fff2855686c1dffb5fe84fc9de8fa3b205e88/tracks/sci/ADDRESS_PHASE_RESULT.md)保存两项授权DEV及独立复核，科学代码`f6e1d01`。产物`tracks/sci/results/address_phase_profile_v1/`包含真实授权、逐项完整输出、总收据和附加离线审计；全部COMPLETE、零重试、许可消费。`ADDRESS_PHASE_CHECKLIST.md`标记已消费，JSON SHA `0d4e0827…442ab7`、`.address_phase_profile_build/`及构建收据原字节保留。此批是后续种子规则的诊断依据，不作为新比较的配对计时；后段恢复停止不变。

SCI[正延迟种子八项结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/fde3409c17b9de68691f9233161cc2dcca03dbef/tracks/sci/ADDRESS_SEED_RESULT.md)对应`tracks/sci/results/address_seed_fixed_v1/`和`address_seed_time_v1/`，分别保存固定修复次数与固定总预算四项。科学代码`93af30f`、同一二进制与作者低层；零延迟车仍可进邻域。两份原manifest、产物与附加独立审计原样保留，全部COMPLETE、零重试、许可消费。新36项奖励比较已执行并独立核验，全部许可消费；详见顶部当前结果入口。

硕士[4fc3a54结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/4fc3a549afeac751fb54deac0056efee4b88a657/tracks/thesis/MOTION_RESULT.md)保存六任务三臂完整运动比较，18臂全部完成，产物在`tracks/thesis/results/nominal_motion_v1/`；`MOTION_RUN_CHECKLIST.md`已标记消费，原JSON SHA和8项科学代码/锁不变。`sci.lock.json`仍消费SCI`535ee1a`的14个证据，validator与supervisor也固定同版Git对象；来源文档固定`16b1ee0`。新汇总只解析保存动作和收据。0.5m六任务均超v2必要域；新同参数接口先使用合格但相关的R16完整投影，独立合格任务仍待准备。不互读最新树，不自动消费新的ADDRESS结果。

日常先读[总入口](README.md)、[进度](GITHUB_PROGRESS.md)、相应支线README。代码在研究分支的专用目录推进，main只集成核定成果。不能把相邻工作树的最新文件当共享依赖；详见[共享清单](shared/README.md)。

## 固定依赖和原位证据

- 12份旧运行代码分别固定执行`81f5866`、来源`43806cf`、工具`5589a7b`；新的文档交接提交不会静默改变代码pin。
- SCI的ADDRESS原版依赖固定`b3d35c431ce03834f95e834d87986f2f341394a1`；作者缓存`/home/lyh/.cache/mapf_research/address-b3d35c4`保持原样，本线提交保存许可、源文件摘要和编译收据，二进制不入库。它是SCI专用依赖，尚未提升为两线公共API。
- 完整ADDRESS原版编译工件见SCI固定[57c3d69](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/57c3d6999e27e50e05164af0686ab6f461dfe1bf/tracks/sci/full_address_build_receipt.json)：`build_address_full.py`树外编译并只查询help，本机`.full_address_build/build/address`。尚未科学运行，也不是六任务清单锁定的SIPP桥接程序；不得替换清单二进制。
- 完整ADDRESS适配版收据见SCI[032bf22](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/adapter_build_receipt.json)，本机`.address_adapter_build/build/address`，已用于原停批功能DEV。`.address_loop_guard_build/`用于根界修补功能DEV；`.address_recovery_build/`仍只编译/help。`.address_budget_guard_build/`是共同预算基线的小型独立overlay，已完成三项授权功能DEV。各收据/二进制分别保留，作者缓存和旧产物不覆盖。
- 实际四次DEV固定于执行证据提交`ae058c5`：[完整报告](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/ae058c5025eaaa61a424ef7627515d40c2e83997/exploration/spatial_constraints_s1_20261016/PREEXECUTION_DEV_RESULT.md)。原路径、收据SHA和消费标记不迁移、不重写。
- 原v2 `composition.py`、C1夹具与失败证据保持原路径。旧运行器仍有绝对路径/`__file__`依赖；只有完成小文件固定bundle适配和新清单后才能脱离旧树运行。
- `MANUSCRIPT_PREEXPERIMENT.md`仅main现有未提交版受保护，不复制到两线作为新稿。
- 现行综述：[本机文献目录](/home/lyh/桌面/MAPF_开题文献综述_20260921/MAPF误差综述_20261011)，仅索引，不复制文库。
- 师兄论文：[现存PDF](/home/lyh/.var/app/com.tencent.WeChat/xwechat_files/wxid_byi6dg2u66wi22_3837/msg/file/2026-06/M202110551-硕士论文.pdf)，用于组织参考，非学校规定。原`文档/.../business/favorite/temp/`入口已失效；现存文件核对题名、林威及81页，SHA256 `e57e11dc85d902f74901d53eca13685f635d68d4a0adb84c95abcf7ece6a4f5a`，未复制PDF。

## 交接顺序

1. 已保存领先提交、原DEV文件及真实结果；旧分支入口改为交接状态。
2. 建立两研究工作树，逐项登记所需依赖及消费者；新产物进入对应`tracks/<line>/results/<run_id>/`，run_id由已授权清单确定，不每轮另建日期框架。
3. 迁移非冻结代码前查调用、SHA、路径及其他窗口；共享实现只维护一份。SCI成熟成果由大论文引用固定SCI提交，只有确需公共API才提升到main/shared。
4. 旧底座无活动调用、独有提交已推送且原位证据约束解决之后，才考虑退出工作树。**本轮未删除、改名或整体合并旧树。**

[归档入口](archive/README.md)保留旧清理标签、L20/L21及各负结果；[旧完整导航](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/c9985fb/REPOSITORY_NAVIGATION.md)仅供历史恢复。
