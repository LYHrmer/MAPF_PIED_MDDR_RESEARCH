# R20 新场景共同轨迹的次级预测评分

冻结位置头在这组共同参考状态上的 delivery MSE/MAE 为 **0.737566 / 0.431722**，旧历史线性为 **0.866442 / 0.488850**。七个冻结预测器中，位置头的两项平均误差最低。这是**主矩阵启动后登记的次级诊断**，不替代完整规划结果，不证明查询政策最优、概率校准或普遍调度获益。

## 注册和范围

主实验于 2026-10-05 06:54:13 UTC 注册；本次评分于 **06:57:18 UTC** 注册，早于读取新科学 episode 数值，分析代码于 07:03:52 UTC 固定。模型仍为此前 06:47:18 UTC 已冻结的 R18 TRAIN 模型，没有重训、调参或按新结果换模型。所有模式事先指定，评分使用独立 SciPy 数学，未导入执行引擎、runner 或训练器。

只取每个 world 唯一的 `learned_linear_structural` 参考臂，共 **18 个完整来源、六个地图×scenario 族**；规模 N32，新 scenario8/9，扰动为稳定、pause duration range [2,5]、speed factor .65。不同政策访问的状态没有混合进评分。全18个参考均 completed，其中 **15个有查询**；三个零查询 world 原样保留在 [SOURCES](SOURCES.json) 与 [RESULTS](RESULTS.json)。

共有 **358 个真实 capture**，其中77个送达时已 stale，**281 个 accepted 且同 occurrence 仍 active 的 delivery**，以及 **281 个实际优化器消费点**。所有标签来自当前动作后续真实 END；未完成时按协议另存右删失，不改成零，本次删失为0。capture、delivery 与 consumer 是同一批过程的不同评分位置，不是三组独立实验；本数据的 delivery 与 consumer 位置完全重合。

## 统一输入和结果

各预测器使用相同实际 paid capture 进度、原 full-action nominal、START 相对年龄和 capture 前已交付 END 历史。当前或未来 END 仅作标签。history/ewma linear 与原 END 模型都保留。capture 评分是 age=0 的离线参考，不声称当时尚未送达的位置已经供执行器使用。

每族等权→族内有可评分世界等权→世界内行等权，零查询世界不伪造残余误差。每族/每世界结果均保留，误差单位与模拟器的时间单位一致。

| Frozen predictor | Delivery MSE | Delivery MAE | Bias |
| --- | ---: | ---: | ---: |
| end_ewma_survival | 1.095195 | 0.570473 | -0.281478 |
| end_learned | 1.133852 | 0.598336 | -0.336385 |
| ewma_linear | 0.886910 | 0.448225 | -0.259478 |
| history_linear | 0.866442 | 0.488850 | -0.307028 |
| observed_average | 5.219848 | 1.079791 | 0.753850 |
| position_constant | 1.033160 | 0.670356 | -0.113412 |
| position_learned | 0.737566 | 0.431722 | -0.157746 |

位置头相对旧历史线性在六族的 delivery MSE 均较低，逐有查询 world 为 **12 个较低、3 个较高**；MAE 在 maze scenario8 仍较差（0.361048 vs 0.339403），不能写成逐条件支配。位置头仍有负偏差 −0.157746，尤其不是校准结论。完整 capture/consumer、族和世界结果见 [RESULTS](RESULTS.json)，逐行输入、标签和所有预测见压缩 JSONL。

## 独立核验

[VERIFICATION](VERIFICATION.json) 从原记录核对358个 END 历史切割、查询正文 hash、连续轨迹的捕获位置，以及281个原优化器实际线性消费；920次部署头与独立 SciPy 结果之差不超过4.44e−16。[INDEPENDENT_CHECK](INDEPENDENT_CHECK.json) 未导入评分器，重新检查920行公共切割/未来标签、**6,440个模式预测**与**1,386项族/世界/整体加权指标**，全部通过。逻辑检查数不是独立样本量。

运行命令为 `python3 score.py --root R20_SCIENTIFIC_ROOT`，随后 `python3 check_scores.py`；没有新训练、solver 或 physical episode。来源路径和所有模型/代码/收据 hash 在注册、SOURCES 和发布清单中保留。本评分不能由更低预测误差直接推导更低 ΣT，root 的主矩阵配对规划分析才回答实际调度效果。
