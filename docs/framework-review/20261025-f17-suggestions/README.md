# F17 · 内容、图解、HTTP阅读与本机观察窗

只实施F17及必要的目录、F16下一课链接、当前进度与工程入口。正文[framework/f17.html](../../../framework/f17.html)，[实验入口](../../../projects/travel-search/labs/f17/README.md)，[真实两轮](../../../projects/travel-search/review/f17/README.md)。

- [内容自审](content-review.json)：正文/样本/固定意图/实际ID/练习/图解/工程片段；作者自审，无独立审阅代理。
- [来源](sources.json)：四个目标本地源码与官方v9.4.0逐字节比对；最新官方文档仅辅助，真实行为锁定ES9.4.0/Lucene10.4.0。
- [推理强度记录](reasoning.json)：用户要求xhigh；根入口不能设置或核验实际强度，不声称提示词已切换配置。
- [图生成](../../../framework/diagrams/f17/generation.json)：两源四SVG，官方D2 v0.9.0、dagre、主题4/201，生成/哈希与实际视觉分列。
- [HTTP阅读](http-review.json)：六宽×双主题、目录/F16必要回归、独立图、复制/锚点/折叠/主题/进度/file/reduced-motion与键盘。
- [真实观察窗](shell-review.json)：浏览器→最终Java jar→ES，模式/卡片/原文/完整DSL/DTO、错误与恢复；无mock，浏览器直连ES计数另核。
- [实际视觉审阅](visual-review.json)：明确逐张打开与总览查看范围；截图生成不等于已看完。
- [仓库检查](repository-checks.json)：结构、片段、语法、图源/产物/证据哈希与范围。
- [资源恢复](workspace-state.json)：本课索引/Java/容器/网络清理，其他节点状态保留。

[探索与修正](attempts/README.md)保留错误和修复依据。最终状态以收据为准；未测整体质量/性能、多节点、自动转写质量、在线发布、安全、DB/CDC、执行超时或部分分片失败。

实际汇总：HTTP正文12组、F16/目录24组、独立图16组；每组19锚点/9折叠；16段真实剪贴板；file双主题与reduced-motion/实际Tab通过。最大阅读列880px，390px正文362px，无整页溢出，表格/长代码局部滚动。真实观察窗3宽×双主题×11输入共66组/73次Java API；400/两个502/503与三次恢复通过，同Java进程，浏览器直连ES为0。57PNG经8张总览查看，10张另逐张打开；其余只看总览，不声称逐字审阅。
