# 固定 R0：规划时钟输入的有界来源回执

2026-09-06。NONBALLOT；这是一手来源核验记录，不是新候选、时钟适配实现、已通过协议或运行结果。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT；保护参数保留原义未赋值。源代码原字面量仅作为原法证据，不转成实验配置。

root 先通过官方 GitHub blob API 取得固定 R0 的 LNS.cpp，随后实际派发 /root/r0_clock_input_evidence，只追 Time/fsec、LaCAM2 Deadline 与 MAPFPlanner 入口的直接依赖。该代理不用任何 skill、不读本地研究工件、不写文件；现已完整实际返回，root 已完整阅读。此文件是回执整理，非原文转录；不冒充原 69E1 全源码任务返回，不投送第三路独立审稿输入。

## 固定对象与亲见强度

仓库 https://github.com/YueZhang-studyuse/LMAPF-delay ，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。

| 精确文件 | Git blob | SHA256 | bytes / lines | 实际阅读 |
|---|---|---|---|---|
| src/MAPF-LNS2/src/LNS.cpp | 1fb0e54f8f2bb00af05de53233ae600774e36f2a | 0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2 | 53100 / 1486 | root 本次取得完整 API 解码文本，选择 clock/runtime/time_limit/deadline 等匹配附近窗口实际阅读；非本次全文，SHA256/原始 bytes 沿用前次固定源身份，不从 gh 添加的输出换行重算。代理未重读该文件 |
| src/MAPFPlanner.cpp | 94afb42df1a70f5e312a382e61cf83576fd7360e | c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1 | 6125 / 208 | 代理全文 L1–208；root 此前已全文阅读，本次仅完整读代理回执 |
| inc/MAPF-LNS2/inc/LNS.h | 5b9ce3ef4aeaf6fcfa88c211c0f536c66f8ae24e | c9751aca5f3c305d5da49c3445ec29cb19819655b496de12c522d83d7af7ad91 | 4201 / 119 | 代理全文；root 本次仅完整读回执 |
| inc/MAPF-LNS2/inc/lns_common.h | 3bddf54ab74388904064a60a92346883a52c10cb | 8994fbaf6e022f7b233b7015741ae277d5773f3c84665845ecc654b44a51ccf6 | 2890 / 102 | 同上 |
| inc/MAPF-LNS2/inc/BasicLNS.h | c22e0b66cc58e9c9ce19d6b161e4f54dabfb4c15 | 9927e17d5c6dd3624ed4e5dc3cc81c20eec854b340ddf4723f93d873a6b526ff | 2042 / 77 | 同上 |
| inc/MAPF-LNS2/inc/lacam2/utils.hpp | 49965f9dc210d3691f35692769f541dada74ea13 | 8c647381901498a3c8033db7117a8696ab38df0858cb9b9520d05edcaee87442 | 1131 / 50 | 同上 |
| src/MAPF-LNS2/src/lacam2/utils.cpp | b10bf551c920677418610622d3ef7095e0e54656 | 7fc143b6073a7aa5673087ba878e88380020620c80e89f1f5094545fa67d1244 | 1222 / 51 | 同上 |
| src/MAPF-LNS2/src/lacam2/planner.cpp | 4f46f988d2c16f09c5a6f65bb9cd70e8e01aa483 | 8d2fa9131f0691b109a00dd6267b3b48f80df7778643daeb806ff82e20fe2789 | 19115 / 616 | 代理完整取得并计算身份，实际只读 L97–114、122–133、143–154、182–199、376–387；root 仅完整读回执 |

代理七份实际源码均一次完整进入缓存，其 UTF-8 字节的 Git blob SHA1 与目录元数据一致；整文件散列不等于每一文件均已阅读全文。代理报告最初 shell 网络沙箱失败、随后 API 限流，经正常只读工具取得正文；失败请求不计证据。没有执行源码、构建或运行检查。

## 已核事实

1. root 实际亲见 [LNS.cpp L18/49/73/78/96–98/166](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp#L96)：存在 Time::now，runtime 由 elapsed duration 得到，循环条件依赖 runtime 与 time_limit。L467 把剩余时间传 InitLNS，L567/575/591 计算并传剩余时间给 findPath，L655 构造 Deadline 再交 solve。因此“固定规划不读外部时间”不成立；不能将“随机/时钟在快照中”当成已定义时钟演化。
2. 代理实际亲见包含链 LNS.h:L2 → BasicLNS.h:L2 → lns_common.h；[lns_common.h L44–45](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lns_common.h#L44) 的 Time 为 std::chrono::high_resolution_clock，fsec 为 duration<float>。BasicLNS.h:L71 的 start_time 同属该 clock。平台标准库的具体 alias 未核，壁钟/单调属性 UNKNOWN；不能称为已核 CPU 时间。using std::clock 的名字导入不证明调用。
3. [LNS.h L62](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h#L62) 将整数入口 time 赋 double time_limit，并按原表达式计算 replan_time_limit。源码的计算规则是原语义，未授予改变保护参数定义或数值的权限。
4. [utils.hpp L23、36–42](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/utils.hpp#L23) 的 SteadyTime 明确是 steady_clock。[utils.cpp L5–20、35–38](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/utils.cpp#L5) 在构造时取起点，elapsed_ms/ns 先转整数单位再返回 double；非空 deadline 的到期判据是 elapsed_ms 严格大于 time_limit_ms。它是单调经过时间，不是 CPU 用时。
5. [planner.cpp L102–108、148、187、193、381](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp#L148) 保存指针并在主循环、部分 break 与 PIBT 循环处检查到期。此证据只支持实际检查位置，不证明所有内部工作均能即时中断。
6. [MAPFPlanner.cpp L6–20、46 起](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp#L46)：initialize 把 preprocess_time_limit 传 LNS，但 initMap/computeAllPair 在前，入口不证明整体预处理受其约束。三个 plan 分支都设置运行限制，首次分支再按原字面量覆盖；本记录不采用该字面量为本项目取值。入口本身没有读取 clock 或构造 Deadline，实际读取在下游。

## 未闭合事项与用于后继的范围

high_resolution_clock 的实际标准库定义仍 UNKNOWN；lacam2/lacam2.cpp 的 solve 自由函数转发未读（仅目录 blob 75ee58f4e1adb46ad3b26991cc212929bbff5f60 / 464 bytes）；InitLNS、SIPP/SpaceTimeAStar 内部计时与停止依赖未读。此处不能称“逐跳核完全部调用链”或“完整时钟清单已闭合”。后继若映射时间输入，需覆盖已读分支与实际启用依赖，并保留原终止比较/单位语义；源码证据本身不决定共享适配中排队、抢占、恢复时 clock 返回什么。

原生 R0 与共享因果适配仍分轨；不能把改了时钟语义的适配输出冒称原字节 trace 等价。对大规模实验，规划等待和实际计算如何占用物理时间直接影响任务吞吐，费用/时钟/停止映射是公平性的一部分；未运行不是纸面问题的豁免，也不要求现在实现虚拟机或跑一次试验。此回执只帮助关闭来源前提，不替任何资格门投票。
