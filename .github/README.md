# MAPF 项目当前状态

更新：2026-10-09，当前科研入口 **R43**。根与3个子智能体完成同一镜像的付费模型接收/计算通路、真实 Session 析构、生命周期费用生产及不可变训练产物接口。**实现已构建并冻结；模型缺失，训练、推理、科学运行和可靠配对标签均为0，研究有效性 UNKNOWN。**

研究问题保持MAPF、有界空间跟踪误差和有限更新资源，方法主线为代价感知进度查询与安全协调。监督查询价值/排序首优先，RL为并列重点候选；安全释放仍由原有效证据决定。普通END、WAIT、结构规则与EWMA保留，论文纳入由独立任务/完整资源比较决定。

[仓库导航](../README.md) · [完整进度](../GITHUB_PROGRESS.md) · [R43](../GITHUB_PROGRESS.md#r43) · [R42](../GITHUB_PROGRESS.md#r42) · [R41](../GITHUB_PROGRESS.md#r41) · [上一版入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/959088c35f588c8870a0e53d5ef7e223586eac05/.github/README.md)

## R43 实际交付

| 交付 | 实际完成 | 仍缺 |
|---|---|---|
| 付费模型通路 | 固定注册→原SOURCE90权限/付费→十维合法输入→376B ridge参数/soft-double核→原检查点独立advice；真实Center/host已链接 | 默认ABSENT，没有权重或模型调用；advice尚不控制原forced QUERY/WAIT，数值兼容与完整窗口未知 |
| 学习数据接口 | fit-time不可变产物，拒绝旧可变artifact；native reader只读prefix；调用前准入与事后实际费用分开 | 旧R42 gate固定DEV且无条件阻断，真正独立TRAIN生产端仍缺；可靠标签0，不能只加模型文件 |
| 真实收尾与生命周期 | 尾结果先持久保存，再实际销毁Session；保留析构abort/未回收/未启动WAIT；外层subreaper/wait4生产已实现 | 动态行为未验证；不将host析构当guest付费清理；全进程完整费用仍UNKNOWN |
| 费用范围 | 同行付费前后快照差、生命周期CPU/wall分别采集；共享前缀与已回收后代CPU不重复加总 | 区间B1、RSS、输出字节都不能代替完整费用；跨行预算与完整未来报价仍缺 |
| 同一执行镜像 | 3 guest+2 host TU实际构建，782去重编译依赖；publication全图、私有kernel及寄存器实码通过 | 普通全栈/heap/全部有限窗口尚缺；局部栈界不升级整镜像资格 |
| 强化学习 | 十九维有限时域线性FQI继续重点，共享费用阶段和生命周期合同 | 不借十维输入资格；多机会episode、训练和独立效果均未形成 |

host两TU共532依赖、24个实际链接输入，Center SHA `7250574d…`、host `07320ec2…`；N/E复用R41。三组件只读冻结核验及交叉复核通过，联合冻结983项新交付/实际来源pin，manifest `6f8280a6…`。旧R42与磁盘冻结仅核registry hash，未把整套旧6520项重审或复制。四稿及历史尾文保持。

本机入口：`implementation_binding_evidence/query_value_paid_inference_20261009_r43/`，含`REPORT.md`、`MENTOR_DECISION.md`、`TRACKS.json`、`RUN_CHECKLIST.md`、`RUN_PLAN.json`、只读`verify_delivery.py`。三个探索树同步`research_update_20261009_r43/REPORT.md`。实现与证据留本机，公共Git只同步两份指定进度。

## 原查询价值委派：部分完成

独立工作树`/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY`、分支`explore/query-value-feasibility`已建立，基于`explore/learned-query`提交`3c809f903e42ce33d287ca7f21e38924bd6dcffc`。旧10,543记录/24组仍只诊断，R20仍DEV；不能从单轨迹造反事实收益。

真实采集器、公开输入、价值回归/排序、付费原生模型通路与RL候选已有探索实现。**合格实际公共输入0、完整成对尾0、可靠因果标签0、拟合/策略调用0。** 同域强规则、外部发表方法和独立新TEST未完成，未融入主线。静态接线或MSE不能证明研究有效，任务效益与完整费用逐单位记录。

## 下一必要工作与全部线路

先定点关闭同一新镜像剩余普通全栈/heap/有限窗口及完整费用生产，再补独立TRAIN/CAL/TEST来源与完整配对语义；现有注册、付费模型接收、真实Session析构和生命周期实现不重复建设。获授权后才采集合法两尾、训练及独立比较。原预算/报价缺口不能用行余量、历史子family或旧BUY阈值顶替。

20条是共享工作线，不是20个算法课题。主线仍4个重叠阶段：共同资格→方法/数据冻结→获授权独立小比较→融合成稿；各支线3或4阶段，不能相加或按文件数递减。导师仍2PASS/4UNKNOWN、CONDITIONAL。条件时长/位置、SADG/GSES共享接口；A保持R39停止观察，B仍NO-GO，持续任务/随机延迟/两台LIMO后置。仅在同预算改善完成，或事前固定相近完成下降低完整资源，才支持论文融合。

## 磁盘整理与运行边界

最新三路只读复核：既有两轮归档清理净回收合计约7.984GiB，10月8日约3.55GiB另计；本次没有新增删除。四树约102.435GiB，磁盘可用约110.41GiB（占用快照）。Git为四树共用一份对象库，不重复repack。新发现R18单包39个输出候选69.656MiB，已核归档成员和副本，但本批引用/恢复索引未齐，暂不删除；其余3.375GiB仅未资格候选池。详见[并行复核](../GITHUB_PROGRESS.md#storage-parallel-20261009)及本机`storage_maintenance_20261009_parallel_review/REPORT.md`。

2026-10-09补充清理：根与3个子智能体核验R18的一个归档，新增删除39个冗余输出副本（20个after、19个stdout），回收69.816MiB；80个归档成员核对、2次实际原路径恢复通过。同包41个输入/回执等文件与四稿保留。旧R18审计须先恢复相关输出。恢复工具及记录位于`implementation_binding_evidence/storage_maintenance_20261009_followup/`；[补充维护详情](../GITHUB_PROGRESS.md#storage-followup-20261009)。这部分新增回收不计入此前7.92GiB。

此前根与3个子智能体完成可恢复清理：R8/R10/R12/R13共1,218个已验证归档的展开JSONL副本，回收文件占用7.93GiB，扣审计索引后净约7.92GiB；四树由110.28降至约102.36GiB。原28个归档、输入/回执、108个被后继引用的日志、源码/工具链/构建工件、四稿和工作树保留。此前约3.55GiB另计，不重复算入本次。

四批次实际恢复核验4/4通过，6,104项R40/QV7冻结、306项历史冻结文件、2,657份输入/回执/stderr及108个保留日志均一致。历史审计需要先恢复相应展开日志。本机记录与恢复工具在`implementation_binding_evidence/storage_maintenance_20261009/`；[本次维护详情](../GITHUB_PROGRESS.md#storage-20261009)。除本次单包39项外，误差引导R18其余约20GiB展开证据尚未完成当前内容/引用迁移核验，继续保留；未删除任何工作树或历史，不重复压缩Git。

磁盘维护目录的 `RESEARCH_RESUME.md` 保留清理时快照；其未完成构建已由 R41/R42 接续，旧记录不改写。R42 新增文件占用快照约 71.5MiB，主要是必要的新 Center 与构建证据，N/E 直接复用；未恢复被清理日志，不重复计算净清理收益。

R40当时复核旧R39的5,779项pin全部一致：外部科研导师skill已恢复旧pin字节，之前维护的漂移记录保留；本轮没有重复该全量检查。历史磁盘/主稿复核见R40 `STORAGE_PROTECTION.json`，原逐文件清理回执仍在 `storage_maintenance_20261008/`。

现行授权仍仅实现、静态检查、冻结和清单。R43新提案只含1个DEV共享prefix+QUERY/WAIT两尾，模型ABSENT，无重试；输入/镜像/输出、每臂270秒、拟外层870+30秒截止和失败保留已列明，**NOT_AUTHORIZED且NOT_QUALIFIED**，未建运行目录。旧R37一次300秒、S3原版60秒、旧六槽/Berlin不互借；训练、独立TEST、随机延迟/机器人未授权。

毕业目标沿用2026-10-07确认：学校无严格SCI分区/名单限制，希望期刊有合理质量，争取2026年底成稿首投，非录用保证。先验证同预算改善固定批次完成，或相近完成下省完整资源；持续任务接口未通不称吞吐。旧9月21日交接仅作历史，已有完整查询闭环不重复建设。
