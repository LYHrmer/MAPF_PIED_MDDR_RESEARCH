# R16 SADG 交叉评审：机制通过，正式比较仍有条件

2026-10-04。评审身份：**主线 R16 evidence/geometry 接口实现者交叉评第三线，非盲评**。采用科研导师 skill 的真实性、对象/方法适配与结论边界。只读已生成源码、input、graph_after、suffix、mapping 和隔离补丁；未运行优化器、执行器或新实验，未修改第三线目录或主线冻结结果。

结论：作者原核心可运行、连续残余能改变一个合法方向、同一真实状态的两条事件后缀有可复核差异，这三项机制证据成立。正式“付费信息改善 MAPF 执行”仍为 CONDITIONAL。最需改正的口径是 **mini_public_history 是历史推位置、未来仍用标称速度；它还不是完整的一致历史速率残余基线**。

## 1. 信息公平性

`run_preflight.py:78–108` 固定同一路径、active index=1、horizon=5、名义速度2、当前段长度2。`solve():205–209` 只从各臂显式 `progress` 字段给当前 IN_PROGRESS vertex 绑定 `get_progress`，没有读取未来 heap/profile。虽各输入的 observation 元数据都带 measured_progress，当前代码只有 mini_measured 的 progress 值进入该臂求解；未发现公共臂偷读观测值。

elapsed 臂由公开开始时刻和名义速度得 A=.75、B=.5；history 臂登记了 A 历史时长1.25，得到 A=.75/1.25=.6；measured 臂得到 A=.25、B=.5。此处 measured 是预先声明的、零龄、无噪声合成位置，不是通过新传感器/证据渠道获取的付费 POSITION，也不是从一条完整随机历史重新采集的测量。`production_cost=null` 正确，不能复制主线真实费用。

**重要限制**：作者当前 nominal_duration=1 保持不变，故 history 臂送入 MILP 的残余是 `(1-.6)*1=.4`，而一致延续历史速率的剩余服务时间会是 `1.25-.75=.5`。前者是合法且已说明的“历史进度估计+未来标称模型”，不能称作已经覆盖历史速率残余基线。若正式比较残余预测，应另外定义同信息的持续历史速率/标称恢复假设，并共同冻结；本次评审不追加实验，也不猜测 .5 的求解结果。单个公开历史时长不是经过校准的强统计基线。

年龄方面，本例 measurement_age=0，尚未验证陈旧证据传播、延迟或不确定性；没有本轮主线完整 geometry/occurrence/age/protected-authority 接入。它验证信息接口的响应，不验证真实付费购买策略。

## 2. 收益不是仅由 stub 对照造成，但也不是学习收益

只读比较 `graph_after.json` 的执行投影（type1、active type2、顶点 status/path/nominal_duration），确认 **mini_stub、mini_public_elapsed、mini_public_history 完全相同**；mini_measured 的单个 `dg_agent0_0` 方向相反。三种非measured臂的差异不是只看解目标值作出的判断。

因此不能把本轮响应轻描淡写为“只赢固定0.5 stub”：两个明确登记的公开估计也得到 A先，而 measured 得到 B先；完整后缀确实比较了这两张图。不过这只胜过这两个具体解析适配，不覆盖上节未验证的一致历史残余模型，不证明预测网络必要，不证明平均性能或购买净收益。

不同估计的 MILP objective（例如 elapsed12.74、measured13.24）属于不同边界条件，**不能直接比较为真实完成时间改善**。本轮有统一真值后缀，所以结果应引用后缀ΣT/makespan。

## 3. 同一真实状态的完整后缀比较有效，范围需写清

`replay_suffix.py:25–35` 对两张图共用真实 A=.25、B=.5、相同初始位置 `[0,5.5]` 与 `[-5,0]`、相同当前残余 .75/.50 秒；未来每段真实时长1秒，路径不变。当前段保持 IN_PROGRESS，不能撤销；后续按同一作者 `Vertex.can_execute()`、next 和 COMPLETED 转移执行。同刻完成先全部处理，再派发新段。这里未发现“一臂用自身估计冒充真实状态”的混淆。

两条 suffix 各14个轨迹段、24个事件，均完成两 agent；elapsed/history 图完成时间5.75/7.75，ΣT=13.5，makespan=7.75；measured 图为7.5/5.5，ΣT=13.0，makespan=7.5。差异0.5/0.25成立，是从共同checkpoint起算的完成时间。history 和 elapsed 的可执行图相同，所以复用 suffix 合理，避免了重复跑图。

这条“完整”只指两 agent 从此checkpoint到既定终点的完整后缀，不是 lifelong 多任务吞吐或基准统计。它是作者图语义上的**新事件执行 adapter**，不是作者2秒ROS timer、原主线 ReferenceController、真实传感器闭环或原论文数值复现。碰撞检查对每对重叠 affine段解析求极小距离，包含 WAIT/GOAL_HOLD，给定小例 min_point_distance=2；支持本例点轨迹无相交，不支持足迹、加速度、延迟或通用系统安全认证。

