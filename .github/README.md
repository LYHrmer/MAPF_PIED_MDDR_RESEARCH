# 当前分支：学习型进度查询探索

本页属于 `explore/learned-query`，当前工作见[分支入口](../README.md)和[学习探索目录](../exploration/learned_query/README.md)。同仓库的 [main](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/main) 保留主研究线，[explore/error-aware-guidance](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/error-aware-guidance) 单独探索误差相关路径代价。三者不合并，结果按分支和验证范围区分。

以下为分叉时继承的主线资料快照，其中旧“未运行/等待许可”状态不代表主线最新进展；最新主线以 [main 入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/.github/README.md) 为准。

# 继承的主线入口快照

更新：2026-09-21。**原生机制闭环与独立B1费用反馈此前分别通过。C/N/E三完整ELF、双域loader、固定站点脚本和唯一世界驱动现已静态装配并链接；17个发布进口对应8张实际ELF图，含全部条件边与已绑定间接目标。完整查询仍未运行，无整次成本或吞吐结果，Compute供给是否足够亦未证明，见Q2 §59。55篇开题综述及SCI二区/三区科研导师独立评估已在桌面交付：工程量充分，投稿证据不足；三区有条件潜力，二区仍需更强机制与推广证据。只实现/静态检查的边界、主稿原修改和冻结证据保持。**

本页是导航和操作约束的唯一入口。按当前缺口读取对应章节与直接证据，不递归全文阅读历史交接、账本和咨询；已有正式审查不因换窗口重新启动。

桌面55篇综述已完成第二版：强化近邻统一比较、证据→退休→准入→执行→任务表现的区分、现有SRDC边界及后续优先次序；科研导师技能独立审查的八项意见已落实并复核。新版综述/汇报/提纲/审查Word及优化前备份均保存在本机，选定PDF哈希未变。另按用户全流程图片整理项目内技能调用方案，主任务按阶段交付、独立评审定点复核；没有改技能源码、冻结方案或运行边界。详细文献进度见GITHUB_PROGRESS，不重启目标或全文审查。

自动目标“完整查询闭环”现为**受阻（blocked）**：候选实现和静态检查已完成，尚缺首次完整运行与实际核账；用户“先只完成实现和静态检查”的限制仍有效。连续三轮确认同一阻塞后停止自动续轮，保留工件及未完成项；没有运行、扩供给或修改保护参数。

[公开进度一页表](../GITHUB_PROGRESS.md)及[导师汇报说明](../RESEARCH_BRIEF_FOR_ADVISOR.md)可直接在GitHub阅读。[本地详细准备表](../implementation_binding_evidence/SCALE_RUN_READINESS_20260920.md)和下文implementation路径指向尚未随本次进度同步上传的本地工件。

## 当前裁决、方案和证据

- Q2 §60接续完整查询的[具体范围](../implementation_binding_evidence/FULL_QUERY_CHAIN_SCOPE_20260921.md)和[本批冷缓存定点证据](../implementation_binding_evidence/FULL_QUERY_NUMERIC_COLD_CACHE_STATIC_20260921.md)。原核账工具已增加显式full-query模式，AST/旧默认模式静态兼容检查通过；一次Opus超时无源码，由Codex完成增量，未执行核账器。首次冷缓存触发仍UNKNOWN；若在C setup首次成功完成，该分支仅EH扫描下界203134976步已超过原窗口53477376步。不能套用旧失败，也不由未知推为可通过；不扩成全库静态审查或增加供给。用户另明确中科院/JCR“两种都考虑”，桌面评估已补双口径、年份/类别分列说明。

- Q2 §59记录[世界驱动静态装配](../implementation_binding_evidence/FULL_QUERY_WORLD_STATIC_20260921.md)与[普通发布图资格](../implementation_binding_evidence/FULL_QUERY_PUBLICATION_STATIC_20260921.md)，均为本机工件。固定流程接原B cap/RUN、四终态付费清退、Collector与下一choose；宿主严格编译链接通过，未执行。Publication最大整行静态阈值1262低于既定每行1048576，但不能推出整个Query或冷启动可负担。没有临时补供给或将节点数当费用。

- Q2 §58记录开题文献交付：A空间误差/安全执行20篇、B信息滞后/付费更新20篇、C误差与延迟交叉及边界对照8篇、D直接MAPF近邻7篇；55份选定全文及阅读卡已归档，版本不重复计数。综合结论是有条件值得继续，但昂贵观测、中心选择对象、联合误差/延迟和资源互斥各有近邻，贡献须具体落在安全释放证据、阻塞依赖与实际查询净收益。一个高度相关候选尚未取得全文，未计入55篇，不宣称穷尽查新或首次。PDF与阅读包只在本机桌面保存。

