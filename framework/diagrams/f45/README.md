# F45 图源与生成

两幅静态D2：景点SQL事实到可搜索结果；现象到源码问题。第一幅表示简化数据方向，不是完整源码调用，酒店固定价表不走CDC；第二幅是学习步骤，不是ES运行时序。无动画、无Archify。

D2 v0.9.0，dagre，theme4浅色/theme201深色，pad24。保留图源，修改后重新生成，禁止手改SVG。从本目录执行：

```bash
d2 fmt sync-boundary.d2 source-question.d2
d2 fmt --check sync-boundary.d2 source-question.d2
d2 validate sync-boundary.d2
d2 validate source-question.d2
d2 --layout=dagre --theme=4 --pad=24 sync-boundary.d2 sync-boundary-light.svg
d2 --layout=dagre --theme=201 --pad=24 sync-boundary.d2 sync-boundary-dark.svg
d2 --layout=dagre --theme=4 --pad=24 source-question.d2 source-question-light.svg
d2 --layout=dagre --theme=201 --pad=24 source-question.d2 source-question-dark.svg
```

[generation.json](generation.json)记录实际版本、命令、退出码与SHA-256。站点切换主题时换对应SVG；窄屏可展开，静态图不承诺动画或重播。HTTP布局和实际截图查看见[阅读验收](../../../docs/framework-review/20261101-f45-capstone/README.md)，真实ES/Java/CDC见[运行记录](../../../projects/travel-search/review/f45/README.md)。
