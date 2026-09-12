# 73L21：固定源的任务、delay消费与生成器格式下一跳

2026-09-11；`/root/successor_identity_audit`。NO-SKILL / CONSTRUCTIVE SOURCE EVIDENCE / NONBALLOT。继L20后的新有界任务，只写本件；不作正式审查或资格投票。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 结论与当前73的关系

固定R0的三类任务分配含义已经可以从构造、补给、完成与同步函数接起来。当前73 §8确实分别保留greedy、Fixed、Inf补给，并用共同TASK世界和PROJECT替换原同步；**原greedy/Fixed的空sync不能据此推断当前适配失败**。需要保留的是选择器实际strategy、初态、队列/计数器和reveal语义的绑定，而不是把三个名字当同一任务流。

LoRR 2024的随机生成分支已证能调用具名ProblemGenerator，但其多errand任务格式及生成JSON并非R0直接兼容输入。没有取得任何输出文件到R0实际blob的绑定；可以生成不等于曾生成。

新增待核接缝是delay：原软件按agent/离散状态时标取矩阵列，当前73按公共行/请求语义id给指定ACTUATOR尝试NO_START，同时仍将delay_blob计入source_id。所读窗口尚未给出两种索引之间的完整变换；需根核其它已登记合同，不能让没有实际作用的blob暗中产生不同来源权重。

## 2. 固定身份、完整阅读与未读域

R0为`YueZhang-studyuse/LMAPF-delay@0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`；归档为`MAPF-Competition/Benchmark-Archive@25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a`。下表均经固定contents API取得raw源码全文，exit0，无执行源码。Git blob/bytes承接L20期间取到的固定树元数据8cd3b2与30e016；行数是实际返回的逻辑行，不充作LF。

| 对象 | Git blob / bytes | 本题回执／全文逻辑行 |
|---|---|---|
| R0 src/CompetitionSystem.cpp | 4e9a86921fda3fd15bd616c3c0dff461688254ed /27752 | 8ad40e /885 |
| R0 inc/CompetitionSystem.h | 6daf0b9e3fa1015e49893b09be87940577427189 /6753 | 9de6b9 /243 |
| R0 inc/Tasks.h | 3ec938bac683bac1494dac24f308dd83440a826b /436 | bcf378，全文 |
| R0 src/DelaySimulation.cpp | 1e1953d9fa9ccb1eb96ae5d7b8829f425679d113 /14733 | 613466 /455 |
| R0 src/PIBTDelaySimulation.cpp | ca57387c1d93d3d773743adb7cbb67747ca68e9f /9373 | c4828d /261 |
| R0 src/PIBTDDelaySimulation.cpp | 04baee3292b45f6a47fdf170d3e874b7fdb849f9 /6935 | 0d755c /206 |
| 归档2024生成器 script/benchmark_generator.py | 0aaf04d7cad4bf9405d81077f41dcbeacb996a8c /9500 | 50cf6f /238 |
| 同目录 problem_generator.py | 86652033f57ebf0186ee9566408ba85057780266 /9899 | e03b48 /265 |
| 同目录 util.py | d2a3cca8310f0383e2bd8da181414b4057fcec28 /3044 | f61739 /95 |

为核编码与通行解释，只沿ProblemGenerator的实际导入额外读取util；其中原有常量/字典不移作研究参数。benchmark和problem的全部方法、入口均已读；随机路径的generate_problem、generate_agents、generate_total_tasks、generate_txt、find_lcc及其调用次序已核。warehouse分支委托的WarehouseTaskGenerator本体未读，不把随机分支结论泛化为其全部输出。

R0完整相关函数包括三类构造/update_tasks/sync_shared_env，BaseSystem的initialize、simulate、move、execution_simulate、set_delay，以及MCP的build/simulate/moveAgent、PIBT/PIBTD的init/simulate/funcPIBT/delayAgents；备用Fixed文件构造/load_agent_tasks也读了，但原driver的roundrobin_fixed用的是向量构造。driver/common.h/Grid解释器承接本代理L20全文核验。本题没有扩读ActionModel、全部planner/库/线程实现或证明整个可达继续域。

