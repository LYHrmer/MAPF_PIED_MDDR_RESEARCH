# R6 原配置运行记录：不进入算法性能比较

原配置实际执行了全部 24 组，不再沿用“尚无 native”的中间状态。两项共同适配错误使本批全部不具备主指标资格：S1 只关闭 insertActions 的半 MOVE 合并，updateQueue 仍可合并；输入几何用了 (-col,-row)，而作者 flipped_coord 控制器对应 (-row,-col)。

12 组 empty 运行达到 8000 ticks，但原始动作映射/点 ACK 审计失败；12 组 random 在第一次规划报告 `error in aStarOF: no path found 937,513`，未产生合法决策。全部结果、退出与部分服务保留在 [summary.json](summary.json)，主性能值全部为 null。不能把这些适配错误记作 hm 或学习方法的规划失败率。

[invalid_configuration_diagnosis.json](invalid_configuration_diagnosis.json)保留首视图的初始映射、实际合并 MOVE 与点误差证据；[merge_bug_reproduction.json](merge_bug_reproduction.json)是实际 C++ 函数复现，未计作完整仿真实验。[archive_manifest.json](archive_manifest.json)收录 24 组的 168 个原始文件，原始 1,192,954,837 bytes，经四个固定地图/规模归档保存并逐成员回读校验。

冻结源、输入、版本与失败记录均保持。R6b 先修合并并在坐标预检失败后停止；[R6c](../published_continuous_execution_20261001_r6c/REPORT.md)在同地图、任务流、方法、种子、时长与扰动矩阵下共同修正坐标后重新冻结。二者属于公开共同适配修复，不是根据算法胜负筛选场景。
