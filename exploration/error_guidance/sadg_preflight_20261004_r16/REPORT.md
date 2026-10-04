# R16 SADG：作者核心已运行，连续响应成立，强公共历史下没有测量增益

日期：2026-10-04。本轮共 **12次唯一作者MILP调用、2条合成事件后缀**；未重跑R13/R14旧物理轨迹、未训练、未改变主线收费/ARRIVE接口、未commit或push。

## 已得到的结论

1. 固定作者源码的ECBS→Plan→compile_sadg→SADG.optimize实际链路已运行。官方test.yaml有4个agent，ECBS cost24；作者连续MILP最优目标30.4。全路径合法性、24动作/20 type1/7 type2、全部连续约束与DAG均通过。这是**无ROS作者核心R0**，不是完整ROS控制栈，也不是原论文表格数值复现。
2. 同一预登记两车交叉例中，公开名义elapsed进度与位置测量能使作者优化器采取不同合法顺序。两条统一真实状态的完整后缀ΣT为13.5和13.0、makespan为7.75和7.5。但**完整公共历史速率对照也选择测量方案的顺序；相同历史时长模型下，再加入POSITION的后果增益为0**。因此不能把0.5秒差值写成付费位置的独立优势。
3. 原预登记warehouse checkpoint成功映射到10743个作者动作、15789条关系、108个active承诺。原compiler存在起点负索引缺陷；隔离修补及保守承诺适配后，两份输入都通过原R13 guard。公共/测量连续目标分别10962.8与10962.883333，**采用图完全相同**，无需重新跑旧后缀。

结果索引：[SUMMARY.csv](SUMMARY.csv)、[全部12调用](ALL_RESULTS.json)、[自检](FINAL_AUDIT.json)、[两条后缀](SUFFIX_RESULTS.json)、[按实际执行内容复用](SUFFIX_REUSE.json)。根独立数学/轨迹审计在根的R16评审目录，不能将本文件的自检冒充独立审核。

## 作者身份、环境与边界

- 官方仓库 https://github.com/alexberndt/sadg-controller ，固定 `c2626d996121a9d6c128844a167b917db24418ac`，AGPL-3.0，原checkout `/home/lyh/.cache/mapf_research/sadg-controller-c2626d9` 完全干净。
- 作者子模块libMultiRobotPlanning固定 `4c75fa20c435c440d8b6bd6dc81668ddc7296ba0`，使用原ECBS C++入口，w=1.0，官方 `sadg_controller/data/ecbs/test.yaml` 和对应dimensions（2.5m resolution）。GCC11.4、Boost1.74、yaml-cpp0.7。
- 独立venv `/home/lyh/.cache/mapf_research/sadg-r16-venv`，Python3.10.12、Python-MIP2.0.0、CBC/cbcbox2.935。依赖满足作者requirements的下界，但作者未冻结历史依赖，不能声称软件环境与论文完全一致。
- 每次命令用Python `-I`隔离环境变量/PYTHONPATH；核心模块本身无需ROS，无fakeROS、无Node shim。原 `get_progress()=0.5` 与完整optimizer代码保留；命名adapter仅处理输入progress/时长与显式compiler修补。
- [SOURCE_ENVIRONMENT.json](SOURCE_ENVIRONMENT.json)包含原tracked文件hash、实际import与依赖；[requirements.lock](requirements.lock)冻结安装结果；[AUTHOR_LICENSE](AUTHOR_LICENSE)保留许可。[ECBS_RECEIPT.json](ECBS_RECEIPT.json)保存实际命令和退出输出。

