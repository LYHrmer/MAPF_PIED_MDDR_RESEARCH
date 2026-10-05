# R19 条件动作时长：资格与事前设计卡

状态：用户明确授权的探索性研发原型，不代表选题或投稿资格通过。按 research-mentor 资格门先登记本卡，随后实施。模型效果未知；不得用 R18 CAL/TEST 重选模型。

| 资格项 | 判定 | 可定位依据与范围 |
| --- | --- | --- |
| 通俗问题合同 | PASS | 执行器用已完成动作历史估计当前动作何时结束，但动作已持续很久仍未结束时，直接减去 elapsed 会给出零剩余时间。本轮估计公共历史条件下的时长分布，再给出“尚未结束”条件下的剩余期望；预测误差与完整调度后果分别评价。 |
| 学科与已发表锚点 | PASS（底座范围） | R18 作者 SADG 代码 pin c2626d996121a9d6c128844a167b917db24418ac、原作者优化器及标准地图结果已核；NEXT_METHOD_DESIGN.md 指定残余预测扩展点。本轮不声称文献新颖性。 |
| 官方工件 R0 | PASS（复用） | R18 ENGINE_VALIDATION.json / ENGINE_NOTES.md，作者原生 optimize 与共用合法方向/物理执行核验已完成；新预测仅由 R19 adapter 接入，不修改 R18。 |
| 外部基线 | UNKNOWN（论文层面） | 原作者底座已有，但本模型的常量、比例、recent/EWMA 均明确内部消融；不包装成已发表外部算法。探索授权允许隔离实现，不能据此宣称论文方案通过。 |
| 数据可得性 | PASS | 仅 R18 episodes/TRAIN/*/history_rule 的 54 个世界，每世界一条轨迹；公共 START/END、完整 delivery history 和 gate snapshots。六个 map/scenario 族完整分组，反事实前缀不重复采样。 |
| 纯仿真闭环 | PASS（研发范围） | 条件模型冻结交 R19 SADG 执行新预注册 TEST，评价完整完成时间/查询成本/失败；预测误差本身不代表调度改善，实机动力学不在结论内。 |

## 冻结训练规则

1. 只读取上述 TRAIN history_rule 原始 episode 和 RUN_RECEIPT，校验文件 hash 和 split。每 (world, agent, occurrence) 仅一个完成动作标签。已交付先前 END 构造特征，当前与未来 END 仅作监督；私有扰动、map、case、seed、族名、位置真值不作特征。族名只用于分组和加权。
2. 时长 D=END−START，包含动作中的驻留/扰动暂停；依赖阻塞 WAIT=START−前次 END 单独记录，绝不加到动作 D。名义时长来自该 occurrence 的公开几何。所有完整终止轨迹无终端删失；执行中 landmark 表示 D>elapsed 的存活信息，不将 elapsed 当已完成标签。若存在缺 END，停止本拟合而保留为显式终端删失记录，不能伪造完成。
3. 学习 log(D/nominal) 的低维 ridge AFT，条件分布为 lognormal，残差 sigma 下限 0.05。特征：log nominal、log1p 历史数、log 全历史时长比例、log 最近4比例、log EWMA(0.3)、log 最后一次比例、历史 ratio CV、最近4与全历史 log 比例差。标准化只用各训练折。
4. ridge alpha 候选固定 [0.1,1,10]，归一化族/世界权重下的二次损失加 alpha×系数平方，截距不罚。每族等权、族内世界等权、世界内 occurrence 等权。外层六族留一；内层在剩余五族留一，按 active gate 剩余时长的族/世界平均 MSE 选择 alpha，差≤1e-10 时取较大 alpha。最终在全部 TRAIN 六族 LOFO 选择，再拟合全部 TRAIN。
5. 无历史名义常量、全历史比例、最近4比例、EWMA(0.3) 均提供直接均值减 elapsed 参考。另有训练常量 lognormal，以及全历史/recent/EWMA 均值配训练 residual sigma 的 survival 条件参考。上述全部是内部参考。学习模型不因对照获胜或失败而取消交付。
6. 条件预测 E[D−e|D>e]=exp(mu+sigma²/2)×S((log e−mu−sigma²)/sigma)/S((log e−mu)/sigma)−e。e=0 返回完整期望。计算使用稳定 log-survival；不提供无根据的概率校准声明。
7. 评价所有 action START 时的完整时长误差与既有公共 gate 上 active occurrence 的剩余误差，按族/世界平均 MAE/MSE。保存逐 occurrence/landmark OOF 预测、所有折边界/参数/选择证据。gate 出现多个年龄不视为独立科学样本；独立分组仍为六族。
8. 最终 predictor.py + MODEL.json + model/code hash 冻结交 R19 执行器。调用只接受公开 END/START 所需字段，POSITION 不进此模型；融合由执行 adapter 另登记。R18 既有 TEST 已开发不可再当新独立 TEST。本目录不运行科学 episode。

## 公共接口与主线桥接

`DurationPredictor(model_path, mode='learned')(context)`，输入 `status, nominal_duration, elapsed, completed_history`，其中 history 每条至少 `nominal_duration,duration`，可带公开 `start,end,delivered`。输出 `remaining_time, future_duration_ratio, metadata`。agent/occurrence 只作来源绑定，禁止进入特征；模型忽略 POSITION。

主线未来应绑定 world/geometry/occurrence 身份、公开 START 时间、当前 tick/elapsed、END capture/delivery 和 history cut、模型与实现 hash。输出是估计而非安全证书；合法候选、预算、当前位置证据及付费收据由原闭环负责。
