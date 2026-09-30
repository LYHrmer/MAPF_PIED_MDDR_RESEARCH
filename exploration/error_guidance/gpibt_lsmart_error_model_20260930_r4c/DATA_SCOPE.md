# R4c 输入、监督与可见性

模型为已冻结R4 ridge residual λ1，102 train完整MOVE、48 cal完整MOVE，按完整run切分；本包不拟合、不校准、不选择权重。checkpoint SHA `16fac44d6d23c7c472a5caed4bdce87ba19bca632e6a70f7fa16a9ccf14c8094`。同一公开历史/候选轴函数提供给zero、analytic、history、learned及两个常量消融。

九维feature为analytic_ticks、agent_median、axis_median、last_duration、max_command_cm_s、mean_command_cm_s、same_last_axis、history_count、axis。只从本world决策时已交付的proposal/admit/最终整格END、实际发出的轮速命令构造；轴来自当前公开goal与地图的合法目标递减邻居。无私有pose、未来FIFO列表、未来扰动名称/倍率/剩余时间。真实pose仍用于各臂相同的joint-settled同步条件和离线物理核验，不能说整套同步接口从不读取pose。所有live `forecast.context.freeze_sequence` 和当前view绑定，只有此前正常整格END进入历史。

analytic实际使用最近已完成MOVE的最大已交付轮速，配公开加速度/距离计算运动下界并加固定10tick轮询余量；history使用同agent同axis最近三个完整运动时长的中位数及公开fallback；learned使用全部九维，经旧train标准化和冻结ridge修正analytic。三者都获得同样context，实际利用的量不同。常量消融bias固定为[+1,-1]或[-1,+1]，不使用预测来选偏好。zero不施加bias。

目标 `first_nonzero_command_tick→normal_full_MOVE_END_tick` 是一次原始1m网格MOVE的运动段，最终节点才是标签；中间半MOVE ACK不是整格标签。转向/排队/派发占用不在该目标内。每行额外给出proposal_received、first_native_dispatch、各自到whole_END的总时长，以及proposal到first_nonzero的间隔。不能把该模型解释成总占用周期模型。

每run `datasets/<run>/delivered_context.jsonl` 与 `offline_original_MOVE_targets.jsonl` 按key配对，共942行：884正常END、58删失null，绝不把未完成当0。`active_delivered_context.jsonl` 与 `offline_remaining_targets.jsonl` 共57,378行，输入仅step-start已交付历史、当时已交付轮速、当时已发生的elapsed，目标才含未来完整END及remaining。END后remaining=0仅由标签可说明；右删失remaining=null。活动行保留至下一proposal，因此包含转向、运动、服务或已完成后的阶段，不能把每行都称为活动MOVE；`active_nodes`、当前命令和END_already_delivered可区别。活动剩余预测没有用于mid-MOVE规划，实际决策点仍joint-settled。

`dataset_audit.py/json` 不调用export或common的context/public_steps/features，独立从raw重建整格final节点、first_command、END、proposal/dispatch占用、历史feature、tick输入/target及FIFO prefix，36run全通过。`audit.py/json` 重放真实parser/ADG/原ACK、服务20tick、owner/id、末pending、完整800tick、1600pose/轮速、live forecast及p/p_copy aging恢复；108个私有pose feature、错误bias、未恢复aging篡改负例均拒绝。原ACK谓词和更严格半节点点距离分别报告。

主要任务指标是正常STATION END服务数，包含已真正服务但尚未在下一view登记bookkeeping的末任务。stats里的已登记数会晚一个view，不能当真实吞吐差。所有服务时间按owner+FIFO ordinal匹配，不用异步分配后的全局task_id硬配；未完成保持删失。`summary.json`保留所有匹配时间及各agent前3项里程碑，不把某一个提前时间挑成总体收益。完成才释放下一任务的流量不适合用已释放任务总停留时长自造优化指标。
