# 72L2 — 固定 R0 数据集元数据、许可与解析字段有界来源回执

日期：2026-09-07。执行代理：`/root/source72_dataset_metadata_license`。

性质：**BOUNDED SOURCE RECEIPT / NONBALLOT / NO-SKILL**。本文件不是正式逻辑审查、不是后继候选、不是资格 PASS，也不替代原 69L1/E1 的旧缺失回执。固定 72 及 69–72、旧报告均未修改。

## 1. 实际边界与结论

本次只核固定官方 Git 元数据、README、LICENSE、必要输入格式说明和 parser 源码窗口。没有读取任何 `.map`、`.scen`、配置/任务 JSON、`.agents`、`.tasks` 或 delay `.txt` 载荷正文；没有下载这些载荷到本地，没有生成任何实例、manifest、种子、参数表或实验数据，没有构建、实现、创建或运行测试、仿真、实验。没有读取 35–38、Q-CAL、Q-CONFIRM、results、实验 tapes 或桌面。

唯一当地科学文件为 `/home/lyh/MAPF_PIED_MDDR_RESEARCH/72_PIE_CENTRAL_SPATIAL_RETIREMENT_AND_PAID_OBSERVATION_PREEXPERIMENT_CANDIDATE_20260906.md`。实际读取 L200–241，后为定位 §10 标题又读取 L192–200；其中 L192–196 属于 §9，超出最初指定的 §10–11 语义边界。这一额外窗口已即时报告根代理，未用于本回执结论，未视作受限载荷访问或源码审计结论。根代理随后仅补给官方仓库与根 commit 身份，并允许固定 `Input_Output_Format.md` 的链接/说明必要窗口、排除示例配置/地图/任务正文。

没有使用 skill，没有派子代理，没有读取审查报告文件。为取得缺失仓库身份曾向根代理和已存在的来源代理发送仅索取身份的消息；结论所用身份来自根代理回复。一次 `list_agents` 返回了另一来源代理的完成摘要，本回执不使用该摘要作证据。

简明结果：

- city、game、random、warehouse-s 的固定目录元数据均成功取得且未截断；每类均有非空 JSON blob 元数据以及非空 maps、agents、tasks 子目录。这里只确认元数据可得性和目录项计数，不确认任何配置的静态合法性。
- 固定根 LICENSE 明文为 MIT，版权声明主体为 The League of Robot Runners。所读 README、输入格式必要窗口及已查数据目录元数据没有提供外来地图/场景素材的独立许可或权利链。**MIT 对各地图/场景/任务素材的覆盖未获本次证据建立；素材授权状态 UNKNOWN。**这不是断言这些素材一概被 MIT 排除，也不是断言它们无许可。
- 按 README 的真实链接链只到达 League 官网的 JavaScript 壳及固定输入格式说明；没有定位到官方上游地图数据集说明/许可 URL。因此上游出处、上游素材许可、R0 与上游素材的逐 blob 对应均为 UNKNOWN。没有凭文件名猜定 MovingAI 归属，没有为弥补失败改查次手博客或其它来源。
- 固定 driver、common.h、Grid.cpp 给出了关键字段和基础解析行为的源码证据；未对任何载荷执行这些谓词。目录存在、文件大小为正或 parser 存在都不授予静态合法来源资格。

`H`、`T_delay`、`B_CAL`、`B_max`、`B*`、`P_active`、density `N` 均未赋值、范围或默认。本文出现的文件数、字节数、行号与文件名字符仅为来源元数据，不是上述实验量的绑定。

## 2. 固定官方身份与读取方式

