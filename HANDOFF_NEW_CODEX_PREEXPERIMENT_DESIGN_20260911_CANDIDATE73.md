# 新 Codex 根代理接续交接：73 实验前设计（2026-09-11）

本件由旧根 /root 根据用户“整理目前情况并生成新 Codex 终端接续说明”的要求建立。**研究没有完成；73 未固定、未送审、未接受；HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。** 本件是接续入口，不是正式候选、审稿意见或资格放行。旧根完成这次精确同步后停止科学写入，避免与接续根竞争；最后一个已启动的 C22 原调用已真实结束并封存，没有把活任务丢给新根。

## 1. 首次接续必须按顺序读取

全部相对路径均位于 /home/lyh/MAPF_PIED_MDDR_RESEARCH/。请完整读取而非只看摘要或关键词；工具输出截断要补齐。旧交接保存历史边界，本件纠正其已过期状态。

1. 本文件全文。
2. HANDOFF_NEW_CODEX_PREEXPERIMENT_DESIGN_20260908_CANDIDATE73.md 全文。
3. 其指向的原始 HANDOFF_NEW_CODEX_PREEXPERIMENT_DESIGN_20260905_9e5e496.md 全文。
4. 当前 73A1_CONSTRUCTION_DECISIONS_AND_ACTUAL_TASK_LEDGER_20260907.md 与 73A2_SUCCESSOR_ROOT_VERIFICATION_AND_PROGRESS_20260908.md 全文，从最新日期段向历史核对。
5. 72R4_THREE_REVIEW_ROOT_SYNTHESIS_AND_SUCCESSOR_REQUIREMENTS_20260907.md 与 72R4A_GOAL_STATE_AND_LATE_RECEIPT_ADMINISTRATIVE_CORRECTION_20260907.md 全文。
6. 当前 73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md 全文。
7. 再按本件第 5–8 节读取接续主题的实际完整报告及原始咨询回执。准备固定新候选之前，应回到 72R1/R2/R3 原报告及 S1–S9 逐项确认，不能用摘要代替全部正式意见。

先检查当前注入的 AGENTS.md、文件身份和报告状态，再独立核验 GitHub 远端。2026-09-11 本轮实核 /home/lyh/AGENTS.md、研究目录 AGENTS.md 与 .codegraph 均不存在；适用用户当前注入的 RTK/CodeGraph 指令。不存在索引就跳过，不创建或重建。新终端如环境改变，应按实际情况核验。

**特别纠正旧交接：** 9 月 8 日主稿 107921 bytes/418 行及其旧 SHA、GROUP_PREFIX 仅备选、P2/L3 待回等均为历史状态；现在 GROUP_PREFIX 已入草稿，主稿为下述 216498 bytes/665 LF。69–72 审查早已收齐且未通过；73 尚没有正式审查。用户最初提供的提交 19137140193636d49e80c4cc50ca2ad4281fc309 是历史交接点，不是当前 HEAD。历史行政段中的 active/paused/待推送时态只对当时有效，不得自动继承。

## 2. 原目标、授权与不可越过的边界

完整目标是：完成大规模实验之前的全部准备，设计符合多智能体路径规划领域认可标准，以能形成有说服力、可发表的论文为最终方向；设计闭合后评估合适会议/期刊。允许组合、改进和更换路线，不把现路线当唯一答案；不能保证正结果或中稿，也不能把阳性数据作为实验前设计通过的前提。主证据仍是大规模 Lifelong MAPF 仿真，局部机制解释和两台 LIMO 仅可作为后续补充，不当前搭建或运行。

用户已授权自主完成必要工作，常规可逆研究和既有私有 GitHub 精确同步不需反复询问。用户明确要求充分使用 Claude Opus，分工不限审查；有界建设、反例、方法学习与来源检索均可，根须独立判断。真正权限审批遵守当前工具规则，不能绕过沙箱、防护拒绝或外部访问限制。

