# F08 静态图源

两幅图分别解释“查询时保留字段、写入时合并值”和“原文到安全文本段”；教学抽象，非完整源码调用图。正文880px列、浅深主题同步与展开入口；没有动画播放器。

官方D2 **v0.9.0** / dagre / light主题4、dark主题201 / pad24。只编辑`.d2`，禁止手改SVG。

```bash
d2 fmt framework/diagrams/f08/field-routes.d2 framework/diagrams/f08/safe-snippets.d2
python3 framework/diagrams/f08/generate.py /path/to/d2
```

[生成收据](generation.json)含fmt/validate/导出命令、CLI及图源/产物SHA256；[浏览器审阅](../../../docs/framework-review/20261020-f08-multifield/README.md)单独记录。生成通过不等于ES实验通过。
