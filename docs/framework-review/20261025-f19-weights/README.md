# F19 · 内容、图解、HTTP阅读与真实观察窗

只实施F19及必要F18下一课、目录、工程入口和当前进度摘要；未实施F20。[正文](../../../framework/f19.html)、[本机入口](../../../projects/travel-search/labs/f19/README.md)、[真实两轮](../../../projects/travel-search/review/f19/README.md)。

- [内容自审](content-review.json)：概念、字段/金额/样本、真实次序/解释、正文/图/练习/速记与代码片段；作者自审，无独立代理。
- [固定来源](sources.json)：五份本地ES9.4.0源码与官方tag字节相同，Lucene10.4.0取大解释源码哈希；当前官方文档辅助。
- [推理入口限制](reasoning.json)：要求xhigh，根入口无法设置/核验，不把提示词当运行配置。
- [图生成](../../../framework/diagrams/f19/generation.json)：D2v0.9.0/dagre/双主题，图源、CLI、命令与产物哈希；无Archify/播放器。
- [HTTP阅读](http-review.json)、[真实观察窗](shell-review.json)分别记录；[视觉审阅](visual-review.json)区分逐张打开和总览，生成不等于已查看。
- [仓库检查](repository-checks.json)、[资源恢复](workspace-state.json)和[探索修正](attempts/README.md)分别保存。

本课只证明固定单分片样本行为，不认证全站质量/性能、多分片/生产安全/DB/CDC。超时/部分分片失败为代码防护；F04–F06历史受阻不回填。状态与范围以对应真实收据为准。

实际汇总：两轮每轮92教学＋39附加，清理两端各2，缺索引与同进程恢复各1另计。HTTP正文12组、F18/目录24回归、独立图16组，18锚点/组、9折叠/组、16段真实剪贴板。观察窗96组/104实际Java调用，补充3次，共107；完整浏览器响应保存在shell-review-full.json.gz，主收据保留输入、ID、布局与检查。57原始PNG全部经7张总览查看，20张另逐张打开；其余37仅总览，不冒充全文逐字。12行样本表与5行次序表已对照真实资料/响应。
