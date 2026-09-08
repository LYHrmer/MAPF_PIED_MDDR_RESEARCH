# 新 Codex 终端交接：完整完成 MAPF 实验前设计

行政交接记录，2026-09-05。它不是新科研候选、审稿票或放行文件，不改变任何冻结裁决。

## 目标与导师最新意图

唯一目标仍是完成实验开始前的全部设计、来源证据、协议、反例、预注册与独立审查，并通过逐项完成性审计。不是只写计划，不是先实现，也不能把目标改成写完下一份文档。

导师认为单纯延迟的创新与实际问题联系不足，希望研究实际误差，或者处理延迟与误差的联合问题；保留 PIE-D 作为基线。用户允许组合与改进，要求机制可实现、效果可检验且比较对审稿人有说服力，允许使用 Claude Opus 建设性协作。

尚未由证据最终选定“连续定位/运动执行偏差”与“离散状态/完成反馈错误”哪个最适合做主问题。当前 69 只覆盖所声明的反馈错误，不涵盖物理偏航、错边和几何定位控制。不要把现有路线说成导师已批准的唯一误差定义。不能把随机延迟改名为随机误差；需要说明真实发生机制、观测与物理状态的区别、可信前提及可能产生效果的算法改变。已安排期刊扩展检索寻找更好的路线。

纯仿真可以支撑明确定义的模型内结论，不自动证明真实机器人传感、制动或部署性能。没有硬件或还没跑出性能数据，不应单独被当成实验前协议不能完成的理由；也不能凭设计宣称效果已经成立或保证期刊录用。

## 强制边界

- 先遵守新会话注入的 AGENTS.md。此前 /home/lyh/AGENTS.md 不存在；若仍不存在，仅记录事实，不创建或臆造内容。
- 所有 shell 命令和命令链每一段均以 rtk 起首。原样读取使用 rtk proxy cat 等；没有调试例外。
- 所有显式文件编辑使用 apply_patch；新科研和行政工件只放 /home/lyh/MAPF_PIED_MDDR_RESEARCH。
- /home/lyh/桌面/智能仓机器人分布式调度_文献备份 永久只读。
- 不得重读旧 35-38；不得读取 Q-CAL/Q-CONFIRM outcome 或 scientific payload。不要进行全目录递归扫描或全量打包上传。
- 不修改既有冻结候选和审稿报告；实质异议必须用新编号、新字节、新哈希处理，不能 cosmetic rehash 或封存有异议的旧稿。
- H、T_delay、B_CAL、B_max、B*、P_active 和 density N 只保留既有含义的未赋值符号，不填数值、范围或暗示取值，不借顾问意见重定义它们。
- 同一 tick 内连续减速在标准离散 MAPF 中是语义空操作，必须与协调 WAIT 分开。多 tick 慢行只有显式 edge-in-progress、区间占用和速度风险模型才有意义。
- PIE 保持唯一默认 MOVE 提案源；外层只能保留该原 MOVE，或转为已证明安全的 WAIT/既有事务 containment，不得另造 MOVE。
- 全程 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。禁止实现算法、构建/测试、运行模拟器、生成实验/scientific payload、调参、写结果或更新全局 release。允许只读审计和写未执行的复现/机械检查合同。
- 在同一任务中每个需要的文件尽量一次完整读取。截断时先利用同次返回缓存补展示；只有硬失败才补读缺段。不靠反复读旧稿堆积上下文。
- 所有实质研究候选/协议须按科研导师 skill、Nature reviewer skill、无 skill 独立逻辑的顺序接受审查，最后由根代理逐条验收。审稿人 CLOSED 不能覆盖另一人的 bearing。
- 正式审查要有注册、开始、结束 hash/bytes/lines 和候选/skill 完整读取证明。空输出、API 失败、身份变化、未读全或仍运行都不是通过。
- Claude Opus 可作 NONBALLOT 建设性顾问；只有实际非空、完整回执有效。顾问运输成功不等于内容正确，更不等于正式审查通过。

## 历史封锁，不要复活旧链

52 不得修改或生成 sidecar。历史预期身份如下，新终端如需要执行原始独立身份检查，只核验这两个精确文件，不重新翻阅整条旧候选链：

- 52_MDDR_PIE_LOCAL_DISTRIBUTED_ALGORITHM_LITERATURE_AND_CONSTRUCTIVE_SUCCESSOR_DESIGN_DRAFT_20260902.md：SHA-256 a87c2396dd46d5006821b4a396325ddb8d309134ff138488db5a1d29808513ed；42702 bytes；336 lines。
- 52R1_MDDR_PIE_LOCAL_DISTRIBUTED_ALGORITHM_RESEARCH_MENTOR_REVIEW_20260902.md：SHA-256 686ac189f958d4adbf0c52dbf052b65871ff1a87d529a440bd981e902f1f5ad5；26527 bytes；234 lines。

