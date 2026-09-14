# MAPF 项目当前入口

更新：2026-09-14。**主线是在PIE-D框架下处理有界跟踪误差的LMAPF执行：误差包络、原MOVE前缀授权、可信进度与空间释放。参数化设计已接受，当前实施并验证具体代码与完整闭环。ECBS外部组件修复已完成，不扩支线。几何/数值/参考控制、普通页内存、arena核心及B1有限内存接入已有实际检查；INIT、分配hooks与服务站点闭环仍待接入。完整实验前目标、端到端核验和主实验启动条件尚未完成。**

本页是导航和操作约束的唯一入口。按当前缺口读取对应章节与直接证据，不递归全文阅读历史交接、账本和咨询；已有正式审查不因换窗口重新启动。

## 当前裁决、方案和证据

- [73R4最新根裁决](../73R4_ROOT_DESIGN_ACCEPTANCE_20260914.md)：前两路各自根直接分析、第三路完整收件及全部意见综合完成。当前六门为2项限域PASS、4项UNKNOWN；参数化设计接受不替实际源/后端/全来源/外部复现资格，也不等于整个实验前目标完成。
- [73Q1当前静态绑定](../73Q1_STATIC_CANDIDATE_BINDINGS_20260914.md)：首轮源容量存在性、R0具体跨job统计/路径容量和P的条件来源、priorities与原uint计数、H19编号/partial focal/数值接缝已具名接纳；§4的根源码修复/静态编译包已完成。Q1可随建设更新；G3/G4/G6整体尚未通过，不回改冻结R4。
- [73Q2主方法实现绑定](../73Q2_MAIN_EXECUTION_IMPLEMENTATION_BINDINGS_20260914.md)：几何、精确数值、认证dyadic区间、参考段和同原MOVE控制器均已实现，根独立有限运行检查全部通过。控制器已核旧边界优先、BRAKE保持、原终点关闭和冻结快照；真实来源、授权、服务与完整闭环仍须接入。具体检查及范围见Q2 §9/10/12/14/15，不用测试条数代替规模证据。
- Q2 §4固定libriscv v1.20 / RV64IMA-LP64底座，B1–B7为已有接口的实现落点。B1核心/有限暂停费用检查、§19付费参数读取均完成；§11固定GNU11工具链、§16目标数值三库及fenv具名修复也已完成。§18 MemoryAdapter经根独立编译/运行48项通过、0失败（c2c188/04dde0）；§23手工SD/LD/ECALL经真实两普通页和付费a0参数/返回口，65项通过、0失败（738493/bf9478）。后者没有INIT或编译业务guest。固定binutils gitlink实际2.41，不重开选型或扩大ECBS。
- Q2 §20 guest first-fit arena核心已由根全文核并独立严格编译/有限native运行通过（fcbfe7/c05bfa）；目标交叉编译6acf73及ABI核验af24c1完成，未运行guest，实际分配hooks仍待接入。§21宿主记录器7项真实辅助进程检查通过（845b3b），只记录宿主开销/退出，不推导P_model或Q。
- Q2 §17澄清在线性与规模：连续误差及资源受限查询不要求离线规划，批量仿真的墙钟速度与在线因果分开。P_model是确定性模型成本；完整闭环后需量时间、内存、查询积压与任务吞吐，当前尚未证明千级规模或实机实时性。
- Q2 §22仅作统计规模诊断，现行Hoeffding合同不变，不新增统计审查门或据此赋实验参数。
- Q1 §6已列下一输入只读范围：固定四目录剩余360配置，随后只取其真实引用闭包；首次未核输入池上界104项，新组合可能需要按需复读旧blob。根已核482项树元数据，新增正文未读，扩大此前L23有限范围待用户确认。selector/alias/服务/roster规则已有定义，输入事实与WORLD/profile/O等实际绑定分别完成。
- [固定73科学规格](../73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md)：SHA256 `b64f5b555034655b2676226d051a70c03aab3679d67c00bc334fb588c4811a8a`，315128 bytes / 971 LF。自2026-09-14起保持原字节；文件名DRAFT、页内NOT-REVIEWED和旧时态是固定时点记录，实际阶段以73R4为准。
- [导师汇报一页说明](../RESEARCH_BRIEF_FOR_ADVISOR.md)：研究问题、数学表达、方法和结果边界，面向汇报，不替科学规格。
- [当前实验前论文主稿](../MANUSCRIPT_PREEXPERIMENT.md)：已形成问题、方法、条件安全论证、实验设计、图表计划和四项承重引用；结果留空。PIE-D为直接改进基础，ECBS只在外部对照复现说明中定位。该稿不替换固定73，不表示实现或大规模实验准备已经完成。
- [本窗口证据/决策索引73A3](../73A3_DESIGN_VERIFICATION_SESSION_20260912.md)：只按具体问题查阅；早期WORKING、任务句柄、SHA和预算状态是历史，不能覆盖实际文件和活工具。
- 完整报告：[73R1科研导师](../73R1_RESEARCH_MENTOR_FULL_REVIEW_20260914.md)、[73R2 Nature](../73R2_NATURE_FULL_REVIEW_20260914.md)、[73R3无skill独立逻辑](../73R3_INDEPENDENT_LOGIC_FULL_REVIEW_20260914.md)。三路均实际gpt-6-astra/ultra且完整终态，严格按各路后根分析的顺序启动；Nature为一个代理三侧重，第三路未用skill/未读他路。第二路运输中断已从原阅读恢复，无待轮询或待重开审查。原任务保留：[R1](../73R1_RESEARCH_MENTOR_FULL_REVIEW_PROMPT_20260914.md)、[R2](../73R2_NATURE_FULL_REVIEW_PROMPT_20260914.md)、[R3](../73R3_INDEPENDENT_LOGIC_FULL_REVIEW_PROMPT_20260914.md)。

