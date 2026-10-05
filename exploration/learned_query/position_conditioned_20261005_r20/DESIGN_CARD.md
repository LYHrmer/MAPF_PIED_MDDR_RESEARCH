# R20 位置条件剩余时长：资格卡与事前协议

研究状态：探索性研发原型，不代表选题或投稿资格通过。沿用 research-mentor 的资格门与前置验证；用户明确授权隔离实现。本目录不运行科学物理或求解实验，也不修改 R18/R19 冻结工件。

| 资格项 | 状态 | 证据与边界 |
| --- | --- | --- |
| 通俗问题合同 | PASS | R19 POSITION 到达后用旧线性历史投影覆盖 END-only 模型，可能把动作中固定暂停误按剩余路程缩放。本轮直接学习 capture 时剩余执行时长，再按当前尚未 END 的事实更新；预测误差和后续完整调度效果分别评价。 |
| 学科与已发表锚点 | PASS（底座）；新颖性 UNKNOWN | R18/R19 固定 SADG 作者 c2626d996121a9d6c128844a167b917db24418ac 与原优化器已实测。R19 review_r19/INTEGRATION_REVIEW.md 定位旧融合算子；本轮不声称新的已发表算法或首次提出。 |
| 官方工件 R0 | PASS（继承）；新融合待验 | R18 ENGINE_VALIDATION.json、R19 324 次完整审计与原始运行保留。新模型只替换当前位置残余估计，不改变作者合法执行逻辑或未来动作预测。 |
| 外部基线 | UNKNOWN（论文层面） | SADG 是执行底座；本轮历史线性、END AFT、EWMA 与观测规则均是内部诊断对照，不能包装为外部标准算法。 |
| 数据可得性 | PASS | R18 TRAIN 的 54 条 history_rule 唯一轨迹有真实已付费 capture、delivery、START/END、原 nominal 与公共历史。只用这些 TRAIN；不读取 R18 CAL/TEST 拟合或选择。 |
| 纯仿真闭环 | PASS（研发设计） | 本轮拟合、族分组 OOF、机械验证和冻结；新执行矩阵由 root 另注册。R19 已消费，仅可作开发诊断。点机器人、有限任务、执行器适配不等于实机安全、无限任务或概率校准。 |

## 预登记模型与数据规则

1. 每个 R18 TRAIN world 只读取 history_rule 的完整 episode 和 RUN_RECEIPT。核 TRAIN/scenario1或2、hash、真实查询 capture 与合法公共 START/END。保留全部 54 世界来源，零查询世界不制造训练行；分组为地图/scenario 六族。地图/族/世界/seed/扰动只用于来源、分组或描述，禁止作为特征。
2. 每个真实 capture 一行，key=(world,agent,occurrence,capture)。标签 R_c=END−capture>0，来源当前动作事后 END；动作执行 D=END−START 含动作中驻留，排除 START 前依赖 WAIT。capture 特征只含该时刻合法可见信息。已捕获但送达时 stale 的点仍参加 capture 拟合，防止按未来存活选择训练样本。终端无 END 时记录删失并停止本拟合，不能伪造完整标签。
3. 位置学习头预测 log(R_c/nominal) 的 ridge AFT，lognormal 残差 sigma 下限0.05。直接学习完整 capture 剩余，不把固定暂停乘 (1−p)。固定特征为 log nominal、progress p、log(max(1−p,1e−6))、log1p(captured_elapsed/nominal)、log1p(history_count)、log 全历史比、log EWMA0.3比、log 最后动作比、history CV、log1p(max(0,captured_elapsed/nominal−p×EWMA比))、p×log1p(captured_elapsed/nominal)。不用已知扰动阈值或时长。
4. 每族等权→有观测世界等权→世界内 capture 等权。外层六族留一，内层其余五族留一；全部标准化只用训练折。ridge alpha=[0.01,0.1,1,10]，截距不罚。内层按真实送达且当时仍在执行的同 occurrence 行，族/世界平均剩余 MSE 选 alpha，差≤1e−10 取较大 alpha。最终按全部 TRAIN 六族 LOFO 选 alpha 并拟合。捕获 OOF 与实际后续 solve 消费误差另列，不增加选模目标。
5. 对比 position_learned、训练常量 capture residual survival、history_linear、ewma_linear、原 END learned、强 END EWMA survival、observed_average。observed_average 在 p>1e−6 时以 captured_elapsed×(1−p)/p 减 age，p≈0 回退 END EWMA survival；规则不利用私有暂停/速度。原 END OOF 对照只用 R19 CV 中排除对应 heldout 族的模型，不能拿全 TRAIN 模型评价该族；真实部署未来动作继续原冻结 R19 END 模型。
6. 运行 age=current−capture。预测 E[R_c−age|R_c>age]，保留 capture 时原全段年龄 e_capture、原 nominal 和原 p；不把 age 作为已完成标签或将原 nominal 改成剩余路段。使用稳定 log-survival 数学。COMPLETED 返回0；STAGED、跨 occurrence、位置未送达或时序非法必须拒绝并由上层使用 END fallback。零进度是有效位置，不除以0；p=1 但尚无 END 也不能制造 END。
7. primary 是按真实已送达查询条件的族加权预测 MSE。原 query policy 选择的数据不是随机位置样本，无法证明新 policy 的无偏总体性能。模型预测分布是工作假设，不宣称概率校准。OOF 只证明既有 TRAIN 族间可迁移预测，不等于新 TEST，也不证明调度改善。R19 已消费诊断必须单独标识且不得影响冻结选择。
8. 保存所有源 hash、行级 OOF、族界限、每折训练参数/权重/正规方程、选择规则与所有对照。实际独立核验原事件切割、数学、runtime/离线一致性和负控；不重跑旧物理/求解实验。完成后交 MODEL.json、position_predictor.py、PINNED_END_MODEL.json、end_predictor.py 和冻结 manifest。

## 引擎接口

`PositionPredictor(model_path)(context)` 输入 `status,occurrence_id,nominal_duration,elapsed,completed_history,position`；position 为 `occurrence_id,progress,captured_elapsed,age,delivered_age`。completed_history 是 capture 前同 agent 已送达 END 列表，每条仅以 nominal_duration/duration 入特征。上层完整保留公开时间戳、geometry/occurrence 和真实 delivery 证明。active 校验 elapsed=captured_elapsed+age，0≤delivered_age≤age，同 occurrence，p∈[0,1]；输出 remaining_time 与 metadata，不改变 future_duration_ratio。身份只作绑定，不入模型。无 POSITION 时不调用新头。机械拒绝非法输入不能替代上层完整日志审计。
