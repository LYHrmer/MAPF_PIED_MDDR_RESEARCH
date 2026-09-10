# 73L12A：Traffic Flow 桌面阅读包更新实际回执

2026-09-10（Asia/Shanghai）。本有界包更新已完成；它接续于已经完成并交付的 L12/C11 四件，未改那四件字节，也不追加科研审查票。仅本次合法下载使用 nature-downloader 的来源与文件核验流程；L12/C11 的科学分析仍为 NO-SKILL / CONSTRUCTIVE / NONBALLOT。研究保持 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT，有效六门未变。

## 1. 授权、来源与实际下载

用户已明确授权本桌面阅读包，根在亲读 Traffic Flow 官方主文后将这一个新增文件及两指南交给本子代理；无需再请求目录/机构登录确认。授权目录为 `/home/lyh/桌面/MAPF_实验前必读论文_20260909`。本次没有访问旧桌面文献备份。先全读 [nature-downloader/SKILL.md](/home/lyh/.codex/skills/nature-downloader/SKILL.md)，只采用已知官方开放 PDF 直取路径；没有机构配置、账号、浏览器会话读取或登录/验证码绕过。

论文：Zhe Chen, Daniel Harabor, Jiaoyang Li, Peter J. Stuckey，*Traffic Flow Optimisation for Lifelong Multi-Agent Path Finding*，AAAI 2024，38(18):20674–20682，DOI 10.1609/aaai.v38i18.30054，官网 Published 2024-03-24。[AAAI 官方元数据](https://ojs.aaai.org/index.php/AAAI/article/view/30054)与[本次官方 PDF URL](https://ojs.aaai.org/index.php/AAAI/article/download/30054/31856)已亲核；当前保存的是官方正文，不是更换为作者预印本。

保存目标 `12_Traffic_Flow_Optimisation_AAAI_2024.pdf` 及本回执在写前均实际核不存在。下载前对原 11 篇逐项读取 bytes/SHA256；guide 前身份也已读取。实际下载命令为 `rtk proxy curl --http1.1 -fLsS --connect-timeout 15 --max-time 60 <同一官方URL> --output <唯一新PDF路径> --write-out <状态字段>`，按已授权网络升级执行。原 exec session 37376，最终 chunk cf615c / exit 0；HTTP 200，content_type=application/pdf，size_download=2877835，effective URL 与请求 URL 相同。无部分文件当成功、无再次重派和未结束下载句柄。

L12 之前曾对同 URL 作纯内存身份读取，其一次 TLS EOF 和随后 HTTP/1.1 成功已记在已完成 L12；本回执仅以这里实际保存及本地核验为下载完成依据，不把前次内存成功代替本地文件。

## 2. 实际本地验证和阅读范围

新 PDF：SHA256 `c57ab25d529e87113035f413d9fae90fc5a05cc5a8c623a357fba55d6be6e30a`，2877835 bytes；首 8 字节 `%PDF-1.5`，末尾经空白裁剪为 `%%EOF`。本地全字节 hash 与 L12 对同 URL 取得的字节身份相同。

`rtk proxy pdfinfo <新PDF>` 实际 exit 0：Pages=9、Encrypted=no、PDF version=1.5、File size=2877835；题名和四位作者与官方条目一致。`rtk proxy pdftotext -f 1 -l 1 -layout <新PDF> -` 实际 exit 0，已完整读第一页提取，确认题名、四作者、AAAI-24 页眉、摘要与第一页印刷页码 20674。PDF 内部创建时间是文件元信息，未拿它替代论文发表日期。

科学阅读范围沿已完成 L12：官方主文文字层 L0–741 全部读完，含方法、实验、表格文字、图注、结论、参考文献；根另报告其独立全文阅读，不以根报告替本子代理阅读。保存后的本地检查限身份、页数和第一页，没有声称重新逐页检查所有图像像素或复算原实验。

状态为 open_access_downloaded。只取主文，SI 未请求/未下载；官方条目未见可确认的独立 SI 入口，存在性仍 UNKNOWN。不下载论文所链的地图、场景、源码、任务、配置或实验结果。

## 3. 两指南的确切变化与身份

00 指南首页已改为当前 12 篇，说明“6 篇基础 + 4 篇主题 + SCALE/Traffic Flow 两篇追加近邻”的阅读层次；旧问题中的“内部随机查询”同时改为当前准确的“内部合理轮询”。新增 Traffic Flow 段建议在 RHCR 后阅读，重点 Fig.4–5、Table1–2 与 lifelong procedure，讨论拥堵引导、扩展性、初始化/维护费用与消融的对应关系。不把原同步动作或 PIBT 保证直接移植，不复制论文数值为本项目参数。

99 只追加第 12 篇的状态/完整身份/日期/版本/阅读层次及新的总量。原 14550 bytes 的历史前缀 SHA256 仍为 `21972106febd09dcd451a0e0e7e987efaf645a49658c0ad727f3e66b0b6f900d`，与修改前完整文件一致；原 10 篇与第 11 篇各自取得日期和版本记录没有重写，SCALE 仍为指定 arXiv v2 作者预印本。

| 文件 | 更新前 SHA256 / bytes / LF | 更新后 SHA256 / bytes / LF |
|---|---|---|
| 00_阅读顺序与交流问题.md | b5731062381cdc58c7b5531fad71329764d5fd862c5bb938d7889785b6d40bee / 8766 / 51 | c381b9c3b71d29395512111ec15ca12e19ece130a84546eb40eb3510ab347758 / 10678 / 63 |
| 99_来源与下载核验.md | 21972106febd09dcd451a0e0e7e987efaf645a49658c0ad727f3e66b0b6f900d / 14550 / 142 | 6773ad057ee662bec5b70b63db20dc083c5b4dffcd675c53e387737fc8f14250 / 17234 / 161 |

## 4. 完整 PDF 文件表与原 11 篇不变证据

下载前原 11 项 JSON 元信息列表与下载后对应 11 项按文件名/bytes/SHA256 比较，结果实际为 True。以下是下载后完整 PDF 表；每个旧条目均与下载前对应值一致。没有读取/修改原 PDF 正文来替代本次文件身份核验。

| PDF 文件 | bytes | SHA256 | 本次状态 |
|---|---:|---|---|
| 01_Hoenig_2019_Persistent_Robust_Execution.pdf | 1188912 | 3b82372d6c6c67aaac6b67eaf91d1bc86529c2671f50dbabbf80e560a9fdb849 | 前后相同 |
| 02_Zhong_2026_Planned_Synchronization_Active_Observations.pdf | 4961033 | f4efba9a20cc2236d2b84f650740a2cc6501841ac07f71175ed5a6ffbe3c8b22 | 前后相同 |
| 03_Chen_2021_S2M2.pdf | 1153174 | 40da52395053c291b3134f207aca4a4b2686f964bcef81c17636a8d4d7ec7fc3 | 前后相同 |
| 04_Okumura_2021_Time_Independent_Planning.pdf | 536064 | 9d0663bcdb99a31311a3ced5ff0e4a741fc169845d9d177c48db78011aaa6986 | 前后相同 |
| 05_Shahar_2021_MAPF_Time_Uncertainty.pdf | 1097341 | def08325da0ee2d4d12e01fd5ed864acaa224b87b0421f402803b9e4a68023bd | 前后相同 |
| 06_Zhu_2022_B_UAVC.pdf | 7788136 | 6de59654091de1bdf388f1544c00e7ce4be1236f2b1aad89dfd682c7897e2e83 | 前后相同 |
| 07_WinkTPG_arXiv_2508.01495v2.pdf | 17909680 | c081fb8bee47117a19632eb4ccc4db98372659086d5d97ca6371bfb12fab6525 | 前后相同 |
| 08_Okumura_2026_MAPF_X_Tree_LaCAM.pdf | 4704831 | 0af4a32fa86be6f2be5612773086829055824ed694a1c1aa642073279740c6ee | 前后相同 |
| 09_Stern_2019_MAPF_Definitions_Variants_Benchmarks.pdf | 782141 | 4ad2e43c6e62fae0acc317e36bb4423bc8e75cd247aa92bc0d489718c5ae5cd1 | 前后相同 |
| 10_Li_2021_Lifelong_MAPF_Large_Scale_Warehouses_RHCR.pdf | 2997584 | 89dc4585239c24625851832ea9728c10f6560c3bfe50fcc7da4054dbc3c7c690 | 前后相同 |
| 11_SCALE_2026_arXiv_v2.pdf | 22934614 | 5fd2432c60e57963bde9ab9cfdbba0ae5c651bdbf77275d9afd3a654e281fb67 | 前后相同 |
| 12_Traffic_Flow_Optimisation_AAAI_2024.pdf | 2877835 | c57ab25d529e87113035f413d9fae90fc5a05cc5a8c623a357fba55d6be6e30a | 本次新增 |

当前目录实际文件集合为这 12 篇 PDF 加上上述两指南，共 14 个文件。PDF 合计 **68931345 bytes / 169 页**；页数总量由先前已核且字节未改的原 11 篇 160 页加本次 pdfinfo 的 9 页得到，未虚称重新运行原 11 篇 pdfinfo。

## 5. 与 L12/C11 已完成件分离及边界

包更新后再次实际核验 L12/C11 四件，仍分别为：L12 `90e8efdaca480f28c9199558943a6e88f788015ce98c411485a0797921ad7521`（24392 / 98）；C11 提示 `1b56806dc4bb76be7b865dd6add8a64a94ed635351d068df8f1e851252e2fb89`（8716 / 33）；C11 原 JSON `a66ce9ea11f97bd9fc8e1af29e6df2681283a4db5e9cf875ab30952a5b648c9b`（10459 / 1）；C11 完整回执 `e9e2c1c5d4afbdf9251ea1e997ef4154789834340c01929c93011ab33432bae4`（13109 / 122），括号为 bytes / LF。C11 已有 exit 0 完整终态，此下载任务没有再调用 Claude。

新研究目录工件仅本回执；桌面新文件仅第 12 篇，文字编辑仅 apply_patch。未修改 73、P10/C9、其它完成报告、行政页或 Git；不写旧桌面备份。无实现、伪代码、构建、测试、仿真、调参或保护参数赋值；35–38、Q-CAL/Q-CONFIRM 和受限/公开实验载荷未读。论文包完成仅表示指定文献取得与这些核验完成，不等于研究设计、来源许可或正式审查已经通过。
