# 73L6：固定 Benchmark-Archive 根元数据与许可状态恢复

日期：2026-09-09。实际恢复核验时间锚：2026-09-09 12:50:57 UTC。

性质：NO-SKILL / NONBALLOT，有界来源恢复，不是正式审查、G5 票或实验放行。维持 **HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT**。

## 1. 已恢复什么，尚不能关闭什么

两个指定失败对象现已完整实收：固定引用 `25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a` 下的根 `README.md`，以及同一引用的非递归根 tree 元数据。README 的实际字节可与根 tree 中的 blob 标识相互核对。根清单完整列出四项，没有 `LICENSE` 或其他根许可文件，因此没有触发第三个许可全文对象的读取授权。

恢复完成不等于来源资格关闭。README 能支持仓库自身的归档用途说明，根 tree 能支持根目录条目身份；两者不能证明特定 R0 实例与上游文件逐字节同源、目录内所有对象都来自赛事、某项具体载荷具有已核实授权，或当前 G5 已通过。

本件仅为一个新 Markdown 工件。落盘前两次核查目标不存在。未读取任何子目录或载荷正文，未读 `.gitignore` 正文，未访问 README 中的站外链接，未获取 commit 差异、子树、许可猜测路径或仓库归档包。

## 2. 对象 A：根 README 完整回执及字节身份

