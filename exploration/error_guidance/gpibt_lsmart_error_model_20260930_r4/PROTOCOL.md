# R4：整格执行时长残差学习与共同预测优先级接口

本协议及 runs.json 在任何本包 native run 前冻结。父为活动 MOVE R3；旧 R3 69工件和 OnlineGGO 44工件不改。官方 GPIBT 搜索对象、算法源码/14对象、group2、作者5×5地图、两起点、LSMART parser/ADG/正常 ACK/20tick 服务/task wire、10Hz 均保持。每run400ticks，整体54s守卫包含清理；实际末pose tick399及pending保存。

完整run切分：训练 seeds42/43/44 × nominal、slow065、slow085、axis；校准 seed51 × 同四条件；留出 seed61 × 六条件 nominal、slow065、slow085、axis、unknown_pause、unknown_shift，各跑 zero/analytic/history/learned 四policy，共40runs。每run重新初始化官方持久planner；同任务seed不假定实际任务前缀相同。训练/校准仅zero-policy。不得按tick或MOVE拆同run到不同split；留出不调模型/幅值/方向/预算。相同地图仅有限pilot，不宣称统计显著或跨图泛化。

扰动施加在controller原函数输出与实际actuator之间，不改PID公式/参数/ACK门限。nominal倍率1；slow065/slow085仅agent0所有非零轮速乘0.65/0.85；axis仅agent0的原生MOVE目标相对上一公开目标改变x轴时乘0.65，其他1。unknown_shift在agent0首次实际活动MOVE触发后所有轮速乘0.55；unknown_pause在相同首次触发后连续20tick零轮速并跳过派发/ACK，随后恢复，沿用R3首次未ACK MOVE＋前次实际非零轮速＋当前位移>1e-6规则。其未来触发/持续时间/倍率名称不得进策略输入。条件名只用于实验分组，不作feature。真实已下发左右轮速、公开command/END属于当时可用history；private pose、位移、PID缓存、未来END/未来任务全部排除。倍率是执行条件干预，不能说原作者执行器完全不变。

R1同步停稳view保持，预测不签发资源/替代ACK。R2新增明确planner-adapter干预：在官方plan前对公开p和p_copy同时加bias，plan后扣回同一bias，恢复原有aging；记录原值、算法实际有效priority、实际ids排序与扣回数值。官方核心搜索不改，但这已不是原始GPIBT策略。三个预测对照共用 `bias_i=amplitude*(predicted_MOVE_ticks_i/mean_predictions-1)`，预测clamp[5,120]，bias clamp[-amplitude,+amplitude]，优先较长动作方向预注册；calibration冻结amplitude只在[0.5,1,2]中选择，规则为校准预测MAPE最低模型对应预测时长差的中位相对差：<0.1选0.5，<0.3选1，否则2。不能据留出吞吐选幅值。zero无bias；analytic公共速度/加速度梯形模型＋原10tick轮询上界；history同信息最近三次匹配轴/agent整MOVE中位数，逐级fallback；learned ridge residual基于完全相同公共历史，lambda[0.1,1,10]只按四calrun整MOVE MAE选一次。强历史/解析都走同一R2，zero只为内部R1参考，均不冒称新发表方法。

监督按原proposal整格start→goal重建，两个原生半MOVE节点分开保留，只有最终整格endpoint的正常ACK构成wholeMOVE END。从首次已下发非零MOVE到该END的duration是模型总时长标签；每tick remaining由同一最终END减当前tick单独离线保存。未到最终END/未开始动作的target为null且显式删失，绝不当0参与训练；服务不是MOVE标签。预测用于joint-settled处下一可行轴的公开几何候选平均时长，只经上述priority改变官方实际排序/动作。活动remaining为诊断shadow，明确未喂活动中的GPIBT。

训练标准化仅训练rows，ridge实际拟合并保存coefficients/mean/scale、输入/训练来源SHA。校准仅选lambda/幅值，随后冻结checkpoint、calibration记录及其SHA，再执行全部24留出runs。输出各run合法context和离线target两份、raw/decision/receipt、真实任务服务/末占用/路径和采样距离审计；逐run报告失败或不收益。验收闭环必须实际排序受到bias且存在对照对齐公共view上的动作/派发变化；若仅预测或排序变化但没有实际动作变化，不能宣称完整闭环获益。最多两次明确bug固定修复，不增加科学预算来择优。
