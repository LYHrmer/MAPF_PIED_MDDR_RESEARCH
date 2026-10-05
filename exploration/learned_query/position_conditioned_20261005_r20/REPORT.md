# R20 位置条件剩余时长模型

本轮已实现并冻结一个直接学习 capture 剩余时长的条件模型，仅复用既有 TRAIN 查询，不新增物理或求解科学实验。六族嵌套 OOF 中，送达时 MSE 为 **0.447765**，旧历史线性为 **0.481741**；新模型 MAE 为 **0.343056**，仍高于 EWMA 线性的 **0.285120**。这是选中查询点的预测证据，不是调度获益、概率校准或投稿资格证明。

## 数据与估计目标

来源为 R18 TRAIN 的 54 条唯一 history_rule 轨迹。49 个世界发生真实查询，共 **821 个 capture**；另五个零查询世界保留在来源清单，没有制造训练行。**110 个送达时已 stale 的 capture 仍用于训练**，避免只按未来存活筛选训练样本。711 个实际送达且同 occurrence 仍 active 的点构成主要评分；其后真实优化器消费位置的 solve 点也是 711 个，本数据中二者完全重合，不能算两份独立证据。所有源 hash、行和零查询世界见 [DATA_AUDIT](DATA_AUDIT.json) 与 [TRAIN_SOURCES](TRAIN_SOURCES.json)。

当前动作时长 D=END−START；START 前依赖 WAIT 单列，动作中暂停属于 D。标签 R_c=END−capture；当前位置 p、全段年龄 e_capture、原 nominal 与此前已送达 END 历史是唯一数值来源。未来 END 只作标签；地图、场景、seed 和私有扰动不入特征。当前 TRAIN 所有 nominal 都是 1.0，log_nominal 系数为零；因此其他物理时间/几何尺度的适用性未由这些数据识别。

模型拟合 log(R_c/nominal) 的 11 维 ridge AFT。R_c 直接作为完整剩余随机变量，不套用 (1−p)×整段时长，因此没有把固定暂停强制乘剩余路程。lognormal 是工作分布假设，不保证真实暂停服从该分布。当前位置送达后，若同 occurrence 尚未 END，则对 age=current−capture 计算：

`E[R_c−age | R_c>age] = exp(mu+sigma²/2) × S((log(age)−mu)/sigma−sigma) / S((log(age)−mu)/sigma) − age`。

age=0 使用完整 capture 剩余期望。原 e_capture、nominal、p 始终保留；不将原动作改为剩余路段。运行时不读取真实暂停/速度或未来 END，也不改变原 R19 END 模型的未来动作比值。

## 分组验证与结果

分析单位为地图/scenario 六族。所有同族规模和扰动留在同一折，族等权、族内有观察世界等权、世界内真实 capture 等权。外层六次留一，内层其余五族留一；标准化、sigma 和系数均仅用当前训练折。alpha 固定 [.01,.1,1,10]，内层实际 accepted-delivery 剩余 MSE 选模，1e−10 内取较大 alpha。六外层与最终均选 .01；共保存 85 个唯一训练折/alpha 拟合。原 END AFT 与 EWMA-survival 对照使用 R19 相应排除该 heldout 族的模型，未使用全 TRAIN 参数给 OOF 对照泄漏。所有方法均是内部参考，不能包装成外部发表算法。

| Predictor | OOF delivery MSE | OOF delivery MAE |
| --- | ---: | ---: |
| end_ewma_survival | 0.518851 | 0.345224 |
| end_learned | 0.513123 | 0.405334 |
| ewma_linear | 0.479594 | 0.285120 |
| history_linear | 0.481741 | 0.359232 |
| observed_average | 1.543711 | 0.472537 |
| position_constant | 0.600451 | 0.501609 |
| position_learned | 0.447765 | 0.343056 |

完整结果见 [RESULTS](RESULTS.json)、[CV](CV.json) 和逐行 OOF 文件。相较 history_linear，新头在六族中五族的 delivery MSE 较低，但 warehouse scenario2 为 1.227436，高于旧线性 1.145858；总体改善不表示逐族获益。最终 sigma=0.3401918516。最终选择不因某个对照在 MAE 更优而改动。

## 已消费 R19 开发诊断

冻结后另注册 [development_r19/REGISTRATION](development_r19/REGISTRATION.json)，每世界只取一个共同 learned_structural 轨迹，避免混合不同策略状态或把重复前缀当独立样本。42 个来源中，核心36个世界有28个发生查询，390个 accepted delivery；N64六个可执行世界有244个。原 N64 maze 三个初始规划失败世界没有替换。

核心位置头/旧线性 delivery MSE 为 **0.526310 / 0.569987**，N64 为 **0.287023 / 0.343349**。EWMA 线性 MAE仍优于位置头：核心 **0.405409 / 0.434292**，N64 **0.243491 / 0.284415**。每个模式共用同一原始查询、公共历史和事后标签，按族→世界→行等权。全部七模式的数学另外由 SciPy 复算。详见 [开发诊断完整结果](development_r19/RESULTS.json)。R19 已被消费，这不是新 TEST，不用于改模型、阈值、alpha 或 root 的新场景矩阵；预测误差仍不等于调度收益。

## 机械验收与交付

[VALIDATION](VALIDATION.json) 的 **28,801** 项检查通过：54 原始来源、821 个 capture 真实物理位置与 query body hash、公共 END 切割、22 个带非零依赖等待的查询、85 个正规方程、所有折分离与 alpha 规则、**15,701** 条 OOF 模式预测及 runtime 一致性。最大正规方程残差 4.44e−16，OOF 数学差 2.09e−14，runtime 与独立 SciPy 差 8.88e−16。九个非法输入负控全部拒绝；零进度有效，p=1 尚未 END 不制造完成，COMPLETED 不读其他字段直接返回零。当前 occurrence 很老的位置允许基于未 END 事实更新；跨 occurrence、未送达、非法时间被拒绝。

部署入口和字段见 [PUBLIC_SCHEMA](PUBLIC_SCHEMA.json)。最低运行文件是 `MODEL.json`、`position_predictor.py`、`end_predictor.py`；后者是原 R19 算术实现的原字节副本。`PINNED_END_MODEL.json` 为原 END 模型对照和未来动作来源，位置头本身不需要加载它。独立 `independent_math.evaluate_position(context, model)` 仅依赖 SciPy/math，不导入训练器或部署头，可直接供执行审核器复算。模型与代码 hash 在 [MODEL_FREEZE](MODEL_FREEZE.json)，完整发布清单另存。

API 的算术校验不能认证上层伪造的 START 时间或历史；实际引擎必须另绑定 occurrence、geometry、capture/delivery、已交付 END cut 与原始事件。模型输出是预计时间，不是物理安全证书。后续新场景只能由 root 在模型/机械验收后另注册运行；本目录没有新增科学 episode，也未改任何 R18/R19 冻结工件。
