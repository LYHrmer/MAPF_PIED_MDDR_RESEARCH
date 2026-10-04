# SADG R16 作者核心预检

先读[REPORT.md](REPORT.md)。12个唯一作者求解均完成；仅2条合成事件后缀，旧R13/R14轨迹没有重跑。结论：作者连续机制可响应，但完整公开历史基线已取得同顺序，POSITION没有新增后果收益。

原源码、ECBS build和venv在 `/home/lyh/.cache/mapf_research/`。来源hash及依赖见SOURCE_ENVIRONMENT.json、requirements.lock。原AGPL-3.0许可保留。run_preflight为无ROS原核心；run_patched为明确命名的compiler/承诺adapter版本；run_history_rate只修改输入时长。

只读复核，不重跑优化：

```bash
rtk proxy /home/lyh/.cache/mapf_research/sadg-r16-venv/bin/python -I /home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_preflight_20261004_r16/finalize_audit.py
```

在新目录独立复现时，先按PROTOCOL和三个追加协议登记输入。主要原执行命令：

```bash
rtk proxy git clone --no-checkout https://github.com/alexberndt/sadg-controller.git /home/lyh/.cache/mapf_research/sadg-controller-c2626d9
rtk proxy git -C /home/lyh/.cache/mapf_research/sadg-controller-c2626d9 checkout --detach c2626d996121a9d6c128844a167b917db24418ac
rtk proxy git -C /home/lyh/.cache/mapf_research/sadg-controller-c2626d9 submodule update --init --recursive
rtk proxy python3 -m venv /home/lyh/.cache/mapf_research/sadg-r16-venv
rtk proxy /home/lyh/.cache/mapf_research/sadg-r16-venv/bin/python -I -m pip install -r requirements.lock
rtk proxy cmake -S /home/lyh/.cache/mapf_research/sadg-controller-c2626d9/third_party/libmultirobotplanning/external/libMultiRobotPlanning -B /home/lyh/.cache/mapf_research/sadg-ecbs-build -DCMAKE_BUILD_TYPE=Release
rtk proxy cmake --build /home/lyh/.cache/mapf_research/sadg-ecbs-build --target ecbs -j2
```

ECBS实际命令收据见ECBS_RECEIPT.json。运行器各自 `register` 冻结输入，然后 `solve --case NAME` 调用；run_preflight all会复用已成功的相同内容键。不要删除旧结果后重跑来“刷新统计”，也不要将新的compiler/adapter结果覆盖原版身份。

每case完整图、LP、变量、约束、目标、cap与日志均在cases中；后缀真实事件、静止和运动段在suffix中。FINAL_AUDIT是自检，根独立审核另存；失败观测器材料保留供审计，不计作者优化调用。
