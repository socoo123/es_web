# F20 D2 图源与生成

两幅静态概念图，分别说明上游信号→函数部分→封顶和候选门槛。箭头是教学的数据与规则关系，非ES线程/调度顺序。无播放器或Archify。

官方D2 v0.9.0，dagre，浅色主题4/深色201，pad24；所有SVG由CLI生成，不手改产物。[生成命令、检查与哈希](generation.json)。

```bash
d2 fmt --check framework/diagrams/f20/signals.d2
d2 validate framework/diagrams/f20/signals.d2
d2 --layout=dagre --theme=4 --pad=24 framework/diagrams/f20/signals.d2 framework/diagrams/f20/signals-light.svg
d2 --layout=dagre --theme=201 --pad=24 framework/diagrams/f20/signals.d2 framework/diagrams/f20/signals-dark.svg
# gates.d2同样生成两主题
```

[HTTP与视觉记录](../../../docs/framework-review/20261026-f20-signals/README.md)与[真实ES两轮](../../../projects/travel-search/review/f20/README.md)分列。
