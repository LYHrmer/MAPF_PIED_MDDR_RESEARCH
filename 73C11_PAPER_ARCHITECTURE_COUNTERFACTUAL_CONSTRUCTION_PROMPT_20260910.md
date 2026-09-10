# 73C11：已读论文的论证架构与反事实实验建设题

任务身份：2026-09-10；新有界建设任务，不是旧 C9/C10 重试；NO-SKILL / CONSTRUCTIVE / NONBALLOT。只能阅读本提示，不调用工具、文件、网络、任何 skill/slash/MCP，不生成代码、伪代码、配置、实验载荷或结果，不为保护参数赋值、范围或默认值。当前 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT；2 PASS / 3 UNKNOWN / 1 FAIL 未改变。不要建议投稿去向，用户要求先设计闭合后评估。

根稿身份：73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md，SHA256 0beccea730aced26203406f8ffa69f5ffa93247f80cec64f00ec9de265065965，155562 bytes / 531 LF，未固定未审。提供者已全文读该稿；本题仅给架构所需事实，不要求你复核未提供的证明。

## A. 提供者亲读的一手论文证据（四篇非 PIE-D 完整主文，另含 PIE-D 锚点，非摘要代读）

1. Li / Tinka / Kiesel / Durham / Kumar / Koenig，Lifelong Multi-Agent Path Finding in Large-Scale Warehouses，AAAI2021，DOI10.1609/aaai.v35i13.17344；合法作者全文 https://arxiv.org/pdf/2005.07371v2。以不断新派目标、单位离散动作的窗口求解为问题，分开重规划周期与冲突检查范围，组合多种 MAPF 求解器。正文 §4.3 提供短窗口停滞反例及增加窗口的补救，同时承认方法不完整；§5 分仓储地图、求解器、窗口比较吞吐与每次调用运行时长。holding-endpoint/reserving-dummy-path 基线有其领域前提。重规划较贵仍可吞吐更高。超时在表中明示；吞吐的离散步分母和调用时间分开，不是本研究全费用共同世界钟。用途：学习模块贡献与运行代价分开论证，不继承其完备性或任务设定。

2. Chen / Harabor / Li / Stuckey，Traffic Flow Optimisation for Lifelong Multi-Agent Path Finding，AAAI2024，DOI10.1609/aaai.v38i18.30054；官方全文 https://ojs.aaai.org/index.php/AAAI/article/download/30054/31856。以最短路拥堵为问题，构造避免逆向流与拥堵的引导路径，并结合 PIBT/LaCAM。实验分别给吞吐、逐步响应时长、随时间变化的初始化与引导收益；比较引导代价形式、路径松弛和懒初始化等。部分地图/规模有超时或引导质量与求解能力取舍。Table2 的团队规模从先前图中峰值选择；single-shot 解成本只在共同求解成功者上比较且另报成功数。这是论文实际口径，不能移植为本研究运行后筛选许可。其队列/消息字节/可信采样费用未形成我们的全费用模型。

3. 仅作项目已读锚点、不占四篇非 PIE-D 名额：Zhang / Chen / Harabor / Le Bodic / Stuckey，Concurrent Planning and Execution in Lifelong Multi-Agent Path Finding with Delay Probabilities，AAAI2025，DOI10.1609/aaai.v39i22.34506；官方全文 https://ojs.aaai.org/index.php/AAAI/article/view/34506/36661。将已提交执行和未提交规划失同步分开，组合执行政策与重规划策略，沿旧路径引导重规划。实验先做策略组合及有无引导，再与即时延迟反馈 PIBT 和等待 commit cut 的 PIE 适配比较。Table1 的重规划成本不包含路径改善，解成本只含成功重规划；最大规模可因超时失去优势。随机 no-start/持续延迟不是真实横向跟踪偏差；该文采用的 Hönig 相关基线不自动等同原完整 H19。用途：组合兼容性、强机制对照和失败解释结构，不借其结论证明当前新域成功。

4. Hönig / Kiesel / Tinka / Durham / Ayanian，Persistent and Robust Execution of MAPF Schedules in Warehouses，IEEE RA-L2019，DOI10.1109/LRA.2019.2894217；合法作者接受稿 https://whoenig.github.io/publications/2019_RA-L_Hoenig.pdf。执行 ADG 依赖，构造闭合 commit cut，使新规划与旧动作继续执行相接。假设不显著偏离路径、动作最终结束和及时完成报告；正文也排除需要精确同步的循环动作。实验用实时模拟的规划/剩余动作时间线、站点利用率、混合现实扰动和同步执行基线支撑持续/鲁棒执行。它的实时费用诚实强于冻结物理的单次规划计时，但没有我们的逐角色全消息费用表；同步基线把多项机制一起换了，不能隔离某项观测选择的效应。用途：系统证据与局部机制证据分开，承认物理域和贡献边界。

