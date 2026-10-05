# R19 作者 SADG 条件残余与结构查询资格卡

状态：**仅获准接口开发与 R0 机械资格验证；科学矩阵待 root 预登记。** 日期：2026-10-05。

导师判断：R18 的学习增益稀疏，且大部分学习查询未覆盖即时公开阻塞/合法可切换机会。下一项应同时检验条件剩余时长、可改变排序的结构与 STOP；仅扩大回归器不足以回答查询价值问题。R18 TEST 已消费，仅可用于开发诊断，不能作为 R19 的新检验样本。新场景/拆分/最终臂由 root 登记。

- 作者仓库 SHA 保持 `c2626d996121a9d6c128844a167b917db24418ac`；AGPL3；原 SADG.optimize 与 60 秒上限不改。
- 基于冻结 R18 engine `7a83912d7fbefa8122ed551cab2ce93a536e6efafc3ebaf0b1e0dbb99eff12f6` 继承物理事件、完整 END、dated POSITION、cursor、共同 adoption guard、碰撞审计与失败分母。隔离 R16 k0/all-head compiler 保留。
- 新增输入适配仅影响 duration/progress 预测与查询；原 IN_PROGRESS 承诺及执行 guard 无新增估计权限。
- 新模型由 query agent 仅从预先允许的已交付 END 历史训练并冻结；本目录不训练模型，不接触新 TEST。
- R0 上限：最多 2 次作者 native optimize，仅人工单动作/小例验证接口、残余编码和 exact-cache；其余为零 solver 机械测试。所有尝试/失败保留，不计科学结果。
- 优先交付可测最小接口、结构政策、CAS、失败 payload 与审计桥接；未知科学效果不承诺。
- 不修改 R18 冻结 source/raw，不 commit/push；新科学矩阵、参数与模型绑定由 root 统一冻结。

公共 predictor contract：`predictor(context) -> {remaining_time, future_duration_ratio, metadata}`。context 固定为 `status, nominal_duration, elapsed, completed_history`（每条 nominal_duration,duration,start,end,delivered）；历史只包含已交付 END。agent/vertex 只作日志 provenance，不作为拟合特征。无世界标签、私有扰动、seed、未来时长、真实 decision progress。

POSITION 融合（root 已确定）：当前 occurrence 有已交付捕获时统一采用原 R18 `remaining=max(0,(1-captured_progress)*original_nominal*all_END_history_ratio-(now-captured_time))`，显式记录 provider 切换。无当前位置时使用所选 END 条件模型。不会实现或评估剩余路段 nominal 重标，不声称联合条件后验。

作者编码：STAGED `duration=original_nominal*future_duration_ratio`；active `duration=max(original_nominal*future_duration_ratio, remaining_time, EPS)`、`progress=1-remaining_time/duration`。两者满足非负残余和归一化 progress；残余大于 unconditional duration 时的显式扩张会留证。COMPLETED duration 为已交付 END 实际时长。

root 确定的对照方向：history/learned/EWMA-conditional 三预测器 × no-query/structural-STOP 两查询模式，另 history/fixed、history/history-rule；N64 保留六因子臂。最终数据、数量和参数以 root 预登记为准。相同臂共享公开历史、solve cadence、query cap 与共同执行 guard。
