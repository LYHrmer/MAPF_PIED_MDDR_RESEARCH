# MAPF 项目当前状态

更新：2026-10-09，当前入口 **R50**。已补实际生命周期 Session、原任务结果读取/清理、真实查询身份钩子及同一协调器的查询主体。**查询价值学习仍部分完成：完整通用 C/N/E 执行尚未闭合，可靠标签、训练和独立比较均为0，研究有效性UNKNOWN。**

研究问题保持MAPF、有界空间跟踪误差和有限更新资源；方法主线为代价感知进度查询与安全协调。学习价值回归/排序优先、RL重点候选；普通END、WAIT、结构规则和EWMA保留。以同预算改善完成，或相近完成下降低完整资源的独立证据决定是否融入论文。

[仓库导航](../README.md) · [完整进度](../GITHUB_PROGRESS.md) · [R50](../GITHUB_PROGRESS.md#r50) · [R49](../GITHUB_PROGRESS.md#r49) · [R48固定镜像](../GITHUB_PROGRESS.md#r48) · [R47物理边界](../GITHUB_PROGRESS.md#r47)

## 本轮实际成果

| 组件 | 已完成 | 仍缺 |
|---|---|---|
| guest | 原启动入口进入同一Coordinator；原任务末段service结果；ResultReady、付费返回清理、Finish；显式完整seed生产接口 | 真实nominal/Batch/seed、实际factory和完整ELF |
| host | 同Registration的实际Owner/Station/运动及END来源；68计划入口；共享8192行准入；真实startup、结果读取和释放检查 | 同一新ELF的INIT/结果符号/全部原子计划；当前仅生命周期基线 |
| 查询身份 | 实际PreparedRequest绑定同root/time/唯一候选，三阶段回执；WAIT无selected；实际driver观察与严格准入 | 新完整镜像/BSS重绑定、可靠成对来源；仍fixed DEV、fit=false |
| 查询主体 | 一个Coordinator/Position/Bridge贯穿原Flow、普通END、公共GrantBook与WAIT；移除固定后车与旧预算常量 | 通用host查询交错脚本、实际E→host查询来源桥，尚未进入完整生产调用 |

根与3子智能体完成定点互审：**10个最终静态对象、3项relocatable组合、0个完整通用镜像**。四组件和联合只读核验通过，1260项去重pin；manifest `d3058ffbe2ef6336ed0f7a5d6a7e40c646c5fbb11481d2c834946af6377871a4`。四稿、旧registry及96234字节历史尾文保持。

结果从实际Coordinator导出，未完成保持-1，异常缺失不补零；host读取后须经实际付费返回释放，再核Finish。末段仍共用原64行。查询元数据使用原4096word中的32word，候选上限4064，超限拒绝。永久物理动作身份与单次query/request分别核验，原E仍检查全部SOURCE/AUTH字段；第二查询的实际host来源尚未完成。

全栈、heap、完整窗口、跨行合法预算、未来完整报价和host观察/I/O费用仍UNKNOWN。结果public_binding按一字节一Word存储会放大容量，须在真实输入/镜像上计入，不扩arena掩盖。静态对象与部分链接不证明运行、费用或研究有效性。

本机入口：`implementation_binding_evidence/query_value_session_integration_20261009_r50/`，含REPORT、MENTOR_DECISION、TRACKS、NEXT_METHOD、RUN_CHECKLIST和verify_delivery。20线按事实为**6直接/7共享/4沿用/3后置**；三探索树已同步`research_update_20261009_r50/REPORT.md`。共享接口推进不等于20项独立算法均有新实验。科研导师仍2PASS/4UNKNOWN、CONDITIONAL。

## 下一步与学习定位

主线仍四个重叠验收阶段：共同执行/费用资格；真实查询机会及合法标签/方法冻结；获授权独立小规模比较；证据融合成稿。当前第一阶段未整体完成。

下一步优先补**同一Registration的完整C/N/E调用链与有限查询脚本，以及实际请求驱动的E→host SOURCE生产端**；随后绑定真实输入、镜像、全部publication plans与完整费用。复用已有组件，不继续堆网络或孤立接口。R49 HostMotion仍匹配初始完整身份，单独放宽q0比较不能补齐q1；旧固定MovementPublished也不能承接新公共GrantBook。

价值回归/排序沿用轻量实现；真实来源gate先于NumPy，当前没有权重/预测。RL保持重点研究候选，需要实际多gate转移、预算变化、完整episode和推理费用；两14tick周期源码不是RL实验，固定续策ΔJ不是Q*，MSE改善不是任务收益。条件时长/位置、SADG/GSES共享共同资格；A规划停止保持，B可拒绝选择NO-GO不重开，终生引导、随机延迟和LIMO后置。

原委派工作树`/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY`与`explore/query-value-feasibility`分支已建，底座`explore/learned-query`提交`3c809f903e42ce33d287ca7f21e38924bd6dcffc`。旧10543记录/24组及R20仅开发诊断；尚无独立成对标签或确认比较，未作为研究有效的方法融入主线。

QUERY/WAIT须同合法初态、同续策规则、配对外生扰动，各臂仅读自身合法信息；不要求两臂动作相同，不泄露查询给WAIT，不给未查候选套用标签。失败、迟到、零/负收益及未完成保留；任务与完整费用分列，未知不记零，训练另计。只用原任务末段service衡量固定批次完成，中间handoff不算完成；持续任务接口未通不称吞吐。

Boston/brc仍被原H34物理必要界排除；Berlin/den只是未被排除。真实Batch若有尚不支持的WAIT应阻断，不删WAIT、不换成功实例、不改输入/split救学习。

## 磁盘整理与保护

R50冻结后目录占用52,281,344B≈49.86MiB，主要是必要静态对象、依赖和修订前像；旧完整镜像与工具链引用复用。本轮联合核验发现并精确清理本轮构建生成的过时pyc，8192分配字节，不计既有清理收益；失败检查、更正及删除回执保留，冻结文件未改。

R49已删除214个无引用可再生pyc，毛回收2,887,680B≈2.754MiB；两项冻结缓存和1980项依赖环境缓存保留。此前10月9日三批清理1296个副本，历史净释放8,645,427,200B≈8.052GiB；10月8日约3.55GiB另计，不重复合计。原始输入、归档、恢复工具、四稿和工具链保留：[大批清理](../GITHUB_PROGRESS.md#storage-20261009)、[补充清理](../GITHUB_PROGRESS.md#storage-followup-20261009)、[单包清理](../GITHUB_PROGRESS.md#storage-final-20261009)、[复核](../GITHUB_PROGRESS.md#storage-status-20261009-r45)。

约3.375GiB旧候选仍缺当前引用/恢复核验，未删；共享Git约3.73GiB不重复repack。R49清理前四树约102.59GiB是历史快照，不是当前精确总量；研发新增占用与回收分别记录。

## 运行边界

现行授权仅实现、静态检查、冻结和清单；训练、solver、仿真、World/科学目标（含--help）、模型/codec/feature执行与机器人均无新增授权。R50通用目标无完整可批准argv，**NOT_AUTHORIZED / NOT_QUALIFIED / NOT_SCHEDULED**。先完成缺失实现和静态绑定，再交具体输入/二进制/argv、预算、截止及失败保留清单。

R48旧固定DEV提案仍未执行：1共享prefix+QUERY/WAIT、ABSENT、无重试、各尾270秒、外层870+30秒；不覆盖R50通用目标、名义求解或TRAIN。原H34/136、每tick2机会、单行8388608 B1、64准备行、总8192行保持；旧R46/R37/S3/六槽/Berlin授权不互借。

毕业目标沿用2026-10-07确认：学校无严格SCI分区/名单限制，期刊须有合理质量，争取2026年底成稿首投。旧9月21日交接仅作历史，不重复已有查询闭环。公共Git只同步本文件与GITHUB_PROGRESS；主稿未提交修改受保护。