这些是继承的冻结身份，不冒充本交接时重新检查的结果。52 的导师裁决为 CONDITIONAL / OPEN / BEARING-OBJECTION / REVISION-REQUIRED / NONBALLOT；当时资格是两 PASS、四 UNKNOWN，不得传承为当前通过。

51 的 d22dfd42867a441d17b0d491c2b17c1785b3bf6e9345befda98125aa7b65905b 候选，Claude 三次运输失败已在 51A ledger §18-23 终结为 FAILED-TRANSPORT-CAP-EXHAUSTED；不得重新投票、生成 sidecar、改名或 cosmetic rehash 复活。旧 Opus handle 22594 没有在本轮收到有效回执，不能替代正式审查；不要把历史未完成状态当成新鲜的运行证据。

## 当前文件与已核验身份

下列路径均相对 /home/lyh/MAPF_PIED_MDDR_RESEARCH。除两份可更新的 GitHub 行政进度页和 .gitignore 外，候选与报告保持冻结原字节。

| 文件 | 本轮实际 SHA-256 | bytes | lines |
| --- | --- | --- | --- |
| 69_PIE_DTRS_KNOWLEDGE_CERTIFIED_PROPOSAL_PRESERVING_TRANSACTIONAL_REFINEMENT_PREEXPERIMENT_CANDIDATE_20260905.md | e07cc5c7dd3e87d4e03d6e7cd544dedad5f05b686585494630c497f4ae1eb80d | 50975 | 787 |
| 69R1_PIE_DTRS_KNOWLEDGE_CERTIFIED_REFINEMENT_RESEARCH_MENTOR_REVIEW_20260905.md | d1c5772b484fad9c9dab101702181557159c4dfcfa90408e19a746644763d7d8 | 19255 | 161 |
| 69C1_PIE_DTRS_BOUNDED_ERROR_OBSERVATION_CLAUDE_OPUS_CONSTRUCTIVE_ADVICE_RECEIPT_20260905.md | ea3638a0beb6632f5c90a7308db6aab39004300b9b2f781d6c998ff94997a1a0 | 24122 | 258 |
| 68R4_PIE_COMMIT_BOUNDARY_THREE_REVIEW_ROOT_SYNTHESIS_AND_SUCCESSOR_RULING_20260905.md | 09ae7b37f32d4fc380f9dd44d8888b04154f1f83d8fadca09bf05e8a39919458 | 13088 | 199 |

69 的方案骨架：有限进度知识集合、提交时证据认证、逆向 WAIT 依赖闭包、资源所有者与 fencing 事务、按需取证。它是尚未通过的候选，不是已证正确的算法。

69R1 已实际返回；根代理已完整读取报告一次并检查其身份。报告记录候选、research-mentor/SKILL.md 与必需片段的完整读取以及相符的开始/结束身份。根代理接受报告有效性。导师 agent Cicero / 01a06ff7-84f4-73f2-818c-901492dafd1f 已完成并关闭。

69R1 裁决：审查工作 CLOSED；候选 OPEN / BEARING-OBJECTION / REVISION-REQUIRED。九项 bearing。当前候选的独立资格裁决为 1 PASS / 3 UNKNOWN / 2 FAIL；历史的“两 PASS”不覆盖它。已同步 GitHub。

## 必须逐项处理的九项导师异议

1. B01：消息更新的保守性不能证明无消息物理推进时知识仍包含真实状态。需精确定义 Issue、Advance、Observe、Recover、Compact 及逐类包含关系。
2. B02：holes/choice/txn_tags 缺有限语法、concretization 与兼容表；CERT 和 repair 无唯一计算规则，自身 PREPARE 豁免边界不明。
3. B03：有限集合增长只证明终止；leastness、队列无关性与局部性还需完整单调闭包和每次加入的必需性证明。
4. B04：跨资源 COMMIT/ABORT 的持久互斥、PREPARE 持有承诺、撤销竞争、迟到 COMMIT、同 epoch 旧授权排除及 partial start 尚未兑现。
5. B05：inactive 恒等与运行时激活的适用域不明；错误报告未触发保护时的安全责任、激活初始化和退出条件需明确，不能偷看注入真值。
6. B06：DOI/commit/许可 blob 定位不能替代关键原文、源码接口、完整身份和准确的原方法最小审计合同；当前有独立源码证据代理补充。
7. B07：场景选择、故障 schema、跨方法故障键、无对应事件处置、处理耗时期间的物理推进、可信来源及 oracle 隔离需确定。
8. B08：公平性不能仅写“相同信息”；应分别定义官方语义保真比较和共同安全底座下的算法增量比较，避免把可信传感或互锁优势算作算法优势。
9. B09：分清独立配对 block、方法运行与重复观测，固定主要比较量、空分母、删失、重试、预算耗尽和未赋值的停止谓词。