- Q2 §57记录三完整guest与ELF后继：[本机静态证据](../implementation_binding_evidence/FULL_QUERY_ELF_STATIC_20260921.md)。C沿原Position根接真实POSITION提交、原后车需求放行准备、四终态Collector、收据和下一选择；N双向opaque转发及E快照证书生产接实际Query账本。RA终态逐字回收与真实movement发布边界已实现。三ELF已链接，实际kernel静态闭包及新loader检查通过；普通业务发布图、原MOVE的实际world接续和全链运行尚未验证。实际Claude Opus完整交付N业务体，归属与根集成修正分开保留。用户新要求的文献综述不改变实验运行或参数边界。

- Q2 §56为上一后继：[站点与中心顺序实现](../implementation_binding_evidence/FULL_QUERY_STATION_SUCCESSOR_20260921.md)及[源码入口](../implementation/pie_station_query/README.md)仍为本地工件。站点绑定真实owner/job/lane、独立计算与发布费用SOURCE及真实检查点；C请求用Selection、E与N用Query。已提交outbox持有实际封存请求，N付费完整复制并回收原件；真实CAPTURE冻结当前物理根、guest按发生历史精确重建。CenterQueryFlow沿同一bridge接至实际Collector/报价安装与下一选择。组合静态入口通过，未运行。此时列出的guest与终态回收缺口已有§57后继，实际world/发布图和全链运行仍未完成。新Opus Copy完整交付，首次网络失败和授权重试成功分开保留。

- Q2 §55记录上一后继：[完整查询实现进度](../implementation_binding_evidence/FULL_QUERY_IMPLEMENTATION_PROGRESS_20260921.md)。中心使用实际已发布根/首次成功事实，将真实准入终态准备到Collector，并把收据安装到原Position根；发布SOURCE以实际指令收费。请求和COST使用原INIT一次性安装的两个固定上下文，原COST镜像不能替代新十二字kernel登记。后继更新以§56为准，不由静态源码宣称完整闭环或规模就绪；复用同一组合编译入口，不新增完整审查或孤立测试前置。

- Q2 §53–54为本次接续：[三站点接入源码](../implementation/pie_station_query/README.md)、[具体工件与运行边界](../implementation_binding_evidence/FIXED_COST_CHAIN_SCOPE_20260921.md)、[实际Opus交付](../implementation_binding_evidence/OPUS_COST_CHAIN_AUDITOR_RECEIPT_20260921.md)。这些路径仍为本机工件。COST部分只形成N→E→C的终态接入，不能代替完整C→N→E→N→C查询。已有真实关闭段经付费SOURCE进入账本，原issuer/收件范围经付费通道保留，C端实际guest准入产生Collector所需能力；以上新路径只有静态证据。用户选择仅实现/静态检查后，本轮不执行候选命令，不重复询问。另已核Robust MADER原文：分档固定注入延迟支持敏感性设计，不是随机抽样实验；当前不生成噪声或赋实验参数。

- [本轮交付记录](../implementation_binding_evidence/IMPLEMENTATION_SESSION_20260919.md)、[查询算法合同](../implementation_binding_evidence/query_scheduler_contract_20260919.md)、[查询源码与检查](../implementation/pie_query/README.md)：直接接续所列接口，不重读全部历史。Q2 §29–31记录新增检查及真实归属；§25时点的FLINT六回调缺口已由§29关闭，全局C/C++入口和完整业务运行仍待接入。独立文献子任务围绕付费观测、依赖释放与互补收益检索，不恢复完整审查或新增流程前置。

- [后继交付与验证记录](../implementation_binding_evidence/POSITION_COMMIT_AND_METHOD_20260920.md)、[组合提交接口](../implementation/pie_position_commit/README.md)、[方法补充稿](../implementation_binding_evidence/QUERY_METHOD_PAPER_SUPPLEMENT_20260920.md)、[定向文献启发](../implementation_binding_evidence/LITERATURE_INSPIRATION_20260920.md)：Q2 §32–33接续原子发布与局部写作修正。主稿原修改已逐字备份，修正依据/范围见[勘误记录](../implementation_binding_evidence/MANUSCRIPT_LOCAL_CORRECTIONS_20260920.md)。此后继尚无实际服务或规模实验结果，不因静态编译关闭真实来源/成本缺口。

