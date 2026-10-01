# R7 独立实作判断

只读 R6 报告、R6e HANDOFF 与源码，未读本轮导师或 root 结论。

1. 主线：复制 R6e，沿 `full_profile.cpp::run_role` 的 owner/demand 与 `driver.cpp::Session::run`，做同输入 WAIT／付费 POSITION 配对。保留证书退休、后车 cap/RUN、四 terminal、收据及下一选择；补原 MOVE 到端点时间与正常公开 END。无生产任务接口则另列目标内静止封装，明确 fixture，不能叫作者 STATION。比较阻塞、正常 END／任务完成时间和实际费用；统一 8m 供给不等于费用或 1m 成功。

2. query：复用 `official_bridge.cpp` 的持久 MAPFPlanner 与 OneGoal 当前 head FIFO；替换 `World3` 静态路径输入，保留 Geometry、PositionCommit 与异步 MOVE。从合法公开离散提交状态规划，已执行／在途承诺不可改；可先保持作者全局依赖，允许尚未 END 的无冲突后继执行。不能复制 joint-settled 屏障。新整运行拆分，按预定多候选机会生成 query／WAIT 边际标签；同任务误差预算比较 WAIT、RR、条件规则、有／无历史，记录选择改变与服务。

3. third：保留共同 S1，新增只读已交付 END 历史的剩余耗时／超额执行损失预测器，送入真实 guidance 排序。新训练运行拟合，新任务／误差种子留出；hm、旧模型、无历史／有历史新模型共用执行与时限。主指标正常 STATION END、删失任务与开销，辅以预测误差、动作改变及 barrier 等待。屏障下可检验引导收益，失败不能否定局部查询价值。

## 本地源码依据

- main：[R6e HANDOFF](../../../MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/receipt_word_successor_20261001_r6e/HANDOFF.md)；实际路径 `/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/receipt_word_successor_20261001_r6e/{driver.cpp,full_profile.cpp,pipeline.cpp}`。
- query：`/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_joint_20261001_r6/{REPORT.md,joint_history_native.cpp}`，重点 `start_ready/service_heads/deliver/candidates/queries`。
- third：[REPORT](published_continuous_execution_20261001_r6c/REPORT.md)、[official_bridge.cpp](published_continuous_execution_20261001_r6c/official_bridge.cpp)、[run_trial.py](published_continuous_execution_20261001_r6c/run_trial.py)；实际 FIFO 源 `/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/published_continuous_execution_20261001_r6c/lsmart_successor/server/src/task_assigners/OneGoalTaskAssigner.cpp`。
