# 共同初解适配后的 ADDRESS 推荐配置

状态：**实现、编译及软件核验完成；新授权功能批次已有2项成功、1项失败，余3项停批未运行。公平方法比较尚未成立。** 见[本批结果](ADDRESS_DEV_RESULT.md)。
旧 `repair_residual_v1` 的六次许可已经消费。本页及配置文件均不能授权新运行。

## 对照的身份和保留语义

固定作者提交 `b3d35c431ce03834f95e834d87986f2f341394a1`。
作者 README 推荐的是 `RandomWalk + bernoulie + top-K` 的单破坏器 ADDRESS，
不是固定 ID 分组，也不要求启用另外的 ALNS 多破坏器或区域分支。

本适配保留作者的 top-K 延迟机器人集合、Beta/Bernoulli 抽样、随机游走构组、
以8为上限的邻域、PP/SIPP重规划、完整回滚与尝试级奖励代码。`runPP()` 整段和
`BasicLNS.cpp` 字节保持一致，软件检查核对这一点。

**奖励仍在最终接受/回滚之前更新。** 原实现可能根据尚未完整规划的邻域累计
代价更新种子奖励，随后才回滚。本适配没有把它偷偷改成“完整接纳收益”，
也不将这种语义当作已修复问题。后续若提出纠正版本，必须另列方法并保留此对照。

初始邻域大小仍为作者构造器固定的8；原代码里邻域大小自适应赋值为注释，
不声称启用了不存在的自适应大小功能。当前拒绝 `n<8`、`top-K>n`、
非正迭代数，以及CBS、PIBT、其他破坏器、区域选择等未核配置。

## 实现改变

1. `build_address_full.py --adapter` 在新的构建目录中从核定作者文件生成
   小型源码 overlay，保留完整许可。作者缓存、原完整二进制与旧SIPP桥均不修改。
2. `address_adapter.py` 精确核对源代码锚点；导入共同的完整初解，填充全部
   `agents.path`、`path_table`、`neighbor`及初始SOC，不重新求一套更有利的初解。
   原 `Instance` 读取失败时会随机生成agent文件的分支在overlay中改为失败退出。
3. `address_adapter_support.h` 核对端点、障碍、四邻接/等待、顶点、对向边和
   永久终点驻留；全体初解合法后才能安装。最终输出再次独立检查全体路径、
   SOC一致性和不劣化，不能逐车回滚拼接。
4. `rand`、LNS各采样函数新建的MT种子和基类MT由显式种子控制。每次采样器
   仍新建引擎，种子改由任务种子流给出；这是公开声明的可复现性适配。
   不保证跨编译器/标准库相同采样序列，也未实跑声称完整搜索可重复。
5. `run_address_adapter.py` 复用 `run_repair_dev.supervise` 与 `GridProblem`，
   不另写一套调度器或Python路径合法性定义。它导出同一初解、执行作者推荐
   配置、解析作者输出、完成外部全车末检，并保留所有输出/失败。

## 预算与失败

`total_wall_s`是成功结果的总时间准入预算，不保证整条命令在该秒数退出。
它从监督脚本入口开始，包含模块导入、清单/输入哈希、宿主初解检查、
输入格式转换、工作进程与原生启动、作者构造/启发式预处理、初解安装、搜索、
原生末检/路径输出、外部输出解析与末检、结果写入、产物哈希。

原生 `cutoffTime` 使用剩余总预算，另留显式内层末检与外部末检余量；
原作者单次修复预算仍取剩余搜索预算的1/100。监督器给整组剩余wall上限，
worker和native分别限制CPU、地址空间、文件大小，禁用core文件。
原生单次SIPP若不响应软时钟，外部整组期限仍会终止它。

父进程输入读取与产物哈希只有完成后的deadline拒绝，没有抢占式硬wall。
后继清单须在外层另加 `timeout --signal=TERM --kill-after=2s 20s`，
与15秒成功准入预算区分：20秒触发命令终止、再给2秒强制回收保护。
这不改变任何超15秒结果不得记为成功的要求，也不能将22秒写成科学比较预算。