- Q2 §34–35记录[已授权有限运行](../implementation_binding_evidence/QUERY_POSITION_NATIVE_SCOPE_20260920.md)、零历时修复、[费用收据接法](../implementation_binding_evidence/QUERY_RECEIPT_BINDING_20260920.md)及[分配运行入口](../implementation/pie_guest_runtime/README.md)。两份native测试已经明确获准，不再次询问同范围修复复测；新runtime ELF没有运行资格。成本报告单列全费，不能把STRICT整行供给当查询业务成本。

- Q2 §36记录[费用核心交付](../implementation_binding_evidence/QUERY_COST_CORE_20260920.md)、[源段/精确汇总接口](../implementation/pie_query_cost/README.md)和[一次性启动接口](../implementation/pie_guest_startup/README.md)。费用夹具随后已在新授权下通过，见§38；真实收据服务未被结构体和求和替代，producer载体不能递归自计。[启动后继](../implementation_binding_evidence/GUEST_STARTUP_BINDING_20260920.md)限当前真实路径，不扩大到全库普查。

- Q2 §37：新的[显式数值启动镜像](../implementation/pie_guest_startup/image/README.md)及TLS/TCB/DTV准备器已接到固定ELF提取和Initializer/B1驱动；后继实际结果见§38，不重做旧组件或模拟整个Linux。另已接纳[成本终态线格式与责任树协议](../implementation_binding_evidence/QUERY_COST_WIRE_SPEC_20260920.md)用于独立候选，COST_DOMAIN_V1是明示的窄权限扩展，真实AUTH/站点接入仍未完成。

- Q2 §38记录[两项有限运行结果](../implementation_binding_evidence/FINITE_NUMERIC_AND_COST_RESULTS_20260920.md)：费用核心通过，数值guest在NATURAL耗尽固定供给、STRICT未开始；[冷缓存成本诊断](../implementation_binding_evidence/NUMERIC_STARTUP_ALLOCATION_COST_20260920.md)给出仅used读取即203,134,976步的保守下界，超过67,100,672步整表。保留失败和原profile，不扩供给或以O2盲重跑。实际Opus交付的[终态codec](../implementation/pie_query_cost_wire/README.md)通过主机/RV64静态编译，其新native夹具未运行。

- Q2 §39：[本地责任账本](../implementation/pie_query_cost_local/README.md)已实现，真实Opus核心加Codex组合接缝；主机/RV64严格静态编译通过，未运行。它把开放计费段、child预留/发布、引用清理和终态守卫落实为私有准备/原子根交换，支持同次发布多个责任变化；并未接通真实AUTH或站点。下一步是中心Collector、实际已发布根/成功POSITION事实和付费来源交付。

- Q2 §40钉住[Collector实现规格](../implementation_binding_evidence/QUERY_COLLECTOR_IMPLEMENTATION_SPEC_20260920.md)和[三类来源接缝](../implementation_binding_evidence/QUERY_COLLECTOR_ADMISSION_BINDING_20260920.md)，明确由真实中心首次成功提交冻结唯一事实，后续合法副本全费而不替换事实。PositionCommit已补[组合预检/无异常提交](../implementation_binding_evidence/POSITION_COMMIT_PREFLIGHT_20260920.md)，两平台静态检查及原已授权序列复测通过；完整中心业务writer和AUTH仍未实现。

- Q2 §41：[中心Collector](../implementation/pie_query_cost_collector/README.md)已实现完整责任图检查、家族封口、真实actual费用汇总和报价安装准备，严格主机/RV64静态编译通过，未运行。一次Opus调用超时且无可用源码，后由Astra/Codex完成，[原始归属与检查回执](../implementation_binding_evidence/opus_cost_collector_receipt_20260920.json)已保留。三类来源接口仍待真实中心writer/AUTH签发和付费站点接入，不以私有构造或静态编译代替业务验证。

- Q2 §42：[收据组合安装](../implementation/pie_query_receipt_install/README.md)已将Collector实际算术输出与PositionCommit内Scheduler接成单writer双根事务，严格主机/RV64静态编译通过，未运行。真实Opus完整交付，Codex修正静态夹具及明确上下文边界，[调用与哈希回执](../implementation_binding_evidence/opus_receipt_install_terminal_20260920.json)保留。成本信封初次封存采用固定`{E,C}`收件范围，仍沿原`N→E→C`付费通道，不新增外套或直连。下一来源实现接B1/MemoryAdapter的实际受保护存储与付费接收，当前还没有AUTH或真实中心writer。

