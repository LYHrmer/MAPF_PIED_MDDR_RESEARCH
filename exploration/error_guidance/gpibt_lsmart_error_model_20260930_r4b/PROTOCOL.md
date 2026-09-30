# R4b：探索性共同rank接口后继

父R4的40native、seed61零动作影响、模型及协议先完整冻结。R4b由该接口失效引出，明确不是原40run预注册内修复，不合并/隐藏旧零结果。模型权重、lambda1、train/cal原数据全部不变，不根据seed61挑新模型或误差条件。

唯一新接口：同信息两agent下一MOVE时长预测若绝对差<1tick，则bias=[0,0]；否则较长者+1、较短者−1，固定幅值1。zero仍无bias，analytic/history/learned三policy同函数。仍使用原R4 bridge给公开p/p_copy加bias、官方plan后扣回，保留原aging；14官方算法对象、执行器及所有扰动/地图参数均相同。是明确planner-adapter干预，不是原GPIBT，不靠学习优先级宣称论文新颖性。

先仅用四个cal51既有公开请求及各自已交付历史，计算本接口实际bias，并对每个公开fixture独立初始化同官方planner检验动作可受影响。每fixture zero和三policy使用同初始化seed51、同public view；是cold-start接口诊断，不冒称保留cal原live算法内部guidance状态的反事实回放。只有实际本接口预测bias出现官方动作变化才允许后续test。probe全保存，不挑收益场景。

probe通过后，事先固定从未用过的task/plannerseed62 ×六既有conditions nominal/slow065/slow085/axis/unknown_pause/unknown_shift × zero/analytic/history/learned，共24个独立400tick、10Hz native。各run整体54s含清理，官方作者taskstream各自实际前缀/删失/pending保留；不以same seed假定任务相同，不加未来扰动/pose输入。unknown活动规则/倍率完全继承R4。模型/接口/seed/预算在任一seed62 native之前冻结，不基于其结果调优。

验收是真实heldout中模型预测改变官方搜索排序且至少改变实际联合动作/任务执行；不要求获益才通过，全部无收益/倒退/失败照录。若只有排序没有动作变化，仍不能宣称闭环动作效果。原谓词通过、更严格半节点点误差、整格ACK/服务/view物理误差与采样中心距离分开，不声称连续足迹安全。R4运动段监督范围失配仍保留，不在此改目标。
