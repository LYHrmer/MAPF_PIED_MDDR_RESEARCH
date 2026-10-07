# MAPF 项目当前状态

更新：2026-10-07，R34/S3静态交付与QV1独立支线预检完成。**真实回执有界编码已接入完整host并编译链接，固定ELF又关闭memcpy/memmove两项栈义务；原版BALANCE计量与回执核验入口已实现。** R34/S3联合3,647项pin通过，QV1另冻结20文件/21来源，科学运行0。完整普通栈、付费公共导出、二维主动查询及完整费用仍待闭合。总体CONDITIONAL，尚无“相近完成表现下节省完整真实更新资源”的独立证据。

研究问题保持MAPF、有界空间跟踪误差和有限更新资源；方法主线为代价感知进度查询与安全协调。普通END、WAIT、结构规则和EWMA保留，学习作为辅助。

[仓库导航](../README.md) · [全部进度历史](../GITHUB_PROGRESS.md) · [整理前完整入口快照](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/a1989d6a0aa4740e665ae21ce369a0a0170e8671/.github/README.md)

## 最新毕业目标（2026-10-07确认）

学校不限制SCI分区或期刊名单，希望期刊有合理质量，争取2026年底前完成稿件并开始投稿；年底不是录用截止。原二区/三区偏好不再作为毕业硬门槛。后续优先验证一项具体任务或完整更新资源收益，10月底检查比较资格与初步作用，主线成立后11月补必要实验并成稿、12月修改首投。此为时间目标，不保证完成或录用；原课题与S1均保持证据资格判断，不自动换题或放宽运行。最新安排存桌面综述`LaTeX综述重构_20260924/毕业导向投稿安排_20261007.md`，本轮无科学运行或保护项变化。

## QV1：独立查询价值可行性支线

按用户明确要求，由一个子智能体从 `explore/learned-query` 已提交基点 `3c809f903e42ce33d287ca7f21e38924bd6dcffc` 创建 `/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY` 与 `explore/query-value-feasibility`。新树未改原三树稿件/冻结材料，也未复制原树未提交R34；外部组件以本机只读SHA pin复用，不冒称公开Git即可独立复现。

已实作本臂公共字段/时间接纳、成对完整尾只读采集与引用绑定；复用R31白名单和R24合同，保留失败/删失、未知成本及普通END，合同禁止WAIT读取QUERY结果，实际信息隔离审计尚缺。只读复核R21旧账本10,543条、24组，保留625条迟到查询，均为开发诊断，新增因果标签0。找到已有R18 ridge和无查询/周期/历史规则、R19结构/纯EWMA；组件存在，主线合法适配待资格，没有重写、调用或拟合模型。

静态实现部分完成，研究有效性UNKNOWN：当前没有合格checkpoint/恢复、真实公共producer、信息隔离/空间安全/完整费用审计，也没有独立TEST；数据接纳器强制`model_input_eligible=false`，尾入口不能靠自报PASS产标签。空模板接纳UNKNOWN仅验证该默认路径。故保留为辅助候选，不融合主线。

20个文件、21项来源pin、4稿保护、5个Python AST及实际旧账本复核通过；阶段补充另追加冻结，按V1机会/标签、V2接口/对照/清单、V3授权验证、V4融合/辅助/停止四验收阶段报告，V1/V2未全过。运行清单列出精确checkpoint、次数/预算/截止等缺项，保持UNASSIGNED，不借六槽。入口在新树 `exploration/learned_query/query_value_feasibility_20261007_qv1/{REPORT.md,PHASE_MAPPING.md,RUN_CHECKLIST.md,verify_delivery.py}`。0训练/策略/solver/host/guest/仿真；下一先补公共生产端和可靠完整尾，强规则足够则停止学习投入。

## 科研导师判断：期刊问题优先，候选不围绕单篇IROS锁定

