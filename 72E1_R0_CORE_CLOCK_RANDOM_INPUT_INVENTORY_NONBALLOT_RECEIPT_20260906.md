# R0 规划核心时钟／随机输入静态清单：既有实际回执归档

- 工件性质：**NONBALLOT / NO-SKILL**；不是原 69E1 全仓审计重派，不是正式审稿。
- 固定仓库：YueZhang-studyuse/LMAPF-delay。
- 正确固定提交：`0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。
- 正确 tree 链接：[固定提交目录](https://github.com/YueZhang-studyuse/LMAPF-delay/tree/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357)。
- 行政更正：此前 37 对象回执顶端 tree URL 有提交字符串拼写错误；正文固定文件 URL、所用对象身份及本件正确提交不变。
- 本件只归档先前已完成、已实际交付的 37 对象关键词清单及其行政补充。归档阶段复用仍存在的内存缓存，没有重新联网、重新扩展搜索、运行源码、实现适配器、构建、测试、仿真、实验或项目／保护参数赋值。
- 先前清单阶段的旧内存缓存曾不可用，因此当时按固定 blob 重新获取；这与本次归档阶段没有再次获取相区分。
- 本次唯一新工件为本 Markdown；摘要与字节／行统计由归档完成回执另外给出，避免文件自引用摘要。

## 1. 完成范围与证据性质

实际搜索对象为官方 headless MAPFPlanner 的源／头文件，以及 MAPF-LNS2 源／头目录和其中 lacam2 子目录，共 **37/37 个对象**，未超过 40 对象边界。全部完整获取至内存；全文 UTF-8 内容共 **304149 bytes、8713 行**。此前实际计算的 Git blob SHA-1 与固定目录元数据、字节数全部相符；全文 SHA256 见对象表。

每个对象的关键词搜索范围都是 L1 至其总行数。人工阅读的是检索命中及必要上下文；**完整获取和全文关键词检索不等于全文语义审计**。

只读取源码中的 Instance.cpp/.h 和 lacam_instance.cpp/.hpp，没有读取任何实例、地图、任务、data 或延迟／trace 载荷。没有读取本地候选、旧 35–38、Q 载荷或桌面。

先前定位所用非递归源码树：
- `inc/MAPF-LNS2/inc`：`20df51622b7b7fa1854b185273e02d38a063d25d`。
- `src/MAPF-LNS2/src`：`76bb16539f95d05f2dc0882d8c06dcd5a47ed2b9`。
- `inc/MAPF-LNS2/inc/lacam2`：`59ef100f87fdc799eec64d8611d35cb9cf8e5975`。
- `src/MAPF-LNS2/src/lacam2`：`6dac3d4b4eddf5132f46a6a721e04b18e62bea6c`。

根代理另告知其已亲见 `mcp.cpp:L14–72` 与 `SingleAgentSolver.h:L35–100`。本条只记录**根告知**，不能表述为归档阶段由本代理重新取得或独立验证。

## 2. 原实际清单结论与新增登记项

**限定集合内新增需要登记的是 MCP 的 CPU 时钟日志读取，以及分散在比较器、路径表、初始化和 LaCAM 中的随机调用。没有发现可执行的 time() 播种、OS 熵读取或 sleep／等待 API 直接调用。**

1. **CPU 时钟日志。** `src/MAPF-LNS2/src/mcp.cpp:L24、65` 实际调用 `(float)clock() / (float)CLOCKS_PER_SEC`，打印 MCP::simulate 起止时间。两处没有减去本地起点，返回值直接送日志而非这两处的停止条件。L139 同类调用被注释。应独立登记 CPU 时钟读取／日志事件，不能混入原 high_resolution_clock 或 steady_clock 预算域。
2. **C 随机状态消费。** rand() 除 LNS／InitLNS 外，还出现在 BasicLNS.cpp:L16、PathTable.cpp:L81、94、121、152、181，以及 SingleAgentSolver.h:L51、93 的有效比较器分支。比较器中的状态消费不能因其不属于显式邻居抽样而漏记。
3. **默认生成器 random_shuffle。** Instance.cpp:L51 的 dummy-goal 排序也使用 std::random_shuffle。所用标准库后端尚未核，不能把其跨平台随机序列直接等同于已固定的某个生成器。
4. **LaCAM 独立 MT 生命周期。** LNS.cpp:L654 在每次 runLACAM2() 内构造 std::mt19937(0)，L659 传给 solve。该局部生成器重建及源码字面量仅作来源事实，未转成项目设置。Planner 使用该状态进行重启抽样、shuffle 和 tie-breaker 抽样；utils.cpp 中存在 uniform_real_distribution<float> 与 uniform_int_distribution<int> 封装。
5. **另一随机构造接口。** lacam_instance.cpp:L79、89、101 的文件名＋mt19937* 构造重载使用 std::shuffle。已显示的 LNS::runLACAM2():L651 使用 LACAMInstance(instance.env)，不能把另一重载自动视作该明示调用路径。
6. **既有 Deadline 的附加读取点。** lacam2/planner.hpp:L127 的日志表达式调用 elapsed_ms(deadline)，属于既有 steady-clock 接口的另一个调用点，不是新时钟类型。

清单层面的映射需求分别涉及：C 随机状态、默认 random_shuffle 后端、局部 MT 构造与状态消费、CPU 日志时钟、以及已登记的两种 chrono 时钟。这里没有实现适配器、调整原算法或指定保护参数。

更早 71E3 中“所读直接路径未见 CPU 时钟调用”的表述只覆盖当时窄窗口，不能扩展为本次 37 对象范围无 CPU 时钟。LNS／InitLNS／SIPP 已核时间语义不在本件重新判读。


## 3. 37 个实际搜索对象与完整身份

| 固定提交对象 | Git blob SHA-1 | 全文 SHA256 | bytes | 总行数／搜索末行 |
|---|---|---|---:|---:|
| [inc/MAPF-LNS2/inc/BasicLNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/BasicLNS.h) | `c22e0b66cc58e9c9ce19d6b161e4f54dabfb4c15` | `9927e17d5c6dd3624ed4e5dc3cc81c20eec854b340ddf4723f93d873a6b526ff` | 2042 | 77 |
| [inc/MAPF-LNS2/inc/ConstraintTable.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/ConstraintTable.h) | `989911214dd4e5045ba392c1526c7b41deeb4da6` | `b9f36851fc2fb53afa8cf81d7c96314b819f91fd902e4e1c396982297202b61c` | 3362 | 67 |
| [inc/MAPF-LNS2/inc/InitLNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/InitLNS.h) | `e3a93022b865afbcd539e9305e618ddc29829c5e` | `7fe9f3e25a9ce2c77a83e8ec3c6177195d464890b1b9690f42abbca25d4d8901` | 1838 | 58 |
| [inc/MAPF-LNS2/inc/Instance.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/Instance.h) | `97808fa7929c1f99772b05b047c20d48bb878814` | `ed1dea14eba7373d13b2378e59839bf962085316ffb6527655f92dfc5aae565d` | 4939 | 154 |
| [inc/MAPF-LNS2/inc/lacam2/graph.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/graph.hpp) | `bdf87cf5a1b911c039ebcf10374ddf317086fbd4` | `166b3ecbe68e7ddcd549504044a3c47cc3abb9ca98653b8639a654607480daee` | 1699 | 61 |
| [inc/MAPF-LNS2/inc/lacam2/lacam_instance.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/lacam_instance.hpp) | `7ada1b5832c0f45a510bb9c98cb97b459731d3f8` | `97d98a8807b64c0cf56ec71ba57bdd6f31c8a15b4fb1155972645d416f38ff1b` | 1205 | 46 |
| [inc/MAPF-LNS2/inc/lacam2/lacam2.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/lacam2.hpp) | `b12113c7e263ac570f53f0af533ec86de9a8bb4d` | `64bdb7cc7b0c0d439bd3dc5a029db70102a1e538b21208b8b3ffb129dce1bfa9` | 481 | 13 |
| [inc/MAPF-LNS2/inc/lacam2/planner.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/planner.hpp) | `48ec12187373e87d6a233bfebea5eaf8b26c9304` | `8e7c6b7221828ef17a73730a3a33c39d5fcc9ccd9f73a6697c7434162ae7312c` | 3850 | 132 |
| [inc/MAPF-LNS2/inc/lacam2/utils.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/utils.hpp) | `49965f9dc210d3691f35692769f541dada74ea13` | `8c647381901498a3c8033db7117a8696ab38df0858cb9b9520d05edcaee87442` | 1131 | 50 |
| [inc/MAPF-LNS2/inc/lns_common.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lns_common.h) | `3bddf54ab74388904064a60a92346883a52c10cb` | `8994fbaf6e022f7b233b7015741ae277d5773f3c84665845ecc654b44a51ccf6` | 2890 | 102 |
| [inc/MAPF-LNS2/inc/LNS.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/LNS.h) | `5b9ce3ef4aeaf6fcfa88c211c0f536c66f8ae24e` | `c9751aca5f3c305d5da49c3445ec29cb19819655b496de12c522d83d7af7ad91` | 4201 | 119 |
| [inc/MAPF-LNS2/inc/mcp.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/mcp.h) | `bec4ba40460faa672be93ef0cb45d3a8fd31fa57` | `420fde80e362234d54f7ea12a1021f228e106a322754a4544e16c87cdf4ac2e0` | 2751 | 94 |
| [inc/MAPF-LNS2/inc/PathTable.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/PathTable.h) | `0ae813e9526367d3076c297deba51fc0ad3a5a76` | `909a0fe4a8ebb89a69819d47cf80db579ed1793a75d1936dc2787edddd5ecbc2` | 3090 | 56 |
| [inc/MAPF-LNS2/inc/ReservationTable.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/ReservationTable.h) | `43c8a4477b18be3be5f0da866d4150b85ef87742` | `73f59983d08b614f22b2becd4750420df140a8c5f0a5200997d715c7678995b1` | 1352 | 31 |
| [inc/MAPF-LNS2/inc/SingleAgentSolver.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SingleAgentSolver.h) | `c22f59ac763c3bc272a82b5c8e9793a91f5da94a` | `daafdc674f90bbe4b34031b19f2564fb93189f07d7ad15e0927e1574cbb5611f` | 7935 | 226 |
| [inc/MAPF-LNS2/inc/SIPP.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SIPP.h) | `9f2366ad6e8bf4084299b6d3649414394c850694` | `8ebf98b9518844473ac66f6064e5c9810774fe4f7f79fdb7e25fe4c69abd318d` | 5725 | 131 |
| [inc/MAPF-LNS2/inc/SpaceTimeAStar.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/SpaceTimeAStar.h) | `cdb96d96e01ae5efa43688019972efa37df01834` | `ef1416a0098f08a17606d734b77f3722a61c3984f795d17d681cdef1dd937909` | 4052 | 112 |
| [inc/MAPFPlanner.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPFPlanner.h) | `68fbfd7a13d2a1513c6634d41d0dca5133740aeb` | `d25fbcb08b6d80b4f03234b4f7c3c08c553d7074a7e12c47fee86d336409633e` | 971 | 42 |
| [src/MAPF-LNS2/src/BasicLNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/BasicLNS.cpp) | `c0c3ca34fb0f1c55cb67b0693de9e42d5b6503cf` | `662f58b4c8241c97933ee1272cf0d13f1733a1dbd9a120db7b620dea84e793ba` | 731 | 24 |
| [src/MAPF-LNS2/src/ConstraintTable.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/ConstraintTable.cpp) | `fea85b83b67af9afe7b92d39fc68e1b660c91c1d` | `b058741afebd738d0ba25f94112dd71c7f1b34b15f6e706fef1effd91844ca0c` | 9188 | 304 |
| [src/MAPF-LNS2/src/InitLNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/InitLNS.cpp) | `6af45595834e2afd82dba985ce5c8d2a6cab0225` | `798003fc1ce279392e2a847ef40411adc9fc12faa32604f9005f8da3cd3d9033` | 31656 | 889 |
| [src/MAPF-LNS2/src/Instance.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/Instance.cpp) | `2183ba41c4a04278fafa0c4ed0605762abd5fb7c` | `dcfd6fb4b134dcc437b6124d5bf099e4fd6a977e9f749607446e87b7fedae2ac` | 14658 | 455 |
| [src/MAPF-LNS2/src/lacam2/graph.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/graph.cpp) | `fb8ab481d5b1e3a959a18b826fd5919b69772e7e` | `7bdb71a22dbdf6df873370c20173f0ef9ab97c34fbb649f222c7bcb9fa2813a0` | 4405 | 185 |
| [src/MAPF-LNS2/src/lacam2/lacam_instance.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/lacam_instance.cpp) | `50f18e9ce8295ba94e4a7d5caa293d5affca0688` | `840d442a5f3a0804ae751e1c39797a3f669dd43dcadf48786b73b1fc0e2db1c4` | 4137 | 139 |
| [src/MAPF-LNS2/src/lacam2/lacam2.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/lacam2.cpp) | `75ee58f4e1adb46ad3b26991cc212929bbff5f60` | `107bdd83cef76baf86831c0a0f3c421d64e65c36381494d7438dfb1f6b1f2f05` | 464 | 10 |
| [src/MAPF-LNS2/src/lacam2/planner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp) | `4f46f988d2c16f09c5a6f65bb9cd70e8e01aa483` | `8d2fa9131f0691b109a00dd6267b3b48f80df7778643daeb806ff82e20fe2789` | 19115 | 616 |
| [src/MAPF-LNS2/src/lacam2/utils.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/utils.cpp) | `b10bf551c920677418610622d3ef7095e0e54656` | `7fc143b6073a7aa5673087ba878e88380020620c80e89f1f5094545fa67d1244` | 1222 | 51 |
| [src/MAPF-LNS2/src/lns_common.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lns_common.cpp) | `dd01957b58c6751e6d6dfd38c8d64503fdf8b94a` | `ea973229792c0ebaa92ac1986464fc87cb454e042e09ba96945a5f0e2911e877` | 453 | 23 |
| [src/MAPF-LNS2/src/lns_driver.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lns_driver.cpp) | `9743c96f157b10895fcbb63155c1f5116644ec83` | `65745a880ce5d3865039c03b59fafe5ebe568232fe7e05027119e268935fad8e` | 16288 | 377 |
| [src/MAPF-LNS2/src/LNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp) | `1fb0e54f8f2bb00af05de53233ae600774e36f2a` | `0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2` | 53100 | 1486 |
| [src/MAPF-LNS2/src/mcp.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/mcp.cpp) | `ec7c149fa01206752ae1eeebff64f699facc2bb2` | `c228082f5d0ae6001366022baace45e4a8c3b4563fe60cb06a3ab8d59bfa3aaf` | 13558 | 427 |
| [src/MAPF-LNS2/src/PathTable.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/PathTable.cpp) | `1dd06d5c8ef71841409a88517cc419df841fefb8` | `96cb8eaef095e01f99f69b91951372c5c2d2f966c6c2c126f315bdbdc429321c` | 12025 | 374 |
| [src/MAPF-LNS2/src/ReservationTable.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/ReservationTable.cpp) | `19351b1629d5ea28107209b8de8a6b67c966b010` | `9df38c7ded4a206c53098156968cb4bfe8ce7f930e436d9d770a10485506f689` | 15974 | 418 |
| [src/MAPF-LNS2/src/SingleAgentSolver.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SingleAgentSolver.cpp) | `bbbc5d1745a8c649ddb29ecbc27122ba92f0a6ef` | `ef3f96da47b9fdd830e4aafff90677f85168370e3ae2fdbb0b402555d4539d30` | 6545 | 176 |
| [src/MAPF-LNS2/src/SIPP.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SIPP.cpp) | `7f8db084c2d03929f51c28a76a29895fbaaa1a64` | `3cb627fcd4a0ebe2646be9985e58bd16ef5f01ff3fce357ab4584b0045d2e2b7` | 30068 | 680 |
| [src/MAPF-LNS2/src/SpaceTimeAStar.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/SpaceTimeAStar.cpp) | `1712e6d081337461437e3458c40fdcb8ef3de8ef` | `4ccef3b2b34a964bd5377e6b742876f371b4fa553d3aa458926c56b2f6f485ac` | 10923 | 300 |
| [src/MAPFPlanner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp) | `94afb42df1a70f5e312a382e61cf83576fd7360e` | `c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1` | 6125 | 208 |

## 4. 实际使用的关键词模式

以下照录当次使用的 JavaScript 正则，区分大小写，逐行 .test()，不带 i／g 标志。本次归档没有重新执行这些检索。

### 4.1 初始原文与屏蔽文本三组

```javascript
clock:
/\b(?:chrono|now|high_resolution_clock|steady_clock|system_clock|Time|SteadyTime|clock|clock_gettime|clock_getres|gettimeofday|times|getrusage|ftime|timespec_get|omp_get_wtime|QueryPerformanceCounter|QueryPerformanceFrequency|GetTickCount|GetTickCount64|__rdtsc|rdtsc|rdtscp|CLOCK_[A-Z_]+)\b|\btime\s*\(/

rng:
/\b(?:rand|rand_r|srand|random|srandom|random_r|srandom_r|drand48|erand48|lrand48|nrand48|mrand48|jrand48|srand48|seed48|lcong48|random_device|seed|seed_seq|mt19937|mt19937_64|default_random_engine|ranlux\w*|knuth_b|minstd_rand\w*|random_shuffle|shuffle|sample|getrandom|getentropy|arc4random\w*|RAND_bytes|RAND_priv_bytes|MT|get_random_\w+|\w*distribution|\w*random_engine)\b|\/dev\/(?:u)?random/

wait:
/\b(?:sleep|usleep|nanosleep|clock_nanosleep|sleep_for|sleep_until|wait|wait_for|wait_until|pthread_cond_timedwait|pthread_cond_wait|poll|ppoll|select|pselect|Sleep)\s*\(|\bthis_thread\b/
```

### 4.2 补充接口组：原文

```javascript
/\b(?:syscall|asm|__asm__|boost::random|boost::chrono|boost::posix_time|SDL_GetTicks|glfwGetTime|ros::Time|rclcpp::Clock|mach_absolute_time|timeGetTime|std::sample|setstate|initstate|seed_seq|generate_canonical|independent_bits_engine|discard_block_engine|shuffle_order_engine|linear_congruential_engine|mersenne_twister_engine|subtract_with_carry_engine|normal_distribution|exponential_distribution|discrete_distribution)\b/
```

当次结果：没有命中。

### 4.3 直接调用／熵／播种阴性组：屏蔽文本

```javascript
legacy_time:
/\b(?:time|clock_gettime|clock_getres|gettimeofday|times|getrusage|ftime|timespec_get|omp_get_wtime|QueryPerformanceCounter|QueryPerformanceFrequency|GetTickCount|GetTickCount64|__rdtsc|rdtsc|rdtscp|mach_absolute_time|timeGetTime)\s*\(/

os_entropy:
/\b(?:random_device|getrandom|getentropy|arc4random\w*|RAND_bytes|RAND_priv_bytes)\b|\/dev\/(?:u)?random/

rng_seed:
/\b(?:srand|srandom|srand48|seed48|lcong48|initstate|setstate|seed_seq|seed)\s*\(/

wait:
/\b(?:sleep|usleep|nanosleep|clock_nanosleep|sleep_for|sleep_until|wait|wait_for|wait_until|pthread_cond_timedwait|pthread_cond_wait|poll|ppoll|select|pselect|Sleep)\s*\(/
```

当次四组结果均无有效代码命中。/dev/random 与 /dev/urandom 字面量的阴性依据是前面的原文检索；不能用已屏蔽字符串后的结果替代该依据。这里没有把 std::mt19937(0) 的构造漏记为“没有任何初始化”；它已经作为独立构造与生命周期事实登记。

### 4.4 既有 Deadline 包装接口组：屏蔽文本

```javascript
/\b(?:Deadline|elapsed_ms|elapsed_ns|is_expired)\b/
```

### 4.5 实际辅助模式

```javascript
/\bR"/
/^\s*#\s*(?:if|ifdef|ifndef|elif|else|endif|define)\b/
```

前者当次显示 graph.cpp:L62–64 及 lacam_instance.cpp:L42 的四个原始字符串正则字面量；它们不是相关外部输入接口。后者仅命中 lns_common.h:L47–49 与 PathTable.h:L4 的常量宏，没有在这 37 个文件中命中条件预处理分支。没有处理或排除外部头文件中的条件编译／宏展开。


## 5. 原文、去注释掩码与分类方法

当次处理过程：
1. 按完整原文逐行执行初始三组检索，保留文件、原行号及命中原文。
2. 使用下列实际缓存的 stripCpp 函数，将行注释、块注释、普通双引号／单引号字面量及其转义内容替换为空格，保留换行，再执行代码命中分组。
3. 人工核对需要区分的比较器、CPU 日志、注释播种、哈希 seed 等窗口；另显示原始字符串位置、文件内预处理分支／宏。
4. 输出中的“屏蔽后命中”只表示词法层面没有被该掩码移除，不自动证明调用可达、已链接或已经执行；include、声明、字段和哈希累加变量另行分类。

该方法不是 C++ AST、预处理器、链接器或运行时追踪。掩码函数没有专门的 C++ 原始字符串语法状态；本次实际四个原始字符串另作了定点显示核对，不能将这次处理泛化为任意 C++ 源的完备解析器。

当次实际函数原码（从已有内存缓存归档；本次未重新执行）：

```javascript
function stripCpp(s){let o="",i=0,mode="code";while(i<s.length){let a=s[i],b=s[i+1];if(mode==="line"){if(a==="\n"){o+="\n";mode="code";}else o+=" ";i++;continue;}if(mode==="block"){if(a==="*"&&b==="/"){o+="  ";i+=2;mode="code";}else{o+=a==="\n"?"\n":" ";i++;}continue;}if(mode==="double"||mode==="single"){const q=mode==="double"?'"':"'";if(a==="\\"){o+=" ";i++;if(i<s.length){o+=s[i]==="\n"?"\n":" ";i++;}}else {o+=a==="\n"?"\n":" ";i++;if(a===q)mode="code";}continue;}if(a==="/"&&b==="/"){o+="  ";i+=2;mode="line";continue;}if(a==="/"&&b==="*"){o+="  ";i+=2;mode="block";continue;}if(a==='"'||a==="'"){o+=" ";i++;mode=a==='"'?"double":"single";continue;}o+=a;i++;}return o;}
```


## 6. 原实际原文命中缓存（包含声明、注释和字符串）

### inc/MAPF-LNS2/inc/BasicLNS.h

**clock**

```text
71:     high_resolution_clock::time_point start_time;
```

### inc/MAPF-LNS2/inc/lacam2/lacam_instance.hpp

**rng**

```text
5: #include <random>
28:     // random instance generation
29:     LACAMInstance(const std::string& map_filename, std::mt19937* MT,
```

### inc/MAPF-LNS2/inc/lacam2/lacam2.hpp

**rng**

```text
12:                std::mt19937* MT = nullptr, const Objective objective = OBJ_NONE,
```

### inc/MAPF-LNS2/inc/lacam2/planner.hpp

**rng**

```text
78:   std::mt19937* MT;
83:   const float RESTART_RATE;  // random restart
95:   std::vector<float> tie_breakers;              // random values, used in PIBT
100:   Planner(const Instance& _instance, const LACAMInstance* _ins, const Deadline* _deadline, std::mt19937* _MT,
```

### inc/MAPF-LNS2/inc/lacam2/utils.hpp

**clock**

```text
7: #include <chrono>
23: using SteadyTime = std::chrono::steady_clock;
37:   const SteadyTime::time_point t_s;
```

**rng**

```text
14: #include <random>
49: float get_random_float(std::mt19937* MT, float from = 0, float to = 1);
50: int get_random_int(std::mt19937* MT, int from = 0, int to = 1);
```

### inc/MAPF-LNS2/inc/lns_common.h

**clock**

```text
11: #include <chrono>
37: using std::clock;
43: using namespace std::chrono;
44: typedef std::chrono::high_resolution_clock Time;
45: typedef std::chrono::duration<float> fsec;
```

### inc/MAPF-LNS2/inc/LNS.h

**clock**

```text
18: // decrease it if replanning fails to find any solutions for several times
```

### inc/MAPF-LNS2/inc/SingleAgentSolver.h

**rng**

```text
32:     //                 return rand() % 2 == 0;   // break ties randomly
51: 						return rand() % 2 == 0;   // break ties randomly
72:     //                     return rand() % 2 == 0;   // break ties randomly
93: 							return rand() % 2 == 0;   // break ties randomly
```

### inc/MAPF-LNS2/inc/SIPP.h

**rng**

```text
46:             size_t seed = 0;
47:             boost::hash_combine(seed, n->location);
48:             boost::hash_combine(seed, n->high_generation);
49:             return seed;
```

### src/MAPF-LNS2/src/BasicLNS.cpp

**rng**

```text
16:     double r = (double) rand() / RAND_MAX;
```

### src/MAPF-LNS2/src/InitLNS.cpp

**clock**

```text
39:     start_time = Time::now();
41:     runtime = ((fsec)(Time::now() - start_time)).count();
181:         runtime = ((fsec)(Time::now() - start_time)).count();
238:     runtime = ((fsec)(Time::now() - start_time)).count();
245:     auto time = Time::now();
247:     while (p != shuffled_agents.end() && !timeout_flag && ((fsec)(Time::now() - time)).count() < T)
251:         agents[id].path = agents[id].path_planner->findPath(constraint_table, T - ((fsec)(Time::now() - time)).count(),timeout_flag);
265:             runtime = ((fsec)(Time::now() - start_time)).count();
340:         runtime = ((fsec)(Time::now() - start_time)).count();
```

**rng**

```text
227:     std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());
327:     std::random_shuffle(neighbor.agents.begin(), neighbor.agents.end());
459:             int a1 = *std::next(neighbors_set.begin(), rand() % neighbors_set.size());
474:                 a = std::next(G.begin(), rand() % G.size())->first;
479:                 a = *std::next(G[a].begin(), rand() % G[a].size());
499:     auto v = all_vertices[rand() % all_vertices.size()]; // pick a random vertex
512:             int a1 = *std::next(neighbors_set.begin(), rand() % neighbors_set.size());
522:         int a = std::next(G.begin(), rand() % G.size())->first;
526:             a = *std::next(G[a].begin(), rand() % G[a].size());
539:     auto r = rand() % (num_of_colliding_pairs * 2);
590:             std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());
597:             std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());
623:             int rand_int = rand() % neighbors_set.size();
641:             rand_int = rand() %targets.size();
668:             r[i] = rand() % total;
691:     int t = rand() % agents[agent_id].path.size();
700:         int step = rand() % next_locs.size();
702:         loc = *std::next(next_locs.begin(), rand() % next_locs.size());
708:         return *std::next(path_table.table[loc][t].begin(), rand() % path_table.table[loc][t].size());
```

### src/MAPF-LNS2/src/Instance.cpp

**clock**

```text
4: #include <chrono>       // std::chrono::system_clock
```

**rng**

```text
2: #include <algorithm>    // std::shuffle
3: #include <random>      // std::default_random_engine
51:     std::random_shuffle(dummy_goals.begin(), dummy_goals.end());
```

### src/MAPF-LNS2/src/lacam2/lacam_instance.cpp

**rng**

```text
79: LACAMInstance::LACAMInstance(const std::string& map_filename, std::mt19937* MT,
83:   // random assignment
89:   std::shuffle(s_indexes.begin(), s_indexes.end(), *MT);
101:   std::shuffle(g_indexes.begin(), g_indexes.end(), *MT);
```

### src/MAPF-LNS2/src/lacam2/lacam2.cpp

**rng**

```text
4:                const int verbose, const Deadline* deadline, std::mt19937* MT,
7:   auto planner = Planner(instance, &ins, deadline, MT, verbose, objective, restart_rate);
```

### src/MAPF-LNS2/src/lacam2/planner.cpp

**clock**

```text
342:         // set occupied now
```

**rng**

```text
103:                  std::mt19937* _MT, const int _verbose,
109:       MT(_MT),
218:             // re-insert or random-restart
219:             auto H_insert = (MT != nullptr && get_random_float(MT) >= RESTART_RATE)
318:     if (MT != nullptr) std::shuffle(C.begin(), C.end(), *MT); //random the order (neighbor)
403:         if (MT != nullptr)
404:             tie_breakers[u->id] = get_random_float(MT);  // set tie-breaker
```

### src/MAPF-LNS2/src/lacam2/utils.cpp

**clock**

```text
6:     : t_s(SteadyTime::now()), time_limit_ms(_time_limit_ms)
12:   return std::chrono::duration_cast<std::chrono::milliseconds>(SteadyTime::now() -
19:   return std::chrono::duration_cast<std::chrono::nanoseconds>(SteadyTime::now() - t_s)
```

**rng**

```text
41: float get_random_float(std::mt19937* MT, float from, float to)
43:   std::uniform_real_distribution<float> r(from, to);
44:   return r(*MT);
47: int get_random_int(std::mt19937* MT, int from, int to)
49:   std::uniform_int_distribution<int> r(from, to);
50:   return r(*MT);
```

### src/MAPF-LNS2/src/lns_driver.cpp

**clock**

```text
27: //         ("cutoffTime,t", po::value<double>()->default_value(7200), "cutoff time (seconds)")
76: // 	srand((int)time(0));
```

**rng**

```text
38: // 		("seed", po::value<int>()->default_value(0), "Random seed")
76: // 	srand((int)time(0));
82: // 	srand(vm["seed"].as<int>());
```

### src/MAPF-LNS2/src/LNS.cpp

**clock**

```text
18:     start_time = Time::now();
49:     preprocessing_time = ((fsec)(Time::now() - start_time)).count();
73:         start_time = Time::now();
78:     initial_solution_runtime = ((fsec)(Time::now() - start_time)).count();
98:         runtime =((fsec)(Time::now() - start_time)).count();
166:         runtime = ((fsec)(Time::now() - start_time)).count();
450:         start_time = Time::now();
467:         init_lns = new InitLNS(instance, agents, time_limit - ((fsec)(Time::now() - start_time)).count(),
481:         initial_solution_runtime = ((fsec)(Time::now() - start_time)).count();
492:     start_time = Time::now();
500:         start_time = Time::now();
519:     start_time = Time::now();
561:     runtime = ((fsec)(Time::now() - start_time)).count();
567:     auto time = Time::now();
570:     while (p != shuffled_agents.end() && ((fsec)(Time::now() - time)).count() < T)
575:             auto remain_time = T - ((fsec)(Time::now() - time)).count();
576:             auto avg_single = ((fsec)(Time::now() - time)).count()/((int)shuffled_agents.size()-remaining_agents);
587:                  ", remaining time = " << T - ((fsec)(Time::now() - time)).count() << " seconds. " << endl
591:         agents[id].path = agents[id].path_planner->findPath(constraint_table, T - ((fsec)(Time::now() - time)).count(),timeout_flag);
1072:                  "runtime of initial solution,restart times,area under curve," <<
1381:     //start_time = Time::now(); 
```

**rng**

```text
119:                     std::random_shuffle(neighbor.agents.begin(), neighbor.agents.end());
547:     std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());
654:     auto MT = std::mt19937(0);
659:     const auto solution = solve(instance, ins, verbose, commit, 0, &deadline, &MT, objective, restart_rate);
741:     std::advance(pt, rand() % intersections.size());
772:         std::random_shuffle(neighbor.agents.begin(), neighbor.agents.end());
801:         int t = rand() % agents[a].path.size();
810:         int idx = rand() % neighbors_set.size();
826:         cout << "Generate " << neighbor.agents.size() << " neighbors by random walks of agent " << a<<endl;
866:     int pt = rand() % (sum_of_costs - sum_of_distances) + 1;
878: // a random walk with path that is shorter than upperbound and has conflicting with neighbor_size agents
889:             int step = rand() % next_locs.size();
920:             int step = rand() % next_locs.size();
```

### src/MAPF-LNS2/src/mcp.cpp

**clock**

```text
24:     cout<<"Start "<<(float)clock()/(float)CLOCKS_PER_SEC<<endl;
65:     cout<<"Simulation done at "<<(float)clock()/(float)CLOCKS_PER_SEC << endl;
139:         // cout<<"time "<<(float)clock()/(float)CLOCKS_PER_SEC<<endl;
407:     cout << "==================== Time ====================" << endl;
412:     cout << "================== End Time ==================" << endl;
418:     cout << "==================== Time ====================" << endl;
426:     cout << "================== End Time ==================" << endl;
```

### src/MAPF-LNS2/src/PathTable.cpp

**rng**

```text
81:             insert_to_set = (rand()%stay_target[agent] < 1);
94:             insert_to_set = (rand()%stay_target[agent] < 1);
121:     int t0 = rand() % t_max;
152:     int t0 = rand() % t_max;
181:         insert_to_set = (rand()*(stay_target[agent] + 1) < 1);
```

### src/MAPF-LNS2/src/SIPP.cpp

**clock**

```text
32:     auto start_time = Time::now();
62:         if (((fsec)(Time::now() - start_time)).count() >= timeout)
```

### src/MAPF-LNS2/src/SpaceTimeAStar.cpp

**clock**

```text
115:             { // now everything is static, so switch to space A* where we always use the same timestep
```

### src/MAPFPlanner.cpp

**rng**

```text
2: #include <random>
```


## 7. 原实际屏蔽后命中缓存（不自动等于可达调用）

### inc/MAPF-LNS2/inc/BasicLNS.h

**clock**

```text
71:     high_resolution_clock::time_point start_time;
```

### inc/MAPF-LNS2/inc/lacam2/lacam_instance.hpp

**rng**

```text
5: #include <random>
29:     LACAMInstance(const std::string& map_filename, std::mt19937* MT,
```

### inc/MAPF-LNS2/inc/lacam2/lacam2.hpp

**rng**

```text
12:                std::mt19937* MT = nullptr, const Objective objective = OBJ_NONE,
```

### inc/MAPF-LNS2/inc/lacam2/planner.hpp

**rng**

```text
78:   std::mt19937* MT;
100:   Planner(const Instance& _instance, const LACAMInstance* _ins, const Deadline* _deadline, std::mt19937* _MT,
```

### inc/MAPF-LNS2/inc/lacam2/utils.hpp

**clock**

```text
7: #include <chrono>
23: using SteadyTime = std::chrono::steady_clock;
37:   const SteadyTime::time_point t_s;
```

**rng**

```text
14: #include <random>
49: float get_random_float(std::mt19937* MT, float from = 0, float to = 1);
50: int get_random_int(std::mt19937* MT, int from = 0, int to = 1);
```

### inc/MAPF-LNS2/inc/lns_common.h

**clock**

```text
11: #include <chrono>
37: using std::clock;
43: using namespace std::chrono;
44: typedef std::chrono::high_resolution_clock Time;
45: typedef std::chrono::duration<float> fsec;
```

### inc/MAPF-LNS2/inc/SingleAgentSolver.h

**rng**

```text
51: 						return rand() % 2 == 0;   // break ties randomly
93: 							return rand() % 2 == 0;   // break ties randomly
```

### inc/MAPF-LNS2/inc/SIPP.h

**rng**

```text
46:             size_t seed = 0;
47:             boost::hash_combine(seed, n->location);
48:             boost::hash_combine(seed, n->high_generation);
49:             return seed;
```

### src/MAPF-LNS2/src/BasicLNS.cpp

**rng**

```text
16:     double r = (double) rand() / RAND_MAX;
```

### src/MAPF-LNS2/src/InitLNS.cpp

**clock**

```text
39:     start_time = Time::now();
41:     runtime = ((fsec)(Time::now() - start_time)).count();
181:         runtime = ((fsec)(Time::now() - start_time)).count();
238:     runtime = ((fsec)(Time::now() - start_time)).count();
245:     auto time = Time::now();
247:     while (p != shuffled_agents.end() && !timeout_flag && ((fsec)(Time::now() - time)).count() < T)
251:         agents[id].path = agents[id].path_planner->findPath(constraint_table, T - ((fsec)(Time::now() - time)).count(),timeout_flag);
265:             runtime = ((fsec)(Time::now() - start_time)).count();
340:         runtime = ((fsec)(Time::now() - start_time)).count();
```

**rng**

```text
227:     std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());
327:     std::random_shuffle(neighbor.agents.begin(), neighbor.agents.end());
499:     auto v = all_vertices[rand() % all_vertices.size()]; // pick a random vertex
512:             int a1 = *std::next(neighbors_set.begin(), rand() % neighbors_set.size());
522:         int a = std::next(G.begin(), rand() % G.size())->first;
526:             a = *std::next(G[a].begin(), rand() % G[a].size());
539:     auto r = rand() % (num_of_colliding_pairs * 2);
590:             std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());
597:             std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());
623:             int rand_int = rand() % neighbors_set.size();
641:             rand_int = rand() %targets.size();
668:             r[i] = rand() % total;
691:     int t = rand() % agents[agent_id].path.size();
700:         int step = rand() % next_locs.size();
702:         loc = *std::next(next_locs.begin(), rand() % next_locs.size());
708:         return *std::next(path_table.table[loc][t].begin(), rand() % path_table.table[loc][t].size());
```

### src/MAPF-LNS2/src/Instance.cpp

**clock**

```text
4: #include <chrono>       // std::chrono::system_clock
```

**rng**

```text
3: #include <random>      // std::default_random_engine
51:     std::random_shuffle(dummy_goals.begin(), dummy_goals.end());
```

### src/MAPF-LNS2/src/lacam2/lacam_instance.cpp

**rng**

```text
79: LACAMInstance::LACAMInstance(const std::string& map_filename, std::mt19937* MT,
89:   std::shuffle(s_indexes.begin(), s_indexes.end(), *MT);
101:   std::shuffle(g_indexes.begin(), g_indexes.end(), *MT);
```

### src/MAPF-LNS2/src/lacam2/lacam2.cpp

**rng**

```text
4:                const int verbose, const Deadline* deadline, std::mt19937* MT,
7:   auto planner = Planner(instance, &ins, deadline, MT, verbose, objective, restart_rate);
```

### src/MAPF-LNS2/src/lacam2/planner.cpp

**rng**

```text
103:                  std::mt19937* _MT, const int _verbose,
109:       MT(_MT),
219:             auto H_insert = (MT != nullptr && get_random_float(MT) >= RESTART_RATE)
318:     if (MT != nullptr) std::shuffle(C.begin(), C.end(), *MT); //random the order (neighbor)
403:         if (MT != nullptr)
404:             tie_breakers[u->id] = get_random_float(MT);  // set tie-breaker
```

### src/MAPF-LNS2/src/lacam2/utils.cpp

**clock**

```text
6:     : t_s(SteadyTime::now()), time_limit_ms(_time_limit_ms)
12:   return std::chrono::duration_cast<std::chrono::milliseconds>(SteadyTime::now() -
19:   return std::chrono::duration_cast<std::chrono::nanoseconds>(SteadyTime::now() - t_s)
```

**rng**

```text
41: float get_random_float(std::mt19937* MT, float from, float to)
43:   std::uniform_real_distribution<float> r(from, to);
44:   return r(*MT);
47: int get_random_int(std::mt19937* MT, int from, int to)
49:   std::uniform_int_distribution<int> r(from, to);
50:   return r(*MT);
```

### src/MAPF-LNS2/src/LNS.cpp

**clock**

```text
18:     start_time = Time::now();
49:     preprocessing_time = ((fsec)(Time::now() - start_time)).count();
73:         start_time = Time::now();
78:     initial_solution_runtime = ((fsec)(Time::now() - start_time)).count();
98:         runtime =((fsec)(Time::now() - start_time)).count();
166:         runtime = ((fsec)(Time::now() - start_time)).count();
450:         start_time = Time::now();
467:         init_lns = new InitLNS(instance, agents, time_limit - ((fsec)(Time::now() - start_time)).count(),
481:         initial_solution_runtime = ((fsec)(Time::now() - start_time)).count();
492:     start_time = Time::now();
500:         start_time = Time::now();
519:     start_time = Time::now();
561:     runtime = ((fsec)(Time::now() - start_time)).count();
567:     auto time = Time::now();
570:     while (p != shuffled_agents.end() && ((fsec)(Time::now() - time)).count() < T)
575:             auto remain_time = T - ((fsec)(Time::now() - time)).count();
576:             auto avg_single = ((fsec)(Time::now() - time)).count()/((int)shuffled_agents.size()-remaining_agents);
587:                  ", remaining time = " << T - ((fsec)(Time::now() - time)).count() << " seconds. " << endl
591:         agents[id].path = agents[id].path_planner->findPath(constraint_table, T - ((fsec)(Time::now() - time)).count(),timeout_flag);
```

**rng**

```text
119:                     std::random_shuffle(neighbor.agents.begin(), neighbor.agents.end());
547:     std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());
654:     auto MT = std::mt19937(0);
659:     const auto solution = solve(instance, ins, verbose, commit, 0, &deadline, &MT, objective, restart_rate);
741:     std::advance(pt, rand() % intersections.size());
772:         std::random_shuffle(neighbor.agents.begin(), neighbor.agents.end());
801:         int t = rand() % agents[a].path.size();
810:         int idx = rand() % neighbors_set.size();
866:     int pt = rand() % (sum_of_costs - sum_of_distances) + 1;
889:             int step = rand() % next_locs.size();
920:             int step = rand() % next_locs.size();
```

### src/MAPF-LNS2/src/mcp.cpp

**clock**

```text
24:     cout<<"Start "<<(float)clock()/(float)CLOCKS_PER_SEC<<endl;
65:     cout<<"Simulation done at "<<(float)clock()/(float)CLOCKS_PER_SEC << endl;
```

### src/MAPF-LNS2/src/PathTable.cpp

**rng**

```text
81:             insert_to_set = (rand()%stay_target[agent] < 1);
94:             insert_to_set = (rand()%stay_target[agent] < 1);
121:     int t0 = rand() % t_max;
152:     int t0 = rand() % t_max;
181:         insert_to_set = (rand()*(stay_target[agent] + 1) < 1);
```

### src/MAPF-LNS2/src/SIPP.cpp

**clock**

```text
32:     auto start_time = Time::now();
62:         if (((fsec)(Time::now() - start_time)).count() >= timeout)
```

### src/MAPFPlanner.cpp

**rng**

```text
2: #include <random>
```


## 8. 原实际 Deadline 包装接口命中缓存

### inc/MAPF-LNS2/inc/lacam2/lacam2.hpp

**deadline**

```text
11:                const int verbose = 0, const Deadline* deadline = nullptr,
```

### inc/MAPF-LNS2/inc/lacam2/planner.hpp

**deadline**

```text
77:   const Deadline* deadline;
100:   Planner(const Instance& _instance, const LACAMInstance* _ins, const Deadline* _deadline, std::mt19937* _MT,
127:     std::cout << "elapsed:" << std::setw(6) << elapsed_ms(deadline) << "ms"
```

### inc/MAPF-LNS2/inc/lacam2/utils.hpp

**deadline**

```text
36: struct Deadline {
40:   Deadline(double _time_limit_ms = 0);
41:   double elapsed_ms() const;
42:   double elapsed_ns() const;
45: double elapsed_ms(const Deadline* deadline);
46: double elapsed_ns(const Deadline* deadline);
47: bool is_expired(const Deadline* deadline);
```

### src/MAPF-LNS2/src/lacam2/lacam2.cpp

**deadline**

```text
4:                const int verbose, const Deadline* deadline, std::mt19937* MT,
```

### src/MAPF-LNS2/src/lacam2/planner.cpp

**deadline**

```text
102: Planner::Planner(const Instance& _instance, const LACAMInstance* _ins, const Deadline* _deadline,
148:     while (!OPEN.empty() && !is_expired(deadline)) 
187:         if (is_expired(deadline)) break;
193:         if (is_expired(deadline)) break;
381:         if (is_expired(deadline)) return false; //timeout
```

### src/MAPF-LNS2/src/lacam2/utils.cpp

**deadline**

```text
5: Deadline::Deadline(double _time_limit_ms)
10: double Deadline::elapsed_ms() const
17: double Deadline::elapsed_ns() const
23: double elapsed_ms(const Deadline* deadline)
26:   return deadline->elapsed_ms();
29: double elapsed_ns(const Deadline* deadline)
32:   return deadline->elapsed_ns();
35: bool is_expired(const Deadline* deadline)
38:   return deadline->elapsed_ms() > deadline->time_limit_ms;
```

### src/MAPF-LNS2/src/LNS.cpp

**deadline**

```text
655:     const auto deadline = Deadline((time_limit-0.1) * 1000);
```


## 9. 命中分类、阴性范围与未搜索范围

### 9.1 不能作为有效输入读取的命中

- lns_driver.cpp:L76 的 srand((int)time(0))、L82 的显式 seed 播种均被注释；当次去注释／字符串后的内容没有有效代码。
- SingleAgentSolver.h:L32、72 的另两处 rand() 被注释，不能与 L51、93 混同。
- InitLNS.cpp:L459、474、479 的 rand() 位于块注释。
- LNS.cpp:L1381 的 Time::now()、mcp.cpp:L139 的 clock() 被注释。
- SIPP.h:L46–49 的 seed 是 boost::hash_combine 局部哈希累加变量，不是随机采样或随机源初始化。
- 注释的 random／now／times、输出字符串中的 Time 及 include 与实际调用分开。
- get_random_int 在限定集合只命中声明和定义，没有找到调用点。

### 9.2 已搜索但未命中的直接接口类别

在上述 37 个对象的有效代码检索结果中，未命中：
- time()、clock_gettime、clock_getres、gettimeofday、times、getrusage、ftime、timespec_get，以及模式中列出的 OpenMP／Windows／硬件计时调用。
- random_device、getrandom、getentropy、arc4random*、OpenSSL 随机字节接口；原文也未命中 /dev/random／/dev/urandom。
- 可执行 srand／srandom／srand48 等模式所列播种或状态初始化调用。
- sleep、usleep、nanosleep、clock_nanosleep、sleep_for/until、wait/for/until、pthread 条件等待、poll/ppoll、select/pselect、Windows Sleep。

实际原文初始关键词也没有命中的 14 个已搜索对象：
- `inc/MAPF-LNS2/inc/ConstraintTable.h`
- `inc/MAPF-LNS2/inc/InitLNS.h`
- `inc/MAPF-LNS2/inc/Instance.h`
- `inc/MAPF-LNS2/inc/lacam2/graph.hpp`
- `inc/MAPF-LNS2/inc/mcp.h`
- `inc/MAPF-LNS2/inc/PathTable.h`
- `inc/MAPF-LNS2/inc/ReservationTable.h`
- `inc/MAPF-LNS2/inc/SpaceTimeAStar.h`
- `inc/MAPFPlanner.h`
- `src/MAPF-LNS2/src/ConstraintTable.cpp`
- `src/MAPF-LNS2/src/lacam2/graph.cpp`
- `src/MAPF-LNS2/src/lns_common.cpp`
- `src/MAPF-LNS2/src/ReservationTable.cpp`
- `src/MAPF-LNS2/src/SingleAgentSolver.cpp`

限定 37 对象内没有获取失败或未搜索对象。没有以“未搜索”冒充“未命中”。

### 9.3 未搜索／未核，仍为 UNKNOWN 的边界

- 限定集合之外的顶层 src/driver.cpp、其他顶层公共头／实现、外部依赖、标准库实现、动态／静态链接库、生成代码、编译配置和运行时路径未搜索。
- **C PRNG 的外层播种／初始化来源仍未核。** 不能由限定集合没有可执行 srand 推断外层未播种，不能指定其种子。
- **实验标准库 high_resolution_clock 的实际 alias 及其单调属性仍为 UNKNOWN。**
- 默认 random_shuffle 的实现后端、分布／shuffle 的跨平台序列及库调用消费顺序没有核验。
- 未排除依赖库内部时钟、随机读取或阻塞；关键词阴性也不能证明无宏包装、函数指针／虚分派外部实现、汇编／系统调用、其它命名包装函数，或运行确定性／无阻塞。
- 源码中的已有数字、布尔值和种子只作为来源事实；没有设置 H、T_delay、B_CAL、B_max、B*、P_active、density 或 N 等项目／保护参数。


## 10. 既有缓存比较器原文与行政定位

对象：inc/MAPF-LNS2/inc/SingleAgentSolver.h；blob c22f59ac763c3bc272a82b5c8e9793a91f5da94a；全文 SHA256 见对象表。

先前行政补充实际读取 L35–100。两处 rand() 是未被注释的比较器 operator() 分支：
- L51：compare_node；在 reached_goal_at、g_val+h_val、h_val 均相等时返回随机布尔值。
- L93：secondary_compare_node；还要求 num_of_conflicts 相等，再在上述相等条件下返回随机布尔值。
- L72 属于被注释的旧比较器。

以下直接由同一已有缓存的原文行组成，不重新联网，也不以手工转录替代缓存源。行号前缀不是源文件内容：

```text
35:     //         }
36: 	// 		return n1->g_val + n1->h_val >= n2->g_val + n2->h_val;
37: 	// 	}
38: 	// };  // used by OPEN (heap) to compare nodes (top of the heap has min f-val, and then highest g-val)
39: 
40: 	// the following is used to comapre nodes in the OPEN list
41: 	struct compare_node
42: 	{
43: 		bool operator()(const LLNode* n1, const LLNode* n2) const
44: 		{
45: 			if (n1->reached_goal_at == n2->reached_goal_at)
46: 			{
47: 				if (n1->g_val + n1->h_val == n2->g_val + n2->h_val)
48: 				{
49: 					if (n1->h_val == n2->h_val)
50: 					{
51: 						return rand() % 2 == 0;   // break ties randomly
52: 					}
53: 					return n1->h_val >= n2->h_val;  // break ties towards smaller h_vals (closer to goal location)
54: 				}
55: 				return n1->g_val + n1->h_val >= n2->g_val + n2->h_val;
56: 			}
57: 			return n1->reached_goal_at >= n2->reached_goal_at;
58: 		}
59: 	};  // used by OPEN (heap) to compare nodes (top of the heap has min f-val, and then highest g-val)
60: 
61: 		// the following is used to compare nodes in the FOCAL list
62: 	// struct secondary_compare_node
63: 	// {
64: 	// 	bool operator()(const LLNode* n1, const LLNode* n2) const // returns true if n1 > n2
65: 	// 	{
66: 	// 		if (n1->num_of_conflicts == n2->num_of_conflicts)
67: 	// 		{
68:     //             if (n1->g_val + n1->h_val == n2->g_val + n2->h_val)
69:     //             {
70:     //                 if (n1->h_val == n2->h_val)
71:     //                 {
72:     //                     return rand() % 2 == 0;   // break ties randomly
73:     //                 }
74:     //                 return n1->h_val >= n2->h_val;  // break ties towards smaller h_vals (closer to goal location)
75:     //             }
76:     //             return n1->g_val+n1->h_val >= n2->g_val+n2->h_val;  // break ties towards smaller f_vals (prefer shorter solutions)
77: 	// 		}
78: 	// 		return n1->num_of_conflicts >= n2->num_of_conflicts;  // n1 > n2 if it has more conflicts
79: 	// 	}
80: 	// };  // used by FOCAL (heap) to compare nodes (top of the heap has min number-of-conflicts)
81: 	struct secondary_compare_node
82: 	{
83: 		bool operator()(const LLNode* n1, const LLNode* n2) const // returns true if n1 > n2
84: 		{
85: 			if (n1->num_of_conflicts == n2->num_of_conflicts)
86: 			{
87:                 if (n1->reached_goal_at == n2->reached_goal_at)
88: 				{
89: 					if (n1->g_val + n1->h_val == n2->g_val + n2->h_val)
90: 					{
91: 						if (n1->h_val == n2->h_val)
92: 						{
93: 							return rand() % 2 == 0;   // break ties randomly
94: 						}
95: 						return n1->h_val >= n2->h_val;  // break ties towards smaller h_vals (closer to goal location)
96: 					}
97: 					return n1->g_val + n1->h_val >= n2->g_val + n2->h_val;
98: 				}
99: 				return n1->reached_goal_at >= n2->reached_goal_at;
100: 			}
```

源摘录行政更正：此前助手手工展示的 L78 注释末尾曾写成 `if n1 has more conflicts`；同一 blob 的缓存原文是 `if it has more conflicts`。本件按缓存原文归档。该注释勘误不改变 L51、93 两处 rand() 的源码位置。

这只确认有效源码分支位置，不宣称这些分支已经在某次运行触发。

## 11. 既有 CPU 日志窗口缓存

对象：src/MAPF-LNS2/src/mcp.cpp；blob ec7c149fa01206752ae1eeebff64f699facc2bb2；全文 SHA256 c228082f5d0ae6001366022baace45e4a8c3b4563fe60cb06a3ab8d59bfa3aaf。

先前本代理清单阶段显示过 L1–72 及 L126–143；下列是已存在缓存中 L14–72 的归档摘录。根后来另称已亲见相同窗口，此归档不把该根告知表述为本次新验证。

```text
14:         if (paths[i]->size()==0){
15:             continue;
16:         }
17:         unfinished_agents.push_back(i);
18:         path_copy[i].reserve(paths[i]->size() * 2);
19:         assert(copy_agent_time[i] > 0);
20:         
21:         path_copy[i].push_back(paths[i]->at(no_wait_time[i][copy_agent_time[i] - 1]));
22:         
23:     }
24:     cout<<"Start "<<(float)clock()/(float)CLOCKS_PER_SEC<<endl;
25: 
26:     for (int t = 0; !unfinished_agents.empty(); t++) {
27:         // cout<<"Similate t = "<<t<<endl;
28:         auto old_size = unfinished_agents.size();
29: 
30: 
31:         std::vector<int> before = copy_agent_time;
32:         for (auto p = unfinished_agents.begin(); p != unfinished_agents.end();) {
33:             int i = *p;
34:             moveAgent(path_copy, paths, p, t);
35:         }
36:         // cout<<endl;
37: 
38:         // cout<<"unfinished: "<< unfinished_agents.size() <<endl;
39: 
40:         if (t <= window_size) // no need to check if all agents stops in window, as collision not allowed.
41:             continue;
42: 
43:         bool no_move = true;
44: 
45:         for (auto p = unfinished_agents.begin(); p != unfinished_agents.end();p++) {
46:             if (copy_agent_time[*p] != before[*p]){
47:                 no_move = false;
48:                 break;
49:             }
50:         } 
51:         if (no_move && !unfinished_agents.empty()){
52:             cout<<"Error: No agent moves at "<<t<<endl;
53:             print_mcp_detail(paths);
54: 
55:             _exit(1);
56:         }       
57: 
58:         
59:     }
60: 
61:     for (int i=0;i<paths.size();i++){
62:         *(paths[i]) = path_copy[i];
63:     }
64: 
65:     cout<<"Simulation done at "<<(float)clock()/(float)CLOCKS_PER_SEC << endl;
66:     // cout <<" pairs:"<<count_pairs(path_copy)<<endl;
67: 
68: 
69:     return;
70: }
71: 
72: bool MCP::moveAgent(vector<Path>& paths_copy, vector<Path*>& paths, list<int>::iterator& p, int t)
```

## 12. 归档边界

本件不是新一轮检索或实验。NO-SKILL / NONBALLOT 保持；没有修改 72 正文、冻结文档或 Git，没有实施／构建／测试／运行／仿真源码，没有读受限数据载荷，也没有对保护参数赋值。新工件的实际文件 SHA256、bytes、lines 由完成回执提供。

