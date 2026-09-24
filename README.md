# LMAPF 空间误差与执行占用引导探索

当前分支：`explore/error-aware-guidance`。从 `main@af17410` 建立，使用同一远端
仓库 `LYHrmer/MAPF_PIED_MDDR_RESEARCH`。本目录是独立 Git worktree。

| 分支 | 负责的问题 | 当前工作入口 |
| --- | --- | --- |
| [`main`](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/main) | PIE-D 误差执行、完整查询与实际费用闭环 | 主线当前进度 |
| [`explore/learned-query`](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/learned-query) | 在既有路径上选择查询对象，分离预测与组合决策 | 查询学习及合法 AND 预检 |
| **`explore/error-aware-guidance`（本分支）** | 固定空间误差安全层上，以执行占用/等待代价引导路径 | [误差引导探索](exploration/error_guidance/README.md) |

共同观察时机预检已通过 **3042 项断言**。非零误差下，t=2 的证书不足释放，
精确等号也不释放；t=5/2 观察使上绕恢复更快，t=4 则下绕更快。这说明本例的
路径排序取决于误差包络与证据时机，尚未证明学习有效。

结果与范围见 [时机预检](exploration/error_guidance/TIMING_PRECHECK.md)；
[夹具](exploration/error_guidance/timing_precheck.cpp)、
[运行器](exploration/error_guidance/run_timing_precheck.py)及
[完整证据](exploration/error_guidance/timing_run_20260924_01.json)可逐项复核。

下一步做“原 prefix / full-MOVE 授权 × 基础运动代价 / 加入解析等待代价”的
2×2 对照，先分离授权方式与等待估计的作用，再判断学习是否有独立收益。

本分支新增工作只放在 `exploration/error_guidance/`。继承的论文和历史文档是
分支起点快照；主线最新事实请看 `main`。主线未提交的主稿修改不属于这个分支。
