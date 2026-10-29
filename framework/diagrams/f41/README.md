# F41 · 全量增量交叠、检查点与回滚

两幅静态D2。snapshot-delta说明本课故意安排的“增量先到、旧全量后到”及删除保护；cutover-rollback说明固定检查点、边界后的业务积压、查询切换及旧版持续追平。箭头是实验协调顺序，不代表跨分区全序或跨系统事务。双主题由站点切换浅/深SVG，窄屏局部滚动并提供展开；无动画。

官方D2 v0.9.0，dagre，浅theme4/深theme201、pad24。本环境CLI `/tmp/es-framework-d2-20261013/d2`；读者使用同版本CLI，在此目录运行。修改图源后重新导出，不手改SVG。

```bash
d2 fmt snapshot-delta.d2 cutover-rollback.d2
d2 fmt --check snapshot-delta.d2 cutover-rollback.d2
d2 validate snapshot-delta.d2
d2 validate cutover-rollback.d2
d2 --layout=dagre --theme=4 --pad=24 snapshot-delta.d2 snapshot-delta-light.svg
d2 --layout=dagre --theme=201 --pad=24 snapshot-delta.d2 snapshot-delta-dark.svg
d2 --layout=dagre --theme=4 --pad=24 cutover-rollback.d2 cutover-rollback-light.svg
d2 --layout=dagre --theme=201 --pad=24 cutover-rollback.d2 cutover-rollback-dark.svg
```

[generation.json](generation.json)记录实际命令、退出码、版本及源/产物SHA-256。[HTTP与实际视觉](../../../docs/framework-review/20261029-f41-rebuild/README.md)、[真实CDC/ES/Java](../../../projects/travel-search/review/f41/README.md)分别记录，图生成不替代链路实测。未采用Archify。