- 每一条 shell 命令及每个链段都加 rtk；需要原始字节/精确引文用 rtk proxy。编辑只用 apply_patch。新研究及行政工件只写研究目录，不能用 shell 重定向/脚本写科学件。
- 不实现、写实现伪代码、构建/研究测试、仿真、调参、控制机器人；不生成或运行实验载荷、结果、O、种子、tape、manifest、具体配置/场景。静态文档核对、来源正文/许可/parser/接口读取、文件哈希和 Git 校验不是研究实验。
- 35–38、受限 Q-CAL/Q-CONFIRM 科学/结果载荷继续禁读。实际公开或本地 map/scen/config/agent/task/delay/result 正文及地图图像也不能因为“公开”就读取。只在既定边界内核对象元数据、目录、README、许可和解析器源码；不得把元数据检查伪装成载荷资格通过。
- 冻结 52、52R1、69–72 候选与已完成报告、提示和原始回执。不能美容改字节、重排换 hash 或回填旧结论。73 当前可以实质修订，但每次说明身份和所改义务；正式固定后任何承重修复按既有新候选规则处理。
- H、T_delay、B_CAL、B_max、B*、P_active、density N 保持原含义且 UNASSIGNED；不赋数值、范围、默认值或偷换定义。纯数学推导条件必须说明不是实验参数赋值。
- /home/lyh/桌面/智能仓机器人分布式调度_文献备份 永久只读。用户后续仅授权在必读论文变化时更新 /home/lyh/桌面/MAPF_实验前必读论文_20260909；这不授权写其他桌面位置。当前 12 PDF 与两份指南未变；本交接未写桌面，PDF 不入 Git。
- Git 只同步精确白名单文档至既有私有仓库，不 add .、不上传整个目录/桌面/受限材料，不改全局 Git 设置或运行仓库 hook，不发布 release，不对人发送外部消息。

最近实际 get_goal 返回 paused，完整 objective 是“完成大规模实验之前所有的准备工作，方案设计一定要符合多智能体路径规划领域的认可标准”。这是目标控制状态，不是研究 blocked 或 complete；本次没有调用 update_goal。新根应查询自己的实际目标状态，不能把旧终端状态或缓存当作当前事实。交接完成不得标记研究目标 complete。

## 3. 已核身份、私有远端与运输边界

既有 origin： https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH.git 。本轮直接 gh API 核 full_name=LYHrmer/MAPF_PIED_MDDR_RESEARCH、private=true、default_branch=main；本地 HEAD 与远端 refs/heads/main 同为 **52a798e2875772387514bbd0f63a6c6311bb6ea6**，交接编辑前工作树 clean。这是本交接提交之前的最新科学批次；本件及 P29/C22 封存会另作精确同步，最终用户答复给实际新提交，不能要求新终端 HEAD 永远等于 52a798e。

52a798e 是 11 文件批次，父 a5a8c15540f4b91d75e27a8ff20d6af8ac3c0c8d。实际 commit 042aa6/exit0，332 insertions、8 deletions；push session97054→8d1224/exit0；本地30740d、远端52bcdf同 SHA，04f1f0当时 clean；默认 cached --check 83de92/exit0、精确路径80fc95，无格式例外。父 a5a8c15 为 13 文件批次，真实 commit b60b9d，push1883→33652f/exit0，默认检查600ea2/exit0。更早运输回执在 A1/A2；不能从它们推断本次尚未执行的推送成功。

本轮根再次实际核得如下 SHA256。bytes/LF 是字节和换行数，不是证据权重。

| 文件简称（精确全名见读取顺序/目录） | SHA256 | bytes / LF |
|---|---|---:|
| 原始 20260905 交接 | f1bdd8d11fb6c433f2465b61eb9cbeac5dd15bf33842cb358cf884c0b3f46461 | 17286 /133 |
| 20260908 交接 | 915e8146c0f19f5a5ea30ca6d5d443c9bee5f68456d92fa1c24babb63d7e6f04 | 25645 /166 |
| 冻结 52 | a87c2396dd46d5006821b4a396325ddb8d309134ff138488db5a1d29808513ed | 42702 /336 |
| 冻结 52R1 | 686ac189f958d4adbf0c52dbf052b65871ff1a87d529a440bd981e902f1f5ad5 | 26527 /234 |
| 冻结 69 | e07cc5c7dd3e87d4e03d6e7cd544dedad5f05b686585494630c497f4ae1eb80d | 50975 /787 |
| 冻结 70 | 487816cd59322e23f79a569454a3bde41f00564143c8c16606e87381caf677d7 | 76103 /450 |
| 冻结 71 | 3a3da493613d36dfe64280d468dd34c90498cdfe854ba939128b1e84bb7b4d51 | 72567 /352 |
| 冻结 72 | d2b7ee412b59b070f33cd80036f1e79b55ffb6fa6b79aa0a3d39e8b359f7bc84 | 86528 /353 |
| 72R1 导师 | 5c216348f5ebc97baf3ef5739344d3878d9ad740c0d707f35c5731b662513e81 | 35031 /240 |
| 72R2 Nature | 03b9fedf0d130a95421b2d6335365e723caa186544d21b8deeff33ff87f0e07d | 36244 /303 |
| 72R3 无 skill 逻辑 | 693b2651b2691b51b9429241f1a32890a7f2bc2b2f109081cbc27bf00b286021 | 16445 /104 |
| 72R4 根综合 | a8b73cb49c56f41a95591ab1813c06c7f708d24dad74406ad14ab36c8cf09720 | 16304 /93 |
| 72R4A 行政更正 | 6a6e574de99644dc5d4a24ce1a886a366ed3f455f4e286dc4d1a605f662e9269 | 1901 /11 |
| **当前 73 主稿** | **9e06199cc6045ddd750b861b3091ec239c7c6ff2ae7eeaebbdd0e7fde61ec113** | **216498 /665** |

