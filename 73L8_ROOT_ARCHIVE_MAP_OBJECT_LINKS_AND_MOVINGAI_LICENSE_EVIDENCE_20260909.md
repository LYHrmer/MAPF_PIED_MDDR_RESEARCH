# 73L8：根核赛事地图对象关系与 Moving AI 明示许可入口

2026-09-09，/root 直接一手核验，NO-SKILL / CONSTRUCTIVE / NONBALLOT。承接72L2、73L6及73A2已实核根commit→tree链。本件没有打开任何地图、场景、任务、配置、delay、解或结果载荷，也没有载荷下载、转换、抽样或生成。只读取14个非递归Git tree元数据端点和4个官方说明/目录/许可网页。保护参数保持未赋值，HOLD。

## 1. 实质新结论

R0的random地图与固定赛事归档2023 Example Instances的random地图，父tree条目给出的Git blob及size一致；这是实际对象身份链接，超过同名猜测。Paris在这两个入口同名但blob与size均不同，不能说逐字节相同。此赛事示例game与warehouse入口列出的地图不同于R0对应条目，不能把类别同名当成整套R0数据来自这套赛事实例。

Moving AI两个官方说明页确实给出ODC-By许可链接，目录也实际列明R0四个地图名称。因此“没有定位任何上游许可入口”已不准确；但网站名称对应不证明R0 blob与该网站原对象一致，也不证明任务/延迟转换链。G5仍UNKNOWN。

## 2. 固定引用和有界读取路径

赛事仓库 MAPF-Competition/Benchmark-Archive 的固定commit仍为25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a，真实根tree为6030f1878e6abf48b833b5b7212953259fc81cb1；此前根已复核commit字段与根对象。这次由根已列的2023 Competition子tree进入Example Instances，再仅进入city/game/random/warehouse四个domain的maps子tree。没有进入Main Round/Test Round/Problem Generator或agents/tasks子tree，没有读2023 README正文。

R0仍为YueZhang-studyuse/LMAPF-delay固定commit0b5b33649fc367abcb1cd0a7ad5ac03511bf9357，其根/类别链取自72L2已登记元数据；本次重新取四个已知maps tree并亲核条目。不是重新遍历仓库，也不从文件名数字推参数。

以下每个GET都完整成功、truncated=false，均无递归参数。根按每条mode/name/SHA构造Git tree对象帧，实际重算都等于表中tree SHA。表中“条数/tree bytes”是元数据条数和树对象内容长度；JSON散列只标识连接器返回content字符串，不声称HTTP原始实体hash。14次端点请求包含跨仓库两次取得同一个random maps tree，故独立tree对象数为13。

