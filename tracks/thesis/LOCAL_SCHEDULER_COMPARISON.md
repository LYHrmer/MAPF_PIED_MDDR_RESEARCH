# 固定路径的全局同步—局部依赖对照：三轮实现与待运行提案

2026-10-22。完成了局部日程构造、独立进度连续检查、既有比较入口接入三轮工作，验证材料全部是明确手写的人工软件夹具。**尚未对六项旧任务、两项R16或其他真实完整输入构造或运行新日程比较。** 新清单状态为 `PENDING_USER`，没有科学收据、性能结果或可复用的旧运行授权。

## 第一轮：固定访问次序的完整动作块

[local_scheduler.py](local_scheduler.py)沿用[名义运动模块](nominal_motion.py)的显式参数类、世界坐标、转向规则、车身圆、障碍候选及精确几何函数，使用同一固定SCI `GridProblem`完整校验器。每个离散格步对应一个完整TURN+MOVE块，原离散等待保留一个完整直行槽。记录块起止时刻、所有边以及TURN、MOVE、WAIT和无限GOAL_HOLD；等待细分为全局转向等待、局部依赖等待、原离散等待。

局部图首先保留每车动作顺序，再检查不同车整块圆扫掠：两轴向中心线的盒距离正好是其空间距离，只有严格分离时才省去依赖。潜在重叠时，按原离散路径在共享顶点的访问时刻固定方向；没有唯一原次序的几何交叠返回 `DEPENDENCY_ORDER_NOT_ESTABLISHED`。不搜索换序、不复制优化器，不用实测运动结果反选路径。DAG最长路给出精确名义完成时钟下的最早开始；成环返回 `DEPENDENCY_CYCLE`，仅表示本保守构造失败。

图中的一次块完成不等于所有可重入空间被永久释放。后续动作仍各有独立依赖；每车等待、后续运动和最终驻留还必须经过第二轮的全时间几何检查。这个局部基线可能比全局barrier更慢，也可能成环而全局可行。

与作者实现的关系：固定来源为SADG `c2626d996121a9d6c128844a167b917db24418ac`，本机已读 `sadg_controller/sadg_controller/sadg/vertex.py` 的 `can_execute()` 与 `compiler.py` 的编图代码。作者API要求全部active前驱状态为COMPLETED，编图还涉及start/goal位置、goal_time和可切换依赖。本实现是**借鉴ADG前驱完成语义的项目固定次序对照**；它用完整圆扫掠形成更保守的块依赖，离线时钟代替反馈状态，不执行作者编图/切换算法。旧 `author_events.py`只适配固定双车CLEAR逻辑；本工作不借其API把自写模块称为完整SADG性能复现，也不移植作者安全定理。

两个新调度器共同使用有理数起停原语。直行沿用原梯形/三角形方程；三角形峰速取平方根的向下有理界，增加非负匀速段补足**精确格边位移**，保持起终速度零、速度和加减速度上界。转向用π的明确有理上界生成时长，但实际角度是 `signed_quarters × π/2`，角进度按真实角度/上界角度缩放，因此不发生多转角，90°/180°终向精确且角速度/角加减速不超界。两调度器共享同一原语和参数；此共同实现与旧18臂的浮点计时版本不同，**不得将新旧秒数直接相减归因于局部依赖**。所有证明用exact时间字符串，浮点只用于输出和汇总，并经一致性核对。

## 第二轮：独立时钟下连续充分条件

每个MOVE按自身起始时刻计算精确有理位置，TURN/WAIT/GOAL_HOLD中心固定。对每对动作的闭时间交集，以单调位置端点构造覆盖整段轨迹的两个盒；盒间距离严格大于两车外接圆半径和时，整段获得充分分离条件，否则二分。该证书允许两车进度不同，没有调用旧共享q最小值证明。

认证依赖全部子区间的保守覆盖，不依赖采样。若某个精确时刻圆外包交叠，返回充分条件未建立；这不是矩形车身碰撞判定。每对动作最多深度16、2048个盒；未能完成覆盖即 `CIRCLE_INTERVAL_SEPARATION_NOT_ESTABLISHED`，不把精度预算耗尽记作安全。全程检查起点初始等待、块间等待、转向、移动、终点至其他车结束的驻留；所有车结束后，以固定终点圆分离覆盖无限尾部。障碍和地图边界用完整轴向线段的精确空间检查。

认证前逐项核对完整原路径及WAIT的位置/顺序、时段连续性、同轴格边、profile身份、动作端点、初末朝向、永久终点、块时间记录、重新生成的固定依赖及前驱完成约束。显示时刻和完成指标必须从同一exact时间一致导出。输入/记录错误为硬失败；依赖环、保守几何未建立和区间证书预算耗尽是保留的构造负结果，不意味着所有日程无解。

## 手写软件机制验收

[局部夹具](test_local_scheduler.py)10项、[既有比较入口夹具](test_compare_nominal_motion.py)10项通过，后者包含原有接口回归。它们没有载入六任务的路径来构造日程。关键完整例使用5×5空格图、0.5m格边、0.22×0.16m车身、速度/加减速度0.5以及角速度/角加减速度1；令共同90°转向时长为τ，直行槽精确2秒。