73 最近八段全文读回比对47f95b/ca74d8/75d4e5/e36f38/60f881/4fc3ee/26a127/fc4b09及整体cd2b83已完成；本交接再次202919核同身份，未改主稿。文件名日期仍为 20260908，不能据名称误判其内容仍是旧版。主稿 W01–99 全部 NOT_IMPLEMENTED / NOT_RUN；没有实际性能结果。

## 4. 六门到底是什么，当前为何未放行

下面是 **72R4 最后一次有效正式根验收快照**，不是已经对修订中 73 做了新的正式裁决。三路审查收齐不等于候选通过。数目不能当完成百分比。

| 门 | 最后正式状态 | 新根仍须解决的内容 |
|---|---|---|
| G1 实际问题 | PASS，限明示模型 | 实体空间偏差、参考/实体、普通反馈与处理耗时已区分。不是随机延迟改名。 |
| G2 已发表锚点/学科 | PASS，限锚点存在 | 有已发表论文支撑问题归属；不等于直接近邻排除、组合首创或投稿竞争力已经证明。 |
| G3 官方 R0 与共享源 | UNKNOWN | 可达调用及库依赖、读域、持续私有状态/RNG、时钟、失败/退出、真实计量与执行后端的完整证据。 |
| G4 外部已发表基线 | UNKNOWN | H19 论文/固定源码/共享系统适配已细化，同域适用、来源继续域及全成本公平仍未全闭。不能用内部消融顶替外部已发表基线。 |
| G5 来源和合法域 | UNKNOWN | map/agent/task/delay 素材许可与对象身份链、完整合法 source_id、非空适用 profile；目录存在或哈希局部匹配不等于全链通过。 |
| G6 公平纯仿真闭环 | FAIL，指冻结 72 字节 | 72 的前向证据时间量词有反例，终点未消费权限、实体真实服务充分条件、INIT/总体与完整服务拓扑需修订。73 已做大量针对性构造，但未固定和接受全稿审查。 |

73 的现状应表述为“设计与证据仍在收束”，不能说“只差运行验证”或“六门已经自动更新”。实际执行/计量、控制与服务可认证性、完整协议组合、外部公平、来源、近邻全文和统计条件仍有承重未知。

## 5. 73 已经入稿的实质内容，避免新根重复或倒退

### 5.1 空间、组前缀与终点

采用真实横向偏差 X=u+s e+z+F、z'=-κz+w，独立保留实际控制误差与处理/通信延迟。有限保守几何允许同一资源多段相交，以最后退出严格判据处理闭边界；不把新空间模型归结为随机慢走。

GROUP_PREFIX 已入稿：同一个原 MOVE/tid 在组合同中推进，q_release≤s≤C≤b≤ell，速度满足到当前已安装 C 的制动余量；RUN/BRAKE/HOLD 明确，没有中点 END 或免费自动 RUN。有限 CAND/Theta/SCC 组搜索、第一合格组、失败候选及几何全部收费。F_G 排他与 A_i/B_i 不交必须组合保持；GROUP_RETIRE 需全组中心 FINISHED 和终点/关闭证明，下一 MOVE 受组退役屏障。READY/WAIT 允许的消费与物理重启不是一回事。E0/F_cap 具有相同 cap/维护能力，E0 不因没有观测就被刻意削弱。

