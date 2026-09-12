# 73L20：source_id 分量的资格链与静态合法域

2026-09-11；`/root/successor_identity_audit`，接续身份核验后获根单独登记的新有界任务。NO-SKILL / BOUNDED PRIMARY-SOURCE EVIDENCE / NONBALLOT。唯一新工件；不修改主稿或历史意见，不投六门资格票。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 实质结论

现有证据可以定位固定软件的输入解释器，并将 agent/task 的下一步取证收束到具名官方生成器；还不能给出任何一个完整合格的 source_id。地图同对象、文件存在、解析成功、适用权利和合法 WORLD 是分别需要证明的命题。当前状态是 **未实例化且尚无完整链合格成员的存在证据**，不是“已经证明合法域为空”，也不是“只是尚未挑选具体样本”。

新实核表明 R0 的 agent/task 解释器只取各记录的逗号首字段；delay 解释器把整数转换成 bool；地图解释器只把 `@`、`T` 视作障碍。这些行为并不完成所需静态检查。因此将另一个官方文件放到相同后缀下，或者看到原程序能够读入，都不能替代语义和合法域核对。

## 2. 输入与实际一手读取

已全文读 L18、L19、L2；读取当前73 §11全部（L445–476）、§12全部（L477–522）。286353逐件实核下列输入，均非符号链接；73没有改变。

| 输入 | SHA256 | bytes / LF |
|---|---|---:|
| 73L18 | e20a7dd2d05b495ece88a31164f2f9d3439439eeeb072aa6019be08ac9da1327 | 7542 /57 |
| 73L19 | 4ee91a0480890f4beae541c6093b098c2190aeafb497852f9ae3cc1941c26f71 | 11912 /83 |
| 73L2 | 7796d5164c7367350c16d7215aa52045c30985fb44f05d1c109f769143eaa776 | 11382 /96 |
| 73 | 9e06199cc6045ddd750b861b3091ec239c7c6ff2ae7eeaebbdd0e7fde61ec113 | 216498 /665 |

R0固定 `YueZhang-studyuse/LMAPF-delay@0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`；归档固定 `MAPF-Competition/Benchmark-Archive@25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a`。通过 GitHub contents API 的 raw 返回，实际完整读取下列六个正文对象，无截断。源码中的示例命令/原有默认值只作原文，不执行或移作研究参数。

