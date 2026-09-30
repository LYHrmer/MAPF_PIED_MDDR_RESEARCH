# 冻结有限预算官方训练与独立留出协议

2026-09-30，首次训练 ask/evaluate 之前。原800 agents/1000 ticks运行量测约12秒完成，
因此保留作者规模，以12个独立进程并发执行；每 native 120秒时限。

固定复用官方四个完整源码类：GridArchive、CMAEvolutionStrategy、
EvolutionStrategyEmitter、Scheduler；不改算法源码。官方quad560权重、初始均值5、
sigma5、5 emitters、每个batch20、ranker=obj、selection=mu、restart=basic、
默认bounds(0.1,100)、官方默认边界处理、float32 archive、原地图/任务配置不变。
保留官方在100次重采样后仍可能输出越界参数的行为，逐代记录，不事后修剪。

本机有限训练预算为2代共200个候选，每候选2个独立训练seed，共400次native。
这小于作者配置10000候选，不能称作者完整论文R0。优化器总seed930031；
按原Manager方式生成archive/emitter/evaluation seeds；按ask的固定索引tell，
绝不按异步完成顺序重排。两个目标取原throughput算术均值，measures同作者为[0,0]。
本地串行协调+进程池替代Dask调度，不更改候选或目标规则。每代保存全部权重、
训练seed、原始结果/日志、目标、CMA更新后的状态摘要及完整本地checkpoint。

第二代完成后只依据训练archive最大平均吞吐冻结一个best checkpoint。
留出seed固定[930101,930103,930107]，不得出现在训练seed集合内；
best和初始全5各跑这3个seed，保存完整路径独立检查。留出结果不得用于选checkpoint、
增加代数、调参数或换场景。记录每次个体值和均值，不做显著性或跨图泛化宣称。
作者部分内部优先级使用random_device；同任务seed不能假定所有内部随机性相同。

失败、非有限目标或timeout中止该训练attempt，原始失败保留，不把失败吞吐当0继续。
无任何误差扰动或我们自己的新学习方法；这一步建立可训练官方外部对照。
后续执行误差残差模型需要独立数据/训练协议和同信息对照，不能把复现作者模型写作创新。

运行环境Python3.10、gin-config0.4.0、pyribs0.5.0与作者相同依赖版本；
NumPy1.26.4/Numba0.60.0为本机Python兼容差异，非作者完整容器。
native二进制继承已审计OBJECTIVE4构建，系统Eigen3差异照实保留。