作者论文已把当前执行进度放入优化边界，补TODO不是新贡献；方法与版本依据为[作者论文§V–VI](https://arxiv.org/html/2312.04190v1#S5)及[固定源码](https://github.com/alexberndt/sadg-controller/tree/c2626d996121a9d6c128844a167b917db24418ac)。此处只主张接口验证与缺陷定位。

## 预登记小例及强对照

所有mini共享14动作、12条type1、1组可切换type2、horizon5，当前动作已承诺，不允许撤销。路径固定、公开当前启动时刻固定；决策时刻0.75。A名义进度0.75，B0.5；A公开历史2米/1.25秒，B2米/1秒；模拟测量A0.25、B0.5。POSITION年龄0，无未来heap/profile，无生产收费。

|输入|A当前progress|A未完成动作时长|作者目标|合法顺序|同一真实后缀ΣT / makespan|
|---|---:|---:|---:|---|---|
|原stub身份对照|0.50|1.00|13.24|A先|非强基线，不用于宣称优势|
|公开elapsed|0.75|1.00|12.74|A先|13.50 / 7.75|
|公开history progress-only消融|0.60|1.00|13.04|A先|复用13.50 / 7.75|
|模拟POSITION，名义时长|0.25|1.00|13.24|B先|13.00 / 7.50|
|完整公开history-rate|0.60|1.25|14.24|B先|复用13.00 / 7.50|
|同history-rate＋POSITION|0.25|1.25|14.24|B先|复用13.00 / 7.50|

另两项事前残余边界：A progress0.05时B先、0.95时A先；未做事后扫参。八个mini、官方原版及patch回归各一个、warehouse配对两个，共12次。完整历史速率对照由独立导师交叉审提出，先登记[HISTORY_RATE_PROTOCOL](HISTORY_RATE_PROTOCOL.md)和输入hash再运行，旧7个结果不覆盖；这是本轮顺序性机制诊断，不能称一次冻结的盲测性能实验。

作者目标是在不同输入预测下的模型值，不能直接相减当真实收益。真实后缀固定A残余0.75、B0.50，未来每动作1秒；用作者 `can_execute()/set_status()/get_next()` 驱动事件adapter。全部动作开始/完成、WAIT及完成后GOAL_HOLD均归档；全部重叠跨agent线段对16项，最小点距2m、无点碰撞。这里的点轨迹检查不替代机器人足迹、加速度、ROS2秒调度周期与控制器认证。

## 原版缺陷、隔离版本和旧域映射

`compiler.py`取 `vertices_i[k-1]`时，k=0对应Python[-1]，不会触发已有IndexError回退。它会把本应不存在的前驱替换为末动作。最小可执行反例见[COMPILER_COUNTEREXAMPLE.json](COMPILER_COUNTEREXAMPLE.json)：A从共享起点离开，原版反向边错误指向A末动作；显式k=0检查进入原作者rev=None分支后，错误反向不可用。该反例只编译图，0求解。

先按公开规模从warehouse10853 visits缩为random1426 visits做额外映射审计，该调整在求解前登记[MAPPING_PROTOCOL](MAPPING_PROTOCOL.md)，不按结果选场景；经根要求，原warehouse预登记目标也完整执行。random原版有88个错误reverse；k0-only修补后仍有2组的缓存反向head未代表全部实际反向head。例：`dg_agent21_0`真实反向head含COMPLETED的`v_21_0`，缓存却是STAGED的`v_5_5`。因此隔离版本逐项要求所有active/inactive head为STAGED，作为本项目保守承诺adapter，不把它外推为论文理论反例。

原warehouse有189个k0错误reverse。隔离版本后反向索引、关系族、active入边全部通过；[原版映射](MAPPING_AUDIT_warehouse.json)与[修补版映射](MAPPING_AUDIT_warehouse_patched.json)分开。所有修改仅在[isolated_patch](isolated_patch)中，原optimizer、nominal speed、MILP目标/约束/60秒上限不变。官方patch回归仍为30.4且采用方向相同。

warehouse的目标agent2、from_state0→1、证据捕获/送达0.5、public0.25/position1/6均绑定同一原证据及public内容hash。坐标2m/格使作者名义MOVE时长1秒；此模型没有STATION/TURN，不等于R14完整时长预测。公共和测量结果都是OPTIMAL，37277行约束、21488变量（仅2个horizon内binary）全部核验，15789关系不变。原R13 `adoption_guard`对两份候选实际执行并通过，108承诺保持；两份candidate hash同为 `a4e75747162b5d73bd4aa99826b7c70bb37d745752b9333f24afd366b433987f`。只导出候选，没有伪称已运行完整旧域物理采用。

## 运行收据及失败保留

所有case保存 `graph_before.json/graph_after.json/models.json/author_model.lp/author_stdout.log/result.json`。模型文件包括所有变量上下界/值、目标系数、全部约束常数/系数/方向/数值残差、status/objective_bound/gap、max_seconds60。12次均OPTIMAL，全部约束与结构自检通过。`solver_seconds`是对原Model.optimize入口/返回的观测区间，包含同步LP导出；`author_wall_seconds`还含建模/打印/初始化，不是实时生产延迟。

初次观测代码把mip.Model换为工厂函数，与Python-MIP惰性导入中的继承冲突，导致7次入口失败、**0次真实optimize**。原结果和代码保留在 `cases_attempt01_instrumentation_failure`、`run_preflight_attempt01.py`；改成 `sys.setprofile`旁观原方法后才运行成功。该错误属于本轮观测adapter，不能归咎作者算法。另一次映射审计混用了raw-file SHA与canonical-content SHA，已按R14 digest规格修正；未修改原证据、未新增求解。首次全图与剩余图比较的原记录也保留，最终按已满足边规则正规化后再核完整关系族。

## 科研导师后判

资格仍为 **CONDITIONAL**。官方无ROS核心R0由UNKNOWN关闭为PASS；真实连续接口与原作者调用身份已有证据，旧域映射也有可审计实现。但完整ROS复现、共同执行域有费信息优势、独立场景泛化、实际收费因果增量均未通过。不能据此锁定最终投稿方法或宣称优于已发表方法。

应保留SADG为连续时间作者对照，保留原GSES资产；下一步先在新TRAIN/CAL登记有物理依据的不同速度/历史偏差及候选集合，检验POSITION是否在**同历史模型**上增加可采用决策价值。当前两个域都没有该增量，先扩大学术上合理的响应条件，暂不训练更大的网络。主线若要接入，必须提供同world/几何/occurrence的证据、合法时效传播和真实费用；这里的production_cost始终null。
