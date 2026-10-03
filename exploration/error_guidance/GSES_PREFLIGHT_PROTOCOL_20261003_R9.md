# R9作者基线可运行性预检

目的：为可能的延迟后通行顺序改进准备真实作者基线，不将现有查询规则或额外global门包装成外部方法。本轮只复核原作者方法的构建、原始实例和接口，尚未与本项目候选方法作同问题比较。

来源：[AAAI 2025正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/34487)、[作者STPG仓库](https://github.com/DiligentPanda/STPG)，固定commit `25fb931eff03f1cce23a22a68ab42b7533f85ab3`，MIT。子模块PBS固定`f1e08e104c0cb575d6f9ed8b26344c0b982f422d`，pybind11固定`19a6b9f4efb569129c878b7f8db09132248fbaa1`。首次递归克隆因作者SSH子模块地址在本机网络拒绝而失败；改HTTPS获取相同对象，未改源码。

构建采用原CMake与Release参数，编译最多2并发。先运行作者simulate.sh给定lak303d实例，再按原run_exps.py的四地图最低机器人数量、instance1、situation0选择固定四实例，原GSES和Improved GSES各一臂；若某登记输入不存在，记录缺失而不按收益替换。两方法参数逐项取作者脚本，搜索上限16秒、权重1、固定原随机种子10；不运行MILP或以自写替代实现。默认实例作为运行预检，不计入后续同实例算法比较。保留超时与失败。

记录原original_cost、cost、status、search_time/total_time与费用单位，核查统计字段与运行配置。完整纸面数值复现、连续动力学安全验证及生产COST不在此R0范围。原路径/延迟snapshot和本项目连续执行、有限信息进度查询之间的差异必须列清，不能跨接口直接比任务数或宣称优越。

本机原始构建、作者仓库和运行收据位于main忽略目录 `implementation_binding_evidence/gses_author_preflight_20261003_r9`，公共分支只归档最小来源、选定输入、日志、配置、汇总和复现入口，避免复制整个上游数据仓库。
