# 旧 checkpoint 映射审计登记

公开规模检查显示预选 warehouse checkpoint 有10853个访问状态、15789条原type2；random checkpoint有1421个访问状态（精确数量以输出为准）。为把本轮保持在最小机制预检，改为审计 R14 `random-32-32-10__t1_2__axis_slow`；该调整发生在任何旧 checkpoint SADG 求解之前，仅依据公开规模，不按响应结果选择。该例的旧测量目标是agent14，公开进度2/5、测量1/3。

固定映射：原路径每个相邻单位MOVE映射到一个作者动作；坐标以2米/格转换，作者2米/秒给1秒名义时长；已 ARRIVE 的动作 COMPLETED，原active MOVE对应 IN_PROGRESS，其他为 STAGED。只读 R14 public / views / evidence，不读未来事件堆或扰动实现。连续剩余采用作者原 `(1-progress)*nominal_duration`；这不会自动等价于R14的速度估计残余，更不包含STATION/TURN。

先核完整type2关系族与当前承诺。如果作者 compiler 生成的关系族不能完整映射回 R13 guard，保留全量差异并停止共同执行采用；不借移除guard推进。最多追加公共/测量两个作者核心诊断输入，但只有映射资格通过才运行。若未通过，本轮仍以已登记小例证明原作者连续机制实际响应，旧 checkpoint 留作接口阻断证据。