完整行号、证据与闭合标准见 69R1。不要仅照此摘要修改后宣称闭合。

## 尚未返回的三个真实任务

最后一次工具检查：三个 wait_agent 句柄均未返回终态；三个精确目标文件均不存在。等待超时不是失败，不要重复创建同一任务。新终端先尝试查询实际句柄；若无法跨会话访问，明确记录可观测性限制，核对输出文件与实际回执，不能直接把不可见说成通过或把超时说成终止。

| 任务 | 代理/句柄 | 唯一约定输出 |
| --- | --- | --- |
| 69 Nature 正式第二路，已在导师回执后启动 | Boyle / 01a0700b-e9cf-7283-abc2-bc3908562d6c | 69R2_PIE_DTRS_KNOWLEDGE_CERTIFIED_REFINEMENT_NATURE_REVIEWER_REPORT_20260905.md |
| 实际误差与处理延迟的扩展期刊检索 | Anscombe / 01a06ff8-a89f-7c91-8248-f7c8f1555577 | 69L1_PRACTICAL_ERROR_AND_PROCESSING_DELAY_JOURNAL_SEARCH_CONSTRUCTIVE_ROUTE_OPTIONS_20260905.md |
| 官方 R0 与外部基线只读源码证据 | Pauli / 01a0700b-ea09-7792-94d3-7b2acff4497d | 69E1_PIE_OFFICIAL_R0_AND_TIME_INDEPENDENT_BASELINE_IMMUTABLE_SOURCE_EVIDENCE_AUDIT_20260905.md |

Nature 代理必须完整读 nature-reviewer skill，输出三个审稿视角及综合；不得读取 69R1、顾问或其他意见，目标仍是精确 69 身份。Nature 完整有效回执后，尚须新派一个明确不使用任何 skill 的独立逻辑代理，完整审查同一 69，输出 69R3。目前 69R3 尚未注册或启动。即使已知导师有 bearing，仍收齐这条顺序审查链，不能用 Nature 通过覆盖导师。

文献代理应用 nature-academic-search，目标至少十二篇相关一手来源和至少四篇可访问全文的深入阅读，达不到如实记录。应给三条不同的建设性路线、推荐排序、可组合机制、外部比较器、消融、失败反例与纯仿真边界。只读摘要不算读全文，不能为凑数提高证据级别。全文任务已含定位/运动误差、反馈错误、处理延迟等方向，不只围绕当前方案寻找支持。

源码代理不实施、不构建，不读本地旧稿。补关键不可变 URL、完整 Git blob SHA、短源码/原文摘录、行号、调用链、输入/动作/完成报告合同和未执行的最小命令模板。它的报告 NONBALLOT，不是复现成功或资格放行。

新终端接任根代理；上述旧线程子任务只完成各自约定输出。不要因新终端启动而自动再派副本，也不要让两个根代理同时起草同一后继文件。

## Opus 的实际进展与拒绝边界

本轮 Opus 本地执行 handle 6394、CLI session 0070e914-b42b-41db-8af8-e081f13aa1a9 已实际终结，exit 0，非空完整 JSON，末尾 ADVICE-COMPLETE。客户端 modelUsage 报告 claude-opus-5；这只是客户端元数据，不是独立后端证明。69C1 保存实际回复、prompt、元数据及根代理限制。

顾问只读概要，没有读 69 全文，不是正式审稿。其建议存在明确问题：单个 MOVE 改 WAIT 未必安全；软件签名/令牌不能证明物理清空；不能把互斥当估计器剪枝前提再用它证明互斥；CLEAR 不自动排除逼近者和不可撤销旧动作；隐藏状态下分别存在恢复动作不代表有一个可观测策略可安全选择；统计覆盖不变成无条件安全；不同模态不自动独立；不得用它重定义保护符号。可借鉴集合更新、因果回溯、按需取证与抽象精化方向，但所有机制还需独立推导。

## 已知一手来源与审计对象

