# 已提交查询快照的数据接口草案

2026-09-24；状态：**只读源码核对后的设计，未实现导出器，未运行 C++ 桥或研究实验，未读取实验载荷/旧结果。** 主线源码根为 `/home/lyh/MAPF_PIED_MDDR_RESEARCH`；下文 S01 等编号对应文末逐文件 SHA-256。源码存在不等于接口已接通、真实数据已取得或科研结论成立。

以上保留 `5ff3f20` 时的审查状态。后续已在孤立源副本实现并运行[组件导出验证](COMPONENT_VALIDATION.md)，接口子集见[组件schema](COMPONENT_SCHEMA.md)；本页关于生产外层发布、实际query/结果关联及计费缺口仍适用，不能将组件fixture改称生产数据。

## 1. 可用来源与真正的提交边界

最窄来源是中心已有的 `PositionCommit::View`，而非物理世界快照。该 View 保持不可变根及其引用的寿命，公开 `structure()`、几何快照与轮询游标，但不暴露可变 Scheduler（S03:59–85、132–133）。导出结构只需 `structure()`；不要为方便导出而接入真实控制器。

**不能把每次 `Scheduler::commit` 当作生产记录触发点。** `PositionCommit::prepare_admitted_update` 和 `prepare_position` 内部已经对私有后继调用该方法；代码明确指出这些嵌套提交尚未对外发布（S03:135–161、184–225）。生产事件须关联 `CenterService::commit_at_opportunity()` 最终返回 `Granted`、完成外层根交换和发布结束的事实；`Starved`、`Rejected`、过期或仅 prepared 的记录不能更新已提交数据集（S05:292–331；S04:314–322）。这是一项未来接线要求，不是在提交临界段内增加未计费回调的建议。

区分三个时点：

1. **选择输入：** 在 `select()` 调用已有 `bridge_.choose(prepared_at)` 的同一提交视图下，保留合法输入快照与选择时刻（S05:178–185）。此时还没有实际发布的 query。
2. **实际发布：** 成功发布后，将前述冻结输入与实际 query/request/MOVE 身份关联；仅选择、封存请求或准备 outbox 不等于已查询。CenterService 已核请求、实际选择、几何五字段、source/profile/epsilon 和 block/session/center 身份（S05:193–226）。
3. **后继证据/费用：** POSITION 成功提交后才能进入下一决策的证书历史；Collector 与 Position 的组合提交成功后，收据才进入下一决策报价（S06:155–179、183–222）。当前查询释放/运动不等待费用树封口。

`CenterCommitBridge::View` 已有只读 `events()`、`published(query)`、`first_success(query)`（S04:101–119）。PublishedRoot 保存发布身份与时间；FirstSuccess 保存 query 根、sample/receipt_key、捕获和提交时刻（S07:42–60）。**FirstSuccess 不含证书 lower 或完整决策快照**；不能单凭它训练跨阈值标签。应在同一次成功外层提交后，关联已准入证书的只读结果。当前精度历史与该证书的 lower/captured/delivered 被强制相等，不能拼接另一份观察（S03:394–408）。

## 2. 最小记录契约

以下是建议的数据格式，不声称已有对应 JSON API。身份字段用于关联/审计；不得无区分地作为学习特征。

| 记录 | 最小字段与来源 |
| --- | --- |
| 决策快照 | schema/version、来源种类、源码 hash、run/block/session/center、`view_id`、选择时刻、policy、Choice generation、游标、导出序号。结构 View 来自 S03，Choice 来自 S01:94–110。选择发布可能保留同一 view 标签却更换实际根，故不能只用 `view_id` 去重（S03:230–236）。导出序号是待实现的日志身份，不是新增公共服务机会。 |
| 活动 MOVE | 完整 action key、agent、source、profile；绑定的 geometry_version/number_encoding/coordinate_frame/distance_unit/move_occurrence；q、b、epsilon 或显式缺失、eligible。取 `structure.actions[key]->input`（S02:36–44、93–98、330–349）。key 与 move_occurrence 必须一致；b 是中心授权上界，不是本地已安装 C。 |
| 需求和关系 | demand key、agent、requester_action、joined/可选 joined_row、non_owner_eligible；完整 relations 中每个责任 owner、action、retirable、kind、可缺失 threshold；保留所有非活动/终点/不可退休责任。取 S02:45–67、397–431。不可过滤后再计算 owner 数。 |
| 一跳权重 | 初始需求 w=1；前缀需求 w=1+out[requester_action]，保留 out 或记录该派生值；不是自由填写的训练权重（S01:484–507）。 |
| 证书历史 | 当前 MOVE 最近两个不同捕获时刻的合法记录：action/source/key/provenance、完整 binding、captured/delivered/lower/epsilon/cap_at_capture。公开输入类型在 S01:28–32；时间及身份核对、代表选择在 S01:249–284。只保留已提交且 delivered≤选择时刻的信息。 |
| 历史费用收据 | profile/source/key/provenance、epsilon、published/captured/committed/delivered/charged_work、工作单位/计费归属版本、实际安装事件。公开类型在 S01:35–39，最新兼容选择在 S01:285–309。派生 pre=captured−published、post=committed−captured；报价分母仍需正总历时（S01:465–482）。 |
| 发布/返回结果 | 实际 query、request_business_id、样本/收据/接收 job、发布行、完整 MOVE/source/profile/binding、实际发布/捕获/交付/提交时刻、合法状态、原始证书 lower、精度、失效/失败或尚未终态原因。query 关联用 S04:270–307、S07:42–60；标签只在后处理结果表，不能回填决策特征。 |

