# MAPF 项目当前状态

更新：2026-10-07，R31 静态交付完成。**有限按需 SOURCE、十二段生命周期和真实发布证人到物理交付的接口已实现；三臂公共输入适配已落地。** 统一完整镜像、初始化与完整费用仍待闭合。当前研究结论为 CONDITIONAL，尚无“相近完成表现下节省完整真实更新资源”的独立证据。

研究问题保持 MAPF、有界空间跟踪误差和有限更新资源；方法主线为代价感知进度查询与安全协调。普通 END、WAIT、结构规则和 EWMA 保留，学习作为辅助。

[仓库导航](../README.md) · [全部进度历史](../GITHUB_PROGRESS.md) · [整理前完整入口快照](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/a1989d6a0aa4740e665ae21ce369a0a0170e8671/.github/README.md)

## 当前三线状态

| 线路 | 已有实质交付 | 当前缺口与正在做的工作 |
|---|---|---|
| 主线：共同安全、执行与费用 | 真正 Notice→END驻留/FIFO、完整 cap 与同批冲突检查、Position/不可变账本双 SOURCE 联合提交已实现；真实提交后缀有新机器码静态推导 | 需组成同一完整 driver/Center 镜像，接纳初态并重新绑定最终 publication 计划；二维主动查询 token、完整栈与费用待验 |
| 执行支线：原计划与完整资源组 | 408 槽按需 SOURCE 接入唯一 Station；12段 END/SERVICE/CAP 单word校验；真实发布证人交付、双agent后继一次代次提交、失败封停与费用前缀保持 | crossing 仍是旧自建机制输入，候选初态未运行；新增主机准备/交付工作在原B1覆盖之外，外部费用尚未测量，不能记零 |
| 查询支线：独立比较资格 | 310行只读适配器实际复用 history/纯EWMA03/结构规则，严格公共schema及WAIT退路；原Berlin 1000行、三臂/两对比设计不扩张 | 公共机会producer与合法初始报价未接线，空报价时结构臂持续WAIT；N/K等12缺项、单图统计与外部基线资格仍待补 |

本轮五个最终实现对象严格编译、2,895 项联合产品/来源 pin 与三稿保护核验通过。真实联合提交分析 ELF 保留37个CFG节点与失败边，最长34条指令；纯编译器求值得B1指令界343、reservation356、原行阈值365，未执行ELF。这只覆盖该分析后缀，不能代替最终镜像计划、全栈或实测完整费用。R29旧镜像普通栈A/D条件界也不转借新代码。

## 已有证据如何解释

- R19 旧原生 BUY 相对 WAIT 的完成时间和少 2，但完整费用多 272,797,762 步，尚不支持节省资源。
- 轨迹中的信息变化、中间提前和最终收益分别登记；缺少合法反事实时，逐 QUERY 因果收益保持 UNKNOWN。
- 两个后继长度属于机制上下文，不是两个独立 TEST 族。策略级比较不以单 QUERY 奖励尾部为统一前置。
- 作者顺序建议须经过共同空间安全 consumer；agent、namespace 或 occurrence 字符串相同不等于取得执行权限。

## 下一步与验收条件

1. 将已编译 guest/Station/物理交付接口组成同一有限 driver 与完整镜像，接纳真实初态并重新抽取最终地址下的 publication 计划；保持原认证和容量。
2. 补新镜像普通栈及新增主机准备/交付费用范围，保留失败前缀；定点接二维主动查询 consumer 与真实公共机会 producer，登记共同报价冷启动。
3. 资格闭合后确定 Berlin 分组、预算/时限/容差，冻结小比较清单；当前没有合格的新科学 launch script，新增运行另按具体授权执行。

主线仍有共同接口、方法与独立比较冻结、获授权的小比较、证据与论文四个阶段；查询和执行支线与这些阶段重叠。扩大规模、随机延迟和两台 LIMO 演示后置。

## 当前证据位置

以下均为本机目录，公开仓库只同步状态与导航。

| 内容 | 本机相对路径 |
|---|---|
| R31 总报告、实现、静态清单与联合核验 | 主仓 `implementation_binding_evidence/finite_dispatch_20261007_r31/`：`REPORT.md`、`RUN_CHECKLIST.md`、`verify_delivery.py` |
| R31 真实提交后缀机器码/B1推导 | 上述目录 `events/publication_scope/` |
| R31 按需 SOURCE、物理交付与费用缺口 | 上述目录 `host/REPORT.md`、`host/COST_SCOPE.json` |
| R31 三臂公共输入适配 | 查询工作树 `exploration/learned_query/readonly_policy_adapter_20261007_r31/` |
| R30 物理事实来源与比较设计 | 主仓 `implementation_binding_evidence/registered_lifecycle_20261007_r30/`；查询树 `exploration/learned_query/comparison_design_20261007_r30/` |

## 现行边界

用户授权仍为“仅完成可运行实现、冻结与清单”。本轮不启动新科学 host/guest、solver、仿真、训练或机器人运行；不扩旧矩阵、不加模型、不以孤立测试代替共同执行证据。

R23/R27 是未来择一的六槽机制包，不能合并成十二次；每槽 300 秒、总 1800 秒、串行各一次、不重试，当前均 NOT_RUN / NOT_AUTHORIZED。原输入、供给、空间误差、控制器和参数边界保留。R30 epoch0/cap0 是隔离的新候选初始化设计，未执行、未授权；agent1 原计划名义 t2 保留，不补写旧 t0 历史。

主稿未提交修改和冻结证据保持。本次依据新增“整理更新 git”要求，只整理 README、当前入口和进度历史三份已追踪文档；实现、原始数据及主稿不随之发布。旧快照中的阶段授权与“下一步”按当时范围查阅，不能覆盖现行边界。
