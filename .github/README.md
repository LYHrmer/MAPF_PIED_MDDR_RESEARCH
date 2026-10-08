# MAPF 项目当前状态

更新：2026-10-09，科研冻结入口 R40/QV7；磁盘维护结果见下。根与3个子智能体并行完成同初态成对采集器、实际学习适配、轻量RL候选、费用SOURCE登记和执行局部界，再做交叉核验。**已有具体学习实现；可靠标签、拟合/推理和科学运行仍0，研究有效性UNKNOWN。**

研究问题保持MAPF、有界空间跟踪误差和有限更新资源，方法主线为代价感知进度查询与安全协调。监督查询价值/排序是首优先方法候选，RL并列重点；模型只建议WAIT/QUERY，安全释放仍由原有效证据决定。普通END、WAIT、结构规则、EWMA保留，是否纳入论文由独立任务/完整资源比较决定。

[仓库导航](../README.md) · [完整进度历史](../GITHUB_PROGRESS.md) · [R40/QV7](../GITHUB_PROGRESS.md#r40-qv7) · [上一版入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/38361a84b2feb04f3daa65609d12345ee08060a7/.github/README.md)

## R40/QV7 已冻结成果

| 交付 | 实际完成 | 仍缺 |
|---|---|---|
| 同初态成对采集 | 原R19共同q0后实际Session停驻并fork；同C/N/E镜像，臂内信息、普通END、原准备窗口；2个RV64 TU+1个host TU完整链接，756依赖，逐臂wait4/失败前缀 | WAIT N/E缺付费收尾，完整尾/原生语义/全栈/堆/窗口及完整费用UNKNOWN；不能生成因果标签 |
| 四任务学习链 | 真实Position付费输出4项公开计数→实际寄存器日志→严格前缀解析→原R18数值核四维价值回归/排序适配 | 合法进度/年龄/目标/预算/报价全合同未齐，无记录、拟合或模型 |
| 共同19维链 | 原R36真实公开生产2TU/REL、成对audit、ridge适配；共同8来源与TRAIN元数据修正 | 与四任务域不同，不互填或借资格；原生语义UNKNOWN |
| 强化学习 | 有限时域线性FQI探索实现，gamma1、同臂序列、真实终态J、费用逐轴、WAIT同价优先 | 无训练/推理；19维WAIT/多机会episode未齐；单个额外q1不能证明序列RL优势 |
| QV7费用来源 | 实际C/N/E journal、SOURCE90/91/92、两个真实next_selection登记及付费聚合/释放；4TU完整新镜像/host，709依赖 | 仅历史Selection/Query/RA的B1子family，非完整费用/未来报价；与成对镜像未融合，脚本表须重导 |
| 原R36执行 | 真实allocator334PC有限扫描公式、Retained对象大小与第二PIN前最多3份的生命周期子界 | 总live-block L、异常、G0/G1及完整栈/窗口未知；新镜像不继承 |

联合冻结6,104项文件/来源pin通过，四份主稿、旧冻结和96,234字节历史尾文保持。成对Center SHA `d241825a…`，host `dede8371…`；发布图在新地址复核，私有kernel字节一致，普通全栈/窗口不因此PASS。

本机主入口：`implementation_binding_evidence/query_value_completion_20261008_r40/` 的 `REPORT.md`、`TRACKS.json`、`RUN_CHECKLIST.md`、`RUN_PLAN.json`、`verify_delivery.py`。查询价值树：`exploration/learned_query/source_registration_20261008_qv7/REPORT.md`。另外两探索树有 `research_update_20261009_r40/REPORT.md`。实现与工件留本机，公开Git仅同步两份指定进度文件，不宣称已含完整复现材料。

## 原查询价值委派：仍为部分完成

独立工作树 `/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY`、分支 `explore/query-value-feasibility` 已建立，基于 `explore/learned-query` 提交 `3c809f903e42ce33d287ca7f21e38924bd6dcffc`。旧10,543记录/24组仅诊断，保留失败和迟到；R20仍DEV。

现在已实现真实采集器、公开输入出口、价值回归/排序适配及一个RL候选，原“新价值模型尚未适配”的状态已推进。**合格实际公共输入0、完整成对尾0、可靠因果标签0、拟合/策略调用0。** 同域强规则、外部发表方法和独立新TEST未完成，未融入主线。静态接线或MSE不能证明研究有效，任务效益与各单位费用分别记录。

## 下一必要工作与全部线路

下一优先：完成R41费用闭段修订的host构建与依赖回执，再对同镜像WAIT付费收尾、费用family和公开特征做联合验收。R41已有三套guest和第一版host；静态检查发现首版账本错误地要求复制的Job与登记对象指针相同，修订header已保留，尚不能当作合格运行候选。旧R40冻结及`WAIT_PAID_CLEANUP_NEXT.md`保留，接续细节见磁盘维护目录`RESEARCH_RESUME.md`。

修订后定点补普通全栈/堆/窗口、完整费用与原生语义；分项条件界和静态接线不升级为完整资格，预算不能用逐行unused替代。监督价值与RL保持并行优先，数据、安全和费用资格一致。实际可靠成对标签、训练与独立比较仍未完成。

20条是共享工作线，不是20个课题；TRACKS区分本轮直接推进、共享接口受益和后置。主线仍4个重叠阶段：共同资格→方法/数据冻结→获授权独立小比较→融合成稿。查询/执行等各3，价值/RL/A各4，不能相加或按文件数递减。导师判定主线/学习仍2PASS/4UNKNOWN、CONDITIONAL。

条件时长/位置与SADG/GSES复用共同交付，保留原信息、安全/整数域和拒绝回退；A停止保留R39真实LNS观察，尚缺采集绑定/完整时钟/独立路径资格；B强工件/许可/fallback费用缺，仍NO-GO；C终生arrival/start/censor仍缺。随机延迟、两台LIMO后置。没有声称这些线本轮都新增了算法，DARI和旧C/LD/STOP矩阵不重开。

## 磁盘整理与运行边界

本轮根与3个子智能体完成可恢复清理：R8/R10/R12/R13共1,218个已验证归档的展开JSONL副本，回收文件占用7.93GiB，扣审计索引后净约7.92GiB；四树由110.28降至约102.36GiB。原28个归档、输入/回执、108个被后继引用的日志、源码/工具链/构建工件、四稿和工作树保留。此前约3.55GiB另计，不重复算入本次。

四批次实际恢复核验4/4通过，6,104项R40/QV7冻结、306项历史冻结文件、2,657份输入/回执/stderr及108个保留日志均一致。历史审计需要先恢复相应展开日志。本机记录与恢复工具在`implementation_binding_evidence/storage_maintenance_20261009/`；[本次维护详情](../GITHUB_PROGRESS.md#storage-20261009)。误差引导R18约20.27GiB展开证据尚未完成当前内容/引用迁移核验，继续保留；未删除任何工作树或历史，不重复压缩Git。

R41未完成研究产物全部保留：新增取消/费用融合已有静态实现，但首版host闭段指针检查存在阻断；修订header已写入，新host构建与联合验收尚未完成。具体接续见维护目录`RESEARCH_RESUME.md`，不能把本次清理写成R41资格通过。

旧R39的5,779项pin现全部一致：外部科研导师skill已恢复旧pin字节，本轮未改写skill，之前维护的漂移记录保留。磁盘/主稿复核见R40 `STORAGE_PROTECTION.json`，原逐文件清理回执仍在 `storage_maintenance_20261008/`。

现行授权仍仅实现、静态检查、冻结和清单。新提案只含1个DEV共享prefix+QUERY/WAIT两尾，无重试；输入/镜像/输出、每臂270秒、拟外层870+30秒截止和失败保留已列明，**NOT_AUTHORIZED且NOT_QUALIFIED**，未建运行目录。旧R37一次300秒、S3原版60秒、旧六槽/Berlin不互借；训练、独立TEST、随机延迟/机器人未授权。

毕业目标沿用2026-10-07确认：学校无严格SCI分区/名单限制，希望期刊有合理质量，争取2026年底成稿首投，非录用保证。先验证同预算改善固定批次完成，或相近完成下省完整资源；持续任务接口未通不称吞吐。旧9月21日交接仅作历史，已有完整查询闭环不重复建设。
