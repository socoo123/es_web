# F21 · 距离、核验时效与排序验收索引

只实施F21及必要F20下一课/目录与工程入口，F22未实施。实际通过范围以对应JSON与最终STATUS为准。

- [正文](../../../framework/f21.html) / [本机实验入口](../../../projects/travel-search/labs/f21/README.md)
- [内容自审](content-review.json)、[5份固定版本源码](sources.json)、[运行与编排记录](reasoning.json)
- [官方D2生成](../../../framework/diagrams/f21/generation.json)
- [真实ES/Java两轮](../../../projects/travel-search/review/f21/README.md)、[运行版本/制品](../../../projects/travel-search/review/f21/runtime.json)
- [HTTP阅读与复制](http-review.json)、[真实本机观察窗](shell-review.json)、[实际截图视觉审阅](visual-review.json)
- [仓库检查与片段一致性](repository-checks.json)、[资源清理](workspace-state.json)
- [探索、失败与修正](attempts/README.md)

用户最新指定gpt-6.1-sol/max；父调度实际spawn设置该参数，子agent无读回API。本课作者自己完成内容、自审、真实实验、HTTP、截图与远端核对，主agent仅调度；不声称本实施者执行了主会话compact。权限按当前会话danger-full-access、approval_policy=never、network enabled；未修改全局配置。

88教学HTTP与作者附加/清理/浏览器调用分别计。数据固定、单节点单主分片，不评整体搜索质量或性能。超时/部分分片失败未构造；F04–F06历史状态不回填。Pages只放教程，本机Java观察窗另启动。

最终验收：真实ES/Java两轮每轮88教学＋55附加；浏览器102组/110实际API＋细节4次；HTTP12组/24回归/16独立图组/14次真实复制。76PNG已通过10张总览和16张单图实际审阅。未测整体质量、性能、多节点；故障范围与限制见对应收据。
