# F10 验收记录

只处理F10；本机ES/Java与Pages教程阅读分别验证。详细结果写入本目录JSON、[运行记录](../../../projects/travel-search/review/f10/README.md)及[图解生成](../../../framework/diagrams/f10/README.md)。

- [内容自审](content-review.json)：用户要求xhigh，根入口无法设置或核验；作者自审，无独立代理。
- [固定版本来源](sources.json)：只读取本课目标文件，与官方v9.4.0逐字节比较。
- [HTTP阅读](http-review.json)：六个宽度×双主题、必要F09/目录回归、复制、进度、图与导航。
- [真实观察页](shell-review.json)：真实浏览器→Java→ES；完整DTO/卡片/排序值，400/502/503恢复。
- [仓库检查](repository-checks.json)、[最终资源状态](workspace-state.json)。

截图生成与视觉审阅分别记录在JSON中；pending/仅生成不能称已审阅。首次脚本失败与修正保留在attempts目录（若发生）。没有Archify或机制播放器；未做多节点、PIT/分页、并发更新、性能/评分质量，也未制造ES执行超时与部分分片失败。

最终实际通过：本课HTTP12组、F09/目录24组、独立图16组、16次真实复制与14折叠/16锚点；本机观察页12组与24次真实搜索。阅读26PNG查看20、观察页11PNG查看10，其余只生成；逐张哈希/范围见[视觉收据](visual-review.json)。固定图源2份/浅深SVG4份；REST↔Java两轮及实际构建/依赖分列。ES探活刚恢复曾首请求仍503，随后同进程重试成功；不以探活承诺业务立即恢复。

最终仅点名删除本课索引、正常关闭Java并停止原先停止的框架ES；卷与源码篇节点保留。初次失败和修正见[attempts](attempts/README.md)。