当前 NOISY_ALGEBRAIC_REFERENCE_PROFILE 保留 eta、原 a_cmd 和 LAUNCH/APPROACH/BRAKE/HOLD，采用明确结构子族 a_hi−a_lo=4δ 及有限代数输入、原允许行上分段常值 eta；这是域限制，不是全旧域等价或保护参数赋值。P20/C18 给 APPROACH 的代数闭式，旧 cap HOLD/ell END 优先，真实 ACTUATOR 到提交仍收费并核当前根。P18/P19 给有限空间驱动下固定 TASK_SERVICE 时刻实体服务谓词的条件可判定构造；不能外推任意连续驱动、任意首次命中事件或真实后端容量已满足。

### 5.2 任务世界、观测复用与更强 R 对照

P21/P22/C19 已选择理想外部 TASK 世界：宿主真值求值 CPU 不挤占虚拟 TASK 行额度，原 TASK_SERVICE 机会不变；所有线上控制/证书/策略仍有各自原配额。TASK 行从同一 A^- 判断原队首，最多每 agent 一次，统一出队和贪心补队后原子发表整个 A+，新任务不在同一行再次服务。宿主 CPU/wall/memory/失败仍按臂真实报告，不强制同账，也不给算法免费真值。Q/E 表示理想任务服务设施下的虚拟系统效应，不冒充全实机 CPU 性能。未认证求值不能留半本 A 或伪造零费用/停止。

P23/P24 已将观测改为 CURRENT_SEGMENT_ROOT：在原 Srv_E 付费冻结当前精确参考段、采样点与必要终点历史索引，作为 FINITE_CAUSAL_REFERENCE_HISTORY 的受限只读投影。已付、合法存在的控制状态允许复用，不强迫每次全史重算；新增求值/认证、查询诱发的引用保留、复制、读屏障和生命周期费用仍付。传递依赖不可变，旧样本不因以后 END 刷新，内部 eta/版本不泄漏。实际源、权限、计量仍未知。

P25/P26/C20 将 R-S/R-F_cap/H19R-S 和 D 零正分回退改为固定 (session,agent) 稳定循环，而非随动作 e 改变排序键。冻结 agent 同时绑定唯一完整 Active tid；请求与 last_agent 同一成功 SELECT 原子发布，后续采样/网络失败不回滚游标，动作更替不重置。纯 R 对持续 Active 原 tid 的成功选择次数有条件上界，不推出有限 O 有足够机会、实际样本到达或 Q；D 正分混合选择没有因此得到同样公平界。唯一未闭槽/Active 索引的一致性已写明，不静默去重。主比较 D-S−R-S 与必须报告 D-S−E0 不变，不能因加强 R 而换弱对照。

### 5.3 R0、外部 H19 与源修复的诚实口径

R0 固定 YueZhang-studyuse/LMAPF-delay，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。当前是明确修复后的 LACAM 共享来源与 ALWAYS_ADVANCE / FAIL_STOP_SOURCE 合同：所有正常完整调用保留私有历史/RNG，即使后续中心 CAS 为 STALE 也不能回滚、重置或重播。E20/E21/E22/E23/E24 已记录终端引导、索引域、explored 对象身份与所有权、图生命周期/复制消除/标量输出、部分构图异常清理的纸面修复；没有实现，也不称原样 native 等价。完整正常继续域及外部依赖/clock/RNG 仍未知。

外部 H19 为 Hoenig 等 RA-L 2019 锚点，固定 whoenig/libMultiRobotPlanning commit 4c75fa20c435c440d8b6bd6dc81668ddc7296ba0 的 ECBS；名为 H19-PR-COMMON-SYSTEM/ECBS-FA。它有自己的 ECBS/ADG/cut，使用相同声明系统能力，完整 cap=ell、不用 GROUP；不是作者 2019 整体实验程序，也不是拿 PIE 提议冒作外部算法。ADG_ENQUEUE 是有限批次单中心 writer，原 Type-2 前驱入队时已经 finished，入队不等于物理 grant。APPEND、f_inst/f_cons、Kc 与 cut/recovery 的前向权限及费用分开。L11 已推 H19 名义 MOVE 时长/原公共规划机会/切拼接；WAIT 名义为零不代表真实消费免费。

H19E0 和 H19R-S 两臂均保留。P27/P28/C21 明确：未 finished 原 Type-2 前驱不能靠途中 q 解除；“已经合法请求 p 但仍有这种前驱”的题设为空域。已入队的动作在所有额外实际资源 owner 阻塞都被合法 q 严格越过最后退出、并真实退休且其它门有效时，局部 guard 才可能改变。不能伪造源实例、把缺 ADG 边称合法几何收益、把 endpoint 从本原动作退休。post-END 历史终点证据可以合法返回，但必须与真正 pre-END 样本分报，不赠给策略真 END。局部可准入不等于 grant、START、真实服务或全 E 总吞吐/总成本更优。