用户要求不能只修改IROS2021。会议来源不决定工作上限，但仅修改网络或换场景也不足以构成独立贡献。本轮定点参考[T-RO的SADG正式论文](https://doi.org/10.1109/TRO.2023.3344051)（卷年2024、线上2023）、[JIRS的跟踪与TADG](https://doi.org/10.1007/s10846-025-02291-8)、[RAS仓库学习MAPF评估](https://doi.org/10.1016/j.robot.2025.105149)及[AI的X*](https://doi.org/10.1016/j.artint.2020.103417)，把共同执行条件、空间安全、任务/计算指标和质量界区分写入设计。各来源的全文/摘要层级在本机报告分列；没有重新全面审查或认定新颖性。

主线保持代价感知进度查询与安全协调；规划/停止方向保留为独立候选，IROS是近邻和待适配基线之一。已发表停止机制要在校准集公平调参；强规则已足够时停止学习投入。当前资格均为2项PASS/4项UNKNOWN，未锁题。

主线剩4阶段：共同接口资格→轻量方法/独立比较冻结→另行授权小比较→证据成稿。原查询、执行支线各剩3阶段并与主线重叠；新查询价值可行性支线4阶段，独立规划/停止候选4阶段。交付编号S3不是科学阶段3。具体验收与一周动作见本机R34 `RESEARCH_DECISION.md`。

## S3：原版计量实现与具体未授权清单

已实现监督进程、worker和作者原版进程的计量入口，以及独立v2回执reader；复用S2全路径/CSV核验。子树CPU通过完整wait链仅计一次，再加不重叠的监督CPU；wall/CPU分别报告。范围覆盖预检、原版构造/求解/输出、路径核验与worker落盘；外层回执写出是另报的harness开销，不称零费用或完整查询成本。

实际32×32/409行前40任务预览、语法、缺失结果NOT_RUN和未授权`--execute`拒绝通过；拒绝发生在mkdir/fork/exec之前。运行提案固定1次、无重试、内部30秒、worker55秒/收尾5秒/总60秒尽力截止，保留超出量；不再称硬实时保证。输出目录不存在，原版R0、真实解析、看护动态验收与候选效果仍UNKNOWN，没有训练标签。

本机 `implementation_binding_evidence/original_measurement_20261007_s3/`：`REPORT.md`、`run_original.py`、`audit_measurement.py`、`RUN_PLAN.json`、`RUN_CHECKLIST.md`。与R34联合冻结，后续科学运行须新的具体授权版本，不改当前NOT_AUTHORIZED冻结，也不借原六槽。S2/S1记录保留如下，其当时的待实现计量器已由本轮静态补齐。

## 历史选题预检 S2：贡献边界与原版输出核验

继续预检停止方向，尚未锁题。IROS2021已覆盖首个可行解后按历史曲线停止、事后监督标签、斜率／平台特征；ICAPS2022和AAAI2024已覆盖联合停止／调参与上下文及规划费用。仅换MAPF场景、加小模型或容差指标不能直接作为新贡献。当前要检验的是：在声明的质量容差下，能否比发表停止机制和强简单规则节省完整计算费用；跨图风险仍是待验证问题。

已固定ICAPS2022官方`Metareasoning.jl`提交`facb41ad…`的23个原文件并定点读源码；它控制RRT*/AWA*，计时使用采样数／节点预算，不能直接折算本项目真实wall/CPU。未找到仓库许可证文件，未安装、导入、训练或上传，外部基线资格仍UNKNOWN。

新增只读`audit_original.py`，实际通过作者32×32地图、409行scenario前40任务及原版binary的哈希／输入核验；缺失运行包返回NOT_RUN，不生成收益或停止标签。程序已实现最终全路径、MOVE/WAIT、顶点／交换／驻留冲突、SOC与CSV对应检查，并消费完整计量回执合同。发现原进程exit0及CSV success均不能单独证明路径成功；没有真实输出，解析分支运行资格仍UNKNOWN。完整计量wrapper尚待实现，不把合同当作生产端完成。

本机报告与核验：`implementation_binding_evidence/stopping_qualification_20261007_s2/REPORT.md`、`MEASUREMENT_CONTRACT.md`、`verify_delivery.py`。S1和R33冻结及三稿保护保持，科学运行0。下一先补一次原版R0的完整计量与明确总截止清单；仍须具体授权才运行。没有开发机会证据或简单规则已足够时停止学习投入。S1分区是原偏好，毕业约束以本页最新确认记录为准；原三线R33缺口及授权未改变。

## 历史选题预检 S1（非锁题，2026-10-07）

按用户新增要求，以**中科院二区／三区、优先纯仿真、可结合学习**建立独立选题预检。科研导师判断：优先核验“已有可行解后，在路径质量容差内学习决定何时停止MAPF优化”；可拒绝算法选择和终生任务流引导分别暂缓／后备。学习停止、邻域选择和预算分配均已有强近邻，本轮没有候选GO或新颖性通过，不改变原三线问题及边界。

已完成三候选近邻／资格对照、三刊适配表、质量与完整时间的比较草案，固定六个作者仓库版本并保存22份源码／配置／许可。BALANCE原版39个C++单元编译并链接通过，89个跟踪文件前后不变；**0求解器执行／训练／仿真**。发现README示例的默认`maxIterations=0`不会进入可行解后的LNS优化循环，且原runtime不覆盖构造预处理与最终校验；均已进入复现清单。源码构建PASS不替代原版最小实例，R0仍UNKNOWN。

期刊优先核RAS，Applied Intelligence有条件备选，ASC后备。武汉大学图书馆显示三刊CAS大类2／3／2，但未标版本年；Applied Intelligence的AI小类为4。中科院文献情报中心[已声明2026年起停止更新分区](https://las.cas.cn/news/tzgg/202603/t20260327_8178738.html)，需按学校认可版本及大／小类规则核定，不能混用JCR或其他机构分区。

本机交付：`implementation_binding_evidence/simulation_learning_scout_20261007_s1/`，入口`README.md`；`original_build/BUILD_REPORT.md`含真实构建与一个未授权原版预检提案（40个作者示例任务、1次、内部30秒／外部硬截止建议60秒、不重试）。提案不借用旧六槽；无运行目录。下一先核创新差异、最强停止基线和独立数据，具备具体授权后才做原版机会预检；简单规则已足够时停止学习投入。原R33共同接口工作未被此支线替代，也未据此记为R34完成。

## 文献补充（2026-10-07）

本机桌面综述在原60项方法与应用工作上补入21项期刊文献：2025卷年10项、2026卷年11项，共81项工作，另加组织参考综述共82条Bib。新增16份合法PDF并阅读重点章节，5项只有官方摘要或出版商片段；POD分配2026年12月卷期，首次上线日期未核。全文与原文备份仅留本机。

新近TIT/JSAC工作已按任务效果选择更新；Hua、Concrete MAPF、P3GASUS和CREST已研究地面跟踪、动作依赖及执行约束释放。课题继续围绕MAPF，但增量需落到：普通END不足时，付费局部进度是否及时改变合法放行，并在完整后续任务中产生值得其费用的收益。TIT状态在通信期间也会演化，不能只用持续运动作为区别。AI/TRE/POD具体信息与费用条件仍待全文核对。

正文和21项阅读记录已更新；按固定问题、方法、效果/局限、改进框架整理，完成科研导师定点复核与文字修订。82条引用及Biber数据模型、LaTeX结构、16份原文标题/页数/哈希和263项旧材料保护通过静态检查。未生成综述PDF，未开展新研究运行、训练或仿真，未改变输入、参数和现行授权；原三线下一步不变。本机入口：桌面综述下`LaTeX综述重构_20260924/README.md`。

## 当前三线状态

| 线路 | 已有实质交付 | 当前缺口与下一步 |
|---|---|---|
| 主线：共同安全、执行与费用 | 首次原付费SOURCE/35字段/完整回放生成私有初态事实；两head同批、真实q0/cap0/几何/owner检查后一起消费，任何发布与cap前必需接纳；完整Center和host已重建 | 动态初态事实发生数0；完整普通栈和原有限行容纳性尚无资格，二维主动查询与完整费用未闭合 |
| 执行支线：原计划与完整资源组 | R33关闭15库叶函数；R34从6函数真实机器字、全分支SP深度与固定跳转表，新增关闭memcpy/memmove各48字节传递峰值 | 剩余94库目标+165间接位置共259项传递义务，另有异常引擎；条件小计不是完整界，不展开全库审查或扩大栈 |
| 查询支线：独立比较资格 | 私有真实回执及失败前缀保留；R34新增最多68批、4类事件×4类结果的有界位掩码编码，接入原成功/失败host计量出口并链接 | 编码仍HOST_ONLY、authority NONE，未付费送达guest；完整公共机会/图/账户/报价缺口仍WAIT。Berlin原12缺项、单图统计与外部基线资格保持 |

R34/S3联合3,647项来源/产物pin、三稿及历史尾文保护通过；R33原3,354项与S2原31项冻结另行复核通过。R34新增1个真实driver对象，复用1个冻结qualification对象，链接新host，SHA以`f54d63c7…`起；最终Center仍为R33 `d9754504…`，未重编或执行。旧构建与新构建记录分开，新增编译前后依赖集合/散列一致。

最终发布计划保留R33实际地址的37CFG节点、最长34指令、B1指令界343、reservation356、原行阈值365。原私有kernel完整跨度一致，1408字节界只限私有域。普通栈条件为`max(19136, max_j(P_j+U_j), E_start) <= 65536`；剩余U_j及异常引擎峰值E_start未知。19136为已知调用树条件小计，46400为最坏前缀对应余量，均不是完整栈资格或实测峰值。

## 已有证据如何解释

- R19旧BUY完成时间和相对WAIT少2，但完整费用多272,797,762步，尚不支持节费。
- 信息变化、合法执行变化、中间提前和最终收益分开；缺合法反事实时逐QUERY因果收益UNKNOWN。
- 两个后继长度是机制上下文，不是两个独立TEST族；内部三臂不是外部发表基线。
- 初态构造/身份字符串不提供AUTH，实际运行时仍须首次SOURCE认证；静态接线不能记成真实接纳已发生。
- START只记录实际被接受的RUN，END只记录停止观察与交付ACK，物理精确停止时刻保持null。
- host日志没有guest权限；外部wall/线程CPU与B1分开，inclusive父子不双加，未知费用不记零。

## 下一步与验收条件

1. 补真实回执的付费公共导出、当前图/账户和同运行完整结算报价，再接二维合法主动查询consumer；原R17固定1D权限不放宽，EMPTY_HISTORY_WAIT保留。
2. 按真实PC、目标和前缀对同类栈义务定点补证；已关闭15库叶函数及2个copy函数不重做，普通栈/arena/供给不扩大。
3. 共同接口和完整费用资格闭合后，补Berlin分组、预算/时限/容差等设计字段，冻结独立小比较，另按具体授权启动。

主线仍有共同接口资格、轻量方法与独立比较冻结、获授权的小比较、证据与论文四阶段，支线与之重叠。扩大规模、随机延迟和两台LIMO后置。

## 当前证据位置

以下均为本机目录，公开仓库只同步状态与导航。

| 内容 | 本机相对路径 |
|---|---|
| QV1查询价值可行性、成对尾入口与组件登记 | 新树 `/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY/exploration/learned_query/query_value_feasibility_20261007_qv1/`：`REPORT.md`、`PHASE_MAPPING.md`、`collect_pair.py`、`BASELINES_AND_MODEL.md`、`RUN_CHECKLIST.md` |
| R34定点接口、阶段判断与联合冻结 | 主仓 `implementation_binding_evidence/targeted_interfaces_20261007_r34/`：`REPORT.md`、`RESEARCH_DECISION.md`、`stack/`、`host/`、`verify_delivery.py` |
| S3原版计量与未授权清单 | 主仓 `implementation_binding_evidence/original_measurement_20261007_s3/`：`REPORT.md`、`run_original.py`、`audit_measurement.py`、`RUN_CHECKLIST.md` |
| S2停止方向贡献审计、原版输出consumer与基线源码 | 主仓 `implementation_binding_evidence/stopping_qualification_20261007_s2/`：`REPORT.md`、`audit_original.py`、`MEASUREMENT_CONTRACT.md`、`BASELINE_SOURCE.json`、`verify_delivery.py` |
| R33总报告、资格/费用与具体清单、联合核验 | 主仓 `implementation_binding_evidence/initial_admission_20261007_r33/`：`REPORT.md`、`QUALIFICATION_GATES.json`、`COST_SCOPE.json`、`RUN_CHECKLIST.md`、`verify_delivery.py` |
| R33初态接口与完整Center/host | 上述目录 `admission/`、`image/`、`host/`，各有报告及冻结回执 |
| R33普通栈权威条件与261项义务 | 主仓 `implementation_binding_evidence/ordinary_stack_20261007_r33/`：`REPORT.md`、`obligations/r33_with_leaves/`、`verify_delivery.py` |
| R33真实交付回执与集成证据 | 查询树 `exploration/learned_query/delivery_receipts_20261007_r33/` |
| 已有公共事实/策略适配 | 查询树 `public_projection_20261007_r32/`、`readonly_policy_adapter_20261007_r31/`，均位于 `exploration/learned_query/` |
| 独立比较冻结设计 | 查询树 `exploration/learned_query/comparison_design_20261007_r30/`，原Berlin储备不变 |

## 现行边界

用户授权仍为“仅完成可运行实现、冻结与清单”。本轮新科学host/guest、solver、仿真、训练、策略调用和真实回执均0；不扩旧矩阵、不加模型、不以孤立测试代替共同执行证据。host在读镜像/创建world前拒绝未授权或普通全栈未资格化的启动，无命令行旁路；path_installed仅是已接动态consumer。

有限登记保持两agent/12MOVE、34tick、408SOURCE机会、68发布、241边界，Compute窗口上限4754≤8192，每行8388608，每phase准备64行，Natural0、额外延迟0。R23/R27另为未来择一六槽，每槽300秒、总1800秒、串行一次、不重试，仍NOT_RUN / NOT_AUTHORIZED；不合并十二次，不转借本轮或Berlin。原空间误差/控制参数、agent1名义t2保留，不补旧t0历史。

三份主稿、旧冻结证据、输入和现行边界保护。本轮只提交当前入口与进度历史两份文档；实现、原始数据和主稿不随之发布。历史快照中的“当前”“下一步”和授权仅描述当时范围。