当前公开 `Choice::score()` **只返回获选者**的 A/P、乘积分母、预测及部分平分字段；没有全候选评分、原始历史或拆分费用（S01:46–59、106–110）。`Scheduler::State.histories/receipts` 是私有字段，无公开 getter（S01:67–80）；`PositionCommit::View` 也不暴露它们。若直接导出这些已提交历史，需后续最小只读投影；另一方案是镜像外层成功提交的证书/收据事件并严格复现保留规则。后者不能仅截获普通 Delta：生产 POSITION 的 Delta 在 `prepare_position` 内部构造。

RR/COUNT 本来跳过历史/报价保留与 SRDC 关系维护（S01:145–154，S02:397–403）。不能给其在线执行免费补图。离线审计可另表保存当时合法字段，但须区分原策略实际使用状态和影子派生状态，并单列导出/派生成本。

## 3. 精确数域与不可进入特征的信息

主线 `FlintReal` 采用实代数数，不能默认每个值可由 Python `Fraction` 表达。**已有可复用出口**：`FlintOps::is_rational` 和 `copy_rational`，非有理数返回 false 且不近似（S08:153–163）。草案第一版可只接受成功精确导出的 numerator/denominator 十进制字符串；其余记录标记 `unsupported_number_domain`、保留身份与数量，不静默丢行后宣称覆盖完整系统。未来代数数桥或带认证区间的特征接口须另定义；不能通过字符串截断/中点替代严格阈值判断。

下列信息不得进入当时的模型特征：世界真实 s/速度、实际 w/eta、未来延迟表/seed/任务、未被算法合法取得的本地 cap C 或控制模式、未提交的后继结构；当前查询未来的捕获/回传时间、结果 lower、实际成本、成功/吞吐结果。已发生但尚未交付/提交的信息也不能提前用。证书 lower 是可信下界，不是真实位置；以历史 cap 裁剪的 midpoint 只是预测构造。

q、owner 和历史必须来自同一已提交状态。POSITION 路径会同步推进 q 和退休 owner，再附入同一证书的精度记录（S03:184–225、394–408）；不能用“新历史＋旧 q/owner”制造训练样本。对已提交历史，相应 lower 不得超过同 MOVE 当前 q。已知 nonretirable、缺阈值、b≤theta、其他准入条件不满足仍由规则屏蔽，不能交由模型猜测。

## 4. 标签、分组与缺失

每个训练实例由**发布前冻结的决策输入、需求关系及 theta**关联一个实际发布 query。合法匹配返回后，标签为 `certificate.lower > frozen_theta`；不能改用后来的 theta、q_after、真实 s 或结果到达时外推的位置。当前一次查询可涉及多个关系阈值，样本必须共享 query 分组；网络副本/重传不能变成独立样本。实际退休、准入、运动和任务服务另列机制/结果表，不当作同一标签。

仅被原策略选择的候选有返回标签。未查询、未发布、pending、无效返回均不填0；有效返回但未跨阈值才为0。截止时未终态属于右删失；已确认失败可供另一个响应成功/失败任务使用，但不混进“条件于合法返回”的跨阈值标签。保留所有状态、失败费用和观察截止，报告条件训练覆盖率。只有成功收据的成本回归同样存在选择偏差与删失。

训练/验证先按完整 run/block 分组，再按地图/来源做所需留出；同 query 的多阈值、同轨迹重复决策、同原始实例复制不跨集合。ID 只是可实施分组的依据，不自动证明独立性。实际记录原行为策略；若随机化不存在，不伪造 propensity，也不能据确定策略日志声称无偏评估新策略。已有两 MOVE 冷启动实例不足以训练或判断泛化。

## 5. 已有记录能力、最小下一步与当前阻碍

本轮只读核对到以下可复用源码，未查看其运行日志：

