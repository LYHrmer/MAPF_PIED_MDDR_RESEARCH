# 73L23：获准四类首个公开配置的有限静态核验

2026-09-12；根 /root；本次有限输入静态核验已完成，不是正式审查、运行记录或完整来源资格票。用户本轮明确允许固定官方提交中每类首个配置及其引用地图、起点、任务、延迟文件的有限只读静态核验。该授权已覆盖本次实际读取，不再沿用“等待读取许可”的旧状态；其它载荷与旧Q结果仍不读取。

固定来源为YueZhang-studyuse/LMAPF-delay@0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。按读取正文之前确定的规范相对路径字节序，每类只取首个JSON；不按队伍数字自然排序，不因检查结果更换候选。四类目录元数据各列91个JSON，树truncated=false；这是目录数量，未读其它360个配置正文，不是全量来源调查。

| 类别 | 首个配置（相对lifelong_benchmark） | Git blob | bytes |
|---|---|---|---:|
| city | city/agent-1000_scen-delay-0.001-1.json | 25dc6add2b38d327ab14d4cc0b575f19554b5a1f | 266 |
| game | game/agent-1000_scen-delay-0.001-1.json | 711c214ccca037ec3ab1db0b62fc3a9f3c662f00 | 267 |
| random | random/agent-100_scen-delay-0.001-1.json | 726ff752521cde5d6733606eaf8cd252fdb147c8 | 267 |
| warehouse-s | warehouse-s/agent-1000_scen-delay-0.001-1.json | 08780335bbf47208eee965c7d0693eb3d285be40 | 277 |

四份JSON已完整取得并解码，均为roundrobin、numTasksReveal=1，四种地图正是L18/L19具名对象；city/game/warehouse-s的teamSize为1000，random为100。上述数字仅描述已有公开文件，未采用为density N、实验规模或其它保护参数。四份均引用同一个规范路径lifelong_benchmark/delay/delay-0.001-1.txt；实际引用闭包为四map、四agent、四task和一个delay，共13个不同对象。配置numTasksReveal不覆盖原driver的commit_window→reveal规则。

根负责对象/输入静态核对；source_service_audit只核解析器及必要前置条件；Opus建设题仅据实核证据构造delay与共同ACTUATOR的衔接方案，建设建议不计正式通过票。当前尚未实例化roster、source_id、参数、O或其它实验载荷，也未实现、构建、测试或运行规划/仿真。

工具记录：网页打开固定GitHub树返回Cache miss，无正文；普通gh树请求因沙箱无法连127.0.0.1:7890而exit1，正常升级后db2844/exit0取得完整目录JSON。该次展示过长，根从实际完整返回值解析并只提取四个首项，没有把截断展示当完整人工阅读。四份配置contents终态83d197/4c5526/a44682/1534db均exit0。

## 实际完整读取与静态检查

13个引用对象均从固定commit的raw端点完整读入内存，未缓存原载荷到文件；逐对象重新计算Git blob（带blob长度前缀）与固定树匹配，另算SHA256。四份JSON也从API正文重算Git blob一致。引用规范化后都仍在lifelong_benchmark内；树对象均为普通blob而非符号链接，map虽有可执行mode也未执行。读取字节完整不等于人工逐字符观看：地图/位置/矩阵由本次纯静态解析覆盖，根核验完整汇总输出。过程没有调用原研究入口、规划器、仿真器或测试套件。

静态方法：按已读Grid的header与@/T障碍解释核矩形；按位置reader核计数与单token十进制位置、int32可表示性、足数、起点唯一性和通行性；对地图做四邻接连通域划分，核全部起点/任务所在分量。连通域划分只检查静态图性质，没有求多机器人轨迹或运行论文算法。矩阵逐行核token数和0/1，未估计生成分布。

| 类别 | 地图height×width | 原teamSize/实读起点 | 原任务记录 | 可通行格数 | 所有引用位置的共同分量大小 |
|---|---:|---:|---:|---:|---:|
| city | 256×256 | 1000/1000 | 50000 | 47240 | 47096 |
| game | 270×133 | 1000/1000 | 50000 | 8959 | 8959 |
| random | 32×32 | 100/100 | 12500 | 819 | 819 |
| warehouse-s | 63×161 | 1000/1000 | 50000 | 5699 | 5699 |

四类均满足：地图精确矩形、agent/task声明数与实读数相同、位置行均恰单token、无空记录、位置无越界/障碍、所有起点互异、全部起点和任务位于同一可通行分量。city整张图有34个分量，但本次引用全部落在大小47096的同一分量，不能把“整图非连通”误作该配置非法。game/warehouse的尺寸顺序在实际header中已明确，这只解开R0正文维度，不证明与官网另一对象同字节。

这些检查建立的是四个已指定配置的基础网格/位置输入存在且可解析，不是全部364配置合法，更不选择它们为正式实验规模。相同任务位置可能多次出现，roundrobin会生成不同任务实例，本次不按位置去重或删任务。四类均未出现LoRR多errand被R0只读首token的问题，但不外推其它任务对象。

