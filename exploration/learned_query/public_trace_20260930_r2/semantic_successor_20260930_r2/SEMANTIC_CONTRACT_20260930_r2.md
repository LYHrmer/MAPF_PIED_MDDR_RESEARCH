# 认证下界语义后继：运行前登记

本合同继承 [父合同](../CONTRACT_20260930_r2.md) 的全部源数据、地图单位、355crop、任务、扰动seed、完整run split、机会3/4、证书epsilon1/10、容量1、预测器及WAIT/QUERY真实执行。父首次alpha序列化失败及02严格标签断言失败连同当时源码冻结，均不覆盖。本后继属于真实接口纠错，未按结果改物理条件、任务目标、预算或奖励。

唯一关系修正：`certificate.lower` 已经是认证的保守进度下界；PositionCommit 的退休几何直接使用它，不再减epsilon。原 `s−epsilon>r_exit` 断言误把证书宽度上限又当成一次下界误差。源码证据：`pie_position_commit.hpp:165–195` 经 `Retirement::prepare` 取下界，`pie_progress_retirement.hpp:74–79` 经 Geometry `g_advance(lower,cap)`；Index 所有权条件比较 `q≤entered_exit`。因此实际接纳严格条件是 lower>Geometry阈值13/20；相等仍保留。epsilon仍是证书精度承诺，固定不改。

全部predictive标签、native执行验收与offline分析改为同一个实际资源语义，但不以同一公式互相认证。native增加source资源在旧/新所有权和真实G残余mask中的状态；证书字段打印实际已提交lower。native直接调用G在等阈及严格超过阈值两种状态，分别核对保留/删除资源；同时记录错误重复减epsilon公式的结果。离线独立从原地图square、足迹、误差盒、方向和认证lower区间重建残余sweep与source-cell的闭矩形相交，重算所有权/准入，不仅复算native条件。错误公式与真实资源不同的快速案例必须显式保留作为负控。

当前工作继续按六个完整生成run×20phase网格全部运行；训练/校准/测试及当前truth遮蔽保持。当前数据只有8个各相位唯一terminal，所以预言监督categorical与方向bin任务选择相同，未建立独立学习收益；这项支持域限制不会通过修改奖励隐藏。

如再出现可修的接口错误，保留失败并注册有科学依据的修正；不因自定修复次数留下已明确可修阻点，也不调整因素来找正结果。严格编译120s、native phase60s仍保持。