## 6. 已完成但尚未采用的最新 P29/C22：接续时首先取舍

四件均已实际完整返回，旧根全文核验 prompt 0b2d28、P29 fa3593、raw 2ea9b3、receipt 6eb144，ef5b69 逐项核 hash/非符号链接/原文相等。不存在活 C22。正文 744 词超过建议约 700，保留完整原文，不重试。

| 精确文件名 | SHA256 | bytes / LF |
|---|---|---:|
| 73P29_SOURCE_ONLY_NONPREEMPTIVE_ROW_PUBLICATION_CONSTRUCTION_20260911.md | 94b881eac78b738b6f61b8171bc1f05724fa2c3ed4d02d3b8f1ef4f4cae8323e | 16561 /89 |
| 73C22_SOURCE_ONLY_NONPREEMPTIVE_ROW_PUBLICATION_PROMPT_20260911.md | 16835758832351e4fd74b279a7e906ca022850804c0968968fd21a855917b519 | 5899 /19 |
| 73C22_SOURCE_ONLY_NONPREEMPTIVE_ROW_PUBLICATION_RAW_RESPONSE_20260911.json | 0255a646f7559f7d35985a9b2a6e295a549916c63659516c5f03aee46ea76f11 | 6229 /1 |
| 73C22_SOURCE_ONLY_NONPREEMPTIVE_ROW_PUBLICATION_COMPLETE_RECEIPT_20260911.md | bc0c8e5cd4f4362571fed53219926eeba69a26f489a370e32a3db0e145dcaf21 | 12229 /77 |

实际唯一正常升级调用由 Copernicus 执行：functions cell323→exec81862，a149e5启动，a3399c仍活，e6165e/exit0。实际 modelUsage=claude-opus-5/firstParty，completed/end_turn/is_error=false，END-C22，52346ms、3595 outputTokens、0.11914749999999999 USD；session_id=f991ec42-109e-4620-b92f-7d990fdcb089。根核 raw.result 与 receipt 原文逐字相等，不冒称根亲自轮询代理 CLI。交接暂停消息到达前调用已提交，之后只续原句柄封存，没有重启或新题。

候选 SOURCE_ONLY_NONPREEMPTIVE_ROW_PUBLICATION 仅将 Srv_P 改为串行非抢占完整体，其他服务站/控制的有限 PROCESS_SLICE 不变；源 chrono 明改为 a+实际单调 elapsed。完整体及 d、成本、S' 封存，逻辑占槽到 a+d；结果只能在原 O 已有严格后继且 t≥a+d、原本源发布容量足够的行发表，再走中心验证/处置与付费释放。没有新增动态公共完成事件，不预跑下一源体，物理和 TASK_SERVICE 不因宿主先求值而暂停。d=0 由严格 row 顺序防同一行递归，不添 epsilon。

P29 对原处置收件和硬终止提出一个显式源生命周期修订：有限处置字段用原 Srv_P 发布检查容量完整消费；依未来取消才需的任意析构不能藏在这个检查中。外部源关闭明确改为 REVOKE_AND_DRAIN：立即撤输出和新调用权限，已开始完整体及真实尾费保留，body 结束/退出确认/引用回收分开。它实质改变原 WORKER_FAIL/INIT 终止能力与源配额，不能藏在旧名称下宣称等价。源异常、未返回、计量/退出不可证仍保留失败/未知，不能捏造完整成本或 Q。

**旧根本次独立无 skill 分析及接受范围：** 接受“原收件必须收费而其原执行载体被删除”的具体接缝缺口；不同意 C22 直接由 pending 推全世界无定义，因为原 O 耗尽仍可有明示 pending 状态。源发表属于 Srv_P，不能按 C22 写成 Srv_C；其建议保留后体精确切片会把尚未具备的指令闸门义务带回来。取消指令上限改变服务能力，即使每臂规则相同也不等于旧合同。P29 的显式撤权/收尾模型在纸面上可以继续研究，**本次不采纳进 73，也不认定已封闭**：原有限发布检查的真实后端/完整付费、冻结读域与跨 job 时钟/测量末端、正常继续与真正异常/退出域仍须证据；任意行政析构不能由“另记费用”证明可执行或有限。源输出即便因固定后继行保持非预知，仍不自动满足下一节统计前提。根的这段判断仅是建设材料取舍，不是 73 的正式第四路根验收。

