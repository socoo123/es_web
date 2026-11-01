# F44 图源与生成

两幅静态D2：请求工作分布、按证据诊断与恢复。前者是简化请求顺序，不表示profile涵盖整段墙钟时间；后者是本课操作顺序，不是生产故障的唯一流程。无动画。

官方D2 v0.9.0、dagre、浅theme4/深theme201、pad24。修改图源后重新生成，禁止手改SVG。从本目录执行：

```bash
d2 fmt request-cost.d2 diagnosis.d2
d2 fmt --check request-cost.d2 diagnosis.d2
d2 validate request-cost.d2
d2 validate diagnosis.d2
d2 --layout=dagre --theme=4 --pad=24 request-cost.d2 request-cost-light.svg
d2 --layout=dagre --theme=201 --pad=24 request-cost.d2 request-cost-dark.svg
d2 --layout=dagre --theme=4 --pad=24 diagnosis.d2 diagnosis-light.svg
d2 --layout=dagre --theme=201 --pad=24 diagnosis.d2 diagnosis-dark.svg
```

[generation.json](generation.json)保存实际命令、退出码、版本与SHA-256。站点主题切换对应SVG，窄屏局部滚动并提供展开入口。没有采用Archify。

[HTTP/视觉](../../../docs/framework-review/20261101-f44-diagnosis/README.md)与[ES/Java](../../../projects/travel-search/review/f44/README.md)分别记录。
