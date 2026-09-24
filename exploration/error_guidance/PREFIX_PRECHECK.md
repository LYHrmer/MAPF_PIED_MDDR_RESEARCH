# 原 prefix 普通分支 × 名义解析等待：有限 2×2 后继

2026-09-24。严格编译和原生运行均退出 0，**2998 项检查通过，8 格实际执行完成**。本次把已有两条路线变成事前择路：在 t=0 用公开计划、已提交责任和声明的名义模型选择一次，然后执行所选路线。原 prefix 的普通初始授权在这个场景中与 full-MOVE 相同；t=4 的等待代价因此仍能改变选择，并使原生参考到达提前约 **0.833071**。t=5/2 两种代价都选择上绕。

## 原 prefix 在这里究竟是什么

冻结 [73 §4–5](../../73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md) 的规则是：**普通初始授予只尝试完整 ell；严格部分初始 cap 只来自 GROUP_ADMIT**。GROUP_ADMIT 需要不同未授请求构成有循环的强连通分量；一个已经 GRANTED 的 blocker 不能当作未授组员。已授请求才按有限 CAND 尝试安全扩展。

本场景每次只有 requester 的一个未授原 MOVE；前一步已经真实 END 并保留终点 resident，后续计划没有提前登记为请求。blocker 已授且仍被中心作为原活动责任保留。因此请求图只有一个顶点、没有不同请求间的边，也没有合法初始部分 cap。上绕被阻塞时必须保留起点等待。把它改成“取最大可安全小前缀先走”会改掉原规则。

新代码每次 prefix 准入尝试都核对这一实际请求/活动状态，记录 `prefix_no_certified_group`，然后使用真实完整 mask/Index 检查和 PositionCommit 提交普通 full-cap 授予。ReferenceController 从零 cap 出发，只有中心提交后才调用 `install_cap` 和 `run`。这是原合同在该有限输入域的普通分支实现，**没有实现或运行通用 GROUP_ADMIT、围栏或部分 cap 扩展**。授权因子在本例不产生运动差异，不能用这张表推断一般 prefix 的价值。

## 选择器的可见信息与名义先验

`predict(route, public_view, opportunity)` 只取得两条公开路线、t=0 的 PositionCommit 视图及该格预先共同安排的观察机会。它没有 World、实际 Controller 或未来快照句柄，预测也不改变视图。候选与主执行共享非零误差半宽 1/5、固定足迹、273 个资源以及上一轮控制系数；blocker 的行为不随选择变化。

两种代价共用名义运动模型：delta=1、a_lo=2、a_hi=6、a_launch=1，名义 eta=-1，声明 blocker 在公共 native RUN 日程 t=0 启动。这里运行器也采用 eta=-1，因而是**匹配先验的人工实现**，不是从有界扰动合同推出未来真实运动的唯一值。只知道 cap 和误差界通常不足以得到确定的未来进度或等待。

名义单 MOVE 时间为 `D(L)=√(3L)`；名义 blocker 进度为：

- 至 `√(4L/3)`：`s_nom(t)=t²/2`；
- 此后至 `√(3L)`：`s_nom(t)=L−(√(3L)−t)²`；
- 更晚取 L。

预测证书下界为 `max(q_committed, s_nom(t_observe)−epsilon)`，其中公开精度 epsilon=1/100。真实几何与当前外部 owner 的交集经已有 `release_threshold::extract` 推得上绕第二段阈值 **61/20**，没有手填等待表。仅当预测下界严格越阈时，等待先验才设为 `max(0,t_observe−预计到达该段起点)`。本次两个机会均满足该条件。

基础代价只比较各段 D(L) 之和；解析等待代价比较沿路线递推的名义运动加等待。两者在执行前输出选择与两条候选预测。**预测只影响择路，不授 cap、不写 q、不释放 owner。** 真正释放仍需 blocker 在共同机会的真实同 MOVE Controller 状态形成 native 证书并经 PositionCommit 实际提交；未查运动不更新知识。25/8 与 24√2−28 这两个已知结果只在实际执行后作回归断言。

## 八格实际结果

以下每行均独立重建同一初态并执行所选路线。两种授权与两种代价在同一机会下共享恰好一次观察，包含所选下绕无需等待的格子。