| 人工例 | 固定路径/动作与依赖 | 可手算机制结果 |
|---|---|---|
| 空间独立转向 | A:6→11，B:16→17，初向均东；局部无跨车边 | A均为τ+2秒；B全局τ+2秒，局部2秒；只减少B的barrier等待 |
| 同向跟随 | A:6→7，B:7→8；边(B,0)→(A,0) | A局部先WAIT[0,2]，再MOVE[2,4]；B完成2秒；全局两车均2秒，展示局部整块序列化更保守 |
| 四车一格环 | 6→7→12→11→6，各车一条边；四条前驱边成环 | 原离散计划合法；局部报告本构造成环；全局可建立连续圆分离，完成时间由初向决定 |
| 早到永久目标 | A:6→6→7，B:8→7→12；删除A依赖等待 | 正式校验因块/前驱时间不符拒绝；单独几何层同时确认早到位置与B的TURN及后续MOVE圆外包交叠 |

另有不同起始时钟的交叉运动：动作时间交集两端圆分离，中段仍捕获重叠；以及缺初始等待、MOVE冒用TURN profile、篡改依赖、篡改显示完成时间、深度/盒预算耗尽的反例。正例的连续证明、负例保留与软件输入检查分别报告，不把测试项数当作科研样本量。

## 第三轮：复用既有整方案比较与有限运行提案

[compare_nominal_motion.py](compare_nominal_motion.py)新增schema，仍从既有固定SCI Git对象读取完整初解和优化后整方案。原方案、冻结SOC方案、转向感知整方案各只选择一次，再分别交给全局/局部调度；每对保存同一完整路径SHA和同一原语参数。整方案选择开销只记一次，两调度器构造/验证/序列化费用分别保留。依赖拒绝和几何拒绝的时间指标为null，不计作成功、不换案例；无优化器搜索、学习、world、误差模型或反馈END。

新清单 [scheduler_motion_v1_manifest.json](config/scheduler_motion_v1_manifest.json) 固定顺序：

1. `maze-32-32-2__s01__n16`，三种路径×两种调度，共6臂；
2. `random-32-32-10__s01__n16`，同样6臂。

第一项是旧DEV的运动时间排序反转例；第二项是原/SOC/转向三方案路径不变的零差异对照。选择在任何新调度运行前固定，不根据新结果挑例。这里的零差异指三种路径方案，不能预先断言两种调度器也没有差异；二者仍是诊断任务，不是独立、无偏性能样本。来源仍为SCI `535ee1adf3135ab79565e0b3aa5d189348fe7ab2` 的旧 `repair_residual_v1 / REMAINING_BOUND`，不混称完整ADDRESS结果。原完整输入SHA `be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b`，清单SHA `6c23695d30d661e823ea6731cb65f1b674d43a5b636f6b7283691031ee628630`；九个运行代码/锁文件SHA及固定supervisor在清单内。输入文件只读其冻结Git对象，无截段、缩放、重新规划或错误集合扩域。

每任务总准入60秒、worker CPU45秒、地址空间512MiB、单文件16MiB，预留2秒收尾；外层62秒TERM+2秒KILL，两项硬保护总计≤128秒。零重试，前项硬失败/缺产物/版本漂移/超限则禁止后项启动。几何充分条件未建立、局部成环及内部证明预算耗尽是完整保留的负结果；过程异常或无效日程是硬失败。费用包括Git读取、导入、选择、依赖与几何、构造、指标、序列化、fsync、哈希和监督等待；最终管理收据/进程退出另列，嵌套时钟不可相加。原优化器费用只作来源元数据。

已执行的静态核验及人工软件夹具命令：

```bash
rtk proxy python3 -B tracks/thesis/test_local_scheduler.py
rtk proxy python3 -B tracks/thesis/test_compare_nominal_motion.py
rtk proxy python3 -B tracks/thesis/compare_nominal_motion.py inspect --manifest tracks/thesis/config/scheduler_motion_v1_manifest.json --sha256 6c23695d30d661e823ea6731cb65f1b674d43a5b636f6b7283691031ee628630
```

inspect仅读取和校验冻结字节，返回 `FROZEN_BYTES_VALIDATED_NO_MOTION_COMPARISON`。**下列命令尚未执行，必须获得这两项的新明确授权后才可执行**；先maze16完整收据通过，再random16，不复用旧许可：

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 62s python3 -B tracks/thesis/compare_nominal_motion.py run --manifest tracks/thesis/config/scheduler_motion_v1_manifest.json --sha256 6c23695d30d661e823ea6731cb65f1b674d43a5b636f6b7283691031ee628630 --case maze-32-32-2__s01__n16 --authorization-reference '<本批真实用户指示引用>'
rtk proxy timeout --signal=TERM --kill-after=2s 62s python3 -B tracks/thesis/compare_nominal_motion.py run --manifest tracks/thesis/config/scheduler_motion_v1_manifest.json --sha256 6c23695d30d661e823ea6731cb65f1b674d43a5b636f6b7283691031ee628630 --case random-32-32-10__s01__n16 --authorization-reference '<同一批真实用户指示引用>'
```

输出独占 `tracks/thesis/results/scheduler_motion_v1/<case>/`，存在则拒绝覆盖。本轮未创建这些目录。

## 旧R16误差提案的冻结版本

两项R16同参数名义/误差清单仍待授权，其文件、输入和SHA未改。新增schema改变了当前 `compare_nominal_motion.py` 字节，因此当前工作树故意不能通过旧R16清单的运行SHA校验；不得为通过检查静默更新旧清单。旧提案绑定的可用代码版本是硕士 `5d85f6214ac7ec0fb8a49eb89b91467e56f1c0ba`。若之后授权旧R16，应使用该完整冻结代码树及原清单，再执行原报告命令；例如先建立该版本的独立detached worktree，`inspect`原清单SHA `1868bd5da40032128adc2f3f54ee2c6686408711b617f372a52f147f9131f4a3`，随后按新授权运行。此处没有创建该工作树，也没有运行R16。旧18臂结果及旧六任务的v2超域判定保持原证据口径。