另读73 L218–234全文（89a646），对delay/source_id作定向定位（a01b94），不宣称这次全文重读73。7cb705复核73仍`9e06199cc6045ddd750b861b3091ec239c7c6ff2ae7eeaebbdd0e7fde61ec113` /216498 bytes/665 LF；L20仍`ee83a72a85ac6018a8525626b2e751e0fdad8966d306a4968976ad0a5bfde136` /10541/74。

## 3. 三种任务语义与共享适配

依据固定[CompetitionSystem.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/CompetitionSystem.cpp)、[头文件](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/CompetitionSystem.h)及L20的driver。

| 原strategy | 原实际消费含义 | 与当前73的精确区分 |
|---|---|---|
| greedy | TaskAssignSystem构造全局有限FIFO；update_tasks按agent下标依次填至reveal深度或队列空，真实分配时写agent与t_assigned | 73 L218/220保这种补给顺序；服务由独立TASK行决定，不能直接称native吞吐或派单时刻等价 |
| roundrobin_fixed | driver先把全局输入按原位置模agent数分到各agent；Fixed构造每agent有限队列，按各自顺序补给、不循环 | 73保各自原序列；任务耗尽不是非法输入或可删失败。原数字task_id的构造次序不替代完整实例身份 |
| roundrobin | Inf保输入向量引用，按`tasks[(counter_i*num_agents+i) mod tasks_size]`循环发出新任务实例 | 73明确同序列/计数器；重复目标可以是新实例，不能去重成一次服务。取模前须有定义域 |

原BaseSystem::move每个离散步最多弹一个相符队首，随后simulate统一调用update_tasks。Inf::sync_shared_env还会依据curr_commits虚拟弹队首并产生预测补给；greedy/Fixed的sync在头文件L174/L206为空。当前73 L228禁止PROJECT虚拟抢未分配任务，L230冻结SharedEnv，已经显式更换这条预测入口，不能继承native同步等价。原driver的reveal深度来自commit_window的既定关系，不能被LoRR JSON同名意义近似的numTasksReveal悄悄替换。

静态谓词可从L20延伸为：构造前位置索引有效、输入计数与容器表示可兼容、合法strategy被完整绑定；Inf凡执行取模须tasks_size非零，乘积/计数/task_id须有表示合同；每个front/按路径下标访问须在其实际前置条件下定义。后两者包含动态继续域，不能简单删掉“后来队列空/可能停滞”的来源来过门。当前PROJECT的空目标NO_INPUT/HOLD是明示适配，不能混成原Inf::sync_shared_env已安全处理所有空队列。

## 4. LoRR格式的具体兼容边界