- Q2 §43：[受保护存储](../implementation/pie_auth_memory/README.md)已实现真实MemoryAdapter保护后端与四个freestanding guest字循环，core主机/RV64对象及后端主机C++20静态编译通过；额外保护表计入R_aux，tail在原子操作最终写值处保护。Opus限时无源码后由Astra/Codex完成，不重试。六页固定[native/B1夹具](../implementation_binding_evidence/AUTH_MEMORY_NATIVE_SCOPE_20260920.md)随后获明确授权并[实际通过265项断言](../implementation_binding_evidence/AUTH_MEMORY_NATIVE_RESULTS_20260920.md)，exit0、无修复或重跑。真实可信worker、AUTH签发、付费交付和中心writer仍待接入；新kernel/worker运行不在本次授权中。

- Q2 §44：[持久可信worker](../implementation/pie_auth_worker/README.md)已把额外CPU付费初始化、固定编译kernel、私有code/stack保护及原B1参数/返回接口接成源码路径，host实际组合与RV64对象静态编译通过。[交付记录](../implementation_binding_evidence/AUTH_WORKER_STATIC_DELIVERY_20260920.md)保留一次完整Opus CPU初始化器及Codex必要修正。普通ECALL停在无后续访存的既有B5边界，kernel停到下一PULL才恢复普通执行；没有免费寄存器快照。对象尚未接成实际镜像或运行，真实AUTH来源、角色业务和站点交付仍未完成。

- Q2 §45：[编译worker固定镜像及驱动](../implementation_binding_evidence/AUTH_WORKER_FINITE_SCOPE_20260920.md)已实际链接，随后获得新增运行授权并[首次通过](../implementation_binding_evidence/AUTH_WORKER_FINITE_RESULTS_20260920.md)：11页/32槽、真实Context与六次kernel请求，两制度各83969步actual；NATURAL收费83969、STRICT收费393216，每制度27977次暂停检查，逐行收据独立复算一致。无需修复或重跑；§44的“未链接/未运行”仅描述当时阶段。真实AUTH/中心writer和原MOVE闭环仍待接通。

- Q2 §46：[中心本地writer事务](../implementation/pie_center_writer/README.md)已实现完整outbox存储/不透明通道待办、SELECT与Position根组合发布，以及q不变仍可成立的唯一first_success锁存；实际能力接现有Collector，旧收据安装直接复用。严格host/RV64静态编译通过，未运行；生产CenterService、AUTH签发、通道复制/登记与付费发布仍未接通。[本包绑定](../implementation_binding_evidence/CENTER_WRITER_BINDING_SPEC_20260920.md)明确源码已闭与真实入口仍缺的范围，不以private构造或字节指针证明AUTH。

- Q2 §47：[比较与消融登记草案](../implementation_binding_evidence/D_SRDC_COMPARISON_BINDING_DRAFT_20260920.md)已将新候选限定为共同协议下SRDC/RR/COUNT及work-only、wait-only、w=1，E0单列、正式臂不替换。[六选择器源码](../implementation_binding_evidence/QUERY_POLICIES_IMPLEMENTATION_20260920.md)已实际实现并通过host/RV64静态编译；COUNT沿原资源存在式计数和真实加入行解平，RR/COUNT不维护无用途SRDC图。原query/position夹具同范围回归通过；新增12组固定native程序随后获用户明确授权并[首次实际通过](../implementation_binding_evidence/QUERY_POLICIES_NATIVE_RESULTS_20260920.md)，无修复或重跑。生产来源和服务闭环仍待接入。

- [本地终态导出与封存接缝](../implementation_binding_evidence/COST_TERMINAL_EXPORT_BINDING_20260920.md)：新增固定账本的规范正文导出和逐字来源接口，保持 TerminalPrepared→外层真实发布→TerminalPublished 的顺序；worker 另接可选私有状态区。新导出仍是结构组件，生产 AUTH、真实站点计费事件与付费封存尚未接通；具体静态证据见该记录，不将旧固定运行结果套用到新路径。

- Q2 §49：[COST封存内核与worker后继](../implementation_binding_evidence/AUTH_COST_KERNEL_BINDING_20260920.md)已实现私有有限序号、Empty/Building/Sealed状态、实际逐字封存、保身份复制和擦除撤权，接入九字付费bootstrap及操作4–6。host组合和最终RV64对象编译通过；最终对象的保守栈上界为1264字节，不能沿用旧kernel的128字节。[七组固定native检查](../implementation_binding_evidence/AUTH_COST_NATIVE_RESULTS_20260920.md)随后获用户明确授权并首次实际通过，无修复或重跑。实际站点镜像/当前job准入、付费上下文安装、跨站验收与原MOVE闭环仍未接通。

