# R19 完整执行结果表

负的完成时间差表示前一方法更快。所有对照共用冻结作者 SADG 核心；预测器/查询规则属于内部因子，不是额外发表算法。

| 层 | 方法 | 完成/登记世界 | 初始规划失败 | 总完成时间 | 查询 |
|---|---|---:|---:|---:|---:|
| core | ewma_no_query | 36/36 | 0 | 63817.666667 | 0 |
| core | ewma_structural | 36/36 | 0 | 63701.166667 | 420 |
| core | fixed_update | 36/36 | 0 | 63622.083333 | 864 |
| core | history_no_query | 36/36 | 0 | 63732.083333 | 0 |
| core | history_rule | 36/36 | 0 | 63621.083333 | 677 |
| core | history_structural | 36/36 | 0 | 63619.083333 | 422 |
| core | learned_no_query | 36/36 | 0 | 63657.916667 | 0 |
| core | learned_structural | 36/36 | 0 | 63696.416667 | 420 |
| scale_extension | ewma_no_query | 6/9 | 3 | 28777.500000 | 0 |
| scale_extension | ewma_structural | 6/9 | 3 | 28809.000000 | 287 |
| scale_extension | history_no_query | 6/9 | 3 | 28836.000000 | 0 |
| scale_extension | history_structural | 6/9 | 3 | 28810.000000 | 293 |
| scale_extension | learned_no_query | 6/9 | 3 | 28701.000000 | 0 |
| scale_extension | learned_structural | 6/9 | 3 | 28709.000000 | 290 |

| 层 | 方法 − 对照 | 好/差/同 | 总时间差 | 查询差 | 族均相对差 | 探索性95%区间 |
|---|---|---:|---:|---:|---:|---|
| core | learned_no_query − history_no_query | 4/2/30 | -74.166667 | 0 | -0.05981% | [-0.15829%, 0.01342%] |
| core | ewma_no_query − history_no_query | 4/4/28 | 85.583333 | 0 | 0.04618% | [-0.03121%, 0.13067%] |
| core | learned_no_query − ewma_no_query | 4/1/31 | -159.750000 | 0 | -0.10498% | [-0.26863%, -0.00516%] |
| core | history_structural − history_no_query | 2/0/34 | -113.000000 | 422 | -0.06753% | [-0.19074%, 0.00000%] |
| core | learned_structural − learned_no_query | 3/2/31 | 38.500000 | 420 | 0.01233% | [-0.02663%, 0.05737%] |
| core | ewma_structural − ewma_no_query | 5/0/31 | -116.500000 | 420 | -0.08030% | [-0.17653%, -0.01332%] |
| core | learned_structural − history_structural | 5/3/28 | 77.333333 | -2 | 0.02044% | [-0.05960%, 0.10048%] |
| core | learned_structural − ewma_structural | 2/3/31 | -4.750000 | 0 | -0.01165% | [-0.06048%, 0.03976%] |
| core | history_structural − history_rule | 1/0/35 | -2.000000 | -255 | -0.00593% | [-0.01779%, 0.00000%] |
| core | learned_structural − fixed_update | 5/3/28 | 74.333333 | -444 | 0.01156% | [-0.07735%, 0.10048%] |
| scale_extension | learned_no_query − history_no_query | 4/0/2 | -135.000000 | 0 | -0.59009% | [-0.89429%, -0.28588%] |
| scale_extension | ewma_no_query − history_no_query | 4/0/2 | -58.500000 | 0 | -0.31021% | [-0.53254%, -0.08787%] |
| scale_extension | learned_no_query − ewma_no_query | 3/1/2 | -76.500000 | 0 | -0.28077% | [-0.36322%, -0.19832%] |
| scale_extension | history_structural − history_no_query | 1/0/5 | -26.000000 | 293 | -0.18202% | [-0.36403%, 0.00000%] |
| scale_extension | learned_structural − learned_no_query | 0/1/5 | 8.000000 | 290 | 0.06120% | [0.00000%, 0.12241%] |
| scale_extension | ewma_structural − ewma_no_query | 0/1/5 | 31.500000 | 287 | 0.06107% | [0.00000%, 0.12213%] |
| scale_extension | learned_structural − history_structural | 4/0/2 | -101.000000 | -3 | -0.34851% | [-0.41114%, -0.28588%] |
| scale_extension | learned_structural − ewma_structural | 3/1/2 | -100.000000 | 3 | -0.28012% | [-0.31953%, -0.24070%] |

核心 6 个地图×场景族；扩规模可执行结果仅 2 族，另 1 族初始规划超时。区间不能替代更大样本独立确认。