| 唯一观察 | 授权 | 路径代价 | 事前所选 | 真实到达 | 真实等待 |
| --- | --- | --- | --- | --- | --- |
| 5/2 | 原 prefix 普通分支 | 基础运动 | 上绕 | 5/2+3√3 ≈ 7.696152 | 5/2−√3 ≈ 0.767949 |
| 5/2 | 原 prefix 普通分支 | 名义解析等待 | 上绕 | 同上 | 同上 |
| 5/2 | full-MOVE | 基础运动 | 上绕 | 同上 | 同上 |
| 5/2 | full-MOVE | 名义解析等待 | 上绕 | 同上 | 同上 |
| 4 | 原 prefix 普通分支 | 基础运动 | 上绕 | 4+3√3 ≈ 9.196152 | 4−√3 ≈ 2.267949 |
| 4 | 原 prefix 普通分支 | 名义解析等待 | 下绕 | 2(√3+√6) ≈ 8.363081 | 0 |
| 4 | full-MOVE | 基础运动 | 上绕 | 4+3√3 ≈ 9.196152 | 4−√3 ≈ 2.267949 |
| 4 | full-MOVE | 名义解析等待 | 下绕 | 2(√3+√6) ≈ 8.363081 | 0 |

每格实际完成 3 个原 MOVE 和 3 次 native END，requester 有 3 次 cap 安装和 3 次 RUN；blocker 另有 1 次初始安装和 RUN。上绕需 4 次完整初授检查（第二段证书前失败、证书后成功），下绕 3 次。所有格子的部分初授、cap 扩展、组准入均为 0；终点 resident 与 blocker 终点责任保留。到达由实际 ReferenceController 自主边界推进产生，闭式只在结束后核对。

t=4 的提前量为 `4+√3−2√6 ≈ 0.833071`。所有匹配先验的预测残差为零；这验证本例计算与接口连接，不是预测在未知扰动、迟到 RUN 或其它观察日程上的泛化证据。t=5/2 的下绕仅是本次未选候选，其实际完成证据仍见未改动的[上一轮配对时机记录](timing_run_20260924_01.json)，不冒充本轮执行。

## 实际命令与文件

从分支根执行的首次命令与当前源码重验命令为：

```sh
rtk proxy python3 -B exploration/error_guidance/run_prefix_precheck.py --source-root /home/lyh/MAPF_PIED_MDDR_RESEARCH --output exploration/error_guidance/prefix_run_20260924_01.json
rtk proxy python3 -B exploration/error_guidance/run_prefix_precheck.py --source-root /home/lyh/MAPF_PIED_MDDR_RESEARCH --output exploration/error_guidance/prefix_run_20260924_02.json
```

[源代码](prefix_precheck.cpp)、[运行器](run_prefix_precheck.py)、[当前源码完整记录](prefix_run_20260924_02.json)、[首次成功记录](prefix_run_20260924_01.json)。两次均严格编译/执行退出 0、2998 检查通过，没有 native 失败。第二次仅因去除新源码和运行器末尾多余空行而重验，使当前 SHA 与证据精确匹配；首次源和运行器可由当前各追加一个换行还原，旧成功记录未覆盖。后续复现必须换新输出名，运行器用排他创建拒绝覆盖。严格编译参数沿用 `g++-11 -std=c++14 -O2 -Wall -Wextra -Werror -pedantic -fno-elide-constructors`，编译上限 120 秒，单次 native 上限 60 秒。

记录保存完整 argv、退出码、stdout/stderr、源码/运行器/二进制 SHA，以及 **11 份既有包文件、9 份主线头与固定73正文的前后 SHA**，全部一致。读取的主线 HEAD 为 `ad3edd4f946e592cff12ff6426e0d31ba5cfd398`；头以原 source_pins.json 的独立 SHA 固定，只在临时目录原样复制，没有纳入分支。当前新源 SHA 为 `1ccbb1491f19fa19e4bb9736028df8257c1b3681191bf9f1af29884e5b3a32e7`，固定73正文 SHA 为 `b64f5b555034655b2676226d051a70c03aab3679d67c00bc334fb588c4811a8a`。

## 机制发现与剩余工作

这个后继把“事后发现某条路线快”推进为“公开信息加声明先验在执行前选择，并由真实组件执行验证”。在原 prefix 的普通分支下，**证据交付时机引起的等待仍能改变路线次序**；简单解析等待已经解释本例 t=4 的全部选择改善，当前没有需要学习才能解决的残差。

下一项若要识别部分 prefix 的独立影响，需要确实满足循环未授请求、A/B 几何与组准入条件的输入，不能把当前已授 blocker 临时改为组员。若继续评估解析预测，应优先保持同一选择器、加入一段任务续接及先验与实际运动不完全匹配的合法轨迹，观察后续责任、证书需求和真实任务结果，再决定是否需要校准或学习。

本轮仍为共同 native 前提下的有限机制运行：未验证生产 AUTH/END 消息服务，未积分二维扰动，未计规划、查询、维护与模型计算的完整费用；观察次数相同不等于实付费用相同。没有研究载荷、保护参数赋值、训练、guest 或生产服务运行。精确安全域与 native 前提沿用[原合同](RESEARCH_CONTRACT.md)和[时机报告](TIMING_PRECHECK.md)。
