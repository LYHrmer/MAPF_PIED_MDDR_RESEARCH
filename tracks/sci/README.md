# SCI MAPF 支线

工作树 `/home/lyh/MAPF_SCI_RESEARCH`，分支 `research/sci-mapf`。[总体决定](../../docs/RESEARCH_PLAN.md)是唯一当前总体计划。main本页只作索引，不复制本线实现。

最新证据固定在[535ee1a](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/535ee1adf3135ab79565e0b3aa5d189348fe7ab2/tracks/sci/PROFILE_RESULT.md)：六项16/32车诊断全部COMPLETE、零重试，共197次SIPP搜索；两项局部组改善SOC 1/2步，一项全体逆序改善1步，三项零余量无改善。它们是传统策略的DEV收益，不是相对完整ADDRESS优势或独立性能实验。

三个有搜索任务的回调wall有79.03%—85.92%在原生RPC之外，尚未分离校验/哈希/序列化各项。下一项是复用固定路径检查、保留增量与最终完整校验并细分计时，作为所有方法共享底座；接着完成已编译ADDRESS的共同初解/随机性适配。当前不训练“跳过昂贵SIPP”，不以工程优化认定创新。

第一批8车六臂结果[c0bd134](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/c0bd1345b8e192380ce2b1313e11475b54bbfa3d/tracks/sci/DEV_RESULT.md)仍保留：原控制48次搜索、增强0次且最终路径相同，三个初解达到同模型h。经典界作为独立贡献的投入停止。两批许可均已消费，不能重跑；第二批已实际覆盖逐车cap，源码仍为`818f1e9`的五个运行文件。

同问题近邻为NNS/ADDRESS/TACKLE；固定路径的Improved GSES/ESADG用于问题边界参照。SCI不等待原v2误差模块或LIMO，不使用L20/L21及本次单组DEV生成新标签。算法继续在本线单份维护，大论文引用核定提交。
