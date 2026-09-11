# 73L18：LoRR 官方归档与 R0 地图对象的元数据连线

2026-09-11，根 /root。NO-SKILL / BOUNDED PRIMARY-SOURCE EVIDENCE / NONBALLOT。接续73L2，不修改旧报告。只核说明与Git元数据；未读取任何map/scen/config/agent/task/delay/result载荷正文、压缩包或地图图片，没有下载/运行生成器，没有生成参数、实例或结果。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT，六门不变。

## 1. 实质结论与范围

固定R0的city地图Paris_1_256.map和random地图random-32-32-20.map，与MAPF-Competition/Benchmark-Archive固定提交的多个官方归档路径具有相同Git blob标识及字节大小。这比类别名/文件名相同多了一层具体对象身份依据；并不证明复制方向、原创作者或适用许可已经完整，也不绑定agent/task/delay生成关系。

R0的game是ht_mansion_n.map，warehouse-s是warehouse-10-20-10-2-1.map；本次完整归档树中的地图条目没有同blob对应。不能把归档中名为game的brc202d或warehouse_large冒作它们，也不能据“未匹配这个归档”断言其它合法上游不存在。

## 2. 真实获取路径

根先完整读取73L2回执（7584a9），其中明确League首页此前仅JavaScript壳，但未穷尽官方其它来源。本次对官方站点及具名MAPF-Competition组织做两个定向搜索；实际结果turn103search12为LoRR官方expo24域的团队报告资源，检索摘要露出明确的Benchmark-Archive链接。只将这一链接用作发现路径，不引用其性能/实例数字或把团队报告本身当许可。

继而直接用GitHub API核归档仓库元数据（dc1adf/exit0）：full_name=MAPF-Competition/Benchmark-Archive，default_branch=main，license=null。null只表示本次仓库API未识别出许可对象，不等于法律上无权使用、也不证明所有目录没有许可。根未发任何邮件或请求外部人员授权。

main ref实际28acd4/exit0为25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a，此后树与说明全部固定该提交。归档递归树d1eb7b、R0固定递归树ddac4f均exit0且truncated=false；返回Git路径/type/blob SHA/size元数据，正文输出只列说明名称和.map条目。未请求任一地图blob的内容，未将任何配置/任务/解文件作为读取对象。

[归档固定README](https://github.com/MAPF-Competition/Benchmark-Archive/blob/25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a/README.md)自称League of Robot Runners Benchmark Archive，说明其发布历届比赛实例、最优已知解及生成脚本，并回链League官网。2023/2024目录README分别明示其对应比赛归档。这补上此前只见首页壳而缺可读说明的入口，不声称根已审阅完整League网站或所有历年档案。

## 3. R0 与归档对象身份

R0固定提交为0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。下表只列每个匹配的一条代表路径；完整匹配数量来自同次不截断树的内存元数据比对，没有读取载荷来计算新哈希。

| R0路径 | Git blob SHA（非SHA256） / bytes | 固定归档中的对应情况 |
|---|---|---|
| lifelong_benchmark/city/maps/Paris_1_256.map | 0ff641690b48c1c4807fcea7c0c31d167973b221 /65829 | 6条同blob同size；如2024 Competition/Example Instances/city.domain/maps/Paris_1_256.map |
| lifelong_benchmark/random/maps/random-32-32-20.map | b44f5a949e91b251b0e3bb29f3cd0784ce7d80b5 /1091 | 9条同blob同size；如2024 Competition/Example Instances/random.domain/maps/random-32-32-20.map |
| lifelong_benchmark/game/maps/ht_mansion_n.map | 7664df2f7cc97791a477b2529e7cae6d1005ee1f /36217 | 本归档树无同blob地图对应 |
| lifelong_benchmark/warehouse-s/maps/warehouse-10-20-10-2-1.map | 302a7ce60744aaf3a0c853c26bbffa3637fa027a /10242 | 本归档树无同blob地图对应 |

必须保持对象精度：2023 Competition/Example Instances/city.domain/maps/Paris_1_256.map虽然文件名相同，但blob为4abf8ac92444fa5a82c19c287ee35c509110db05、size131659，不能计入上述city匹配。根未读两文件内容，不能推断差异是换行、编码、地图改变还是其它原因。同理归档内部分warehouse同名对象也有不同blob，本报告不做内容等价猜测。所有大小只作来源元数据，不是选择地图规模或给density N赋值。

根可以准确说“相同Git对象身份已在固定官方归档中定位”，不能说“已通过原始Moving AI全文比对”“已证明源传承顺序”或“这些对象许可全部通过”。若未来需要不同算法使用相同材料，仍须完整授权/来源合同和既定静态合法性检查。

## 4. 实际说明读取与身份

以下五个README由GitHub连接器完整取得UTF-8正文，字段sha与固定归档树一致。阅读对象是说明文档，不是其链接的任何实验载荷。目录README含公开比赛成绩/提交链接，生成器README含示例命令及既有默认值；本题不使用那些性能数字，不将示例值作为本研究赋值，也没有打开解包、配置、教程载荷或运行其中命令。

| 说明路径 | Git blob SHA | 树报告bytes |
|---|---|---:|
| README.md | 77ddb82e6cba768e590d91976d158ec74dc8ee5f | 1008 |
| 2023 Competition/README.md | 51d03995131049e9a95390361d89340e82a96092 | 7267 |
| 2024 Competition/README.md | d83459326b9578abb55fe5e9bd982d3257579467 | 7634 |
| 2023 Competition/Problem Generator/README.md | 48f95041c49174af67b55cfee6079d9297d58c1e | 2742 |
| 2024 Competition/Problem Generator/README.md | 72f9918aa53f089b20ed836f69d472ae8c888dc9 | 6058 |

生成器说明支持一个有限事实：组织方公开说明其有用于对应年度比赛的实例/仓库地图/任务生成脚本，且任务可来自随机生成或预先给定任务集。[2023说明](https://github.com/MAPF-Competition/Benchmark-Archive/blob/25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a/2023%20Competition/Problem%20Generator/README.md)、[2024说明](https://github.com/MAPF-Competition/Benchmark-Archive/blob/25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a/2024%20Competition/Problem%20Generator/README.md)。它们没有在本次读到的正文中把R0具体agent/task/delay对象与生成输出逐一绑定，因而不能据脚本“可能生成”推它“确实生成”了R0文件。未读取脚本本体或教程，不对生成器代码正确性或可复现性授资格。

## 5. 对73L2缺口的准确更新

73L2当时“尚无R0逐对象到公开上游连线”和“League只有JavaScript壳”的实际取证状态保留原文。本后继已找到可读官方归档，并为city/random补入同blob对象定位；这是新的局部来源证据，不回改旧报告或把其UNKNOWN伪写为历史PASS。

仍缺：这两类对象的更早素材/独立权利链与适用说明；game/warehouse-s的具体同对象上游；R0各agent/task/delay到合法来源及其生成/转换的记录；主roster合法支持集和全部字段/表示绑定。归档API的license=null及本树未列命名LICENSE/NOTICE文件都不能代替适用许可判断，R0软件MIT也不自动覆盖素材。Moving AI ODC-By及游戏研究分发声明沿73L2的对象范围保留，不因有了归档连线就套给所有R0对象。

本轮只更新G5缺口的证据精度，不把2个对象匹配等同2类数据资格通过，不产生任何map/scen/config/agent/task/delay载荷或实验结果。检索在本有界归档证据处收束，不继续抓同名地图。完整文件仅写研究目录、apply_patch编辑，所有shell以rtk前缀执行；旧冻结/桌面/参数边界保持。