科学结果写入及外部完整验证必须在预算内，否则该臂失败。最后的管理收据
写入/进程退出不计入上述结果完成时刻，明确单列；不能把这个排除项隐藏成
“全部程序退出耗时”。耗时包含关系明确记录，不把native时间再加到其父时间。

输出目录在启动前独占创建，创建后即消费一次尝试；拒绝重用，零重试。
失败、超时、丢失输出、末检不通过或超预算均留存；初始方案和输入始终保留，
失败不冒充完整成功或改善。批次上层须采用任一失败立即停，不自动接续其它臂。

## 已完成的验证与产物

- `test_address_adapter.py`：7项软件检查通过。包括原奖励/回滚段保持一致、
  精确锚点拒绝漂移、C++无求解器几何与种子契约、假进程成功/末检及失败保留。
  另外覆盖overlay生成失败仍保留FAILED收据，以及运行入口拒绝错配或失败的
  编译收据。假进程只写固定字节，没有创建作者 `Instance` 或执行SIPP。
- [adapter_build_receipt.json](adapter_build_receipt.json)：全部作者源文件身份、
  overlay摘要、工具链、编译日志摘要、`--help`记录。`--help`在Instance构造前返回。
  编译后仅补修构建失败记录和运行收据身份绑定；未改变C++ overlay或重编译。
  收据保留当时生成器SHA，不改写为补修后的脚本SHA。
- 本地二进制 `.address_adapter_build/build/address`，SHA256
  `e14f8805270ac7a09ea748413274e8d1c6c163f79e806050691878bf20b7d11a`。
- 两份maze任务已完成真实导入/搜索/末检闭环；random16失败且停止全批。仍未完成全部任务闭环、跨方法公平配对、运行可重复性与性能结论。
  作者奖励语义被保留，不等于已经证明它合理。

## 已消费的清单接口（SHA冻结、本批关闭）

具体六项输入、代码SHA、命令、预算和停止条件固定在[ADDRESS_RUN_CHECKLIST.md](ADDRESS_RUN_CHECKLIST.md)。本批已按真实授权执行并因第3项失败关闭。下列接口作为历史说明保留，不授权继续剩余项目或重试。

沿用现有 `repair_residual_v1_inputs.json`，输入SHA
`be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b`；
不生成新任务或初解。新清单使用 `address_common_initial_dev_v1`，声明
`authorization: PENDING_USER`、唯一batch/job、`retry: 0`，固定每任务的case、seed、
iterations、top_k、二进制SHA，以及下述运行文件SHA：
`run_address_adapter.py`、`run_repair_dev.py`、`address_backend.py`、`pp_repair.py`、
`adapter_build_receipt.json`。这些实现已冻结到清单；文件身份核验不授予科学运行许可。

已准备的功能DEV限额为每臂总wall15秒、worker/native分别CPU10秒、各AS512MiB，
内层末检预留0.25秒、外部末检预留0.5秒、16次成功构组修复迭代、零重试。
迭代数约束不能被当成固定时间或相同计算量；正式比较仍按总预算配对。
六个case已由统一清单一次性冻结，保留零余量任务作为无改善检查，不能挑成功臂
宣称性能。原SIPP桥128次固定请求的结果并非本方法的公平配对数据。

```bash
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect \
  --manifest tracks/sci/config/address_common_initial_v1_manifest.json \
  --sha256 5f89443a8ad7e9281fffa74e8c9b47b1edf79c2a41203068057840046183bb3d
# 仅真实用户批准上述新清单后，才能把inspect改成run，并指定：
# --job <frozen_job> --authorization-reference '<实际用户授权原文及范围>'
```

下一项任务是修补共同终止条件，按新版本与新授权完成剩余功能核验，再让候选方法使用
相同宿主优化、反馈和末检。当前工程适配本身不是论文方法增量。