- Q2 §50：[站点guest导出与实际调用接缝](../implementation_binding_evidence/STATION_COST_GUEST_BINDING_20260920.md)已将真实账本编码、Context三块分配/逐字打包、Seal/Wipe真实RV64 ECALL及B1付费参数读取接成源码；host严格检查、RV64对象与ld -r组合通过，未执行。guest不读取保护表，清理逐块保留已做前缀；标记或普通a0返回都不自动成为AUTH/发布事实。生产站点owner、当前job准入、outbox和原通道仍须接入，下一步集中贯通这些真实入口，不再以孤立native通过替代完整业务证据。

- Q2 §51：执行拥有者已统一实际INIT、两CPU、worker和调用桥的生命周期与付费推进；上下文工厂生成原INIT直接消费的Region，组合严格host静态检查通过。实际站点/job、发布及通道仍在接入，尚未运行新路径。下一步以小规模完整流程验证可运行性、机制区别和计入开销后的效果；已有检查按相关修改需要复用，不重开全面审查。

- Q2 §52：原生闭环首跑6465a7 exit0，实际退休两个阻塞资源后启动后车并完成两原MOVE；实际B1费用反馈最终c2bc27 exit0，NATURAL/STRICT各actual84，收费84/95，报价更新使选择A→B。首次owner绑定失败保留，旧算法未放宽。详细结果、复现与后继方案在本地`NEXT_CODEX_HANDOFF_20260921.md`；该文件为新终端首读入口之一。完整费用链留后继，不扩成新的全面审查。

- [73R4最新根裁决](../73R4_ROOT_DESIGN_ACCEPTANCE_20260914.md)：前两路各自根直接分析、第三路完整收件及全部意见综合完成。当前六门为2项限域PASS、4项UNKNOWN；参数化设计接受不替实际源/后端/全来源/外部复现资格，也不等于整个实验前目标完成。
- [73Q1当前静态绑定](../73Q1_STATIC_CANDIDATE_BINDINGS_20260914.md)：首轮源容量存在性、R0具体跨job统计/路径容量和P的条件来源、priorities与原uint计数、H19编号/partial focal/数值接缝已具名接纳；§4的根源码修复/静态编译包已完成。Q1可随建设更新；G3/G4/G6整体尚未通过，不回改冻结R4。
- [73Q2主方法实现绑定](../73Q2_MAIN_EXECUTION_IMPLEMENTATION_BINDINGS_20260914.md)：几何、精确数值、认证dyadic区间、参考段和同原MOVE控制器均已实现，根独立有限运行检查全部通过。控制器已核旧边界优先、BRAKE保持、原终点关闭和冻结快照；真实来源、授权、服务与完整闭环仍须接入。具体检查及范围见Q2 §9/10/12/14/15，不用测试条数代替规模证据。
- Q2 §4固定libriscv v1.20 / RV64IMA-LP64底座，B1–B7为已有接口的实现落点。B1核心/有限暂停费用检查、§19付费参数读取均完成；§11固定GNU11工具链、§16目标数值三库及fenv具名修复也已完成。§18 MemoryAdapter经根独立编译/运行48项通过、0失败（c2c188/04dde0）；§23手工SD/LD/ECALL经真实两普通页和付费a0参数/返回口，65项通过、0失败（738493/bf9478）。后者没有INIT或编译业务guest。固定binutils gitlink实际2.41，不重开选型或扩大ECBS。
- Q2 §20 guest first-fit arena核心已由根全文核并独立严格编译/有限native运行通过（fcbfe7/c05bfa）；目标交叉编译6acf73及ABI核验af24c1完成，arena目标尚未运行，其GMP/MPFR hooks后于§25完成。§21宿主记录器7项真实辅助进程检查通过（845b3b），只记录宿主开销/退出，不推导P_model或Q。
- Q2 §24付费静态镜像初始化根编译/运行通过，58项/0失败；已付48字状态仅交接为ReadyToExecute，不等于整体INIT_READY。§25 GMP/MPFR三回调到arena的native检查及目标静态链接通过，目标未运行，完整C/C++/FLINT分配闭包仍待接入。§26服务供给计量60项/0失败，实际接B1跨行暂停/返回，NATURAL/STRICT收费分开。
- Q2 §27固定无运行库的C++编译诊断已由根独立编译/运行通过（bae118/3e3fbb）：ELF→付费INIT→B1/Memory/ServerMeter链接通，两制度均初始化12769步、执行465步；全部结果/页面/逐行实际账一致，17项畸形ELF拒绝。它不运行研究或数值库业务，也不证明完整world或规模性能。§28现行加权Hoeffding数学内核的7项固定单元已由根实际运行通过（ec6427），区间向外舍入，未改变统计合同或读取研究结果。
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

