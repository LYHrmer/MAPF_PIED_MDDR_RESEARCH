# MAPF 项目当前入口

更新：2026-09-14。**固定73的完整顺序审查和根综合已经结束，参数化设计规格接受；当前进入限定静态候选资格准备。完整实验前目标未完成，仍为HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。**

本页是导航和操作约束的唯一入口。按当前缺口读取对应章节与直接证据，不递归全文阅读历史交接、账本和咨询；已有正式审查不因换窗口重新启动。

## 当前裁决、方案和证据

- [73R4最新根裁决](../73R4_ROOT_DESIGN_ACCEPTANCE_20260914.md)：前两路各自根直接分析、第三路完整收件及全部意见综合完成。当前六门为2项限域PASS、4项UNKNOWN；参数化设计接受不替实际源/后端/全来源/外部复现资格，也不等于整个实验前目标完成。
- [固定73科学规格](../73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md)：SHA256 `b64f5b555034655b2676226d051a70c03aab3679d67c00bc334fb588c4811a8a`，315128 bytes / 971 LF。自2026-09-14起保持原字节；文件名DRAFT、页内NOT-REVIEWED和旧时态是固定时点记录，实际阶段以73R4为准。
- [导师汇报一页说明](../RESEARCH_BRIEF_FOR_ADVISOR.md)：研究问题、数学表达、方法和结果边界，面向汇报，不替科学规格。
- [本窗口证据/决策索引73A3](../73A3_DESIGN_VERIFICATION_SESSION_20260912.md)：只按具体问题查阅；早期WORKING、任务句柄、SHA和预算状态是历史，不能覆盖实际文件和活工具。
- 完整报告：[73R1科研导师](../73R1_RESEARCH_MENTOR_FULL_REVIEW_20260914.md)、[73R2 Nature](../73R2_NATURE_FULL_REVIEW_20260914.md)、[73R3无skill独立逻辑](../73R3_INDEPENDENT_LOGIC_FULL_REVIEW_20260914.md)。三路均实际gpt-6-astra/ultra且完整终态，严格按各路后根分析的顺序启动；Nature为一个代理三侧重，第三路未用skill/未读他路。第二路运输中断已从原阅读恢复，无待轮询或待重开审查。原任务保留：[R1](../73R1_RESEARCH_MENTOR_FULL_REVIEW_PROMPT_20260914.md)、[R2](../73R2_NATURE_FULL_REVIEW_PROMPT_20260914.md)、[R3](../73R3_INDEPENDENT_LOGIC_FULL_REVIEW_PROMPT_20260914.md)。

