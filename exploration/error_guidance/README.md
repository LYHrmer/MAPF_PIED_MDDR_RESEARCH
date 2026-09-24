# 空间误差约束下的路径引导探索

分支 `explore/error-aware-guidance`，起点 `main@af17410`。本目录研究：在固定足迹和空间误差安全层不变时，学习预测占用或等待代价能否帮助 lifelong MAPF 选择路径。首先验证路径选择确有可利用的误差相关差异，再决定是否训练模型。

最新[历史校准闭环](HISTORY_CALIBRATION_PRECHECK.md)通过3722检查：真实历史MOVE的已交付END拟合运动时长，再用于事前择路。在合法较快运动条件下，旧模型错误选择上绕，历史校准改选下绕，实际到达从5.750325提前至5.231320，消除约0.519005的两候选选择损失；其余三组选择不变。拟合与单END解析校准相同，尚未证明复杂学习的独立价值。此前[冻结先验失配检查](MISMATCH_PRECHECK.md)通过2962检查，明确了没有历史时两种私有条件对选择器不可区分。

最新[原prefix普通分支与解析等待对照](PREFIX_PRECHECK.md)通过2998项检查、完成8格实际执行：t=4时解析等待事前选择下绕，约8.363081到达，比基础代价上绕约9.196152提前0.833071；t=2.5两者均选上绕。当前只有一个未授请求，不满足GROUP_ADMIT循环条件，原prefix普通初授和full-MOVE同轨，因此该2×2的授权因子退化。收益来自匹配先验的解析等待，未运行学习器，也不构成一般部分cap授权消融。

此前共同观察时机预检：**3042 项断言，严格编译和运行均退出 0**。四个具名机会各检查“零/非零误差 × 上/下绕路径”四个组合，实际结果如下。

| 唯一共同观察时刻 | 证书下界 | 非零误差上绕结果 | 已完成路径比较 |
| --- | --- | --- | --- |
| `2` | `2 < 61/20` | 仍等待，`arrival=null` | 不作完工时间排序 |
| `√(61/10)` | `61/20`，精确等号 | 仍等待，`arrival=null` | 不作完工时间排序 |
| `5/2` | `25/8 > 61/20` | 到达 `≈7.696152` | 上绕更快 |
| `4` | `24√2−28 > 61/20` | 到达 `≈9.196152` | 下绕更快 |

所有机会下，下绕均到达于 `2(√3+√6)≈8.363081`；零误差上绕均为 `4√3≈6.928204`。决策与断言使用精确实代数数，小数仅供阅读。不足释放时保留合法驻留和待处理需求，没有追加第二次观察。

上绕路径经 y=1，下绕经 y=−2，均从 `(0,0)` 到 `(4,0)`；阻塞机器人固定沿 `(2,3/2) → (8,3/2)` 运动。每组双方使用相同误差盒 Z、共同控制参数及同一次观察，包括不等待的路线。真实 Geometry/Index 给出责任和阈值，PositionCommit 实际提交证书后才释放。

这些是有限人工路线的机制结果，已验证历史尺度拟合修复一次选路失误，尚未证明学习优于解析或LMAPF净吞吐。下一项将稳定历史改成合法变化条件并接后续任务，检验校准是否仍有预测价值；若专门研究部分初授，须构造确实满足GROUP_ADMIT条件的循环请求。此前精确结果及边界见 [TIMING_PRECHECK.md](TIMING_PRECHECK.md)，方向与已有工作的区别见 [研究合同](RESEARCH_CONTRACT.md)。

复现命令从本分支根目录执行；输出文件须使用新名字，旧记录不会被覆盖：

```sh
rtk proxy python3 -B exploration/error_guidance/run_timing_precheck.py --source-root /home/lyh/MAPF_PIED_MDDR_RESEARCH --output exploration/error_guidance/timing_run_20260924_02.json
```

新源码为 [timing_precheck.cpp](timing_precheck.cpp)，运行器为 [run_timing_precheck.py](run_timing_precheck.py)，完整命令、退出码、stdout/stderr 和 SHA 见 [timing_run_20260924_01.json](timing_run_20260924_01.json)。运行依赖 [source_pins.json](source_pins.json) 指定的本地主线头与既有 FLINT SDK；这些源码仅在临时目录使用，不随分支上传。

原 t=4 预检的 [源码](precheck.cpp)、[运行器](run_precheck.py)及 [790 项断言证据](precheck_run_20260924_01.json)保持不变。
