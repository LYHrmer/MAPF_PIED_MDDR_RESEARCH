# 作者 GSES：图接口、完整轨迹和独立重放已打通

R10 将 R9 的原作者程序可运行预检推进到图和轨迹接口验证。保持作者搜索、分组、图构造及模拟器源码不变，新增 API 包装器导出原始/采用的固定图与逐时刻状态。四个原登记实例 × GSES/Improved GSES 共八次实际运行完成，原/新图合计十六次 Python 独立重放全部通过；状态、轨迹和 cost 全部匹配原生执行，八次状态及 cost 也与 R9 作者 CLI 一致。

|作者实例|机器人|原 cost|GSES|Improved GSES|采用图的反转依赖数 GSES / Improved|
|---|---:|---:|---:|---:|---:|
|random-32-32-10|60|1375|1292|1292|12 / 14|
|warehouse-10-20-10-2-1|110|10816|10804|10804|4 / 41|
|Paris_1_256|120|29860|超时，29860|29786|0 / 218|
|lak303d|41|10496|超时，10496|10229|0 / 88|

这些沿用 R9 的输入用于验证接口一致性；不能当新留出泛化测试，也不是与本项目连续任务吞吐的排名。cost 是作者离散执行的剩余完工时间和。仓库地图中 cost 降低但 makespan 从200变201，两种指标不会互相替代。超时仍保留原图、完整轨迹和真实超时耗时。

## 可复核实现

- `export_author.cpp` 只调用原 `construct_graph`、`GroupManager`、`Astar` 和 `NewSimulator`；顺序与原单次 situation 入口相同。16秒、seed10、A*/focal权重1及两种作者配置均保留。
- 每次执行使用新 NewSimulator。原对象的 `reset()` 使用 `paths.resize()`，复用同样大小的对象会保留旧行；新对象保证导出的是本次轨迹。额外比较原 `simulate()` 与用原 `step()` 收集的逐时刻轨迹，搜索和运动实现没有重写。
- `verify_replay.py` 用独立 Python 同步更新计算每个下一状态，不读取原记录来选择动作；校验所有原始/采用图的状态、逐智能体路径、目标驻留、完工时间、总 cost、顶点/跟随冲突、type1与合法type2反转。篡改状态、cost、轨迹及未来非单位边权四项破坏控制全部被拒绝。
- `SOURCE_BINDINGS_01.json` 绑定43个实际编译所需作者文件及四个预先冻结的接口/验证文件；`build_attempt01`、`commands` 保存原命令及回执，八份压缩原始结果共约3.65MB，无执行失败。
- 直接从已公开的 MIT 作者源码归档离线重编，无须 SFML、Python 开发包或网络；结果与实际执行二进制逐字节相同，见 `ARCHIVE_REBUILD.json`。原作者源码没有修改。

## 已明确的下一适配边界

固定路径依赖图和完整轨迹已经可用于下一阶段共同执行接口。现在仍不能直接把连续 primitive 时长填入作者边权：原模拟器只在 reset 读取当前 type1 延迟，之后不逐边加载未来权重；TURN 留在原位置，简单插重复顶点也不能表示资源已释放。独立校验明确拒绝这种输入。

另登记并实际运行三例原作者 API 机械验证：单机器人两步路径的默认单位边、当前边加2、未来第二边加2，图权重和分别为2/4/4，原生实际cost为2/4/2。这直接确认未来加权边未被执行器加载，见 `mechanical/RESULTS.json`。这是接口边界验证，未来加权输入不在原论文离散接口内，不作为作者算法错误或性能反例。

下一步应把一个顶点访问映射为真实到达/离开资源事件，保留原已承诺前缀；在共同 primitive 执行器中重放 GSES 选出的依赖，使用相同扰动、服务和完工定义。先验证零误差映射，再比较原图/GSES/Improved GSES。只有这个共同接口实际成立后，才能评价预测时长或查询策略相对作者算法的收益。固定路径调度与 LMAPF 重路由仍分别报告。

## 复现

在本目录执行以下命令，`--dest` 指定新的空目录：

```sh
rtk proxy python3 verify_replay.py
rtk proxy python3 reproduce.py --dest /tmp/gses-r10-new-rebuild
```

若要重跑八配置，`run_pipeline.py run --vendor /tmp/gses-r10-new-rebuild/STPG --raw /tmp/gses-r10-new-rebuild --attempt reproduction` 会生成新的命令目录和结果，不覆盖登记的 attempt01。`verify_replay.py` 默认核对已公开的 attempt01。

来源：[AAAI 2025 论文](https://ojs.aaai.org/index.php/AAAI/article/view/34487)、[作者 STPG](https://github.com/DiligentPanda/STPG/tree/25fb931eff03f1cce23a22a68ab42b7533f85ab3)。R9 的作者源码归档、MIT许可证及八个输入位于相邻 `gses_author_preflight_20261003_r9/`。本目录的新包装与独立重放不冒充作者原版功能。
