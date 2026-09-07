# 原生 headless 命令来源合同：实际完整回执归档

- 工件性质：**NO-SKILL / NONBALLOT**；仅归档实际交付内容，不是正式审查，没有通过票。
- 本任务真实路径：`/root/construct72_native_command_contract`。
- TIP 子任务真实路径：`/root/construct72_native_command_contract/tip_entry_sources`。
- 本任务亲见边界：已读取指定 72E1 收据的 L1–240，以及候选 72 第 8–10 节（L128–205）；为定位章节曾仅显示该候选的标题行。已从固定 raw URL 完整获取 R0 的 CMakeLists.txt、README.md、src/driver.cpp 及 TIP 顶层 CMakeLists.txt；R0 与 TIP 顶层 CMake 已全文显示核读，R0 README 人工阅读限标题及 L19–49，R0 driver 人工阅读包含 L17–172 连续正文及此前显示的头部 include／预处理行。完整获取不等于未显示部分已做全文语义审计。
- TIP 子代理来源边界：小写 readme.md、app.cpp 及 time_independent/CMakeLists.txt 的来源阅读由上述有界子代理实际完成，其证据范围依附录原文；本任务未将这些源重新独立获取／全文核读。正文相关结论据实际收到的子代理回执合并。附录中的“上层已核根 CMake”指本任务已核 TIP 仓库顶层 CMake，不指根代理已重新独立读取。
- 根代理阅读状态按根告知记录：根本次两个 raw CMake 的 web 请求均 Cache miss；随后 gh 管道发生沙箱网络失败，末段退出状态不能作为获取成功证据，升级请求被用户中断。因此不能表述为根已独立新读这两个 CMake。本条不是本任务重新验证根的工具记录。
- 归档状态：**所有模板 NOT_IMPLEMENTED / NOT_RUN**。模板不是执行授权；未绑定项不得省略以承接运行默认。未构建、编写／运行测试、仿真、调参、生成种子／载荷／结果，也未绑定任何保护参数。
- 本次归档未重新检索官方来源或修改候选；写入前已确认目标路径不存在。下文完整保留上次本任务最终正文及 TIP 子任务实际最终原文，不补写保护参数默认数值或范围。
- 本文件 SHA256、bytes、lines 在归档完成回执中另行报告，避免文件自引用摘要。

## A. 本任务上次实际最终正文（完整原文）

**NONBALLOT / NO-SKILL。可补入 ORIGINAL-CHECK 的来源合同，但状态仍为 NOT_IMPLEMENTED / NOT_RUN。** 以下均为不可执行的占位模板；未绑定项不能省略并承接运行默认值。