当前主稿仍是严格 PROCESS_SLICE 源模型。不要把 P29 口头备选当已经入稿的默认。E17 已给固定 QEMU v10.2.0/commit 698104725efad4b29079d857dfdebbd804e34c99 的具体缺口：现有 icount 预算会再授予、暂停确认未绑定研究 token、chrono 时钟与同 row 常值语义不合；不是“找到 QEMU 就已有后端”。C8SR 只给封存体条件非预知，不能继承实际源/物理/统计资格。新根应对两个源服务模型及其它有证据支持的路线作具体取舍，避免再次泛搜同一工具或重复咨询。

## 7. 最紧接的未完成工作及可并行分工

1. **源执行/计费与原故障合同作实质取舍。** 先全文读 P29/C22、73E17_ROOT_QEMU_FIXED_IDENTITY_AND_CLOCK_INTERFACE_ANALYSIS_20260910.md 和 73C8SR_ROOT_SEALED_SERVICE_CAUSAL_COST_AND_PAIRED_DESIGN_ANALYSIS_20260910.md，再检查 73 §8/9/10/12。若继续 P29，必须补实际 clock/read-domain/metering/发布及退出证据，并解决与原故障、STRICT/NATURAL、有限服务拓扑的组合；不能只换名称即可宣布可实验。若保留严格配额，给真实可支持的接口证据，不能重新称普通 stopwatch 能精确抢占。
2. **统计前提与宿主顺序效应。** 根在用户要求交接前只重读 C8SR 与当前 §11/12，没有完成新的统计原始论文检索或新合同。现稿仍是固定全 roster、固定 E、原权重的配对有界差与独立 block 条件，d_b=(QD−QR)/E_b、目标为按 X 条件期望加权的 theta_DR。真实宿主 elapsed 会受前序臂/区块缓存、负载和调度历史影响；随机臂顺序不能自动证明 block 独立。不能为过门静默改成历史条件 martingale 目标、只随机单臂、只描述结果、只留成功者或无内容的全范围区间。必要时先核一手统计来源并明确同一科学目标下可支持的设计；无新统计方案被旧根采用。
3. **G4/G5 与近邻证据继续收束。** 外部 H19 的源域/读钟/原合法动作和资源 guard、公平能力与费用不能被内部修复掩盖。来源按对象身份、许可/使用依据及 parser 静态合法谓词连成完整链；地图/任务/延迟载荷禁读不变。已发表直接近邻未读全文处继续明确证据强度，不能凭检索摘要声称对方没有某机制。
4. **全稿组合而非继续堆局部报告。** 根据 72R4 S1–S9 核同一状态与权限表：前向 max-q、终点未消费、组退役和下一 MOVE、实际 cap/ACTUATOR、任务世界原子性、所有 writer/server/公开行/费用、INIT/Stop/失败/缺失、两外部臂与强 R、源持续状态。局部代数可终止不等于实际认证精度和配额可支付；99 个未运行 witness 不是已执行证据。
5. **贡献和投稿。** L12/L13 已开展 LMAPF 论文架构学习；不要重做无边界“多看论文”。在方法/比较域收束后给具体贡献—近邻差异—可证伪结果—总成本/失败主张，设计关闭后再以实际文章范围和当时官方征稿/期刊范围评估会议/期刊，不以 Nature reviewer skill 推断要投 Nature。

Claude 推荐用于彼此有不同输入和清晰交付的有界建设题，例如源生命周期反例、同一目标下统计假设核查、某一直接近邻全文机制比较；每题只回答具体义务，根同步做源码/文献原证据与独立推导。调用必须 Opus/high，并核实际 modelUsage、完整终态与正文；请求模型名称不是实际使用证明。保存提示/原始回执/独立纠错，成功 exit 也不是通过。当前没有已启动的这些新任务，应先登记唯一题目/文件/负责人再开展，不能假称旧根已派好或已有结论。

## 8. 最近证据文件导航及来源强度

下列均为已存在的完整建设/证据件，不是新正式审查。按待解问题读，避免重复启动已经完成的同题。

