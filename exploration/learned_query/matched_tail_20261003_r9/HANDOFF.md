# R9 query-line handoff

工作已完成：实现、45个同续策反事实、三模型冻结训练、40个原生留出臂、91臂物理重放、完整前缀/尾策/预算/拟合核对、10项负控、结果表和raw压缩均完成。没有待运行的科学实验或检查。root负责最终跨线判断、提交和远端发布；本worker未执行任何Git提交/推送，也未修改旧R7/R8冻结文件或入口README。

工作区：`/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE`，branch `explore/learned-query`，起始及工作期HEAD `b8577300b11786b0daeb2d4f4a1fd2c145ffe061`。本包目录是`exploration/learned_query/matched_tail_20261003_r9`。

## 核心结论

八个新N16测试world：WAIT366任务/0query/固定first4时间43915.333671；condition及三个once模型全部367任务/123query/44331.3311765。三个模型每个world的任务、时间及query与condition均完全相同，学习增益为0。相对WAIT的1任务属于原pi0。

history/nohistory/nobudget实际改变pi0动作的比例为4/8、4/8、6/8，全部query改当前WAIT。14次实际变更导致RUN/物理END记录变化，但任务服务和planner请求逐事件相同；24次评分都是单候选、发生在所有ordinal64 MOVE之前。不能声称留出多源排序、漂移后适应、重复部署优势或学习改善服务。

16训练query标签：3正、8零、5负；主任务差全部0。8校准query标签：0正、5零、3负，含1个少完成1任务的负例。另21个WAIT分支显式保留。校准不用于调参；没有按收益补选数据。

## 审阅入口

- `REPORT.md`：完整方法、正负结论、全部8world结果、限制。
- `CONTRACT.md`、`REGISTRATION.json`：事前合同、全部14world输入、源码/二进制/作者bridge配置pin。
- `RESULTS.json` / `RESULTS.csv` / `SUMMARY.json`：全部91次原生运行和全部40留出臂的可复算结果。
- `TRAIN_CAL_LABELS.json`、`LABEL_SELECTION_BEFORE_PROBES.json`：21机会的完整候选+WAIT、预算、公开特征及目标。
- `MODELS_FROZEN_BEFORE_TEST.json`、`MODEL_FREEZE_RECEIPT.json`、`TEST_START.json`：三模型及冻结前0测试证据。模型SHA `ec96643b3b4bc8d81b26731c983ed05b4578b5595a13aad59456ceff596a1f76`。
- `TEST_REPLACEMENT_DECISIONS.json`、`REPLACEMENT_MECHANISM_DIAGNOSTICS.json`：真实改变14/24、24/24单候选、漂移前触发，以及后续任务无变化的机制记录。
- `AUDIT_ALL.json`：91臂独立70位Decimal物理、资源、访问依赖、服务、24特征与原生选择审计。
- `MATCHED_TAIL_MODEL_AUDIT.json`：完整pi0前缀、WAIT下一事件、同pi0尾策、预算扣除、45标签重算、三模型增广lstsq、31同首行动全轨迹恒等对照。
- `NEGATIVE_CONTROLS.json`：10项篡改全部拒绝。
- `SOURCE_DELTA_AUDIT.json` / `SOURCE_DELTA.patch`、`PARENT_PINS_VERIFIED.json`、`PUBLIC_MAP_SOURCE_AUDIT.json`、`AUTHOR_PROVENANCE.json`：选择层delta、旧冻结/生产/作者pin、两图原.map与.scen及注册layout/start行核对。
- root提供的`root_refit.py`、`ROOT_REFIT.json`、`root_heldout.py`、`ROOT_HELDOUT.json`均纳入白名单；root两项审计PASS。

## 发表包

`PUBLICATION_MEMBERS.json`是精确白名单，`FROZEN_MANIFEST.json`逐文件绑定最终worker包。root已有独立审计文件已包含。只按白名单提交，排除`runs/`、`audits/`、`build/`、`__pycache__/`；不要把同一raw再次展开入Git。

五个raw包分别约13.25、13.21、6.85、13.89、12.98 MB，均小于45MB。`RAW_ARCHIVE_MANIFEST.json`记录546成员，每成员SHA和整包SHA均核对，成员互斥覆盖全部91次输入、raw、planner、receipt、stderr。0个执行失败也完整记录在RECEIPT和SUMMARY中。

保留现有writer的排他创建约束，不要在冻结目录重跑生成器以制造新独立样本。原注册源码、模型、物理控制器和作者planner均未在测试后修改。新增后验分析脚本只读证据，不参与采样或选择。复现命令与本地外部依赖见README。

本轮仅N16，不做N32兼容变更；查询计数尚未接主线生产COST/AUTH。两图均见于训练，仅4个新测试family，IID/SHIFT配对相关。原condition为内部公开规则，当前官方bridge仍为承诺frontier适配，不能称为完整作者实位姿benchmark或发表SOTA比较。
