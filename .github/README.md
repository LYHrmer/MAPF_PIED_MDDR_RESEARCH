# MAPF 项目当前状态

更新：2026-10-07，R30 静态交付完成。**二维物理来源已接入真正的私有 END 验证实现，Berlin 来源已形成无结果的三臂比较设计；完整付费 dispatcher 仍待闭合。** 当前研究结论为 CONDITIONAL，尚无“相近完成表现下节省完整真实更新资源”的独立证据。

研究问题保持 MAPF、有界空间跟踪误差和有限更新资源；方法主线为代价感知进度查询与安全协调。普通 END、WAIT、结构规则和 EWMA 保留，学习作为辅助。

[仓库导航](../README.md) · [全部进度历史](../GITHUB_PROGRESS.md) · [整理前完整入口快照](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/a1989d6a0aa4740e665ae21ce369a0a0170e8671/.github/README.md)

## 当前三线状态

| 线路 | 已有实质交付 | 当前缺口与正在做的工作 |
|---|---|---|
| 主线：共同安全、执行与费用 | R29 空间安全接口保留；新增持久 World owner、真正私有 SOURCE→回放→END verifier、统一账户及 import 登记；1 个主机与 2 个 RV64 对象严格编译通过 | 后继按需 SOURCE 登记、十二段事件编码、Position/驻留/FIFO 与物理交付的联合付费 dispatcher 未闭合；新镜像、完整栈/费用待验 |
| 执行支线：原计划与完整资源组 | 12 MOVE 已精确绑定原弧长控制器，24 端点恒等式、10 FIFO、2 候选初态通过静态派生；生命周期 Layout 与物理配置各通过 1 个严格对象编译 | crossing 仍是旧自建机制输入。候选两台 epoch0 静止/cap0 尚未执行；真实误差保证、普通 END 消费与执行权限不由静态配置证明 |
| 查询支线：独立比较资格 | Berlin 1000 原行形成用途储备；冻结 WAIT_HISTORY、STRUCTURE_HISTORY、纯 STRUCTURE_EWMA03 三臂、两个完整策略对比、失败分母与费用向量 | N/K/时限/预算/容差与接口等 12 缺项已被登记器实际拒绝；单图条件设计不是跨地图 iid，三臂也不充作外部发表基线 |

本轮实产 408 个 SOURCE 和 68 个 publication 静态机会，未计为观察、费用或运行；主线与支线合计五个严格对象编译、2,815 项联合产品/来源 pin 与三稿保护核验通过。普通栈沿用 R29 对旧 R27 镜像的定点结果：A=10016、D≤37/43，范围外库/异常 B 仍 UNKNOWN；这些条件界不覆盖新增接口。

## 已有证据如何解释

- R19 旧原生 BUY 相对 WAIT 的完成时间和少 2，但完整费用多 272,797,762 步，尚不支持节省资源。
- 轨迹中的信息变化、中间提前和最终收益分别登记；缺少合法反事实时，逐 QUERY 因果收益保持 UNKNOWN。
- 两个后继长度属于机制上下文，不是两个独立 TEST 族。策略级比较不以单 QUERY 奖励尾部为统一前置。
- 作者顺序建议须经过共同空间安全 consumer；agent、namespace 或 occurrence 字符串相同不等于取得执行权限。

## 下一步与验收条件

1. 完成有限 dispatcher：真实普通 END→驻留/FIFO→完整空间检查→联合付费发布→物理交付，解决后继实际激活登记和十二段事件编码；不能只放宽旧 255 位限制。
2. 接线闭合后生成新镜像，定点补普通栈与完整费用资格；保持原认证、容量和失败前缀。当前没有合格的 crossing 科学 launch script。
3. 将合格共同接口接入已冻结三臂设计，事前确定 Berlin 分组、预算/时限/容差，生成小比较清单；新增科学运行另按具体授权执行。

主线仍有共同接口、方法与独立比较冻结、获授权的小比较、证据与论文四个阶段；查询和执行支线与这些阶段重叠。扩大规模、随机延迟和两台 LIMO 演示后置。

## 当前证据位置

以下均为本机目录，公开仓库只同步状态与导航。

| 内容 | 本机相对路径 |
|---|---|
| R30 总报告、实现、静态清单与联合核验 | 主仓 `implementation_binding_evidence/registered_lifecycle_20261007_r30/`：`REPORT.md`、`RUN_CHECKLIST.md`、`verify_delivery.py` |
| R30 共享生命周期登记 | 主仓 `implementation_binding_evidence/lifecycle_contract_20261007_r30/` |
| R30 物理绑定与候选初始化 | 执行工作树 `exploration/error_guidance/physical_binding_20261007_r30/` |
| R30 有限条件比较设计与输入登记器 | 查询工作树 `exploration/learned_query/comparison_design_20261007_r30/` |
| R29 安全接口与旧镜像栈结果 | 主仓 `implementation_binding_evidence/common_safety_20261007_r29/`、`stack_targets_20261007_r29/` |

## 现行边界

用户授权仍为“仅完成可运行实现、冻结与清单”。本轮不启动新科学 host/guest、solver、仿真、训练或机器人运行；不扩旧矩阵、不加模型、不以孤立测试代替共同执行证据。

R23/R27 是未来择一的六槽机制包，不能合并成十二次；每槽 300 秒、总 1800 秒、串行各一次、不重试，当前均 NOT_RUN / NOT_AUTHORIZED。原输入、供给、空间误差、控制器和参数边界保留。R30 epoch0/cap0 是隔离的新候选初始化设计，未执行、未授权；agent1 原计划名义 t2 保留，不补写旧 t0 历史。

主稿未提交修改和冻结证据保持。本次依据新增“整理更新 git”要求，只整理 README、当前入口和进度历史三份已追踪文档；实现、原始数据及主稿不随之发布。旧快照中的阶段授权与“下一步”按当时范围查阅，不能覆盖现行边界。
