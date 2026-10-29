# F40 · 修订号、删除保护与失败位置

两幅静态D2：revision-guard解释同一景点跨topic的完整快照、单调修订号、保留删除标记与合法重开；failure-position只解释c03的真实部分成功、未提交、重新隔离及审核恢复。箭头是本课安排的处理/恢复先后，不代表跨topic固有次序或跨系统事务。无动画，站点主题切换浅深SVG；窄屏局部滚动并可展开。

官方D2 v0.9.0，dagre、浅色theme4/深色theme201、pad24。修改图源后重新生成，不手改产物。本环境CLI为`/tmp/es-framework-d2-20261013/d2`；读者使用自己的同版本CLI，在本目录执行：

```bash
d2 fmt revision-guard.d2 failure-position.d2
d2 fmt --check revision-guard.d2 failure-position.d2
d2 validate revision-guard.d2
d2 validate failure-position.d2
d2 --layout=dagre --theme=4 --pad=24 revision-guard.d2 revision-guard-light.svg
d2 --layout=dagre --theme=201 --pad=24 revision-guard.d2 revision-guard-dark.svg
d2 --layout=dagre --theme=4 --pad=24 failure-position.d2 failure-position-light.svg
d2 --layout=dagre --theme=201 --pad=24 failure-position.d2 failure-position-dark.svg
```

[generation.json](generation.json)记录版本、实际命令、退出码和源/产物SHA-256。图生成、[HTTP/视觉](../../../docs/framework-review/20261029-f40-replay/README.md)与[真实CDC/ES/Java](../../../projects/travel-search/review/f40/README.md)分别记录。未采用Archify。