- 数学控制与服务：73P18_FINITE_SPATIAL_DRIVE_AND_TASK_SERVICE_DECIDABILITY_CONSTRUCTION_20260910.md；73P19_ROOT_FIXED_SERVICE_PREDICATE_AND_SPATIAL_DRIVE_ANALYSIS_20260910.md；73P20_ROOT_NOISY_ALGEBRAIC_REFERENCE_PROFILE_AND_C18_ANALYSIS_20260911.md。
- 任务世界与费用：73P21_TASK_WORLD_ATOMIC_SERVICE_AND_COST_CONSTRUCTION_20260911.md；73P22_ROOT_TASK_WORLD_COST_AND_ATOMIC_LEDGER_ANALYSIS_20260911.md；73C19_TASK_WORLD_SERVICE_COST_COMPLETE_RECEIPT_20260911.md。
- 观测复用：73P23_PAID_CURRENT_REFERENCE_ROOT_CAPTURE_AND_REUSE_CONSTRUCTION_20260911.md；73P24_ROOT_PAID_CURRENT_REFERENCE_REUSE_AND_CAPTURE_ANALYSIS_20260911.md。
- 稳定 RR：73P25_ROOT_STABLE_AGENT_ROUND_ROBIN_AND_C20_ANALYSIS_20260911.md；73P26_STABLE_AGENT_SELECTION_BINDING_AND_ONE_ACTIVE_INVARIANT_AUDIT_20260911.md；73C20_STABLE_AGENT_ROUND_ROBIN_CONSTRUCTION_COMPLETE_RECEIPT_20260911.md。
- H19：73L11_ROOT_H19_NOMINAL_DURATION_PUBLIC_OPPORTUNITY_AND_CUT_SPLICE_CONSTRUCTION_20260910.md；73P27_EXTERNAL_H19_OBSERVATION_ENABLEMENT_AND_COST_BOUNDARY_CONSTRUCTION_20260911.md；73P28_ROOT_EXTERNAL_H19_OBSERVATION_STAGE_AND_C21_ANALYSIS_20260911.md；73C21_EXTERNAL_H19_OBSERVATION_ENABLEMENT_CONSTRUCTION_COMPLETE_RECEIPT_20260911.md。
- 源对象域：73E20_ROOT_GOAL_INDEX_DOMAIN_AND_TERMINAL_GUIDANCE_CONSTRUCTION_20260910.md；73E21_R0_EXPLORED_IDENTITY_AND_OWNERSHIP_CONSTRUCTION_20260910.md；73E22_ROOT_EXPLORED_IDENTITY_OWNERSHIP_AND_SOURCE_CHOICE_ANALYSIS_20260910.md；73E23_ROOT_GRAPH_LIFETIME_COPY_ELISION_AND_SCALAR_OUTPUT_ANALYSIS_20260910.md；73E24_ROOT_PARTIAL_GRAPH_CONSTRUCTION_OWNERSHIP_ANALYSIS_20260910.md。E24 已占号，不可覆盖另题。
- 来源：73L18_ROOT_LORR_ARCHIVE_MAP_OBJECT_METADATA_PROVENANCE_20260911.md；73L19_GAME_WAREHOUSE_OFFICIAL_METADATA_AND_REUSE_SCOPE_20260911.md。
- 近邻全文缺口：73L17_KIM_TII_PRIMARY_FULLTEXT_AND_NEAREST_MECHANISM_EVIDENCE_20260910.md。Kim TII DOI 10.1109/TII.2026.3681327 仍缺已核全文；POD/RAS 2026 与 AI 2026 有访问失败及仅官方摘要/预览边界，不称已读全文。
- 论文架构/阅读包：73L12_LMAPF_LEADING_VENUE_PAPER_ARCHITECTURE_AND_METHOD_LESSONS_20260910.md；73L13_ROOT_LMAPF_ARCHITECTURE_EVIDENCE_AND_READING_DECISIONS_20260910.md；73L12A_TRAFFIC_FLOW_READING_PACKET_UPDATE_RECEIPT_20260910.md。

LoRR Benchmark-Archive 固定 commit 25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a。L18 只读元数据：R0 Paris_1_256.map blob 0ff641690b48c1c4807fcea7c0c31d167973b221/65829 与 2024 archive 对象一致，2023 同名 4abf.../131659 不同；random-32-32-20.map b44f5a949e91b251b0e3bb29f3cd0784ce7d80b5/1091 一致。game ht_mansion_n.map 7664df2f7cc97791a477b2529e7cae6d1005ee1f/36217 及 warehouse 目标 302a7ce60744aaf3a0c853c26bbffa3637fa027a/10242 未在该 archive 找到同对象。L19 增补 MovingAI 官方 game DA2/warehouse 目录和使用语境，未核官方同 blob；尺寸排序差异不能擅自按转置认同一图。以上不证明所有 map/agent/task/delay 许可与非空合法 profile。