| 精确目录及GET链接 | tree SHA（独立重算相同） | 条数 / tree bytes | JSON bytes | JSON SHA256 |
|---|---|---|---|---|
| [Archive/2023 Competition](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/2776a40fbf6d7aa83a04fe9cc6fef9540ca1f8c0) | 2776a40fbf6d7aa83a04fe9cc6fef9540ca1f8c0 | 5 / 241 | 1387 | cc28cf85d0c473d77183375c9e544c50b7ceadde456ff39054e2a291c32fe96a |
| [Archive/2023 Competition/Example Instances](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/1c4e53d21a835438dcaecdd15b7d83977552e434) | 1c4e53d21a835438dcaecdd15b7d83977552e434 | 4 / 159 | 1107 | 49bdf5435d50abda9f64f7833d56edf849bdffcae6d3b8ee2cfcee01dcede2ac |
| [Archive/Example Instances/city.domain](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/c45bd5afc3a2deb88612253ba54d6597cd5945f0) | c45bd5afc3a2deb88612253ba54d6597cd5945f0 | 12 / 524 | 3058 | a86cfe434bf177256c11067d0f569032d3c0b37ef3a658657386e32dd22a92c5 |
| [Archive/Example Instances/game.domain](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/64d2c9f63355e4cb6b42ceeb12416518226abe69) | 64d2c9f63355e4cb6b42ceeb12416518226abe69 | 13 / 579 | 3311 | b879ce5f829e3e65ebb07e00256f733aaf7e933782fef8f0c555285a85fbf166 |
| [Archive/Example Instances/random.domain](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/86138da4e2be82a893319279733c91dcb17cea29) | 86138da4e2be82a893319279733c91dcb17cea29 | 10 / 430 | 2570 | 7bf8a3ce41b8c05d754abe8a125e58a1780f0a4e42feeee534f8d65014a58f3f |
| [Archive/Example Instances/warehouse.domain](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/f98c14646581f9efef61e077b7cd54882b972da8) | f98c14646581f9efef61e077b7cd54882b972da8 | 30 / 1645 | 7725 | 903b55ecb4d5f2c3211213dd7e454a4a50d4c6c31d745d413b953b7fa44a6f82 |
| [Archive/Example Instances/city.domain/maps](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/5c7734378afaa428ad9cde584aa2a23972ccc4e7) | 5c7734378afaa428ad9cde584aa2a23972ccc4e7 | 1 / 43 | 443 | 6b70c4a4802cce105e83833552d9b646aecd8b1e0608194a663a87a12aeef89f |
| [Archive/Example Instances/game.domain/maps](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/4581b6bc3121854087cdb7d1ff6a93b034cdc4e0) | 4581b6bc3121854087cdb7d1ff6a93b034cdc4e0 | 1 / 39 | 439 | d3c20d00b95b71f7b60f49e0a816310e2b9b6d6e3b97b78a64c5cb039becbbff |
| [Archive/Example Instances/random.domain/maps](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/8b1a9718b9317122154ee416992f9772e1deb652) | 8b1a9718b9317122154ee416992f9772e1deb652 | 1 / 47 | 445 | b7b307430b8012c329eda4afced816c0be3383ae906fb2d731d897ec958c16de |
| [Archive/Example Instances/warehouse.domain/maps](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/6caab5c9527b2e96bcc26b0637f412efd80eaef9) | 6caab5c9527b2e96bcc26b0637f412efd80eaef9 | 3 / 141 | 937 | 51a2eab773fb79b8dfa2bb925f2efd9f49363aecb801ff44230fd4c848796cb4 |
| [R0/lifelong_benchmark/city/maps](https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/f5db5b06e3f0531fe814f4cecf944e7a31ef183a) | f5db5b06e3f0531fe814f4cecf944e7a31ef183a | 1 / 43 | 432 | 7049471b82760a4913f5e7b86b48a4324262860b237deb0e3085bdb2a34cc244 |
| [R0/lifelong_benchmark/game/maps](https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/8b3285417e230eb1da4dcfbb242862760ace1bea) | 8b3285417e230eb1da4dcfbb242862760ace1bea | 1 / 44 | 433 | d25fbb7fc01c2f09acc93e3de967dbbb9ac0da1915613c772521c153e398edab |
| [R0/lifelong_benchmark/random/maps](https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/8b1a9718b9317122154ee416992f9772e1deb652) | 8b1a9718b9317122154ee416992f9772e1deb652 | 1 / 47 | 435 | 936fda8f416b256de0fc23b9546b938748e6297fe0b3c54d796ce1f6cc5fd090 |
| [R0/lifelong_benchmark/warehouse-s/maps](https://api.github.com/repos/YueZhang-studyuse/LMAPF-delay/git/trees/d1248ff1cf4af4163a64828e1398f7b02a98bef8) | d1248ff1cf4af4163a64828e1398f7b02a98bef8 | 1 / 54 | 443 | 363b37bfa198357656a25e393542699312298d651fc462e87dc8394da3a1b0d6 |

2023一级有五条，包括三种实例/生成目录和README；Example Instances一级恰四个domain。domain目录中的配置只见名称、类型、大小、对象id，不读内容。上述目录范围没有列出独立许可文件。元数据中的JSON条目不构成本项目实验配置，也没有用于求值source_id或保护参数。

## 3. 地图blob关系的正负证据

下表全是API tree的元数据，不是对地图正文的计算。路径前缀Archive为固定2023 Competition/Example Instances；R0为lifelong_benchmark。

| 对应类别 | R0条目及blob / bytes | Archive示例maps条目及blob / bytes | 根可支持结论 |
|---|---|---|---|
| city | Paris_1_256.map；0ff641690b48c1c4807fcea7c0c31d167973b221 /65829 | Paris_1_256.map；4abf8ac92444fa5a82c19c287ee35c509110db05 /131659 | 文件名相同、Git blob及size不同；不能认逐字节同一对象，不猜测编码或转换 |
| game | ht_mansion_n.map；7664df2f7cc97791a477b2529e7cae6d1005ee1f /36217 | brc202d.map；2cd2ea9ad30d460eb5a3a18f64c4b720b3b490dd /255448 | 该示例game目录没有R0这一个名称；不能扩大为整个赛事归档都不存在 |
| random | random-32-32-20.map；b44f5a949e91b251b0e3bb29f3cd0784ce7d80b5 /1091 | 同名、同blob、同size，maps tree也同为8b1a9718b9317122154ee416992f9772e1deb652 | 两固定入口引用同一Git内容对象；不由此推导复制方向、任务同源或合法source_id |
| warehouse-s / warehouse | warehouse-10-20-10-2-1.map；302a7ce60744aaf3a0c853c26bbffa3637fa027a /10242 | sortation_large.map；8814604ba7a6f70ccb92ce45a20ab53a690ee280 /70177；warehouse_large.map；e8820df9f859ea5b17c47b871867262a5b8d1909 /70177；warehouse_small.map；1945236c2863a77375218ccfb09c589d546dc5ea /1949 | 该示例目录三条均非R0条目，不能按“小仓库”标签视为同图 |

没有下载blob来验证语义几何相同，也没有把同Git对象推成合法转换已经全闭。特别是city差异的原因目前未知；大小关系不授权猜编码、删行或自动规范化。已确证的正关系仅限所列random地图对象，未推广到agent/task/delay或配置引用。

## 4. Moving AI官方入口与许可阅读边界

根实际完整读取[2D Pathfinding Benchmarks](https://movingai.com/benchmarks/grids.html)可提取文字106行，以及[MAPF Benchmarks](https://movingai.com/benchmarks/mapf.html)37行。前者列明不同地图集合来源，并同时记载BioWare研究分发许可和部分其他集合再分发许可未明确取得的情况；两页页脚均指向ODC-By。不能只取页脚而抹去集合说明。本文没有由该声明直接作第三方内容权利已全清的结论。

根读取[MAPF目录](https://movingai.com/benchmarks/mapf/index.html)的文本条目；首显至153行，随后精确find实际展示至212行，因此四个所需名称均亲见：Paris_1_256.map、ht_mansion_n.map、random-32-32-20.map、warehouse-10-20-10-2-1.map。没有点击map/scen/图像或压缩包链接，没有从目录尺寸/问题数设定本项目参数。这只是网站条目与R0名称关系；网页未给本次可与R0 Git blob比较的内容散列。

沿上述明确链接实际打开[ODC-By v1.0全文](https://opendatacommons.org/licenses/by/1-0/)，可提取194行完整读。其序言及2.4区分数据库权利和内容本身的独立权利，4.2–4.3区分数据库分发与公开产出物的告示要求。当前只据此登记许可版本、范围和归属告示义务，未将ODC-By改称全地图MIT，也未把页面声明当R0衍生链证明。

上述网页是2026-09-09实际读取的现行网页，未取得版本化内容hash；工具crawl日期不是本站修改日期。固定Git元数据与现行网站许可自述是两类证据，不能混成固定commit内自带的许可证。

## 5. 对G5关闭条件的实际影响

- 已关闭的小项：赛事根到2023 Example Instances四类maps的明确元数据入口；R0与该归档random地图的同Git对象关系；Moving AI官网四个同名地图条目与ODC-By明示入口存在。
- 已排除的错误捷径：R0四类地图就是这套2023赛事示例地图；同名Paris必定同字节；仓库根MIT或Moving AI页脚自动覆盖任意第三方内容、任务和delay；文献/网站引用等同完整数据谱系。
- 仍须关闭：R0各具体对象到正确上游版本的链和实际转换依据、适用素材许可/归属、agent/task/delay来源、配置引用与本项目合法source_id资格。受限载荷正文当前仍不读取；不能为了把门写成PASS而越界求值。
- 后续可以在当前边界内继续精确元数据和官方说明核验；若一条候选来源链本身不足，就比较其他有明确依据的来源路线，并将总体定义和可比性变化事前写清。不能在看过结果后换池或只留有利实例。

本件没有法律通过票、来源通过票或研究结果，未发送作者邮件/issue。全部工具实际返回完毕，无新增失落句柄。它是根自行完成的L8，不替代待回L7外部协议合同，也不覆盖旧L6回执。73未固定未送审，六门仍2 PASS /3 UNKNOWN /1 FAIL。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。
