# R5：四张官方地图的共同任务流真实试跑

事前固定四张MovingAI地图、每图官方random-1.scen前64个机器人、1000步、任务流seed930301；hm+GPIBT与冻结OnlineGGO模型各运行一次，共8次native，全部退出0、无重跑、无弃样。两方法读同一起点、首任务和完整逐agent FIFO流，作者FixedAssignSystem每agent最多揭示1项，完成时各自揭示下一项。

| 官方地图 | hm+GPIBT完成任务 | 冻结OnlineGGO完成任务 | learned−hm任务/步 |
|---|---:|---:|---:|
|empty-32-32|2745|2678|−0.067|
|random-32-32-10|2673|2620|−0.053|
|maze-32-32-2|932|946|+0.014|
|room-32-32-4|1866|1908|+0.042|

结果有正有负；每图仅一次配对、内部priority随机平局未控制，不能作统计优越结论。模型来自原sortation_small_kiva的200候选有限训练，560参数逐值保持，无新训练或地图后调优；这是向这些地图的transfer pilot，不能代表足额10000候选训练后的作者方法上限。没有本项目执行误差模型参与，没有LSMART或物理误差，不证明新方法收益或连续安全。

地图和场景原字节来自[MovingAI官方MAPF benchmark](https://movingai.com/benchmarks/mapf/index.html)，hash匹配已登记原zip及100场景registry。保留Moving AI Lab/Nathan Sturtevant及其[Open Data Commons Attribution许可来源](https://movingai.com/benchmarks/)。官方场景只给起点/首任务；后续工作负载是本次公开适配：每agent独立RNG在自身可达自由格中均匀抽取且排除前一目标，总1002项/agent，在首个native前完整冻结。该后续流不是官方场景的原生长期任务集。全部输入重生成逐值一致，各run最少仍有951项未揭示，未因任务耗尽抬高吞吐。

规划器是[OnlineGGO作者代码](https://github.com/zanghz21/OnlineGGO)ff6d830e2fd5bf85ccbb72eaec0fb8df1cf1c256：沿用已构建OBJECTIVE3 SUM_OVC hm+GPIBT与OBJECTIVE4 quad560模型模块、冻结R3 checkpoint及原native_worker。模块SHA、原构建provenance、checkpoint/worker/原939源blob及3子模块引用身份、所有输入和8jobs均绑定到`freeze.json`，运行前后保持。子模块内容未重新审计，未修改或仿造作者搜索。除了共同map/instance、64agent、64128任务、seed与FIFO输入，两臂kwargs只在network_params及输出路径不同；完整参数在归档job.json中。

`verify.py`独立重放512,000动作、512,512联合位置，通过四邻接/障碍、每步顶点冲突及交换边冲突、唯一任务派发、当前任务FIFO、真实到达/完成、未揭示尾部、吞吐与全部冻结hash检查。作者FixedAssignSystem的重复任务定义按原raw保留，恰好对应已揭示项，定义相同且并非重复派发。八臂native/audit失败均为0；全部原输入、trace、日志、job/result/receipt lossless压缩，成员hash见`archive_manifest.json`。

本包完成官方地图上的方法兼容性和共同任务流落地，不是全benchmark。后续仍需预注册多场景、密度/机器人梯度、训练域/预算与执行误差条件，不能把本次单seed差值、数十万动作数量当独立重复或误差闭环收益。`summary.json`保留逐图结果与这些边界；`run.py`拒绝覆盖，真实重跑须另立目录。
