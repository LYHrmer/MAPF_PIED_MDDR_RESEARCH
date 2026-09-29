# 空间误差约束下的路径引导探索

2026-09-29 设计收敛：见[三线设计与外部基线合同](RESEARCH_DESIGN_AND_BASELINES_20260929.md)。第三线优先评估作者 GPIBT／OnlineGGO 引导接口与 LSMART 执行环境；原作者复现和共同误差执行器上的适配比较分表。本文已有 motion-only、解析与历史校准均为内部机制对照，不冒充已发表外部基线。论文主比较须有作者源码、固定版本、可复核运行和公平预算。

本轮新增[作者基线实际构建/运行记录](BASELINE_PREFLIGHT_20260929.md)和[官方GPIBT固定2×2先导](external_baseline_pilot_20260929/REPORT.md)：两个作者工作负载×seed42/43均完成450步，独立重放189,000动作通过，全部原始数据、补丁、脚本及[共同误差执行接口合同](external_baseline_pilot_20260929/COMMON_EXECUTION_ERROR_CONTRACT.md)已归档。这里只验证外部方法实验入口，尚未接连续误差或学习臂；OnlineGGO的学习策略仍未完成R0。下一项实现共同接口并验零误差/反馈因果性，再从真实执行日志检验可学习残差。

分支 `explore/error-aware-guidance`，起点 `main@af17410`。本目录研究：在固定足迹和空间误差安全层不变时，学习预测占用或等待代价能否帮助 lifelong MAPF 选择路径。现定位为替代学习/模型 LMAPF 底座评估，不预设必须在PIE-D内追加路径模块；已有native机制可用于迁移接口判别，不代表已切换或复现OnlineGGO等外部方法。

最新[两任务连续执行实验](CONTINUATION_RESULTS_20260929.md)已完成预声明16实例×4路线组合，包含零/非零二维误差、同一合法历史校准、两次择一的共同观察时刻，以及正常真实END/无后续END两个制度。正常END下，非零误差的4组中3组解析等待选路提前0.519005、0.833071或2.019005，1组无收益；零误差8组均无收益。缺END早观察的完成数优势在正常END后消失，失败范围已保留。全部64组合的完成数和60个可完成组合的到达均被同信息强解析解释，当前不支持为增加工作量而另加复杂学习。详见[冻结协议](CONTINUATION_PROTOCOL_20260929.md)、[64行原始结果表](continuation_summary_20260929.csv)和[最终完整回执](continuation_run_20260929_03.json)。尚未计全费用或接正式标准benchmark。

此前[历史校准闭环](HISTORY_CALIBRATION_PRECHECK.md)通过3722检查：真实历史MOVE的已交付END拟合运动时长，再用于事前择路。在合法较快运动条件下，旧模型错误选择上绕，历史校准改选下绕，实际到达从5.750325提前至5.231320，消除约0.519005的两候选选择损失；其余三组选择不变。拟合与单END解析校准相同，尚未证明复杂学习的独立价值。此前[冻结先验失配检查](MISMATCH_PRECHECK.md)通过2962检查，明确了没有历史时两种私有条件对选择器不可区分。

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
