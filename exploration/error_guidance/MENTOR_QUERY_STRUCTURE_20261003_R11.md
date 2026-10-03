# R11 导师只读补充：coupled 机会是否可达

结论：在当前 World3 的单位 cardinal MOVE、独占单位 cell、每 robot 一个当前请求、合法联合计划与 `last_depart` 门槛同时成立时，`owners > 1` 和一个候选具有多个当前 blocked-head claim 都受到结构排除。四个 family 没出现 coupled 不是这个结论的依据；依据是下面的几何与依赖推理。本判断不改变 R11 登记，不新增运行，也不把该结论推广到一般 PIED/MAPF。

只读源码：查询 R11 `joint_history_native.cpp` 的 `geometry`（约 238 行）、`replenish`（约 256 行）、`rebuild_demands`（279 行）、`start_ready`（295 行）、`deliver`（341 行）和 `candidates`（371 行）；原 `implementation/pie_query/include/pie_query_index.hpp` 的 `rebuild`（约 397 行）。查询编译入口 `runner.py` 从已固定的 `legal_and_sources.json` 取得该 Index 原源。

## 单请求最多一个外部 owner

几何不是半径 .15 的圆盘：代码使用半宽 .1 的轴对齐正方形 footprint，加半宽 .05 的误差盒，得到有效轴向半宽 .15。单位 cell 半宽 .5。一个整数中心到相邻整数中心的水平或竖直 MOVE 的完整 sweep 只与起点 cell 和终点 cell 相交；它接触不到旁边一行或超出两端的另一格。闭边界约定不改变这个结论，因为 .15 严格小于 .5。

`rebuild_demands` 只为 `ready` robot 的下一项 MOVE 产生一个请求。`ready` 在正常 END 接受后恢复；该 robot 当前中心所在的起点 cell 保持为它自己的 resident owner。Index 重建关系时跳过 `owner.agent == demand.agent`，并按外部责任聚合。因而 source 不产生外部关系，唯一的 destination cell 又只有一个排他 owner。这个请求至多产生一个外部 owner relation。凡是进入候选 claim 的请求，至少有该候选的一条可退休关系，所以其 `owners` 恰为 1，而不是可能大于 1。

## 一个候选最多阻塞一个当前请求/head

候选是一个已 RUN、尚未 normal END 的单位 MOVE。其 destination 是 endpoint-retained，不可通过 POSITION 退休。因此它给候选 claim 提供的可退休格只能是 source。要让一个候选关联两个请求，就必须同时存在两个可见的下一步请求，都想进入同一个 source cell。

单独的每轮 `unique endpoints` 检查不足以排除这种情况：异步执行可能让不同规划轮次同时有未执行动作。还要用 `last_depart` 和实际执行门槛。对同一 cell，把合法联合计划中各次进入按规划顺序排列。因为每轮终点唯一，后一次进入之前，前一次进入者必须先有一个离开该 cell 的计划动作。`replenish` 记录该 cell 最近离开动作，并把它存到后一次进入的 `deps`。只有这个离开动作已经真实加入 `launched`，`precedence` 才允许后一次进入生成需求。

若前一次进入还在等待该候选释放 source，则进入者连这一步都未能 RUN，更不可能完成它、接收 normal END、变回 ready 后再 RUN 离开动作。故后一次进入的离开前驱还没 launched，它不能进入 `rebuild_demands`。若两次进入属于同一 robot，一个 robot 仅有一个 next 请求也直接排除并存。这样，同一 source cell 最多有一个当前可见进入请求；一个候选最多有一条当前 blocked-head claim。

上述论证依赖：联合计划的初始占居唯一、每轮唯一终点且无 edge swap、路径是顺序单位移动、`last_depart` 是对同一计划前沿连续更新的、`launched` 只在实际 RUN 后增加、robot 在 END 前不能产生下一请求、cell 的 owner 排他且 endpoint 保留。当前源码明确维持这些条件。它不是对任意未来改造的形式化定理，也不是一般图调度、长 primitive、多资源 footprint 或同时暴露多个未来请求时的不可达性结论。

## 对研究判断的影响

两个不同候选同时可见仍然可能：它们可以分别阻塞两个不同 source cell；候选数量 2 不能据此叫 coupled。当前 `condition` 中每候选的多 claim 求和和 `owners` 分母在有 claim 时分别退化为一项与 1。相应的多 owner/多 head 特征不能在这套接口上提供学习信号。提高同一规则下的 agent 密度本身也不会打破上述不变量。

R11 的双干预和公开 successor trigger 仍可研究跨时刻预算与 occurrence 选择；它们与瞬时 coupled 结构是不同问题。若下一阶段确实以多责任耦合为研究对象，需要先依据外部任务合同选择能实际产生该结构的合法接口，例如真实多 cell primitive/较大 footprint，或者具有明确 admission 语义的多个当前需求。不能为出现正标签而私自移除当前安全依赖或扩大候选到未合法公开的未来请求。是否采用任何这样的接口尚需另行资格判断与登记，本补充不授权新实验。
