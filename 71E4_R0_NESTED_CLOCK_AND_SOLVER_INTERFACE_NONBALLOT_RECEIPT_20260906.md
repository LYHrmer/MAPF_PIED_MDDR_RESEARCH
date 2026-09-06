# 71E4：R0 嵌套时钟与单代理入口有界来源回执

2026-09-06；NONBALLOT，不替代原 69E1 或授予 G3 通过。真实 /root/r0_clock_input_evidence followup 已完整实际返回，root 完整读完六对象身份、直接读钟/停止、预算传递、亲见窗口和未核部分。固定官方仓库 YueZhang-studyuse/LMAPF-delay，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。代理不用 skill，不读本地研究文件、不写文件，不运行源码。

## 1. 身份与真实阅读范围

表内路径相对固定仓库；六文件一次完整获取/散列、Git blob 复算一致，但实际语义阅读只在所列范围。元数据全文件身份不冒充全文件语义审阅。

| 路径 | Git blob | SHA256 | bytes / 总行数 | 代理实际阅读 |
|---|---|---|---|---|
| src/MAPF-LNS2/src/lacam2/lacam2.cpp | 75ee58f4e1adb46ad3b26991cc212929bbff5f60 | 107bdd83cef76baf86831c0a0f3c421d64e65c36381494d7438dfb1f6b1f2f05 | 464 / 10 | 全文 |
| src/MAPF-LNS2/src/InitLNS.cpp | 6af45595834e2afd82dba985ce5c8d2a6cab0225 | 798003fc1ce279392e2a847ef40411adc9fc12faa32604f9005f8da3cd3d9033 | 31656 / 889 | L1–365；额外检索命中 L719/728/743/745/747/765/767/771/775/779/846/863/866 |
| src/MAPF-LNS2/src/SIPP.cpp | 7f8db084c2d03929f51c28a76a29895fbaaa1a64 | 3cb627fcd4a0ebe2646be9985e58bd16ef5f01ff3fce357ab4584b0045d2e2b7 | 30068 / 680 | L1–105、160–242、305–345 |
| src/MAPF-LNS2/src/SpaceTimeAStar.cpp | 1712e6d081337461437e3458c40fdcb8ef3de8ef | 4ccef3b2b34a964bd5377e6b742876f371b4fa553d3aa458926c56b2f6f485ac | 10923 / 300 | L1–140、170–258 |
| inc/MAPF-LNS2/inc/SingleAgentSolver.h | c22f59ac763c3bc272a82b5c8e9793a91f5da94a | daafdc674f90bbe4b34031b19f2564fb93189f07d7ad15e0927e1574cbb5611f | 7935 / 226 | L2–3、145–185 |
| inc/MAPF-LNS2/inc/SpaceTimeAStar.h | cdb96d96e01ae5efa43688019972efa37df01834 | ef1416a0098f08a17606d734b77f3722a61c3984f795d17d681cdef1dd937909 | 4052 / 112 | L1–9、77–90 |

root 在收到完整回执后，独立 GitHub API 获取 SpaceTimeAStar.h 上述固定 blob 并完整显示读取 L1–112，包括空带超时入口及注释。API 解码显示加末尾换行不作为原对象字节散列计算；表内散列为代理对原解码字节的复算。root 没有将这一处亲见扩写为其余五文件本轮全文读完。

## 2. 承重事实与适配影响