## 延迟文件的实核与原生边界

共用对象的首行实际为`5000,53983`；后有5000行，每行恰2000个0/1 token，共53983个1。原reader只消费首行第一个token作为max_team_size，不把第二个token当列数。第二token恰等于本次统计1总数是内容关系，不是已证生成器规范；文件名中的0.001也不是本次已证的Bernoulli概率，不能由经验比例推独立分布或称文件标错。

原入口只读前teamSize行，故这四配置分别需要的1000/100行均存在；所有实际可用列宽为2000。固定消费者取D[i][current_time+u]，每次整个commit_window都须落在零基0至1999；边界条件是原调用的current_time≥0、commit_window合法且各current_time+u<2000（算术亦可表示）。未绑定commitStep/时间窗口，也未运行源，故这里只给具体已知支持宽度，不能判某未来native运行不越界，更不能自动把模拟时长设为2000。

原driver实际set_num_tasks_reveal(commit_window+1)，忽略本次JSON的numTasksReveal=1。这一字段只能作原文件记录；把1直接用作native有效深度会改变来源语义。Inf的counter/任务实例表示、sync_shared_env的copy_tasks.front条件仍是动态继续义务，基础数据通过不能修复它们。完整必要条件见73L23A（根已全文核读，SHA256 68a70ee35c9a91626d0e491145a236a56a17934e84d8209f620be65c13c7452f）。

## 对当前设计的含义

本次关闭“是否连四个具名配置的引用/基本格式/位置合法性都未知”的缺口。仍未关闭：全固定来源集合、实体F/Z和resource Mask的共同初态/障碍分离、ServiceRegion、实际原源正常继续与有用有限运行见证、原数据生成/权利链，以及新delay映射与有限O支持。图上点起始互异不等于有尺寸且有横向偏差的包络不相交；连通性也不保证多机器人规划成功。前述动态无解/拥塞/合法失败不能作为事后排除理由。

本次只对17个已有官方对象取证；原payload不入仓库。随件73L23_STATIC_INPUT_CHECK_RECEIPT_20260912.json仅保存哈希、计数和静态检查汇总，不含完整地图、起点列表、任务序列、延迟矩阵、O/seed/roster或Q结果。C28获准另做delay到ACTUATOR的具体语义构造，根单独判采用；不以顾问答复替代这些数据事实。

## 引用对象身份

下表路径相对lifelong_benchmark；完整SHA256/字节/换行/检查汇总见机器回执。所有Git blob为本次字节重算匹配，不只抄树元数据。

| 路径 | Git blob | bytes |
|---|---|---:|
| city/agents/agent-1000_scen-1.agents | de43d553860822c840b3fd9b9aa52e8078a97e48 | 5850 |
| city/maps/Paris_1_256.map | 0ff641690b48c1c4807fcea7c0c31d167973b221 | 65829 |
| city/tasks/agent-1000_scen-1.tasks | 27c9eb21ee057ccfbe0c3e4a434e78743a1c0d22 | 290882 |
| delay/delay-0.001-1.txt | ff0df58b4fb3223f247888afaec0b40208621407 | 20000011 |
| game/agents/agent-1000_scen-1.agents | 9045c27d05c8a7bb7d65072382caf0943bb7bedd | 5713 |
| game/maps/ht_mansion_n.map | 7664df2f7cc97791a477b2529e7cae6d1005ee1f | 36217 |
| game/tasks/agent-1000_scen-1.tasks | 17564a366dd474a89423f9573054381be9ebd8c1 | 284726 |
| random/agents/agent-100_scen-1.agents | a3fa642cbb5d397039bfa48f783f6b8ad9833f72 | 392 |
| random/maps/random-32-32-20.map | b44f5a949e91b251b0e3bb29f3cd0784ce7d80b5 | 1091 |
| random/tasks/agent-100_scen-1.tasks | 70f8fcaba558a36c03454cc5c5874529e80dbf18 | 48871 |
| warehouse-s/agents/agent-1000_scen-1.agents | 015865f2104a52a0c274c69e25d3980b748a5b50 | 4912 |
| warehouse-s/maps/warehouse-10-20-10-2-1.map | 302a7ce60744aaf3a0c853c26bbffa3637fa027a | 10242 |
| warehouse-s/tasks/agent-1000_scen-1.tasks | 2e58552f627da2e7623ee390abb3915144dcdc2c | 245501 |

一手访问入口：[固定官方树](https://github.com/YueZhang-studyuse/LMAPF-delay/tree/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/lifelong_benchmark)、[原解析器](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/common.h)、[原driver](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp)、[原delay消费者](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/CompetitionSystem.cpp#L146)。固定引用元数据26056c、完整静态读取/汇总453f53均exit0；后者实际exec41113。四配置正文之外未读取其它配置，未为通过改换候选；没有读取本地旧Q或35–38材料，没有赋保护参数或生成研究载荷。
