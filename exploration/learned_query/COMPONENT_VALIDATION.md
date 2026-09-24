# 组件已提交状态到模型入口的验证

2026-09-24。已运行真实 C++ 组件头文件与 FLINT 数值库，将组件提交后的状态精确导出到 Python，并完成现有小模型推理。输入证书和收据仍是程序内人工夹具；这不是生产 AUTH/站点链，也不是学习性能实验。

## 实现和实际结果

- `component_snapshot.hpp` 按值保活一个 `PositionCommit::View`，从同一根读取结构、历史、报价及时间，显式标记 `synthetic_component_fixture` 和 `outer_publication_verified=false`。
- `run_component_check.py` 先核对 `component_sources.json` 中七个头文件的 SHA-256，再复制到临时目录。只在副本增加 const getter；原目录不写入。编译/运行后再次核对源指纹。
- `component_io.py` 严格检查 schema、身份关联、时间、精度和精确数域，生成不可变 `Snapshot`。原来源、绑定及排除项另存不可变 metadata，不进入模型特征。
- `component_fixture.cpp` 运行两次 POSITION 组件提交和一次人工收据提交，检查准备阶段不外泄、提交后 q/责任/历史同步、旧 View 保持不变，以及缺精度和不可查询责任的保留。

验证结果：57 项 Python 检查通过；C++ 夹具的 29 项断言通过。共导出九条快照，八条有理状态成功投影；一条已提交的非有理 q 整条拒绝，错误精确定位为 `$.actions[0].q`，没有进行近似或继续评分。

在 `rational_ready` 上，Python 与实际 C++ `choose` 的正收益首选均为 `move-A`，预测证书下界均为 `3/4`、成本乘积分母均为 `4`；需求权重和完整 owner 数逐项一致。无报价状态下 C++ 返回 RR，Python 返回 `defer_to_original`。未知精度的 `move-U` 明确报告 `missing_precision_promise`，它的阻塞关系仍保留。

已有人工训练模型读取该投影并产生有限查询建议。本次新夹具没有提供训练标签；仅一个可评分候选也不足以比较学习排序收益。该结果证明这条组件接口能够组合运行，不证明模型更优。

## 实际修复的数值问题

反向审查提示并实际复现了旧 Python 评分的浮点累计问题：候选 A 的 P 是三个 `1/10`，候选 B 的 P 是一个 `3/10`，同费且 B 的需求更早；精确并列本应选择 B，旧代码却因 `0.1+0.1+0.1 > 0.3` 选择 A。该回归在修复前分别对割线与常量概率预测器失败。

现在先将每个输入概率转换为 Fraction，再乘权重、除完整 owner 数、累计和排序；仅报告字段转浮点。割线0/1路径保留精确有理组合，学习路径保留模型实际返回的浮点概率对应的精确有理值。这不使概率更准确或更校准，也没有解决前一轮发现的组合决策目标问题。Fraction计算及导出成本尚未接原 B1 核算。

## 审查分工与边界

Astra Ultra 复核单根读取、数据时间与数域边界，并要求收缩测试命名：时间链检查不能声称拒绝所有未提交或跨根伪造信息。JSON字段的一致性不认证来源；同根性质依赖本轮审查并执行的 C++ 取数路径。

按用户授权，Claude CLI 实际以 `--model opus --effort high` 完成一次只读规格反向审查，返回 success、`is_error=false`，报告模型 `claude-opus-5`，用时84689 ms。它未读取最终代码或运行测试。采用其数值并列提醒并补了责任ID与动作同名时仍不可查询的检查；未采纳“仅凭root/generation/time三元组即可认证混投”的意见。snapshot已限定每profile至多一条保留收据，重复profile直接拒绝，不另发明收据选择规则。实现、修复和运行由Codex完成，不归为Opus源码交付。

生产外层发布仍未接通，不能用内部 `Scheduler::commit` 触发生产导出。真正候选接点仍是 `CenterService::commit_at_opportunity()` 完成所有根交换、finish成功并返回Granted之后。本轮不运行该业务服务、guest、world或研究实验，不读取研究载荷，不赋原保护参数。

## 复现

依赖本机原始源码及既有 FLINT SDK，七份原始头仍未纳入本分支。仓库单独克隆不能自动获得这些本地依赖；指纹变化时脚本拒绝构建，必须重新核对。首次构建发现现有SDK的生成头搜索路径不足，补入 `third_party/flint_host_config/src` 后严格编译和组件运行通过；没有下载或重建依赖。

```bash
rtk proxy python3 -B -m exploration.learned_query.run_component_check --source-root /home/lyh/MAPF_PIED_MDDR_RESEARCH
rtk proxy python3 -B -m unittest exploration.learned_query.test_model exploration.learned_query.test_shadow exploration.learned_query.test_integration exploration.learned_query.test_decision_structure exploration.learned_query.test_component_io
```

当前闭合的是组件接口与一次模型推理。仍需实际发布query与返回证书的身份关联、具有覆盖度的训练/留出数据及完整费用闭环，才能验证学习是否带来独立任务收益。
