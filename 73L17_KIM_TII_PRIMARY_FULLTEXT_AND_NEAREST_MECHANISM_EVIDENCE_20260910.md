# 73L17 Kim 等 TII 论文的一手全文可得性与最近机制证据

状态：科研 NO-SKILL / CONSTRUCTIVE / NONBALLOT；2026-09-10。**本轮合法全文仍未取得。** 已完成有界的一手元数据/摘要/全文入口核验，不把它称作论文精读或新颖性排除完成。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT 保持；本件不改 73、桌面、行政页、Git 或旧完成件。

## 1. 论文身份和出版状态重新核验

完整题名为 **A Scalable Framework for Lifelong Multiagent Path Finding With Asynchronous Actions**。作者按出版方 Crossref 登记顺序为 Hyojeong Kim、Woonsang Kang、Sung-Kee Park、Myo-Taeg Lim、Yoonseon Oh、ChangHwan Kim。DOI 为 [10.1109/TII.2026.3681327](https://doi.org/10.1109/TII.2026.3681327)，期刊为 IEEE Transactions on Industrial Informatics，正式编排为 **22(8):6859–6870，2026-08**；韩国大学作者机构当前页面进一步明示 **Published－2026-08-01**。[作者机构记录](https://pure.korea.ac.kr/en/publications/a-scalable-framework-for-lifelong-multiagent-path-finding-with-as/)

本次实际取得的 [Crossref 出版方登记 JSON](https://api.crossref.org/works/10.1109%2FTII.2026.3681327) 与上述题名、六作者、卷期和页码一致，primary resource 为 [IEEE document 11511843](https://ieeexplore.ieee.org/document/11511843/)。JSON 的 published、published-print 和 issued 精度是年月，没有 published-online 字段。created 为 2026-05-07、deposited 为 2026-08-06；二者不是可代用的首次在线发表日期。精确到日的 2026-08-01 由机构 Published 字段支持，不把 Crossref 的年月字段冒称同样给了日期。

本轮先读旧 73L9 的 Kim 对应条目及其相邻证据/缺口行，核定没有混入其它同名作者或 Zhuang 论文；其本轮完整文件身份为 SHA256 `855ccddbf5b808c48c11ea4d2a5f0f91c62d61a8c32e099bcd8b41b5feabb896`，17245 bytes / 90 LF，未声称本题重新精读它的全部科学内容。根随后明确不必额外扩读其它“来源账本”。旧 L9 中机构网页 Accepted/In press 的历史描述保留原字节；现在记录为机构页面已更新。搜索缓存仍可能显示旧 Accepted/In press，不能覆盖本轮直接打开得到的 Published 正文。

## 2. 逐项一手入口及真实终态

| 来源 URL | 本次实际取得与阅读强度 | 全文结论 |
|---|---|---|
| [Crossref DOI 对象](https://api.crossref.org/works/10.1109%2FTII.2026.3681327) | Web 打开未成功；普通 rtk curl 取得完整 JSON，exec 76138 最终 exit 0，题录、日期、resource、license/link 字段实际读到。原 JSON 本轮未另存工件，未将旧 L9 JSON hash 当成本轮新哈希。 | 它是元数据，不是论文全文。link 中存在 intended-application=similarity-checking 的 staging VOR 地址；未访问，也未当作 OA 授权。 |
| [韩国大学作者机构记录](https://pure.korea.ac.kr/en/publications/a-scalable-framework-for-lifelong-multiagent-path-finding-with-as/) | 本轮直接打开的解析正文共 188 行，实际读题名/作者、摘要、卷期/日期、Access to Document 和题录导出。Access to Document 仅指 DOI，另有 Scopus 链接。 | 有一手摘要，没有可用论文附件；12 页是题录记载，不是 PDF 页数核验。 |
| [IEEE 正式条目](https://ieeexplore.ieee.org/document/11511843/) | 实际只得到要求启用 JavaScript 并验证非机器人的三行页面；没有论文正文、PDF 按钮内容或访问许可状态。 | 未取得全文；该返回不等于已经证明订阅付费墙或全球非 OA，不能绕过验证或改走内部地址。 |
| [KIST 完整机构记录](https://pubs.kist.re.kr/handle/201004/154784?mode=full) | Web 返回错误；同一对象的原始只读请求先遇沙箱 Operation not permitted，正常升级后 HTTP 200。完整可见文字及全部链接实际解析读取。HTML 23265 bytes，SHA256 `6cbfb7c5a9e26bc0db407625840caabbd447e365732f004b791cf368e3c17575`；exec 29226 最终 exit 0。 | 记录明确 dc.description.isOpenAccess=N；仅有题录导出/简单记录等链接，没有全文附件或可合法继续的 PDF 链接。 |
| [作者实验室 publications](https://sites.google.com/view/robots-oh/publications) | 实际读该文条目及其链接结构，解析正文共 68 行；该文为题名/六作者/期刊年份文字，相邻其它论文有项目链接。 | 该文条目没有 PDF、项目全文或作者稿链接；不能借其它论文链接补齐它。 |
| [作者实验室 members](https://sites.google.com/view/robots-oh/members) | 只核相关姓名定位窗口与可跟进链接；Woonsang 的 alumni 条目及另一拼写的 Hyojeoung intern 条目未提供绑定本 DOI 的全文地址。未凭姓名近似认定额外论文身份。 | 没有获得本题可用的新全文下一跳。 |

KIST 原站成功返回是本轮相对先前仅有检索摘要/Cache miss 的实际新增证据。其内容仍为 2026-05、pp.1–12、Article; Early Access 和非 OA，入库时间为 2026-05-27。该记录可以证明机构所列的旧早期状态及当前未挂附件，不能覆盖 Crossref 和韩国大学更新后的正式卷期，更不能把入库日期当在线发表日期。[KIST 原记录](https://pubs.kist.re.kr/handle/201004/154784?mode=full)

定点检索使用精确 DOI、完整题名、题名加 PDF、作者加 lifelong，以及 arXiv/Zenodo 和相关机构域限制；未找到匹配的官方预印本/开放仓储全文 URL。搜索出现的第三方聚合页和明显不匹配结果不作为科学证据，不跟随非授权下载入口。搜索未返回不证明世界上不存在作者稿；本轮只是未发现合法可读下一跳。没有请求作者发文、登录学校账号、调用机构凭据、绕过访问限制或下载独立实验载荷。

## 3. 最近机制：仅限一手摘要能支持的层次

作者机构摘要明确描述了以下组合：规划侧排除 cycle conflicts；执行侧用顶点先后约束处理 following conflicts，不显式建模动作时间；非 idle 机器人的剩余路径经调度器重同步后供局部重规划复用；另配贪心任务分配。这里是作者摘要所述机制，不是本代理核过算法或安全证明的结论。[作者机构摘要](https://pure.korea.ac.kr/en/publications/a-scalable-framework-for-lifelong-multiagent-path-finding-with-as/)

与本项目最接近的是**执行依赖、未完成路径复用与持续重规划之间的组合接口**。它提示“异步 lifelong 协调”或“保留剩余路径减少重算”已经有直接近邻，不能单凭这些词给本项目划出空白。摘要没有给出足以核对付费 POSITION、可信 q 下界、不可撤 cap/空间 owner、消息丢失、公共规划机会或完整费用模型的内容；不能从摘要未提这些内容反推全文没有。

本轮没有读到主文、定理/公式、算法段、图注、表格、消融或实验设置；没有 PDF 签名、PDF hash 或实际非零页数。题录的 12 页不计为已读 12 页。作者摘要中的安全、规模和吞吐主张没有经主文和表格复核，不转写为本研究效果、参数或可继承保证，也不拿来给该方法指定已有外部适配规则。

具体仍缺：顶点先后约束依据什么完成/进度信息更新、调度器读取的信息是否无误差/即时；重同步是否能改动已提交或正在执行动作；循环冲突排除与持续到达任务的联合前提；重规划/重同步/维护/分配/通信的实际成本和比较基线；失败/未完成与统计分母。以上是待全文核验的问题，不是指控原文缺漏这些项。

## 4. 目前唯一可采纳的改良：把残余路径复用的费用边界列入外部证据合同

在没有全文时，不提出“移植 Kim 算法”或新的查询策略。可立即采纳的是一项**证据与费用分工改良**：对以后任何声称借助剩余路径复用提高持续规划效率的外部比较，事前列一张责任映射表，将剩余路径读取/重同步、执行依赖维护、任务分配、候选生成与校验、消息/失败清理分别映射到它实际承担的服务和既有机会。只有全文或可资格化源能填实这些栏位，才把相应实现称作合格外部基线；不能只计新搜索时间而把重同步和执行知识更新移到免费底座。

该改良的直接用途是让 Kim 这种一手摘要已明示“复用与重同步”组合的近邻，进入对来源和执行成本的实质比较。它不要求现在修改 73 的规划器、O、D/R/E0 或主估计，也不强造额外对照臂。若后来实现中为该表新增运行记录，记录与核验自身的真实工作同样计费；复用能省多少搜索、增加多少重同步费用、最终是否有任务增量，均需之后合法设计和实测，当前不填数值。

强 R、E0 和完整外部方法比较仍保留；不能把更弱同步假设下的旧基线当作该近邻已被排除，也不能为对齐本项目而暗删对方已发表机制。若其任务分配或可撤/可改路径权限与本项目不同，应先标清方法域和适配身份；具体能否对齐仍待全文，现不编造裁剪合同。这是本代理独立提出的证据改良，不是声称 Kim 论文已经采用本项目的付费模型。

## 5. 交付边界与明确停止点

本次完成的是同一篇已登记论文的身份重核、真实入口检查、摘要级最近机制和精确全文缺口。**未取得合法主文，不能完成方法精读、新颖性排除或外部基线资格。** 不因多次检索无全文而把 UNKNOWN 改为“不重叠”，也不以元数据已闭代替设计闭合。

可继续的最小外部输入是一份由 IEEE 正常访问、作者公开页面或有明确开放权限的正式机构仓储提供的主文；本轮没有这样的可用链接。停止扩大检索，不请求 staging，不反复访问验证页面或其它无附件题录，也没有新增 Claude 调用。以后有合法主文再核公式/图表和具体机制，且明确区分正式 VOR 与作者稿版本。

本件唯一新增科学工件为本报告，文字仅 apply_patch，新工件只写研究目录；没有改阅读包、73 或完成旧件。未读取受限/公开实例载荷、35–38/Q 文件；没有实施、代码/伪代码、构建、研究测试、仿真、调参或保护参数赋值。全文检索分项未成功，建设报告交付不投资格票，HOLD 继续。
