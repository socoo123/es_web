# F31 · 内容、图解与阅读验收

本目录只对应F31及必要的F30下一课链接/课程目录。内容作者自审；入口无法设置或读回逐课提示词最新要求的`gpt-6.1-sol / max`，未启动独立代理，未宣称已启用，见[reasoning.json](reasoning.json)。

- [固定tag来源](sources.json)：6份必要ES源码与官方v9.4.0原始字节一致，包含分配过滤/同组/磁盘与resize条件。
- [D2生成](../../../framework/diagrams/f31/generation.json)：2源、浅深4SVG；D2 v0.9.0/dagre/4与201，fmt/check/validate/export各自成功，哈希可复核。未采用Archify，无Archify门禁或动画声明。
- [HTTP阅读](http-review.json)：本地HTTP真实`/es_web/`前缀、1920/1440/1024/768/390/320×浅深；880px/对齐/局部滚动；复制、目录、进度隔离、主题重载、file与reduced-motion/键盘分别检查。
- [内容与响应交叉核对](content-review.json)、[实际截图审阅](visual-review.json)、[最终检查](checks.json)由实际执行后写入，不用截图生成代替观看。
- [ES/Java两轮](../../../projects/travel-search/review/f31/README.md)独立统计。首轮浏览器观察窗的28次真实Java调用和28次DSL重放另记；运维不由浏览器发起。
- [原节点基线](existing-node-before.json)与[持续采样](existing-node-monitor.jsonl)只检查原容器ID/Pid/StartedAt/healthy，不包含其业务字段对账。

所有JSON与截图只反映本次固定样本。没有实际满盘、high/flood触发、跨机器容灾或性能结论；不以静态阅读/源码一致替代真实运行。
