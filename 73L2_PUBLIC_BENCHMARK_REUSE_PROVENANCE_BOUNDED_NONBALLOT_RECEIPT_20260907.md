# 73L2 — 公开 benchmark 再使用与来源链有界回执

日期：2026-09-07。执行代理：`/root/source72_dataset_metadata_license`。

性质：**BOUNDED SOURCE RECEIPT / NONBALLOT / NO-SKILL**。这是 72L2 之后的新来源任务，不修改或替代 72L2，不重复旧 69L1/69E1，不是候选、不作资格投票、不授予 PASS。本回执记录公开说明的文字、对象范围及证据缺口，不提供法律建议。

## 1. 结论

Moving AI 官方 benchmark 说明已提供可引用的公开依据：数据页链接 **Open Data Commons Attribution License（ODC-By）1.0**，并提出论文使用时的文献引用要求。2D 页另列研究用途的游戏地图分发说明和未取得明确再分发许可的情形。这些不同层次的文字应一起保留，不宜只摘页脚许可名称。[基准总页](https://movingai.com/benchmarks/)、[MAPF 说明](https://movingai.com/benchmarks/mapf.html)、[2D 说明](https://movingai.com/benchmarks/grids.html)。

**这些证据尚不能连接到 R0 四类具体素材。**本次没有逐对象出处声明、转换记录或内容身份比对，也没有读取载荷；相同类别名或文件名不是来源证明。R0 的 city、game、random、warehouse-s 各自的素材来源链、原素材权利链及适用许可仍为 **UNKNOWN**。

League 官网本次仅返回需要启用 JavaScript 的页面壳。它是否公开提供地图/任务出处及许可说明，仍为 **UNKNOWN**；这次抓取未取得说明不能证明网站没有说明。[League 首页](https://www.leagueofrobotrunners.org/)。

## 2. 本次边界与对象额度

仅请求下表 **六个不同官方说明对象**；没有搜索查询、没有浏览下载链接，没有追加第七个对象。ODC 原文是 Moving AI 页脚实际链接的官方许可文本。网页均按当前公开内容读取，非固定历史版本；网页自身没有取得 Git commit/blob 或内容哈希，不假称它们是不可变快照。

R0 身份由根任务直接给出：`YueZhang-studyuse/LMAPF-delay`，commit `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。本次重新请求其固定 README，仅为亲见 League 链接，不读取旧当地候选或回执补证。

没有使用 skill，没有派子代理，没有读取任何本地旧候选、旧报告、35–38、Q-CAL、Q-CONFIRM、results、实验 tapes 或桌面。没有请求任何 map/scen/config/agent/task/delay 载荷正文、压缩包、图像地图或实验输出；没有生成、实现、构建或运行测试、仿真、实验。没有向外部人员发消息。没有赋值任何实验参数、范围、默认或 density N。

| ID | 官方说明对象与原始 URL | 实际进入路径 | 亲见范围与技术结果 |
|---|---|---|---|
| O1 | Moving AI Pathfinding Benchmarks： https://movingai.com/benchmarks/ | 本任务明确授权的官方站点，直接 GET | `web.run` 返回 16 行（L0–15），全文说明可见；成功 |
| O2 | League of Robot Runners： https://www.leagueofrobotrunners.org/ | 官方平台首页，直接 GET；O6 L7 的原始链接为 `http://www.leagueofrobotrunners.org/` | `web.run` 返回 1 行（L0），只提示启用 JavaScript；页面可取得、内容说明未取得 |
| O3 | Open Data Commons Attribution License v1.0： https://opendatacommons.org/licenses/by/1-0/ | 点击 O1 的实际许可链接 | 返回 194 行（L0–193）；本次用途集中于序言 L19–24、定义 L33–57、覆盖范围 L60–84、授权 L85–102、使用条件 L103–123；未声称完整法律分析 |
| O4 | Moving AI MAPF Benchmarks： https://movingai.com/benchmarks/mapf.html | 点击 O1 的 MAPF 说明链接 | 返回 37 行（L0–36），全文说明可见；未点击 benchmark 下载/浏览入口 |
| O5 | Moving AI 2D Pathfinding Benchmarks： https://movingai.com/benchmarks/grids.html | 点击 O1 的 2D 说明链接 | 返回 106 行（L0–105），说明及分类元信息可见；重点 L11–26、L39–105；未点击任何 map/scenario 下载、图像、游戏站点或论文链接 |
| O6 | R0 固定 README： https://raw.githubusercontent.com/YueZhang-studyuse/LMAPF-delay/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/README.md | 固定 commit 定点 GitHub GET | 全对象传入工具内存，2730 UTF-8 bytes、86 行；只输出链接及许可/出处关键词定位命中，命中 L7/65/69/72/78；没有用它推素材许可 |

O6 的官方展示 URL 为 https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/README.md 。本次未请求 Git tree 或 blob API，因此不为它补写未经本次取得的 blob 哈希。O1–O5 的行号仅指本次工具可提取文本，非网站源代码永久行号。

O2 的唯一可提取文字为 “You need to enable JavaScript to run this app.”。本次没有可调用浏览器渲染工具，也没有进一步读取页面脚本、猜测网站路由或以其它年份站点替代；因此停止在真实可见边界。失败的是取得素材说明内容，不是断言 HTTP 访问失败。

## 3. 可以引用的官方文字与覆盖对象

### 3.1 数据页的公开声明

O1 L15、O4 L36、O5 L105 都将数据声明链接到 ODC-By；这是 **benchmark 数据集合的公开许可声明**，不是给整个网站所有文字、图片、代码及所有第三方原素材作统一许可的证据。[O1](https://movingai.com/benchmarks/)、[O4](https://movingai.com/benchmarks/mapf.html)、[O5](https://movingai.com/benchmarks/grids.html)。

O3 的序言及 §2.2–2.4 区分数据库与独立内容权利，且不覆盖数据库制作/运行软件、专利或商标。§3.1 的数据库使用授权包含商业用途；§4.2–4.3 规定相应公开分发/使用中的许可、告示和来源归属要求。因此这里有数据库层再使用依据，不能把它改写为每份游戏原素材均已获全面再授权。[ODC-By 1.0 原文](https://opendatacommons.org/licenses/by/1-0/)。

### 3.2 游戏素材与研究用途

O5 L12 记载 BioWare 允许其地图为研究目的分发；L14 又说明一些其它地图集未取得明确再分发许可、可应请求移除。保留这两句的不同对象和条件；页面未将后一说明逐项映射到本任务的任何 R0 blob。[2D 官方说明](https://movingai.com/benchmarks/grids.html)。

这可以证明官网确实公布过研究用途分发说明及权利链缺口，不能证明 R0 的 game 类必属 BioWare，也不能反向认定 R0 的 city/random/warehouse-s 无许可。本次不凭同名文件、游戏名称或类别名称作归属判断。

### 3.3 论文 benchmark 使用声明

O4 L25–33 要求论文使用 MAPF benchmarks 时引用 Stern 等的 2019 年综述；O5 L15–26 要求使用 2D benchmark problems 时引用 Sturtevant 的 2012 年论文。这是学术引用指引，不能替代具体独立素材的权利链。[MAPF 引用说明](https://movingai.com/benchmarks/mapf.html)、[2D 引用说明](https://movingai.com/benchmarks/grids.html)。

没有把官方 MAPF 场景文件的传统 start/goal 问题定义直接认作 R0 的 lifelong task 流；后者是否经过转换、另行生成或重新安排仍待来源记录。

## 4. 必须分开的证据层次

| 层次 | 本次状态 | 本回执允许的表述 | 本回执不作的推断 |
|---|---|---|---|
| 网站声明 / 网站内容许可 | 亲见 Moving AI 数据页页脚；League 内容不可提取 | 官网将 benchmark 数据关联至 ODC-By | 不把数据页脚当作网站全部页面内容统一许可 |
| 数据库/benchmark 集合许可 | ODC-By 原文可得 | 官方存在集合层再使用依据及其条件 | 不由集合许可消除独立内容权利问题 |
| 软件许可 | 本次没有请求 R0 或其它库的 LICENSE | 本次不以软件 MIT 作为素材授权证据 | 不由库 MIT 自动推地图/场景/任务许可 |
| 游戏等独立原素材权利 | 有 BioWare 研究分发说明；其它情形须保留局限 | 引用官网明确写出的对象和用途 | 不推定 R0 game 的原权利人，不授更广用途 |
| 论文 benchmark 学术引用 | 官方引用要求可得 | 可按实际使用的数据集标注对应基准论文 | 不把论文引用等同于权利链补齐 |

本表作证据分类，不针对任何具体司法辖区、商业行为或研究行为给出合法/违法判断。

## 5. R0 与公开声明之间仍缺少的连线

本次可确认的连线只有：固定 R0 README L7 → League 官网；Moving AI 官方 benchmark 页 → ODC-By 原文及各自的学术说明。**没有证据把前一条连到后一条，也没有具体 R0 素材到 Moving AI 原对象的映射。**

| 对象/链条 | 本次状态 | 原因 |
|---|---|---|
| R0 city 原素材 → 官方上游对象 → 适用声明 | UNKNOWN | 未取得逐对象出处与版本/身份记录 |
| R0 game 原素材 → 官方上游对象/原权利人 → 适用声明 | UNKNOWN | 同上；不能套用 BioWare 说明 |
| R0 random 原素材 → 官方上游对象/生成来源 → 适用声明 | UNKNOWN | 同上；人工类别名不是证明 |
| R0 warehouse-s 原素材 → 官方上游对象/生成来源 → 适用声明 | UNKNOWN | 同上 |
| R0 agent/task/delay 与上游场景的转换/生成关系 | UNKNOWN | 没有转换来源、生成者或权利记录；没有读取载荷 |
| League 是否公开地图/任务出处及素材许可 | UNKNOWN / CONTENT_NOT_RETRIEVED | 首页只取得 JavaScript 壳；不作网站全面不存在声明 |
| 六对象之外是否还有足以补齐的官方说明 | NOT_SEARCHED | 遵守六对象上限；未假装穷尽公开互联网 |

## 6. 最小可补证据

下面是以后补证所需的最小材料说明，不是本次生成计划、运行授权、外部联系动作或载荷请求：

1. **R0 的对象级出处表或维护者公开声明。**必须明确固定 commit 与每个地图/agent/task/delay 对象的身份，列原来源 URL、上游版本/身份以及原样复制、转换或另行生成的关系。只写 “from Moving AI” 或只列同名文件不足以连接具体对象。可以是官方 README/NOTICE/来源清单，不要求本次读取任何载荷。
2. **适用于这些具体对象的许可/允许用途声明。**数据库集合声明与独立游戏等素材声明分别指到相应对象；若主张某项研究用途分发许可，应明确该对象与权利人声明的对应关系，而不是从别的游戏或库许可类推。
3. **如依赖 League 作为中间来源，取得其可引用的官方素材出处页/NOTICE。**材料须明确哪些地图、初态、任务或转换由平台提供以及所附来源和许可。可稳定读取的官方文本页或官方仓库说明即可；目前首页 JavaScript 壳不能承担这条证据。

具备上述来源文本仍不等于已求值实际配置的合法性；本回执没有检查或授予任何配置资格。

## 7. 文件操作与交付状态

写入前对精确新路径执行存在检查及符号链接检查，均返回不存在/非链接；没有递归本地搜索或读取任何当地科学文件。唯一文件变更为 `apply_patch` 新建本回执。所有 shell 均以 `rtk` 开头，原始输出使用 `rtk proxy`。

六对象核验至此停止。SHA256、bytes、lines 在写入后仅对本新文件作只读计算并随交付报告；不写入自引用哈希，不修改 72L2、旧 69L1/69E1 或任何候选。
