# 73R2 Nature reviewer 完整设计审查任务

日期2026-09-14。你是固定73第二路正式审查，根已完成首路有效性验收与不用skill的直接分析后才启动本任务。不要以此前流程的推进推断本稿应当通过；不读取73R1报告或本轮根意见。目标为MAPF领域认可标准及SCI二区/三区（JCR或中科院均可），没有指定期刊，当前是实验前参数化设计，不是已有结果的投稿稿。

项目/home/lyh/MAPF_PIED_MDDR_RESEARCH。唯一科学输入73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md，SHA256 b64f5b555034655b2676226d051a70c03aab3679d67c00bc334fb588c4811a8a，315128 bytes / 971 LF。读前/读后核身份，分段亲读全部971行及15节，无缺段/截断；标题/状态为固定时点，不修改任何候选字节。不以摘要、关键词、章节表或他路阅读代替全文。原要求来自72R4_THREE_REVIEW_ROOT_SYNTHESIS_AND_SUCCESSOR_REQUIREMENTS_20260907.md，实际完整读其S1–S9及必要上下文，旧72意见不自动转成73反例。

实际完整读/home/lyh/.codex/skills/nature-reviewer/SKILL.md及所需七参考：references/source-basis.md、reviewer-workflow.md、review-axes.md、report-structure.md、role-boundaries.md、qa-checklist.md、editorial criteria and processes.md。以本地主source与候选事实为依据。按skill由同一个审查代理产生三种侧重的报告＋综合，不派子代理替代亲读，不冒称三名独立真人或虚构专业身份。用户目标优先：五维评估可用，但Nature的广泛影响力/录用标准不能变成SCI二区/三区设计准入门；不给录用概率、无数据结果或期刊分区新断言。

审查应完整覆盖条件安全、贡献与强对照、设计可检验性和表达，并特别核：

- 真实横向误差、名义参考/实体、普通反馈与可信进度是否分清；以PIE-D为底座保留哪些、共同修订哪些；内部D/R/E0与发表原法/适配系统分别承担何种证据，不能造基线。
- P1–P6及§15的全部前提、量词、控制/原MOVE、q前向/闭边界、有限组/围栏、终点责任、END→READY→消费及乱序/撤销/GC的全稿组合。有反例给完整前提和可定位推理，不能只说“可能不安全”。
- 付费CAPTURE与权限、AUTH受控类型、单writer/占槽、后继发布、原时钟/RNG、AA历史/缓存、GNU11/Boost/arena/诊断及原子guard合同。区分已读源证据、正常参考接口与具体后端未验证；未知回调/源UB不是合法算法失败，已定义接口未实现也不自动是数学反例。
- §9.3给定FIT以及独立deadline/窗口/交付等前提的联合日历与首次真实服务；本稿没有证明FIT域非空或具体ABI可容纳实例。判断条件结论是否支持现有主张，若缺证据写明层级及最小下一项，不要求逐编译指令或全系统库普查。
- §10外部PIE-D/H19规则、共同域与实际复现差异，§11来源/selector/alias/有效delay/MAIN与压力层，§12 WORLD/INIT、全roster/固定E和w、真实服务、失败/缺失/可估性、独立block与主次区间。
- §13–15信息价值、净服务假设、机制/系统比较和零/负效应解释；不能要求先跑阳性或硬件结果才允许可检验设计，也不能由纯仿真模型推实机性能。

输出73R2_NATURE_FULL_REVIEW_20260914.md，只有这个新文件可编辑，使用apply_patch。遵守skill的Review setup→Reviewer 1/2/3→Cross-review synthesis→Risk / unsupported claims，每个侧重均覆盖五轴，标明同一事实基底、同一代理三种侧重；引用短句/节/实际行号，不大量复印候选。综合需给每条主要意见的定位、证据或反例、实际影响和最小下一项；区分承重矛盾、未定义规格、实例化资格未知、待实验假设、可读性。

请明确分别回答：能否接受为下一阶段参数化设计规格；是否已具候选实现资格；是否已具主实验资格。按S1–S9给对应，不以报告数量、章节齐全或无反例当通过。不读取首路报告或根当前意见来形成结论；不要求它们作为科学证据。关键一手来源若本次未读，明确只是候选所载证据，不假称亲读；仅在具体事实影响判断时有界核查候选所引来源，不另开泛文献调查。

操作约束直接在此自足列明：全部shell前缀rtk，精确内容rtk proxy；无.codegraph不建立。不实现、不写实现伪代码、不构建或运行研究测试/算法/RNG/仿真/机器人，不赋H/T_delay/B_CAL/B_max/B*/P_active/density N，不生成O/种子/tape/manifest/配置/结果。不读实际map/scen/config/agent/task/delay/result正文或图像、35–38、Q-CAL/Q-CONFIRM；L23已完成，不重读扩读。源码/原文/许可/parser/库头的具名静态核验可以做；桌面旧备份只读，不改冻结候选/报告/提示及其它文件，不做Git写入、不向外部人员发消息，不绕过审批或登录限制。用户要求加速且不降低质量，停止没有新证据的重复审查或底层发散。

完成后核候选身份未变，给报告SHA256/bytes/LF及END_73R2_NATURE_FULL_REVIEW。只完整报告和真实终态算收件；不得只交评价摘要、半读候选或意向任务。
