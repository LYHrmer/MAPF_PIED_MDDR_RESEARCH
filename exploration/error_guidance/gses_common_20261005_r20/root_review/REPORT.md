# R20 第三线独立交叉复核

评审者为主线实现者，独立读取第三线原输入/原输出/源pin与事件记录；并非盲评。只在root_review/新增脚本和报告，0新作者调用、0新物理执行，未导入第三线oracle、engine或guard实现来计算结果。

**结论：本次指定范围PASS。** 四个修正nominal schedule的作者搜索结果与两个positive_switch完整后缀可由原JSON独立复算。必须把作者整数arrival ordering surrogate、连续执行的完工时间和、以及新POSITION信息价值分别陈述。报告中的反例是扩展权重域的资格边界，不是对原单位时间论文方法的泛化否定。

## 输入、源与原作者结果

核43个原作者源文件SHA、原ELF SHA、旧R13 adapter源码SHA，以及本轮phase3登记source pins。ELF位于main旧R13，adapter源位于第三worktree旧R13，两个路径有意不同，均按实际登记核验。优化器原commit为25fb931eff03f1cce23a22a68ab42b7533f85ab3；episode另有SADG执行底座c2626d9…标识，不能把二者合称同一作者仓库。

顶层PHASE1_RESULTS保留原4次构造失败；valid_nominal_schedule/PHASE1_RESULTS才是4次实际作者搜索。独立检查修正仅为B路径nominal timestamps全部+4，坐标、current/offsets、显式type1/type2权重不变；没有删除原失败。所有修正输入hash、原receipt returncode0、reply.status=Succ、原输出图对paths/current/type1的保持均核验。

独立脚本使用Fraction和完整拓扑最长路径，对每个可翻转方向的全部2种选择枚举：

|图例|返回方向精确Σarrival|全部方向最优|判断|
|---|---:|---:|---|
|p01整数当前延迟、unit type2|17|17|该例最优|
|p02整数未来延迟、unit type2|16|16|该例最优|
|p03二进制精确分数type1|101/16|99/16|返回非最优|
|p04 type2权重8|31|28|返回非最优|

第三agent的固定下游release依赖明确出现在输入，不将它伪称真实几何冲突。p03分母为2的幂，给定权重在float中精确可表示，不能把该差异简单归因于十进制输入舍入。两个unit/integer成功小例也不足以证明任意整数实例最优。现有证据支持继续使用明确命名的ordering surrogate，不支持任意连续权重同目标适配。

## 实际切图和承诺guard

两臂在t4.75采用前具有完全相同的图状态、相同query及此前START/END事件。agent0的v_0_0已完成，v_0_1在执行；agent1的前两动作已完成，v_1_2尚未启动。原方向为v_0_3 END→v_1_2 START，对应arrival边[4,10,1]；作者选反向[11,3,1]，提升回原执行约束为v_1_3 END→v_0_2 START。

独立复核图族集合、每对forward/reverse、type1和全部vertex状态保持，旧/新依赖头均为STAGED，组switchable/within_horizon=true，全图无环；正在执行的v_0_1没有获得新的前置条件。真实after图只翻转dg_agent0_0，且与作者输出方向对应，没有只在报告写adopted而执行仍用旧图。

作者arrival模型两方向目标为36和24，返回24确为该整数模型的全枚举最优。它把活动动作剩余3.25取ceil为4，type2仍是unit arrival gap；原连续执行仍使用tail-END→head-START，不等同于把24作为连续完工目标值。

从两臂每臂12对原START/END独立重算：

|臂|agent0完成|agent1完成|ΣT|makespan|
|---|---:|---:|---:|---:|
|gses_surrogate|24|35/4=8.75|131/4=32.75|24|
|keep_parent_control|24|20|44|24|

被释放的agent1 v_1_2实际在4.75启动、5.75 END，反向依赖尾v_1_3在6.75 END；agent0新依赖头v_0_2直到8才START，满足原执行依赖。控制臂v_1_2直到agent0 v_0_3在16 END后才START，最后20完成。所有type1和当时有效type2都由原事件时间检查，没有重跑executor。

## 连续物理与信息因果范围

对原分段轨迹使用Fraction精确计算全部闭时间交集上相对位置二次函数的极小值，核每车从0到makespan24连续覆盖、WAIT、初始位置与完工驻留。切图臂全程最小距离平方为625/68，发生在104/17；对照为4，发生在12。均大于0。这仅支持当前仿射点轨迹无碰撞，不支持有限footprint、加速度跟踪误差或ROS。审计枚举闭端点组合，控制臂检查15个交集，原两指针审计记11个；差额来自重复端点计数，精确最小距离一致，不是额外物理样本。

**关键因果限制：本例不证明新增POSITION的信息价值。** t4公开END历史已经给出agent0耗时比4；t4.5历史预测progress=1/8，与新POSITION实际值完全相同。t4.75仅靠已公开的elapsed=.75和历史比4，剩余13/4、progress=3/16，与测量融合后的优化器输入相同。独立脚本从prediction_evidence和public snapshot直接核算这一等式。

两个实际臂都发同一查询、都等到4.75；唯一干预是采用新图或保留原图。因此32.75 vs44支持“原作者候选经合法guard实际切图产生完整后果”，不支持“必须付费测量才能得到收益”。未执行no-query新物理臂，也不把静态相同预测冒充那个反事实执行结果。production_cost=null、POSITION为模拟capture、不是生产AUTH；真实作者调用wall/solver时间不能冒充主线Query账。

完整机器结果见INDEPENDENT_REVIEW.json，复算脚本independent_main_crossreview.py。脚本首次误设adapter源与ELF同目录、其次将package-version元数据当文件路径；已按原登记修正，未改任何科学输入或重新求解，见DEVELOPMENT_NOTE.md。