后缀协议是在优化结果产生后、后缀执行前追加；可作为机制诊断的预登记后缀，不能包装成整个样例选择独立于已见结果的确认性实验。

## 4. 原作者和补丁版如何进入外部基线

建议坚持三种名称和不同证据作用：

|版本|可支持的身份|不可支持的说法|
|---|---|---|
|固定 c2626d9、原 compiler/optimizer、get_progress=0.5|原作者代码核心 R0；说明依赖/后端可运行、原输入能求解|不能仅凭其弱 stub 与适配版的差异宣称新方法胜过强外部执行基线；不是ROS全栈|
|原 compiler/optimizer + 显式 public/history/measured progress adapter|以原作者优化器为底座的同小例机制对照；本次 mini suffix 所属版本|不能叫“未改原作者基线”；不能把模拟 measured称真实付费测量|
|k0 compiler patch + all-head commitment guard + 原 optimizer +同域映射|补丁后的作者方法共同域适配版，若完整原guard及后果检查通过，可作为公平共同域外部算法比较底座|不能抹去原版失败、把补丁版称原版，或把修复量直接称论文算法创新|

公共/测量/未来学习臂必须使用**同一 compiler补丁和同一保守guard**。否则观测臂还得到更大/不同切换集合，算法和信息两个因素混杂。公共历史、预测器、查询策略的消融也应共享执行adapter、真实随机流和求解时限；原版无法安全映射时，应报告不兼容，不能强行解除guard以凑对照。

当前 `MAPPING_AUDIT_warehouse_patched.json` 是 110 agents/10743 actions/15789 remaining type2 的 **PASS_MAPPING_ONLY**，其自身 `actual_optimizer_calls=0,physical_suffix_runs=0`。映射通过不等于该旧checkpoint已获得性能收益。正式评价还需要同域完整续跑、失败回退、求解耗时计入和公平时序。

## 5. k=0 与 OPPOSITE 缓存问题及 all-head guard

**k=0：同意显式修补。** 原 compiler 在 `vertices_i[k-1]` 外只捕获 IndexError；Python `[-1]` 合法地取最后一项，因此能给首动作造出错误“前驱”，而不是进入作者已有 `rev=None,switchable=False` 分支。隔离补丁 `if k==0: raise IndexError(...)` 精确修复这个边界，保留原MILP/时长/目标。它是可定位的 Python 实现问题，不应扩写为 SADG 理论普遍不安全。

**OPPOSITE：同意当前保守适配，但不声称已修复全部缓存语义。** 作者 `append_switch` 用 `new_active_dependency.get_head()` 更新 `first_head_inactive`，这个缓存不一定代表反向头；归档random案例中因此出现已完成 reverse head，而缓存仍为 STAGED。隔离 `is_switchable()` 逐对要求 active/inactive head 全部 STAGED、reverse存在、dep.switchable，直接保护已完成/进行中的动作，不依赖错误缓存。它还覆盖附加的不可反转pair未正确汇入组标志的可能性。

这会缩小允许切换集合，是合适的保守承诺合同。它不是最小性能等价修复，可能拒绝某些本可安全重排的组；因此须跨全部比较臂共享，后续才能分辨保守度的影响。它只解决切换资格，不能取代原guard、DAG、全部active边/共享资源及物理碰撞检查。原缓存仍用于 within_horizon 等逻辑，不能写“所有缓存/时域问题已彻底解决”。

本次读取的隔离 compiler SHA-256：`1bebcd960fdc51678ba404da5136192b4407164fbeecb302e45dd38a6cb0c43a`；guard SHA-256：`3f6cb328c32ff947f04e3aab304cb1996881652cd4c7b1733248ed5fb6d234f1`。所有判断仅覆盖这些源码和本次已见结果；后续若新增求解/补丁应另核对。

## 导师判断与允许写入的结果句

资格维持 **CONDITIONAL**：机制预检已从静态接口推进到作者优化器的图响应，再推进到共同真值后缀；这是有效增量。现在不需要扩大模型，下一步要补强同信息残余定义、在共同旧域通过完整guard后记录非选择性后果，并保持费用和安全口径。

可写：“在一个预先声明的合成两智能体机制例中，零龄位置输入使作者 SADG 优化器选择不同的未承诺依赖方向；在相同真实checkpoint和未来名义执行条件下，该方向相对所登记的公开进度适配图将后缀ΣT减少0.5秒、makespan减少0.25秒。”

必须随句保留：此为选定机制例、模拟零费用观测和事件adapter结果，不是总体统计、学习优势、真实付费查询收益、ROS全栈复现或主线证据跨域合法性证明。历史适配目前仅校正进度，持续历史速率残余对照尚未覆盖。
