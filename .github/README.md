# MAPF 项目当前状态

更新：2026-10-09，当前科研入口 **R48**。根与3个子智能体把候选提取、48维编码和记录出口接入真实固定DEV执行程序，重编16个guest TU和2个host TU并实际链接；通用段guest协调器与host来源接缝另完成静态对象。**实现有新增，查询价值学习尚未完成：实际候选记录、可靠标签、训练和科学运行仍为0。**

研究问题保持MAPF、有界空间跟踪误差和有限更新资源，方法主线为代价感知进度查询与安全协调。价值回归/排序首优先，RL重点候选；安全释放仍依原有效证据，普通END、WAIT、结构规则与EWMA保留。研究有效性UNKNOWN，是否入论文由独立任务与完整资源比较决定。

[仓库导航](../README.md) · [完整进度](../GITHUB_PROGRESS.md) · [R48](../GITHUB_PROGRESS.md#r48) · [R47物理边界](../GITHUB_PROGRESS.md#r47) · [上一版入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/4969469/.github/README.md)

## R48实际成果与边界

| 组件 | 实际完成 | 仍缺 |
|---|---|---|
| 固定执行镜像 | 候选提取→编码→专用BSS→host单向记录进入真实C-next Selection；16 guest/2 host TU组合链接，N/E复用 | 没有运行记录；固定DEV不能当通用TRAIN；全栈/heap/整窗未资格 |
| 学习数据接口 | 同根CandidateSet产生48个有单位Q16字段、60word记录和独立缺失/越界掩码，实际RV64编译 | 旧10D/47word权重未绑定；决策预算/完整报价/训练标签UNKNOWN |
| 通用guest协调 | typed付费END→真实双SOURCE发布→resident/handoff/晚tick末段service，commit后推进cache/head；两个RV64对象 | 每tick只有2commit；0/1commit时跨有限脚本剩余机会未通；cap/RUN仍缺 |
| host有限来源 | 实际Station按自身已出版的新协议word推进私有head，固定136import按当前链生成真实付费SOURCE；实际host对象 | 未链接generic Session；查找/分配/检查/生命周期完整成本未定价 |

真实新Center SHA `71c2d854…`，host `e398b2d6…`。实际ELF核调用点、32768B BSS与保护区互斥、原publication与kernel；局部证据不升级整栈/整窗。新候选工厂新增26次SOURCE90 scalar调用，本局部ABSENT路径由27变53，次数不是费用。旧advice区间包住新增特征/编码/导出/回收，不能称纯模型推理成本。

互审修复旧8位role限制必然拒绝新64位word的问题；根进一步发现旧同guard头遮蔽新Station，强制定义次序并加编译断言后重编。早期对象/失败/源码前像保留，不能冒充新接缝证据。新通用模式未装入固定DEV镜像，不把两类对象当成同一完整运行。

四组件默认静态核验和联合冻结通过：1294项去重pin，manifest `d4702cc341117ddcd508f585e8b113a7e9daf5e56bdb9b12b6a8d9e908e09118`；四稿、旧registry及96234字节历史尾文保持。20线6直接/7共享/4沿用/3后置，三探索树同步`research_update_20261009_r48/REPORT.md`。

本机当前入口：`implementation_binding_evidence/query_value_execution_integration_20261009_r48/`，含REPORT、MENTOR_DECISION、TRACKS、NEXT_METHOD、RUN_CHECKLIST、verify_delivery。科研导师仍2PASS/4UNKNOWN、CONDITIONAL；没有模型/codec/World/solver/仿真/机器人执行。

## 下一步与原委派状态

原查询价值委派**部分完成**：独立工作树`/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY`、分支`explore/query-value-feasibility`已建立，基于`explore/learned-query`提交`3c809f903e42ce33d287ca7f21e38924bd6dcffc`；旧10543记录/24组与R20只开发诊断。现有实现覆盖候选、采集接口、价值/排序通路及RL候选，未得到独立成对标签或正式比较，也未以研究有效的方法融主线。

主线仍有四个重叠验收阶段：共同来源/安全/执行/费用资格；查询机会及合法标签/方法冻结；获授权独立比较；证据融合成稿。当前第一阶段尚未完成，不能按接口数量减少阶段。

下一只闭合具体缺口：有限脚本无提交/单提交时的调度、原安全grant→cap/RUN与初始HOLD启动、同一Registration和真实路径进入实际generic Session，随后核完整窗口与费用。复用本轮已完成的候选调用/编码，不重搭接口、不堆网络。

R47物理必要界仍成立：Boston/brc即使理想合并也超H34，Berlin/den仅未被排除；没有真实名义路径/WAIT消费者/可行性证明。输入、split和边界保持，不换图救学习。固定ΔJ^π0不等于Q*，RL还需真实多gate转移与预算演化；只有独立任务/完整资源改善才最小融合。A保持、B NO-GO，持续任务、随机延迟和LIMO继续后置。

## 磁盘整理与运行边界

已完成可恢复清理：10月9日三批合计删除1,296个经归档核验的冗余输出副本，净释放8,645,427,200B，约**8.052GiB**；10月8日约3.55GiB另计。最新单包39项净释放69.168MiB，80个归档成员核对及2次原路径恢复通过；三批删除集合无重复。原归档、输入/回执、后继引用日志、冻结工件、四稿与工作树保留。旧审计使用展开日志前，须按对应批次工具恢复。

| R45末空间快照（历史占用，硬链接与共享Git不重复计） | GiB |
|---|---:|
| 主研究树 | 68.183 |
| 误差引导树 | 25.903 |
| 学习探索树 | 7.290 |
| 查询价值可行性树 | 1.012 |
| 四树合计 | **102.387** |

R45冻结内容及三份报告新增约9.11MiB；当时整盘可用空间快照约110.54GiB。这些是R45末占用，不能当作累计清理收益。三批已确认可删清单均已处理；另约3.375GiB旧候选池缺当前内容/引用/恢复核验，继续保留。共享Git对象库约3.73GiB，不重复repack；约2.73MiB缓存含冻结引用，不泛删。其余R18展开证据、author_cache、构建工件和工具链也不按目录名称直接清除。

维护记录与恢复工具：`implementation_binding_evidence/storage_maintenance_20261009/`、`storage_maintenance_20261009_followup/`、`storage_maintenance_20261009_final_review/`。对应历史记录：[大批清理](../GITHUB_PROGRESS.md#storage-20261009) · [补充清理](../GITHUB_PROGRESS.md#storage-followup-20261009) · [最近单包清理](../GITHUB_PROGRESS.md#storage-final-20261009) · [本次只读复核](../GITHUB_PROGRESS.md#storage-status-20261009-r45)。冻结维护快照保留原文，旧R41未完构建已由后续记录接续，不改写历史。

R46目录冻结后占用快照93,069,312B，约88.76MiB，主要为必要的新Center、host和对象；本轮未再清理旧证据，未复制原N/E。以上旧四树占用不是当前重测，研发新增工件也不抵扣历史清理收益。

R47冻结目录占用快照7,962,624B，约7.594MiB，新增为静态对象和记录；本轮没有继续删除旧证据。

R48冻结后目录占用快照101,228,544B，约96.54MiB，包含必要的新Center/host、对象、失败与源码前像；原N/E复用，本轮未再删除旧证据。研发新增占用不重复计为清理收益或损失。

现行授权仍仅实现、静态检查、冻结和清单。R48具体固定DEV提案是1共享prefix＋QUERY/WAIT，ABSENT、无重试，各尾270秒，外层870＋30秒尽力截止，原H34/136/行容量/64行/8192行不变。新目标为R48 execution/host_build_final的实际镜像，旧监督计划尚未接纳该新目标；**NOT_AUTHORIZED、NOT_QUALIFIED、NOT_SCHEDULED**，输出未创建。它不含通用段对象、不作TRAIN。旧R46/R37/S3/六槽/Berlin授权不互借，训练/独立TEST/随机延迟/机器人未授权。

毕业目标沿用2026-10-07确认：学校无严格SCI分区/名单限制，希望期刊有合理质量，争取2026年底成稿首投，非录用保证。先验证同预算改善固定批次完成，或相近完成下省完整资源；持续任务接口未通不称吞吐。旧9月21日交接仅作历史，已有完整查询闭环不重复建设。