- PIE-D / PIE 官方论文：AAAI 2025，DOI 10.1609/aaai.v39i22.34506；官方 PDF https://ojs.aaai.org/index.php/AAAI/article/download/34506/36661 。
- R0：https://github.com/YueZhang-studyuse/LMAPF-delay ，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357；已有版本/许可/入口声称由 69E1 重新以原始证据核验。
- 外部基线：Time-Independent Planning for Multiple Moving Agents，AAAI 2021，https://arxiv.org/abs/2005.13187 ；https://github.com/Kei18/time-independent-planning ，commit 755a7ce740d49543b1165403371752c08e342ca4，publication tag v1.0；包括 FSP/MCP/Causal-PIBT，具体接口由 69E1 审计。
- Hönig 等 RA-L 2019，DOI 10.1109/LRA.2019.2894217，作者全文 https://whoenig.github.io/publications/2019_RA-L_Hoenig.pdf 。
- Liu 等 SoCS 2024，DOI 10.1609/socs.v17i1.31543；近邻原文曾读过，后继证据仍须可直接复核。
- Liu 等 Artificial Intelligence 2026，DOI 10.1016/j.artint.2026.104586，官方 https://www.sciencedirect.com/science/article/pii/S0004370226001128 。
- POD / Protocol-observation discrepancy calibration for robust multi-AGV coordination under noise, delay, and faults，Robotics and Autonomous Systems 2026，DOI 10.1016/j.robot.2026.105701，官方 https://www.sciencedirect.com/science/article/pii/S0921889026003726 。本轮直接打开全文返回 403；搜索所得官方片段不能支持“它没有某功能”的否定结论。
- Planned synchronization for multi-robot systems with active observations，Autonomous Robots，DOI 10.1007/s10514-025-10225-4，官方开放页面 https://link.springer.com/article/10.1007/s10514-025-10225-4 。本轮根代理只展示并阅读了部分页面，不冒充全文；文献代理负责深入阅读与更多来源。

ADG、commit cut、通用 MOVE/WAIT 协调、信念安全过滤、fencing/事务、主动查询、CEGAR 等已有工具本身不能重新认领为创新。对组合贡献必须有差异矩阵和可证伪的增量效果机制。

## 后继候选必须覆盖的完整协议范围

按依赖顺序闭合官方 R0、外部已发表基线、一手 robust-delay/robust-execution 近邻全文及差异矩阵；再闭合可计算方法和证明、C1 的资源唯一 owner/commit authority、事务 ID、epoch/fencing、幂等消息、OBSERVE/PROPOSE/PREPARE/COMMIT/EXECUTE/COMPLETE/ACK/ABORT/RECOVER 状态机；明确 vertex/directed-edge/opposite-edge/origin-release/destination-acquire/mid-edge failure 与 physical occupancy 优先级；safe holding vertex 须同时满足静态可停、动态预约、制动可达；覆盖 lost ACK、clock skew、network partition、unbounded delay、corridor/tree、intersection、starvation、component merge 的最小反例及降级；固定 PIE inactive bitwise identity 与 triggered refinement 两个机械检查合同；冻结外部比较器、strict same-compute/natural-runtime 双轨、独立样本单位、配对、失败分母、停止/删失、公开地图/任务/delay-trace 来源和纯仿真预注册。

三路报告收齐后根代理逐项综合所有 bearing，并结合 69L1/69E1 的有效证据决定后继路线。69 已有 bearing，必须另立新编号、新字节；不要修改或封存 69。下一个编号通常可考虑 70，但先确认精确目标未被另一根代理占用，不能盲目覆盖。

每个新实质候选依序接受科研导师、Nature、无 skill 审查，并由根代理按证据验收。形式上的章节齐全、审稿分数、候选篇幅、版本数量和主观完成百分比都不是通过。完成性审计要逐项指向有效原始证据；所有六门、协议与审查闭合前不得宣布实验前工作完成。

## GitHub 私有进度与上传规则

用户已明确授权创建并持续阶段性同步私有仓库：https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH 。

根代理已实际核验 private=true、visibility=private。默认分支 main，最近远端实际核验提交为 9e5e49699d3dbb789cf12d7e567ef207729bfe32。它包含当前 69R1 与更新后的九项修订任务。

本地 /home/lyh/MAPF_PIED_MDDR_RESEARCH 已初始化 Git；.gitignore 默认忽略全部，只逐文件放行允许上传的实验前 Markdown。现有根 README.md 保留未改且未上传；GitHub 首页使用新建 .github/README.md，详细进度是 GITHUB_PROGRESS.md。这两页与 .gitignore 是可更新的行政文件，不是冻结科学裁决。

只提交明确清单，不能 git add 整个目录、全量备份或创建 release。新报告应在实际结束、核验身份和阅读后决定同步，运行中或缺失的报告不能先记为完成。本交接记录目前仅本地保存，尚未纳入上传清单。

Git 操作已获用户授权；不要修改全局 Git 设置。此前沙箱阻止连接 GitHub 代理，联网推送需使用正常授权机制，不能绕过。已获批准的推送形式为：
rtk git -c core.hooksPath=/dev/null push -u origin main
禁用该次 Git hooks 是为避免提交/推送触发未经授权的构建或测试，不代表改变科研代码。

本次前一轮是实质进展：取得并核验 69R1、启动顺序 Nature 审查和源码审计、同步私有 GitHub；不是完成整个目标。目标继续 active，不应标记 complete 或 blocked。
