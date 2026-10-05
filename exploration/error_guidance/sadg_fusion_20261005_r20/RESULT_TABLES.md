# R20 完整执行结果表

负的完成时间差表示前一方法更快。所有对照共用冻结作者 SADG 核心；预测器/查询规则属于内部因子，不是额外发表算法。

| 层 | 方法 | 完成/登记世界 | 初始规划失败 | 总完成时间 | 查询 |
|---|---|---:|---:|---:|---:|
| core | ewma_structural | 18/18 | 0 | 41951.779482 | 361 |
| core | history_structural | 18/18 | 0 | 42082.467054 | 366 |
| core | learned_linear_structural | 18/18 | 0 | 42066.519713 | 358 |
| core | learned_no_query | 18/18 | 0 | 42047.413369 | 0 |
| core | learned_position_structural | 18/18 | 0 | 42066.519713 | 358 |

| 层 | 方法 − 对照 | 好/差/同 | 总时间差 | 查询差 | 族均相对差 | 探索性95%区间 |
|---|---|---:|---:|---:|---:|---|
| core | learned_position_structural − learned_linear_structural | 0/0/18 | 0.000000 | 0 | 0.00000% | [0.00000%, 0.00000%] |
| core | learned_position_structural − history_structural | 4/4/10 | -15.947341 | -8 | -0.08100% | [-0.35174%, 0.20402%] |
| core | learned_position_structural − ewma_structural | 4/3/11 | 114.740231 | -3 | 0.12729% | [-0.22673%, 0.63476%] |
| core | learned_position_structural − learned_no_query | 2/1/15 | 19.106344 | 358 | 0.01552% | [-0.09277%, 0.13934%] |
| core | learned_linear_structural − learned_no_query | 2/1/15 | 19.106344 | 358 | 0.01552% | [-0.09277%, 0.13934%] |

核心为新场景8/9的6个地图×场景族；N32，暂停/变速强度迁移。主要对比为位置条件融合与原线性融合，区间不能替代更多地图和真实外部方法。