官方固定对象链接：[README.md](https://github.com/MAPF-Competition/Benchmark-Archive/blob/25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a/README.md)。本次调用为 GitHub connector `github_fetch_file`，显式传入上述仓库、固定 `ref`、根路径 `README.md` 和 `encoding=base64`，没有行范围限制；没有依赖默认分支。

| 核验项 | 实收值 |
|---|---|
| repository | `MAPF-Competition/Benchmark-Archive` |
| 固定 ref | `25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a` |
| path | `README.md` |
| connector encoding | `base64` |
| connector blob sha | `77ddb82e6cba768e590d91976d158ec74dc8ee5f` |
| Base64 解码后实际字节数 | `1008` |
| LF 数 / splitlines 行数 | `17 / 17` |
| 实际字节 SHA256 | `1cf7f15a1389560b1fc7e3aa69734c3be69915ea2a10ca7fef5a1d40f116ba61` |
| 按 Git blob 帧重新计算 SHA1 | `77ddb82e6cba768e590d91976d158ec74dc8ee5f` |
| 根 tree 对应条目 size / sha | `1008` / `77ddb82e6cba768e590d91976d158ec74dc8ee5f` |
| 工具实际终态 | `isError=false`，完整 structuredContent；执行单元正常完成，无挂起句柄 |

Base64 中的传输换行不计为 README 内容；字节散列在解码后计算。独立 blob 核验使用 Git 的类型、十进制长度、NUL 分隔及原始内容共同形成的对象帧，而非只对 Markdown 文本直接作 SHA1。两个来源回执与独立重算三者一致。

已实际完整读完解码后的 17 行，未截断。第 1 行标题将其标为 League of Robot Runners 的 benchmark archive；第 3–4 行说明按年度赛事结束后发布实例和最佳已知解；第 8–12 行列出评估实例、解及其指标、实现交叉引用和生成脚本四类内容；第 16 行给出赛事网站和组织者联络方式。本段是 README 自述的归纳，并不是对相关实例、结果或脚本的正文核查。该全文没有许可条款，也没有指向某一许可文件的声明。[依据：固定 README](https://github.com/MAPF-Competition/Benchmark-Archive/blob/25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a/README.md)。

## 3. 对象 B：非递归根 tree 完整元数据

本次调用为 GitHub connector `github_fetch`，唯一 URL 是 [固定引用的 Git trees 端点](https://api.github.com/repos/MAPF-Competition/Benchmark-Archive/git/trees/25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a)。没有 `recursive` 参数。完整 JSON 的 `tree` 恰有下列四项，`truncated=false`；没有读取这些条目的 blob 或子树正文。

| 根 path | mode | type | sha | size（字节） |
|---|---|---|---|---|
| `.gitignore` | `100644` | `blob` | `e0e8c990d47b4f5a4831182bb0108349e38cbe0a` | `22` |
| `2023 Competition` | `040000` | `tree` | `2776a40fbf6d7aa83a04fe9cc6fef9540ca1f8c0` | 未提供 |
| `2024 Competition` | `040000` | `tree` | `3dd2a8f99c961d8166b21bf6d4e2478a5c74260a` | 未提供 |
| `README.md` | `100644` | `blob` | `77ddb82e6cba768e590d91976d158ec74dc8ee5f` | `1008` |

根 JSON 原样返回的顶层 `sha` 为 `25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a`，`url` 为本节上述请求端点。工具返回 `isError=false`，执行单元正常完成，无挂起句柄。connector 返回的 JSON `content` 字符串按 UTF-8 编码为 `1129` 字节，SHA256 为 `97470db3d2e982670c305431e2cd311f892cebdf93210182cf7eb5386a61acd1`。这是**connector 所交付 JSON 字符串**的字节身份，不能冒称服务器原始 HTTP 响应实体的散列。

### 3.1 不能混写的两个 sha

用这四条完整元数据按 Git tree 原生条目编码独立重建：目录 mode 使用 `40000`，普通文件使用 `100644`；每项包含 mode、空格、名称、NUL、20 字节子对象标识；按 Git tree 的名称顺序拼接。得到 tree 内容长度 `161` 字节，再加 Git tree 对象帧后求 SHA1 为：

`6030f1878e6abf48b833b5b7212953259fc81cb1`。

它与上述响应顶层 `sha` 不同。本件保留这一实际差异，不将返回的固定引用值直接命名为“独立核实的根 tree 对象 SHA”。这里请求端点以任务给定的 commit 引用寻址，返回也使用该值；仅这两个读取对象不足以判定其回显语义或独立验证 commit 对象本身及其 `tree` 字段。不得由此直接声称源内容损坏，也不得悄悄抹平差异。需要 commit→tree 的独立对象证据时，须由根另行授权精确的纯 commit 元数据对象；本次没有借机读取 commit、diff 或第四对象。

因此当前可复核的精确表述是：“给定固定 ref 的非递归 tree API 实收上述完整四项；它们按 Git 规范重建的树对象散列为 `6030f1878e6abf48b833b5b7212953259fc81cb1`；响应顶层字段原样为 `25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a`。”

## 4. 许可真实状态与最小结论

根 tree 已完整返回，四个根条目中没有 `LICENSE`、`LICENSE.md`、`LICENSE.txt`、`COPYING`、`NOTICE` 或其他独立许可条目；README 全文也没有许可授予声明。**本次核实的是固定引用的根目录没有许可文件、所读 README 没有许可条款。**

本次没有读取根目录之下任何对象，故不能据此证明全仓库及所有上游都没有许可证，也不能声称特定数据、代码、解或第三方内容享有相同授权。公开可访问、赛事使用、README 鼓励比较和构建于已有工作之上，均不能替代尚未取得的具体许可对象证据。本件不作法律裁断；对研究来源账本，精确状态应保留为“根级许可文件未发现；具体 R0 对象许可/授权证据仍未闭合”，不得写成“许可证全文已核实”或“全部载荷许可通过”。

第三对象的条件是根 tree 列明许可文件。本次条件不成立，实际外部对象总数为 **2**，许可全文读取数为 **0**。没有发出 `/license`、猜测路径、子目录递归或其他扩大检索请求。

## 5. 上游关系能证明到哪一步

| 命题 | 本次证据足以支持的范围 | 本次证据不足以支持的范围 |
|---|---|---|
| 归档与赛事的关系 | 固定 README 自述为该赛事的年度 benchmark archive，并链接赛事网站 | 独立核实网站控制者、法律权利主体或所有具体内容的产生者 |
| 年度目录 | 固定根 tree 实有 `2023 Competition`、`2024 Competition` 两个目录入口及其子树标识 | 目录内部是哪一版赛题、何时产生、是否逐项为官方评估实例 |
| README 身份 | 根 tree 的 README blob/size 与全字节实收及独立重算一致 | README 中对其他内容的概述等同于这些内容已检查 |
| 本地 R0 对象来源 | 为之后精确选择对象提供固定归档入口和可核对根元数据 | 本地 R0 与某个上游 blob 相同、变换链完整、分割未泄漏或载荷已具资格 |
| GitHub 上游/派生关系 | 本次没有额外取得 fork/parent/source 元数据，不作相关断言 | 由目录名称或 README 链接推定 fork 关系、提交祖先关系或数据继承关系 |

尤其不能把“当前根 README 已恢复”替代“R0 精确路径→该固定提交对应条目→上游 blob→已知本地对象身份/合法变换→许可证据”的完整链。本次未读取 R0 或任何具体 map、scen、config、task、结果、压缩包或生成脚本正文，也没有对这些对象做隐式内容比较。

## 6. 工具终态、既往失败句柄和完成边界

根派工说明已明确：上一轮 root 的 curl/gh 普通尝试及正常升级尝试均已超时终止，没有活句柄。本代理没有实际持有那些旧句柄，也未重新轮询它们；这条旧任务终态以根交付的已核状态为依据，不能写成“本代理亲自 poll 到结束”。本次是两个既定来源对象的 connector 恢复，没有重派任何失落咨询或 Claude 环几何任务。

本次两项 connector 只读调用在一个 `functions.exec` 中以有界并行形式发出，结果均完整返回，批次耗时约 `1.6` 秒；没有抛出异常、超时、`Script running`、会话 ID 或审批拒绝。解码、精确散列和 tree 重建检查的只读 shell 返回退出码 `0`。其后仅核查新报告目标不存在和当前时间；没有 shell 网络重试，没有启用 Claude、skill、新代理或 Git 写操作。

所有 shell 均经 `rtk proxy`；新文件只通过 `apply_patch` 写入研究目录。未改旧件、账本、73、Git 或保护参数。这里的身份计算是已获准来源元数据的只读核验，未生成实验载荷或研究实现。

本有界任务的实际完成范围是“README 与根 tree 两个精确对象恢复、元数据和字节身份核对、许可条件核验、证据限度成文”。具体未闭项是：独立 commit→tree 对象链接仍须避免字段误认；子目录及特定 R0 上游对象未获本次读取授权；具体许可/授权来源未闭合；本地 R0 字节与合法变换链未在本次核验；其他设计、来源及正式审查义务不受本件替代。任何后续扩大读取须由根在现行边界内另行明确范围。维持 **HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT**。