R0 固定提交的 [README L26–38](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/README.md#L26) 明示 CMake→Make 与 `lifelong --inputFile … -o …`；[CMake L63–72](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/CMakeLists.txt#L63) 的非 Python 分支实际建立 `lifelong`。可将官方步骤写成路径显式模板：

```text
rtk proxy cmake -S <UNBOUND_R0_FIXED_SOURCE> -B <UNBOUND_R0_BUILD> -DPYTHON=OFF -DCMAKE_BUILD_TYPE=Release
rtk proxy cmake --build <UNBOUND_R0_BUILD> --target lifelong
```

未来真正实例入口应保留运行字段未绑定，不能直接采用 README 省略这些字段的最简示例：

```text
rtk proxy <UNBOUND_R0_BUILD>/lifelong
  --inputFile <UNBOUND_R0_INPUT>
  --output <UNBOUND_R0_OUTPUT>
  --outputSimple <UNBOUND_OUTPUT_MODE>
  --fileStoragePath <UNBOUND_STORAGE_PATH>
  --logFile <UNBOUND_LOG_PATH>
  --simulationTime <UNBOUND_SIMULATION_TIME>
  --planTimeLimit <UNBOUND_PLAN_TIME_LIMIT>
  --initTimeLimit <UNBOUND_INIT_TIME_LIMIT>
  --preprocessTimeLimit <UNBOUND_PREPROCESS_TIME_LIMIT>
  --commitStep <UNBOUND_COMMIT_STEP>
  --mapfPlanner <UNBOUND_PLANNER_SELECTION>
  --delayPolicy <UNBOUND_DELAY_POLICY>
  --delaySimulateAll <UNBOUND_DELAY_SIMULATION_MODE>
```

选项名及类型依据 [driver.cpp L40–55](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp#L40)。入口会从输入进一步读取地图、agent、任务和 delay 引用，最终调用 `simulate`；因此输入文件及其全部引用均须保持未绑定、未读取。[driver.cpp L86–162](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp#L86)

两个合同细节：

- `commitStep` 还影响任务揭示深度；所读 `main` 虽声明 `initTimeLimit`，未见向系统下传该值，不能据选项名称宣称初始化受其约束。[driver.cpp L106–158](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp#L106)
- `--help` 的源码路径在 `clock()` 语句之后、输入通知及载荷读取之前返回非零。它属于入口检查，不能用“非零即实例失败”或“帮助成功即原法复现成功”判定。[driver.cpp L59–68](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp#L59)

TIP 固定提交的说明文件实际为小写 [readme.md L25–33](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/readme.md#L25)，原文构建为 `cmake ..`、`make`；[根 CMake](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/CMakeLists.txt#L1) 建立 `app` 并链接 `lib-time-ind`：

```text
rtk proxy cmake -S <UNBOUND_TIP_FIXED_SOURCE> -B <UNBOUND_TIP_BUILD>
rtk proxy cmake --build <UNBOUND_TIP_BUILD> --target app

rtk proxy <UNBOUND_TIP_BUILD>/app
  -i <UNBOUND_TIP_INSTANCE>
  -o <UNBOUND_TIP_OUTPUT>
  -s MCP
```

`-s` 是 solver 选择；MCP 是源码列出的名称。实例及其内部运行字段、地图和计划引用全部未绑定；不能让未核字段落入内部默认。[app.cpp L50–72、L304 起](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/app.cpp#L50) 编译时 `_PLANDIR_` 参与计划路径拼接，实际入口随后调用 `P->run()` 并写日志，属于真正实例运行。[app.cpp L175 起](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/app.cpp#L175)、[L255 起](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/app.cpp#L255)

仍未核的依赖和边界：

- R0 要求 CMake、C++14 及 Boost 的 `program_options/system/filesystem/log/log_setup`；本地版本、链接与传递依赖均未验证。[R0 CMake L3–33](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/CMakeLists.txt#L3)
- TIP 要求 C++17；库公开使用 `-O3 -Wall -mtune=native -march=native`，机器与编译器必须纳入未来 profile。已核构建层没有可视化器依赖，但未审完整传递依赖。[TIP 子目录 CMake](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/time_independent/CMakeLists.txt#L1)
- TIP README 示例目录拼写与入口缺参示例不同；任何样例路径、输入完整性、默认覆盖及合法计划域仍待后续独立核验。
- 源码定位、配置/编译检查、入口帮助检查和真正实例运行必须分别记账；目前没有任何构建成功、输出合法或真实完成证据。

本任务及有界 TIP 子任务均未写文件、构建、测试、仿真或读取载荷，也未绑定保护参数。

## B. TIP 子任务实际最终原文（完整附录）

已核定固定提交 `755a7ce740d49543b1165403371752c08e342ca4` 的入口与构建关系；找到的说明文件是小写 **`readme.md`**。

| 来源与行号 | 短原文／证据 | 结论 |
|---|---|---|
| [readme.md L25–33](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/readme.md#L25) | `cmake ..`、`make` | 官方模拟器采用独立 build 目录中的 CMake→Make 构建流程。 |
| [readme.md L7–8](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/readme.md#L7) | `C++(17)`、`openFrameworks` | README 标明 C++17；openFrameworks 被归于可视化器。 |
| [readme.md L96–113](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/readme.md#L96) | 可视化器另有 Building、Usage 段落 | 可视化器另行构建，读取结果文件；官方说明支持把模拟器作为 headless 候选入口。 |
| [app.cpp L40、L50–72](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/app.cpp#L40) | `main`、`instance`、`output`、`solver` | 真正程序入口是 main；`-i` 绑定实例文件路径，`-o` 绑定输出文件路径，`-s` 绑定求解器名称。**`-s` 不是种子选项。** |
| [app.cpp L208–211](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/app.cpp#L208) | `std::ifstream file(param_file);` | `readParam` 在这里打开参数文件；未在交付证据中核定 main 调用该函数的具体行号。 |
| [app.cpp L115–143](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/app.cpp#L115) | `readMAPFPlan`、`MCP(path)` | 先由字段名建立 Grid，再在存在计划字段时读取计划。MCP 分支检查路径非空，随后构造 MCP。 |
| [app.cpp L255–258](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/app.cpp#L255) | `std::ifstream file(_PLANDIR_ + plan_file);` | 计划文件通过编译时 `_PLANDIR_` 与计划字段拼接后打开。没有读取任何计划载荷。 |
| [app.cpp L175–176、L191–195](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/app.cpp#L175) | `P->run();`、`log.open(output_file, std::ios::out);` | L176 是入口中明确的仿真调用边界；之后会打开并写入输出文件。因此实际入口执行具有仿真和文件写入副作用。 |
| [app.cpp L304–311](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/app.cpp#L304) | 帮助列出求解器和日志选项 | 求解器名称包括 GREEDY、CAUSAL_PIBT、CAUSAL_PIBT_MAPF、FSP、MCP；另有 `-l/--log-simple`、`-v/--verbose`、`-h/--help`。 |

[time_independent/CMakeLists.txt](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/time_independent/CMakeLists.txt#L1) 的依赖证据：

- L1：CMake 最低版本为 3.1。
- L3–15：建立静态库 `lib-time-ind`，列入 graph、agent、greedy、causal_pibt、causal_pibt_mapf、fsp、mcp、problem、mapf_random、mapf_dp、stn 的 `.cpp`。
- L16：定义 `_MAPDIR_`，指向源码树中的 map 目录。
- L17：公开编译选项包含 `-O3 -Wall -mtune=native -march=native`。
- L18–19：要求 `cxx_std_17`，公开 `./include` 作为接口包含目录。
- 结合上层已核根 CMake，`app` 链接该静态库；这两个已核 CMake 文件未显示可视化器或 openFrameworks 构建依赖。

以下仅为**不可执行、未绑定的契约模板**：

```text
BUILD_CONTRACT
  source_directory: <UNBOUND_FIXED_COMMIT_SOURCE>
  build_directory: <UNBOUND_BUILD_DIRECTORY>
  configure_working_directory: <UNBOUND_BUILD_DIRECTORY>
  configure_program: cmake
  configure_arguments: [<UNBOUND_FIXED_COMMIT_SOURCE>]
  build_program: make
  expected_target: app
  execution_authorized_by_this_template: false

MCP_ENTRY_CONTRACT
  working_directory: <UNBOUND_WORKING_DIRECTORY>
  executable: <UNBOUND_BUILT_APP>
  arguments:
    -i: <UNBOUND_INSTANCE_PATH>
    -o: <UNBOUND_OUTPUT_PATH>
    -s: MCP
  instance_and_referenced_assets: <UNBOUND_AND_UNREAD>
  execution_authorized_by_this_template: false
```

尚未核实：

- 本地编译器、CMake、Make、平台及上述原生架构编译选项的兼容性；没有构建或运行证据。
- 所列库源码与头文件的传递依赖，以及库内部是否还引入 GUI 或其他外部库；因此 headless 判断属于已核构建与入口层面的结论。
- 输入字段是否完整覆盖内部默认值，以及实例、地图、计划之间的语义与路径有效性。
- README L39 的示例目录为复数 `instances`，app.cpp L91 的缺参示例为单数 `instance`；示例存在目录拼写差异，不能据此绑定实际输入路径。
- 已发现默认初始化段，但不复述、不采用其中运行数值，不据此填充任何保护参数。

本子任务仅进行了指定来源的只读获取；没有写文件、构建、测试、仿真或读取实例／地图／计划载荷。

## C. 归档边界声明

A、B 中“未写文件”等语句描述各自原来源任务交付时的状态，作为历史原文完整保留。本次另经根明确指令，仅创建本 Markdown 归档；不将归档动作计为实现、构建或运行。根将独立筛选，本件不构成正式审查或通过票。
