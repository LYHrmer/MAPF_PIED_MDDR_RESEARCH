# R4c：固定可达争用机制，真实历史驱动动作闭环

旧R4四十run零动作结果、R4b两种完整校准失败probe先冻结；本后继是预先设计机制场景，不是随机benchmark，不冒称原40run内修复。固定原地图/两起点、GPIBT初始化seed42、环境/任务seed62，800ticks10Hz一次固定，绝不看结果延长。六条件nominal/slow065/slow085/axis/unknown_pause/unknown_shift×六policy zero/analytic/history/learned/fixed_agent0/fixed_agent1，共36独立native；每run54s含清理。

共同rank规则全保持：预测差<1tick无bias，否则较长者+1、较短者−1；三预测共用同输入/同函数；两常量内部消融分别[+1,-1]/[-1,+1]，不读预测，不冒称外部baseline。原λ1模型/权重/标准化完全不动；官方搜索14对象/持久GPIBT、public p/p_copy加回/扣回保留aging，原parser/ADG/ACK/驻留阈值及执行条件也不改。

使用作者已有task_file读取器的FIFO环境适配：OneGoal原本加载tasks却genGoal忽略它，本后继只在非random_task时取各agent已加载队列front并pop，返回location，仍由原Task构造赋唯一id/owner。环境私有完整未来列表，actor从get_location只见当前goal，公共context抽取不读取任务文件。每agent固定66个合法任务足够800tick；20tick服务上界最多40次/agent，不能耗尽FIFO。任务agent0前缀5→0→21→0→21…；agent1为15→10→7→10→7…。

前两轮独立完整MOVE及服务让两agent在本world获得可辨识的已交付执行历史，再分别回原0/10并驻留完成服务。第三轮同时公开goal21/7，形成共同下一顶点cell5争用；全部条件/策略都经历这一同任务机制，未知暂停/突变仍在第一次实际活动MOVE触发。原随机任务流被此明确固定环境替代，不声称作者随机任务对照或跨图泛化。

闭环验收以真实同条件同公共warming前缀后的forecast→bias→实际官方排序→联合动作→真实pose/ACK/服务/pending为因果链；必须有学习模型动作变化，不能仅排序、shadow MAE或手动bias探针。所有36结果无收益/失败照录。常量偏好消融辨别适应信息价值，不能把同常量结果当学习独有收益。

整MOVE模型仍只预测first_nonzero_MOVE→whole_END，不含转向/派发gap；总占用诊断继续保留。future任务/扰动时长/pose不入feature；删失为null。原径向半MOVE ACK谓词与更严格中点距离指标分开，最终整格END/驻留/停稳view按原容差核，采样距离不作连续足迹证明。
