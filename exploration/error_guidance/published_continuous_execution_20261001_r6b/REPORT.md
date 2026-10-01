# R6b 合并修复与坐标预检

本版关闭两处半 MOVE 合并入口，实际函数回归由失败转为通过，见 [merge_regression_pass.json](merge_regression_pass.json)。随后输入坐标预检在 252 项中发现 244 项不一致，见 [geometry_preflight_failure.json](geometry_preflight_failure.json)。

R6b 未运行 native 矩阵，不报告任务吞吐或学习性能。保留冻结的源、编译回执、全部共同输入及失败预检，供对照 [R6 原配置](../published_continuous_execution_20261001_r6/REPORT.md)与 [R6c 坐标修复](../published_continuous_execution_20261001_r6c/REPORT.md)。三个版本都不通过修改既有结果来掩盖适配问题。
