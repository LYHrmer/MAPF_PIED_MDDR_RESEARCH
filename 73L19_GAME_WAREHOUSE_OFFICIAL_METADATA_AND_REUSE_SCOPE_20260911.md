# 73L19：game / warehouse-s 的 Moving AI 官方目录分类与研究分发范围

2026-09-11；执行代理 `/root/source73_r0_remaining_contract`。NO-SKILL / BOUNDED PRIMARY-SOURCE EVIDENCE / NONBALLOT。只读官方说明和目录文字，不是素材资格审查或法律结论。保持 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT，六门不变。

## 1. 结论与精确增量

两张目标地图均在 Moving AI 官方 MAPF 目录中有同名条目。`ht_mansion_n.map` 另可沿官网 2D 分类页的 Dragon Age 2 浏览链接定位到该游戏目录中的同名条目；这是明确的官网分类线索，比仅凭 R0 的 game 类别或文件名猜游戏来源更强。`warehouse-10-20-10-2-1.map` 有官方 MAPF 收录；该说明页还记载加入四张 warehouse 地图的更新，但没有给本对象具名生成者或生成记录。[MAPF 目录](https://www.movingai.com/benchmarks/mapf/index.html)、[2D 分类页](https://www.movingai.com/benchmarks/grids.html)、[Dragon Age 2 目录](https://www.movingai.com/benchmarks/da2/index.html)、[MAPF 说明](https://www.movingai.com/benchmarks/mapf.html)。

本次取得的目录没有提供这两个目标的内容哈希或 Git blob。故没有将 R0 的两个固定 blob 连接为“已证与 Moving AI 对象相同”；也没有证明 R0 的复制方向、转换历史及适用权利已闭合。game 的官网分类与研究分发文字可以形成有条件的来源线索，warehouse-s 的集合收录与集合许可可以形成有条件的再使用依据；两者都不能直接记为对象许可 PASS。

## 2. 输入身份与实际读取

先精确确认新报告不存在，落盘前再确认不存在且非符号链接。以下两件已完整读取，未修改；没有扩读另一账本或候选73。

| 输入文件 | SHA256 | bytes / LF |
|---|---|---|
| 73L18_ROOT_LORR_ARCHIVE_MAP_OBJECT_METADATA_PROVENANCE_20260911.md | e20a7dd2d05b495ece88a31164f2f9d3439439eeeb072aa6019be08ac9da1327 | 7542 / 57 |
| 73L2_PUBLIC_BENCHMARK_REUSE_PROVENANCE_BOUNDED_NONBALLOT_RECEIPT_20260907.md | 7796d5164c7367350c16d7215aa52045c30985fb44f05d1c109f769143eaa776 | 11382 / 96 |

R0 固定仓库为 `YueZhang-studyuse/LMAPF-delay`，commit `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。下列路径、Git blob SHA 和大小承接根73L18的已取树元数据，本子题亲读的是该来源回执，未再次请求 R0 树，更未请求地图正文。Git blob SHA 不是本报告的 SHA256，也不是本题新算的地图哈希。

| R0 路径 | 已登记 Git blob SHA | bytes |
|---|---|---:|
| lifelong_benchmark/game/maps/ht_mansion_n.map | 7664df2f7cc97791a477b2529e7cae6d1005ee1f | 36217 |
| lifelong_benchmark/warehouse-s/maps/warehouse-10-20-10-2-1.map | 302a7ce60744aaf3a0c853c26bbffa3637fa027a | 10242 |

73L18 已说明其固定 LoRR 归档树未见这两个同 blob 地图对应。本题没有把该未匹配改成上游不存在，也不重复其 city/random 取证。

## 3. 官方对象额度与阅读层次

实际取得 **4 / 最多6个**不同官方说明或目录对象，到此停止。先对两个精确文件名作 Moving AI 站内定向检索，取得 MAPF 目录；随后读取旧73L2已登记的两张说明页，并只点击2D说明中的 Dragon Age 2“Browse data”目录链接。另作一次两查询的 warehouse 来源定向检索，只找到已读 MAPF 说明及无关官网页面；没有据搜索摘要宣称新增作者来源，也没有打开无关页面。搜索结果不计说明对象；没有为用满额度请求第五、第六对象。

| ID | 精确请求／最终 URL | 实际可见范围与使用位置 |
|---|---|---|
| O1 | https://www.movingai.com/benchmarks/mapf/index.html | HTML 提取文字全文 L0–211；重点 L82、L190 的两目标目录元数据。页面中的地图／场景／ZIP／图像链接均未请求。 |
| O2 | https://www.movingai.com/benchmarks/mapf.html | HTML 提取文字全文 L0–36；重点 L18 warehouse 更新、L25–33 学术引用、L36 集合许可链接。 |
| O3 | https://www.movingai.com/benchmarks/grids.html | HTML 提取文字全文 L0–105；重点 L12–14 游戏分发说明、L45 的 Dragon Age 2 分类及目录链接、L105 集合许可链接。 |
| O4 | https://www.movingai.com/benchmarks/da2/index.html | 经 O3 Dragon Age 2 目录链接取得；HTML 提取文字全文 L0–277，重点 L105 的目标条目。没有打开任一图像或载荷。 |

行号是本次网页工具提取文本的位置，不是永久 HTML 源码行号。四对象均成功返回可读 `text/html`；本次未请求原始 HTML 字节用于哈希，未取得固定网页版本、历史快照、Git commit/blob 或 HTTP 内容身份。因此它们是访问日可读的官方声明／目录证据，不能写成不可变快照。网页工具对 O4 标记的缓存抓取时间为两周前，不冒称它与本次其余页面是服务端同一瞬间的快照。

没有运行浏览器渲染、请求页面图片或追取下载资源；目录文字中的预览占位和下载链接不等于读取地图图片／文件。没有进行 shell 网络调用、权限升级、Claude 调用或外部联系；无运行中或失落工具句柄。

## 4. game：分类连接、尺寸差异与权限边界

O3 在商业游戏分类中将 Dragon Age 2 的浏览入口指向 O4。O4 的 `ht_mansion_n.map` 条目列尺寸 **270×133**、状态数 **8,959**；O1 同名条目列尺寸 **133×270**、状态数同为 **8,959**。这些是照录的公开目录元数据，不是本研究参数赋值。[2D 分类页](https://www.movingai.com/benchmarks/grids.html)、[Dragon Age 2 目录](https://www.movingai.com/benchmarks/da2/index.html)、[MAPF 目录](https://www.movingai.com/benchmarks/mapf/index.html)。

本题只能确认“官网 Dragon Age 2 分类包含这个名称的条目”和“官网 MAPF 分类也包含同名条目”。不能把尺寸顺序不同自行解释为行列显示惯例、地图转置、编码转换或内容改变；相同状态数也不能判定内容相同。尤其不能用 R0 文件大小与上述尺寸凑一个可能的文件格式，反推它必为其中某个对象。未读载荷时，这种反推不是身份核验。

O3 的说明感谢 BioWare 允许为研究目的分发其地图，同时保留另一类地图未取得明确再分发许可、可按请求移除的说明；其 Dragon Age 2 来源链接本身指向 BioWare 域。由官网分类及这段署名说明，可以将“官方 DA2 集合条目”与 BioWare 研究分发声明建立来源上下文关联。原文没有列出逐 blob 的授权附件，本次也没有读取 BioWare 单独授权文件。[2D 官方说明](https://www.movingai.com/benchmarks/grids.html)。

上述关联是官网对所收录游戏集合的分类和分发说明，不是 R0 game 的已证授权链；缺的正是 R0 blob 到该集合具体对象的可靠连接及可能转换记录。旧73L2“不得由 game 名称套用 BioWare 声明”的边界仍成立，新增事实是本次已找到可指向 DA2 的官方目录入口。也不能把官网关于其它地图的保留说明反过来自动套到此对象，直接判定它没有研究分发依据。

## 5. warehouse-s：收录和更新说明可证，创作者与生成链未证

O1 列 `warehouse-10-20-10-2-1.map`，尺寸 **161×63**、状态数 **5,699**。O2 的更新说明记载 **2019-11-26** 为 benchmark 添加四张 warehouse 地图；这是官网集合更新日期，不能直接认作 R0 blob 的生成／复制日期。页面没有在本次可见文字中将该对象归给某一具名生成者、HOG2、LoRR 生成器或具体公开脚本。[MAPF 目录](https://www.movingai.com/benchmarks/mapf/index.html)、[MAPF 说明](https://www.movingai.com/benchmarks/mapf.html)。

据此可说“Moving AI 官方 MAPF 集合公开列有目标同名仓库地图，且有仓库子类的新增说明”；这比只从文件名含 warehouse 猜分类强。但不能扩写成“仓库素材由某作者原创且授权明确”或“R0 warehouse-s 就是官网下载原样”。O3 中其它人工地图的 HOG2 署名不跨类别转移到它；73L18 中 LoRR 生成器的存在也不能证明它生成过这个固定对象。

当前说明主要面向 MAPF 的地图和 start/goal 问题比较；没有把 R0 lifelong 的任务队列、agent 或 delay 文件列为其分发对象。因此地图集合收录和 task/delay 的生成来源是两项证据义务，不得由前者代签后者。

## 6. 可引用再使用说明与尚不能完成的连接

O2 和 O3 的数据声明均链接 Open Data Commons Attribution License；O2 要求论文使用这些 MAPF benchmarks 时引用 Stern 等 SoCS 2019，O3 对2D基准另给 Sturtevant 2012引用指引。这是本次亲见的集合层声明及学术引用要求。[MAPF 官方说明](https://www.movingai.com/benchmarks/mapf.html)、[2D 官方说明](https://www.movingai.com/benchmarks/grids.html)。

ODC-By 1.0 官方许可正文这次未重新请求；它的数据库与独立内容权利区分、公开使用／分发条件由已完整读到的73L2 §3.1承接，不冒充本轮新读许可条款。保留其登记的[官方许可原文入口](https://opendatacommons.org/licenses/by/1-0/)，本报告不另做法律适用分析。研究目的分发说明、数据库层许可、学术引用要求和软件许可不是可互换证据。

| 待证命题 | 本题允许的精确状态 | 不能随之声称 |
|---|---|---|
| 官方 DA2 目录是否有 ht_mansion_n.map | 已亲见分类路径及同名条目 | R0 blob 已等于官方 DA2 或 MAPF 对象 |
| 官方 MAPF 是否有目标 warehouse 条目 | 已亲见条目及 warehouse 集合更新文字 | 已识别原创生成者、生成脚本或复制日期 |
| Moving AI 是否公布相关再使用／研究分发说明 | 已亲见集合许可链接、BioWare 研究分发文字及保留条件 | 已替每个 R0 blob 完成逐对象权利连接 |
| 两张官方目录对象的不可变内容身份 | 未取得；目录没有展示目标哈希／Git blob | 文件名、尺寸或状态数足以代替内容身份 |
| R0 到官方对象的复制／转换关系 | UNKNOWN；承接R0身份，尚无跨端同对象证明或公开逐对象出处记录 | 已排除转换、同名异物或后续变更 |
| R0 agent/task/delay 的来源与许可 | 本题未调查，原缺口保留 | 由地图收录推其任务流或延迟载荷也被覆盖 |

## 7. 可停止调查的明确结论与最小下一证据

本题已完成有界目录／说明核验。新增的是 game 的官方 DA2 分类连接、两个目标的 MAPF 同名收录、仓库子类更新记录以及具体可关联的声明层次。**没有取得两个 R0 blob 的官方同对象上游，因此完整对象身份与适用许可仍未闭合。**不将来源局部进展折成资格票。

若后继仍要把这两个固定对象作为研究材料，最小还缺一份可公开核验的逐对象来源记录：应将 R0 固定路径/blob 指到官方上游的不可变对象标识，明确原样或转换关系，并保留适用的集合／独立素材分发说明。可以是已有官方来源清单、含哈希的目录元数据或公开出处说明；本题没有声称它已经存在，也没有向维护者索取。当前禁读载荷边界下，不通过下载 ZIP、地图正文或图片补这一步。

本次到四个官方对象即收束，不继续泛搜镜像、地图生成器或其它论文，不更动旧73L2/L18的历史状态。唯一新工件由 apply_patch 写入研究目录；未改73、行政页、Git、桌面或任何完成旧件。未读取35–38、Q-CAL/Q-CONFIRM及任何地图／场景／配置／agent／task／delay／result载荷，没有实现、构建、测试、仿真、调参或生成实例／结果；保护参数全未赋值。交付时另以只读工具给出本文件 SHA256、bytes、LF，真实完成状态与任何科学资格通过分开。