1. **优先完成PIE-D误差执行主线的具体绑定。** 接续D_SRDC_v1、PositionCommit及已验收组件，沿已通过的有限组件接真实查询收据、观测核验与付费原子发布，再接已有C/C++分配入口的付费启动绑定、整体应用INIT、受限imports及来源授权、真实任务服务和站点闭环，复用73 §8/9现成合同。PositionCommit已完成源码、静态接缝和具名有限运行，不能重写为仍无原子组合实现，也不能冒称真实站点已接通。FLINT六回调已完成，不重复建设。Q1已接纳首轮源存储FIT存在性、R0跨job统计／路径容量、P的条件来源及priorities／计数语义；这些具体证据不重做，也不扩成全roster或实际二进制资格。剩余AA只补实际继续域及其它搜索／导入表示，不笼统重查所有字段。实现后符合性在实现阶段验证，不以尚无实现循环阻止已具备条件的实现。R3-06的入桶前分量过滤结论保持。
2. **来源与外部共同域。** [L23](../73L23_LIMITED_PUBLIC_INPUT_STATIC_VERIFICATION_20260912.md)及[L23A](../73L23A_STATIC_INPUT_PARSER_CONTRACT_CHECK_20260912.md)四类首配置和13引用的基础有限静态核验已完成，不重做。完整selector/alias/全潜在ACTUATOR有效delay/WORLD/服务区和主roster仍须资格；已有研究用途依据，固定版本覆盖与第三方再分发范围分别处理。PIE-D/H19现成矩阵继续复用。Q1已关闭H19整批id守卫、失败fmin来源及partial focal具体身份/计数；实际Astra Ultra的`astra_ultra_ecbs_focal_closure`亦已终态，根在Q1 §2.3选定每轮重建FOCAL/默认cost阈值及不复制handle的数据复制构造，不把抽象风险冒成已运行反例。此前`external_static_binding`两轮建设均终态，不轮询或重做。
3. **准入后的实现与验证。** GPT-6-Astra Ultra负责最难理论、路线及跨模块取舍；Claude Opus承担已获阶段授权且规格明确的代码实现、修复、调试与复现适配。C36首次网络错误、授权重试超过30分钟仍无正文后中止，两次均终态且实际模型未认证；根已接手同一ECBS包、核两处差异/固定来源并通过g++-11 C++14 -fsyntax-only实际模板实例化。原始回执和73C36_ATTEMPT_AND_ROOT_IMPLEMENTATION_RECEIPT_20260914.md、本地implementation/h19_ecbs/README.md分别保存真实调用与源码检查，不归为Claude交付。每包明确文件、输入输出、禁止改动、验收和停止条件，独立修改范围。不让模型无新证据往返审查；W01–99按共同不变量组织覆盖，复用驱动，当前研究运行验证仍未实施/运行。
4. **完整实验前交付。** 结果留空的论文正文初稿、实验章节、图表计划及四篇承重引用已形成于MANUSCRIPT_PREEXPERIMENT.md；两项写作／文献子任务均完整终态。继续补具体预注册、执行／验证／分析工具冻结、完整相关工作与复现包，并完成最终逐项验收。已有至少十二项正文层来源和四份期刊全文历史阅读记录沿73A3查阅；新四篇核验只算相关正文定点阅读，不关闭未读近邻对强新颖性的限制。不得以正文初稿或参数化设计接受代替全部目标。

不新增阳性结果、Nature广泛影响力、硬件或逐编译指令/全库普查门。已定义接口的实现后符合性在对应阶段验证，不能循环要求先有实现才准实现；实际承重语义矛盾也不能推给未来测试。没有新反例或科学规格变更时，不重开固定73的完整审查。

## 有效操作边界

