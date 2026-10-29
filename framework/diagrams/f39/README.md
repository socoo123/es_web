# F39 · 受影响实体与转移清理

两幅静态D2：affected-ids解释城市/景点/标签行变化怎样路由；transfer-cleanup解释只写新归属的残留、旧新重算及删除边界。箭头为事件处理与本课观察顺序，不表示跨topic全局次序、耗时或跨系统原子性。无动画；窄屏局部滚动/展开，站点切换浅深SVG。

官方D2 v0.9.0，dagre、浅色theme4/深色theme201、pad24。修改图源后重新生成，禁止手改SVG。本环境CLI为/tmp/es-framework-d2-20261013/d2；读者可使用自己的同版本路径，在本目录运行：

```bash
d2 fmt affected-ids.d2 transfer-cleanup.d2
d2 fmt --check affected-ids.d2 transfer-cleanup.d2
d2 validate affected-ids.d2
d2 validate transfer-cleanup.d2
d2 --layout=dagre --theme=4 --pad=24 affected-ids.d2 affected-ids-light.svg
d2 --layout=dagre --theme=201 --pad=24 affected-ids.d2 affected-ids-dark.svg
d2 --layout=dagre --theme=4 --pad=24 transfer-cleanup.d2 transfer-cleanup-light.svg
d2 --layout=dagre --theme=201 --pad=24 transfer-cleanup.d2 transfer-cleanup-dark.svg
```

[generation.json](generation.json)记录实际命令、退出码、版本与产物SHA-256。图生成、[HTTP与视觉](../../../docs/framework-review/20261029-f39-projection/README.md)、[真实CDC/Java/ES](../../../projects/travel-search/review/f39/README.md)分别验收。未使用Archify。