[lacam2.cpp L3–9](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/lacam2.cpp#L3) 将传入 Deadline 指针原样交给 Planner，没有新建时钟或重设起点。接合 71E3 已核 steady_clock/毫秒/严格大于到期，关闭此前自由函数转发缺口。

[InitLNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/InitLNS.cpp#L37)：run 起点在初始规划前；主循环比较缓存 runtime，若干 continue 绕过末尾更新。源码另含增加 time_limit 的分支和超限后 MCP 后处理，故原 time_limit 不是自动的全流程硬上界。runPP 对剩余预算再设局部计时起点并递减传入单代理；初始规划却逐代理传完整预算，局部 timeout 调后未检查，超时 break 被注释。以上源码语义必须与“统一预算”主张分开；原常量只作来源事实，不转为本项目参数。

[SIPP.cpp L30–66](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp#L30) 带超时入口在准备搜索前取起点，循环开头检查经过秒数 >= timeout，超限置标志并退出；未直接重置传入标志。另有单参数入口，不能把前者计时保证直接覆盖后者。

[SpaceTimeAStar.h L83](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SpaceTimeAStar.h#L83) 的三参数 findPath 实际函数体为空，没有返回值、时钟、标志更新或转发。root 亲见确认。其单参数 cpp 的时间步/路径长度约束不属于计算时限；[SingleAgentSolver.h L176–177](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h#L176) 两签名均为纯虚，没有可见基类自动补计时。注释称未使用不证明所有配置避开该入口。

InitLNS/SIPP 的 Time/fsec 接合 71E3 为 high_resolution_clock 与浮点秒；实际标准库 alias/是否单调尚 UNKNOWN。LaCAM2 为 steady_clock 经过毫秒；所读路径没有 CPU clock 证据。服务暂停时若原经过钟继续推进，恢复读取会包含暂停，源中未见自动扣除；这属于由已读表达式得出的条件推论，不是已实现的适配。后继应固定时钟返回及工作暂停语义，并保留原预算分支或明确标注适配差异；不可偷偷修空入口后仍称原字节基线。

## 3. 尚缺与后续界限

未知：实际平台 alias、MCP 后处理内部、预约表/约束表/启发式与邻居生成内部耗时和可中断性，以及各条件在具体配置下的可达性。root 已发最后有界 followup，仅核 Agent 构造及至多一个直接 caller 如何选择 SIPP/SpaceTimeAStar，优先原缓存、最多 Agent.h/Agent.cpp 和直接 caller，不继续展开库或数据。当前未返前不假定空入口可达或不可达，不把源缺陷导致的失败记作我们方法收益。

本回执不产生运行证据、实现、测试或参数绑定，不改 71/71R4。六门、协议与原来源任务未闭，仍 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 4. 后续实际完整回执：明示构造路径选择 SIPP

上述最后有界 followup 已返回，root 完整读完。代理沿用 71E3 缓存 BasicLNS.h L1–19、LNS.h L33–40、MAPFPlanner.cpp L6–20；只新补 LNS.cpp 的直接构造窗口 L1–54。不是再次获取旧全文，不增加库扫描。

[MAPFPlanner.cpp L11–20](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp#L11) 的 L19 true 由 LNS.h L37–40/LNS.cpp L7–10 参数次序确认对应 use_sipp。[LNS.cpp L43–47](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L43) 原样传给 agents.emplace_back；[BasicLNS.h L12–17](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h#L12) 的 Agent 构造选择 new SIPP，反分支才为 new SpaceTimeAStar。故本明示构造所得且保持该对象的 path_planner，带超时虚分派到 SIPP，不进入空 A* 入口。没有 use_sipp 默认值豁免，是实际调用实参证据。

三份缓存对象身份沿用 71E3：BasicLNS.h blob c22e0b66cc58e9c9ce19d6b161e4f54dabfb4c15；LNS.h 5b9ce3ef4aeaf6fcfa88c211c0f536c66f8ae24e；MAPFPlanner.cpp 94afb42df1a70f5e312a382e61cf83576fd7360e。LNS.cpp 固定 blob 1fb0e54f8f2bb00af05de53233ae600774e36f2a、总 bytes 53100，本次 1856 bytes/54 实际文本行的窗口 SHA256 b7d11bddd503ec5a218e62c71cf0d08321a778f5440042267b52c378959f6636；显示 L55 是末尾换行空项。该 hash 仅窗口，不冒充全文件散列；全对象既有根核见 71E3。

其他调用端、后续指针替换和实际配置运行覆盖未核，不扩写为全仓不可达。原布尔值只作源选择事实，未赋项目保护参数。此补核关闭明示分派疑点，不关闭 T3 的完整适配时钟/预算语义。
