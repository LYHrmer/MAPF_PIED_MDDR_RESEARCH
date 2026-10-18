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

两研究树的总体README/计划/进度/导航已改为main与本线入口的简短索引；创建时快照保留在历史提交中。唯一当前总体决定始终读取main的`docs/RESEARCH_PLAN.md`。SCI当前共同预算实现为`101f18c`、硕士完整任务比较接口为`a4ad94c`，main用固定提交索引，不复制算法。SCI原8车六臂见`c0bd134`的`tracks/sci/DEV_RESULT.md`；其`RUN_CHECKLIST.md`已消费，不能重跑。

SCI六份16/32车诊断已获本批新授权并全部完成：[PROFILE_RESULT.md](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/535ee1adf3135ab79565e0b3aa5d189348fe7ab2/tracks/sci/PROFILE_RESULT.md)。配置在`tracks/sci/config/repair_residual_v1_*`，冻结结果在`tracks/sci/results/repair_residual_v1/`；`PROFILE_CHECKLIST.md`许可已消费。`repair_profile.py`增加仅解析已有记录的费用拆分，不替换原运行代码或旧消费记录。

SCI[65a968c](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/65a968c7138cfdc6097a81178362c6e03f2dfbd3/tracks/sci/README.md)保存两批完整ADDRESS功能结果：原批2成功、1失败、3未运行，科学代码`032bf22`、产物`results/address_common_initial_v1/`；根界修补批1成功、1失败、2未运行，科学代码`eb4a60f`、产物`results/address_loop_guard_v1/`。两批均零重试、许可关闭，原证据未回填。`ADDRESS_GUARD_RESULT.md`记录本轮退出缺口与下一共同预算修补；恢复原型只编译/help与软件检查，运行器尚拒绝该变体。

SCI[101f18c](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/101f18c6d65ae3d8b1ba263bd95e0397df21eaf0/tracks/sci/ADDRESS_BUDGET.md)新增共用软截止、完整回滚及预处理初解回退，`ADDRESS_BUDGET_CHECKLIST.md`与`config/address_budget_guard_v1_manifest.json`准备三项功能验收，未执行。新科学产物计划进入`results/address_budget_guard_v1/`，目录尚不存在，不覆盖旧批。

硕士[a4ad94c](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/a4ad94c5c84dc9f2239bc9b77e00a36740f70d2f/tracks/thesis/README.md)新增`compare_nominal_motion.py`，三方案共用运动条件并保留完整成本；`MOTION_RUN_CHECKLIST.md`与`config/nominal_motion_v1_manifest.json`准备六项三臂比较，未执行。产物计划进入`results/nominal_motion_v1/`，目录尚不存在。`sci.lock.json`仍消费SCI`535ee1a`的14个证据，validator与supervisor也固定同版Git对象；来源文档固定`16b1ee0`。不互读最新树，不自动消费完整ADDRESS新结果，全部旧派生产物原字节保留。

日常先读[总入口](README.md)、[进度](GITHUB_PROGRESS.md)、相应支线README。代码在研究分支的专用目录推进，main只集成核定成果。不能把相邻工作树的最新文件当共享依赖；详见[共享清单](shared/README.md)。

## 固定依赖和原位证据

- 12份旧运行代码分别固定执行`81f5866`、来源`43806cf`、工具`5589a7b`；新的文档交接提交不会静默改变代码pin。
- SCI的ADDRESS原版依赖固定`b3d35c431ce03834f95e834d87986f2f341394a1`；作者缓存`/home/lyh/.cache/mapf_research/address-b3d35c4`保持原样，本线提交保存许可、源文件摘要和编译收据，二进制不入库。它是SCI专用依赖，尚未提升为两线公共API。
- 完整ADDRESS原版编译工件见SCI固定[57c3d69](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/57c3d6999e27e50e05164af0686ab6f461dfe1bf/tracks/sci/full_address_build_receipt.json)：`build_address_full.py`树外编译并只查询help，本机`.full_address_build/build/address`。尚未科学运行，也不是六任务清单锁定的SIPP桥接程序；不得替换清单二进制。
- 完整ADDRESS适配版收据见SCI[032bf22](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/adapter_build_receipt.json)，本机`.address_adapter_build/build/address`，已用于原停批功能DEV。`.address_loop_guard_build/`用于根界修补功能DEV；`.address_recovery_build/`仍只编译/help。新`.address_budget_guard_build/`是共同预算基线的小型独立overlay，完整编译/help成功但未科学运行。各收据/二进制分别保留，作者缓存和旧产物不覆盖。
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