- **组件夹具：** `query_native.cpp::World::apply` 在 Scheduler commit 成功后镜像 facts/evidence/settlements，可参考提交后的事件保留方式（S09:195–228）。但全部来源/收据是人工 admitted-input test double，部分评分状态刻意不可物理到达；只可用 `reachable_prediction()` 等一致状态检查接口语义，不能称真实数据（S09:9–17、333–357）。未核其远端公开发布状态。
- **原生机制日志：** 最小循环确在 PositionCommit 外部提交后输出日志，但标明 `native_snapshot_not_AUTH`、无成本收据；同条日志含 `captured_s` 这一世界私有真值，必须排除。`value_text` 输出认证包围区间文本，并非 exact Fraction 序列化（S10:59–64、138–176）。现有事件缺完整选择前快照和全部候选，不能直接当训练集。
- **生产事实：** Bridge 的 Published/FirstSuccess 记录可关联实际 query，但缺 lower、全候选和完整历史；ReceiptInstallation 可取得实际 pending receipt，只有其组合提交成功后才可记为已安装（S04:101–119，S06:70–73、155–222）。pending accessor 不提供提前使用权。
- **完整驱动记录器：** `full_query_driver.cpp` 已写 closed_segment/job_total/完成或失败诊断，重点是费用与固定业务状态，不是上述学习快照（S11:132–142、200–221、408–438）。最新主线进度仍写明完整查询没有运行证据（S13:18–33）；不能从这些 printf 推断已有真实训练日志。

最小真实接线依赖为：①选择输入与实际发布 query 的同根关联；②在外层成功提交后保留合法证书/实际安装收据，并公开必要只读历史投影；③以 `copy_rational` 明确数域支持及拒收原因；④把冻结输入、后继结果、成本和分组身份分表输出。先验收一条来源明确的导出链与主线选择/证据一致性，再讨论数据规模和学习优劣。原生夹具仅能做这条链的语义检查，不能替代真实来源。

尚未具备上述导出器、完整 query 结果关联、一般实代数数到 Python 的桥、真实全费用数据和新策略覆盖。离线读取记录不能反向改变执行；若未来在线使用模型，特征提取、模型推理、关系维护、记录复制/保留/回收均需明确实际成本，不把宿主耗时自动折成 B1。主线现行入口保留只实现/静态检查、受限输入与冻结范围边界（S12:3、9、117）；本草案不更改这些边界、不提出新的权限流程，也不以存在旧组件授权推断完整研究运行已获准。

## 6. 本轮来源指纹

以下为主线文件的完整 SHA-256；行号均指这些字节。读取范围限上述相关窗口或定点搜索，不宣称逐行审计整个文件。

| ID | 主线相对路径 | SHA-256 |
| --- | --- | --- |
| S01 | `implementation/pie_query/include/pie_query_scheduler.hpp` | `a1572501e39b711b9c8253e05083aa5799884145263d81352c9d71fd1965fefb` |
| S02 | `implementation/pie_query/include/pie_query_index.hpp` | `936a30e4e19c85977ab187181dbe59130daffb49c71a60b41ba28d5c3c348c70` |
| S03 | `implementation/pie_position_commit/include/pie_position_commit.hpp` | `2f7be5ec11293df2fdbda3919393f8a30b43b2a432f56879e59f26d0a3b9d7c6` |
| S04 | `implementation/pie_center_writer/include/pie_center_writer.hpp` | `4f55ccd61721efbc7e92a3ec3ed408a2c013668f22a936bc0fa835286b7e4076` |
| S05 | `implementation/pie_station_query/include/pie_center_service.hpp` | `008d734de2dfa52ecff4fd3d7e9bb243d574345532bda692645ba9463d120d3d` |
| S06 | `implementation/pie_query_receipt_install/include/pie_query_receipt_install.hpp` | `e23ff0a2f505863c7a43bbc5ecbbad104fd4c4c9781f40e09252c3f6580003aa` |
| S07 | `implementation/pie_query_cost_collector/include/pie_query_cost_collector.hpp` | `fddcd1551b9a2084dc3c0ae7cf1ae13b60703645e953d5cb058aa36e4361a280` |
| S08 | `implementation/pie_geometry/include/pie_geometry_flint.hpp` | `239040d62285b5f370233b9732824ea6ff2747193c8ad404f8ef93498a806900` |
| S09 | `implementation/pie_query/tests/query_native.cpp` | `200b9adb81a106bc4ddcaafc8be3bd9086b5a6d831b77c1cbba15d869731b003` |
| S10 | `implementation/pie_minimal_loop/minimal_loop.cpp` | `0add68357d352e68b96942c77278454859f689d77b8123c010dd6fce05e7305f` |
| S11 | `implementation/pie_station_query/full_query_driver.cpp` | `95a153515018ddf8d81b6081ed977172472a6728eb3ced781b2013c2ba2a61b9` |
| S12 | `.github/README.md` | `98aeefde6a5c8f209f9c0b2edb000659961be1e792b315555a2397697540fb9c` |
| S13 | `GITHUB_PROGRESS.md` | `2928d5ad57322606ccc5750913600cfe24f8685c6c4a4fbaa8b3ccbb19fd9589` |
| S14 | `implementation/pie_query/README.md` | `d67b60470935ddc13b32ce6d827540c4bc3a4fc0711bd88d8ba200767c704ecb` |

费用口径补充依据为 S14:59–76：`Receipt.charged_work` 是实际查询归属工作，不能误接 STRICT 整行收费；原生产信息准入也不能由本草案或公开 Python dataclass 替代。
