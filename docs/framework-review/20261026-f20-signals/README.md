# F20 · 内容、图解、HTTP阅读与真实观察窗

只实施F20及必要F19下一课、目录、工程入口与当前进度摘要；F21未实施。[正文](../../../framework/f20.html)、[本机实验](../../../projects/travel-search/labs/f20/README.md)、[真实两轮](../../../projects/travel-search/review/f20/README.md)。

- [运行配置](reasoning.json)：主agent实际spawn参数gpt-6.1-sol/max；子agent不可自行读回，权限指令danger-full-access/never/网络启用，无配置修改；历史xhigh记录保留。
- [内容自审](content-review.json)、[固定来源](sources.json)；作者自审，无额外子agent。
- [D2正式生成](../../../framework/diagrams/f20/generation.json)：两图四SVG与CLI/图源/产物哈希。
- [HTTP阅读](http-review.json)、[真实观察窗](shell-review.json)、[视觉范围](visual-review.json)分别记录。
- [仓库检查](repository-checks.json)、[资源清理](workspace-state.json)、[初探与修正](attempts/README.md)分列。

所有状态以实际收据为准，截图生成不等于已查看。固定样本通过不认证全站质量、性能、多节点、生产安全或数据链路；超时/部分分片失败未构造，不回填F04–F06历史受阻。

最终验收：每轮79教学＋35附加HTTP，两个点名清理轮次；HTTP正文12/前课与目录24/独立图16组、16段实际复制；观察窗90组/98实际Java调用＋细节3次。65PNG均经9张总览查看，15张另逐张打开，其余50仅总览。资源点名清理与版本/哈希核对通过范围见对应收据。全部由本课子agent自审和验证，主agent仅调度；没有独立内容审阅者或父内容验收。
