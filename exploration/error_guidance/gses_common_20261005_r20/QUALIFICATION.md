# R20 资格卡与实施边界

状态：**CONDITIONAL，仅获准探索性最小机制预检，不代表共同基线资格已通过。**

机制一句话：在冻结R19事件执行器的优化入口，把公开未完成时长与固定依赖图交给原作者Improved GSES选择方向，再经原完整图／活动承诺guard采用；路径、物理扰动和已开始动作不改变。此机制与root当前授权一致，无新增用户确认。

| 项 | 判断 | 证据与关闭条件 |
|---|---|---|
| 问题合同 | PASS | R19部分MILP候选违反原模型；需真实已发表固定路径顺序优化器对照，比较合法性、完成目标与实际尾部。此轮先核接口，不比较总体性能。 |
| 已发表锚点 | PASS | Jiang/Lin/Li，AAAI2025 Improved GSES，DOI10.1609/aaai.v39i22.34487；已读R19 EXTERNAL_BASELINE_NEXT。 |
| 作者R0 | PASS | STPG `25fb931eff03f1cce23a22a68ab42b7533f85ab3`，MIT；R9/R10原例及R13连续采用已有完整证据。复用R13原ELF与43作者文件hash，不重跑旧例。 |
| 共同接口 | UNKNOWN | `COST_TYPE=float`不证明任意权重有效；Astar的`>=0`与heuristic `+1`依赖单位间隔。原NewSimulator不执行未来加权边。用新小例Fraction枚举验证，不改作者核心掩盖差异。 |
| 数据与独立单位 | PASS（机制） | 新登记确定性微图，完整输入、输出、枚举所有合法方向；无训练/TEST效果筛选，不能当独立场景泛化。 |
| 仿真闭环 | UNKNOWN | 原R19执行器可复用；须先验证action节点到STPG状态节点的时长／逆边映射、活动保护和捕获/送达边界。通过后才允许新标准场景比较。 |

复杂度中等，按阶段交付。第一阶段严格4次新作者调用，16秒原搜索上限、20秒host watchdog、Improved_GSES、seed10；无结果驱动重试。第二阶段至多8次作者调用，具体新输入和适配版本须在调用前另登记，总上限12。Fraction枚举／旧工件只读不计作者调用。失败、返回原图、非最优和目标不一致全部保留。

实施清单：`phase1.py`登记四个新输入与源码/ELF哈希并逐次执行；`fraction_oracle.py`独立解析图、穷举反转、核DAG和完成目标；保存每例原stdout/stderr/JSON/receipt；阶段报告明确单位／实数限制。之后再交`common_adapter.py`与R19 Simulator子类，核完整group、活动承诺、延迟消息和物理后缀，不能以自写优化器代替原方法。

来源：[正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/34487)、[固定作者仓库](https://github.com/DiligentPanda/STPG/tree/25fb931eff03f1cce23a22a68ab42b7533f85ab3)、[R13已完成接口](../gses_online_adoption_20261004_r13/REPORT.md)。应用skills：research-mentor、reproducing-papers；本卡将未知降为已授权机械预检，不锁题或作投稿声明。
