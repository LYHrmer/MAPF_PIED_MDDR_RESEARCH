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

两研究树的公共文档是创建时快照；唯一当前总体决定始终读取main的`docs/RESEARCH_PLAN.md`。SCI运行代码`818f1e9`、六臂证据`c0bd134`、硕士实现`6771137`分别在本线维护，main用固定提交索引，不复制算法。SCI六臂见`tracks/sci/DEV_RESULT.md`；原`RUN_CHECKLIST.md`已消费，不能重跑。

SCI后继准备固定`32bbc38`：[PROFILE_CHECKLIST.md](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/32bbc38c732bdc7b1c0b172f9c7b2074275ff38d/tracks/sci/PROFILE_CHECKLIST.md)，六份既有16/32车完整任务与单一强策略诊断，尚未获新授权/运行。`repair_profile.py`负责准备和离线解析，复用原运行器；配置在`tracks/sci/config/repair_residual_v1_*`，新结果目录尚不存在。不替换旧消费记录或另起研究分支。

日常先读[总入口](README.md)、[进度](GITHUB_PROGRESS.md)、相应支线README。代码在研究分支的专用目录推进，main只集成核定成果。不能把相邻工作树的最新文件当共享依赖；详见[共享清单](shared/README.md)。

## 固定依赖和原位证据

- 12份旧运行代码分别固定执行`81f5866`、来源`43806cf`、工具`5589a7b`；新的文档交接提交不会静默改变代码pin。
- SCI的ADDRESS原版依赖固定`b3d35c431ce03834f95e834d87986f2f341394a1`；作者缓存`/home/lyh/.cache/mapf_research/address-b3d35c4`保持原样，本线提交保存许可、源文件摘要和编译收据，二进制不入库。它是SCI专用依赖，尚未提升为两线公共API。
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
