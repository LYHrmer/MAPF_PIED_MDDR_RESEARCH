# MAPF 项目当前状态

更新：2026-10-09，当前科研入口 **R44**。根与3个子智能体并行交付真实地图输入提案、host来源与加载费用生产端，以及当前执行镜像的局部栈/付费组件界。**实现已静态构建；通用地图到Session的适配仍缺，可靠标签、训练、模型和科学运行均为0，研究有效性 UNKNOWN。**

研究问题保持MAPF、有界空间跟踪误差和有限更新资源，方法主线为代价感知进度查询与安全协调。监督查询价值/排序首优先，RL为重点候选；安全释放仍由原有效证据决定。普通END、WAIT、结构规则与EWMA保留，论文纳入由独立任务/完整资源比较决定。

[仓库导航](../README.md) · [完整进度](../GITHUB_PROGRESS.md) · [R44](../GITHUB_PROGRESS.md#r44) · [R43](../GITHUB_PROGRESS.md#r43) · [上一版入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/df24fe5/.github/README.md)

## R44 实际交付

| 交付 | 实际完成 | 仍缺 |
|---|---|---|
| 输入来源 | 复用R29作者源，生成四地图、16起终点任务；TRAIN/CAL/TEST角色提前固定，核地图与端点 | 不是16个独立实验；Berlin不是未见TEST，仅R29声明范围查重；通用地图到实际Session的适配尚缺 |
| host来源 | 实际driver在Session前采集自身ELF字节SHA/PID，接入START、wait4和fork parent读取接口 | 尚无实际receipt；不能代替guest身份、共同合法初态或臂内信息隔离 |
| 学习接口 | 纯任务、独立TRAIN、完整费用、预算部署分别核查；fit-time不可变产物复用原ridge及47-word格式 | 唯一实际source factory仍为固定R19 DEV，当前不能训练；不能靠改family或补文件升级资格 |
| 加载费用 | 实际注册/模型读取分别采集返回字节、CPU/wall及失败；ABSENT的未读模型为null | 只是host读取分项，已包含在outer CPU；通信、完整I/O、完整报价/余额仍UNKNOWN |
| 同镜像执行 | 两次paid receiver与ABSENT组件上界3,392 B1；该调用点含活动祖先栈11,040B；两次计数的已知部分各2,709 B1 | 原子helper、整程序栈/heap/完整有限窗口及Present分支尚缺；小于一行不证明剩余窗口足够 |
| 强化学习及其他线路 | 20条共享线路与三个探索树同步，十九维有限时域FQI保持重点候选 | 不借十维资格；多机会episode、训练和独立效果未形成；A保持、B NO-GO、持续任务/延迟/LIMO后置 |

本轮两次host链接实际新编译3个TU、558去重输入；最终host两活动TU共557依赖、24链接输入，SHA `165ca0b3…`。三guest直接复用，不重建/复制大型ELF。三个组件默认只读核验及互审通过；联合冻结详情见[R44进度](../GITHUB_PROGRESS.md#r44)。四稿与历史尾文保持，旧冻结仅核registry hash。

本机入口：`implementation_binding_evidence/query_value_training_sources_20261009_r44/`，含`REPORT.md`、`MENTOR_DECISION.md`、`TRACKS.json`、`NEXT_METHOD.md`、`RUN_CHECKLIST.md`、最终`RUN_PLAN_ORIGIN.json`与只读`verify_delivery.py`。三个探索树同步`research_update_20261009_r44/REPORT.md`。实现和证据留本机，公共Git只同步两份指定进度。

## 原查询价值委派：部分完成

独立工作树`/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY`、分支`explore/query-value-feasibility`已建立，基于`explore/learned-query`提交`3c809f903e42ce33d287ca7f21e38924bd6dcffc`。旧10,543记录/24组仍只诊断，R20仍DEV；不能从单轨迹造反事实收益。

采集、合法特征、价值回归/排序、付费原生模型通路与RL候选已有探索实现。**合格实际公共输入0、完整成对尾0、可靠因果标签0、拟合/策略调用0。** 同域强规则、可合法复现的发表方法和独立新TEST未完成，未融入主线。任务因果标签与完整费用资格分开：未知费用不必否定其他前提成立的纯任务标签，但阻止完整资源收益与预算部署结论；当前连任务标签前提也未齐。

## 下一必要工作与全部线路

复用R18已有通用地图QUERY/WAIT成对完整续跑接缝，接入共同空间安全、精确共同初态、臂内来源与真实付费接口；旧点运动/次数预算/截尾标签不能直接成为主线证据。同步关闭同一原生镜像剩余原子调用、全栈/heap/有限窗口与完整费用。不重写规划器，不把所有独立数据固定在R19四任务，也不扩旧实验矩阵。新四地图尚未被原生采集器消费，不能写成“只差授权即可训练”。

20条是共享工作线，不是20个算法课题。主线仍4个重叠阶段：共同资格→方法/数据冻结→获授权独立小比较→融合成稿；各支线3或4阶段，不能相加或按文件数递减。导师仍2PASS/4UNKNOWN、CONDITIONAL。条件时长/位置、SADG/GSES共享接口；仅同预算改善完成，或事前固定相近完成下降低完整资源，才支持论文融合。

## 磁盘整理与运行边界

本次根与3个子智能体完成单包归档、Git/缓存及恢复工具的并行核查，实际新增清理R18 s04/package00014的39个冗余输出副本。释放69.656MiB，扣0.488MiB新增维护记录后净69.168MiB；80成员核验、2次原路径恢复验证通过，同包41个输入/回执和四稿保留。10月9日三轮归档整理净合计约8.052GiB，10月8日约3.55GiB另计。Git共用对象库不重复repack，约2.73MiB含冻结引用缓存保留；其余3.375GiB候选池未扩大删除。详见[本批结果](../GITHUB_PROGRESS.md#storage-final-20261009)与本机`storage_maintenance_20261009_final_review/CLEANUP_RESULT.md`；旧R18审计需先用对应批次工具恢复缺失输出。

2026-10-09补充清理：根与3个子智能体核验R18的一个归档，新增删除39个冗余输出副本（20个after、19个stdout），回收69.816MiB；80个归档成员核对、2次实际原路径恢复通过。同包41个输入/回执等文件与四稿保留。旧R18审计须先恢复相关输出。恢复工具及记录位于`implementation_binding_evidence/storage_maintenance_20261009_followup/`；[补充维护详情](../GITHUB_PROGRESS.md#storage-followup-20261009)。这部分新增回收不计入此前7.92GiB。

此前根与3个子智能体完成可恢复清理：R8/R10/R12/R13共1,218个已验证归档的展开JSONL副本，回收文件占用7.93GiB，扣审计索引后净约7.92GiB；四树由110.28降至约102.36GiB。原28个归档、输入/回执、108个被后继引用的日志、源码/工具链/构建工件、四稿和工作树保留。此前约3.55GiB另计，不重复算入本次。

四批次实际恢复核验4/4通过，6,104项R40/QV7冻结、306项历史冻结文件、2,657份输入/回执/stderr及108个保留日志均一致。历史审计需要先恢复相应展开日志。本机记录与恢复工具在`implementation_binding_evidence/storage_maintenance_20261009/`；[本次维护详情](../GITHUB_PROGRESS.md#storage-20261009)。除两批共78项输出外，误差引导R18其余约20GiB展开证据尚未完成当前内容/引用迁移核验，继续保留；未删除任何工作树或历史，不重复压缩Git。

磁盘维护目录的 `RESEARCH_RESUME.md` 保留清理时快照；其未完成构建已由 R41/R42 接续，旧记录不改写。R42 新增文件占用快照约 71.5MiB，主要是必要的新 Center 与构建证据，N/E 直接复用；未恢复被清理日志，不重复计算净清理收益。

R40当时复核旧R39的5,779项pin全部一致：外部科研导师skill已恢复旧pin字节，之前维护的漂移记录保留；本轮没有重复该全量检查。历史磁盘/主稿复核见R40 `STORAGE_PROTECTION.json`，原逐文件清理回执仍在 `storage_maintenance_20261008/`。

现行授权仍仅实现、静态检查、冻结和清单。R44最终RUN_PLAN_ORIGIN提案仅替代未执行旧提案：1个DEV共享prefix+QUERY/WAIT两尾，模型ABSENT，无重试；每臂270秒、拟外层870+30秒截止和失败保留已列明，**NOT_AUTHORIZED且NOT_QUALIFIED**，未建运行目录。四地图输入另属静态提案，尚未接入该固定原生采集器。旧R37一次300秒、S3原版60秒、旧六槽/Berlin不互借；训练、独立TEST、随机延迟/机器人未授权。

毕业目标沿用2026-10-07确认：学校无严格SCI分区/名单限制，希望期刊有合理质量，争取2026年底成稿首投，非录用保证。先验证同预算改善固定批次完成，或相近完成下省完整资源；持续任务接口未通不称吞吐。旧9月21日交接仅作历史，已有完整查询闭环不重复建设。
