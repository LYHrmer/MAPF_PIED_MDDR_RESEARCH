# R16 根独立复核

本目录与候选运行器分开实现复核，不重复科学实验。主线 agent 另交叉审核 SADG 和查询模型；不是盲评。只读源工件、原始事件、生产几何和冻结协议用于重建结果。

|入口|验证内容|新增科学运行|
|---|---|---:|
|[main_independent.py](main_independent.py)|原 SOURCE 正文、精确几何、时效外包、资源交集、旧实际 RUN 与291费用段|0|
|[query_independent.py](query_independent.py)|27个native STOP、同前缀、正常后续执行、FIFO/受限T；复用对应C/LD raw|0|
|[query_cal_independent.py](query_cal_independent.py)|24TRAIN双臂、40有效分割、精确树重拟合、6CAL选择与3语义别名|0|
|[sadg_independent.py](sadg_independent.py)|全部12模型的语义约束、可行性与采用图；20个累计独立小LP检查|0作者调用；独立数学LP另计|
|[suffix_independent.py](suffix_independent.py)|两条后缀的依赖时序、完整驻留、闭时间段连续点距|0|

对应 JSON 是实际检查输出。`QUERY_INDEPENDENT.json` 的 CAL 汇总仅含3个新native B8，完整6项用 `QUERY_CAL_MODEL_INDEPENDENT.json`，不能混用分母。后者独立确认固定STOP以同任务、更少查询和更短受限T严格支配当前学习树。

SADG原七项独立LP结果按四个原始文件hash复用，另外五项继续核验；warehouse两大模型独立重建约束并核CBC返回解可行性，不另求最优。两条suffix是合成事件adapter、固定真实持续时间、点几何，不能替代完整足迹或ROS认证。

重现需要按各发布包说明恢复新生成的详细JSON/raw，并保有旧R13来源数据。脚本路径对应本机三个既有worktree，异机需改路径根；没有隐藏自动下载或求解步骤。主线实现按用户既有仓库分工保留本机，所以其公共JSON用于审阅，公共仓库本身不含重跑主线所需全部受保护工件。

`FROZEN_BEFORE/AFTER.json`核15份选定旧工件及原稿不变；不是全目录快照。跨线结果和后续工作见[总报告](../THREE_ROUTE_POSTUPDATE_20261004_R16.md)。

发布静态检查保留冻结材料原字节：CSV为标准CRLF；作者许可末尾空行、原作者派生guard文档中的行尾空格及统一diff的空白上下文不作格式改写。除此之外新增源码/文档通过限定路径的diff空白检查，所有发布Python通过AST语法解析；这些检查不代替上述行为核验。
