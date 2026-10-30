# F42 图源与生成

两幅静态D2分别说明延迟的五层证据、固定边界对账与来源补偿。箭头表示传播/观察与控制顺序，不代表跨系统事务；单topic/单分区/合作写入者和小集合限制见正文。静态图不承诺动画。

官方D2 v0.9.0，dagre，浅theme4/深theme201、pad24。本环境CLI `/tmp/es-framework-d2-20261013/d2`。修改源后重新生成，不手改SVG：

```bash
d2 fmt latency-stages.d2 reconcile-repair.d2
d2 fmt --check latency-stages.d2 reconcile-repair.d2
d2 validate latency-stages.d2
d2 validate reconcile-repair.d2
d2 --layout=dagre --theme=4 --pad=24 latency-stages.d2 latency-stages-light.svg
d2 --layout=dagre --theme=201 --pad=24 latency-stages.d2 latency-stages-dark.svg
d2 --layout=dagre --theme=4 --pad=24 reconcile-repair.d2 reconcile-repair-light.svg
d2 --layout=dagre --theme=201 --pad=24 reconcile-repair.d2 reconcile-repair-dark.svg
```

[generation.json](generation.json)保留实际命令/版本/退出码/图源与产物SHA-256。[HTTP/视觉](../../../docs/framework-review/20261030-f42-reconcile/README.md)与[真实链路](../../../projects/travel-search/review/f42/README.md)分开验收。站点切换浅深SVG，窄屏仅图内滚动并提供展开；未采用Archify。
