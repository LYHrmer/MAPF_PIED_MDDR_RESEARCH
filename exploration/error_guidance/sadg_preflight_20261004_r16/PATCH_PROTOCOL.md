# 隔离 compiler 边界修补预登记

原版完整checkpoint映射发现88个反向依赖不满足 `j,l+1 -> i,k-1`，全部来自 `k=0` 时Python负索引返回末动作。原版源 `compiler.py` 的 try/except IndexError 不会捕获合法的 `[-1]`，所以本应不可反转的起点依赖被错误建成指向末动作的反向边。原版副本保持不变。

最小隔离修补仅在取 `vertices_i[k-1]` 前显式拒绝 `k==0`，进入原作者已经提供的 `rev=None / switchable=False` 分支。不修改 MILP、时长、目标、求解器、依赖组、状态或执行接口。通过三动作手工反例和已映射checkpoint全量反向索引审计验证修补作用；二者不调用优化器。

原版与补丁版结果分开命名和归档，不用补丁结果覆盖原版失败。补丁的共同执行资格仍需全量已满足边/承诺保护和原guard；没有默认授权删除任何 guard。

## 第二项：本项目的保守承诺守卫

k0修补后的random映射仍发现2个已完成tail的组被标记可切换。具体 `dg_agent21_0` 的反向head含COMPLETED的 `v_21_0`，但OPPOSITE组缓存的 `first_head_inactive` 为STAGED的 `v_5_5`。原 `append_switch` 用新active依赖的head更新这一字段，不能代表全部反向head状态。

隔离版本增补保守适配：`is_switchable`逐一检查每个依赖对确有reverse，且当前active/inactive的全部head均为STAGED。此项属于本项目完整承诺保护，不能直接外推为论文理论安全缺陷。它不修改优化目标/时长/求解器，仅缩小允许切换集合。

经根要求，额外random映射只留诊断，原预登记warehouse t0.5 axis_slow仍须完成。全量映射和原guard通过后，登记1个官方patch回归＋最多2个warehouse公共/测量诊断调用；总实际作者MILP调用最多10（原7＋回归1＋配对2），仍小于原上限12。所有旧域实验使用原作者optimizer、60s cap，patch和承诺adapter单列。不会把参数适配的结果冒称原作者未改基线。
