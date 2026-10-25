# F19 图源与生成

两幅静态D2：evidence比较整名/短语/散词；gates说明候选、组合得分、可选奖励与实际代价。前者隐形边仅排版；后者箭头为教学判断顺序，不是内部执行调度。省略中文语义理解、分片和底层查询执行。

官方D2 **v0.9.0**，dagre；浅主题4、深主题201、pad24。复现命令（仓库根目录，d2在PATH）：

```bash
d2 fmt --check framework/diagrams/f19/evidence.d2
d2 validate framework/diagrams/f19/evidence.d2
d2 --layout=dagre --theme=4 --pad=24 --timeout=30 framework/diagrams/f19/evidence.d2 framework/diagrams/f19/evidence-light.svg
d2 --layout=dagre --theme=201 --pad=24 --timeout=30 framework/diagrams/f19/evidence.d2 framework/diagrams/f19/evidence-dark.svg
d2 fmt --check framework/diagrams/f19/gates.d2
d2 validate framework/diagrams/f19/gates.d2
d2 --layout=dagre --theme=4 --pad=24 --timeout=30 framework/diagrams/f19/gates.d2 framework/diagrams/f19/gates-light.svg
d2 --layout=dagre --theme=201 --pad=24 --timeout=30 framework/diagrams/f19/gates.d2 framework/diagrams/f19/gates-dark.svg
```

只改.d2后重生成；[生成命令/CLI及源产物哈希](generation.json)。无Archify、无动画播放器，不承诺播放/暂停。主题由站点选择对应SVG，保留展开入口与离线资产。[正文](../../f19.html)、[HTTP/视觉记录](../../../docs/framework-review/20261025-f19-weights/README.md)；图生成不替代真实ES验收。