明确基于Zhang等[PIE-D（AAAI2025）](https://ojs.aaai.org/index.php/AAAI/article/view/34506)改进，当前复用作者LACAM-only及承诺/未来路径切分，经明示共同修订，不等于原论文完整PIBT-D＋A。研究真实横向跟踪偏差、有尺寸实体、同原MOVE的GROUP_PREFIX、付费可信进度与空间退休；普通错误反馈、计算通信等待和no-start分开。主比较为NATURAL的D-S−强轮询R-S，D-S−E0必报；内部R/E0及释放消融不冒称文献基线。H19E0/H19R-S是必需的外部系统候选，尚未完成忠实性/共同域资格。P_model计确定基本步，宿主/world CPU、耗时和内存另报，不保证正效应或实机速度，不删失败。

固定R0为`YueZhang-studyuse/LMAPF-delay@0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`；完整PIE-D作者候选为`improve_morereveal@74cfba3c81a0c165c2e7044dea6fd4dee8ddf415`，停止重搜分支。原字节检查、论文规则复现和共同适配分轨；A按(a+b,a)、PIBT-D按delay优先及窗口计数已有规则证据。H19的ECBS组件固定`whoenig/libMultiRobotPlanning@4c75fa20c435c440d8b6bd6dc81668ddc7296ba0`，不是作者整套系统；首匹配/图闭包/源完成GC等已有合同，不重新发明。MCP归属Ma等AAAI2017及TIP库仿真实现，非Causal-PIBT。

DARI已淘汰，旧编号计划不恢复为待办。目标SCI二区/三区，JCR或中科院均可；大规模LMAPF主要是仿真，两台LIMO仅可选补充。既有纯仿真期刊先例不等于录用保证，无硬件不设为当前前置。

## 当前必要工作与分工

1. **优先完成PIE-D误差执行主线的具体绑定。** 接续已验收组件，完成付费INIT、allocator hooks、受限imports及来源授权、观测/资源事务/真实任务服务和站点闭环，复用73 §8/9现成合同。Q1已接纳首轮源存储FIT存在性、R0跨job统计／路径容量、P的条件来源及priorities／计数语义；这些具体证据不重做，也不扩成全roster或实际二进制资格。剩余AA只补实际继续域及其它搜索／导入表示，不笼统重查所有字段。实现后符合性在实现阶段验证，不以尚无实现循环阻止已具备条件的实现。R3-06的入桶前分量过滤结论保持。
2. **来源与外部共同域。** [L23](../73L23_LIMITED_PUBLIC_INPUT_STATIC_VERIFICATION_20260912.md)及[L23A](../73L23A_STATIC_INPUT_PARSER_CONTRACT_CHECK_20260912.md)四类首配置和13引用的基础有限静态核验已完成，不重做。完整selector/alias/全潜在ACTUATOR有效delay/WORLD/服务区和主roster仍须资格；已有研究用途依据，固定版本覆盖与第三方再分发范围分别处理。PIE-D/H19现成矩阵继续复用。Q1已关闭H19整批id守卫、失败fmin来源及partial focal具体身份/计数；实际Astra Ultra的`astra_ultra_ecbs_focal_closure`亦已终态，根在Q1 §2.3选定每轮重建FOCAL/默认cost阈值及不复制handle的数据复制构造，不把抽象风险冒成已运行反例。此前`external_static_binding`两轮建设均终态，不轮询或重做。
3. **准入后的实现与验证。** GPT-6-Astra Ultra负责最难理论、路线及跨模块取舍；Claude Opus承担已获阶段授权且规格明确的代码实现、修复、调试与复现适配。C36首次网络错误、授权重试超过30分钟仍无正文后中止，两次均终态且实际模型未认证；根已接手同一ECBS包、核两处差异/固定来源并通过g++-11 C++14 -fsyntax-only实际模板实例化。原始回执和73C36_ATTEMPT_AND_ROOT_IMPLEMENTATION_RECEIPT_20260914.md、本地implementation/h19_ecbs/README.md分别保存真实调用与源码检查，不归为Claude交付。每包明确文件、输入输出、禁止改动、验收和停止条件，独立修改范围。不让模型无新证据往返审查；W01–99按共同不变量组织覆盖，复用驱动，当前研究运行验证仍未实施/运行。
4. **完整实验前交付。** 结果留空的论文正文初稿、实验章节、图表计划及四篇承重引用已形成于MANUSCRIPT_PREEXPERIMENT.md；两项写作／文献子任务均完整终态。继续补具体预注册、执行／验证／分析工具冻结、完整相关工作与复现包，并完成最终逐项验收。已有至少十二项正文层来源和四份期刊全文历史阅读记录沿73A3查阅；新四篇核验只算相关正文定点阅读，不关闭未读近邻对强新颖性的限制。不得以正文初稿或参数化设计接受代替全部目标。

不新增阳性结果、Nature广泛影响力、硬件或逐编译指令/全库普查门。已定义接口的实现后符合性在对应阶段验证，不能循环要求先有实现才准实现；实际承重语义矛盾也不能推给未来测试。没有新反例或科学规格变更时，不重开固定73的完整审查。

## 有效操作边界

1. 当前按已接受接口实施和验证。Q1 §4外部组件及Q2 §3/6/9–16/18–21/23已完成相应源码、构建和有限检查；§13/15/18/19/20/23实际运行有限指令、控制事件、页面、参数或arena组件，§21运行宿主辅助进程，不能误称仅语法，也不等于业务guest/完整world已验证。§20目标产物只编译/核ABI，§23仅手工指令接入且无INIT。其它未列研究规划/控制服务/业务guest/实验/RNG/仿真仍不运行，不赋保护参数或生成/扩读受限实验载荷。后继按既有接口推进，不循环以缺少实现禁止必要实现。
2. H、T_delay、B_CAL、B_max、B*、P_active、density N保持原含义且UNASSIGNED，不赋数值、范围或默认值；纯符号证明条件不作实验赋值。35–38/Q-CAL/Q-CONFIRM科研/结果载荷禁读；实际公开或本地map/scen/config/agent/task/delay/result正文和地图图像也受限。唯一输入例外是已完成L23固定四类首配置及引用的有限只读静态核验，不扩大或重做。具名源码/原文/许可/parser/库头静态核验可以继续。
3. 已冻结候选、已完成报告、提示和原回执保留字节，包括52/52R1、69–72、固定73及73R1–R4，不向52加sidecar；实质修复另立后继。73A3、本入口、工作记忆、导师说明可更新。删除授权只针对确认误导的旧交接/工作记忆，不等于删除科研证据或恢复旧失败路线。
4. `/home/lyh/桌面/智能仓机器人分布式调度_文献备份`永久只读。仅既获准的`/home/lyh/桌面/MAPF_实验前必读论文_20260909`可在必读材料变化时更新；PDF不入Git。新工件写研究目录，编辑用apply_patch。
5. shell每段前缀rtk，精确内容用rtk proxy；仅仓库实际有.codegraph时先用CodeGraph，不创建/重建索引。不绕过沙箱、审批拒绝或登录限制，不向外部人员发消息。
6. 用户已授权既有仓库`LYHrmer/MAPF_PIED_MDDR_RESEARCH`的精确文档同步。2026-09-14根实际GitHub API核该仓库为公开（`private=false`），与原“私有”记录不一致；含未发表主稿的本次七文件更新先准备本地提交，公开推送范围待确认，不自行更改仓库可见性。先核实际工作树/远端，只暂存核过路径；不add .、不上传整个目录/受限材料、不跑hook、不改全局Git设置、不发release。历史提交号不是当前状态。
7. Claude C31取消，C32–C43及C45均已终态，不轮询旧句柄。C36–38无完整交付后的Codex接手代码不冒称Opus成果；C39–41及C43有完整Opus源码，C42截断后由Codex完成并实测。C44启动工具被中止，未返回CLI session、RAW或模型代码，不是provider推理失败或Opus交付，MemoryAdapter由Codex完成。C45实际CLI退出0，Opus头文件与Codex修正/测试/README为混合交付。一次性额度等待已于2026-09-12 16:37 UTC结束，不重设。已证本地代理网络在沙箱不可用，后续沿获准require_escalated路径，避免重复沙箱失败；不绕过实际审批或改共享provider。保原RAW及终态；增量、状态或模型请求标签不冒充完整交付/上游身份认证，thinking只统计而不输出。
8. 历史51失败链、失落69L1/69E1、73P7/73L7/73C2及所有终态咨询按原记录处理，不因旧文件写“运行中”重启。先核活句柄和实际工件，缺回执不算完成；有新证据的不同具体工作可继续。

## 历史材料与视频

三份误导性旧HANDOFF已按用户授权删除，约束收拢于本页。旧报告对它们的引用沿[清理前提交](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/0153a15e4f059a567de169716985444cca86ec9d)查历史，不恢复为现行指令。旧[72R4](../72R4_THREE_REVIEW_ROOT_SYNTHESIS_AND_SUCCESSOR_REQUIREMENTS_20260907.md)的G6 FAIL属于72，不覆盖最新73R4。

[视频建议V1](../73V1_BILIBILI_RESEARCH_QUALITY_AND_EFFICIENCY_GUIDANCE_20260912.md)只有官方简介/章节，实际画面、语音和字幕读取量均为零，不能说已观看。项目采用的有限问题分工、强对照、贡献/反证表及减少重复咨询是独立判断，不归为未核视频观点。