[benchmark_generator.py](https://github.com/MAPF-Competition/Benchmark-Archive/blob/25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a/2024%20Competition/Problem%20Generator/script/benchmark_generator.py)的随机分支构造ProblemGenerator并调用generate_problem；任务首次生成后供同批后续team复用。以下仅根据已读[problem_generator.py](https://github.com/MAPF-Competition/Benchmark-Archive/blob/25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a/2024%20Competition/Problem%20Generator/script/problem_generator.py)与[util.py](https://github.com/MAPF-Competition/Benchmark-Archive/blob/25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a/2024%20Competition/Problem%20Generator/script/util.py)作静态推导，未生成实例。

| 输出层 | 已证格式关系 |
|---|---|
| agents | 注释、数量、逐行一个十进制位置；encode_loc为row×width+col，与R0行主序编码形式一致。实际同图、数量、位置、几何合法性及对象身份仍未检查 |
| tasks | 数量之后每行一个任务的若干位置，以逗号相连。R0只读首token；多errand会丢后续任务内容，不是保持原任务语义的直接兼容。每行恰单一位置时只有表示层兼容的条件结论，不证明存在某个合格R0输出对象 |
| problem JSON | 生成器写mapFile、agentFile、teamSize、taskFile、numTasksReveal、version；不写原R0必需的taskAssignmentStrategy、delayFile。原样交给固定driver缺字段，不能以共同几个字段宣称整套可用 |
| map/抽样域 | util只把`.`/`S`/`E`视为通行，R0将非`@`/`T`均视为通行；相等须另证符号域。生成器find_lcc只改内存抽样域，未因此改写已复制地图正文 |

生成器在find_lcc前检查team_size对全图自由格数的关系，generate_agents随后在修改后的抽样域反复拒绝采样；因此其前置检查本身不保证后续生成终止。这个源码事实不准用来筛实际研究成功样本，也不证明某个现有配置有问题。源随机状态、原始输入、生成记录、转换和适用许可均未与R0的agent/task_blob绑定；两文件没有提供这种逐对象证书。

## 5. delay的真实消费、静态边界及来源下一跳

L20的read_int_delay先得到agent为行的bool矩阵。BaseSystem::execution_simulate L146完整表明：取`current_time=curr_states[0].timestep`，对整个commit_window读取`simulation_delay[agent][current_time+offset]`，转置为局部`delay[offset][agent]`，再交给三种执行策略。最终评价窗口即将结束也不能从这个函数本身推出只读剩余列；其取列先覆盖完整原commit窗口。[固定消费者](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/CompetitionSystem.cpp#L146)。

MCP的moveAgent以delay阻止拟移动并保留位置；PIBT/PIBTD先决定下一点，再由delayAgents将直接受阻与依赖占位的其它agent等待传播。三个simulate在局部delay行之外采用无额外delay的后续预测；这不保护前一步对原simulation_delay的越界读取，也不等于原始未知尾部可填零。[MCP](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/DelaySimulation.cpp#L8)、[PIBT](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/PIBTDelaySimulation.cpp)、[PIBTD](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/PIBTDDelaySimulation.cpp)。

这些是原native离散执行逻辑；73已更换物理/控制/TASK世界，不能直接把原delay策略当当前安全控制器。后继需明确：delay_blob如何参与新profile；旧agent/列如何对应新公共时刻或ACTUATOR尝试；越出已定义支持集时是哪种静态不适用/未知状态；同语义alias和权重如何处理。若某blob只留作出处而不影响任何评价机制，不能未经说明将其作为独立语义来源重复加权。当前未作这种映射选择。

仅作一次具名历史下一跳：288037请求固定R0祖先、`path=lifelong_benchmark/delay`、每页上限10的commit消息，实际返回7项；未请求任何patch/载荷或下一页。消息含`a3c9e01cbae08b59777a2f6670e7e6e355bd10f0`的“delay benchmark update”，其余为generic new/formatting/refactor benchmarks。它给出一个可引用历史节点，不含生成器、随机机制或逐对象出处；不从提交标题推出素材原创/许可，也不声称完整历史已穷尽。[具名节点](https://github.com/YueZhang-studyuse/LMAPF-delay/commit/a3c9e01cbae08b59777a2f6670e7e6e355bd10f0)。因此delay生成链仍未知，本题到此停止，不重做L20超时的跨树比对、不泛搜。

## 6. 交付边界

本件把“能读入”扩展为具体构造/消费/接口义务；仍没有任何实际完整source_id、合法roster成员或非空profile证明，未实例化不等于空域已证。所有来源资格与完整运行域保持未闭，不能靠排除动态失败来修复。ef59a0与落盘前7cb705均确认输出不存在且非链接；仅apply_patch建立本件，无Claude、skill或活句柄。未读Input_Output_Format正文、35–38/Q资料、任何数据/config/地图图像或结果载荷，未执行生成器、构建测试、仿真、赋保护参数、生成source_id/O/seed/配置/实验结果；旧报告、主稿、行政/Git及桌面未改。
