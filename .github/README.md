# MAPF 项目当前状态

更新：2026-10-12，L15后导师判断。**继续有限验证，暂不训练：先完成待授权L15验收，随后以独立合法来源检验强规则外的净余量。** [导师判断与四阶段](../GITHUB_PROGRESS.md#mentor-after-l15) · [L15交付及清单](../GITHUB_PROGRESS.md#conflict-timing-l15) · [L14实际结果](../GITHUB_PROGRESS.md#full-search-l14) · [五线导航](../README.md#分支与工作区)。

研究问题保持有界跟踪误差、有限状态更新资源下的MAPF执行协调。学习辅助完整Improved GSES是优先条件候选，是否训练取决于强规则外的可辨净费用余量。

导师定点澄清：largest_diff有论文优先分支及作者完整配置依据，conflict是需补验的相关作者变体。现有首根一次干预标签只能支持同范围的首版学习；全程学习须另验证。L14三个组均单边、只有2–4次展开，不支持直接训练或泛化。下一四阶段是L15验收、来源准入与余量筛查、完整标签与轻量排序、有限执行与成稿；后续运行各按具体授权，不扩大本人工DEV。详细本机判断为implementation_binding_evidence/mentor_after_l15_20261012/DECISION.md。

## 本轮实际完成

- full-conflict全程调用作者已有conflict；root-conflict只首根调用，随后largest_diff。保留作者完整分组、双向、下界、环检查与OPEN，增强值不被排名分数替换。
- pidfd/selector等待退出事件，wait4统一回收CPU并记录完整wall；固定2ms主动轮询已从新内层实现移除，但尚未做运行验收或精度校准。
- 新收件区分同根同续策干预与完整策略比较，保留全部原context；四项策略元数据逐项核实，未知差异拒绝，不生成标签。
- 一次编译exit0、wall25.533秒，新ELF未执行。Python静态及源码审查通过，监督默认metadata核对122项源pin通过。

唯一待授权清单：同一L13 DEV，先4个非科学进程验收，再original/root_conflict/full_conflict三臂各一次。每科学臂solve6/host8秒，全部共享60＋5秒、4GiB/进程、16MiB监测、零重试；门槛不符停止并保留NOT_STARTED。旧一次性许可已消费，当前新fixture/solver/world/train/inference均0，不启动旧L7或扩大旧矩阵。

L14已有的2/3/4次展开机制事实保持，净加速与学习收益尚未成立。计时改造本身不证明加速，三臂一次DEV也不证明优于全部强规则。作者规则若已解释差异则结束本例；独立来源有余量才开展轻量排序与独立比较。完整报价/付费预算及实际执行效果仍UNKNOWN。

## 五线与Git入口

| 分支 | 当前角色 |
|---|---|
| main | 唯一当前总入口，方案、共同合同、实测判断与论文进度 |
| explore/error-aware-guidance | 活动执行线，有限空间适配、作者完整搜索与计量 |
| explore/query-value-feasibility | 活动证据/学习接口线，同根配对收件、合法特征和条件标签 |
| explore/learned-query | 历史归档，保留旧模型及正负结果，不重开 |
| explore/gaussian-mapf-feasibility | 限额备选，保留独有来源与合同，没有新运行 |

五条线不等于五个同时训练的模型。RL、持续任务、随机延迟和LIMO按既定条件后置。各支线.github/README.md与进度文件提供角色和main入口；其根README是受保护的L7快照，旧“下一步”按历史阅读。

本机implementation_binding_evidence/conflict_timing_l15_20261012/保存新实现、计量合同、审查及具体清单；L14实际结果保持原目录。实现和原始数据按现有范围留本机，Git导航不是源码/数据备份。317项保护来源、五稿与主稿未提交修改、原作者/输入/划分/参数/H34和全部失败保持；无大型复制或新工作树。
