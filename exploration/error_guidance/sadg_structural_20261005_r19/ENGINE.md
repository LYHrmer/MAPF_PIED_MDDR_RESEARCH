# R19 作者优化器适配接口

`Simulator(case, disturbance, seed, predictor=object, config=EngineConfig(...))` 接收原 R18 case 和扰动格式。`run(policy, probe_override=None)` 的调用方式不变。`EngineConfig` 继承 R18 参数，新增必须提供的 `evidence_dir`；整个矩阵应共享该目录和 `cache_dir`。`run_study.py` 的构造接口已只读核对。

默认 `HistoryPredictor()` 精确使用完整已交付 END 历史比率。外部 `DurationPredictor(model_path, mode=...)` 可直接传入，支持冻结 `learned` 和 `ewma03_survival` 等模式；engine 没有硬编码预测器种类。没有新训练或测试集选模逻辑。

`StructuralStopPolicy()` 只接收公开 snapshot。候选须仍 IN_PROGRESS，且从当前顶点沿公共活动 DAG 可到达合法、在作者 horizon 内的可切换组尾部，或其他当前被阻塞 cursor。该可达性是结构机会，不保证查询有收益。评分为 `(history_cv + overdue + observation_age/expected_duration) × (legal_group_count + blocked_frontier_count) × urgency`；`urgency=1/(1+minimum_public_path_time/solve_period)`。没有结构机会或没有正分则返回 `[]`（STOP）。路径时长忽略 AND 等待，不是真实 ETA。

原 R18 的物理演化、私有扰动生成、连续 WAIT/MOVE/GOAL、cursor、capture/delivery、承诺与 adoption guard 均从固定 SHA 源码继承；原作者 `SADG.optimize` 与内部 60 秒上限不改。当前动作的输入字段将预测残余显式编码为 `duration × (1-progress)`；STAGED 时长为作者原 nominal 乘公共 future ratio。残余并非执行许可或安全上界。

同 occurrence 的已交付 POSITION 统一覆盖当前残余：`max(0, (1-captured_progress)*original_nominal*all_history_ratio-age)`。future ratio 仍由所选 END 模型给出。无 POSITION 时使用所选预测器。每次 context、输出、provider 切换和编码均留存，不宣称这是联合条件后验。

## 无损证据和审计桥接

`EvidenceStore(root).get(ref)` 读取对象，`get_graph(ref)` 无损恢复完整 R18 `graph_snapshot`。ref 包含内容 SHA256 与相对 gzip 路径；读取时检验原始 canonical JSON 字节哈希。图拆为静态拓扑、顶点状态、组方向状态，before/after 相同部分只存一次。

- episode：`initial_graph_ref`、`prediction_evidence_ref`、`evidence_store`。
- gate：`public_snapshot_ref`、`capture_graph_ref`、`prediction_keys`。capture 图与 0.25 秒后 solve 图分别留证，额外图 ref 不进入 policy callback。
- solve：`before_ref`、`candidate_ref`、`after_ref`、`model_ref`、`author_log_ref`、`prediction_keys`；原 status、objective、bound、row/bound/integrality 残差仍在 `model`。
- `expand_episode(result, store)` 恢复旧形状的 `initial_graph` 与 gate `public_snapshot`，供独立审计沿用。物理事件和轨迹仍完整保留在 episode。

缓存键绑定完整优化器输入图、horizon、作者/适配 compiler 哈希、原作者语义版本与 60 秒上限。成功和失败均缓存原观察结果；失败命中继续采用父图，不重试以寻找成功。reference 时间继承、新实际工作记 0；不能将缓存顺序当成方法加速收益。同 key 并行 miss 仍可能产生重复实际调用；原子文件写保证读取完整，不提供进程间 solver 锁。

所有失败也保存完整变量、上下界、约束系数/常数/方向、目标、返回值及原错误 traceback。没有 incumbent 的值保持 null，非有限浮点显式 tagged，不能伪装成有效零值。独立 `audit_solver_payloads.py` 只读 decimal 重算失败的约束/界/整数性与父图保持，不导入 engine，不调用 solver。

R18 既有 11 次拒绝、5 个唯一输入缺少失败模型完整 payload；R19 新 schema 不会补造旧变量值或改写旧结果。旧缺口保持在原独立审计的说明中，未经另行授权不重跑这 5 个输入。

## 机械资格与限制

`r0/VALIDATION.json`：15 项、2 次真实作者调用（人工单动作 history 与 learned），另有明确标记的合成拒绝模型 fixture，零 native。`r0/CAPTURE_VALIDATION.json`：9 项、0 次新作者调用，验证 capture 绑定、结构可达、STOP、承诺头拒绝。原两次调用之后只增加了 capture 证据字段；完整原记录保留，追加检查精确复用缓存。

这些是 R0 接口资格，不是新科学样本。没有额外 TEST pilot 或大矩阵；数据、科学预注册、模型冻结与运行由 root 管理。执行范围仍是固定路径、连续点事件模型，不覆盖 ROS 物理栈、机器人足迹/加速度、LMAPF 吞吐或生产收费。
