# R19 复核入口

[三线结果与科研导师后评审](REPORT.md) · [完整数值表](RESULT_TABLES.md) · [下一方法](NEXT_METHOD_PLAN.md) · [作者基线资格](EXTERNAL_BASELINE_NEXT.md)。

本轮342登记行＝324完整执行＋18初始规划失败行。模型、执行器及科学登记冻结后不再改动；原始资料按内容寻址去重，重复请求复用已有成功或失败。分析和审核不是额外科学样本。

## 只读查看

`SUMMARY.csv` 给逐世界逐方法结果；`ANALYSIS.json` 给配对与按地图×场景族的探索性区间。`CORE_RESULTS.pdf/png` 是可导出的描述性结果图。N64只有2个可执行族，另1族初始规划超时，不能与核心6族混成完整规模优势。

`model/` 保存本次实际部署的 TRAIN-only 模型及来源；完整训练/九模式共同状态预测诊断位于 `explore/learned-query` 分支的 `exploration/learned_query/conditional_duration_20261005_r19/`。本目录 `PUBLIC_SCHEMA.json` 是查询接口，`model/PUBLIC_SCHEMA.json` 是模型输入，两者用途不同。

## 恢复新增证据

从本分支仓库根目录运行以下命令；只恢复数据，不运行优化器或重放科学实验：

```sh
rtk proxy python3 exploration/error_guidance/sadg_structural_20261005_r19/restore_delta.py \
  --destination exploration/error_guidance/sadg_structural_20261005_r19
```

省略 `--destination` 只核验归档。已有同名文件须字节相同，否则拒绝覆盖。`publication_delta/MANIFEST.json` 保存每文件与分块哈希、原始回执身份、全量审核哈希；分块打包时已逐成员解包校验。

R19只保存新增证据。R18的原作者快照、官方地图归档、R16/R18继承实现和已绑定ECBS二进制，沿用本仓库旧轮次资料及其恢复入口。作者 SADG 固定提交为 `c2626d996121a9d6c128844a167b917db24418ac`；核查原算法时使用该提交，不自行替换新版。`data/planner/ecbs` 的旧二进制软链接在manifest中作为外部引用保存，不把软链接误报为自包含构建产物。复算既有结果不需要重新运行ECBS。

两份大的诊断 JSON 以无损gzip镜像提交（普通文本本机保留）。恢复到对应目录时使用 Python `gzip.decompress`，并核对 `solver_failure_review/FINAL_REVIEW_MANIFEST.json` 中原文SHA；无需重新求解。其它诊断清单与报告直接提交。

## 跨目录独立核验

解包后 `review/audit_episode.py` 不导入执行引擎或预测器，独立复算公共历史、条件预测、物理事件及采用图。下例中的 `/clone/repo` 是新检出目录，`/clone/cas` 对应已恢复的 `evidence_store`，`/clone/author` 是原绑定作者快照；不要将旧路径文本改写进冻结原始JSON：

```sh
rtk proxy python3 /clone/repo/exploration/error_guidance/sadg_structural_20261005_r19/review/audit_episode.py \
  --episode /clone/repo/exploration/error_guidance/sadg_structural_20261005_r19/episodes/random-32-32-10__s06__n16__stable/learned_no_query/episode.json \
  --root /clone/repo/exploration/error_guidance/sadg_structural_20261005_r19 \
  --store /clone/cas \
  --bundle /clone/repo/exploration/error_guidance/sadg_structural_20261005_r19/model \
  --path-map /home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE=/clone/repo \
  --path-map /home/lyh/.cache/mapf_research/sadg-controller-c2626d9=/clone/author \
  --output /tmp/r19-audit.json
```

实际迁移核验及负例见归档 `review/SCIENCE_RELOCATION_CHECK.json` 和 `review/VERIFIER_SELFCHECK.json`。全324条核验结果位于 `INDEPENDENT_AUDIT.json`，逐条证明在 `review/episodes/`。

定位勘误：冻结 `review/PUBLICATION_MANIFEST.json` 的外部登记引用标签写为 `REGISTRATION.json`，实际文件为本目录 `EXPERIMENT_REGISTRATION.json`，所记 SHA256 `9484ed1cd99e65ab65ba3fadea35e09162ab06e3762963bf26882b90051a9889` 正确。保留原清单字节，通过此处说明定位，不影响数据与审核身份。

`run_study.py` 是原登记矩阵入口；它以原身份复用已完成科学回执。用于阅读本轮证据时无需启动它。修改模型、预算、扰动或环境产生新研究问题时应新建下一轮登记，保留本轮结果。