阅读包 12 篇涵盖 Hoenig 2019、Zhong 2026、S2M2 2021、TIP 2021、Shahar 2021、BUAVC 2022、TPG arXiv 2508.01495v2、MAPF-X TreeLaCAM 2026、Stern 2019 Definitions、RHCR 2021、SCALE 2026 arXiv v2、Traffic Flow AAAI 2024；期刊/会议正式发表与预印本身份按 L12/L13 逐篇核对。不能把“12 篇”都叫期刊全文；本交接没有改变必读清单。后续变化才派明确范围子任务更新获准包并保留来源回执。

## 9. 真实任务、失落句柄与禁止重复

本轮实际 collaboration 列表：/root/construct73_prefix_protocol（Ptolemy）pending_init；/root/source73_external_comparator（Feynman）pending_init；/root/source73_r0_remaining_contract（Copernicus）已给 P29/C22 完整最终回执并承诺停止科学写入。最后两个旧 missing 目标本轮精确 exists=false：

- 73P7_FINITE_SHARED_THRESHOLD_GROUP_PREFIX_POLICY_CONSTRUCTION_20260909.md，旧 /root/construct73_prefix_protocol。pending_init 和曾 interrupt 返回 pending_init 不是科学完成；不重启同题。
- 73L7_H19_NOMINAL_DURATION_PLAN_OPPORTUNITY_AND_CUT_SPLICE_TOTAL_CONTRACT_20260909.md，旧 /root/source73_external_comparator。状态同上；后来的 L11/P27/P28 不冒充 L7 原回执。

更早 69L1/69E1 失落、71C3 第二次 exec60396 不可恢复、73C2 旧 functions117 无可恢复 exec 和完整回执（仅存提示）等历史见两旧交接及 A1/A2。新根先查实际约定文件和可访问原句柄，不从存在同名进程推成功，不重新投同提示。没有实际完整原回执就保留 UNKNOWN/MISSING；新不同题的定点证据不能冒名补旧任务。

C14 实际防护拒绝，无建议；C16 exec29117 timeout124/错误 JSON 无正文且 modelUsage 空；C17 exec14628 timeout124/空输出。不要按“调用过 Opus”记完成，不绕过拒绝。C18/C19 成功终态前的网络/沙箱失败原回执均保存。C20 原 exec69960→fb8591/exit0，C21 原95740→6348b3/exit0，C22 原81862→e6165e/exit0，都已完整收齐及根纠错，不再轮询或重启。

新终端不能依赖旧 functions store、cell、exec session 或代理名称仍可访问。本件和磁盘原件才是接续依据；句柄仅用于核对原运输历史。旧根没有替新根启动未指定的统计/论文任务。

## 10. 何时可以固定、送审和结束实验前目标

必须先完成可审查的同一完整设计、证据和适用域，解决全部承重缺口，再固定新候选身份。必要正式顺序不可省略或并发替代：

1. research-mentor skill 的真实完整审查。
2. 根不用任何 skill，独立逐条分析该意见。
3. nature-reviewer skill 的真实完整审查。
4. 根不用任何 skill，独立逐条分析该意见。
5. 明确不使用任何 skill 的独立逻辑审查；该逻辑代理不读前两路意见，不冒充根已看多路后的盲审。
6. 根完整读回所有实际报告、核固定身份、逐项验收六门及全部原要求。

每次实际使用 skill 须按当前注入规则读取并说明；不能只写名字假装使用。本次交接及 P29/C22 建设没有使用审稿 skill，也没有提前举行 73 正式审查。历史曾为合法下载使用相关 skill，不能将全研究过程说成从未用 skill。

设计 GO 不要求先得到阳性性能；要求公平、可证伪且允许否定/失败/不可估的完整合同及可用来源/后端资格。没有证据时保持 UNKNOWN，不虚设通用失败轨迹来冒充有效研究域。审查完成、报告数量、同步成功或本文写完都不是研究完成。全部资格、协议、来源与最终审查关闭前，保持 **HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT**。

本件及本次行政同步只交付新根可继续推进的真实状态。下一步必须继续第 7 节具体研究义务，而不是再次无限整理交接。