5. Zhang / Chen / Harabor / Le Bodic / Stuckey，Planning and Execution in Multi-Agent Path Finding: Models and Algorithms，ICAPS2024 Main Track，DOI10.1609/icaps.v34i1.31534；作者团队正式版式全文 https://pathfinding.ai/pdf/zchls-icaps24-pie.pdf，9页。原 PIE 从规划等待也应计入到达代价的失配出发，分开单次 SGAT 与 lifelong 吞吐；组合快速可行解和并行改善，并分别研究承诺长度、新目标处理和失败修复。正文明确完美执行、免费传送动作；实验先比较达到同解质量再执行的离线参照、初始规划和承诺长度，再做 lifelong 策略表及 RHCR/无改善 LaCAM 对照。Table1 标记每次初始求解都失败而仅有部分解的情况；规模扩大可由策略优势转为退化。Table2 按图中表现选每图最佳承诺长度，不能据此给我们的保护参数取值或在主数据上择优。它把规划时长带入执行目标，但没有关闭逐消息/观测/全初始化费用。用途：先明确目标失配，再让组件比较逐项回答原因；单次到达改善不代替长期服务收益。

## B. 当前研究的必要语义

问题：保留固定 PIE-D 原 MOVE 提议，面对实体尺寸和真实横向跟踪偏差，付费买可信进度，安全退休已不再需要的空间，是否增加全窗口真实任务服务。不能把随机延迟改名误差；共享稳健控制对所有比较臂相同。当前 GROUP_PREFIX 允许原边单调累计 cap、有限组准入/围栏、原终点证明与付费退栏，无绕路/伪目标；纯 D 只选公共阻塞分数最大者，R 为合理轮询。D/R 都有同样的前缀、查询能力和源历史策略 ALWAYS_ADVANCE / FAIL_STOP_SOURCE。共同源修复收益不归 D；accepted-only 回滚后端不合格，不能偷偷加作免费对照。

唯一确认主量：固定公共来源 roster / 权重 / 评价窗口下 NATURAL 的 D-S 减 R-S，S 表示凭付费可信证据退休。另必报 D-S 减 E0；E0 同平台/控制/终点推送等能力但不买途中 POSITION，不做无用途索引。D 胜 R 而输 E0 只支持既定查询制度内选择改良。F_cap 保留已授资源至原 END，是次要释放因子；它并非初始就占整边的 WHOLE_EDGE。STRICT、S/F_cap、G/N、前缀/整边是预列机制比较，不择显著改主量。

所有应用 INIT / 预处理 / 成功与失败查询 / 原源工作 / 控制与协议工作均按实际收费；合法待命世界从 t=0 就存在，软件未就绪可 HOLD 且可能合法服务，不能自动给零。主分母是事前 E；source failure、合法超时及围栏锁死均留 roster，有可信服务前缀才有分数，缺日志不能填零。动态映射/源语义/评分不闭则不作数值因果推断。各 block 创新根独立是显式条件，块内臂相关可接受，不能以随机换运行次序证明独立。

已有结构性正/负见证只说明某些条件下可退休、可启动、可在事前任务服务行多服务；全窗口其他服务/成本可能抵销。环状组可说明 E0 与 F_cap 在特定资源制度下停滞，但不是公共 R0 实际输出实例，不外推为大规模效应。精度、源后端、素材许可链及 H19 外部组合未闭。H19 原样/守卫共同适配必须分名，不能靠弱化原法或删外部域使内部方法获胜。当前未生成任何实验结果。

## C. 请交付

在上述已读证据和当前定义内，给一份精炼但可审核的论文论证架构，说明主文与附录如何分工，哪些结果能够或不能够支持哪些主张。独立找一个最危险的归因错误或反事实缺口，提供一个可直接预注册的修复；最多提出两项方法/证据改良，不扩充成庞大新项目，不放弃强 R / E0 / 已发表外部比较。指出你的建议是否其实已在当前定义中，新增的是方法还是证据组织。任何建议若依赖未闭接口、改变目标量或新增费用，要明确说出，不能借写作结构掩盖。

不要预言阳性结果或声称已证明新颖性。给一个即便未来 D-R 为正仍不能支持广泛主张的具体反例情形，并明确在文稿中如何报告。仅做建设性分析，不给 PASS/GO。结尾单独一行 END-C11。