1. 当前按已接受接口实施和验证。Q1 §4外部组件及Q2 §3/6/9–16/18–21/23–28已完成相应源码、构建和有限检查；不能误称仅语法，也不等于业务guest/完整world已验证。§20/25目标产物只编译/静态核验；§24完成计算启动前缀，§26完成供给计量，尚非整个应用INIT/站点。§27具名固定编译诊断guest的有限计量执行已实际通过；§28仅纯数学单元。其它未列研究规划/控制服务/业务guest/实验/RNG/仿真仍不运行，不赋保护参数或生成/扩读受限实验载荷。后继按既有接口推进，不循环以缺少实现禁止必要实现。
2. H、T_delay、B_CAL、B_max、B*、P_active、density N保持原含义且UNASSIGNED，不赋数值、范围或默认值；纯符号证明条件不作实验赋值。35–38/Q-CAL/Q-CONFIRM科研/结果载荷禁读；实际公开或本地map/scen/config/agent/task/delay/result正文和地图图像也受限。唯一输入例外是已完成L23固定四类首配置及引用的有限只读静态核验，不扩大或重做。具名源码/原文/许可/parser/库头静态核验可以继续。
3. 已冻结候选、已完成报告、提示和原回执保留字节，包括52/52R1、69–72、固定73及73R1–R4，不向52加sidecar；实质修复另立后继。73A3、本入口、工作记忆、导师说明可更新。删除授权只针对确认误导的旧交接/工作记忆，不等于删除科研证据或恢复旧失败路线。
4. `/home/lyh/桌面/智能仓机器人分布式调度_文献备份`永久只读。仅既获准的`/home/lyh/桌面/MAPF_实验前必读论文_20260909`可在必读材料变化时更新；PDF不入Git。新工件写研究目录，编辑用apply_patch。
5. shell每段前缀rtk，精确内容用rtk proxy；仅仓库实际有.codegraph时先用CodeGraph，不创建/重建索引。不绕过沙箱、审批拒绝或登录限制，不向外部人员发消息。
6. 用户已授权既有仓库`LYHrmer/MAPF_PIED_MDDR_RESEARCH`的精确文档同步。2026-09-14根实际GitHub API核该仓库为公开（`private=false`），纠正原“私有”记录；用户随后明确允许公开推送已准备的七文件文档批次（含未发表主稿）。2026-09-20用户进一步要求“进度及时更新github”，后继进度文档可按此授权同步；本轮仅同步入口、GITHUB_PROGRESS、Q2和导师说明，主稿现有修改保留未提交。不自行更改仓库可见性；先核实际工作树/远端，只暂存核过路径，不add .、不上传整个目录/受限材料、不跑hook、不改全局Git设置、不发release。历史提交号不是当前状态。
7. Claude C31取消，C32–C43及C45/46均已终态，不轮询旧句柄。C36–38无完整交付后的Codex接手代码不冒称Opus成果；C39–41及C43有完整Opus源码，C42截断后由Codex完成并实测。C44启动工具被中止，未返回CLI session、RAW或模型代码，不是provider推理失败或Opus交付，MemoryAdapter由Codex完成。C45实际CLI退出0，Opus头文件与Codex修正/测试/README为混合交付。C46实际HTTP402每日额度拒绝，零token/无代码，Codex随后完成§25；不重复请求或改共享路由，原调用与实现记录分开。旧一次性等待已于2026-09-12结束，不当作402的已知恢复时刻。2026-09-21用户新要求提高Opus任务占比；新的日志核账任务实际exit0完整交付，modelUsage报告claude-opus-5，见Q2 §53及独立回执。明确文件范围的实现、工具、局部修复、文档整理优先交Opus；根负责难理论、安全/费用边界及跨模块验收，不为低难度任务默认增加Astra。新成功不抹去旧失败，也不保证以后额度。已证本地代理网络在沙箱不可用，后续合法调用沿require_escalated路径；不绕过实际审批。保原RAW及终态，thinking只统计而不输出。
8. 历史51失败链、失落69L1/69E1、73P7/73L7/73C2及所有终态咨询按原记录处理，不因旧文件写“运行中”重启。先核活句柄和实际工件，缺回执不算完成；有新证据的不同具体工作可继续。
9. 用户2026-09-20已明确允许query_native与position_native两份程序内固定native组件测试及同范围必要修复复测；实际首次运行及零历时修复后的复测已通过，见Q2 §34。不再次请求这两份范围，也不据此运行新runtime ELF、研究服务/guest/world/仿真或扩读实验输入。Q2 §35分配入口只有静态编译/链接/调用路径证据，完整启动和实际业务执行仍待接通。
10. 用户随后明确允许[固定数值guest与查询费用核心两项](../implementation_binding_evidence/NUMERIC_AND_COST_FINITE_SCOPE_20260920.md)及同范围必要修复复测：前者最多300秒、固定SHA镜像经付费INIT/B1执行真实数值组件并双制度核账；后者最多30秒、三组固定native费用检查。不再次请求该范围。授权不扩至新codec测试、规划/控制/站点业务、world/仿真、实验输入或保护参数。
11. 用户另明确允许[受保护内存固定native/B1检查](../implementation_binding_evidence/AUTH_MEMORY_NATIVE_SCOPE_20260920.md)及同范围必要修复复测，每次最多30秒；实际首次通过265项断言，见[原始结果](../implementation_binding_evidence/AUTH_MEMORY_NATIVE_RESULTS_20260920.md)。不再次请求此范围，也不将其扩大到新编译可信kernel、CpuInitializer/worker运行、AUTH业务签发、站点或仿真。其它实现和静态编译继续推进。
12. 用户随后明确允许[编译可信worker固定检查](../implementation_binding_evidence/AUTH_WORKER_FINITE_SCOPE_20260920.md)及同范围必要修复复测，每次最多60秒；根已首次实际通过，无修复/重跑，见[完整记录](../implementation_binding_evidence/AUTH_WORKER_FINITE_RESULTS_20260920.md)。该具名11页/32槽/六请求镜像及驱动的付费INIT、CpuInitializer、worker/普通B1执行已获准，不再询问同范围；不扩大到生产AUTH签发、中心writer/规划/控制/站点服务、world/仿真、研究输入或保护参数。
13. 用户随后明确允许[六策略12组固定native检查](../implementation_binding_evidence/QUERY_POLICIES_NATIVE_SCOPE_20260920.md)及同范围必要修复复测，每次最多30秒；根6e76a6首次实际通过，无运行后修复/重跑，见[完整记录](../implementation_binding_evidence/QUERY_POLICIES_NATIVE_RESULTS_20260920.md)。不再次请求此范围，也不扩大到实际站点、guest/仿真、实验输入或保护参数。
14. 用户随后明确允许[COST封存七组固定native检查](../implementation_binding_evidence/AUTH_COST_NATIVE_SCOPE_20260920.md)及同范围必要修复复测，每次最多30秒；根758559首次实际通过，无修复/重跑，见[完整记录](../implementation_binding_evidence/AUTH_COST_NATIVE_RESULTS_20260920.md)。不再次请求此范围。该授权不扩至新COST kernel/站点guest执行、生产签发或交付、服务/仿真、实验输入或保护参数；源码和静态接入继续推进。
15. 用户随后将当前目标设为“尽快拿到一轮最小闭环结果”，再总结进度、优化后续方案并交接新终端，并于2026-09-21明确选择“先完成原生机制闭环，再交接完整计费链”。本轮据此实现并运行具名自包含原生机制闭环，以及实际B1工作量反馈的集成诊断，含必要修复复测。前者连接真实控制器、数值观测、PositionCommit和动作继续执行；后者连接实际B1扣费、账本、codec及下一次选择。两者分别报告，不合称完整站点/AUTH/全费用业务闭环。输入限程序内人工原型，不读取研究map/scen/config或旧结果，不赋既有保护参数，不启动规模实验。该新增目标覆盖这次最小运行，旧组件授权继续有效，不再逐项重复询问。
16. 接续完整计费链后，三站点COST工件已静态链接。针对其最多300秒、两制度各两轮的具体新增运行范围，用户明确回复“先只完成实现和静态检查”。本轮据此不执行新驱动/镜像或日志核账，不生成运行与吞吐结果；运行范围文档保留为候选说明，不当作许可。生产请求/POSITION来源、公共发布及完整Collector收据安装继续按已有接口建设；旧已授权组件范围不变，保护输入和参数未赋值。

## 历史材料与视频

三份误导性旧HANDOFF已按用户授权删除，约束收拢于本页。旧报告对它们的引用沿[清理前提交](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/0153a15e4f059a567de169716985444cca86ec9d)查历史，不恢复为现行指令。旧[72R4](../72R4_THREE_REVIEW_ROOT_SYNTHESIS_AND_SUCCESSOR_REQUIREMENTS_20260907.md)的G6 FAIL属于72，不覆盖最新73R4。

[视频建议V1](../73V1_BILIBILI_RESEARCH_QUALITY_AND_EFFICIENCY_GUIDANCE_20260912.md)只有官方简介/章节，实际画面、语音和字幕读取量均为零，不能说已观看。项目采用的有限问题分工、强对照、贡献/反证表及减少重复咨询是独立判断，不归为未核视频观点。
