# R16 发布与恢复说明

本目录本机原文件全部保留。发布集合只包括代码、协议、报告、摘要、原失败说明、许可、可读小规模后缀，以及压缩的详细生成记录；不包括venv、ECBS可执行文件、字节码或外部R13/R14轨迹。

`PUBLICATION_MANIFEST.json`列出需要发布的每个相对仓库路径、已有文件hash、归档hash和每个归档成员的原始字节hash。`PUBLICATION_PATHSPEC.txt`是同一明确路径集合，可交给根智能体审核；本任务没有执行git add/commit/push。父仓库默认忽略此研究目录，所以审核后如需暂存，命令必须显式处理忽略规则：

```bash
rtk proxy git -C /home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE add -f --pathspec-from-file=exploration/error_guidance/sadg_preflight_20261004_r16/PUBLICATION_PATHSPEC.txt
```

上面的命令仅说明，不代表本轮已执行或批准发布。

## 压缩内容

- `archives/sadg_models_inputs_r16.tar.gz`：12个case的完整前后图、全部MILP变量/约束、LP、作者stdout、guard候选和所有登记输入。
- `archives/sadg_mapping_r16.tar.gz`：旧checkpoint的完整动作映射、原版及隔离修补图；没有重新收集外部旧轨迹。
- `archives/sadg_attempt_logs_r16.tar.gz`：初次观测器失败的原case记录及过程日志。失败说明与汇总仍在可读REPORT/RESULTS_attempt01文件中。

`author_core_source.tar.gz`是固定提交的原作者核心源码子集，附许可；不包含编译二进制或venv。它不是完整ROS发行包。`MANIFEST.json`是压缩前科研工件清单，保留原样；此次发布范围以新增PUBLICATION_MANIFEST为准。

## 只读校验与无覆盖恢复

从研究目录运行：

```bash
rtk proxy python3 package_publication.py verify
```

它核对全部发布文件、归档本体和每个解压成员的SHA256，不运行ECBS/MILP/轨迹。

需要恢复详细工件时，选择一个新的空目录，运行：

```bash
rtk proxy python3 package_publication.py extract --destination /tmp/sadg-r16-restored
```

恢复器仅允许显式清单中的常规相对路径文件；拒绝链接、越界路径及覆盖既有文件。恢复后的 `cases/inputs/mapping/logs` 结构与原记录相同。它不是搬移，本机原始文件和压缩包都保留。

如需在新环境重现科学调用，按README和协议另建目录、固定源码/依赖并重新登记；校验或解包不需要重新运行已完成的12个优化配置。
