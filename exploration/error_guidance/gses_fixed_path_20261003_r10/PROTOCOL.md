# R10 作者 GSES 固定路径接口与独立重放

登记于新接口结果产生之前。此轮沿用 R9 已登记的四个作者实例及两种配置，明确是接口一致性验证，不是新留出性能测试。作者 STPG 提交 `25fb931eff03f1cce23a22a68ab42b7533f85ab3`，不修改作者搜索、图构造、分组或模拟器源文件。

实现一个 C++ API 包装器：照作者 `simulate.cpp` 的顺序建图、分组、裁剪当前状态、加入当前延迟、调用 Astar；保持 16 秒、seed=10、权重=1、相同 GSES/Improved GSES 设置。超时按作者规则执行原图。导出原图、实际采用的图、完整状态时间序列、原生轨迹和 cost。每个模拟使用新 NewSimulator，避免其 `paths.resize` 在复用对象时保留旧行。额外以原 `simulate()` 的结果校验逐步记录。

Python 独立实现同步时间步重放，从图和当前延迟计算每一步，不从被校验轨迹推导动作。检查全部状态、每个智能体轨迹、完工时间、总 cost、固定路径、节点/跟随冲突、原/新 type2 合法反转和 R9 作者 CLI 结果。设置四项破坏控制：篡改状态、cost、轨迹及无效未来边权应被拒绝。

资源：顺序运行，编译 1，地址空间 4 GiB，CPU 90 秒，外部超时 120 秒；完整保留编译及执行失败。输出压缩原始 JSON，公开代码、命令、输入及源文件哈希、检查结果。

接口边界：作者模型是离散顶点访问与不允许跟随冲突的固定路径重排。原 NewSimulator 仅在 reset 读取当前 type1 延迟，不在每次移动后读取未来边权；不能直接把所有未来 TURN/MOVE/STATION 时长塞入权重并宣称原生执行。TURN 保持原位置，直接插入重复顶点也破坏 type2 的“下一顶点即离开资源”语义。此轮明确检测并拒绝此类适配，下一阶段须实现独立 primitive 执行映射并验证。R10 的 R1 图与轨迹一致性不能冒充 LMAPF 端到端排名。

来源：AAAI 2025 *Speedup Techniques for Switchable Temporal Plan Graph Optimization*，https://ojs.aaai.org/index.php/AAAI/article/view/34487 ，作者 https://github.com/DiligentPanda/STPG 。具体源文件按 SOURCE_BINDINGS.json 锁定。