| 正文对象与固定链接 | Git blob / bytes | 本题实际回执 |
|---|---|---|
| [R0 README](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/README.md) | a4578f87f918dab4b67b50cd404e3ec901a8f636 /2730 | 5db2a7，全文 |
| [R0 LICENSE](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/LICENSE) | 1f4b6eadac278447824a47d409bb4de04ea7f3ee /1084 | 4221ce，全文 |
| [R0 driver](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp) | b75764cc26c2374ce51dabb94e13a138e50f166f /6664 | ed9459，全文 |
| [R0 common.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/common.h) | 9ddeff363a76cbd70a3e6e1ca98cfd79f69c8237 /5954 | ba697a，全文及全部读入函数 |
| [R0 Grid.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/Grid.cpp) | b78abb1848a74d4c801e6eea6e1e89ccf4f6ddbe /2155 | d4e105，全文 |
| [归档2024生成器README](https://github.com/MAPF-Competition/Benchmark-Archive/blob/25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a/2024%20Competition/Problem%20Generator/README.md) | 72f9918aa53f089b20ed836f69d472ae8c888dc9 /6058，blob承接L18 | 53d032，本题重新取得全文 |

前五个blob/size由本题固定R0递归树8cd3b2取得，`truncated=false`；未将raw正文另作Git blob复算。30e016取得归档生成器脚本元数据，99d836取得R0 agent/task/delay子树身份；均完整元数据返回，不读取其数据blob。Moving AI/ODC-By的声明范围承接已全文阅读的L2/L19，不冒称本题重新浏览许可正文。

## 3. source_id 分量资格矩阵

下表评价证据链，不生成任何实际source_id或roster。

| 分量／关系 | 当前确有证据 | 尚缺的承重连接 |
|---|---|---|
| category | 73固定四类树；99d836复核目录身份 | 类别存在不保证每类有合法完整成员；不得删空类重分权 |
| city/random的map_blob | L18：R0与固定官方归档存在同blob/size对象 | 更早权利与适用声明、转换/复制关系、与其agent/task/delay绑定 |
| game/warehouse-s的map_blob | L19：官网具名分类、同名条目及相应声明上下文 | 无官方同对象hash；名称、尺寸/状态数不能完成身份连接 |
| agent_blob | 固定四类agents子树存在；driver调用带team_size的read_int_vec | 哪个配置引用哪个blob、来源/生成记录及适用权利；索引/初态合法性未求值 |
| task_blob | 固定四类tasks子树存在；driver调用无team_size的read_int_vec | 队列及实例身份、跨map incidence、来源/转换和许可；不能把多errand任务静默压成单点 |
| delay_blob | 固定delay子树4e3fe329a547e682d1520047bf767a5397b3b43f；driver具名读入接口 | 具体对象的生成者/版本/允许用途、行列及时间解释；暂无已读说明给出具名生成链 |
| assignment_strategy | driver实际分派greedy、roundrobin、roundrobin_fixed三个字符串 | 各构造器后继语义及草稿任务世界的精确映射不由此字符串证实；本题不选值 |
| parsed_semantic_options及alias | driver可定位输入字段；common.h可定位类型/词法解释 | 必须按实际解析语义合并别名并保存原身份；不能因只取首字段就丢失未解释内容 |
| 完整WORLD/profile合法性 | §11/12给出静态输入、共同初態、Mask、任务世界及支持集义务 | 没有已核合格实例、非空必需profile或完整素材许可链；软件INIT成功不能代签 |

R0 LICENSE亲见MIT对软件及随附文档的授权文字；它没有逐对象说明这些地图或任务的独立素材权利。归档README说明用途与生成器存在，也没有在该正文中将R0具体对象认领为其输出。此处只记录声明覆盖证据，未作特定司法辖区的法律结论。

## 4. 从原parser可提出的静态核验义务

这些是未来静态资格判定应核的谓词及其根据，不是已执行检查，也不擅自新增来源筛选结果。

1. **路径/类型。** driver将JSON父目录字符串与各文件字段相接；未在此处执行73要求的固定树约束或规范化。未来须分别证实引用仍处固定树、存在blob、JSON类型正确及解析无歧义；不能把草稿的路径防护说成原程序已有。
2. **数值/完整记录。** common.h对计数及记录调用`atoi`，在多处直接解引用首token；打不开文件返回空向量。原函数没有给出严格十进制、溢出、缺行/空token的完整拒绝合同。合法域必须确保所有后续访问所需记录和表示均定义，不能用“空返回”解释成已证合法空任务世界。
3. **地图/位置。** Grid按header取rows/cols并按其积分配、逐行索引，只区分`@`/`T`与其余字符。维度/乘积可表示、每行足长、符号解释、agent/task索引范围及通行性需要独立谓词；地图通行还不证明连续实体初态与bootstrap Mask不交。
4. **delay与语义别名。** 原delay读每个agent一行，整数到bool会将非零值合并；该函数不核统一行宽或后续所需时间域。不得把这种转换当所有整数delay数据的合法解释。必须绑定原输入字节、转换规则与后续索引域；是否允许这些别名需明确合同，不能读入后再猜。

本题没有阅读task分配器完整实现或delay消费器，也没有证明上述局部读入条件已覆盖全部继续域。静态语法成立、全部动态映射良定义和实际评分可得仍为不同层；未知运行评分不得倒填为静态排除。

## 5. 最小下一证据与停止边界

**agent/task有具名下一入口。** 本题亲读的2024 README将`benchmark_generator.py`明确描述为接收地图、team sizes及任务集说明的实例生成器，并区分随机任务与预先给定任务集。30e016元数据固定其路径`2024 Competition/Problem Generator/script/benchmark_generator.py`、blob `0aaf04d7cad4bf9405d81077f41dcbeacb996a8c`、9500 bytes；同目录`problem_generator.py`为`86652033f57ebf0186ee9566408ba85057780266`、9899 bytes，仅有存在元数据，未证明调用链。本题未读脚本体或运行生成器。后继可有界核其格式/来源声明，先辨清2024多errand任务与R0首字段单整数读法，再寻找输出对象到R0的公开记录；不因生成器“能生成”就认定“生成过”。采用另一个新生成来源还会改变既定来源选择与支持集，必须由根显式取舍。

**delay没有同等已证下一入口。** R0 README只链接一般输入输出说明，当前已读六正文没有delay生成或逐对象出处声明。本题对`Input_Output_Format.md`仅见路径/blob元数据，未打开正文或其中可能的实例。下一证据应是固定R0的具名delay出处/生成说明或能对齐具体对象的公开历史记录；目前不能指定一个已证的生成器，也不能推出它不存在。软件MIT和LoRR任务生成器均不补此缺口。

**完整链需要元数据绑定，不能在禁读边界下装作已经检查。** 可用的下一种材料是逐对象出处/许可与原样或转换关系记录；仅有配置、数据文件与目录的存在不够。任何后继都不得下载同名地图正文比hash、读取载荷或为得到非空域临时制造source_id。若必需类别或profile是否非空仍无证据，保留未实例化与存在性未知；不虚构失败轨迹作为有效样本。

额外尝试仅为两固定Git树的agent/task/delay跨端blob元数据比对：9687c5的子进程exit1未得结果；正常升级后只续原functions cell14，117e01明确TLS handshake timeout/exit1，仍未取得比较。没有“零匹配”的实测结论，不另重试或冒称完整调查。其余具名API调用均exit0。报告在上述六正文及固定树元数据处停止，不泛搜镜像、不索取外部人员授权。

286353确认输出此前不存在且非符号链接；仅apply_patch新建本件。全部shell/链段均rtk，无新Claude/skill/正式审查，无实现、伪代码、构建、测试、仿真、参数赋值或载荷/结果生成；35–38、Q及全部map/scen/config/agent/task/delay/result载荷正文与地图图片未读，桌面未触及。研究资格及总体设计仍未闭合。
