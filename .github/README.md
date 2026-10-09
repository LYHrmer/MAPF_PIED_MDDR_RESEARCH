# MAPF 项目当前状态

更新：2026-10-09，当前入口 **R49**。已实现有限执行脚本、同初态安全grant→真实cap/RUN、候选记录与轻量学习准入接口，并完成5个最终静态对象和host组合链接。**查询价值学习仍部分完成：可靠标签、训练、独立比较均为0，完整generic Session及完整费用尚未闭合。**

研究问题保持MAPF、有界空间跟踪误差和有限更新资源；方法主线为代价感知进度查询与安全协调。价值回归/排序优先，RL重点候选；普通END、WAIT、结构规则和EWMA保留。只有独立对照证实任务或完整资源改善，才最小融合入论文。

[仓库导航](../README.md) · [完整进度](../GITHUB_PROGRESS.md) · [R49](../GITHUB_PROGRESS.md#r49) · [R48实际固定镜像](../GITHUB_PROGRESS.md#r48) · [R47物理边界](../GITHUB_PROGRESS.md#r47)

## 本轮实际成果

| 线路 | 本轮完成 | 仍缺 |
|---|---|---|
| 共同安全与执行 | 同GuestInitialPosition的完整资源grant；真实发布后才cap/RUN；每tick两机会的0/1/2提交与Skip接入实际Coordinator/Station/driver | 真实路径/Batch、完整C/N/E Session、原子地址与startup/Finish全程绑定 |
| 有限协议 | 显式新模式修复底层旧8位检查；启动必须消费真实付费StartupReady；各阶段核实际脚本索引 | 完整查询续策与总供给；不能把库对象当运行资格 |
| 价值学习 | 60word/48字段读取与来源审计，20字段×6状态通道，复用ridge数值核；真实来源/标签gate先于NumPy | 当前仅固定DEV、无真实QUERY身份和独立TRAIN，fit入口不可达；无权重/预测 |
| 费用 | 同R48 Center源码/ELF分析：每候选量化外层至多1176比较，成功出口至多4097word写入，局部已知祖先帧有界 | 精确数值复杂度、全栈/heap/整窗、跨行合法预算与完整报价UNKNOWN |

两个模块的实际host对象通过relocatable链接，私有bind/published符号已解析；这不是完整可运行ELF。当前最终guest/host依赖分别为275/423；finite另两个guest279/278、一个host451依赖。首次RUN可能tick1或更晚，END/交接/服务/Grant共享两个机会；启动排队与保守full-cap规则可能影响完成，不能许诺H34可行。

R48固定DEV已有真实Center/host镜像与候选出口，本轮复用，不重建；generic组件尚未装入完整查询程序。R48上层Station修复仍漏底层Boundary限制，R49已定点关闭并保留旧冻结原文。静态成本核验曾因导入产生新缓存触发成员保护，记录并清理后用`python3 -B`通过；冻结源码/报告未改。

四组件及联合冻结通过，**980项去重pin**，manifest `532ea43fe2d97f96f68d7d08f3dc9fe68e5036f097280f8339b9d74230e87533`。四稿、旧registry及96234字节历史尾文保持。20线**7直接/6共享/4沿用/3后置**，三探索树已同步`research_update_20261009_r49/REPORT.md`。科研导师仍2PASS/4UNKNOWN、CONDITIONAL；静态编译不能证明研究有效。

本机入口：`implementation_binding_evidence/query_value_generic_execution_20261009_r49/`，含REPORT、MENTOR_DECISION、TRACKS、NEXT_METHOD、RUN_CHECKLIST和只读verify_delivery；四组件是motion_grant、finite_script、execution_bounds、learning_intake。

## 下一步与原委派状态

主线仍有四个重叠验收阶段：共同执行/费用资格；真实查询机会及合法标签/方法冻结；获授权独立比较；证据融合成稿。当前第一阶段未整体完成。下一步直接补**同一Registration的完整C/N/E Session生产调用点**、真实QUERY身份回执和原任务末段service结果，统一定义编译链接，再核有限费用窗口；不继续堆孤立接口或网络。

原委派的独立工作树`/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY`及`explore/query-value-feasibility`分支已建，底座`explore/learned-query`提交`3c809f903e42ce33d287ca7f21e38924bd6dcffc`。旧10543记录/24组与R20只作开发诊断；尚无独立成对标签或正式比较，未作为研究有效的方法融入主线。QUERY/WAIT保持同合法初态、同续策规则、配对外生扰动、臂内合法信息；不复制查询结果给WAIT，不给未查询候选套同一标签，失败/负/零/迟到/未完成保留。

固定续策DeltaJ不是Q*；RL仍需多gate转移、预算演化、推理收费和完整episode。当前固定R19四service审计指标不等于通用原任务指标。任务与完整费用分列，未知不记零，训练另计；MSE不证明研究收益。Boston/brc仍被原H34物理必要界排除，Berlin/den只是未被排除；不改输入/split救学习。A保持、B NO-GO，持续任务、随机延迟和LIMO后置。

## 磁盘整理与保护

本轮逐项核验后删除**214个可再生pyc，毛回收2,887,680B≈2.754MiB**；两项冻结引用缓存及1980项依赖环境缓存保留。原始输入、归档、四稿、工具链与构建证据未删。清理前四树快照约102.59GiB，主要是研究证据和工具链；没有新增GiB级删除资格。逐项清单、失败预检与删除回执在本轮`storage_audit/`，其REPORT/INVENTORY是删除前快照，实际结果见AFTER_CLEANUP与DELETION_RESULT。

此前10月9日三批已归档清理1296个冗余副本，历史净释放8,645,427,200B≈8.052GiB；10月8日约3.55GiB另计。本轮pyc毛回收不与上述历史净值直接合计，不用df差额冒充收益。恢复工具和原归档保留：[大批清理](../GITHUB_PROGRESS.md#storage-20261009)、[补充清理](../GITHUB_PROGRESS.md#storage-followup-20261009)、[单包清理](../GITHUB_PROGRESS.md#storage-final-20261009)、[R45复核](../GITHUB_PROGRESS.md#storage-status-20261009-r45)。旧审计需要展开日志时先按各批次恢复工具恢复。

约3.375GiB旧候选池仍缺逐项当前引用/恢复核验，保留；共享Git约3.73GiB不重复repack。R49冻结后目录占用15,695,872B≈14.97MiB，主要为必要静态对象与记录；原R48完整镜像及N/E复用。研发新增占用与清理回收分别报告。

## 运行边界

现行授权仍仅实现、静态检查、冻结和清单。训练、solver、仿真、World/目标执行、模型/codec及机器人没有新增授权。R49 generic尚无可批准的完整argv，状态**NOT_AUTHORIZED / NOT_QUALIFIED / NOT_SCHEDULED**，不以等待授权替代剩余实现。

R48固定DEV旧提案仍未执行：1共享prefix+QUERY/WAIT、ABSENT、无重试，各尾270秒，外层870+30秒尽力截止；不覆盖R49通用实现或TRAIN。原H34/136、每tick2机会、单行8388608 B1、64准备行、总8192行保持；旧R46/R37/S3/六槽/Berlin授权不互借。运行申请须绑定实际输入/二进制/argv、预算、截止与失败保留，不能把实现冻结当成授权。

毕业目标沿用2026-10-07确认：学校无严格SCI分区/名单限制，期刊须有合理质量，争取2026年底成稿首投。先验证同预算改善固定批次完成，或相近完成下省完整资源；持续任务接口未通不称吞吐。旧9月21日交接仅作历史，不重复已有查询闭环。公共Git只同步本文件与GITHUB_PROGRESS，主稿未提交修改受保护。