明确基于Zhang等[PIE-D（AAAI2025）](https://ojs.aaai.org/index.php/AAAI/article/view/34506)改进，当前复用作者LACAM-only及承诺/未来路径切分，经明示共同修订，不等于原论文完整PIBT-D＋A。研究真实横向跟踪偏差、有尺寸实体、同原MOVE的GROUP_PREFIX、付费可信进度与空间退休；普通错误反馈、计算通信等待和no-start分开。主比较为NATURAL的D-S−强轮询R-S，D-S−E0必报；内部R/E0及释放消融不冒称文献基线。H19E0/H19R-S是必需的外部系统候选，尚未完成忠实性/共同域资格。P_model计确定基本步，宿主/world CPU、耗时和内存另报，不保证正效应或实机速度，不删失败。

固定R0为`YueZhang-studyuse/LMAPF-delay@0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`；完整PIE-D作者候选为`improve_morereveal@74cfba3c81a0c165c2e7044dea6fd4dee8ddf415`，停止重搜分支。原字节检查、论文规则复现和共同适配分轨；A按(a+b,a)、PIBT-D按delay优先及窗口计数已有规则证据。H19的ECBS组件固定`whoenig/libMultiRobotPlanning@4c75fa20c435c440d8b6bd6dc81668ddc7296ba0`，不是作者整套系统；首匹配/图闭包/源完成GC等已有合同，不重新发明。MCP归属Ma等AAAI2017及TIP库仿真实现，非Causal-PIBT。

DARI已淘汰，旧编号计划不恢复为待办。目标SCI二区/三区，JCR或中科院均可；大规模LMAPF主要是仿真，两台LIMO仅可选补充。既有纯仿真期刊先例不等于录用保证，无硬件不设为当前前置。

## 当前必要工作与分工

1. **限定静态候选资格。** 复用73 §8/9的安装、AA两分支、缓存、字段界、AUTH及参考例程表，只补尚缺的跨job归纳、具体表示/布局/导入与同一X/X_0/A的FIT相容证书。原`astra_ultra_paid_service_closure`正在复用前次构造补FIT，不是新增审查；尚无完整结果时不得计非空域已证。新核GNU11.4.0首轮标准hash分支和原fresh时限设置见73A3，实际二进制对应仍分层。R3-06已由根核入桶前连通分量过滤，原B_bucket≤V_comp无需改成V或强制全图连通。
2. **来源与外部共同域。** [L23](../73L23_LIMITED_PUBLIC_INPUT_STATIC_VERIFICATION_20260912.md)及[L23A](../73L23A_STATIC_INPUT_PARSER_CONTRACT_CHECK_20260912.md)四类首配置和13引用的基础有限静态核验已完成，不重做。完整selector/alias/全潜在ACTUATOR有效delay/WORLD/服务区和主roster仍须资格；已有研究用途依据，固定版本覆盖与第三方再分发范围分别处理。PIE-D/H19现成矩阵在§10、来源矩阵在§11/73L20/73L22，按实际缺项补证，不重搜整套资料。
3. **准入后的实现与验证。** 用户新分工：GPT-6-Astra Ultra负责最难理论、路线及跨模块取舍；Claude Opus主要承担已获阶段授权且规格明确的代码实现、修复、调试与复现适配。根拆包、核接口/差异及真实检查再整合；每包明确文件、输入输出、禁止改动、验收和停止条件，独立修改范围。不让模型无新证据往返审查；W01–99按共同不变量组织覆盖，复用驱动，当前仍全为NOT_IMPLEMENTED/NOT_RUN。
4. **完整实验前交付。** 仍包括预注册、执行/验证/分析工具冻结、结果留空的论文实验前稿、引用/主张/图表规划、复现包和最终逐项验收。已有至少十二项正文层来源和四份期刊全文历史阅读记录已定位，参见73A3；不是本次重新亲读，也不关闭未读近邻对强新颖性的限制。不得以本轮设计接受或文件整理代替全部目标。

不新增阳性结果、Nature广泛影响力、硬件或逐编译指令/全库普查门。已定义接口的实现后符合性在对应阶段验证，不能循环要求先有实现才准实现；实际承重语义矛盾也不能推给未来测试。没有新反例或科学规格变更时，不重开固定73的完整审查。

## 有效操作边界

1. 当前仅设计/已授权静态证据及文档工作。不实现、不写实现伪代码、不构建或运行研究测试/算法/RNG/仿真、不调参或控制机器人；不生成实验O、seed、tape、manifest、具体配置/场景或结果。相应静态准入后才进入实现和资格验证，不因旧计划提前开始。
2. H、T_delay、B_CAL、B_max、B*、P_active、density N保持原含义且UNASSIGNED，不赋数值、范围或默认值；纯符号证明条件不作实验赋值。35–38/Q-CAL/Q-CONFIRM科研/结果载荷禁读；实际公开或本地map/scen/config/agent/task/delay/result正文和地图图像也受限。唯一输入例外是已完成L23固定四类首配置及引用的有限只读静态核验，不扩大或重做。具名源码/原文/许可/parser/库头静态核验可以继续。
3. 已冻结候选、已完成报告、提示和原回执保留字节，包括52/52R1、69–72、固定73及73R1–R4，不向52加sidecar；实质修复另立后继。73A3、本入口、工作记忆、导师说明可更新。删除授权只针对确认误导的旧交接/工作记忆，不等于删除科研证据或恢复旧失败路线。
4. `/home/lyh/桌面/智能仓机器人分布式调度_文献备份`永久只读。仅既获准的`/home/lyh/桌面/MAPF_实验前必读论文_20260909`可在必读材料变化时更新；PDF不入Git。新工件写研究目录，编辑用apply_patch。
5. shell每段前缀rtk，精确内容用rtk proxy；仅仓库实际有.codegraph时先用CodeGraph，不创建/重建索引。不绕过沙箱、审批拒绝或登录限制，不向外部人员发消息。
6. 用户已授权既有私有仓库`LYHrmer/MAPF_PIED_MDDR_RESEARCH`的精确文档同步。先核实际工作树/远端，只暂存核过路径；不add .、不上传整个目录/受限材料、不跑hook、不改全局Git设置、不发release。历史提交号不是当前状态。
7. Claude C31已取消无正文，C32–C35均完整终态；不再轮询。一次性额度等待截止2026-09-12 16:37 UTC已过，不重新顺延；只实际完整终态及正文算收件，核实际模型并保原回执。当前代码任务仍须对应阶段准入，调用次数不是收益。
8. 历史51失败链、失落69L1/69E1、73P7/73L7/73C2及所有终态咨询按原记录处理，不因旧文件写“运行中”重启。先核活句柄和实际工件，缺回执不算完成；有新证据的不同具体工作可继续。

## 历史材料与视频

三份误导性旧HANDOFF已按用户授权删除，约束收拢于本页。旧报告对它们的引用沿[清理前提交](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/0153a15e4f059a567de169716985444cca86ec9d)查历史，不恢复为现行指令。旧[72R4](../72R4_THREE_REVIEW_ROOT_SYNTHESIS_AND_SUCCESSOR_REQUIREMENTS_20260907.md)的G6 FAIL属于72，不覆盖最新73R4。

[视频建议V1](../73V1_BILIBILI_RESEARCH_QUALITY_AND_EFFICIENCY_GUIDANCE_20260912.md)只有官方简介/章节，实际画面、语音和字幕读取量均为零，不能说已观看。项目采用的有限问题分工、强对照、贡献/反证表及减少重复咨询是独立判断，不归为未核视频观点。
