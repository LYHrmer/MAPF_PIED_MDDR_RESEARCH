# 两项初始运动认证：预算可行性验证

2026-10-25，**本批已执行并关闭，不可重用许可**。maze在20秒初始认证事务中因依赖构造超期未获证书，random为`NOT_RUN_AFTER_FAILURE`；零重试，候选评价和新搜索均为0。完整结果见[初始认证报告](INITIAL_CERTIFICATION_RESULT.md)，失败/未运行原始产物见[总收据](results/initial_motion_certification_v1/RUN_RECEIPT.json)。下文保留执行前冻结的范围、预算和历史命令；后继收益比较门槛未通过。

本批只回答已固定32车完整初解能否在现有20秒初始认证软限内建立完整名义证书，以及费用消耗在哪个阶段；**不评价候选、不比较收益、不运行新ADDRESS搜索、训练、world或误差模型**。此前31项人工软件检查及固定输入静态检查已完成。

本轮真实用户指示为：“验证SCI新旧预算合同的实际行为，以及硕士初始认证的预算可行性，再开展收益比较”。下列两项数量和资源限制是本轮据此制定的执行安排，不能写成用户曾逐项指定这些数字。新指示不复用任何消费许可，也不自动授权后继收益批。实际执行时原文与安排记录入本批AUTHORIZATION；记录文件本身不是授权来源。

## 固定输入、代码和范围

- [manifest](config/initial_motion_certification_v1_manifest.json) SHA `2fd0f0a96746d1d1ad10fa5493d5b1ed5d1c866f924493125e230dc7e29e4492`；运行代码逐文件SHA在manifest中固定，科学提交 `1e74ba0b600fe0019f3e76d33314e5c0f19c8281`。manifest冻结字节不因运行结果而改写。
- 输入来自既有 [motion_acceptance.lock.json](motion_acceptance.lock.json) 固定的SCI证据提交 `f9c651ad0680679cf99a4973f722b65fd6f7aa97`，输入对象SHA `660b7bc4b4282db1feedd373a9220dc98638c18bcb835123aff448c83eadcf3e`。这是ADDRESS旧批共用的完整初解，不是新的优化结果。本模式只读取该输入对象，不读取final候选对象。
- 依次为 `maze-32-32-2__s05__n32`、`random-32-32-10__s05__n32`，各只认证原完整32车方案一次，不投影或缩短任务。运动参数、初向和固定局部依赖调度完全沿现行名义接口；不换调度器。validator、SharedBudget、supervisor仍固定SCI `535ee1a`。
- 旧接纳器提案与旧锁/结果不变；因新窄入口及阶段计费改变当前源码，旧收益提案以后只能在其冻结`34d0cac`代码恢复，不能把本批SHA塞回旧manifest。

## 时间与失败合同

| 口径 | 每项限制 |
|---|---|
| 原初始认证事务软限 | ≤20秒：内部快照、完整初始构造/检查、私有证书状态序列化 |
| 整项准入 | ≤26秒：输入/Git读取、导入/problem设置、上述事务、证书导出/写盘、哈希与监督等待 |
| 收尾保留 | worker输出2秒，父进程验收/哈希2秒 |
| worker资源 | CPU≤24秒、地址空间≤512MiB、单文件≤16MiB |
| 外层命令保护 | 28秒TERM，再2秒KILL；两项外层合计≤60秒 |

父进程传递绝对准入截止。事务实际截止为 `min(事务开始+20秒, 父绝对截止−4秒)`，准备阶段侵占只会缩短而不会扩大20秒；实际可用纳秒原样记录。准备费用不在20秒事务子区间内，但计入26秒完整准入。SharedBudget只提供wall软截止，CPU由固定supervisor硬限制。旧离散validator内部和个别Python/序列化调用不可协作抢占，外层保护仍必要，不声称任意规模硬实时返回。

**零重试；任一初始认证未成功立即停止整个硕士批。** 包括正常预算截尾、充分分离未建立、成环，以及实现异常、硬退出/强杀、超限、缺产物或SHA漂移。第二项必须记为`NOT_RUN_AFTER_FAILURE`，不换任务、不补跑、不延长20秒。诊断正常产出与认证成功分列：可正常记录“20秒内未建立证书”，但它仍是预算可行性负结果，不能返回未认证初解作为安全fallback。圆外包未分离不等于真实车身碰撞。

## 执行入口与产物

先运行静态检查；此命令不构造任务或运动日程，已返回`PINNED_INITIAL_INPUT_ONLY_NO_CERTIFICATION_OR_SEARCH`：

```bash
rtk proxy python3 -B tracks/thesis/compare_nominal_motion.py inspect --manifest tracks/thesis/config/initial_motion_certification_v1_manifest.json --sha256 2fd0f0a96746d1d1ad10fa5493d5b1ed5d1c866f924493125e230dc7e29e4492
```

以下是原顺序命令，仅供复核，不能再次执行：本轮第一项已运行一次，第二项因第一项未获证书而关闭。实际命令和授权原文以[外层记录](results/initial_motion_certification_v1/OUTER_EXECUTION.json)及[授权来源记录](results/initial_motion_certification_v1/AUTHORIZATION.json)为准。

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 28s python3 -B tracks/thesis/compare_nominal_motion.py run --manifest tracks/thesis/config/initial_motion_certification_v1_manifest.json --sha256 2fd0f0a96746d1d1ad10fa5493d5b1ed5d1c866f924493125e230dc7e29e4492 --case maze-32-32-2__s05__n32 --authorization-reference '2026-10-25用户：验证SCI新旧预算合同的实际行为，以及硕士初始认证的预算可行性，再开展收益比较'
rtk proxy timeout --signal=TERM --kill-after=2s 28s python3 -B tracks/thesis/compare_nominal_motion.py run --manifest tracks/thesis/config/initial_motion_certification_v1_manifest.json --sha256 2fd0f0a96746d1d1ad10fa5493d5b1ed5d1c866f924493125e230dc7e29e4492 --case random-32-32-10__s05__n32 --authorization-reference '2026-10-25用户：验证SCI新旧预算合同的实际行为，以及硕士初始认证的预算可行性，再开展收益比较'
```

产物独占 `tracks/thesis/results/initial_motion_certification_v1/<case>/`，存在则拒绝覆盖。保留attempt、worker日志、完整 `initial_certification.json`（成功时含完整证书，失败时含结构化原因）、result、receipt及外层退出记录；主窗口汇总全部成功/失败/未运行终态。候选评价与搜索计数必须为0。

同一SharedBudget新增嵌套阶段计费，不改变调度规则：离散检查/块构造、依赖建图、释放时序、依赖复核、区间几何和完整证书；记录首次失败的最深阶段。阶段费用嵌套，不能相加冒充总时间；源码checkpoint首次观察到截止不等于精确越限瞬间。软件证据见 [initial_certification_software.json](derived/initial_certification_software.json)。

## 进入后续比较的条件

两项均按原限完成、完整名义证书/费用/输入身份核对通过且无异常，才能认为这两份初解的初始化预算条件在本次观测成立。它只解除初始化缺口，不证明20秒还能完成候选评价，更不是接纳器收益。应按实测初始化费用及剩余时间明确下一有限比较的预算；没有容纳完整候选认证与收尾的证据时，先收缩问题或另提明确预算，不直接执行旧收益清单。

若到期，先利用已记录的具体阶段判断瓶颈，不反复追加seed或静默延长时间；如果主要是共同构造/复核成本，按工程基线处理。新收益比较仍需独立固定输入、代码、费用与停止条件，由实际后续指示决定执行。
