# T1 单次有限完整任务清单（未授权、未运行）

2026-10-16。目的仅为验收已有 v2 闭式来源的两/三车自主事件循环、完整 END 和总费用；不是数值 world、独立 benchmark、学习或原作者优化器实验。87 项固定静态检查通过，C1 的63项回归通过；这不等于本清单已执行。四个活动分支服务同一问题，所有旧许可（含 G2c）不适用。

## 固定输入

| 项目 | SHA256 / 身份 |
|---|---|
| 本轮9文件清单 TIMED_MANIFEST.json | `9ec6de1cce0f62eefc24af9568796c338c6cdbe7a1f43d512e925d6cd2556c47` |
| timed_fixture.json | `cebd5e6f5d01771b55c7429ada5bae56ce8eefd71decf50ab77a110bc5013505` |
| 原 C1 composition_fixture.json | `21505bab2eceb3b86c311bf870d8c70b3c81621ff194466b3be25fc62681d68a` |
| 继承的旧输入 | 原集成21项、C1新增6项及固定 SADG 作者8文件，入口逐项核验 |
| 作者 SADG | `c2626d996121a9d6c128844a167b917db24418ac`，既有 R16 原版/AGPL 许可证据 |

本清单本身的 SHA 也必须写入新授权收据，防止预算变化；授权前用 `rtk proxy sha256sum` 计算，不自引用。全部 Python 文件、来源说明与执行说明的具体 SHA 见清单。入口要求现有 CPython 3.10+、stdlib和固定作者类依赖，不安装软件。三工作区和作者缓存均复用现有路径，不复制。

固定 A/B 路径、世界 [-2,2]²、已有 A_0→B_2、v2 车体/速度/加速度与共同输入时钟；第三车 C 从(-1,1.6)向东 .5 m 后永久 HOLD。每台车任务初态沿程 .02 m、横向 -.01 m、朝向 .002 rad，定位偏置(.009999,-.009999)m，完整任务不重置。初态的物理意义不随世界坐标heading而改写。每 .5 s 采集，另有启动 ACK 和最终 END；交付延迟 .1 s，相位半宽 .005 s、TTL1 s、命令执行延迟0。每次消息交付后按固定机器人优先级尝试尚未放行的链，两臂提议策略一致。

自主循环按反馈决定放行，**不硬编码静态夹具9.45 s的放行时刻**。其结果目前未知；不得把固定消息夹具的34.77/36.47 s写成此清单测量值。场景与参数检查前冻结，运行后不挑选/改参数追求正结果。

## 授权与命令

当前可以执行的只读输入检查（本次会执行）：

```bash
rtk proxy python3 -B /home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/spatial_constraints_s1_20261016/run_timed.py --check-inputs
```

另行明确授权本清单后，由执行窗口记录新的 `T1_AUTHORIZATION.json`，字段必须且只能为：`scope="T1_v2_four_children_once"`、`approved_by_user=true`、可追溯本次授权的非空 `authorization_id`、上述 `manifest_sha256`、本清单实际 `checklist_sha256`。本窗口不预填授权，不创建该文件；旧口头允许/旧manifest/旧授权ID不能复用。

授权后唯一顶层运行命令（本次不执行）：

```bash
rtk proxy python3 -B /home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/spatial_constraints_s1_20261016/run_timed.py --execute --permission /home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/spatial_constraints_s1_20261016/T1_AUTHORIZATION.json --output /home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/spatial_constraints_s1_20261016/timed_run_once_20261016
```

父进程依次仅启四个子进程：2_guard、2_SADG_events、3_guard、3_SADG_events。创建独占消费标记和唯一输出目录后，即使失败也不能删除后重跑。不允许绕过父入口直接调用 `task_child`；内部CLI也要求父收据和消费标记，并以各子目录独占 CHILD_STARTED.json 防止重复运行同一子任务。子进程使用 -B，不写入冻结模块的编译缓存。授权字段不是密码学认证，执行窗口仍须核对用户真正的许可。

## 预算、产物与失败

- 每子进程最长60 s wall、45 s CPU、512 MiB地址空间；四次合计子进程上界240 s wall/180 s CPU，父进程及系统调用少量开销另记，不声称硬实时总时限。
- 每任务≤40 s物理时间、≤1024个事件；每次区间查询≤4096格，停止细分阈值1/64 s，预算到达不降低精度继续放行。
- 每子进程总输出≤16 MiB：public.jsonl、evaluation.jsonl、result.json、process.log、CHILD_STARTED.json。进程单文件限制与日志合计检查均启用；超过总额保留并停批，不删除失败。四子进程≤64 MiB目标上界，失败越界如实记录。
- 总试次4，重试0，不加种子、不改变运动条件、不运行新的 world/solver/训练/查询或机器人。
- 输出目录保存授权副本、4个预登记任务行及 RUN_RECEIPT.json。异常无结果时保存 `PROCESS_FAILED_NO_RESULT`、exit/timeout、日志；后续未运行行保留为 `NOT_RUN_AFTER_STOP`，不从分母删去。

立即停当前任务并停后续子进程：SHA/条件不符、相位或消息合同破坏、覆盖违例、数值碰撞见证或接触不确定、时间/内存/输出超预算、任务超时或进程失败。区间交叠本身不计碰撞：阻止本次放行，继续等待合法反馈直至预定40 s；若始终无法放行则保留 TIMEOUT。不得把超时解释成全部安排无解。静态检查失败也不获得运行许可。

## 指标和退出决定

所有完整任务报告Σ实际完成时间（本地 END 确认）、makespan、起点等待、所有完成/未完成状态、截止删失指标；本控制器中途中无可调等待，制动/停稳由原语确定，不偷换成等待收益。反馈记录capture/delivery、消息数、字节和流SHA；真值/参考/控制单列evaluation日志，中心不能读取它。

连续安全依据全允许族区间分离证书；评估额外记录真实矩形的单时刻 SAT 内部交叠数值见证与覆盖违例。零见证仅限已检查时刻，不能当作独立连续证明。物理碰撞响应与数值 world 不在本轮范围；不宣称完成机器人仿真器验收。

费用报告父进程从spawn至退出的wall/CPU（含导入、构造、更新、控制、消息、日志、最终序列化），内部各段及区间格数另列，不把嵌套段相加。自有臂和作者事件适配臂使用同一证书、缓存和信息；作者包装层开销差不算约束算法创新。一对DEV测量不支持显著加速结论。

约束/选择、总计算成本和保证三个维度分别判断：当前静态结果前者相同、核心工作量相同、保证相同，总实耗未测。若运行只是验证同一证书的两种事件接线，结束**当前贡献候选**并保留接口；不因微小噪声或包装层差异扩实验。若出现分歧，先保留并诊断公平性/正确性，仍不自动增加运行。只有另有具体的约束算法或保证差异并形成新预登记，才可提出下一候选；不恢复旧查询学习或 LMAPF。
