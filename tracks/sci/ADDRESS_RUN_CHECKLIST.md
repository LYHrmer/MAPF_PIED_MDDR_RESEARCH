# 完整 ADDRESS 共同初解功能 DEV：本批已关闭

**执行补充：** 用户本轮明确授权后按本清单顺序执行，2项成功、第3项失败，立即停批；后三项未运行。零重试，原参数及JSON字节保持不变，剩余项目不能沿用本批许可。见[完整结果与失败记录](ADDRESS_DEV_RESULT.md)。下文保留授权前清单，历史“未运行/待授权”不再是当前状态。

本清单仅准备6项真实功能闭环，**未运行、未获本批科学运行授权**。旧两批SCI许可已消费，不能继承。原始用户指示优先于清单字段；先获明确授权，再逐项执行，任一失败即停止全批，零重试。没有恢复候选、训练、world或新初解求解。

目的：核验共同合法初解进入作者推荐ADDRESS配置后，能完成自适应邻域修复、最终全车校验和完整费用记录。它不是新算法比较，也不是独立泛化数据。旧Python固定ID组计时不作为此原生完整循环的公平配对成绩。

## 固定工件

- [清单JSON](config/address_common_initial_v1_manifest.json)，SHA256 `5f89443a8ad7e9281fffa74e8c9b47b1edf79c2a41203068057840046183bb3d`。
- 复用原六份完整初解：[输入](config/repair_residual_v1_inputs.json)，SHA256 `be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b`，不重采集、不重新规划初解。
- 原作者提交 `b3d35c431ce03834f95e834d87986f2f341394a1`；运行/构建文件SHA逐项登记在JSON。构建收据与二进制身份绑定，拒绝错配或静默重编译。
- 适配二进制位于工作树根`.address_adapter_build/build/address`，SHA256 `e14f8805270ac7a09ea748413274e8d1c6c163f79e806050691878bf20b7d11a`。不是旧SIPP桥，也不是原版完整二进制。
- 已执行`inspect`：六份旧路径完整合法、代码/输入/构建身份检查通过，均`search_executed=false`。功能性能仍待真实运行。

## 固定顺序与设置

| 次序 | job ID | top-K |
|---|---|---:|
| 1 | maze-32-32-2__s01__n16__address | 16 |
| 2 | maze-32-32-2__s01__n32__address | 32 |
| 3 | random-32-32-10__s01__n16__address | 16 |
| 4 | random-32-32-10__s01__n32__address | 32 |
| 5 | warehouse-10-20-10-2-1__s01__n16__address | 16 |
| 6 | warehouse-10-20-10-2-1__s01__n32__address | 32 |

共同seed=0、RandomWalk、bernoulie、PP/SIPP、邻域上限8、最多16次已构组修复迭代。小任务采用`K=min(32,n)`，明确区别于原论文默认K=32。保留作者原尝试级奖励及回滚；不静默改成完整接纳奖励。构组失败可能不增加修复迭代数，仍由时间/CPU监督约束，不能把迭代上限说成固定计算量。

每项成功结果的总准入预算15秒，从Python入口计入导入、输入/身份检查、进程启动、构造/距离表、修复、原生末检、输出、外部全检、结果写盘和产物哈希。内层末检预留0.25秒、外部末检预留0.5秒。worker/native分别CPU≤10秒、地址空间≤512 MiB、单文件≤16 MiB。

worker/native进程组有剩余wall硬监督；父进程I/O不受它抢占。**整条命令另用`timeout`在20秒发TERM、再留2秒强制回收，最迟22秒终止**。6项命令保护合计最多132秒；单项超出15秒成功准入即记失败，不把多出的回收时间当可用优化预算。最后管理收据写入和进程退出在准入计时之外单列，不称整个进程退出耗时。

## 命令与停止条件

从`/home/lyh/MAPF_SCI_RESEARCH`执行。以下命令只有在真实用户授权本清单后才可运行；逐项替换上表job，保持顺序，每项核验成功再进入下一项。

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 20s python3 -B tracks/sci/run_address_adapter.py run \
  --manifest tracks/sci/config/address_common_initial_v1_manifest.json \
  --sha256 5f89443a8ad7e9281fffa74e8c9b47b1edf79c2a41203068057840046183bb3d \
  --job maze-32-32-2__s01__n16__address \
  --authorization-reference '<真实用户对本清单的授权原文与范围>'
```

输出根`tracks/sci/results/address_common_initial_v1/`目前不存在。每项独占目录先写attempt，随后保留共同初解、地图、作者stdout/stderr、native收据/路径、外部结果与总收据及其SHA。失败或中断不删、不覆盖、不创建另名目录重试；即使终止前未能写末收据，也保留partial目录并登记失败。

以下任一发生即停全批：代码/输入/二进制身份变化，旧目录已存在，原生退出非零，超时/强制回收，缺路径/收据，末检冲突/漏车/端点改变，SOC劣化，费用字段缺失或超准入预算。不得修好后沿用本批剩余许可；先保留失败并报告。

零改善本身不是软件失败，继续记录其完整费用；它也不证明恢复候选无效。全部COMPLETE后，仅报告完整功能结果。恢复机制对比需另冻结代码、同框架原方法/随机重排/优先级搜索对照与同总预算，先满足实现条件再申请新授权。