官方仓库：[YueZhang-studyuse/LMAPF-delay](https://github.com/YueZhang-studyuse/LMAPF-delay)。固定 commit：`0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。根 commit API 给出的真实根 tree 为 `85d5dc37b79690724256f7b5c00806bf55a85e37`。

GitHub 使用只读 `github_fetch` 定点 GET；网页使用 `web.run` 定点 open，没有搜索查询。tree GET 不加 `recursive`，每个子目录均先由已知父 tree 定位。非载荷源码/文档对象在工具内存中取得全文，再仅输出指定窗口或定位命中；这是完整对象传输、有限窗口语义阅读，不冒称“服务器只传输了那些行”。所有源码/文档的实际传输 UTF-8 字节数均与 tree `size` 相符，但未独立计算这些对象的 Git blob 哈希或 SHA256。下列 blob 身份来自固定父 tree 元数据。

第一批 tree 的直出过长，展示被截断；随后对保存在工具会话内的完整 API JSON 再作定点统计，所涉每个 API 对象的 `truncated` 都是 false。展示截断与 GitHub tree 截断分开记录；本回执不声称逐字人工审阅了首批被截断的展示。

| 对象/范围 | 精确 GET URL | 结果 |
|---|---|---|
| 固定 commit Git 元数据 | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/commits/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357 | 成功；只用于 commit→根 tree 身份 |
| 初次按 commit ref 的根一级 tree | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357 | 成功；11 项，未截断；不把请求 ref 当真实 tree SHA |
| 真实根一级 tree | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/85d5dc37b79690724256f7b5c00806bf55a85e37 | 成功；11 项，未截断；条目与上行完全相同 |
| lifelong_benchmark 一级 tree | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/22ae3c8b3ad1f4791bd8c15b7d7b5521ed043c17 | 成功；四类别及 delay 共 5 个 tree |
| src 一级 tree | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/0e240728303cc756503163e49814e87c9d591fbe | 成功；14 项，未截断；定位 parser 对象，不进入 MAPF-LNS2 子树 |
| inc 一级 tree | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/c776be05bf0f0ddac8220218659d50db400e9c88 | 成功；16 项，未截断；定位 common.h 等，不进入其它子树 |

## 3. 四类别非空元数据

以下统计来自每类完整非递归 tree 及其三个明确子目录，不读取其 blob 内容。四类一级 JSON 条目的 `type` 均为 blob，`size` 均为正；四个 maps 目录各有一个正大小 `.map` blob。agents/tasks 所列条目均为正大小 blob。所查这些目录元数据未出现 mode `120000` 符号链接，也未出现 README、LICENSE/LICENCE、NOTICE、COPYING、COPYRIGHT 名称的目录项。这个有限范围的“未出现”不等于全仓库无其它许可文本，更不能证明 JSON 内引用均无符号链接或合法。

| 类别 | 类别 tree | 一级总项 / JSON blob 项 | maps / agents / tasks 的 blob 项数 | 元数据状态 |
|---|---|---|---|---|
| city | `3e12a4483e615cd1a261d1e2476a29294fa4d0d1` | 94 / 91 | 1 / 18 / 18 | 成功、非空、未截断 |
| game | `8d8f8fbe8d16d80f5dab7a5cbf5ab6f3a341215a` | 94 / 91 | 1 / 10 / 10 | 成功、非空、未截断 |
| random | `2264326dfda14559e0db92e1649aaf512f9ff98f` | 95 / 91 | 1 / 7 / 7 | 成功、非空、未截断；另有 `.DS_Store` 元数据 |
| warehouse-s | `60b252f11972fed7d12f00960a7c6738b3f35a19` | 94 / 91 | 1 / 15 / 15 | 成功、非空、未截断 |

各类别一级 tree 的精确 URL：

| 类别 | URL |
|---|---|
| city | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/3e12a4483e615cd1a261d1e2476a29294fa4d0d1 |
| game | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/8d8f8fbe8d16d80f5dab7a5cbf5ab6f3a341215a |
| random | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/2264326dfda14559e0db92e1649aaf512f9ff98f |
| warehouse-s | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/60b252f11972fed7d12f00960a7c6738b3f35a19 |

每个已定位子目录的精确 GET 与范围：

| 固定相对目录 | 精确 URL | 读取范围 / 结果 |
|---|---|---|
| lifelong_benchmark/city/maps | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/f5db5b06e3f0531fe814f4cecf944e7a31ef183a | 一级完整元数据；1 blob，成功 |
| lifelong_benchmark/city/agents | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/c0fee9366c82e4c760d40d22aff3c5092ea270e6 | 一级完整元数据；18 blob，成功 |
| lifelong_benchmark/city/tasks | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/861e4e16acfd7e9003a417280d05b6ae5a78e339 | 一级完整元数据；18 blob，成功 |
| lifelong_benchmark/game/maps | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/8b3285417e230eb1da4dcfbb242862760ace1bea | 一级完整元数据；1 blob，成功 |
| lifelong_benchmark/game/agents | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/daab21eec30411b80bb91e434c25244fad8526d2 | 一级完整元数据；10 blob，成功 |
| lifelong_benchmark/game/tasks | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/bedef87e1c3ceadb4c24e2da505dc9b8010480e7 | 一级完整元数据；10 blob，成功 |
| lifelong_benchmark/random/maps | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/8b1a9718b9317122154ee416992f9772e1deb652 | 一级完整元数据；1 blob，成功 |
| lifelong_benchmark/random/agents | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/c998994b76d6726eae5ad3cc878f24bd6f7676a3 | 一级完整元数据；7 blob，成功 |
| lifelong_benchmark/random/tasks | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/7584768384137d1c05d0ddc423be8ccfd7a3f66c | 一级完整元数据；7 blob，成功 |
| lifelong_benchmark/warehouse-s/maps | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/d1248ff1cf4af4163a64828e1398f7b02a98bef8 | 一级完整元数据；1 blob，成功 |
| lifelong_benchmark/warehouse-s/agents | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/9d343cdafe66122ed15c3531be1af04fae5faa84 | 一级完整元数据；15 blob，成功 |
| lifelong_benchmark/warehouse-s/tasks | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/c27c62cb21a662a1891a480f348096a3c83b047c | 一级完整元数据；15 blob，成功 |
| lifelong_benchmark/delay | https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/4e3fe329a547e682d1520047bf767a5397b3b43f | 一级完整元数据；13 个正大小 `.txt` blob，无子树/符号链接/许可名目录项，成功、未截断 |

地图仅登记从 maps tree 取得的元数据，没有请求以下 map blob 正文：

| 类别 | 文件名元数据 | 固定 map blob | size 元数据 |
|---|---|---|---|
| city | `Paris_1_256.map` | `0ff641690b48c1c4807fcea7c0c31d167973b221` | 65829 bytes |
| game | `ht_mansion_n.map` | `7664df2f7cc97791a477b2529e7cae6d1005ee1f` | 36217 bytes |
| random | `random-32-32-20.map` | `b44f5a949e91b251b0e3bb29f3cd0784ce7d80b5` | 1091 bytes |
| warehouse-s | `warehouse-10-20-10-2-1.map` | `302a7ce60744aaf3a0c853c26bbffa3637fa027a` | 10242 bytes |

没有从 `agent-*` 或 map 文件名反推 teamSize、density、尺寸、场景概率或实验参数。没有读取配置 JSON 的引用边，因此 map/agent/task/delay blob 的实际组合、同语义别名、跨地图 incidence、完整合法 source_id 数量均为 UNKNOWN / NOT_EVALUATED。不能用相同条目数声称 agent/task 一一合法对应。

## 4. README、许可与上游链接链

以下所有仓库文件均属于上述固定 commit。

| 来源 | 精确 URL | blob / bytes / lines | 实际语义读取范围 | 结果 |
|---|---|---|---|---|
| README.md | https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/README.md | `a4578f87f918dab4b67b50cd404e3ec901a8f636` / 2730 / 86 | L1–86 全文；仅作来源/许可/入口上下文，不执行命令 | 成功 |
| LICENSE | https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/LICENSE | `1f4b6eadac278447824a47d409bb4de04ea7f3ee` / 1084 / 21 | L1–21 全文 | 成功；MIT 明文 |
| Input_Output_Format.md | https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/Input_Output_Format.md | `a16e1a41630d0a6229118ef5f4096e6717bb6c36` / 12724 / 69 | 全文仅作标题/链接定位，排除 fenced examples；输出标题 L2/15/31/48；语义读 L31–47 地图格式说明，未读配置/输出 JSON 样例 | GET 成功；未定位上游数据集链接 |
| README L7 指向的 League 官网 | http://www.leagueofrobotrunners.org/ → https://www.leagueofrobotrunners.org/ | 非 Git 页面；commit/blob 不适用 | 本次 `web.run` 展示全部可提取内容，仅 1 行，要求启用 JavaScript | 页面 GET/解析返回成功，但许可/数据说明内容不可得；上游追踪失败 |

LICENSE 的授权对象写作软件及其相关文档，并要求保留版权和许可告示；文中没有逐项列举这四类地图、场景、agent/task/delay 文件的来源或第三方再授权。README L7 指到 League 官网，L65 指到输入输出格式文档，L69/L78 分别是规划/提交说明链接，L72 为可视化代码库；没有直接上游地图数据集链接。未请求可视化库、规划/提交说明的替代材料来推定素材许可。

输入格式说明 L31–47 仅说明地图头部字段 `type`、`height`、`width`、`map` 及符号表，未给出上游来源或许可链接；它不能充当外来地图的授权证明。该窗口的头部文字是格式占位说明，不是地图载荷。

| 许可/来源问题 | 本次可支持状态 | 不可推出之事 |
|---|---|---|
| 根代码/关联文档是否出现 MIT 文本 | 明文可得 | 不等于已核清每个第三方成分的权利归属 |
| 四类数据目录有无单独许可名目录项 | 已查完整目录元数据中未见 | 不等于所有潜在文本均无素材许可 |
| 根 MIT 是否已证明覆盖四类外来素材 | **UNKNOWN / 未建立覆盖证据** | 不能把“仓库 MIT”改写为“全部地图/场景 MIT”；也不能据此宣告其违法或必然不受 MIT 覆盖 |
| 官方上游数据集是谁、许可是什么 | **UNKNOWN / 未定位** | 不凭文件名或个人记忆定上游归属 |
| R0 map blob 与上游原素材是否相同 | **NOT_CHECKED** | 没有地图正文或上游下载比对 |
| agents/tasks/delay 是否为上游原始场景、衍生转换或另行生成 | **UNKNOWN** | 不以扩展名/目录名推定数据生成链与授权链 |

## 5. 输入 parser 对象与实际读取窗口

源码仅作字段和解析语义证据，不是编译、执行或运行故障证明。对以下所有对象均先由固定 src/inc tree 定位具体文件与 blob，再请求 commit 固定 raw URL。

| 来源 | 精确 URL | blob / 元数据 bytes / 传输文本 lines | 实际读取范围及状态 |
|---|---|---|---|
| src/driver.cpp | https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp | `b75764cc26c2374ce51dabb94e13a138e50f166f` / 6664 / 172 | 成功；语义读 L1–18、L71–78、L78–94、L92–157；另外仅定位 `base_folder` 的行，命中 L70/73/74/75/77/102/114/115/150 |
| src/Grid.cpp | https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/Grid.cpp | `b78abb1848a74d4c801e6eea6e1e89ccf4f6ddbe` / 2155 / 71 | 成功；L1–71，完整且仅为地图 parser |
| inc/common.h | https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/common.h | `9ddeff363a76cbd70a3e6e1ca98cfd79f69c8237` / 5954 / 224 | 成功；先定位 `read_int_vec`/`read_int_delay`/`read_param_json`，再语义读 L62–208；L208 仅触及带默认参数重载的签名，未读取其体、未接纳任何默认 |
| src/CompetitionSystem.cpp | https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/CompetitionSystem.cpp | `4e9a86921fda3fd15bd616c3c0dff461688254ed` / 27752 / 885 | GET 成功；仅定位加载/构造/starts 相关单行，见下段；未展开方法，不把它作为初态合法性审计 |
| src/DelaySimulation.cpp | https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/DelaySimulation.cpp | `1e1953d9fa9ccb1eb96ae5d7b8829f425679d113` / 14733 / 455 | GET 成功；寻找输入加载入口的定位模式无命中；未输出/语义读方法体；定位失败，不作 delay 时序定义证据 |
| src/common.cpp | https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/common.cpp | `37b91585718f2079c436508e592fdb9dd2eb7aee` / 1237 / 48 | GET 成功；所找三个 read helper 均无命中；未输出/语义读方法体；helper 实际位于 common.h |

CompetitionSystem 的第一次加载名定位输出 L772（`load_agent_tasks` 签名）和 L791（加载失败注释）。第二次构造/starts 定位仅输出 L95、L507、L551–553、L813；本回执没有把这些孤立行串成已审查的初始化调用链。DelaySimulation 的 455 行为本次传输文本按换行计数，不借候选既有行数记载声称再次全文审阅；其字节数与固定 tree 一致，但未独立复算 blob 哈希。

## 6. 静态合法解析谓词所需字段的定义证据

下表区分“源码读了什么/怎样读”与“未来完整合法解析还需检查什么”。后列属于固定 72 §11 所要求但本次未执行的谓词工作项，不是本次新增实验合同、已实现检查或任何资格判定。

| 字段/数据层 | 固定证据与实际语义 | 仍未执行或未证明 |
|---|---|---|
| JSON 文件与类型 | driver L86–99 用输入文件流调用 JSON parse；common.h L187–204 检查指定键存在，再按模板类型读取，捕获类型错误 | 任一实际 JSON 的编码、完整语法、重复键语义、异常覆盖、非空内容与字段值均未检查 |
| 引用根目录 | driver L71–78 从 `inputFile` 取 parent_path 并补目录分隔符；L102/114/115/150 将这个字符串与字段路径拼接 | 这些窗口未建立规范化后仍在固定树内、禁止绝对路径、解释符号链接、引用 blob 存在等保证；固定 72 的严格引用谓词仍待实施/求值 |
| `mapFile` | driver L101 按 string 读取；L102 交给 Grid | 未读取 JSON 内实际引用，不确认 map blob 与此配置相连 |
| `teamSize` | driver L112 按 int 读取，并传给 agents 与 delay reader | 没有赋值或由文件名取值；数值合法域及与未来 density N 绑定后的相容性未检验 |
| `agentFile` | driver L114 按 string 取路径；common.h L62–99 跳过以 `#` 开头的行，首行首逗号 token 经 `atoi` 作为容量声明，容量不足会退出，随后按请求 team size 读取每行首个整数 token | 初态整数列表的真实长度、严格整数语法、索引范围、通行、互异和分配初态合法性未检查；源码旁注含 row/col，但实际只取一个 token，不能据注释猜成坐标对 |
| `taskFile` | driver L115 按 string 取路径；common.h L103–137 将首行首 token 经 `atoi` 当计数，再读取对应数量行各自首个 token | 变量名虽叫 team_size，这个重载按其文件首项决定循环次数，不证实它等于机器人数量；任务非空、真实条目数、索引范围和静态通行未检查 |
| `delayFile` | driver L150 按 string 取路径，传入 team size；common.h L139–183 读容量声明，按 team size 读取各行逗号分隔 token，经 `atoi` 存入 bool 向量 | 布尔词法合法域、各行长度、时间索引定义和全部所需索引的可访问性未检查；存入 bool 不等于已严格验证合法二值数据，未据此赋 T_delay |
| `taskAssignmentStrategy` | driver L121 按 string 读取；L122–144 分到 greedy、roundrobin、roundrobin_fixed 或退出；fixed 分支 L132–137 按 agent 数建立任务分组 | 未读取实际策略值，未证明任何分支的完整原分配初态合法；空 agent 等前置条件及完整策略语义不由三个分支名自动满足 |
| 地图尺寸与行结构 | Grid L19–47 依据首行首字符区分 benchmark 头部或逗号尺寸格式；读取 rows/cols；L49 分配 rows×cols 存储 | dimensions 的严格语法、正性、乘积可表示性、行数/行宽与头部一致性未检查；这些访问没有成为实际载荷已合法的证据 |
| 地图索引与通行编码 | Grid L54–64 用 `id = cols * i + j`，`@` 或 `T` 记障碍，其它字符记通行；输入格式说明 L40–46 列 `@`、`.`、`E`、`S` | 文档符号表与源码并不完全相同：源码额外阻挡 `T`，且其它字符宽泛走 free 分支。严格字符词汇表、agent/task 对线性索引和静态通行的检查均未求值 |
| 其它语义选项 | driver 所读窗口显示 command-line commitStep、mapfPlanner、delayPolicy、delaySimulateAll 等进入相应对象/字段 | 未读取、接受或绑定这些选项的运行默认；parsed_semantic_options、版本身份和 source_id 的完整规范化仍未生成 |

重要区分：`read_int_vec` / `read_int_delay` 对文件打开失败直接返回空向量；多处使用 `atoi`、首字符访问和 tokenizer 首项。上述亲见行为说明“parser 能执行某段读取”不能代替严格词法/长度/非空/域检查。这里没有在实际输入上运行它们，也不据此宣称已发生崩溃、越界、未定义行为或任何算法结果。

静态几何/通行、初态互异、可用任务及完整参考计划的适用性，均未由本次读取证明。尤其不由“四类都有目录”推出“四类各有至少一个完整静态合法 source_id”。当前合法 roster、合法来源计数、比较配置适用性仍为 NOT_EVALUATED / UNINSTANTIATED。

## 7. 成功、失败与未知的最终登记

| 项目 | 最终记录 |
|---|---|
| 固定 commit→真实根 tree→lifelong→四类别及其 maps/agents/tasks 的目录身份链 | SUCCESS，限 Git 元数据 |
| 四类非空元数据可得性 | SUCCESS，限条目存在与正大小，不是载荷合法性 |
| README/LICENSE 原文可得性 | SUCCESS |
| 根 MIT 明文存在 | SUCCESS，素材覆盖与第三方权利链仍 UNKNOWN |
| 官方上游数据集/素材许可页定位 | 未成功；README→League 的可提取网页内容仅 JavaScript 壳，固定格式文档未给上游链接；UNKNOWN |
| driver/common.h/Grid 输入字段及基础 parser 行为定位 | SUCCESS，限记录窗口 |
| 在 DelaySimulation.cpp、common.cpp 中定位 read helper | 未命中；不冒充相关方法体已读 |
| 载荷解析、静态合法性求值、别名合并、source_id/manifest 生成 | NOT_DONE，未授权执行且未执行 |
| 初态、动力学、计划、编译/链接、实际运行或实验复现 | NOT_CHECKED / NOT_RUN |
| 资格投票及后继候选 | NONE；本回执不授 PASS、不替换固定 72 或旧缺失回执 |

文件写入前两次对精确目标路径执行 `rtk proxy test -e`，均返回 1、无输出，确认目标不存在。唯一文件变更是以 `apply_patch` 新建本回执。所有 shell 命令均使用 `rtk`，原文使用 `rtk proxy`。本回执的文件 SHA256、bytes、lines 在写入后另行只读计算并随交付消息报告，避免把自引用哈希写入自身。
